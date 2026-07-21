"""Continuous Discovery Runner -- the Phase-2 minimum working orchestrator.

One "pass" = generate a research perspective -> select a task within it -> select a market
window -> obtain data (live TV primary, CSV fallback) -> invoke Alpha through the structured
adapter -> validate the response -> persist the investigation. The runner repeats this for a
bounded number of passes and can resume after an interruption from its last checkpoint.

Safety controls present in Phase 2: bounded per-pass retries, a consecutive-failure circuit
breaker, an optional wall-clock ceiling, graceful shutdown (finish the current pass, checkpoint,
exit), a dry-run mode (no data pull, no external Alpha call), and a hard max-passes ceiling.
Continuous mode, candidate freeze/handoff, and CEO notification are Phases 3-4 and are NOT here;
CANDIDATE_PROPOSED outcomes are recorded and left for the Phase-3 gate.
"""

from __future__ import annotations

import json
import signal
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from . import schemas
from .config import Config
from .ids import IdAllocator, make_run_id
from .logutil import JsonlLogger
from .memory import ResearchMemory
from .perspective import PerspectiveGenerator
from .task_selector import ResearchTaskSelector
from .window_selector import MarketWindowSelector
from .data_access import DataAccess, assert_holdout_matches
from .adapters import build_adapter, StubAdapter, AlphaContext, AlphaAdapterError
from .mission import MISSION


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Runner:
    def __init__(
        self,
        config: Config,
        *,
        memory: Optional[ResearchMemory] = None,
        data_access: Optional[DataAccess] = None,
        adapter=None,
        tv_env=None,
        clock: Callable[[], str] = _utc_iso,
        install_signals: bool = True,
    ):
        config.validate()
        self.config = config
        self.clock = clock
        self.install_signals = install_signals

        config.state_path.mkdir(parents=True, exist_ok=True)
        config.runs_dir.mkdir(parents=True, exist_ok=True)

        self.ids = IdAllocator(config.id_allocator_path)
        self.memory = memory or ResearchMemory(config.memory_dir)
        self.data = data_access or DataAccess(config)
        self.adapter = adapter or build_adapter(config)
        # dry-run must never call the real reasoning backend
        self._dry_adapter = StubAdapter(config.seed)

        self.perspective_gen = PerspectiveGenerator(config.seed)
        self.task_sel = ResearchTaskSelector(config.seed)
        self.window_sel = MarketWindowSelector(
            config.seed, config.instrument_csv, config.data_split_id, config.holdout_cutoff)

        # TVRE (Phase 2.5): built lazily only when Alpha researches on TradingView.
        self.tv_env = tv_env
        if self.config.use_tv_research and self.tv_env is None:
            from .tv.client import TvClient
            from .tv.workspace import WorkspaceLog
            from .tv.environment import ResearchEnvironment
            wlog = WorkspaceLog(config.state_dir)
            self.tv_env = ResearchEnvironment(config, TvClient(config, action_log=wlog.action_sink()), wlog)

        self._stop = False
        self.logger: Optional[JsonlLogger] = None

    # ---------- run-state persistence ----------
    def _run_dir(self, run_id: str) -> Path:
        return self.config.runs_dir / run_id

    def _state_path(self, run_id: str) -> Path:
        return self._run_dir(run_id) / "run_state.json"

    def _write_state(self, state: dict) -> None:
        errs = schemas.validate(state, schemas.load_schema("run_state"))
        if errs:
            raise ValueError(f"invalid run state: {errs}")
        p = self._state_path(state["run_id"])
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
        tmp.replace(p)  # atomic checkpoint

    def _load_state(self, run_id: str) -> dict:
        p = self._state_path(run_id)
        if not p.exists():
            raise FileNotFoundError(f"no run state to resume for {run_id} at {p}")
        return json.loads(p.read_text(encoding="utf-8"))

    # ---------- signals ----------
    def _install_signal_handlers(self) -> None:
        if not self.install_signals:
            return
        def handler(signum, frame):
            self._stop = True
            if self.logger:
                self.logger.warn("shutdown_requested", signal=int(signum))
        for sig in ("SIGINT", "SIGTERM"):
            s = getattr(signal, sig, None)
            if s is not None:
                try:
                    signal.signal(s, handler)
                except (ValueError, OSError):
                    pass  # not in main thread / unsupported platform

    # ---------- one pass ----------
    def _select_window(self, task: dict, pass_no: int) -> dict:
        """Select a holdout-safe window from the CSV catalog (used by both data paths)."""
        tf = task["window_hint"]["timeframe"]
        timestamps = self.data.timestamps(tf)
        reviewed = self.memory.reviewed_windows(tf)
        window = self.window_sel.select(task, pass_no, timestamps, reviewed)
        if window is None:
            raise RuntimeError(f"no timestamps available for {tf}")
        return window

    def _acquire_window_and_data(self, task: dict, pass_no: int):
        """Select a window and obtain its data, with bounded retries. Returns (window, summary, provenance)."""
        tf = task["window_hint"]["timeframe"]
        last_err = None
        for attempt in range(self.config.max_retries + 1):
            try:
                window = self._select_window(task, pass_no)
                summary, provenance = self.data.get_window(window)
                return window, summary, provenance
            except Exception as e:  # transient data/selection failure
                last_err = e
                if self.logger:
                    self.logger.warn("acquire_retry", attempt=attempt, tf=tf, error=str(e))
        raise RuntimeError(f"data acquisition failed after retries: {last_err}")

    def run_pass(self, run_id: str, pass_no: int) -> dict:
        seed = self.perspective_gen.master_seed
        recent = self.memory.recent_stances(self.config.avoid_recent_perspectives)
        perspective = self.perspective_gen.generate(pass_no, recent)

        task_id = self.ids.next_investigation_id()
        asked = self.memory.asked_question_norms()
        task = self.task_sel.select(perspective, pass_no, asked, task_id)

        prior = sorted(asked)[: self.config.avoid_recent_questions]

        if self.config.dry_run:
            window = None
            provenance = {"data_source": "none"}
            context = AlphaContext(
                task_id=task_id, mission=MISSION, perspective=perspective, task=task,
                window=window, data_summary={"note": "dry_run: data pull skipped"},
                prior_questions=prior)
            response = self._dry_adapter.investigate(context)
        elif self.config.use_tv_research:
            # Alpha researches on TradingView: build the observation dossier + hybrid follow-ups.
            window = self._select_window(task, pass_no)
            response, provenance = self.tv_env.investigate(
                task=task, window=window, task_id=task_id, adapter=self.adapter,
                mission=MISSION, perspective=perspective, prior_questions=prior)
        else:
            window, data_summary, provenance = self._acquire_window_and_data(task, pass_no)
            context = AlphaContext(
                task_id=task_id, mission=MISSION, perspective=perspective, task=task,
                window=window, data_summary=data_summary, prior_questions=prior)
            response = self.adapter.investigate(context)

        outcome = response["finding_type"]

        record = {
            "task_id": task_id,
            "run_id": run_id,
            "pass": pass_no,
            "seed": seed,
            "perspective": perspective,
            "task": task,
            "window": window,
            "data_provenance": provenance,
            "response": response,
            "outcome": outcome,
            "gate_pending": outcome == "CANDIDATE_PROPOSED",
            "error": None,
            "ts": self.clock(),
        }
        self.memory.record_investigation(record)
        if self.logger:
            self.logger.info(
                "pass_complete", run_id=run_id, **{"pass": pass_no}, task_id=task_id,
                lens=perspective["lens"], framing=perspective["framing"],
                outcome=outcome, data_source=provenance.get("data_source"))
        return record

    def _record_pass_error(self, run_id: str, pass_no: int, error: str) -> dict:
        task_id = self.ids.next_investigation_id()
        record = {
            "task_id": task_id, "run_id": run_id, "pass": pass_no,
            "perspective": {}, "task": {}, "window": None,
            "data_provenance": {"data_source": "none"},
            "response": None, "outcome": "ERROR", "gate_pending": False,
            "error": error[:1000], "ts": self.clock(),
        }
        self.memory.record_investigation(record)
        if self.logger:
            self.logger.error("pass_error", run_id=run_id, **{"pass": pass_no}, error=error[:500])
        return record

    # ---------- run loop ----------
    def start(self, run_id: Optional[str] = None) -> dict:
        rid = run_id or make_run_id()
        state = {
            "run_id": rid,
            "mode": self.config.mode,
            "seed": self.config.seed,
            "next_pass": 0,
            "max_passes": self.config.max_passes,
            "delay_s": self.config.delay_s,
            "adapter": self.config.adapter,
            "dry_run": self.config.dry_run,
            "consecutive_failures": 0,
            "passes_completed": 0,
            "started_ts": self.clock(),
            "updated_ts": self.clock(),
            "status": "running",
            "config_snapshot": self.config.as_dict(),
        }
        self._write_state(state)
        return self._loop(state)

    def resume(self, run_id: str) -> dict:
        state = self._load_state(run_id)
        if state["status"] in ("completed", "failed"):
            if self.logger:
                self.logger.info("resume_noop", run_id=run_id, status=state["status"])
            return state
        state["status"] = "running"
        state["updated_ts"] = self.clock()
        self._write_state(state)
        return self._loop(state)

    def _loop(self, state: dict) -> dict:
        rid = state["run_id"]
        self.logger = JsonlLogger(self._run_dir(rid) / "run.log.jsonl", echo=False, clock=self.clock)
        self._install_signal_handlers()
        if not self.config.dry_run:
            assert_holdout_matches(self.config)

        self.logger.info("run_start", run_id=rid, next_pass=state["next_pass"],
                         max_passes=state["max_passes"], mode=state["mode"], adapter=state["adapter"])

        deadline = None
        if self.config.max_wallclock_s:
            deadline = time.monotonic() + self.config.max_wallclock_s

        pass_no = state["next_pass"]
        while pass_no < state["max_passes"]:
            if self._stop:
                state["status"] = "stopping"
                break
            if deadline and time.monotonic() >= deadline:
                self.logger.warn("wallclock_limit_reached", run_id=rid)
                break
            if state["consecutive_failures"] >= self.config.max_consecutive_failures:
                state["status"] = "failed"
                self.logger.error("circuit_breaker_tripped", run_id=rid,
                                  consecutive_failures=state["consecutive_failures"])
                break

            try:
                self.run_pass(rid, pass_no)
                state["consecutive_failures"] = 0
                state["passes_completed"] += 1
            except Exception as e:
                self._record_pass_error(rid, pass_no, f"{type(e).__name__}: {e}")
                state["consecutive_failures"] += 1

            # checkpoint AFTER the pass so a resume starts at the next one
            pass_no += 1
            state["next_pass"] = pass_no
            state["updated_ts"] = self.clock()
            self._write_state(state)

            if self.config.delay_s and pass_no < state["max_passes"] and not self._stop:
                time.sleep(self.config.delay_s)

        # finalize
        if state["status"] not in ("failed",):
            if self._stop:
                state["status"] = "stopped"
            elif pass_no >= state["max_passes"]:
                state["status"] = "completed"
            else:
                state["status"] = "stopped"
        state["updated_ts"] = self.clock()
        self._write_state(state)
        self.logger.info("run_end", run_id=rid, status=state["status"],
                         passes_completed=state["passes_completed"],
                         next_pass=state["next_pass"], memory=self.memory.stats())
        return state


# ------------------------- CLI -------------------------
def _build_config_from_args(args) -> Config:
    base = Config.from_json_file(args.config) if args.config else Config()
    return base.merged(
        mode=args.mode,
        max_passes=args.max_passes,
        delay_s=args.delay,
        seed=args.seed,
        adapter=args.adapter,
        data_source=args.data_source,
        dry_run=True if args.dry_run else None,
        state_dir=args.state_dir,
        use_tv_research=True if args.use_tv_research else None,
        research_mode=args.research_mode,
    )


def main(argv=None) -> int:
    import argparse

    p = argparse.ArgumentParser(
        prog="alpha_automation.runner",
        description="Alpha Automation v1.0 -- Continuous Discovery Runner (Phase 2: bounded).")
    p.add_argument("--config", help="optional JSON config file")
    p.add_argument("--mode", choices=["bounded", "continuous"], default=None)
    p.add_argument("--max-passes", type=int, default=None, dest="max_passes")
    p.add_argument("--delay", type=float, default=None, help="inter-pass delay seconds")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--adapter", choices=["stub", "codex"], default=None)
    p.add_argument("--data-source", choices=["auto", "live", "csv"], default=None, dest="data_source")
    p.add_argument("--use-tv-research", action="store_true", dest="use_tv_research",
                   help="Alpha researches on the live TradingView instance (TVRE)")
    p.add_argument("--research-mode", choices=["replay_pre_cutoff", "live_observation"],
                   default=None, dest="research_mode")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--state-dir", default=None, dest="state_dir")
    p.add_argument("--resume", metavar="RUN_ID", default=None,
                   help="resume an interrupted run by its run id")
    args = p.parse_args(argv)

    config = _build_config_from_args(args)
    runner = Runner(config)
    if args.resume:
        state = runner.resume(args.resume)
    else:
        state = runner.start()
    print(json.dumps({
        "run_id": state["run_id"], "status": state["status"],
        "passes_completed": state["passes_completed"], "next_pass": state["next_pass"],
        "memory": runner.memory.stats(),
    }, indent=2))
    return 0 if state["status"] in ("completed", "stopped") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

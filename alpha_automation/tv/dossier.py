"""Observation Dossier builder -- Alpha's multi-modal view of one investigation window.

Assembles the guaranteed baseline packet (the hybrid model's floor) via the gated TvClient, in
the mode-enforced (holdout-safe) research environment: chart state, OHLCV summary, indicator
values, custom Pine output (lines/labels/tables/boxes), a live quote, a short bar-by-bar replay
track, screenshots, and optional numeric multi-timeframe context. Everything is descriptive and
boundary-safe; no tradability metric is computed.

Robust by design: optional pieces are best-effort (a missing indicator or a failed screenshot
degrades that section to null, it does not fail the whole dossier). Holdout safety is enforced by
ResearchMode before and during observation.
"""

from __future__ import annotations

from typing import Callable, Optional

from .client import TvClient
from .mode import ResearchMode, HoldoutViolation
from .workspace import WorkspaceLog


class DossierBuilder:
    def __init__(self, config, client: TvClient, mode: ResearchMode, workspace: WorkspaceLog,
                 context_provider: Optional[Callable[[str], dict]] = None, logger=None):
        self.config = config
        self.client = client
        self.mode = mode
        self.workspace = workspace
        self.context_provider = context_provider
        self.log = logger

    def build(self, task: dict, window: dict, task_id: str) -> dict:
        tf = window["timeframe"]
        symbol = self.config.instrument_live

        # 1. Point the (single, Alpha-owned) chart at the window's symbol + timeframe.
        self.client.batch([("set_symbol", {"symbol": symbol}),
                           ("set_timeframe", {"timeframe": _tf_to_tv(tf)})], task_id=task_id)

        # 2. Enter the correct research mode (replay anchored pre-cutoff, or live) -- fail-closed.
        mode_info = self.mode.prepare(window, task_id=task_id)

        # 3. Provenance snapshot of what Alpha is observing under.
        self.workspace.snapshot(self.client, task_id, mode_info)

        # 4. Core reads in one batch (best-effort per item).
        reads = self.client.batch([
            ("get_state", None),
            ("get_ohlcv", {"summary": True}),
            ("get_study_values", None),
            ("get_pine_lines", None),
            ("get_pine_labels", None),
            ("get_pine_tables", None),
            ("get_pine_boxes", None),
            ("get_quote", None),
        ], task_id=task_id, strict=False)
        r = {item.get("verb"): (item.get("result") if item.get("ok") else None) for item in reads}

        # 5. Bar-by-bar replay track (replay mode only), holdout-verified per step.
        replay_track = self._replay_track(task_id) if self.mode.mode == "replay_pre_cutoff" else []

        # 6. Screenshots (visual observation; attached to codex via -i by the adapter).
        screenshots = []
        if self.config.tv_screenshots:
            shot = self.client.try_call("capture_screenshot", {"region": "chart"}, task_id=task_id)
            if shot and shot.get("file_path"):
                screenshots.append(shot["file_path"])

        # 7. Numeric multi-timeframe context (holdout-safe, from the caller's provider).
        multi_tf = {}
        if self.context_provider:
            for ctx_tf in self.config.tv_multi_tf:
                try:
                    multi_tf[ctx_tf] = self.context_provider(ctx_tf)
                except Exception as e:  # context is optional enrichment, never fatal
                    if self.log:
                        self.log.warn("multi_tf_context_failed", tf=ctx_tf, error=str(e))

        return {
            "task_id": task_id,
            "mode": mode_info.get("mode"),
            "data_regime": mode_info.get("data_regime"),
            "validation_eligible": mode_info.get("validation_eligible", False),
            "instrument": symbol,
            "primary_timeframe": tf,
            "window": {"start": window["start"], "end": window["end"]},
            "chart_state": r.get("get_state"),
            "ohlcv_summary": r.get("get_ohlcv"),
            "indicators": r.get("get_study_values"),
            "pine": {
                "lines": r.get("get_pine_lines"),
                "labels": r.get("get_pine_labels"),
                "tables": r.get("get_pine_tables"),
                "boxes": r.get("get_pine_boxes"),
            },
            "quote": r.get("get_quote"),
            "replay_track": replay_track,
            "screenshots": screenshots,
            "multi_tf_context": multi_tf,
            "notes": mode_info.get("note"),
        }

    def _replay_track(self, task_id: str) -> list:
        """Step the replay forward a few bars, reading the developing quote, holdout-verified."""
        track = []
        n = max(0, int(self.config.tv_replay_samples))
        for i in range(n):
            try:
                step = self.mode.step_safely(task_id=task_id)  # advances + re-verifies < cutoff
            except HoldoutViolation:
                # We reached the cutoff boundary; stop stepping (do not observe at/after cutoff).
                if self.log:
                    self.log.warn("replay_track_stopped_at_cutoff", step=i)
                break
            quote = self.client.try_call("get_quote", None, task_id=task_id)
            track.append({
                "step": i,
                "current_date": step.get("current_date"),
                "quote": _quote_snippet(quote),
            })
        return track


def _tf_to_tv(tf: str) -> str:
    return {"M15": "15", "H1": "60", "H4": "240", "D1": "D"}.get(tf, "60")


def _quote_snippet(q: Optional[dict]) -> Optional[dict]:
    if not q:
        return None
    return {k: q.get(k) for k in ("last", "open", "high", "low", "close", "volume") if k in q}

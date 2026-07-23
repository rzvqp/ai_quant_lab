"""Learning Feedback -- Phase 1: Capture Activation, Stage 1 (CEO directive, 2026-07-23). Activates the
already-built Learning/Research Feedback capture pipeline (Sprint 1 Phase F + Sprint 2, both CLOSED,
``PROJECT_STATE_v2.md`` Sec8.27) for the first time in this repository's history and validates it against the
CEO's own 10-point canary scope. **Zero existing files touched** -- every parameter used below
(``learning_feedback_repository_path``, ``context.shadow_config``) already exists on
``SimulationHarness``/``SimulationContext`` and is already covered by Sprint 2's own 825-test regression;
this script only supplies real values for parameters that have always defaulted to inert.

**Window**: a 30-day slice of the SAME CEO-approved, non-holdout 12-month window
``phase69a_funnel_run.py``/``portfolio_architect_tiebreak_evidence.py`` already established
(2024-10-23 -> 2025-10-23) -- short and representative, per the CEO's own canary-scope instruction, not a
new or enlarged window invented for this run. The sealed terminal holdout is untouched either way.

**Configuration**: ``use_strategy_runtime=True`` and ``strategy_id_filter=None`` (all 43 registered
strategies eligible for real-competitive trades, matching Wave D's own baseline), ``shadow_config``
enabled for all 43 registered strategies (``all_registered_strategies()``, Checkpoint 3's own existing
helper -- no strategy hand-picked), ``learning_feedback_repository_path`` set to a real, on-disk directory
under ``learning_feedback_data/`` -- the only two switches (Phase 1 design Sec1) that were ever inert by
default.

**Two runs, both required by the CEO's own canary scope**:
1. ``run_baseline()`` -- a clean, single, uninterrupted run over the full canary window into
   ``learning_feedback_data/canary/``. This is the primary data-collection result.
2. ``run_interruption_experiment()`` -- on a SEPARATE, throwaway repository path
   (``learning_feedback_data/canary_interrupt_test/``), a harness is stepped manually (``harness.step()``
   in a loop, NOT ``run_to_completion()``) for only part of the window, then simply abandoned -- no
   ``stop()``/finalize call, faithfully simulating an uncontrolled process kill (canary criterion 8). The
   partial repository is then verified parseable, and a SECOND, fresh harness re-runs the SAME full window
   into the SAME path (canary criterion 9: does resuming/re-running produce duplicates or corruption).
   Content-hash-based record identity (``identities.py``'s own ``compute_edge_evidence_id``/
   ``compute_position_outcome_id``, unmodified) is the mechanism under test: a deterministic re-run of the
   same window should produce byte-identical records, which the repository's own already-tested
   idempotent-append behavior should collapse rather than duplicate.

Produces ``learning_feedback_capture_activation_canary_report.json`` -- every metric the CEO's own
mandatory validation list requires, computed directly from the repository's own public read API
(``iter_outcomes``/``iter_position_outcomes``/``iter_observations``/``iter_interim_realizations``,
``get_outcome``/``get_position_outcome``/``get_interim_realization`` for FK checks) -- never by parsing
JSONL by hand, so every count is exactly what any future reader of the repository would also see.
"""

from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from ai_trader.context_memory.enums import OutcomeKind, OutcomeStatus
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.shadow_evidence.config import ShadowConfig, all_registered_strategies
from ai_trader.simulation.config import DateRange, SimulationContext
from ai_trader.simulation.harness import SimulationHarness
from ai_trader.simulation.types import RunState
from ai_trader.strategy_manager.config import ManagerConfig

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}

# Same CEO-approved, non-holdout window origin as phase69a_funnel_run.py / portfolio_architect_tiebreak_
# evidence.py (2024-10-23 09:00:00 UTC start) -- this script uses only the first 30 days of it, a short,
# representative canary slice, per the CEO's own explicit "do not start the full 12-month run yet" limit.
FULL_WINDOW_START = 1_729_674_000  # 2024-10-23 09:00:00 UTC
CANARY_WINDOW_END = FULL_WINDOW_START + 30 * 86_400  # +30 days = 2024-11-22 09:00:00 UTC

BASELINE_REPO_PATH = REPO_ROOT / "learning_feedback_data" / "canary"
INTERRUPT_REPO_PATH = REPO_ROOT / "learning_feedback_data" / "canary_interrupt_test"
REPORT_PATH = REPO_ROOT / "learning_feedback_capture_activation_canary_report.json"

ALL_STRATEGY_IDS = tuple(sorted(all_registered_strategies()))


def _risk_config() -> RiskConfig:
    # Identical to portfolio_architect_phase2a_calibration.py / portfolio_architect_tiebreak_evidence.py's
    # own _risk_config() -- no new risk logic invented for this run.
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    return cfg


def new_harness(run_id: str, repo_path: Path, window_end: int = CANARY_WINDOW_END) -> SimulationHarness:
    context = SimulationContext(
        run_id=run_id, date_range=DateRange(FULL_WINDOW_START, window_end),
        symbols=("XAUUSD",), timeframes=("M15", "H1", "H4", "D1"), starting_balance=2000.0,
        run_seed=1, warmup_bars=200,
        shadow_config=ShadowConfig(enabled=True, shadow_strategies=ALL_STRATEGY_IDS),
    )
    harness = SimulationHarness(
        context, SYMBOL_META, DATA_DIR,
        manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
        enable_time_stops=True, enable_trailing_stops=True, strategy_id_filter=None,
        learning_feedback_repository_path=repo_path,
    )
    harness.configure()
    harness.load()
    assert harness.state is RunState.WARMUP, harness.fail_reason
    assert harness.shadow_engine is not None, "shadow_config was set but shadow_engine did not construct"
    return harness


# ================================================================================================
# Run 1: clean baseline
# ================================================================================================


def run_baseline() -> dict[str, Any]:
    start = time.time()
    harness = new_harness("LF-CANARY-BASELINE", BASELINE_REPO_PATH)
    harness.run_to_completion()
    elapsed = time.time() - start
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    assert harness._lf_repo is not None  # noqa: SLF001 -- read-only introspection, this script's own harness instance
    assert harness._lf_correlation is not None  # noqa: SLF001
    assert harness._lf_correlation.pending_count() == 0, (  # noqa: SLF001
        "Sprint 2 Blocker 3 invariant violated: a candidate leaked past end-of-run"
    )
    return {
        "run_id": "LF-CANARY-BASELINE", "elapsed_seconds": elapsed,
        "bars_processed": harness.bars_processed, "state": harness.state.value,
        "repo_path": str(BASELINE_REPO_PATH),
    }


# ================================================================================================
# Run 2: uncontrolled-interruption + re-run experiment (canary criteria 8 and 9)
# ================================================================================================


def run_interruption_experiment() -> dict[str, Any]:
    """IMPORTANT, discovered this session: ``position_key``/Shadow's own ``position_id`` are BY DESIGN
    deterministic only across replays of the SAME ``run_id`` (``learning_feedback/position_registry.py:36-41``,
    ``shadow_evidence/engine.py:334`` -- both docstrings state this explicitly: "reproducible across
    identical replays of the SAME run_id/config"). A true "resume after an interrupted run" must therefore
    reuse the EXACT SAME ``run_id`` for the abort phase and the completing re-run -- using two different
    ``run_id`` values (an earlier version of this experiment did) is not "resuming," it is two independent
    runs, and their records will legitimately never deduplicate against each other (each carries its own,
    different, run_id-embedded position identity) -- not a defect, a scoping fact about the identity model
    that any future real recovery procedure must respect."""
    if INTERRUPT_REPO_PATH.exists():
        import shutil
        shutil.rmtree(INTERRUPT_REPO_PATH)

    SAME_RUN_ID = "LF-CANARY-INTERRUPT"

    # Phase A: step manually, stop partway, WITHOUT calling stop()/finalize -- an uncontrolled abort, not
    # a clean shutdown. Whatever the repository holds at this point is exactly what a real process kill
    # would have left on disk (each _JsonlStream.append() write is already flushed per-call).
    harness_partial = new_harness(SAME_RUN_ID, INTERRUPT_REPO_PATH)
    bars_before_abort = 0
    # 900 bars -- comfortably past the 200-bar warmup (new_harness()'s own warmup_bars=200), so the abort
    # point genuinely lands mid-capture with real, non-empty Observation/Outcome/PositionOutcome state
    # already on disk, not merely mid-warmup (an earlier 40-bar abort point was found, on inspection of
    # its own results, to land entirely inside warmup -- zero records existed yet at that point, which
    # validates "abort before any capture" but does NOT exercise "abort with real partial data already
    # written," a materially weaker test than canary criterion 8 requires).
    target_abort_bars = 900
    while bars_before_abort < target_abort_bars and harness_partial.step():
        bars_before_abort += 1
    # Deliberately abandon harness_partial here -- no stop(), no finalize, no drain_pending().

    partial_parse_ok, partial_parse_error, partial_counts = _check_parseable_and_count(INTERRUPT_REPO_PATH)

    # Phase B: a SECOND, fresh harness, SAME run_id, re-runs the SAME full canary window into the SAME
    # (already partially-populated) repository path -- the genuine "resume by re-running" scenario this
    # architecture supports (no mid-run checkpoint/resume capability exists, by design; re-running the
    # full window under the identical run_id and relying on content-hash identity + idempotent append is
    # the only correct recovery procedure). If it works as designed, the final state must equal a clean
    # single run exactly.
    harness_resumed = new_harness(SAME_RUN_ID, INTERRUPT_REPO_PATH)
    harness_resumed.run_to_completion()
    assert harness_resumed.state is RunState.COMPLETED, harness_resumed.fail_reason

    final_parse_ok, final_parse_error, final_counts = _check_parseable_and_count(INTERRUPT_REPO_PATH)

    return {
        "bars_before_abort": bars_before_abort,
        "partial_state_parseable": partial_parse_ok, "partial_parse_error": partial_parse_error,
        "partial_counts": partial_counts,
        "final_state_parseable": final_parse_ok, "final_parse_error": final_parse_error,
        "final_counts": final_counts,
        "repo_path": str(INTERRUPT_REPO_PATH),
    }


def _check_parseable_and_count(repo_path: Path) -> tuple[bool, str | None, dict[str, int]]:
    """Every JSONL line in every stream must parse. Uses the repository's own public API (which itself
    parses every line via its own codec on construction/rebuild) rather than reimplementing JSON parsing
    here -- if any line were malformed, this call raises."""
    try:
        repo = ContextMemoryRepository(repo_path)
        repo.rebuild()
        counts = {
            "context_snapshots": repo.count_context_snapshots(), "observations": repo.count_observations(),
            "outcomes": repo.count_outcomes(), "operational_metadata": repo.count_operational_metadata(),
            "interim_realizations": repo.count_interim_realizations(),
            "position_outcomes": repo.count_position_outcomes(),
        }
        return True, None, counts
    except Exception as exc:  # noqa: BLE001 -- deliberately broad: this IS the corruption-detection check
        return False, repr(exc), {}


# ================================================================================================
# Validation report (canary criteria 1-7, 10)
# ================================================================================================


def validate_repository(repo_path: Path) -> dict[str, Any]:
    repo = ContextMemoryRepository(repo_path)
    repo.rebuild()  # canary criterion 6: every line must parse, or this raises

    outcomes = list(repo.iter_outcomes())
    position_outcomes = list(repo.iter_position_outcomes())
    interim_realizations = list(repo.iter_interim_realizations())
    observations = list(repo.iter_observations())

    outcome_kind_counts = Counter(o.outcome_kind.value for o in position_outcomes)
    strategy_distribution: dict[str, Counter[str]] = defaultdict(Counter)
    for po in position_outcomes:
        strategy_distribution[po.strategy_id][po.outcome_kind.value] += 1

    outcome_status_counts = Counter(o.status.value for o in outcomes)
    complete_outcomes = sum(1 for o in outcomes if o.status is OutcomeStatus.RESOLVED)
    incomplete_outcomes = len(outcomes) - complete_outcomes

    # Duplicate detection: content-hash identity means the record's OWN id (recoverable via
    # compute_edge_evidence_id/compute_position_outcome_id, unmodified) must be unique per record -- but
    # since the repository already de-duplicates on append (Sprint 1's own idempotent-append behavior,
    # tested), the real check here is "does re-deriving each record's id from its own content match a
    # unique count" -- i.e. no two DISTINCT lines hash to the same id (would indicate corruption) and no
    # semantically-identical record appears more than once by coincidence of non-deterministic fields.
    from ai_trader.context_memory.identities import compute_edge_evidence_id, compute_position_outcome_id

    outcome_ids = [compute_edge_evidence_id(o).value for o in outcomes]
    position_outcome_ids = [compute_position_outcome_id(po).value for po in position_outcomes]
    duplicate_outcome_ids = len(outcome_ids) - len(set(outcome_ids))
    duplicate_position_outcome_ids = len(position_outcome_ids) - len(set(position_outcome_ids))

    # Orphan-record check: every PositionOutcome.terminal_outcome_id must resolve to a real Outcome
    # already in the repository; every constituent_interim_realization_id must resolve to a real
    # InterimRealization; every Outcome/Observation reference (observation_id) must resolve too.
    from ai_trader.context_memory.contracts import EdgeEvidenceId

    orphan_position_outcome_terminal_refs = 0
    orphan_position_outcome_interim_refs = 0
    for po in position_outcomes:
        if repo.get_outcome(EdgeEvidenceId(po.terminal_outcome_id.value)) is None:
            orphan_position_outcome_terminal_refs += 1
        for irid in po.constituent_interim_realization_ids:
            if repo.get_interim_realization(irid) is None:
                orphan_position_outcome_interim_refs += 1

    orphan_outcome_observation_refs = sum(
        1 for o in outcomes if repo.get_observation(o.observation_id) is None
    )
    orphan_position_outcome_observation_refs = sum(
        1 for po in position_outcomes if repo.get_observation(po.observation_id) is None
    )
    orphan_interim_observation_refs = sum(
        1 for ir in interim_realizations if repo.get_observation(ir.observation_id) is None
    )

    # File sizes, per stream (repository root is a flat directory of the 6 JSONL files).
    file_sizes = {
        p.name: p.stat().st_size for p in sorted(repo_path.glob("*.jsonl"))
    } if repo_path.exists() else {}

    return {
        "repository_path": str(repo_path),
        "total_position_outcomes": len(position_outcomes),
        "position_outcomes_by_kind": dict(outcome_kind_counts),
        "position_outcomes_by_strategy": {
            sid: dict(counts) for sid, counts in sorted(strategy_distribution.items())
        },
        "total_outcomes": len(outcomes),
        "outcomes_by_status": dict(outcome_status_counts),
        "complete_outcomes_resolved": complete_outcomes,
        "incomplete_outcomes_non_resolved": incomplete_outcomes,
        "total_interim_realizations": len(interim_realizations),
        "total_observations": len(observations),
        "duplicate_outcome_ids": duplicate_outcome_ids,
        "duplicate_position_outcome_ids": duplicate_position_outcome_ids,
        "orphan_position_outcome_terminal_refs": orphan_position_outcome_terminal_refs,
        "orphan_position_outcome_interim_refs": orphan_position_outcome_interim_refs,
        "orphan_outcome_observation_refs": orphan_outcome_observation_refs,
        "orphan_position_outcome_observation_refs": orphan_position_outcome_observation_refs,
        "orphan_interim_observation_refs": orphan_interim_observation_refs,
        "file_sizes_bytes": file_sizes,
        "total_repository_size_bytes": sum(file_sizes.values()),
    }


# ================================================================================================
# Main
# ================================================================================================


def main() -> None:
    print(f"n_strategies_shadow_enabled={len(ALL_STRATEGY_IDS)}")
    print("=== Run 1: baseline canary run ===")
    baseline_run_info = run_baseline()
    print(json.dumps(baseline_run_info, indent=2))

    print("=== Validating baseline repository ===")
    baseline_validation = validate_repository(BASELINE_REPO_PATH)
    print(json.dumps(baseline_validation, indent=2, default=str))

    print("=== Run 2: uncontrolled-interruption + re-run experiment ===")
    interruption_result = run_interruption_experiment()
    print(json.dumps(interruption_result, indent=2, default=str))

    # Cross-check: the interruption experiment's FINAL state (after abort + full re-run) should match
    # the clean baseline's own counts exactly -- both ran the identical deterministic window/seed.
    counts_match_baseline = (
        interruption_result["final_counts"].get("position_outcomes")
        == baseline_validation["total_position_outcomes"]
        and interruption_result["final_counts"].get("outcomes") == baseline_validation["total_outcomes"]
        and interruption_result["final_counts"].get("observations") == baseline_validation["total_observations"]
    )

    report = {
        "canary_window": {"start": FULL_WINDOW_START, "end": CANARY_WINDOW_END, "days": 30},
        "baseline_run": baseline_run_info,
        "baseline_validation": baseline_validation,
        "interruption_experiment": interruption_result,
        "interruption_resume_matches_clean_baseline": counts_match_baseline,
    }
    with REPORT_PATH.open("w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()

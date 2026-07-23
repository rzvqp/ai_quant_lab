"""Learning Feedback -- Phase 1: Capture Activation, Stage 2 (CEO directive, 2026-07-24). The full,
12-month real data-collection run, authorized after Stage 1's canary (READY FOR FULL CAPTURE verdict,
`LEARNING_FEEDBACK_PHASE1_STAGE1_CANARY_REPORT.md`). **Zero new logic** -- reuses
`learning_feedback_capture_activation_run.py`'s own `new_harness()`/`validate_repository()`/
`_check_parseable_and_count()` verbatim (imported, not duplicated), with two changes only: the full
12-month window instead of a 30-day slice, and a durable, non-canary repository path.

**The CEO's own explicit rule, carried forward from Stage 1's own disclosed finding**: `position_key`/
Shadow `position_id` are deterministic only WITHIN the same `run_id`
(`learning_feedback/position_registry.py:36-41`, `shadow_evidence/engine.py:334`). This run therefore
commits to exactly ONE fixed `run_id` (`STAGE2_RUN_ID` below) for its entire duration. **If this run is
ever interrupted, recovery is: re-invoke this same script, unchanged, with the same `run_id` -- never a
new one** -- Stage 1's own interruption/resume experiment proved this reconciles cleanly via idempotent,
content-hash record identity; a different `run_id` would NOT deduplicate and would leave orphaned partial
records behind (Stage 1's own disclosed negative-control finding).

**Scope, per the CEO's own explicit instruction**: capture and integrity validation ONLY. No decision or
execution logic of any kind is implemented, read, or exercised by this script beyond what
`SimulationHarness`/`ShadowEvidenceEngine` already do for the real-competitive and Shadow paths
(unmodified, pre-existing, already-validated code).

**Window**: the SAME CEO-approved, non-holdout 12-month window `phase69a_funnel_run.py`/
`portfolio_architect_tiebreak_evidence.py` established (2024-10-23 09:00:00 UTC -> 2025-10-23 09:00:00
UTC) -- not re-derived, the exact same timestamps. The sealed terminal holdout is untouched.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from ai_trader.simulation.types import RunState
from learning_feedback_capture_activation_run import (
    ALL_STRATEGY_IDS,
    FULL_WINDOW_START,
    REPO_ROOT,
    new_harness,
    validate_repository,
)

# Same CEO-approved 12-month window end phase69a_funnel_run.py / portfolio_architect_tiebreak_evidence.py
# already used -- the literal timestamp, not re-derived from a day count, to avoid any drift.
STAGE2_WINDOW_END = 1_761_210_000  # 2025-10-23 09:00:00 UTC

# ONE fixed run_id for this run's entire duration/lifetime, including any future recovery re-invocation of
# this exact script after an interruption -- per the CEO's own explicit Stage 2 instruction and Stage 1's
# own proven recovery procedure. Do not change this value between invocations of the same logical run.
STAGE2_RUN_ID = "LF-STAGE2-FULL-CAPTURE"

STAGE2_REPO_PATH = REPO_ROOT / "learning_feedback_data" / "full_capture"
REPORT_PATH = REPO_ROOT / "learning_feedback_stage2_full_capture_report.json"


def main() -> None:
    print(f"n_strategies_shadow_enabled={len(ALL_STRATEGY_IDS)}")
    print(f"run_id={STAGE2_RUN_ID!r} repo_path={STAGE2_REPO_PATH}")
    print(f"window: {FULL_WINDOW_START} -> {STAGE2_WINDOW_END}")

    start = time.time()
    harness = new_harness(STAGE2_RUN_ID, STAGE2_REPO_PATH, window_end=STAGE2_WINDOW_END)
    harness.run_to_completion()
    elapsed = time.time() - start
    assert harness.state is RunState.COMPLETED, harness.fail_reason
    assert harness._lf_repo is not None  # noqa: SLF001 -- read-only introspection, this script's own harness
    assert harness._lf_correlation is not None  # noqa: SLF001
    assert harness._lf_correlation.pending_count() == 0, (  # noqa: SLF001
        "Sprint 2 Blocker 3 invariant violated: a candidate leaked past end-of-run"
    )

    run_info = {
        "run_id": STAGE2_RUN_ID, "elapsed_seconds": elapsed, "bars_processed": harness.bars_processed,
        "state": harness.state.value, "repo_path": str(STAGE2_REPO_PATH),
        "window": {"start": FULL_WINDOW_START, "end": STAGE2_WINDOW_END},
    }
    print(json.dumps(run_info, indent=2))

    print("=== Validating full-capture repository ===")
    validation = validate_repository(STAGE2_REPO_PATH)
    print(json.dumps(validation, indent=2, default=str))

    report = {"stage2_run": run_info, "stage2_validation": validation}
    with REPORT_PATH.open("w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()

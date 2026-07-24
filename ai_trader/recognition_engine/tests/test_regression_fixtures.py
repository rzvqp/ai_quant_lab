"""Control 7 (permanent mismatch regression fixtures): the 4 real cases found by
`LEARNING_FEEDBACK_DATASET_AUDIT.md` §2, where `PositionOutcome.total_net_pnl`'s own sign disagrees with
the terminal `Outcome.normalized_result`'s own sign (a multi-partial position: an early profitable
partial followed by a losing final fill, or vice versa). Reproduced here as synthetic fixtures (never
depending on the actual, real, 765MB generated repository) mirroring each real case's own shape exactly,
so this regression is permanent and runs in every future test invocation, matching this project's own
established "fast, synthetic fixture over a full real-data re-run" precedent
(shadow_evidence/research.py's own 43-synthetic-strategy tests, Portfolio Architect's own synthetic
genericity tests).

CEO decision 5 / Phase 1 Design §1: Recognition Engine must use `PositionOutcome.total_net_pnl`, NEVER
the terminal `Outcome.normalized_result`, as the position's own truth. Every fixture below is
constructed so that using the WRONG field would flip the favorable/unfavorable classification --
proving, not merely asserting, that the engine reads the correct field.
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.context_memory.enums import OutcomeKind
from ai_trader.recognition_engine.engine import compute_conditional_statistics
from ai_trader.recognition_engine.types import ContextDimension
from ai_trader.recognition_engine.tests._fixtures import build_repository

# Each tuple: (total_net_pnl, terminal_outcome_normalized_result) -- signs deliberately opposite,
# mirroring the 4 real cases from LEARNING_FEEDBACK_DATASET_AUDIT.md §2 verbatim:
#   LF-STAGE2-FULL-CAPTURE:XAUUSD:1731333600:SHORT -- net_pnl=+4.62,  terminal=-1.08
#   LF-STAGE2-FULL-CAPTURE:XAUUSD:1734013800:SHORT -- net_pnl=+3.65,  terminal=-1.05
#   LF-STAGE2-FULL-CAPTURE:XAUUSD:1745361000:LONG  -- net_pnl=-0.63,  terminal=+0.51
#   LF-STAGE2-FULL-CAPTURE:XAUUSD:1746686700:SHORT -- net_pnl=+4.87,  terminal=-1.00
_KNOWN_SIGN_MISMATCH_CASES = (
    (4.6248, -1.0809812659899394),
    (3.6473, -1.0504632913637375),
    (-0.6312, 0.5065727699530029),
    (4.867, -1.0001258653241116),
)


def test_known_sign_mismatch_cases_classified_by_total_net_pnl_not_terminal_outcome(tmp_path: Path) -> None:
    records = [
        {
            "strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": net_pnl,
            "snapshot_overrides": {"session_state": "ny"},
        }
        for net_pnl, _terminal in _KNOWN_SIGN_MISMATCH_CASES
    ]
    repo = build_repository(tmp_path, records)
    stats = compute_conditional_statistics(repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert len(stats) == 1
    bucket = stats[0]
    assert bucket.n == 4

    net_pnls = [net_pnl for net_pnl, _ in _KNOWN_SIGN_MISMATCH_CASES]
    expected_favorable = sum(1 for v in net_pnls if v > 0)
    expected_unfavorable = sum(1 for v in net_pnls if v < 0)
    # 3 of the 4 known cases have total_net_pnl > 0; using total_net_pnl (correct) gives 3 favorable/1
    # unfavorable. Using the terminal Outcome's own normalized_result instead (the forbidden field) would
    # give the OPPOSITE: 1 favorable/3 unfavorable -- a materially different, wrong answer.
    assert expected_favorable == 3
    assert expected_unfavorable == 1
    assert bucket.favorable_count == expected_favorable
    assert bucket.unfavorable_count == expected_unfavorable

    terminal_results = [terminal for _, terminal in _KNOWN_SIGN_MISMATCH_CASES]
    wrong_favorable = sum(1 for v in terminal_results if v > 0)
    wrong_unfavorable = sum(1 for v in terminal_results if v < 0)
    assert (bucket.favorable_count, bucket.unfavorable_count) != (wrong_favorable, wrong_unfavorable)
    assert bucket.mean_result == sum(net_pnls) / len(net_pnls)  # computed from total_net_pnl, not terminal

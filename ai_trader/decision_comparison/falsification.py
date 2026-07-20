"""Falsification study orchestrator -- Phase 7 Checkpoint 15. Composes every comparison dimension the
CEO named into one `FalsificationReport` with an explicit `FalsificationVerdict`. The default,
safe verdict is `V1_REMAINS_ACTIVE` -- per the CEO's own explicit rule, absent measured proof of a v2
benefit, v1 remains the active system. `V2_SUPERIOR_CONFIRMED` is not reachable by this function today:
Checkpoint 14's own architecture makes v2's recommendation stream provably identical to v1's, so no
trade-outcome dimension can ever show a v2 benefit under the CURRENT integration design -- reaching
`V2_SUPERIOR_CONFIRMED` would require a future, separately-authorized checkpoint that lets Context
Memory's evidence actually influence a decision, which this project has not authorized.
"""

from __future__ import annotations

from collections.abc import Sequence

from ai_trader.decision_comparison.calibration import evaluate_calibration
from ai_trader.decision_comparison.explanation_quality import score_explanation_quality
from ai_trader.decision_comparison.recommendation import compare_recommendations
from ai_trader.decision_comparison.trade_outcome_proof import prove_trade_outcome_equivalence
from ai_trader.decision_comparison.types import CalibrationSample, FalsificationReport, FalsificationVerdict
from ai_trader.decision_intelligence.types import DecisionReport
from ai_trader.decision_intelligence_v2.types import DecisionReportV2


def run_falsification_study(
    pairs: Sequence[tuple[DecisionReport, DecisionReportV2]],
    calibration_samples: Sequence[CalibrationSample] = (),
) -> FalsificationReport:
    recommendation_comparison = compare_recommendations(pairs)
    trade_outcome_equivalence = prove_trade_outcome_equivalence(recommendation_comparison)
    explanation_quality = score_explanation_quality([v2 for _, v2 in pairs])
    calibration = evaluate_calibration(calibration_samples)

    if trade_outcome_equivalence.equivalence_holds:
        verdict = FalsificationVerdict.V1_REMAINS_ACTIVE
        rationale = (
            "No measurable trade-outcome benefit exists for v2 over v1: their recommendation streams "
            f"are provably identical ({recommendation_comparison.n_compared} compared decision(s), "
            "0 divergences), so expectancy/win-rate/drawdown/false-positive-rate/false-negative-rate/"
            "regime-robustness are identical by construction (see trade_outcome_equivalence.rationale). "
            "v2 adds explanatory context only "
            f"(strictly more explanatory content than v1: {explanation_quality.v2_strictly_more_explanatory_content}), "
            f"and its confidence-calibration skill cannot yet be measured ({calibration.rationale}). "
            "Per the CEO's own explicit falsification rule -- absent proof of a v2 benefit, v1 remains "
            "the active system. This is not a default choice; it is the measured, structurally-proven "
            "result of this study."
        )
    else:
        verdict = FalsificationVerdict.V1_REMAINS_ACTIVE
        rationale = (
            f"v2 diverged from v1 on {recommendation_comparison.divergences} of "
            f"{recommendation_comparison.n_compared} compared decision(s) -- this should be structurally "
            "impossible under Checkpoint 14's own design (see trade_outcome_equivalence.rationale). v1 "
            "remains active pending investigation of the divergence; no superiority claim can be made "
            "from a divergence alone, and no claim of v1 defect is made either without further study."
        )

    return FalsificationReport(
        recommendation_comparison=recommendation_comparison,
        trade_outcome_equivalence=trade_outcome_equivalence,
        explanation_quality=explanation_quality,
        calibration=calibration,
        verdict=verdict,
        rationale=rationale,
    )

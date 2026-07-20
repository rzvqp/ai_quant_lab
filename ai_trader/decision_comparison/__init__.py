"""Decision Intelligence v1-vs-v2 falsification comparison framework -- Phase 7 Checkpoint 15.

Never modifies v1 or v2; reads their outputs only. Goal is falsification, not confirmation -- the CEO's
own explicit instruction. See `falsification.py`'s own module docstring for why `V2_SUPERIOR_CONFIRMED`
is not reachable under the current Checkpoint 14 integration design.
"""

from __future__ import annotations

from ai_trader.decision_comparison.calibration import evaluate_calibration
from ai_trader.decision_comparison.explanation_quality import score_explanation_quality
from ai_trader.decision_comparison.falsification import run_falsification_study
from ai_trader.decision_comparison.recommendation import compare_recommendations
from ai_trader.decision_comparison.trade_outcome_proof import prove_trade_outcome_equivalence
from ai_trader.decision_comparison.types import (
    CalibrationResult,
    CalibrationSample,
    ExplanationQualityResult,
    FalsificationReport,
    FalsificationVerdict,
    RecommendationComparison,
    TradeOutcomeEquivalenceProof,
)

__all__ = [
    "evaluate_calibration",
    "score_explanation_quality",
    "run_falsification_study",
    "compare_recommendations",
    "prove_trade_outcome_equivalence",
    "CalibrationResult",
    "CalibrationSample",
    "ExplanationQualityResult",
    "FalsificationReport",
    "FalsificationVerdict",
    "RecommendationComparison",
    "TradeOutcomeEquivalenceProof",
]

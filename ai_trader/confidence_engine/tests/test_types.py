from __future__ import annotations

import pytest

from ai_trader.confidence_engine.types import (
    CalculationTraceStep,
    ConfidenceAssessment,
    Grade,
    GradeBands,
    ScoreComponents,
)
from ai_trader.scoring_engine.types import Quality


def test_grade_bands_rejects_out_of_order_thresholds() -> None:
    with pytest.raises(ValueError):
        GradeBands(a_threshold=0.5, b_threshold=0.6, c_threshold=0.4)


def test_grade_bands_default_is_valid() -> None:
    bands = GradeBands()
    assert bands.c_threshold <= bands.b_threshold <= bands.a_threshold


def test_assessment_rejects_score_out_of_range() -> None:
    with pytest.raises(ValueError):
        ConfidenceAssessment(
            strategy_id="S1", symbol="XAUUSD", as_of=1, correlation_id="C1", grade=Grade.D, score=1.5,
            components=ScoreComponents(None, None), quality=Quality.WEAK, eligible_for_risk_evaluation=False,
            reason_codes=("X",), calculation_trace=(CalculationTraceStep("A", True),),
        )


def test_assessment_requires_nonempty_calculation_trace() -> None:
    with pytest.raises(ValueError):
        ConfidenceAssessment(
            strategy_id="S1", symbol="XAUUSD", as_of=1, correlation_id="C1", grade=Grade.D, score=0.1,
            components=ScoreComponents(None, None), quality=Quality.WEAK, eligible_for_risk_evaluation=False,
            reason_codes=("X",), calculation_trace=(),
        )


def test_assessment_rejects_eligible_true_with_grade_c_or_d() -> None:
    with pytest.raises(ValueError):
        ConfidenceAssessment(
            strategy_id="S1", symbol="XAUUSD", as_of=1, correlation_id="C1", grade=Grade.C, score=0.5,
            components=ScoreComponents(None, None), quality=Quality.MODERATE, eligible_for_risk_evaluation=True,
            reason_codes=(), calculation_trace=(CalculationTraceStep("A", True),),
        )


def test_assessment_accepts_eligible_true_with_grade_a() -> None:
    assessment = ConfidenceAssessment(
        strategy_id="S1", symbol="XAUUSD", as_of=1, correlation_id="C1", grade=Grade.A, score=0.9,
        components=ScoreComponents(0.9, 0.9), quality=Quality.PREMIUM, eligible_for_risk_evaluation=True,
        reason_codes=(), calculation_trace=(CalculationTraceStep("A", True),),
    )
    assert assessment.eligible_for_risk_evaluation is True


def test_score_components_strategy_health_is_always_none() -> None:
    components = ScoreComponents(context_confidence_component=0.5, recognition_component=0.5)
    assert components.strategy_health_component is None

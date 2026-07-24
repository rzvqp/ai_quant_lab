from __future__ import annotations

from ai_trader.confidence_engine.engine import assess_confidence
from ai_trader.confidence_engine.tests._fixtures import make_market_context_snapshot, make_recognition_result, make_statistics
from ai_trader.confidence_engine.types import ConfidenceEngineConfig, Grade, GradeBands
from ai_trader.context_engine.types import CONTEXT_ENGINE_SCHEMA_VERSION, MarketContextSnapshot, Provenance
from ai_trader.context_engine.types import CalculationTraceStep as ContextTraceStep
from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.recognition_engine.types import Sufficiency


def test_well_formed_inputs_produce_grade_a_and_eligible() -> None:
    assessment = assess_confidence("S1", "C1", make_market_context_snapshot(), make_recognition_result())
    assert assessment.grade is Grade.A
    assert assessment.eligible_for_risk_evaluation is True
    assert assessment.reason_codes == ()


def test_missing_recognition_result_is_optional_not_a_failure() -> None:
    assessment = assess_confidence("S1", "C1", make_market_context_snapshot(), None)
    assert assessment.components.recognition_component is None
    assert assessment.components.context_confidence_component is not None


def test_stale_context_blocks_eligibility_even_at_grade_a() -> None:
    context = make_market_context_snapshot(data_quality_level="STALE")
    assessment = assess_confidence("S1", "C1", context, make_recognition_result())
    assert assessment.eligible_for_risk_evaluation is False
    assert "DATA_STALE" in assessment.reason_codes
    assert "DATA_QUALITY_NOT_OK" in assessment.reason_codes


def test_unauthorized_recognition_pattern_blocks_eligibility() -> None:
    recognition = make_recognition_result(pattern_authorized=False)
    assessment = assess_confidence("S1", "C1", make_market_context_snapshot(), recognition)
    assert assessment.eligible_for_risk_evaluation is False
    assert "RECOGNITION_PATTERN_UNAUTHORIZED" in assessment.reason_codes


def test_insufficient_recognition_evidence_never_boosts_score() -> None:
    recognition = make_recognition_result(sufficiency=Sufficiency.INSUFFICIENT_EVIDENCE, statistics=make_statistics(sufficiency=Sufficiency.INSUFFICIENT_EVIDENCE))
    assessment = assess_confidence("S1", "C1", make_market_context_snapshot(), recognition)
    assert assessment.components.recognition_component == 0.0


def test_low_score_produces_grade_d_and_ineligible() -> None:
    recognition = make_recognition_result(statistics=make_statistics(favorable_rate=0.05, sufficiency=Sufficiency.SUFFICIENT))
    config = ConfidenceEngineConfig(bands=GradeBands(a_threshold=0.99, b_threshold=0.98, c_threshold=0.97))
    assessment = assess_confidence("S1", "C1", make_market_context_snapshot(), recognition, config)
    assert assessment.grade is Grade.D
    assert assessment.eligible_for_risk_evaluation is False
    assert "GRADE_BELOW_ELIGIBLE_THRESHOLD" in assessment.reason_codes


def test_missing_market_intelligence_degrades_gracefully() -> None:
    context = MarketContextSnapshot(
        symbol="XAUUSD", as_of=1, version=CONTEXT_ENGINE_SCHEMA_VERSION, market_intelligence=None,
        edge_intelligence=None, data_quality=DataQualityLevel.INSUFFICIENT, is_stale=False,
        provenance=Provenance(source_schema_versions={}), calculation_trace=(ContextTraceStep("X", True),),
    )
    assessment = assess_confidence("S1", "C1", context, None)
    assert assessment.components.context_confidence_component is None
    assert "MARKET_INTELLIGENCE_UNAVAILABLE" in assessment.reason_codes
    assert assessment.eligible_for_risk_evaluation is False


def test_grade_to_quality_mapping_is_applied() -> None:
    from ai_trader.confidence_engine.types import GRADE_TO_QUALITY

    assessment = assess_confidence("S1", "C1", make_market_context_snapshot(), make_recognition_result())
    assert assessment.quality == GRADE_TO_QUALITY[assessment.grade]


def test_calculation_trace_never_empty() -> None:
    assessment = assess_confidence("S1", "C1", make_market_context_snapshot(), make_recognition_result())
    assert len(assessment.calculation_trace) >= 5


def test_determinism_same_inputs_produce_equal_assessment() -> None:
    context = make_market_context_snapshot()
    recognition = make_recognition_result()
    first = assess_confidence("S1", "C1", context, recognition)
    second = assess_confidence("S1", "C1", context, recognition)
    assert first.grade == second.grade
    assert first.score == second.score

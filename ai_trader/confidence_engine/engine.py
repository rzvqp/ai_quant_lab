"""`assess_confidence` -- Confidence Engine's single public entry point. Pure, read-only: never
constructs or submits a `TradeProposal`/order (CEO: "never automatically executable"). Fail-closed: any
exception degrades to `Grade.D`, `eligible_for_risk_evaluation=False`, never raises."""

from __future__ import annotations

from ai_trader.confidence_engine import reason_codes as rc
from ai_trader.confidence_engine.types import (
    GRADE_TO_QUALITY,
    CalculationTraceStep,
    ConfidenceAssessment,
    ConfidenceEngineConfig,
    Grade,
    GradeBands,
    ScoreComponents,
)
from ai_trader.context_engine.types import MarketContextSnapshot
from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.recognition_engine.types import Sufficiency
from ai_trader.recognition_engine_live.types import RecognitionResult


def _grade_for_score(score: float, bands: GradeBands) -> Grade:
    if score >= bands.a_threshold:
        return Grade.A
    if score >= bands.b_threshold:
        return Grade.B
    if score >= bands.c_threshold:
        return Grade.C
    return Grade.D


def _failed_assessment(strategy_id: str, symbol: str, as_of: int, correlation_id: str, trace: list[CalculationTraceStep]) -> ConfidenceAssessment:
    return ConfidenceAssessment(
        strategy_id=strategy_id, symbol=symbol, as_of=as_of, correlation_id=correlation_id, grade=Grade.D,
        score=0.0, components=ScoreComponents(context_confidence_component=None, recognition_component=None),
        quality=GRADE_TO_QUALITY[Grade.D], eligible_for_risk_evaluation=False,
        reason_codes=(rc.ASSESSMENT_FAILED,), calculation_trace=tuple(trace),
    )


def assess_confidence(
    strategy_id: str, correlation_id: str, context: MarketContextSnapshot,
    recognition: RecognitionResult | None, config: ConfidenceEngineConfig | None = None,
) -> ConfidenceAssessment:
    resolved_config = config if config is not None else ConfidenceEngineConfig()
    trace: list[CalculationTraceStep] = []
    reason_codes: list[str] = []

    try:
        context_component = None
        if context.market_intelligence is not None:
            context_component = context.market_intelligence.confidence.score
        trace.append(CalculationTraceStep(
            "CONTEXT_COMPONENT_COMPUTED", context_component is not None,
            detail=None if context_component is not None else "market_intelligence unavailable or carries no score",
        ))
        if context_component is None:
            reason_codes.append(rc.MARKET_INTELLIGENCE_UNAVAILABLE)

        recognition_component = None
        if recognition is not None:
            if recognition.statistics is not None and recognition.sufficiency is Sufficiency.SUFFICIENT:
                recognition_component = (
                    recognition.statistics.favorable_rate if recognition.statistics.favorable_rate is not None else 0.0
                )
            else:
                recognition_component = 0.0  # conservative: absent/insufficient evidence never boosts a score
        trace.append(CalculationTraceStep("RECOGNITION_COMPONENT_COMPUTED", True, detail=f"value={recognition_component}"))

        components = [c for c in (context_component, recognition_component) if c is not None]
        score = sum(components) / len(components) if components else 0.0
        trace.append(CalculationTraceStep("SCORE_COMPUTED", True, detail=f"score={score:.4f}"))

        grade = _grade_for_score(score, resolved_config.bands)
        quality = GRADE_TO_QUALITY[grade]
        trace.append(CalculationTraceStep("GRADE_ASSIGNED", True, detail=grade.value))
    except Exception as exc:  # noqa: BLE001 -- fail-closed: this is a read-only query with no side
        # effects to protect, but the discipline is applied uniformly with every other module.
        trace.append(CalculationTraceStep("ASSESSMENT_RAISED", False, detail=f"{type(exc).__name__}: {exc}"))
        return _failed_assessment(strategy_id, context.symbol, context.as_of, correlation_id, trace)

    data_quality_ok = context.data_quality is DataQualityLevel.OK
    trace.append(CalculationTraceStep("DATA_QUALITY_CHECKED", data_quality_ok, detail=context.data_quality.value))
    if resolved_config.require_data_quality_ok and not data_quality_ok:
        reason_codes.append(rc.DATA_QUALITY_NOT_OK)

    stale_ok = not context.is_stale
    trace.append(CalculationTraceStep("STALE_CHECKED", stale_ok))
    if resolved_config.require_not_stale and not stale_ok:
        reason_codes.append(rc.DATA_STALE)

    pattern_ok = recognition is None or recognition.pattern_authorized
    trace.append(CalculationTraceStep("PATTERN_AUTHORIZED_CHECKED", pattern_ok))
    if resolved_config.require_pattern_authorized and recognition is not None and not recognition.pattern_authorized:
        reason_codes.append(rc.RECOGNITION_PATTERN_UNAUTHORIZED)

    grade_eligible = grade in (Grade.A, Grade.B)
    if not grade_eligible:
        reason_codes.append(rc.GRADE_BELOW_ELIGIBLE_THRESHOLD)

    eligible = grade_eligible and not reason_codes
    trace.append(CalculationTraceStep("ELIGIBILITY_DETERMINED", eligible, detail=f"grade={grade.value}"))

    return ConfidenceAssessment(
        strategy_id=strategy_id, symbol=context.symbol, as_of=context.as_of, correlation_id=correlation_id,
        grade=grade, score=score, components=ScoreComponents(
            context_confidence_component=context_component, recognition_component=recognition_component,
        ),
        quality=quality, eligible_for_risk_evaluation=eligible, reason_codes=tuple(reason_codes),
        calculation_trace=tuple(trace),
    )

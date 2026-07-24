"""Shared fixture builders for `confidence_engine` tests."""

from __future__ import annotations

from ai_trader.context_engine.engine import build_context_snapshot
from ai_trader.context_engine.types import MarketContextSnapshot
from ai_trader.market_intelligence.tests._fixtures import make_context
from ai_trader.recognition_engine.types import ConditionalStatistics, ContextDimension, Sufficiency
from ai_trader.context_memory.enums import OutcomeKind
from ai_trader.recognition_engine_live.types import CalculationTraceStep, RecognitionResult

AS_OF = 1_700_000_000


def make_market_context_snapshot(**context_overrides: object) -> MarketContextSnapshot:
    return build_context_snapshot(make_context(**context_overrides))  # type: ignore[arg-type]


def make_statistics(**overrides: object) -> ConditionalStatistics:
    kwargs: dict[str, object] = {
        "strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "context_dimension": ContextDimension.SESSION,
        "context_bucket_value": "ny", "n": 30, "favorable_count": 20, "unfavorable_count": 8, "zero_count": 2,
        "favorable_rate": 20 / 30, "unfavorable_rate": 8 / 30, "mean_result": 1.5, "median_result": 1.0,
        "stdev_result": 2.0, "min_result": -3.0, "max_result": 6.0, "sufficiency": Sufficiency.SUFFICIENT,
        "min_observations_threshold": 25, "data_provenance": "test",
    }
    kwargs.update(overrides)
    return ConditionalStatistics(**kwargs)  # type: ignore[arg-type]


def make_recognition_result(**overrides: object) -> RecognitionResult:
    kwargs: dict[str, object] = {
        "strategy_id": "S1", "pattern_id": "REC-SESSION-STRATEGY", "pattern_version": "v1", "as_of": AS_OF,
        "correlation_id": "C1", "context_bucket_value": "ny", "statistics": make_statistics(),
        "sufficiency": Sufficiency.SUFFICIENT, "pattern_authorized": True, "reason_codes": (),
        "calculation_trace": (CalculationTraceStep("X", True),),
    }
    kwargs.update(overrides)
    return RecognitionResult(**kwargs)  # type: ignore[arg-type]

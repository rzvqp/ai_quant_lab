from __future__ import annotations

import pytest

from ai_trader.recognition_engine_live.tests._fixtures import make_candidate
from ai_trader.recognition_engine_live.types import CalculationTraceStep, RecognitionResult
from ai_trader.recognition_engine.types import Sufficiency


def test_candidate_requires_nonempty_strategy_id() -> None:
    with pytest.raises(ValueError):
        make_candidate(strategy_id="")


def test_candidate_requires_nonempty_pattern_id() -> None:
    with pytest.raises(ValueError):
        make_candidate(pattern_id="")


def test_candidate_requires_nonempty_correlation_id() -> None:
    with pytest.raises(ValueError):
        make_candidate(correlation_id="")


def test_result_requires_nonempty_calculation_trace() -> None:
    with pytest.raises(ValueError):
        RecognitionResult(
            strategy_id="S1", pattern_id="P1", pattern_version="v1", as_of=1, correlation_id="C1",
            context_bucket_value=None, statistics=None, sufficiency=Sufficiency.INSUFFICIENT_EVIDENCE,
            pattern_authorized=False, reason_codes=(), calculation_trace=(),
        )
    RecognitionResult(
        strategy_id="S1", pattern_id="P1", pattern_version="v1", as_of=1, correlation_id="C1",
        context_bucket_value=None, statistics=None, sufficiency=Sufficiency.INSUFFICIENT_EVIDENCE,
        pattern_authorized=False, reason_codes=(), calculation_trace=(CalculationTraceStep("X", True),),
    )

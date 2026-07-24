from __future__ import annotations

import pytest

from ai_trader.execution_orchestrator.tests._fixtures import make_candidate
from ai_trader.execution_orchestrator.types import ExecutionMode, OrchestrationResult
from ai_trader.execution_orchestrator.types import CalculationTraceStep


def test_candidate_requires_nonempty_strategy_id() -> None:
    with pytest.raises(ValueError):
        make_candidate(strategy_id="")


def test_candidate_requires_concrete_direction_type() -> None:
    with pytest.raises(TypeError):
        make_candidate(direction="LONG")


def test_result_requires_nonempty_calculation_trace() -> None:
    with pytest.raises(ValueError):
        OrchestrationResult(
            correlation_id="C1", strategy_id="S1", symbol="XAUUSD", as_of=1, mode=ExecutionMode.DRY_RUN,
            approved=False, context=None, recognition=None, confidence=None, risk_decision=None,
            portfolio_decision=None, order_result=None, reason_codes=("X",), calculation_trace=(),
        )


def test_denied_result_requires_reason_codes() -> None:
    with pytest.raises(ValueError):
        OrchestrationResult(
            correlation_id="C1", strategy_id="S1", symbol="XAUUSD", as_of=1, mode=ExecutionMode.DRY_RUN,
            approved=False, context=None, recognition=None, confidence=None, risk_decision=None,
            portfolio_decision=None, order_result=None, reason_codes=(),
            calculation_trace=(CalculationTraceStep("X", True),),
        )


def test_approved_result_requires_order_result() -> None:
    with pytest.raises(ValueError):
        OrchestrationResult(
            correlation_id="C1", strategy_id="S1", symbol="XAUUSD", as_of=1, mode=ExecutionMode.DRY_RUN,
            approved=True, context=None, recognition=None, confidence=None, risk_decision=None,
            portfolio_decision=None, order_result=None, reason_codes=(),
            calculation_trace=(CalculationTraceStep("X", True),),
        )

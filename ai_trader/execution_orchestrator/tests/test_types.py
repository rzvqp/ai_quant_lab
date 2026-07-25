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


def test_candidate_rejects_long_with_stop_above_entry() -> None:
    """Decision Logic Audit #2: a LONG's stop must sit strictly below entry -- the only prior check
    anywhere in the pipeline was `abs(entry - stop) > 0`, which a stop on the WRONG side of entry
    satisfies just as well as a correct one. Must be rejected, never silently corrected."""
    from ai_trader.signal_engine.types import Direction

    with pytest.raises(ValueError):
        make_candidate(direction=Direction.LONG, entry=2000.0, stop=2010.0)


def test_candidate_rejects_long_with_stop_equal_to_entry() -> None:
    from ai_trader.signal_engine.types import Direction

    with pytest.raises(ValueError):
        make_candidate(direction=Direction.LONG, entry=2000.0, stop=2000.0)


def test_candidate_rejects_short_with_stop_below_entry() -> None:
    from ai_trader.signal_engine.types import Direction

    with pytest.raises(ValueError):
        make_candidate(direction=Direction.SHORT, entry=2000.0, stop=1990.0)


def test_candidate_accepts_correctly_sided_stops() -> None:
    from ai_trader.signal_engine.types import Direction

    make_candidate(direction=Direction.LONG, entry=2000.0, stop=1990.0)
    make_candidate(direction=Direction.SHORT, entry=2000.0, stop=2010.0)


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

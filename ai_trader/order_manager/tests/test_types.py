from __future__ import annotations

import pytest

from ai_trader.execution_engine.types import OrderState
from ai_trader.order_manager.tests._fixtures import make_intent
from ai_trader.order_manager.types import OrderExecutionResult
from ai_trader.signal_engine.types import Direction


def test_intent_requires_nonempty_proposal_id() -> None:
    with pytest.raises(ValueError):
        make_intent(proposal_id="")


def test_intent_requires_nonempty_correlation_id() -> None:
    with pytest.raises(ValueError):
        make_intent(correlation_id="")


def test_intent_requires_nonempty_strategy_id() -> None:
    with pytest.raises(ValueError):
        make_intent(strategy_id="")


def test_intent_requires_nonempty_symbol() -> None:
    with pytest.raises(ValueError):
        make_intent(symbol="")


def test_intent_requires_concrete_direction_type() -> None:
    with pytest.raises(TypeError):
        make_intent(direction="LONG")


def test_intent_requires_positive_volume() -> None:
    with pytest.raises(ValueError):
        make_intent(volume=0.0)


def test_intent_requires_nonempty_comment() -> None:
    with pytest.raises(ValueError):
        make_intent(comment="")


def test_intent_valid_construction_succeeds() -> None:
    intent = make_intent()
    assert intent.direction is Direction.LONG
    assert intent.volume == 0.2


def test_execution_result_requires_dry_run_true() -> None:
    with pytest.raises(ValueError):
        OrderExecutionResult(
            order_request_id="R1", client_order_id="C1", state=OrderState.ACKNOWLEDGED, dry_run=False,
        )


def test_execution_result_dry_run_true_succeeds() -> None:
    result = OrderExecutionResult(
        order_request_id="R1", client_order_id="C1", state=OrderState.ACKNOWLEDGED, dry_run=True,
    )
    assert result.dry_run is True

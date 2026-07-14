"""Tests for :mod:`ai_trader.execution_engine.types` -- basic construction/equality/closed-vocabulary
sanity, matching every prior module's own light ``test_types.py``.
"""

from __future__ import annotations

from ai_trader.execution_engine.types import (
    PRE_SUBMIT_STATES,
    TERMINAL_STATES,
    BracketLegs,
    BrokerCapabilities,
    MarketStatus,
    OrderConstraints,
    OrderIntent,
    OrderRefs,
    OrderRequest,
    OrderSide,
    OrderState,
    OrderType,
    TimeInForce,
)
from ai_trader.signal_engine.types import Direction


class TestOrderStateVocabulary:
    def test_exactly_eleven_states(self) -> None:
        assert len(list(OrderState)) == 11

    def test_terminal_states_are_exactly_five(self) -> None:
        assert TERMINAL_STATES == {
            OrderState.FILLED, OrderState.CANCELLED, OrderState.REJECTED, OrderState.EXPIRED, OrderState.FAILED,
        }

    def test_pre_submit_states_are_exactly_three(self) -> None:
        assert PRE_SUBMIT_STATES == {OrderState.CREATED, OrderState.VALIDATED, OrderState.QUEUED}

    def test_terminal_and_pre_submit_are_disjoint(self) -> None:
        assert TERMINAL_STATES.isdisjoint(PRE_SUBMIT_STATES)


class TestOrderTypeVocabulary:
    def test_exactly_six_order_types(self) -> None:
        assert len(list(OrderType)) == 6

    def test_exactly_four_time_in_force(self) -> None:
        assert len(list(TimeInForce)) == 4


class TestOrderRequestConstruction:
    def test_minimal_market_order_builds(self) -> None:
        order = OrderRequest(
            order_schema_version="1.0.0", execution_engine_version="1.0.0",
            order_request_id="REQ-1", client_order_id="CID-1", decision_id="D1",
            strategy_id="S1", symbol="XAUUSD", timestamp=1, as_of=1,
            side=OrderSide.BUY, direction=Direction.LONG, intent=OrderIntent.OPEN,
            order_type=OrderType.MARKET, time_in_force=TimeInForce.GTC, quantity=1.0,
            constraints=OrderConstraints(max_slippage=0.1, reduce_only=False, post_only=False),
            refs=OrderRefs(risk_schema_version="1.0.0", risk_policy_version="1.0.0"),
        )
        assert order.limit_price is None
        assert order.bracket is None

    def test_bracket_order_carries_legs(self) -> None:
        order = OrderRequest(
            order_schema_version="1.0.0", execution_engine_version="1.0.0",
            order_request_id="REQ-1", client_order_id="CID-1", decision_id="D1",
            strategy_id="S1", symbol="XAUUSD", timestamp=1, as_of=1,
            side=OrderSide.BUY, direction=Direction.LONG, intent=OrderIntent.OPEN,
            order_type=OrderType.BRACKET, time_in_force=TimeInForce.GTC, quantity=1.0,
            limit_price=100.0, bracket=BracketLegs(take_profit=102.0, stop_loss=99.0),
            constraints=OrderConstraints(max_slippage=None, reduce_only=False, post_only=False),
            refs=OrderRefs(risk_schema_version="1.0.0", risk_policy_version="1.0.0"),
        )
        assert order.bracket is not None
        assert order.bracket.take_profit == 102.0


class TestBrokerCapabilities:
    def test_status_for_unknown_symbol_is_unknown(self) -> None:
        caps = BrokerCapabilities(
            supported_order_types=frozenset({OrderType.MARKET}),
            supported_time_in_force=frozenset({TimeInForce.GTC}),
            tick_size=0.01, lot_step=0.01, min_qty=0.01, max_qty=100.0,
        )
        assert caps.status_for("XAUUSD") is MarketStatus.UNKNOWN

    def test_status_for_declared_symbol(self) -> None:
        caps = BrokerCapabilities(
            supported_order_types=frozenset({OrderType.MARKET}),
            supported_time_in_force=frozenset({TimeInForce.GTC}),
            tick_size=0.01, lot_step=0.01, min_qty=0.01, max_qty=100.0,
            market_status={"XAUUSD": MarketStatus.OPEN},
        )
        assert caps.status_for("XAUUSD") is MarketStatus.OPEN

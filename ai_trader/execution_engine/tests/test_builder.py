"""Tests for :mod:`ai_trader.execution_engine.builder`."""

from __future__ import annotations

from dataclasses import replace

from ai_trader.execution_engine.builder import BuildOutcome, build_flatten_order, build_order
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.tests.fixtures.fake_broker import make_capabilities
from ai_trader.execution_engine.tests.fixtures.fake_decision import (
    make_allow_decision,
    make_deny_decision,
    make_reduce_only_allow_decision,
)
from ai_trader.execution_engine.types import OrderIntent, OrderRequest, OrderSide, OrderType
from ai_trader.risk_manager.types import OpenPosition
from ai_trader.signal_engine.types import Direction

CONFIG = ExecConfig()
CAPS = make_capabilities()


def _sizing(outcome: BuildOutcome) -> OrderRequest:
    assert outcome.success and outcome.order is not None
    return outcome.order


class TestHappyPath:
    def test_allow_decision_with_stop_and_target_builds_bracket(self) -> None:
        decision, portfolio = make_allow_decision(entry=100.0, stop=99.0, target=102.0)
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert order.order_type is OrderType.BRACKET
        assert order.bracket is not None
        assert order.bracket.stop_loss == 99.0
        assert order.bracket.take_profit == 102.0
        assert order.limit_price == 100.0
        assert order.side is OrderSide.BUY
        assert order.intent is OrderIntent.OPEN

    def test_short_decision_produces_sell_side(self) -> None:
        decision, portfolio = make_allow_decision(direction="SHORT", entry=100.0, stop=101.0, target=98.0)
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert order.side is OrderSide.SELL
        assert order.direction is Direction.SHORT

    def test_quantity_matches_sizing_size_units(self) -> None:
        decision, portfolio = make_allow_decision()
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert decision.sizing is not None
        assert order.quantity <= decision.sizing.size_units  # rounding may only reduce, never increase

    def test_client_order_id_is_derived_from_decision_id(self) -> None:
        decision, portfolio = make_allow_decision()
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert decision.decision_id in order.client_order_id
        assert decision.decision_id in order.order_request_id

    def test_timestamp_equals_as_of_never_wall_clock(self) -> None:
        decision, portfolio = make_allow_decision()
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert order.timestamp == decision.as_of
        assert order.as_of == decision.as_of

    def test_refs_echo_risk_versions(self) -> None:
        decision, portfolio = make_allow_decision()
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert order.refs.risk_schema_version == decision.risk_schema_version
        assert order.refs.risk_policy_version == decision.risk_policy_version

    def test_broker_capabilities_ref_is_echoed(self) -> None:
        decision, portfolio = make_allow_decision()
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert order.broker_capabilities_ref is not None
        assert order.broker_capabilities_ref.tick_size == CAPS.tick_size


class TestDenyIsNeverBuilt:
    def test_deny_decision_has_no_sizing_or_constraints_and_fails_to_build(self) -> None:
        """A DENY decision always carries ``direction=NONE`` (Risk Manager's own DENY sentinel,
        ``risk_manager/assembler.py``) as well as ``sizing=None``/``constraints=None`` -- either alone
        is sufficient to refuse building an order; the builder reports whichever it hits first."""
        decision, portfolio = make_deny_decision()
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        assert outcome.success is False
        assert outcome.order is None
        assert outcome.reason is not None
        assert "INVALID_DIRECTION" in outcome.reason or "MISSING_SIZING_OR_CONSTRAINTS" in outcome.reason


class TestInvalidDirection:
    def test_direction_none_fails_to_build(self) -> None:
        decision, portfolio = make_allow_decision()
        broken = replace(decision, direction=Direction.NONE)
        outcome = build_order(broken, portfolio, CAPS, CONFIG)
        assert outcome.success is False
        assert outcome.reason is not None and "INVALID_DIRECTION" in outcome.reason


class TestReduceOnly:
    def test_reduce_only_produces_market_reduce_only_order(self) -> None:
        decision, portfolio = make_reduce_only_allow_decision()
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert order.order_type is OrderType.MARKET
        assert order.constraints.reduce_only is True
        assert order.bracket is None

    def test_reduce_only_long_position_closes_with_sell(self) -> None:
        decision, portfolio = make_reduce_only_allow_decision(direction="LONG")
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert order.side is OrderSide.SELL

    def test_reduce_only_short_position_closes_with_buy(self) -> None:
        decision, portfolio = make_reduce_only_allow_decision(direction="SHORT", entry=100.0, stop=101.0)
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert order.side is OrderSide.BUY

    def test_reduce_only_full_size_close_is_close_intent(self) -> None:
        decision, portfolio = make_reduce_only_allow_decision(size_units=1.0)  # smaller than sizing
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert order.intent is OrderIntent.CLOSE  # order qty (from sizing) >= the tiny existing position

    def test_reduce_only_partial_close_is_reduce_intent(self) -> None:
        decision, portfolio = make_reduce_only_allow_decision(size_units=100_000.0)  # much bigger position
        outcome = build_order(decision, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert order.intent is OrderIntent.REDUCE


class TestTickAndLotNormalization:
    def test_price_rounds_to_tick_size(self) -> None:
        decision, portfolio = make_allow_decision(entry=100.003, stop=99.003, target=102.003)
        caps = make_capabilities(tick_size=0.01)
        outcome = build_order(decision, portfolio, caps, CONFIG)
        order = _sizing(outcome)
        assert order.limit_price is not None
        assert round(order.limit_price / 0.01) == order.limit_price / 0.01  # exact multiple after rounding
        assert abs(order.limit_price - 100.0) < 0.02

    def test_quantity_rounds_to_lot_step(self) -> None:
        decision, portfolio = make_allow_decision()
        caps = make_capabilities(lot_step=0.5)
        outcome = build_order(decision, portfolio, caps, CONFIG)
        order = _sizing(outcome)
        assert (order.quantity / 0.5) == round(order.quantity / 0.5)

    def test_rounding_disabled_leaves_raw_values(self) -> None:
        decision, portfolio = make_allow_decision(entry=100.003)
        config = replace(CONFIG, rounding=replace(CONFIG.rounding, round_prices=False))
        caps = make_capabilities(tick_size=0.01)
        outcome = build_order(decision, portfolio, caps, config)
        order = _sizing(outcome)
        assert order.limit_price == 100.003


class TestQuantityLimits:
    def test_quantity_clamped_to_max_qty(self) -> None:
        decision, portfolio = make_allow_decision()
        caps = make_capabilities(max_qty=1.0)
        outcome = build_order(decision, portfolio, caps, CONFIG)
        order = _sizing(outcome)
        assert order.quantity <= 1.0

    def test_quantity_below_min_qty_fails_to_build(self) -> None:
        decision, portfolio = make_allow_decision()
        caps = make_capabilities(min_qty=1_000_000.0, max_qty=2_000_000.0)
        outcome = build_order(decision, portfolio, caps, CONFIG)
        assert outcome.success is False
        assert outcome.reason is not None and "QTY_BELOW_MIN" in outcome.reason

    def test_max_qty_clamp_then_below_min_fails(self) -> None:
        """The notional-cap-then-below-min interaction (mirrors the Risk Manager's own precedent):
        max_qty clamps the quantity down below min_qty -> a genuine SIZE_BELOW_MIN-style failure."""
        decision, portfolio = make_allow_decision()
        caps = make_capabilities(min_qty=150.0, max_qty=10.0)
        outcome = build_order(decision, portfolio, caps, CONFIG)
        assert outcome.success is False
        assert outcome.reason is not None and "QTY_BELOW_MIN" in outcome.reason


class TestUnsupportedCapabilities:
    def test_unsupported_order_type_fails_to_build(self) -> None:
        decision, portfolio = make_allow_decision()
        from ai_trader.execution_engine.types import BrokerCapabilities, TimeInForce
        caps = BrokerCapabilities(
            supported_order_types=frozenset({OrderType.MARKET}),  # BRACKET not supported
            supported_time_in_force=frozenset({TimeInForce.GTC, TimeInForce.IOC}),
            tick_size=0.01, lot_step=0.01, min_qty=0.01, max_qty=1_000_000.0,
        )
        outcome = build_order(decision, portfolio, caps, CONFIG)
        assert outcome.success is False
        assert outcome.reason is not None and "UNSUPPORTED_ORDER_TYPE" in outcome.reason

    def test_unsupported_time_in_force_fails_to_build(self) -> None:
        decision, portfolio = make_allow_decision()
        from ai_trader.execution_engine.types import BrokerCapabilities, TimeInForce
        caps = BrokerCapabilities(
            supported_order_types=frozenset({OrderType.MARKET, OrderType.LIMIT, OrderType.BRACKET}),
            supported_time_in_force=frozenset({TimeInForce.IOC}),  # GTC (open default) not supported
            tick_size=0.01, lot_step=0.01, min_qty=0.01, max_qty=1_000_000.0,
        )
        outcome = build_order(decision, portfolio, caps, CONFIG)
        assert outcome.success is False
        assert outcome.reason is not None and "UNSUPPORTED_TIME_IN_FORCE" in outcome.reason


class TestMaxSlippage:
    def test_marketable_order_without_max_slippage_fails_to_build(self) -> None:
        decision, portfolio = make_allow_decision(entry=100.0, stop=99.0, target=102.0)
        assert decision.constraints is not None
        no_slippage = replace(decision, constraints=replace(decision.constraints, entry=None, max_slippage=None))
        outcome = build_order(no_slippage, portfolio, CAPS, CONFIG)
        assert outcome.success is False
        assert outcome.reason is not None and "MISSING_MAX_SLIPPAGE" in outcome.reason


class TestFlattenOrder:
    def test_builds_a_reduce_only_market_close(self) -> None:
        position = OpenPosition(
            symbol="XAUUSD", strategy_id="S1", direction=Direction.LONG, size_units=5.0,
            entry_price=100.0, opened_bars_ago=3, risk_pct=0.005,
        )
        outcome = build_flatten_order(position, CAPS, CONFIG, as_of=1, risk_schema_version="1.0.0", risk_policy_version="1.0.0")
        assert outcome.success is True
        order = _sizing(outcome)
        assert order.order_type is OrderType.MARKET
        assert order.constraints.reduce_only is True
        assert order.intent is OrderIntent.CLOSE
        assert order.side is OrderSide.SELL  # closing a LONG

    def test_short_position_flatten_buys(self) -> None:
        position = OpenPosition(
            symbol="XAUUSD", strategy_id="S1", direction=Direction.SHORT, size_units=5.0,
            entry_price=100.0, opened_bars_ago=3, risk_pct=0.005,
        )
        outcome = build_flatten_order(position, CAPS, CONFIG, as_of=1, risk_schema_version="1.0.0", risk_policy_version="1.0.0")
        order = _sizing(outcome)
        assert order.side is OrderSide.BUY

    def test_flatten_client_order_id_is_idempotent_per_position_and_as_of(self) -> None:
        position = OpenPosition(
            symbol="XAUUSD", strategy_id="S1", direction=Direction.LONG, size_units=5.0,
            entry_price=100.0, opened_bars_ago=3, risk_pct=0.005,
        )
        first = build_flatten_order(position, CAPS, CONFIG, as_of=1, risk_schema_version="1.0.0", risk_policy_version="1.0.0")
        second = build_flatten_order(position, CAPS, CONFIG, as_of=1, risk_schema_version="1.0.0", risk_policy_version="1.0.0")
        assert _sizing(first).client_order_id == _sizing(second).client_order_id


class TestDeterminism:
    def test_identical_inputs_produce_identical_order(self) -> None:
        decision, portfolio = make_allow_decision()
        first = build_order(decision, portfolio, CAPS, CONFIG)
        second = build_order(decision, portfolio, CAPS, CONFIG)
        assert first == second


class TestNoRoundingIncrement:
    def test_zero_tick_size_passes_prices_through(self) -> None:
        decision, portfolio = make_allow_decision(entry=100.0037)
        caps = make_capabilities(tick_size=0.0)
        outcome = build_order(decision, portfolio, caps, CONFIG)
        order = _sizing(outcome)
        assert order.limit_price == 100.0037

    def test_zero_lot_step_passes_quantity_through(self) -> None:
        decision, portfolio = make_allow_decision()
        assert decision.sizing is not None
        caps = make_capabilities(lot_step=0.0)
        outcome = build_order(decision, portfolio, caps, CONFIG)
        order = _sizing(outcome)
        assert order.quantity == decision.sizing.size_units


class TestConcreteDirectionMissingSizing:
    def test_allow_shaped_decision_with_sizing_stripped_fails_to_build(self) -> None:
        """Distinct from a genuine DENY (which also carries direction=NONE): a concrete-direction
        decision that is missing sizing/constraints must be refused for THAT reason specifically."""
        decision, portfolio = make_allow_decision()
        broken = replace(decision, sizing=None)
        outcome = build_order(broken, portfolio, CAPS, CONFIG)
        assert outcome.success is False
        assert outcome.reason is not None and "MISSING_SIZING_OR_CONSTRAINTS" in outcome.reason


class TestOrderTypeMappingWithoutABracket:
    def test_entry_only_no_stop_no_target_is_a_plain_limit(self) -> None:
        decision, portfolio = make_allow_decision()
        assert decision.constraints is not None
        no_stop_no_target = replace(decision, constraints=replace(decision.constraints, stop=None, target=None))
        outcome = build_order(no_stop_no_target, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert order.order_type is OrderType.LIMIT
        assert order.bracket is None
        assert order.limit_price == decision.constraints.entry

    def test_no_entry_no_stop_no_target_is_a_plain_market(self) -> None:
        decision, portfolio = make_allow_decision()
        assert decision.constraints is not None
        nothing = replace(
            decision, constraints=replace(decision.constraints, entry=None, stop=None, target=None),
        )
        outcome = build_order(nothing, portfolio, CAPS, CONFIG)
        order = _sizing(outcome)
        assert order.order_type is OrderType.MARKET
        assert order.limit_price is None
        assert order.bracket is None


class TestFlattenOrderFailureModes:
    def test_flatten_invalid_direction_fails_to_build(self) -> None:
        position = OpenPosition(
            symbol="XAUUSD", strategy_id="S1", direction=Direction.NONE, size_units=5.0,
            entry_price=100.0, opened_bars_ago=3, risk_pct=0.005,
        )
        outcome = build_flatten_order(position, CAPS, CONFIG, as_of=1, risk_schema_version="1.0.0", risk_policy_version="1.0.0")
        assert outcome.success is False
        assert outcome.reason is not None and "INVALID_DIRECTION" in outcome.reason

    def test_flatten_quantity_below_min_fails_to_build(self) -> None:
        position = OpenPosition(
            symbol="XAUUSD", strategy_id="S1", direction=Direction.LONG, size_units=0.001,
            entry_price=100.0, opened_bars_ago=3, risk_pct=0.005,
        )
        caps = make_capabilities(min_qty=1.0)
        outcome = build_flatten_order(position, caps, CONFIG, as_of=1, risk_schema_version="1.0.0", risk_policy_version="1.0.0")
        assert outcome.success is False
        assert outcome.reason is not None and "QTY_BELOW_MIN" in outcome.reason

    def test_flatten_unsupported_market_order_type_fails_to_build(self) -> None:
        from ai_trader.execution_engine.types import BrokerCapabilities, TimeInForce
        position = OpenPosition(
            symbol="XAUUSD", strategy_id="S1", direction=Direction.LONG, size_units=5.0,
            entry_price=100.0, opened_bars_ago=3, risk_pct=0.005,
        )
        caps = BrokerCapabilities(
            supported_order_types=frozenset({OrderType.LIMIT}),  # MARKET not supported
            supported_time_in_force=frozenset({TimeInForce.IOC, TimeInForce.GTC}),
            tick_size=0.01, lot_step=0.01, min_qty=0.01, max_qty=1_000_000.0,
        )
        outcome = build_flatten_order(position, caps, CONFIG, as_of=1, risk_schema_version="1.0.0", risk_policy_version="1.0.0")
        assert outcome.success is False
        assert outcome.reason is not None and "UNSUPPORTED_ORDER_TYPE" in outcome.reason

    def test_flatten_unsupported_time_in_force_fails_to_build(self) -> None:
        from ai_trader.execution_engine.types import BrokerCapabilities, TimeInForce
        position = OpenPosition(
            symbol="XAUUSD", strategy_id="S1", direction=Direction.LONG, size_units=5.0,
            entry_price=100.0, opened_bars_ago=3, risk_pct=0.005,
        )
        caps = BrokerCapabilities(
            supported_order_types=frozenset({OrderType.MARKET}),
            supported_time_in_force=frozenset({TimeInForce.GTC}),  # close TIF (IOC) not supported
            tick_size=0.01, lot_step=0.01, min_qty=0.01, max_qty=1_000_000.0,
        )
        outcome = build_flatten_order(position, caps, CONFIG, as_of=1, risk_schema_version="1.0.0", risk_policy_version="1.0.0")
        assert outcome.success is False
        assert outcome.reason is not None and "UNSUPPORTED_TIME_IN_FORCE" in outcome.reason

"""Tests for :mod:`ai_trader.execution_engine.validator`."""

from __future__ import annotations

from dataclasses import replace

from ai_trader.execution_engine.builder import build_order
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.tests.fixtures.fake_broker import make_capabilities
from ai_trader.execution_engine.tests.fixtures.fake_decision import make_allow_decision
from ai_trader.execution_engine.types import MarketStatus, OrderRequest, OrderType, TimeInForce
from ai_trader.execution_engine.validator import validate_order
from ai_trader.risk_manager.types import OpenPosition, PortfolioState
from ai_trader.signal_engine.types import Direction

CONFIG = ExecConfig()
CAPS = make_capabilities()


def _built_order() -> tuple[OrderRequest, PortfolioState]:
    decision, portfolio = make_allow_decision()
    outcome = build_order(decision, portfolio, CAPS, CONFIG)
    assert outcome.success and outcome.order is not None
    return outcome.order, portfolio


class TestHappyPath:
    def test_a_correctly_built_order_is_valid(self) -> None:
        order, portfolio = _built_order()
        result = validate_order(order, CAPS, portfolio)
        assert result.valid is True
        assert result.reasons == ()


class TestDirectionValidation:
    def test_open_with_mismatched_side_is_invalid(self) -> None:
        order, portfolio = _built_order()
        from ai_trader.execution_engine.types import OrderSide
        broken = replace(order, side=OrderSide.SELL)  # LONG+OPEN should be BUY
        result = validate_order(broken, CAPS, portfolio)
        assert result.valid is False
        assert any("DIRECTION_MISMATCH" in r for r in result.reasons)


class TestPositionLimitConsistency:
    def test_open_order_when_position_already_open_is_invalid(self) -> None:
        order, _portfolio = _built_order()
        existing = OpenPosition(
            symbol=order.symbol, strategy_id=order.strategy_id, direction=Direction.LONG,
            size_units=1.0, entry_price=100.0, opened_bars_ago=1, risk_pct=0.001,
        )
        from ai_trader.risk_manager.tests.fixtures.fake_opportunity import make_portfolio
        portfolio_with_position = make_portfolio(open_positions=(existing,))
        result = validate_order(order, CAPS, portfolio_with_position)
        assert result.valid is False
        assert any("POSITION_LIMIT_CONSISTENCY" in r for r in result.reasons)

    def test_open_order_with_no_matching_position_is_fine(self) -> None:
        order, portfolio = _built_order()
        result = validate_order(order, CAPS, portfolio)
        assert result.valid is True


class TestTickSize:
    def test_price_not_a_multiple_of_tick_is_invalid(self) -> None:
        order, portfolio = _built_order()
        assert order.limit_price is not None
        broken = replace(order, limit_price=order.limit_price + 0.0037)
        result = validate_order(broken, CAPS, portfolio)
        assert result.valid is False
        assert any("TICK_SIZE" in r for r in result.reasons)


class TestLotSize:
    def test_quantity_not_a_multiple_of_lot_step_is_invalid(self) -> None:
        order, portfolio = _built_order()
        broken = replace(order, quantity=order.quantity + 0.0037)
        result = validate_order(broken, CAPS, portfolio)
        assert result.valid is False
        assert any("LOT_SIZE" in r for r in result.reasons)


class TestQuantityBounds:
    def test_quantity_below_min_qty_is_invalid(self) -> None:
        order, portfolio = _built_order()
        broken = replace(order, quantity=0.0001)
        result = validate_order(broken, CAPS, portfolio)
        assert result.valid is False
        assert any("MIN_QTY" in r for r in result.reasons)

    def test_quantity_above_max_qty_is_invalid(self) -> None:
        order, portfolio = _built_order()
        broken = replace(order, quantity=CAPS.max_qty + 1000.0)
        result = validate_order(broken, CAPS, portfolio)
        assert result.valid is False
        assert any("MAX_QTY" in r for r in result.reasons)


class TestTimeRestrictions:
    """Regression guard (adversarial review, MEDIUM finding): §8 names a "time restrictions" check;
    the module previously had no function for it at all."""

    def test_reduce_only_with_gtc_is_invalid(self) -> None:
        order, portfolio = _built_order()
        reduce_gtc = replace(
            order, constraints=replace(order.constraints, reduce_only=True), time_in_force=TimeInForce.GTC,
        )
        result = validate_order(reduce_gtc, CAPS, portfolio)
        assert result.valid is False
        assert any("TIME_RESTRICTIONS" in r for r in result.reasons)

    def test_reduce_only_with_ioc_is_fine(self) -> None:
        order, portfolio = _built_order()
        reduce_ioc = replace(
            order, constraints=replace(order.constraints, reduce_only=True), time_in_force=TimeInForce.IOC,
        )
        result = validate_order(reduce_ioc, CAPS, portfolio)
        assert not any("TIME_RESTRICTIONS" in r for r in result.reasons)

    def test_opening_order_with_gtc_is_fine(self) -> None:
        order, portfolio = _built_order()
        assert order.constraints.reduce_only is False
        assert order.time_in_force is TimeInForce.GTC
        result = validate_order(order, CAPS, portfolio)
        assert not any("TIME_RESTRICTIONS" in r for r in result.reasons)


class TestSlippage:
    def test_marketable_order_without_slippage_is_invalid(self) -> None:
        order, portfolio = _built_order()
        marketable = replace(order, limit_price=None, order_type=OrderType.MARKET, bracket=None,
                              constraints=replace(order.constraints, max_slippage=None))
        result = validate_order(marketable, CAPS, portfolio)
        assert result.valid is False
        assert any("SLIPPAGE_LIMITS" in r for r in result.reasons)

    def test_negative_slippage_is_invalid(self) -> None:
        order, portfolio = _built_order()
        marketable = replace(order, limit_price=None, order_type=OrderType.MARKET, bracket=None,
                              constraints=replace(order.constraints, max_slippage=-0.1))
        result = validate_order(marketable, CAPS, portfolio)
        assert result.valid is False


class TestMarketStatus:
    def test_closed_market_is_invalid(self) -> None:
        order, portfolio = _built_order()
        closed_caps = make_capabilities(market_status=MarketStatus.CLOSED)
        result = validate_order(order, closed_caps, portfolio)
        assert result.valid is False
        assert any("MARKET_STATUS" in r for r in result.reasons)

    def test_unknown_market_status_is_invalid(self) -> None:
        order, portfolio = _built_order()
        from ai_trader.execution_engine.types import BrokerCapabilities
        unknown_caps = BrokerCapabilities(
            supported_order_types=CAPS.supported_order_types,
            supported_time_in_force=CAPS.supported_time_in_force,
            tick_size=CAPS.tick_size, lot_step=CAPS.lot_step, min_qty=CAPS.min_qty, max_qty=CAPS.max_qty,
        )  # no market_status declared for the symbol -> UNKNOWN
        result = validate_order(order, unknown_caps, portfolio)
        assert result.valid is False


class TestUnsupportedCapabilities:
    def test_order_type_not_supported_is_invalid(self) -> None:
        order, portfolio = _built_order()
        from ai_trader.execution_engine.types import BrokerCapabilities
        narrow_caps = BrokerCapabilities(
            supported_order_types=frozenset({OrderType.MARKET}),
            supported_time_in_force=CAPS.supported_time_in_force,
            tick_size=CAPS.tick_size, lot_step=CAPS.lot_step, min_qty=CAPS.min_qty, max_qty=CAPS.max_qty,
            market_status=CAPS.market_status,
        )
        result = validate_order(order, narrow_caps, portfolio)
        assert result.valid is False
        assert any("UNSUPPORTED_ORDER_TYPE" in r for r in result.reasons)


class TestSchemaValidation:
    def test_schema_violation_is_caught(self) -> None:
        order, portfolio = _built_order()
        broken = replace(order, as_of="not an int")  # type: ignore[arg-type]
        result = validate_order(broken, CAPS, portfolio)
        assert result.valid is False


class TestDeterminism:
    def test_identical_inputs_produce_identical_result(self) -> None:
        order, portfolio = _built_order()
        first = validate_order(order, CAPS, portfolio)
        second = validate_order(order, CAPS, portfolio)
        assert first == second


class TestClosingDirectionMismatch:
    def test_close_intent_with_wrong_side_is_invalid(self) -> None:
        from ai_trader.execution_engine.types import OrderIntent, OrderSide
        order, portfolio = _built_order()
        broken = replace(order, intent=OrderIntent.CLOSE, side=OrderSide.BUY)  # LONG close should be SELL
        result = validate_order(broken, CAPS, portfolio)
        assert result.valid is False
        assert any("DIRECTION_MISMATCH" in r for r in result.reasons)


class TestPriceValidationDirect:
    """Constructs OrderRequest objects directly (rather than via the builder, which never produces
    STOP/STOP_LIMIT in v1) to exercise the Order Validator's price checks for every order type the
    frozen schema defines -- the Validator must defend ANY schema-valid order, not just what this
    module's own Builder happens to emit."""

    def test_stop_without_stop_price_is_invalid(self) -> None:
        order, portfolio = _built_order()
        broken = replace(order, order_type=OrderType.STOP, limit_price=None, bracket=None, stop_price=None)
        result = validate_order(broken, CAPS, portfolio)
        assert result.valid is False
        assert any("PRICE_VALIDATION" in r for r in result.reasons)

    def test_stop_limit_without_either_price_is_invalid(self) -> None:
        order, portfolio = _built_order()
        broken = replace(order, order_type=OrderType.STOP_LIMIT, limit_price=None, bracket=None, stop_price=None)
        result = validate_order(broken, CAPS, portfolio)
        assert result.valid is False
        assert any("PRICE_VALIDATION" in r for r in result.reasons)

    def test_stop_limit_with_nonpositive_stop_price_is_invalid(self) -> None:
        order, portfolio = _built_order()
        broken = replace(order, order_type=OrderType.STOP_LIMIT, bracket=None, stop_price=-1.0)
        result = validate_order(broken, CAPS, portfolio)
        assert result.valid is False

    def test_bracket_take_profit_not_finite_is_invalid(self) -> None:
        from ai_trader.execution_engine.types import BracketLegs
        order, portfolio = _built_order()
        assert order.bracket is not None
        broken = replace(order, bracket=BracketLegs(take_profit=float("inf"), stop_loss=order.bracket.stop_loss))
        result = validate_order(broken, CAPS, portfolio)
        assert result.valid is False
        assert any("PRICE_VALIDATION" in r for r in result.reasons)

    def test_bracket_parent_limit_price_not_finite_is_invalid(self) -> None:
        order, portfolio = _built_order()
        broken = replace(order, limit_price=float("nan"))
        result = validate_order(broken, CAPS, portfolio)
        assert result.valid is False


class TestNoTickIncrementConfigured:
    def test_zero_tick_size_treats_every_price_as_a_multiple(self) -> None:
        order, portfolio = _built_order()
        from ai_trader.execution_engine.types import BrokerCapabilities
        no_tick_caps = BrokerCapabilities(
            supported_order_types=CAPS.supported_order_types,
            supported_time_in_force=CAPS.supported_time_in_force,
            tick_size=0.0, lot_step=CAPS.lot_step, min_qty=CAPS.min_qty, max_qty=CAPS.max_qty,
            market_status=CAPS.market_status,
        )
        broken = replace(order, limit_price=100.0037123)  # would fail a real tick check
        result = validate_order(broken, no_tick_caps, portfolio)
        assert not any("TICK_SIZE" in r for r in result.reasons)

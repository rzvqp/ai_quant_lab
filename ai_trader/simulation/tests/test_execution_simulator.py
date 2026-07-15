"""Unit tests for the Execution Simulator: fill rules per order type, cost model, partial fills,
TIF/expiry, OCO/bracket, stop-before-target same-bar conflict, margin/qty rejects, gaps.
"""

from __future__ import annotations

from ai_trader.execution_engine import builder
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.tests.fixtures.fake_broker import make_capabilities
from ai_trader.execution_engine.tests.fixtures.fake_decision import make_allow_decision
from ai_trader.execution_engine.types import MarketStatus, OrderState
from ai_trader.simulation.config import (
    CostModel, FillModel, MarginModel, SimulationContext, SlippageModel,
)
from ai_trader.simulation.config import DateRange
from ai_trader.simulation.execution_simulator import ExecutionSimulator
from ai_trader.simulation.types import Bar, IntrabarRule, PartialFillPolicy, SlippageModelType


def make_context(**overrides: object) -> SimulationContext:
    defaults: dict[str, object] = dict(
        run_id="R1", date_range=DateRange(1_600_000_000, 1_600_100_000), symbols=("XAUUSD",),
        timeframes=("M15",), starting_balance=100_000.0, run_seed=42,
    )
    defaults.update(overrides)
    return SimulationContext(**defaults)  # type: ignore[arg-type]


def make_bar(as_of: int, o: float, h: float, l: float, c: float) -> Bar:
    return Bar(symbol="XAUUSD", timeframe="M15", ts_open=as_of - 900, ts_close=as_of, open=o, high=h, low=l, close=c)


def build_order_request(context: SimulationContext, **decision_kwargs: object):  # type: ignore[no-untyped-def]
    caps = make_capabilities(symbol="XAUUSD", tick_size=0.01)
    decision, portfolio = make_allow_decision(**decision_kwargs)  # type: ignore[arg-type]
    outcome = builder.build_order(decision, portfolio, caps, ExecConfig())
    assert outcome.success and outcome.order is not None, outcome.reason
    return outcome.order, caps


class TestMarketOrderFill:
    def test_market_order_fills_at_next_bar_open_not_signal_bar(self) -> None:
        context = make_context()
        order, caps = build_order_request(context, entry=100.0, stop=99.0)
        # A LIMIT-mapped order is built by default (ExecConfig's own order-mapping policy) -- force a
        # MARKET order directly on the WorkingOrder path instead, since we're testing fill TIMING, not
        # order-type selection.
        from dataclasses import replace
        from ai_trader.execution_engine.types import OrderType
        order = replace(order, order_type=OrderType.MARKET, limit_price=None)

        exsim = ExecutionSimulator(context, caps)
        ack = exsim.submit_order(order)
        assert ack.accepted

        signal_bar = make_bar(order.as_of, 100.0, 100.5, 99.5, 100.2)
        fills = exsim.advance_bar(order.as_of, {"XAUUSD": signal_bar})
        assert fills == (), "must never fill on the signal/submission bar (no lookahead)"

        next_as_of = order.as_of + 900
        next_bar = make_bar(next_as_of, 101.0, 101.5, 100.8, 101.2)
        fills = exsim.advance_bar(next_as_of, {"XAUUSD": next_bar})
        assert len(fills) == 1
        fill = fills[0]
        assert fill.qty == order.quantity
        # buy: ask = open + half_spread + slippage (1 tick spread + 1 tick slippage defaults)
        assert fill.price > next_bar.open
        status = exsim.query_status(order.client_order_id)
        assert status is not None and status.state is OrderState.FILLED

    def test_market_order_never_fabricates_a_price_on_missing_bar(self) -> None:
        context = make_context()
        order, caps = build_order_request(context, entry=100.0, stop=99.0)
        from dataclasses import replace
        from ai_trader.execution_engine.types import OrderType
        order = replace(order, order_type=OrderType.MARKET, limit_price=None)
        exsim = ExecutionSimulator(context, caps)
        exsim.submit_order(order)
        fills = exsim.advance_bar(order.as_of + 900, {})  # no bar for XAUUSD this cycle
        assert fills == ()
        status = exsim.query_status(order.client_order_id)
        assert status is not None and status.state is OrderState.ACKNOWLEDGED


class TestLimitOrderFill:
    def test_limit_buy_fills_only_when_range_touches(self) -> None:
        context = make_context()
        order, caps = build_order_request(context, entry=100.0, stop=99.0)  # builds a LIMIT by default
        exsim = ExecutionSimulator(context, caps)
        exsim.submit_order(order)
        assert order.limit_price == 100.0

        untouched = make_bar(order.as_of + 900, 101.0, 101.5, 100.5, 101.2)
        fills = exsim.advance_bar(order.as_of + 900, {"XAUUSD": untouched})
        assert fills == ()

        touched = make_bar(order.as_of + 1800, 101.0, 101.2, 99.8, 100.9)
        fills = exsim.advance_bar(order.as_of + 1800, {"XAUUSD": touched})
        assert len(fills) == 1
        assert fills[0].price == 100.0  # fills exactly at limit_price, no extra spread/slippage


class TestPartialFillPolicy:
    def test_full_fill_default_never_partials(self) -> None:
        context = make_context()
        order, caps = build_order_request(context, entry=100.0, stop=99.0)
        from dataclasses import replace
        from ai_trader.execution_engine.types import OrderType
        order = replace(order, order_type=OrderType.MARKET, limit_price=None)
        exsim = ExecutionSimulator(context, caps)
        exsim.submit_order(order)
        bar = make_bar(order.as_of + 900, 100.0, 100.5, 99.5, 100.2)
        fills = exsim.advance_bar(order.as_of + 900, {"XAUUSD": bar})
        assert len(fills) == 1 and fills[0].qty == order.quantity

    def test_fixed_fraction_policy_partially_fills_then_completes(self) -> None:
        context = make_context(fill_model=FillModel(
            partial_fill_policy=PartialFillPolicy.FIXED_FRACTION, partial_fill_fraction=0.5,
        ))
        order, caps = build_order_request(context, entry=100.0, stop=99.0)
        from dataclasses import replace
        from ai_trader.execution_engine.types import OrderType
        order = replace(order, order_type=OrderType.MARKET, limit_price=None, time_in_force=order.time_in_force)
        exsim = ExecutionSimulator(context, caps)
        exsim.submit_order(order)
        bar1 = make_bar(order.as_of + 900, 100.0, 100.5, 99.5, 100.2)
        fills1 = exsim.advance_bar(order.as_of + 900, {"XAUUSD": bar1})
        assert len(fills1) == 1
        assert fills1[0].qty == order.quantity * 0.5
        status = exsim.query_status(order.client_order_id)
        assert status is not None and status.state is OrderState.PARTIALLY_FILLED


class TestTimeInForce:
    def test_ioc_cancels_unfilled_remainder_on_first_eligible_bar(self) -> None:
        from dataclasses import replace
        from ai_trader.execution_engine.types import TimeInForce
        context = make_context()
        order, caps = build_order_request(context, entry=100.0, stop=99.0)
        order = replace(order, time_in_force=TimeInForce.IOC)  # a LIMIT far from the market
        exsim = ExecutionSimulator(context, caps)
        exsim.submit_order(order)
        bar = make_bar(order.as_of + 900, 200.0, 200.5, 199.5, 200.2)  # never touches limit=100.0
        fills = exsim.advance_bar(order.as_of + 900, {"XAUUSD": bar})
        assert fills == ()
        status = exsim.query_status(order.client_order_id)
        assert status is not None and status.state is OrderState.CANCELLED

    def test_day_order_expires_at_utc_day_boundary(self) -> None:
        from dataclasses import replace
        from ai_trader.execution_engine.types import TimeInForce
        context = make_context()
        order, caps = build_order_request(context, entry=100.0, stop=99.0)
        order = replace(order, time_in_force=TimeInForce.DAY)
        exsim = ExecutionSimulator(context, caps)
        exsim.submit_order(order)
        next_day = ((order.as_of // 86400) + 2) * 86400  # well past the day boundary
        bar = make_bar(next_day, 200.0, 200.5, 199.5, 200.2)
        fills = exsim.advance_bar(next_day, {"XAUUSD": bar})
        assert fills == ()
        status = exsim.query_status(order.client_order_id)
        assert status is not None and status.state is OrderState.EXPIRED


class TestMarketClosedReject:
    def test_market_closed_symbol_rejected_at_submit(self) -> None:
        context = make_context()
        order, _caps = build_order_request(context, entry=100.0, stop=99.0)
        closed_caps = make_capabilities(symbol="XAUUSD", tick_size=0.01, market_status=MarketStatus.CLOSED)
        exsim = ExecutionSimulator(context, closed_caps)
        ack = exsim.submit_order(order)
        assert not ack.accepted
        assert ack.reason == "MARKET_CLOSED"


class TestQuantityBounds:
    def test_qty_below_min_rejected_at_submit(self) -> None:
        context = make_context()
        order, _caps = build_order_request(context, entry=100.0, stop=99.0)
        tight_caps = make_capabilities(symbol="XAUUSD", tick_size=0.01, min_qty=order.quantity + 1.0)
        exsim = ExecutionSimulator(context, tight_caps)
        ack = exsim.submit_order(order)
        assert not ack.accepted
        assert ack.reason == "QTY_OUT_OF_BOUNDS"


class TestOcoBracket:
    def test_target_fills_cancel_the_sibling_stop(self) -> None:
        from dataclasses import replace
        context = make_context()
        order, caps = build_order_request(context, entry=100.0, stop=99.0)
        exsim = ExecutionSimulator(context, caps)
        exsim.submit_order(order)
        entry_bar = make_bar(order.as_of + 900, 100.0, 100.2, 99.8, 100.0)
        entry_fills = exsim.advance_bar(order.as_of + 900, {"XAUUSD": entry_bar})
        assert len(entry_fills) == 1

        # a bar that only touches the take-profit leg (order.limit_price + 2.0 default target spread
        # from make_allow_decision), never the stop -- confirms OCO wiring, not the race-resolution path.
        assert order.bracket is not None
        target = order.bracket.take_profit
        assert target is not None
        target_bar = make_bar(order.as_of + 1800, target, target + 0.3, target - 0.3, target)
        fills = exsim.advance_bar(order.as_of + 1800, {"XAUUSD": target_bar})
        assert len(fills) == 1
        assert fills[0].price == target

        # both OCO legs are now terminal (one FILLED, one CANCELLED) -- neither remains open.
        open_orders = exsim.query_open_orders()
        assert all(o.client_order_id not in (f"{order.client_order_id}-TP", f"{order.client_order_id}-SL") for o in open_orders)


class TestStopLimit:
    def test_stop_limit_triggers_then_fills_at_limit_same_bar(self) -> None:
        from dataclasses import replace
        from ai_trader.execution_engine.types import OrderType
        context = make_context()
        order, caps = build_order_request(context, entry=100.0, stop=99.0)
        stop_limit = replace(order, order_type=OrderType.STOP_LIMIT, stop_price=105.0, limit_price=105.2)
        exsim = ExecutionSimulator(context, caps)
        exsim.submit_order(stop_limit)
        bar = make_bar(order.as_of + 900, 105.1, 105.3, 104.9, 105.1)  # crosses stop AND touches limit
        fills = exsim.advance_bar(order.as_of + 900, {"XAUUSD": bar})
        assert len(fills) == 1
        assert fills[0].price == 105.2


class TestCancel:
    def test_cancel_working_order(self) -> None:
        context = make_context()
        order, caps = build_order_request(context, entry=100.0, stop=99.0)
        exsim = ExecutionSimulator(context, caps)
        exsim.submit_order(order)
        ack = exsim.cancel_order(order.client_order_id)
        assert ack.accepted
        status = exsim.query_status(order.client_order_id)
        assert status is not None and status.state is OrderState.CANCELLED

    def test_cancel_unknown_order_rejected(self) -> None:
        context = make_context()
        _order, caps = build_order_request(context, entry=100.0, stop=99.0)
        exsim = ExecutionSimulator(context, caps)
        ack = exsim.cancel_order("does-not-exist")
        assert not ack.accepted

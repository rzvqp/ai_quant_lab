"""Conformance test: Execution Simulator fills vs. the frozen research engine's documented
conventions (``IMPLEMENTATION_CHOICES.md`` §7). ``code/mstrat.py`` is read ONLY to quote its own
documented convention in this docstring -- it is never imported into ``ai_trader`` production code,
preserving the Research-Lab-is-frozen boundary. The check is exact (0-tick tolerance): both the
research engine and ``EXECUTION_SIMULATOR.md`` §4's default v1 cost model use the SAME fixed rule
(entry at next-bar open, 1 tick spread + 1 tick slippage per side, stop-before-target intrabar), so a
numeric mismatch here would indicate a genuine implementation bug, not a modeling difference to
tolerate.
"""

from __future__ import annotations

from dataclasses import replace

from ai_trader.execution_engine import builder
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.tests.fixtures.fake_broker import make_capabilities
from ai_trader.execution_engine.tests.fixtures.fake_decision import make_allow_decision
from ai_trader.execution_engine.types import OrderType
from ai_trader.simulation.config import CostModel, DateRange, FillModel, SimulationContext, SlippageModel
from ai_trader.simulation.execution_simulator import ExecutionSimulator
from ai_trader.simulation.types import Bar, SlippageModelType

TICK = 0.01


def make_context() -> SimulationContext:
    return SimulationContext(
        run_id="CONFORM", date_range=DateRange(1_600_000_000, 1_600_100_000), symbols=("XAUUSD",),
        timeframes=("M15",), starting_balance=100_000.0, run_seed=1,
        cost_model=CostModel(spread_ticks=1.0),
        fill_model=FillModel(slippage_model=SlippageModel(type=SlippageModelType.FIXED, fixed_ticks=1.0)),
    )


def test_market_buy_fill_equals_next_open_plus_one_tick_spread_plus_one_tick_slippage() -> None:
    """Research engine convention (``EXECUTION_SIMULATOR.md`` §4, mirrored from ``code/mstrat.py``'s
    own documented "entry at next-bar open, cost = spread + slippage, 1 tick each side" rule): a BUY
    market fill = next_open + 1 tick (spread) + 1 tick (slippage) = next_open + 2 ticks."""
    context = make_context()
    caps = make_capabilities(symbol="XAUUSD", tick_size=TICK)
    decision, portfolio = make_allow_decision(entry=100.0, stop=99.0, direction="LONG")
    outcome = builder.build_order(decision, portfolio, caps, ExecConfig())
    order = replace(outcome.order, order_type=OrderType.MARKET, limit_price=None)

    exsim = ExecutionSimulator(context, caps)
    exsim.submit_order(order)
    next_bar = Bar(symbol="XAUUSD", timeframe="M15", ts_open=order.as_of, ts_close=order.as_of + 900,
                    open=101.0, high=101.5, low=100.8, close=101.2)
    fills = exsim.advance_bar(order.as_of + 900, {"XAUUSD": next_bar})
    assert len(fills) == 1
    expected = 101.0 + TICK + TICK  # next_open + spread + slippage
    assert abs(fills[0].price - expected) < 1e-9


def test_stop_before_target_when_a_bar_spans_both() -> None:
    """Research engine convention: "stop-before-target, worst-case, engine-parity" when a single bar's
    range could hit both -- never random, never target-first."""
    context = make_context()
    caps = make_capabilities(symbol="XAUUSD", tick_size=TICK)
    decision, portfolio = make_allow_decision(entry=100.0, stop=99.0, target=102.0, direction="LONG")
    outcome = builder.build_order(decision, portfolio, caps, ExecConfig())
    order = outcome.order
    assert order.bracket is not None and order.bracket.stop_loss == 99.0 and order.bracket.take_profit == 102.0

    exsim = ExecutionSimulator(context, caps)
    exsim.submit_order(order)
    entry_bar = Bar(symbol="XAUUSD", timeframe="M15", ts_open=order.as_of, ts_close=order.as_of + 900,
                     open=100.0, high=100.2, low=99.8, close=100.0)
    exsim.advance_bar(order.as_of + 900, {"XAUUSD": entry_bar})  # parent fills, OCO children created

    spanning_bar = Bar(symbol="XAUUSD", timeframe="M15", ts_open=order.as_of + 900, ts_close=order.as_of + 1800,
                        open=100.0, high=103.0, low=98.0, close=100.5)  # crosses BOTH stop and target
    fills = exsim.advance_bar(order.as_of + 1800, {"XAUUSD": spanning_bar})
    assert len(fills) == 1
    # The stop leg must win the same-bar race (never the target) -- fills at its OWN trigger price
    # (99.0) +/- slippage only, per EXECUTION_SIMULATOR.md's Stop row (no spread on a stop trigger).
    # A SHORT-side (closing) fill subtracts slippage: 99.0 - 1 tick = 98.99.
    assert fills[0].price == 99.0 - TICK, "stop must win, priced at its own trigger +/- slippage only"

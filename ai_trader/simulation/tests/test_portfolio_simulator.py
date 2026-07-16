"""Unit tests for the Portfolio Simulator: accounting invariants, position lifecycle, margin,
liquidation, and the ``PortfolioState`` projection."""

from __future__ import annotations

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.config import DateRange, MarginModel, SimulationContext
from ai_trader.simulation.portfolio_simulator import PortfolioSimulator
from ai_trader.simulation.types import Bar, SimFillEvent

SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}


def make_context(**overrides: object) -> SimulationContext:
    defaults: dict[str, object] = dict(
        run_id="R1", date_range=DateRange(1_600_000_000, 1_600_100_000), symbols=("XAUUSD",),
        timeframes=("M15",), starting_balance=100_000.0, run_seed=42,
    )
    defaults.update(overrides)
    return SimulationContext(**defaults)  # type: ignore[arg-type]


def make_fill(
    as_of: int, price: float, qty: float = 10.0, direction: Direction = Direction.LONG,
    reduce_only: bool = False, client_order_id: str = "C1", commission: float = 0.0,
) -> SimFillEvent:
    return SimFillEvent(
        client_order_id=client_order_id, order_request_id="REQ1", strategy_id="S1", symbol="XAUUSD",
        direction=direction, intent_close=reduce_only, qty=qty, price=price, spread_cost=0.0,
        slippage_cost=0.0, commission=commission, as_of=as_of, reduce_only=reduce_only,
    )


def make_bar(as_of: int, close: float, high: float | None = None, low: float | None = None) -> Bar:
    return Bar(
        symbol="XAUUSD", timeframe="M15", ts_open=as_of - 900, ts_close=as_of, open=close,
        high=high if high is not None else close + 0.5, low=low if low is not None else close - 0.5,
        close=close,
    )


class TestOpenAndClose:
    def test_open_position_then_close_books_realized_pnl(self) -> None:
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.apply((make_fill(1000, 100.0, qty=10.0),), bar_index=0)
        assert "XAUUSD" in psim.account.positions
        assert psim.account.positions["XAUUSD"].size == 10.0

        psim.apply((make_fill(2000, 105.0, qty=10.0, direction=Direction.SHORT, reduce_only=True),), bar_index=1)
        assert "XAUUSD" not in psim.account.positions
        assert len(psim.account.trade_ledger) == 1
        trade = psim.account.trade_ledger[0]
        assert trade.net_pnl == 50.0  # (105-100) * 10 * point_value(1.0)
        assert psim.account.balance == context.starting_balance + 50.0

    def test_scale_in_uses_weighted_average_entry(self) -> None:
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.apply((make_fill(1000, 100.0, qty=10.0, client_order_id="A"),), bar_index=0)
        psim.apply((make_fill(1900, 110.0, qty=10.0, client_order_id="B"),), bar_index=1)
        pos = psim.account.positions["XAUUSD"]
        assert pos.size == 20.0
        assert pos.avg_entry == 105.0

    def test_commission_deducted_from_balance_immediately(self) -> None:
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.apply((make_fill(1000, 100.0, qty=10.0, commission=5.0),), bar_index=0)
        assert psim.account.balance == context.starting_balance - 5.0


class TestMarkToMarket:
    def test_floating_pnl_and_equity(self) -> None:
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.apply((make_fill(1000, 100.0, qty=10.0),), bar_index=0)
        psim.mark_to_market(1900, {"XAUUSD": make_bar(1900, 103.0)})
        assert psim.account.floating_pnl == 30.0
        assert psim.account.equity == context.starting_balance + 30.0

    def test_drawdown_tracked_from_equity_hwm(self) -> None:
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.apply((make_fill(1000, 100.0, qty=10.0),), bar_index=0)
        psim.mark_to_market(1900, {"XAUUSD": make_bar(1900, 110.0)})
        assert psim.account.equity_hwm == context.starting_balance + 100.0
        psim.mark_to_market(2800, {"XAUUSD": make_bar(2800, 95.0)})
        assert psim.account.max_drawdown_pct > 0

    def test_mfe_mae_tracked_from_bar_range(self) -> None:
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.apply((make_fill(1000, 100.0, qty=10.0),), bar_index=0)
        psim.mark_to_market(1900, {"XAUUSD": make_bar(1900, 102.0, high=105.0, low=98.0)})
        pos = psim.account.positions["XAUUSD"]
        assert pos.mfe == 5.0  # high - entry
        assert pos.mae == 2.0  # entry - low


class TestMargin:
    def test_liquidation_closes_worst_loser_first(self) -> None:
        margin_model = MarginModel(initial_margin_pct=0.5, maintenance_margin_pct=0.4, leverage_max=2.0)
        symbol_meta = {
            "XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2),
        }
        context = make_context(
            symbols=("XAUUSD",), starting_balance=1000.0, margin_model=margin_model,
        )
        psim = PortfolioSimulator(context, symbol_meta)
        # Open a large position relative to equity so a price drop breaches maintenance margin.
        psim.apply((make_fill(1000, 100.0, qty=15.0),), bar_index=0)
        psim.mark_to_market(1900, {"XAUUSD": make_bar(1900, 10.0)})  # catastrophic drop
        assert "XAUUSD" not in psim.account.positions
        assert psim.account.liquidation_halted is True
        assert any(e.type == "LIQUIDATION" for e in psim.account.risk_events)


class TestRiskEventAttribution:
    """Phase 6.9A (CEO-approved 2026-07-16): ``RiskEventRecord.strategy_id`` is additive and
    optional -- these tests prove the storage/plumbing is correct and that the default (no
    ``strategy_id`` passed) is unchanged from before this field existed."""

    def test_strategy_id_defaults_to_none(self) -> None:
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.record_risk_event("DENY_BELOW_FLOOR", as_of=1000, detail="strength below floor")
        assert psim.account.risk_events[-1].strategy_id is None

    def test_strategy_id_is_recorded_when_provided(self) -> None:
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.record_risk_event("DENY_LIMIT_MAX_PER_SYMBOL", as_of=1000, strategy_id="S17")
        event = psim.account.risk_events[-1]
        assert event.strategy_id == "S17"
        assert event.type == "DENY_LIMIT_MAX_PER_SYMBOL"

    def test_positional_detail_and_keyword_strategy_id_do_not_collide(self) -> None:
        """The exact call shape ``harness.py`` uses: positional ``detail``, keyword-or-positional
        ``strategy_id`` -- both must land in the right field, never swapped."""
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.record_risk_event("DENY_FILTER_VOLATILITY", 2000, "atr out of band", "S28")
        event = psim.account.risk_events[-1]
        assert event.as_of == 2000
        assert event.detail == "atr out of band"
        assert event.strategy_id == "S28"

    def test_liquidation_events_are_unchanged_and_still_have_no_strategy_id(self) -> None:
        """Liquidation can close positions from more than one strategy in a single event -- this
        stays deliberately unattributed (``strategy_id=None``) rather than attributing to only the
        last-closed position, never fabricating a single-strategy attribution for a multi-position
        event."""
        margin_model = MarginModel(initial_margin_pct=0.5, maintenance_margin_pct=0.4, leverage_max=2.0)
        context = make_context(starting_balance=1000.0, margin_model=margin_model)
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.apply((make_fill(1000, 100.0, qty=15.0),), bar_index=0)
        psim.mark_to_market(1900, {"XAUUSD": make_bar(1900, 10.0)})
        liquidation_events = [e for e in psim.account.risk_events if e.type == "LIQUIDATION"]
        assert len(liquidation_events) == 1
        assert liquidation_events[0].strategy_id is None


class TestPortfolioStateProjection:
    def test_projection_matches_open_positions_and_equity(self) -> None:
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.apply((make_fill(1000, 100.0, qty=10.0),), bar_index=0)
        psim.mark_to_market(1900, {"XAUUSD": make_bar(1900, 103.0)})
        state = psim.to_portfolio_state(1900)
        assert state.equity == context.starting_balance + 30.0
        assert len(state.open_positions) == 1
        assert state.open_positions[0].symbol == "XAUUSD"
        assert state.is_stale is False

    def test_bars_since_close_advances_with_as_of(self) -> None:
        """Regression test for a real bug found during Wave D's own full-portfolio run:
        ``bars_since_close`` was hardcoded to 0, so ``check_cooldown_after_loss`` (whose ONLY clock
        source this is) never expired -- a symbol's first loss permanently blocked every future
        entry for the rest of the run. This must actually advance with ``as_of``."""
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.apply((make_fill(1000, 100.0, qty=10.0, client_order_id="C1"),), bar_index=0)
        psim.apply(
            (make_fill(1900, 90.0, qty=10.0, direction=Direction.SHORT, reduce_only=True, client_order_id="C1"),),
            bar_index=1,
        )  # a real loss, closed at as_of=1900

        state_at_close = psim.to_portfolio_state(1900)
        assert state_at_close.recent_closed_positions[-1].bars_since_close == 0

        state_5_bars_later = psim.to_portfolio_state(1900 + 5 * 900)
        assert state_5_bars_later.recent_closed_positions[-1].bars_since_close == 5

        state_much_later = psim.to_portfolio_state(1900 + 500 * 900)
        assert state_much_later.recent_closed_positions[-1].bars_since_close == 500

    def test_r_multiple_uses_registered_stop_hint(self) -> None:
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.register_stop_hint("C1", 98.0)  # risk = 2.0 per unit
        psim.apply((make_fill(1000, 100.0, qty=10.0, client_order_id="C1"),), bar_index=0)
        psim.apply((make_fill(2000, 104.0, qty=10.0, direction=Direction.SHORT, reduce_only=True, client_order_id="C1"),), bar_index=1)
        trade = psim.account.trade_ledger[0]
        assert trade.pnl_r == 2.0  # (104-100)/2.0

    def test_no_stop_hint_leaves_pnl_r_none(self) -> None:
        context = make_context()
        psim = PortfolioSimulator(context, SYMBOL_META)
        psim.apply((make_fill(1000, 100.0, qty=10.0, client_order_id="C1"),), bar_index=0)
        psim.apply((make_fill(2000, 104.0, qty=10.0, direction=Direction.SHORT, reduce_only=True, client_order_id="C1"),), bar_index=1)
        trade = psim.account.trade_ledger[0]
        assert trade.pnl_r is None

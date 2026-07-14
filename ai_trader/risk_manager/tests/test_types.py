"""Tests for :mod:`ai_trader.risk_manager.types`."""

from __future__ import annotations

from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.risk_manager.types import PortfolioState, RiskContext, SymbolRiskSnapshot


class TestRiskContext:
    def test_for_symbol_returns_configured_snapshot(self) -> None:
        snap = SymbolRiskSnapshot(atr=1.0)
        ctx = RiskContext(as_of=1, per_symbol={"XAUUSD": snap})
        assert ctx.for_symbol("XAUUSD") is snap

    def test_for_symbol_missing_is_insufficient_not_a_crash(self) -> None:
        ctx = RiskContext(as_of=1, per_symbol={})
        snap = ctx.for_symbol("XAUUSD")
        assert snap.data_quality is DataQualityLevel.INSUFFICIENT


class TestPortfolioState:
    def test_daily_pnl_combines_realized_and_unrealized(self) -> None:
        p = PortfolioState(as_of=1, equity=100.0, equity_high_water_mark=100.0, realized_pnl_pct_daily=-0.01, unrealized_pnl_pct_daily=-0.02)
        assert p.daily_pnl_pct == -0.03

    def test_weekly_pnl_combines_realized_and_unrealized(self) -> None:
        p = PortfolioState(as_of=1, equity=100.0, equity_high_water_mark=100.0, realized_pnl_pct_weekly=0.01, unrealized_pnl_pct_weekly=0.02)
        assert p.weekly_pnl_pct == 0.03

    def test_drawdown_pct_zero_when_at_high_water_mark(self) -> None:
        p = PortfolioState(as_of=1, equity=100.0, equity_high_water_mark=100.0)
        assert p.drawdown_pct == 0.0

    def test_drawdown_pct_positive_below_high_water_mark(self) -> None:
        p = PortfolioState(as_of=1, equity=88.0, equity_high_water_mark=100.0)
        assert p.drawdown_pct == 0.12

    def test_drawdown_pct_never_negative_above_hwm(self) -> None:
        p = PortfolioState(as_of=1, equity=110.0, equity_high_water_mark=100.0)
        assert p.drawdown_pct == 0.0

    def test_drawdown_pct_zero_hwm_does_not_crash(self) -> None:
        p = PortfolioState(as_of=1, equity=0.0, equity_high_water_mark=0.0)
        assert p.drawdown_pct == 0.0

    def test_leverage_zero_equity_does_not_crash(self) -> None:
        p = PortfolioState(as_of=1, equity=0.0, equity_high_water_mark=0.0, gross_notional=100.0)
        assert p.leverage == 0.0

    def test_leverage_computed_from_gross_notional(self) -> None:
        p = PortfolioState(as_of=1, equity=100.0, equity_high_water_mark=100.0, gross_notional=250.0)
        assert p.leverage == 2.5

    def test_portfolio_risk_pct_sums_open_position_risk(self) -> None:
        from ai_trader.risk_manager.types import OpenPosition
        from ai_trader.signal_engine.types import Direction

        positions = (
            OpenPosition(symbol="A", strategy_id="S1", direction=Direction.LONG, size_units=1, entry_price=1, opened_bars_ago=1, risk_pct=0.01),
            OpenPosition(symbol="B", strategy_id="S2", direction=Direction.SHORT, size_units=1, entry_price=1, opened_bars_ago=1, risk_pct=0.02),
        )
        p = PortfolioState(as_of=1, equity=100.0, equity_high_water_mark=100.0, open_positions=positions)
        assert p.portfolio_risk_pct == 0.03

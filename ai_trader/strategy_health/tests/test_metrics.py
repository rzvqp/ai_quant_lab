"""Unit tests for rolling-window metric computation."""

from __future__ import annotations

from ai_trader.strategy_health.metrics import compute_window_metrics, trades_in_window
from ai_trader.strategy_health.types import ClosedTrade

_DAY = 86400
AS_OF = 1_700_000_000  # arbitrary fixed reference instant


def trade(days_ago: int, net_pnl: float, pnl_r: float | None = None, holding_bars: int = 10) -> ClosedTrade:
    return ClosedTrade(
        strategy_id="S1", exit_as_of=AS_OF - days_ago * _DAY, net_pnl=net_pnl, pnl_r=pnl_r,
        holding_bars=holding_bars,
    )


class TestTradesInWindow:
    def test_excludes_trades_older_than_the_window(self) -> None:
        trades = [trade(10, 1.0), trade(100, 1.0)]
        result = trades_in_window(trades, "3m", AS_OF)  # 3m = 90 days
        assert len(result) == 1

    def test_includes_trade_exactly_at_the_window_boundary(self) -> None:
        trades = [trade(90, 1.0)]
        result = trades_in_window(trades, "3m", AS_OF)
        assert len(result) == 1

    def test_excludes_trades_after_as_of(self) -> None:
        trades = [ClosedTrade(strategy_id="S1", exit_as_of=AS_OF + _DAY, net_pnl=1.0, pnl_r=None, holding_bars=1)]
        assert trades_in_window(trades, "12m", AS_OF) == []


class TestComputeWindowMetrics:
    def test_zero_trades_returns_all_none(self) -> None:
        m = compute_window_metrics([], "3m", AS_OF)
        assert m.n_trades == 0
        assert m.win_rate is None
        assert m.profit_factor is None
        assert m.expectancy_r is None
        assert m.net_r is None
        assert m.net_pnl == 0.0
        assert m.max_drawdown == 0.0
        assert m.monthly_consistency is None
        assert m.max_losing_streak == 0

    def test_win_rate_and_profit_factor(self) -> None:
        trades = [trade(1, 10.0), trade(2, -5.0), trade(3, 20.0), trade(4, -5.0)]
        m = compute_window_metrics(trades, "3m", AS_OF)
        assert m.n_trades == 4
        assert m.win_rate == 0.5
        assert m.profit_factor == 3.0  # (10+20) / (5+5)
        assert m.net_pnl == 20.0
        assert m.expectancy_currency == 5.0

    def test_profit_factor_none_when_no_losses(self) -> None:
        trades = [trade(1, 10.0), trade(2, 5.0)]
        m = compute_window_metrics(trades, "3m", AS_OF)
        assert m.profit_factor is None

    def test_expectancy_r_and_net_r_none_when_no_pnl_r_registered(self) -> None:
        trades = [trade(1, 10.0, pnl_r=None), trade(2, -5.0, pnl_r=None)]
        m = compute_window_metrics(trades, "3m", AS_OF)
        assert m.expectancy_r is None
        assert m.net_r is None

    def test_expectancy_r_and_net_r_computed_from_available_pnl_r(self) -> None:
        trades = [trade(1, 10.0, pnl_r=2.0), trade(2, -5.0, pnl_r=-1.0)]
        m = compute_window_metrics(trades, "3m", AS_OF)
        assert m.expectancy_r == 0.5
        assert m.net_r == 1.0

    def test_max_losing_streak(self) -> None:
        # oldest-first exit order: win, loss, loss, loss, win -- longest streak is 3
        trades = [trade(5, 1.0), trade(4, -1.0), trade(3, -1.0), trade(2, -1.0), trade(1, 1.0)]
        m = compute_window_metrics(trades, "3m", AS_OF)
        assert m.max_losing_streak == 3

    def test_isolated_max_drawdown(self) -> None:
        # cumulative: +10, +5 (peak 10, dd 5), +25 (new peak)
        trades = [trade(3, 10.0), trade(2, -5.0), trade(1, 20.0)]
        m = compute_window_metrics(trades, "3m", AS_OF)
        assert m.max_drawdown == 5.0

    def test_monthly_consistency_and_equity_stability_need_at_least_one_two_months(self) -> None:
        trades = [trade(1, 10.0)]
        m = compute_window_metrics(trades, "3m", AS_OF)
        assert m.monthly_consistency == 1.0  # the one active month was net-positive
        assert m.equity_stability is None  # needs >= 2 distinct months

    def test_avg_holding_bars(self) -> None:
        trades = [trade(1, 1.0, holding_bars=10), trade(2, 1.0, holding_bars=20)]
        m = compute_window_metrics(trades, "3m", AS_OF)
        assert m.avg_holding_bars == 15.0

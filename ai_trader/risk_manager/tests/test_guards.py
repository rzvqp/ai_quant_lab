"""Tests for :mod:`ai_trader.risk_manager.guards`."""

from __future__ import annotations

from ai_trader.risk_manager import guards
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.guards import GuardResult
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import make_portfolio
from ai_trader.risk_manager.types import ClosedPosition, EngineState

CONFIG = RiskConfig()


def _code(result: GuardResult) -> str:
    assert result.reason is not None
    return result.reason.code


class TestDailyLoss:
    def test_under_limit_passes(self) -> None:
        portfolio = make_portfolio(realized_pnl_pct_daily=-0.01)
        assert guards.check_daily_loss(portfolio, CONFIG).passed is True

    def test_at_limit_fails_and_escalates(self) -> None:
        portfolio = make_portfolio(realized_pnl_pct_daily=-0.03)
        result = guards.check_daily_loss(portfolio, CONFIG)
        assert result.passed is False
        assert _code(result) == "LOSS_DAILY"
        assert result.escalate_to is EngineState.SUSPENDED

    def test_combines_realized_and_unrealized(self) -> None:
        portfolio = make_portfolio(realized_pnl_pct_daily=-0.02, unrealized_pnl_pct_daily=-0.02)
        result = guards.check_daily_loss(portfolio, CONFIG)
        assert result.passed is False


class TestWeeklyLoss:
    def test_under_limit_passes(self) -> None:
        portfolio = make_portfolio(realized_pnl_pct_weekly=-0.01)
        assert guards.check_weekly_loss(portfolio, CONFIG).passed is True

    def test_at_limit_fails_and_escalates(self) -> None:
        portfolio = make_portfolio(realized_pnl_pct_weekly=-0.06)
        result = guards.check_weekly_loss(portfolio, CONFIG)
        assert result.passed is False
        assert _code(result) == "LOSS_WEEKLY"
        assert result.escalate_to is EngineState.SUSPENDED


class TestMaxDrawdown:
    def test_under_limit_passes(self) -> None:
        portfolio = make_portfolio(equity=95.0, equity_high_water_mark=100.0)  # 5% dd
        assert guards.check_max_drawdown(portfolio, CONFIG).passed is True

    def test_at_limit_fails_and_escalates(self) -> None:
        portfolio = make_portfolio(equity=88.0, equity_high_water_mark=100.0)  # 12% dd
        result = guards.check_max_drawdown(portfolio, CONFIG)
        assert result.passed is False
        assert _code(result) == "DRAWDOWN_MAX"
        assert result.escalate_to is EngineState.SUSPENDED


class TestCooldownAfterLoss:
    def test_no_recent_exits_passes(self) -> None:
        portfolio = make_portfolio()
        assert guards.check_cooldown_after_loss("XAUUSD", portfolio, CONFIG).passed is True

    def test_recent_loss_within_window_fails(self) -> None:
        closed = (ClosedPosition(symbol="XAUUSD", strategy_id="S1", was_loss=True, bars_since_close=1),)
        portfolio = make_portfolio(recent_closed_positions=closed)
        result = guards.check_cooldown_after_loss("XAUUSD", portfolio, CONFIG)
        assert result.passed is False
        assert _code(result) == "COOLDOWN_AFTER_LOSS"

    def test_loss_beyond_window_passes(self) -> None:
        closed = (ClosedPosition(symbol="XAUUSD", strategy_id="S1", was_loss=True, bars_since_close=10),)
        portfolio = make_portfolio(recent_closed_positions=closed)
        assert guards.check_cooldown_after_loss("XAUUSD", portfolio, CONFIG).passed is True

    def test_win_does_not_trigger_cooldown(self) -> None:
        closed = (ClosedPosition(symbol="XAUUSD", strategy_id="S1", was_loss=False, bars_since_close=1),)
        portfolio = make_portfolio(recent_closed_positions=closed)
        assert guards.check_cooldown_after_loss("XAUUSD", portfolio, CONFIG).passed is True

    def test_loss_on_other_symbol_does_not_trigger(self) -> None:
        closed = (ClosedPosition(symbol="EURUSD", strategy_id="S1", was_loss=True, bars_since_close=1),)
        portfolio = make_portfolio(recent_closed_positions=closed)
        assert guards.check_cooldown_after_loss("XAUUSD", portfolio, CONFIG).passed is True


class TestCooldownConsecutive:
    def test_under_threshold_passes(self) -> None:
        portfolio = make_portfolio(consecutive_losses=2)
        assert guards.check_cooldown_consecutive(portfolio, CONFIG).passed is True

    def test_at_threshold_within_window_fails(self) -> None:
        portfolio = make_portfolio(consecutive_losses=3, minutes_since_last_loss=10.0)
        result = guards.check_cooldown_consecutive(portfolio, CONFIG)
        assert result.passed is False
        assert _code(result) == "COOLDOWN_CONSECUTIVE"

    def test_at_threshold_beyond_window_passes(self) -> None:
        portfolio = make_portfolio(consecutive_losses=3, minutes_since_last_loss=90.0)
        assert guards.check_cooldown_consecutive(portfolio, CONFIG).passed is True

    def test_at_threshold_missing_minutes_fails_defensively(self) -> None:
        portfolio = make_portfolio(consecutive_losses=3, minutes_since_last_loss=None)
        result = guards.check_cooldown_consecutive(portfolio, CONFIG)
        assert result.passed is False


class TestCooldownStrategy:
    def test_unconfigured_strategy_passes(self) -> None:
        portfolio = make_portfolio()
        assert guards.check_cooldown_strategy("S1", portfolio, CONFIG).passed is True

    def test_configured_strategy_within_window_fails(self) -> None:
        config = RiskConfig()
        config.cooldowns.per_strategy_cooldown_bars["S1"] = 5
        closed = (ClosedPosition(symbol="XAUUSD", strategy_id="S1", was_loss=False, bars_since_close=2),)
        portfolio = make_portfolio(recent_closed_positions=closed)
        result = guards.check_cooldown_strategy("S1", portfolio, config)
        assert result.passed is False
        assert _code(result) == "COOLDOWN_STRATEGY"

    def test_configured_strategy_beyond_window_passes(self) -> None:
        config = RiskConfig()
        config.cooldowns.per_strategy_cooldown_bars["S1"] = 5
        closed = (ClosedPosition(symbol="XAUUSD", strategy_id="S1", was_loss=False, bars_since_close=10),)
        portfolio = make_portfolio(recent_closed_positions=closed)
        assert guards.check_cooldown_strategy("S1", portfolio, config).passed is True

    def test_different_strategy_not_affected(self) -> None:
        config = RiskConfig()
        config.cooldowns.per_strategy_cooldown_bars["S1"] = 5
        closed = (ClosedPosition(symbol="XAUUSD", strategy_id="S1", was_loss=False, bars_since_close=1),)
        portfolio = make_portfolio(recent_closed_positions=closed)
        assert guards.check_cooldown_strategy("S2", portfolio, config).passed is True


class TestRunners:
    def test_run_loss_drawdown_guards_fixed_order(self) -> None:
        portfolio = make_portfolio()
        results = guards.run_loss_drawdown_guards(portfolio, CONFIG)
        assert [name for name, _ in results] == ["LOSS_DAILY", "LOSS_WEEKLY", "DRAWDOWN_MAX"]

    def test_run_cooldowns_fixed_order(self) -> None:
        portfolio = make_portfolio()
        results = guards.run_cooldowns("XAUUSD", "S1", portfolio, CONFIG)
        assert [name for name, _ in results] == ["COOLDOWN_AFTER_LOSS", "COOLDOWN_CONSECUTIVE", "COOLDOWN_STRATEGY"]

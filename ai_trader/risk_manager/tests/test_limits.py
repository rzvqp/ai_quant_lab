"""Tests for :mod:`ai_trader.risk_manager.limits`."""

from __future__ import annotations

from ai_trader.risk_manager import limits
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.limits import LimitResult
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import make_portfolio
from ai_trader.risk_manager.types import OpenPosition, SymbolRiskSnapshot
from ai_trader.signal_engine.types import Direction

CONFIG = RiskConfig()


def _code(result: LimitResult) -> str:
    assert result.reason is not None
    return result.reason.code


def _position(symbol: str = "XAUUSD", group: str | None = None) -> OpenPosition:
    return OpenPosition(
        symbol=symbol, strategy_id="S1", direction=Direction.LONG, size_units=1.0,
        entry_price=100.0, opened_bars_ago=1, risk_pct=0.01, correlation_group=group,
    )


class TestMaxPositions:
    def test_under_limit_passes(self) -> None:
        portfolio = make_portfolio(open_positions=tuple(_position(f"S{i}") for i in range(4)))
        assert limits.check_max_positions(portfolio, CONFIG).passed is True

    def test_at_limit_fails(self) -> None:
        portfolio = make_portfolio(open_positions=tuple(_position(f"S{i}") for i in range(5)))
        result = limits.check_max_positions(portfolio, CONFIG)
        assert result.passed is False
        assert _code(result) == "LIMIT_MAX_POSITIONS"


class TestMaxPerSymbol:
    def test_no_existing_position_passes(self) -> None:
        portfolio = make_portfolio()
        assert limits.check_max_per_symbol("XAUUSD", portfolio, CONFIG).passed is True

    def test_existing_position_on_symbol_fails(self) -> None:
        portfolio = make_portfolio(open_positions=(_position("XAUUSD"),))
        result = limits.check_max_per_symbol("XAUUSD", portfolio, CONFIG)
        assert result.passed is False
        assert _code(result) == "LIMIT_MAX_PER_SYMBOL"

    def test_position_on_other_symbol_passes(self) -> None:
        portfolio = make_portfolio(open_positions=(_position("EURUSD"),))
        assert limits.check_max_per_symbol("XAUUSD", portfolio, CONFIG).passed is True


class TestMaxCorrelated:
    def test_under_group_limit_passes(self) -> None:
        portfolio = make_portfolio(open_positions=(_position("EURUSD", group="METALS"),))
        config = RiskConfig()
        config.correlation_groups["XAUUSD"] = "METALS"
        result = limits.check_max_correlated("XAUUSD", portfolio, config)
        assert result.passed is True

    def test_at_group_limit_fails(self) -> None:
        portfolio = make_portfolio(open_positions=(
            _position("EURUSD", group="METALS"), _position("GBPUSD", group="METALS"),
        ))
        config = RiskConfig()
        config.correlation_groups["XAUUSD"] = "METALS"
        config.correlation_groups["EURUSD"] = "METALS"
        config.correlation_groups["GBPUSD"] = "METALS"
        result = limits.check_max_correlated("XAUUSD", portfolio, config)
        assert result.passed is False
        assert _code(result) == "LIMIT_MAX_CORRELATED"

    def test_unconfigured_symbols_are_singleton_groups(self) -> None:
        """No configured correlation_groups mapping -> every symbol is its own group -> the limit
        never fires against a DIFFERENT symbol (the safe, conservative default)."""
        portfolio = make_portfolio(open_positions=(_position("EURUSD"), _position("GBPUSD")))
        result = limits.check_max_correlated("XAUUSD", portfolio, RiskConfig())
        assert result.passed is True


class TestMaxExposure:
    def test_under_cap_passes(self) -> None:
        portfolio = make_portfolio(open_positions=(OpenPosition(
            symbol="A", strategy_id="S1", direction=Direction.LONG, size_units=1, entry_price=1,
            opened_bars_ago=1, risk_pct=0.1,
        ),))
        assert limits.check_max_exposure(portfolio, CONFIG).passed is True

    def test_at_cap_fails(self) -> None:
        portfolio = make_portfolio(open_positions=(OpenPosition(
            symbol="A", strategy_id="S1", direction=Direction.LONG, size_units=1, entry_price=1,
            opened_bars_ago=1, risk_pct=0.30,
        ),))
        result = limits.check_max_exposure(portfolio, CONFIG)
        assert result.passed is False
        assert _code(result) == "LIMIT_MAX_EXPOSURE"


class TestMaxLeverage:
    def test_under_cap_passes(self) -> None:
        portfolio = make_portfolio(equity=100.0, gross_notional=100.0)  # leverage 1.0 < 3.0
        assert limits.check_max_leverage(portfolio, CONFIG).passed is True

    def test_at_cap_fails(self) -> None:
        portfolio = make_portfolio(equity=100.0, gross_notional=300.0)  # leverage 3.0 >= 3.0
        result = limits.check_max_leverage(portfolio, CONFIG)
        assert result.passed is False
        assert _code(result) == "LIMIT_MAX_LEVERAGE"


class TestMaxOvernight:
    def test_not_near_close_always_passes(self) -> None:
        portfolio = make_portfolio(open_positions=(OpenPosition(
            symbol="A", strategy_id="S1", direction=Direction.LONG, size_units=1, entry_price=1,
            opened_bars_ago=1, risk_pct=0.9,
        ),))
        snap = SymbolRiskSnapshot(is_near_session_close=False)
        assert limits.check_max_overnight("XAUUSD", snap, portfolio, CONFIG).passed is True

    def test_near_close_under_cap_passes(self) -> None:
        portfolio = make_portfolio(open_positions=(OpenPosition(
            symbol="A", strategy_id="S1", direction=Direction.LONG, size_units=1, entry_price=1,
            opened_bars_ago=1, risk_pct=0.05,
        ),))
        snap = SymbolRiskSnapshot(is_near_session_close=True)
        assert limits.check_max_overnight("XAUUSD", snap, portfolio, CONFIG).passed is True

    def test_near_close_over_cap_fails(self) -> None:
        portfolio = make_portfolio(open_positions=(OpenPosition(
            symbol="A", strategy_id="S1", direction=Direction.LONG, size_units=1, entry_price=1,
            opened_bars_ago=1, risk_pct=0.20,
        ),))
        snap = SymbolRiskSnapshot(is_near_session_close=True)
        result = limits.check_max_overnight("XAUUSD", snap, portfolio, CONFIG)
        assert result.passed is False
        assert _code(result) == "LIMIT_MAX_OVERNIGHT"


class TestRunPortfolioLimits:
    def test_returns_all_limits_in_fixed_order(self) -> None:
        portfolio = make_portfolio()
        snap = SymbolRiskSnapshot()
        results = limits.run_portfolio_limits("XAUUSD", snap, portfolio, CONFIG)
        names = [name for name, _ in results]
        assert names == [
            "LIMIT_MAX_POSITIONS", "LIMIT_MAX_PER_SYMBOL", "LIMIT_MAX_CORRELATED",
            "LIMIT_MAX_EXPOSURE", "LIMIT_MAX_LEVERAGE", "LIMIT_MAX_OVERNIGHT",
        ]
        assert all(r.passed for _, r in results)

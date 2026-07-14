"""Tests for :mod:`ai_trader.risk_manager.filters`."""

from __future__ import annotations

from typing import Any

from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.risk_manager import filters
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.filters import FilterResult
from ai_trader.risk_manager.types import RiskContext, SymbolRiskSnapshot

CONFIG = RiskConfig()


def _ctx(**kwargs: Any) -> RiskContext:
    defaults: dict[str, Any] = {"atr": 1.0, "atr_rolling_median": 1.0, "current_spread": 0.2, "liquidity_proxy": 1000.0}
    defaults.update(kwargs)
    return RiskContext(as_of=1, per_symbol={"XAUUSD": SymbolRiskSnapshot(**defaults)})


def _code(result: FilterResult) -> str:
    assert result.reason is not None
    return result.reason.code


class TestDataQuality:
    def test_ok_passes(self) -> None:
        assert filters.check_data_quality("XAUUSD", _ctx(), CONFIG).passed is True

    def test_stale_fails(self) -> None:
        result = filters.check_data_quality("XAUUSD", _ctx(data_quality=DataQualityLevel.STALE), CONFIG)
        assert result.passed is False
        assert _code(result) == "DATA_DEGRADED"

    def test_insufficient_fails(self) -> None:
        result = filters.check_data_quality("XAUUSD", _ctx(data_quality=DataQualityLevel.INSUFFICIENT), CONFIG)
        assert result.passed is False

    def test_global_context_data_quality_also_checked(self) -> None:
        ctx = RiskContext(as_of=1, per_symbol={"XAUUSD": SymbolRiskSnapshot()}, data_quality=DataQualityLevel.STALE)
        assert filters.check_data_quality("XAUUSD", ctx, CONFIG).passed is False


class TestVolatility:
    def test_within_band_passes(self) -> None:
        ctx = _ctx(atr=1.0, atr_rolling_median=1.0)
        result = filters.check_volatility("XAUUSD", ctx.for_symbol("XAUUSD"), CONFIG)
        assert result.passed is True

    def test_too_dead_fails(self) -> None:
        ctx = _ctx(atr=0.1, atr_rolling_median=1.0)  # ratio 0.1 < 0.25
        result = filters.check_volatility("XAUUSD", ctx.for_symbol("XAUUSD"), CONFIG)
        assert result.passed is False
        assert _code(result) == "FILTER_VOLATILITY"

    def test_too_wild_fails(self) -> None:
        ctx = _ctx(atr=5.0, atr_rolling_median=1.0)  # ratio 5.0 > 4.0
        result = filters.check_volatility("XAUUSD", ctx.for_symbol("XAUUSD"), CONFIG)
        assert result.passed is False

    def test_missing_atr_fails(self) -> None:
        ctx = _ctx(atr=None)
        result = filters.check_volatility("XAUUSD", ctx.for_symbol("XAUUSD"), CONFIG)
        assert result.passed is False

    def test_zero_median_fails_not_a_crash(self) -> None:
        ctx = _ctx(atr=1.0, atr_rolling_median=0.0)
        result = filters.check_volatility("XAUUSD", ctx.for_symbol("XAUUSD"), CONFIG)
        assert result.passed is False


class TestSpread:
    def test_within_limit_passes(self) -> None:
        config = RiskConfig()
        config.filters.reference_spread["XAUUSD"] = 0.1
        ctx = _ctx(current_spread=0.2)
        result = filters.check_spread("XAUUSD", ctx.for_symbol("XAUUSD"), config)
        assert result.passed is True

    def test_over_limit_fails(self) -> None:
        config = RiskConfig()
        config.filters.reference_spread["XAUUSD"] = 0.1
        ctx = _ctx(current_spread=0.5)  # > 3*0.1
        result = filters.check_spread("XAUUSD", ctx.for_symbol("XAUUSD"), config)
        assert result.passed is False
        assert _code(result) == "FILTER_SPREAD"

    def test_no_reference_configured_fails(self) -> None:
        result = filters.check_spread("XAUUSD", _ctx().for_symbol("XAUUSD"), RiskConfig())
        assert result.passed is False


class TestLiquidity:
    def test_above_floor_passes(self) -> None:
        config = RiskConfig()
        config.filters.liquidity_floor["XAUUSD"] = 100.0
        result = filters.check_liquidity("XAUUSD", _ctx(liquidity_proxy=1000.0).for_symbol("XAUUSD"), config)
        assert result.passed is True

    def test_below_floor_fails(self) -> None:
        config = RiskConfig()
        config.filters.liquidity_floor["XAUUSD"] = 100.0
        result = filters.check_liquidity("XAUUSD", _ctx(liquidity_proxy=10.0).for_symbol("XAUUSD"), config)
        assert result.passed is False
        assert _code(result) == "FILTER_LIQUIDITY"

    def test_no_floor_configured_fails(self) -> None:
        result = filters.check_liquidity("XAUUSD", _ctx().for_symbol("XAUUSD"), RiskConfig())
        assert result.passed is False


class TestNews:
    def test_no_event_passes(self) -> None:
        result = filters.check_news("XAUUSD", _ctx().for_symbol("XAUUSD"), CONFIG)
        assert result.passed is True

    def test_within_blackout_fails(self) -> None:
        ctx = _ctx(minutes_to_high_impact_event=5.0)
        result = filters.check_news("XAUUSD", ctx.for_symbol("XAUUSD"), CONFIG)
        assert result.passed is False
        assert _code(result) == "FILTER_NEWS"

    def test_outside_blackout_passes(self) -> None:
        ctx = _ctx(minutes_to_high_impact_event=30.0)
        result = filters.check_news("XAUUSD", ctx.for_symbol("XAUUSD"), CONFIG)
        assert result.passed is True


class TestWeekendAndGap:
    def test_past_friday_cutoff_fails(self) -> None:
        ctx = _ctx(is_past_friday_cutoff=True)
        result = filters.check_weekend("XAUUSD", ctx.for_symbol("XAUUSD"), CONFIG)
        assert result.passed is False
        assert _code(result) == "RULE_WEEKEND"

    def test_not_past_cutoff_passes(self) -> None:
        result = filters.check_weekend("XAUUSD", _ctx().for_symbol("XAUUSD"), CONFIG)
        assert result.passed is True

    def test_gap_within_threshold_fails(self) -> None:
        ctx = _ctx(is_weekend_gap=True, bars_since_gap=1)
        result = filters.check_gap("XAUUSD", ctx.for_symbol("XAUUSD"), CONFIG)
        assert result.passed is False
        assert _code(result) == "RULE_GAP"

    def test_gap_beyond_threshold_passes(self) -> None:
        ctx = _ctx(is_weekend_gap=True, bars_since_gap=10)
        result = filters.check_gap("XAUUSD", ctx.for_symbol("XAUUSD"), CONFIG)
        assert result.passed is True

    def test_no_gap_passes(self) -> None:
        result = filters.check_gap("XAUUSD", _ctx().for_symbol("XAUUSD"), CONFIG)
        assert result.passed is True


class TestRunPreTradeFilters:
    def test_returns_all_filters_in_fixed_order(self) -> None:
        """``RISK_POLICY.md`` §5's own table order: Volatility, Spread, Liquidity, News, then
        Data-quality -- NOT data-quality first. Regression guard for adversarial-review finding #8."""
        config = RiskConfig()
        config.filters.reference_spread["XAUUSD"] = 0.1
        config.filters.liquidity_floor["XAUUSD"] = 100.0
        results = filters.run_pre_trade_filters("XAUUSD", _ctx(), config)
        names = [name for name, _ in results]
        assert names == [
            "FILTER_VOLATILITY", "FILTER_SPREAD", "FILTER_LIQUIDITY", "FILTER_NEWS",
            "DATA_DEGRADED", "RULE_WEEKEND", "RULE_GAP",
        ]
        assert all(r.passed for _, r in results)

    def test_missing_symbol_snapshot_fails_volatility_not_a_crash(self) -> None:
        ctx = RiskContext(as_of=1, per_symbol={})
        results = filters.run_pre_trade_filters("XAUUSD", ctx, RiskConfig())
        by_name = dict(results)
        assert by_name["DATA_DEGRADED"].passed is False

    def test_stale_data_and_bad_volatility_together_surface_volatility_first(self) -> None:
        """When multiple filters would fail simultaneously, the pipeline stops at the FIRST failure
        in the fixed order -- with the policy-table order, that must be FILTER_VOLATILITY, not
        DATA_DEGRADED (the previous, incorrect data-quality-first order would have surfaced
        DATA_DEGRADED here instead)."""
        ctx = _ctx(atr=0.1, atr_rolling_median=1.0, data_quality=DataQualityLevel.STALE)  # both fail
        results = filters.run_pre_trade_filters("XAUUSD", ctx, CONFIG)
        first_failure = next(name for name, result in results if not result.passed)
        assert first_failure == "FILTER_VOLATILITY"

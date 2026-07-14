"""Tests for :mod:`ai_trader.risk_manager.sizing`."""

from __future__ import annotations

from dataclasses import replace

import pytest

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.sizing import SizingOutcome, compute_sizing
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import make_opportunity, make_portfolio
from ai_trader.risk_manager.types import OpenPosition, Sizing
from ai_trader.scoring_engine.types import OpportunityScore, Quality
from ai_trader.signal_engine.types import Direction

CONFIG = RiskConfig()


def _with_quality(opp: OpportunityScore, quality: Quality) -> OpportunityScore:
    """Force a specific ``Quality`` band directly -- decouples sizing tests from the Scoring
    Engine's own total_score arithmetic (which the Risk Manager's tests are not responsible for
    re-verifying), letting each test target a specific quality_factor deterministically."""
    return replace(opp, quality=quality)


def _sizing(outcome: SizingOutcome) -> Sizing:
    assert outcome.sizing is not None
    return outcome.sizing


def _deny_code(outcome: SizingOutcome) -> str:
    assert outcome.deny_reason is not None
    return outcome.deny_reason.code


class TestBasicSizing:
    def test_fixed_fractional_matches_the_formula(self) -> None:
        """POSITION_SIZING.md §1: risk_budget = risk_per_trade_pct * equity;
        size_units = risk_budget / (stop_distance * point_value). Uses a wide stop (distance 5.0)
        so the raw formula result (100 units) stays under the notional cap (200 units) -- isolating
        the base formula from the separate clamping behavior covered by ``TestNotionalCap``."""
        opp = _with_quality(make_opportunity(entry=100.0, stop=95.0), Quality.STRONG)  # factor 1.0
        portfolio = make_portfolio(equity=100_000.0)
        outcome = compute_sizing(opp, portfolio, CONFIG)
        assert outcome.valid is True
        sizing = _sizing(outcome)
        expected_budget = CONFIG.sizing.risk_per_trade_pct * portfolio.equity
        assert sizing.risk_budget_currency == pytest.approx(expected_budget)
        assert sizing.stop_distance == pytest.approx(5.0)
        assert sizing.size_units == pytest.approx(expected_budget / 5.0)

    def test_risk_r_is_always_one(self) -> None:
        opp = make_opportunity()
        outcome = compute_sizing(opp, make_portfolio(), CONFIG)
        assert _sizing(outcome).risk_R == 1.0

    def test_quality_factor_scales_the_risk(self) -> None:
        weak_opp = _with_quality(make_opportunity(entry=100.0, stop=95.0), Quality.WEAK)
        strong_opp = _with_quality(make_opportunity(entry=100.0, stop=95.0), Quality.STRONG)
        weak_outcome = compute_sizing(weak_opp, make_portfolio(equity=100_000.0), CONFIG)
        strong_outcome = compute_sizing(strong_opp, make_portfolio(equity=100_000.0), CONFIG)
        assert _sizing(weak_outcome).risk_per_trade_pct < _sizing(strong_outcome).risk_per_trade_pct


class TestInvalidStop:
    def test_missing_trade_context_is_invalid(self) -> None:
        opp = replace(make_opportunity(), trade_context=None)
        outcome = compute_sizing(opp, make_portfolio(), CONFIG)
        assert outcome.valid is False
        assert _deny_code(outcome) == "INVALID_STOP"

    def test_zero_stop_distance_is_invalid(self) -> None:
        opp = make_opportunity(entry=100.0, stop=100.0)
        outcome = compute_sizing(opp, make_portfolio(), CONFIG)
        assert outcome.valid is False
        assert _deny_code(outcome) == "INVALID_STOP"

    def test_zero_equity_is_invalid(self) -> None:
        opp = make_opportunity()
        outcome = compute_sizing(opp, make_portfolio(equity=0.0), CONFIG)
        assert outcome.valid is False


class TestExposureBudgetClamp:
    def test_remaining_budget_clamps_the_size(self) -> None:
        """POSITION_SIZING.md §3: sizing at the computed size would breach the aggregate cap ->
        reduced to fit the remaining budget."""
        opp = _with_quality(make_opportunity(entry=100.0, stop=99.0), Quality.STRONG)
        existing = OpenPosition(
            symbol="OTHER", strategy_id="S9", direction=Direction.LONG, size_units=1, entry_price=1,
            opened_bars_ago=1, risk_pct=CONFIG.portfolio_limits.max_exposure_pct - 0.001,  # nearly full
        )
        portfolio = make_portfolio(equity=100_000.0, open_positions=(existing,))
        outcome = compute_sizing(opp, portfolio, CONFIG)
        # remaining budget (0.001) < default risk_per_trade_pct (0.005) -> clamped down
        if outcome.valid:
            assert _sizing(outcome).risk_per_trade_pct < CONFIG.sizing.risk_per_trade_pct
        else:
            assert _deny_code(outcome) == "SIZE_BELOW_MIN"

    def test_no_remaining_budget_denies_below_min(self) -> None:
        opp = make_opportunity(entry=100.0, stop=99.0)
        existing = OpenPosition(
            symbol="OTHER", strategy_id="S9", direction=Direction.LONG, size_units=1, entry_price=1,
            opened_bars_ago=1, risk_pct=CONFIG.portfolio_limits.max_exposure_pct,
        )
        portfolio = make_portfolio(equity=100_000.0, open_positions=(existing,))
        outcome = compute_sizing(opp, portfolio, CONFIG)
        assert outcome.valid is False
        assert _deny_code(outcome) == "SIZE_BELOW_MIN"


class TestNotionalCap:
    def test_size_clamped_to_max_notional(self) -> None:
        """POSITION_SIZING.md §6: max_position_notional_pct clamps size even if the risk budget
        would allow more. STRONG quality + the default entry/stop (distance 1.0) already produces a
        raw risk-based size (500 units) well above the notional cap (200 units at 20% of 100k
        equity / $100 entry) -- clamped down, but still comfortably above min_allocation."""
        opp = _with_quality(make_opportunity(entry=100.0, stop=99.0), Quality.STRONG)
        portfolio = make_portfolio(equity=100_000.0)
        outcome = compute_sizing(opp, portfolio, CONFIG)
        assert outcome.valid is True
        sizing = _sizing(outcome)
        max_notional = CONFIG.sizing.max_position_notional_pct * portfolio.equity
        assert sizing.notional == pytest.approx(max_notional)
        # confirms the cap actually engaged (not merely equal to the unclamped size by coincidence)
        unclamped_size = (CONFIG.sizing.risk_per_trade_pct * portfolio.equity) / 1.0
        assert sizing.size_units < unclamped_size


class TestMinAllocation:
    def test_below_min_denies_when_remaining_exposure_budget_is_too_small(self) -> None:
        """Neither tiny equity nor low quality alone can trigger SIZE_BELOW_MIN under the default
        config: risk_budget and min_allocation are both percentages of the SAME equity, so they
        scale together regardless of its absolute value, and risk_per_trade_pct * quality_factor_min
        (0.005*0.5=0.0025) is still above min_allocation_risk_pct (0.001) at every quality tier. The
        genuine trigger is an almost-exhausted exposure budget (POSITION_SIZING.md §3)."""
        opp = make_opportunity(entry=100.0, stop=99.0)
        existing = OpenPosition(
            symbol="OTHER", strategy_id="S9", direction=Direction.LONG, size_units=1, entry_price=1,
            opened_bars_ago=1, risk_pct=CONFIG.portfolio_limits.max_exposure_pct - 0.0005,
        )
        portfolio = make_portfolio(equity=100_000.0, open_positions=(existing,))
        outcome = compute_sizing(opp, portfolio, CONFIG)
        assert outcome.valid is False
        assert _deny_code(outcome) == "SIZE_BELOW_MIN"

    def test_tiny_equity_alone_does_not_trigger_below_min(self) -> None:
        """Regression guard for the proportional-scaling property documented above."""
        opp = _with_quality(make_opportunity(entry=100.0, stop=99.0), Quality.STRONG)
        outcome = compute_sizing(opp, make_portfolio(equity=1.0), CONFIG)
        assert outcome.valid is True


class TestCorrelationGroupBudget:
    """POSITION_SIZING.md §3, sentence 2: trades sharing a correlation group share a smaller,
    deterministic sub-budget of the aggregate exposure cap -- distinct from (and can bind tighter
    than) the pure aggregate-exposure clamp covered by ``TestExposureBudgetClamp``."""

    def test_correlated_positions_share_a_budget_smaller_than_aggregate(self) -> None:
        config = replace(CONFIG, correlation_groups={"XAUUSD": "METALS", "XAGUSD": "METALS"})
        opp = _with_quality(make_opportunity(symbol="XAUUSD", entry=100.0, stop=90.0), Quality.STRONG)
        existing = OpenPosition(
            symbol="XAGUSD", strategy_id="S9", direction=Direction.LONG, size_units=1, entry_price=1,
            opened_bars_ago=1, risk_pct=0.146, correlation_group="METALS",
        )
        portfolio = make_portfolio(equity=100_000.0, open_positions=(existing,))
        # group_budget = max_exposure_pct(0.30) / max_correlated(2) = 0.15; remaining = 0.004,
        # well below the default risk_per_trade_pct*quality_factor (0.005*1.0=0.005) and far below
        # what the aggregate-exposure clamp alone would allow (0.30-0.146=0.154) -- the group budget
        # is the ONLY thing that can be binding here.
        outcome = compute_sizing(opp, portfolio, config)
        assert outcome.valid is True
        assert _sizing(outcome).risk_per_trade_pct == pytest.approx(0.004, abs=1e-9)

    def test_uncorrelated_open_positions_do_not_share_the_budget(self) -> None:
        config = replace(CONFIG, correlation_groups={"XAUUSD": "METALS", "XAGUSD": "METALS"})
        opp = _with_quality(make_opportunity(symbol="XAUUSD", entry=100.0, stop=90.0), Quality.STRONG)
        existing = OpenPosition(
            symbol="EURUSD", strategy_id="S9", direction=Direction.LONG, size_units=1, entry_price=1,
            opened_bars_ago=1, risk_pct=0.20,  # large, but in its own singleton group ("EURUSD")
        )
        portfolio = make_portfolio(equity=100_000.0, open_positions=(existing,))
        outcome = compute_sizing(opp, portfolio, config)
        assert outcome.valid is True
        assert _sizing(outcome).risk_per_trade_pct == pytest.approx(CONFIG.sizing.risk_per_trade_pct)


class TestDeterminism:
    def test_identical_inputs_produce_identical_sizing(self) -> None:
        opp = make_opportunity()
        portfolio = make_portfolio()
        first = compute_sizing(opp, portfolio, CONFIG)
        second = compute_sizing(opp, portfolio, CONFIG)
        assert first == second

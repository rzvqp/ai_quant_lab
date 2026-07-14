"""Tests for :mod:`ai_trader.risk_manager.constraints`."""

from __future__ import annotations

from dataclasses import replace

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.constraints import build_constraints
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import make_opportunity

CONFIG = RiskConfig()


class TestBuildConstraints:
    def test_carries_entry_stop_target_from_trade_context(self) -> None:
        opp = make_opportunity(entry=100.0, stop=99.0, target=102.0)
        c = build_constraints(opp, CONFIG)
        assert c.entry == 100.0
        assert c.stop == 99.0
        assert c.target == 102.0

    def test_max_hold_bars_from_config(self) -> None:
        opp = make_opportunity()
        c = build_constraints(opp, CONFIG)
        assert c.max_hold_bars == CONFIG.constraints.max_hold_bars

    def test_valid_until_from_config(self) -> None:
        opp = make_opportunity()
        c = build_constraints(opp, CONFIG)
        assert c.valid_until == CONFIG.constraints.valid_for_bars

    def test_max_slippage_scales_with_entry_price(self) -> None:
        opp = make_opportunity(entry=200.0)
        c = build_constraints(opp, CONFIG)
        assert c.max_slippage == 200.0 * CONFIG.constraints.max_slippage_pct

    def test_missing_trade_context_leaves_prices_none(self) -> None:
        opp = replace(make_opportunity(), trade_context=None)
        c = build_constraints(opp, CONFIG)
        assert c.entry is None
        assert c.stop is None
        assert c.max_slippage is None

    def test_reduce_only_defaults_false(self) -> None:
        opp = make_opportunity()
        c = build_constraints(opp, CONFIG)
        assert c.reduce_only is False

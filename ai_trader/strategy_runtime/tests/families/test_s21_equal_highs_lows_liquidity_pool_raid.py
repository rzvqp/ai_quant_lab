"""Unit tests for S21 -- Equal-Highs/Lows Liquidity-Pool Raid: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s21_equal_highs_lows_liquidity_pool_raid import (
    S21EqualHighsLowsLiquidityPoolRaid,
)

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S21_equal_highs_lows_liquidity_pool_raid" / "strategy.json"


def make_evaluator() -> S21EqualHighsLowsLiquidityPoolRaid:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S21EqualHighsLowsLiquidityPoolRaid("S21", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], rmax20: float = 2020.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"rmax20": rmax20, "m_atr": atr}, "bars": bars}},
    }


def flat_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


class TestNoSetup:
    def test_raid_without_enough_prior_touches_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(21, 2000.0)  # never near rmax20=2020 -- zero prior touches
        bars.append(bar(bars[-1]["ts_close"] + 900, 2000.0, 2025.0, 1999.0, 2010.0))  # raid, but no touch history
        ctx = make_context(bars, rmax20=2020.0, atr=2.0)
        assert ev.evaluate(ctx).setup_forming is False

    def test_enough_touches_but_no_raid_is_no_setup(self) -> None:
        ev = make_evaluator()
        # 3 bars touching near rmax20, but the current bar doesn't raid (close stays above the level).
        bars = [bar(1000 + i * 900, 2019.9, 2019.95, 2019.5, 2019.8) for i in range(20)]
        bars.append(bar(bars[-1]["ts_close"] + 900, 2019.9, 2020.1, 2019.5, 2020.05))  # no close-back-inside
        ctx = make_context(bars, rmax20=2020.0, atr=2.0)
        assert ev.evaluate(ctx).setup_forming is False


class TestActionable:
    def test_raid_after_enough_prior_touches_is_actionable_short(self) -> None:
        ev = make_evaluator()
        # 20 prior bars touching near rmax20=2020 (within 0.2*ATR=0.4) -- well over min_touches=2.
        bars = [bar(1000 + i * 900, 2019.9, 2019.95, 2019.5, 2019.8) for i in range(20)]
        bars.append(bar(bars[-1]["ts_close"] + 900, 2019.8, 2022.0, 2019.0, 2015.0))  # raid: sweeps then closes back inside
        ctx = make_context(bars, rmax20=2020.0, atr=2.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"
        assert result.entry == 2015.0
        assert result.risk_R == 2.0

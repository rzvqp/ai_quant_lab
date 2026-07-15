"""Unit tests for S46 -- Volume-Confirmed Breakout: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s46_volume_confirmed_breakout import S46VolumeConfirmedBreakout

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S46_volume_confirmed_breakout" / "strategy.json"


def make_evaluator() -> S46VolumeConfirmedBreakout:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S46VolumeConfirmedBreakout("S46", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(
    bars: list[dict], rmax50: float = 2010.0, rmin50: float = 1990.0,  # type: ignore[type-arg]
    volrank: float | None = 0.9, atr: float | None = 2.0,
) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {
            "features": {"rmax50": rmax50, "rmin50": rmin50, "m_volrank": volrank, "m_atr": atr},
            "bars": bars,
        }},
    }


def flat_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


class TestNoSetup:
    def test_low_volrank_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, 2000.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2010.0, 2015.0, 2009.0, 2014.0))
        assert ev.evaluate(make_context(bars, rmax50=2010.0, volrank=0.5)).setup_forming is False

    def test_already_broken_out_before_this_bar_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, 2014.0)  # already above rmax50=2010 the whole window
        assert ev.evaluate(make_context(bars, rmax50=2010.0, volrank=0.9)).setup_forming is False


class TestActionable:
    def test_fresh_high_volrank_breakout_is_actionable_long_with_wide_opposite_stop(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, 2000.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2005.0, 2015.0, 2004.0, 2014.0))
        result = ev.evaluate(make_context(bars, rmax50=2010.0, rmin50=1990.0, volrank=0.9, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.stop == 1990.0 - 2 * 0.1  # opposite (rmin50) extreme, not the breakout level
        assert result.risk_R == 3.0

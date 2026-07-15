"""Unit tests for S38 -- Patient Pullback-into-Zone: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s38_patient_pullback_into_zone import S38PatientPullbackIntoZone

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S38_patient_pullback_into_zone" / "strategy.json"


def make_evaluator() -> S38PatientPullbackIntoZone:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S38PatientPullbackIntoZone("S38", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(
    bars: list[dict], h1_trend_up: bool | None = True, ema20: float = 2000.0,  # type: ignore[type-arg]
    rmax20: float = 2050.0, rmin20: float = 1950.0, atr: float | None = 2.0,
) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {
            "features": {"h1_trend_up": h1_trend_up, "m_ema20": ema20, "rmax20": rmax20, "rmin20": rmin20, "m_atr": atr},
            "bars": bars,
        }},
    }


class TestNoSetup:
    def test_no_touch_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2010.0, 2011.0, 2009.0, 2010.0), bar(1900, 2010.0, 2011.0, 2009.0, 2010.0)]
        assert ev.evaluate(make_context(bars, h1_trend_up=True, ema20=2000.0)).setup_forming is False

    def test_already_touching_before_this_bar_is_no_setup(self) -> None:
        ev = make_evaluator()
        touching = bar(1000, 2001.0, 2001.5, 1999.0, 2000.5)  # low=1999 <= ema20=2000
        assert ev.evaluate(make_context([touching, touching], h1_trend_up=True, ema20=2000.0)).setup_forming is False


class TestActionable:
    def test_fresh_uptrend_pullback_touch_is_actionable_long_with_trailing(self) -> None:
        ev = make_evaluator()
        above = bar(1000, 2010.0, 2011.0, 2009.0, 2010.0)
        touch = bar(1900, 2009.0, 2009.5, 1999.0, 2000.5)  # low=1999 <= ema20=2000, fresh
        result = ev.evaluate(make_context([above, touch], h1_trend_up=True, ema20=2000.0, rmin20=1950.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.target is None
        assert ev.trailing_stop_atr_mult == 1.5

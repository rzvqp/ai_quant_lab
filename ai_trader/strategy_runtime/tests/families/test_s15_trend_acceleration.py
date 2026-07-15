"""Unit tests for S15 -- Trend Acceleration: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s15_trend_acceleration import S15TrendAcceleration

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S15_trend_acceleration" / "strategy.json"


def make_evaluator() -> S15TrendAcceleration:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S15TrendAcceleration("S15", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], h1_trend_up: bool | None = True, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"h1_trend_up": h1_trend_up, "m_atr": atr}, "bars": bars}},
    }


class TestNoSetup:
    def test_no_expansion_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2000.0, 2000.5, 1999.5, 2000.2), bar(1900, 2000.2, 2000.7, 1999.7, 2000.4)]
        assert ev.evaluate(make_context(bars, h1_trend_up=True)).setup_forming is False

    def test_already_expanding_before_this_bar_is_no_setup(self) -> None:
        ev = make_evaluator()
        expanding = bar(1000, 2000.0, 2010.0, 1999.5, 2008.0)
        assert ev.evaluate(make_context([expanding, expanding], h1_trend_up=True)).setup_forming is False


class TestActionable:
    def test_fresh_uptrend_expansion_is_actionable_long_with_trailing(self) -> None:
        ev = make_evaluator()
        flat = bar(1000, 2000.0, 2000.5, 1999.5, 2000.2)
        expanding = bar(1900, 2000.2, 2010.0, 1999.5, 2008.0)  # range=10.5 > 1.5*2=3, bullish
        result = ev.evaluate(make_context([flat, expanding], h1_trend_up=True, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.target is None
        assert ev.trailing_stop_atr_mult == 1.5

"""Unit tests for S50 -- Outside-Bar / Engulfing Reversal: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s50_outside_bar_engulfing_reversal import (
    S50OutsideBarEngulfingReversal,
)

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S50_outside_bar_engulfing_reversal" / "strategy.json"


def make_evaluator() -> S50OutsideBarEngulfingReversal:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S50OutsideBarEngulfingReversal("S50", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"m_atr": atr}, "bars": bars}},
    }


class TestNoSetup:
    def test_inside_bar_is_no_setup(self) -> None:
        ev = make_evaluator()
        prev = bar(1000, 2000.0, 2001.0, 1999.0, 2000.0)
        cur = bar(1900, 2000.0, 2000.5, 1999.5, 2000.2)
        assert ev.evaluate(make_context([prev, cur], atr=2.0)).setup_forming is False

    def test_outside_bar_without_range_expansion_is_no_setup(self) -> None:
        ev = make_evaluator()
        prev = bar(1000, 2000.0, 2000.5, 1999.5, 2000.0)
        cur = bar(1900, 2000.0, 2000.7, 1999.3, 2000.5)  # outside but range (1.4) < atr (2.0)
        assert ev.evaluate(make_context([prev, cur], atr=2.0)).setup_forming is False


class TestActionable:
    def test_bullish_engulfing_expansion_fades_short(self) -> None:
        ev = make_evaluator()
        prev = bar(1000, 2000.0, 2000.5, 1999.5, 2000.0)
        cur = bar(1900, 1998.0, 2003.0, 1996.0, 2002.0)  # outside, range=7>atr=2, bullish close
        result = ev.evaluate(make_context([prev, cur], atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"
        assert result.stop == cur["high"] + 2 * 0.1  # RESEARCH_ENGINE_TICK=0.1
        assert result.risk_R == 2.0

    def test_bearish_engulfing_expansion_fades_long(self) -> None:
        ev = make_evaluator()
        prev = bar(1000, 2000.0, 2000.5, 1999.5, 2000.0)
        cur = bar(1900, 2002.0, 2003.0, 1996.0, 1998.0)  # outside, range=7>atr=2, bearish close
        result = ev.evaluate(make_context([prev, cur], atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"

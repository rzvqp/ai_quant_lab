"""Unit tests for S5 -- Opening-Range Breakout: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s05_opening_range_breakout import S05OpeningRangeBreakout

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S05_opening_range_breakout" / "strategy.json"


def make_evaluator() -> S05OpeningRangeBreakout:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S05OpeningRangeBreakout("S5", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(
    bars: list[dict], session: str = "ny", bar_in_sess: int = 6, or_high: float = 2010.0,  # type: ignore[type-arg]
    atr: float | None = 2.0,
) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {
            "features": {"session": session, "bar_in_sess": bar_in_sess, "or_high": or_high, "m_atr": atr},
            "bars": bars,
        }},
    }


class TestNoSetup:
    def test_wrong_session_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2015.0, 2015.5, 2014.5, 2015.0)]
        assert ev.evaluate(make_context(bars, session="london")).setup_forming is False

    def test_before_or_formed_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2015.0, 2015.5, 2014.5, 2015.0)]
        assert ev.evaluate(make_context(bars, bar_in_sess=2)).setup_forming is False

    def test_close_below_or_high_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2005.0, 2005.5, 2004.5, 2005.0)]
        assert ev.evaluate(make_context(bars, or_high=2010.0)).setup_forming is False


class TestActionable:
    def test_close_above_or_high_within_session_is_actionable_long(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2010.0, 2016.0, 2009.5, 2015.0)]
        result = ev.evaluate(make_context(bars, session="ny", bar_in_sess=6, or_high=2010.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 2015.0
        assert result.risk_R == 2.0

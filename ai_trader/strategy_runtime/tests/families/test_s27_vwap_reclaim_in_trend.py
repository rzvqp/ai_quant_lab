"""Unit tests for S27 -- VWAP Reclaim in Trend: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s27_vwap_reclaim_in_trend import S27VwapReclaimInTrend

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S27_vwap_reclaim_in_trend" / "strategy.json"


def make_evaluator() -> S27VwapReclaimInTrend:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S27VwapReclaimInTrend("S27", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(
    bars: list[dict], h4_trend_up: bool | None, vwap: float = 2000.0, std: float = 4.0,  # type: ignore[type-arg]
    atr: float | None = 2.0,
) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {
            "features": {"h4_trend_up": h4_trend_up, "vwap": vwap, "m_std": std, "m_atr": atr},
            "bars": bars,
        }},
    }


class TestNoSetup:
    def test_uptrend_but_no_reclaim_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 1990.0, 1991.0, 1989.0, 1990.0), bar(1900, 1990.0, 1991.0, 1989.0, 1990.0)]
        assert ev.evaluate(make_context(bars, h4_trend_up=True, vwap=2000.0)).setup_forming is False

    def test_already_above_vwap_before_this_bar_is_no_setup(self) -> None:
        ev = make_evaluator()
        above = bar(1000, 2005.0, 2006.0, 2004.0, 2005.0)
        assert ev.evaluate(make_context([above, above], h4_trend_up=True, vwap=2000.0)).setup_forming is False


class TestActionable:
    def test_uptrend_fresh_reclaim_above_vwap_is_actionable_long(self) -> None:
        ev = make_evaluator()
        below = bar(1000, 1998.0, 1999.0, 1997.0, 1998.0)
        reclaim = bar(1900, 1998.0, 2003.0, 1997.5, 2002.0)
        result = ev.evaluate(make_context([below, reclaim], h4_trend_up=True, vwap=2000.0, std=4.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.stop == 2000.0 - 0.25 * 4.0  # vwap - 0.25*std -- floor never binds here
        assert result.target == 2000.0 + 1.0 * 4.0  # far vwap band, NOT a literal 2R target
        assert result.risk_R is None

    def test_downtrend_fresh_break_below_vwap_is_actionable_short(self) -> None:
        ev = make_evaluator()
        above = bar(1000, 2002.0, 2003.0, 2001.0, 2002.0)
        break_below = bar(1900, 2002.0, 2002.5, 1997.0, 1998.0)
        result = ev.evaluate(make_context([above, break_below], h4_trend_up=False, vwap=2000.0, std=4.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"

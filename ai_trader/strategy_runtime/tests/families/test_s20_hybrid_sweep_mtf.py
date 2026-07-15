"""Unit tests for S20 -- Hybrid Sweep + MTF: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s20_hybrid_sweep_mtf import S20HybridSweepMtf

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S20_hybrid_sweep_mtf" / "strategy.json"


def make_evaluator() -> S20HybridSweepMtf:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S20HybridSweepMtf("S20", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], h4_trend_up: bool | None = True, rmax20: float = 2010.0, rmin20: float = 1990.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {
            "features": {"h4_trend_up": h4_trend_up, "rmax20": rmax20, "rmin20": rmin20, "m_atr": atr},
            "bars": bars,
        }},
    }


class TestNoSetup:
    def test_downtrend_h4_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2000.0, 2000.5, 1999.5, 2000.0), bar(1900, 2000.0, 2015.0, 1999.5, 2012.0)]
        assert ev.evaluate(make_context(bars, h4_trend_up=False, rmax20=2010.0)).setup_forming is False

    def test_already_above_before_this_bar_is_no_setup(self) -> None:
        ev = make_evaluator()
        above = bar(1000, 2012.0, 2013.0, 2011.5, 2012.0)
        assert ev.evaluate(make_context([above, above], h4_trend_up=True, rmax20=2010.0)).setup_forming is False


class TestActionable:
    def test_fresh_breakout_aligned_with_h4_is_actionable_long(self) -> None:
        ev = make_evaluator()
        below = bar(1000, 2005.0, 2006.0, 2004.0, 2005.0)
        breakout = bar(1900, 2005.0, 2013.0, 2004.5, 2012.0)
        result = ev.evaluate(make_context([below, breakout], h4_trend_up=True, rmax20=2010.0, rmin20=1990.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.risk_R == 2.0

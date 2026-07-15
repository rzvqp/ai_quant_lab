"""Unit tests for S41 -- Volume-Climax Reversal: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s41_volume_climax_reversal import S41VolumeClimaxReversal

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S41_volume_climax_reversal" / "strategy.json"


def make_evaluator() -> S41VolumeClimaxReversal:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S41VolumeClimaxReversal("S41", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], rmax20: float = 2010.0, rmin20: float = 1990.0, volrank: float | None = 0.95, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {
            "features": {"rmax20": rmax20, "rmin20": rmin20, "m_volrank": volrank, "m_atr": atr},
            "bars": bars,
        }},
    }


class TestNoSetup:
    def test_low_volrank_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2005.0, 2011.0, 2004.0, 2010.0), bar(1900, 2010.0, 2012.0, 2009.0, 2011.0)]
        assert ev.evaluate(make_context(bars, rmax20=2010.0, volrank=0.5)).setup_forming is False


class TestActionable:
    def test_fresh_climax_at_20bar_low_is_actionable_long(self) -> None:
        ev = make_evaluator()
        above = bar(1000, 1995.0, 1996.0, 1994.0, 1995.0)
        climax = bar(1900, 1994.0, 1994.5, 1988.0, 1990.0)  # touches below rmin20=1990
        result = ev.evaluate(make_context([above, climax], rmax20=2010.0, rmin20=1990.0, volrank=0.95, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.stop == 1988.0 - 2 * 0.1
        assert result.risk_R == 2.0

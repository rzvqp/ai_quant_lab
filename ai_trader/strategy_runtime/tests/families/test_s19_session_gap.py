"""Unit tests for S19 -- Session Gap: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s19_session_gap import S19SessionGap

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S19_session_gap" / "strategy.json"


def make_evaluator() -> S19SessionGap:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S19SessionGap("S19", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], gap: float | None, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"gap": gap, "m_atr": atr}, "bars": bars}},
    }


class TestNoSetup:
    def test_no_gap_feature_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [{"ts_open": 0, "ts_close": 900, "open": 2000.0, "high": 2000.5, "low": 1999.5, "close": 2000.2}]
        assert ev.evaluate(make_context(bars, gap=None)).setup_forming is False

    def test_small_down_gap_below_threshold_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [{"ts_open": 0, "ts_close": 900, "open": 1999.0, "high": 1999.5, "low": 1998.5, "close": 1999.2}]
        assert ev.evaluate(make_context(bars, gap=-0.5, atr=2.0)).setup_forming is False  # -0.5 > -0.5*2.0

    def test_up_gap_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [{"ts_open": 0, "ts_close": 900, "open": 2001.0, "high": 2001.5, "low": 2000.5, "close": 2001.2}]
        assert ev.evaluate(make_context(bars, gap=3.0, atr=2.0)).setup_forming is False


class TestActionable:
    def test_qualifying_down_gap_is_actionable_long_with_time_stop(self) -> None:
        ev = make_evaluator()
        bars = [{"ts_open": 0, "ts_close": 900, "open": 1995.0, "high": 1996.0, "low": 1994.0, "close": 1995.5}]
        result = ev.evaluate(make_context(bars, gap=-1.5, atr=2.0))  # -1.5 < -0.5*2.0=-1.0
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 1995.5
        assert result.stop is not None and result.stop < result.entry
        assert result.target is None
        assert ev.time_stop_bars == 24

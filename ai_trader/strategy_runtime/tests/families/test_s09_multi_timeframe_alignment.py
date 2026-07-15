"""Unit tests for S9 -- Multi-Timeframe Alignment: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s09_multi_timeframe_alignment import S09MultiTimeframeAlignment

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S09_multi_timeframe_alignment" / "strategy.json"


def make_evaluator() -> S09MultiTimeframeAlignment:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S09MultiTimeframeAlignment("S9", contract, frozenset({"XAUUSD"}))


def bar(ts: int, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": c, "high": c + 0.1, "low": c - 0.1, "close": c}


def make_context(closes: list[float], h4_trend_up: bool | None = True, rmin20: float = 1990.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    bars = [bar(1000 + i * 900, c) for i, c in enumerate(closes)]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"h4_trend_up": h4_trend_up, "rmin20": rmin20, "m_atr": atr}, "bars": bars}},
    }


class TestNoSetup:
    def test_downtrend_h4_is_no_setup(self) -> None:
        ev = make_evaluator()
        closes = [2000.0] * 11 + [2010.0]
        assert ev.evaluate(make_context(closes, h4_trend_up=False)).setup_forming is False

    def test_no_breakout_is_no_setup(self) -> None:
        ev = make_evaluator()
        closes = [2000.0] * 12
        assert ev.evaluate(make_context(closes, h4_trend_up=True)).setup_forming is False


class TestActionable:
    def test_fresh_10bar_closing_breakout_aligned_with_h4_is_actionable_long(self) -> None:
        ev = make_evaluator()
        closes = [2000.0] * 11 + [2010.0]  # last close breaks above the prior 10 flat closes
        result = ev.evaluate(make_context(closes, h4_trend_up=True, rmin20=1990.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.risk_R == 3.0

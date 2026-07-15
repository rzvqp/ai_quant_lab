"""Unit tests for S45 -- Consecutive-Bar Streak: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s45_consecutive_bar_streak import S45ConsecutiveBarStreak

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S45_consecutive_bar_streak" / "strategy.json"


def make_evaluator() -> S45ConsecutiveBarStreak:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S45ConsecutiveBarStreak("S45", contract, frozenset({"XAUUSD"}))


def bar(ts: int, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": c, "high": c + 0.1, "low": c - 0.1, "close": c}


def make_context(closes: list[float], atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    bars = [bar(1000 + i * 900, c) for i, c in enumerate(closes)]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"m_atr": atr}, "bars": bars}},
    }


class TestNoSetup:
    def test_no_streak_is_no_setup(self) -> None:
        ev = make_evaluator()
        assert ev.evaluate(make_context([100, 101, 100.5, 101.5, 101.0, 102.0, 101.5])).setup_forming is False

    def test_streak_longer_than_6_is_no_setup(self) -> None:
        ev = make_evaluator()
        closes = [95.0 + i for i in range(9)]  # 8 consecutive up closes -- streak is 7 (not exactly 6)
        assert ev.evaluate(make_context(closes)).setup_forming is False


class TestActionable:
    def test_exact_6_up_streak_fades_short(self) -> None:
        ev = make_evaluator()
        closes = [99.0] + [100.0 + i for i in range(6)]  # down then exactly 6 up closes
        result = ev.evaluate(make_context(closes, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"
        assert result.target is None
        assert ev.time_stop_bars == 24

    def test_exact_6_down_streak_fades_long(self) -> None:
        ev = make_evaluator()
        closes = [107.0] + [106.0 - i for i in range(6)]  # up then exactly 6 down closes
        result = ev.evaluate(make_context(closes, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"

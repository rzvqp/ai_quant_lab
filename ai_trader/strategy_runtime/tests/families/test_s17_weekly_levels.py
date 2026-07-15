"""Unit tests for S17 -- Weekly Levels: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s17_weekly_levels import S17WeeklyLevels

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S17_weekly_levels" / "strategy.json"


def make_evaluator() -> S17WeeklyLevels:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S17WeeklyLevels("S17", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], pw_high: float | None = 2010.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"pw_high": pw_high, "m_atr": atr}, "bars": bars}},
    }


def flat_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


class TestNoSetup:
    def test_no_wick_above_pw_high_is_no_setup(self) -> None:
        ev = make_evaluator()
        ctx = make_context(flat_bars(3, 1990.0), pw_high=2010.0)
        assert ev.evaluate(ctx).setup_forming is False

    def test_clean_close_above_pw_high_without_rejection_is_no_setup(self) -> None:
        """A clean breakout close (no wick-and-reject) is not the S17 'reject' mechanism."""
        ev = make_evaluator()
        bars = flat_bars(3, 1990.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 1990.0, 2015.0, 1989.0, 2015.0))  # closes ABOVE pw_high
        ctx = make_context(bars, pw_high=2010.0)
        assert ev.evaluate(ctx).setup_forming is False


class TestActionable:
    def test_fresh_rejection_at_pw_high_is_actionable_short_with_time_stop(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, 2000.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2000.0, 2012.0, 1999.0, 2005.0))  # wick above, close back below
        ctx = make_context(bars, pw_high=2010.0, atr=2.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"
        assert result.entry == 2005.0
        assert result.stop is not None and result.stop > result.entry
        assert result.target is None
        assert ev.time_stop_bars == 24

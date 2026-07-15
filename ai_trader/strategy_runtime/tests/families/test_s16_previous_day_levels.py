"""Unit tests for S16 -- Previous-Day Levels: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s16_previous_day_levels import S16PreviousDayLevels

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S16_previous_day_levels" / "strategy.json"


def make_evaluator() -> S16PreviousDayLevels:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S16PreviousDayLevels("S16", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], pd_close: float | None = 2000.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"pd_close": pd_close, "m_atr": atr}, "bars": bars}},
    }


def flat_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


class TestNoSetup:
    def test_missing_pd_close_is_no_setup(self) -> None:
        ev = make_evaluator()
        ctx = make_context(flat_bars(3, 2010.0), pd_close=None)
        assert ev.evaluate(ctx).setup_forming is False

    def test_already_above_pd_close_before_this_bar_is_no_setup(self) -> None:
        """Onset semantics: the previous bar was already above pd_close -- not a FRESH cross."""
        ev = make_evaluator()
        bars = flat_bars(3, 2010.0)  # every bar already above pd_close=2000
        ctx = make_context(bars, pd_close=2000.0)
        assert ev.evaluate(ctx).setup_forming is False


class TestActionable:
    def test_fresh_close_above_pd_close_is_actionable_with_time_stop(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, 1995.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 1995.0, 2005.0, 1994.0, 2005.0))  # fresh cross above 2000
        ctx = make_context(bars, pd_close=2000.0, atr=2.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 2005.0
        assert result.stop is not None and result.stop < result.entry
        assert result.target is None  # time-exit only, no price target
        assert result.risk_R is None
        assert ev.time_stop_bars == 24

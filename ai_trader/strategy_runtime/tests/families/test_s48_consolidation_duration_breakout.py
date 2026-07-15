"""Unit tests for S48 -- Consolidation-Duration Breakout: hand-constructed bar sequences plus
hand-constructed ``feature_history`` (the Phase 6.8 Wave B historical-features window), no live
data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s48_consolidation_duration_breakout import (
    S48ConsolidationDurationBreakout,
)

CONTRACT_PATH = (
    Path(__file__).resolve().parents[4]
    / "knowledge" / "strategies" / "S48_consolidation_duration_breakout" / "strategy.json"
)

D = 6  # CONSOLIDATION_BARS


def make_evaluator() -> S48ConsolidationDurationBreakout:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S48ConsolidationDurationBreakout("S48", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def coil_bars(n: int, price: float, start_ts: int = 1000) -> list[dict]:  # type: ignore[type-arg]
    return [bar(start_ts + i * 900, price, price + 0.3, price - 0.3, price) for i in range(n)]


def make_context(bars: list[dict], compress_flags: list[bool], atr: float | None = 1.0) -> dict:  # type: ignore[type-arg]
    history = [{"compress": f} for f in compress_flags]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"m_atr": atr}, "bars": bars, "feature_history": history}},
    }


def _coiled_then(breakout_bar: dict) -> tuple[list[dict], list[bool]]:  # type: ignore[type-arg]
    """D+2 compressed bars (coil sustained BOTH as-of the signal bar and as-of the bar before it,
    so the onset filter sees a truly FRESH breakout) followed by one breakout bar."""
    bars = coil_bars(D + 2, 2000.0)
    bars.append(breakout_bar)
    flags = [True] * (D + 3)
    return bars, flags


class TestNoSetup:
    def test_insufficient_history_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = coil_bars(3, 2000.0)
        ctx = make_context(bars, [True, True, True])
        assert ev.evaluate(ctx).setup_forming is False

    def test_coil_not_sustained_is_no_setup(self) -> None:
        ev = make_evaluator()
        breakout = bar(1000 + (D + 2) * 900, 2000.0, 2004.0, 1999.5, 2003.5)
        bars, flags = _coiled_then(breakout)
        flags[-2] = False  # one bar of the D-bar window (just before the signal) was NOT compressed
        ctx = make_context(bars, flags, atr=1.0)
        assert ev.evaluate(ctx).setup_forming is False

    def test_no_band_break_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = coil_bars(D + 3, 2000.0)  # stays inside the coil band the whole time
        flags = [True] * (D + 3)
        ctx = make_context(bars, flags, atr=1.0)
        assert ev.evaluate(ctx).setup_forming is False


class TestActionable:
    def test_fresh_upside_breakout_after_sustained_coil_is_actionable_long(self) -> None:
        ev = make_evaluator()
        breakout = bar(1000 + (D + 2) * 900, 2000.0, 2005.0, 1999.5, 2004.5)  # closes above the 0.3-wide coil band
        bars, flags = _coiled_then(breakout)
        ctx = make_context(bars, flags, atr=1.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 2004.5
        assert result.stop is not None and result.stop < result.entry
        assert result.target is None  # trailing-exit only, no fixed price target
        assert result.risk_R is None
        assert ev.trailing_stop_atr_mult == 1.5

    def test_fresh_downside_breakout_after_sustained_coil_is_actionable_short(self) -> None:
        ev = make_evaluator()
        breakout = bar(1000 + (D + 2) * 900, 2000.0, 2000.5, 1995.0, 1995.5)  # closes below the coil band
        bars, flags = _coiled_then(breakout)
        ctx = make_context(bars, flags, atr=1.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present
        assert result.direction == "SHORT"
        assert result.entry == 1995.5
        assert result.stop is not None and result.stop > result.entry

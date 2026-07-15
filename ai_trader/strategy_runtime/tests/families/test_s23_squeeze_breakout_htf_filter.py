"""Unit tests for S23 -- Squeeze Breakout + HTF Filter: hand-constructed bar sequences plus
hand-constructed ``feature_history`` (the Phase 6.8 Wave B historical-features window), no live
data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s23_squeeze_breakout_htf_filter import (
    S23SqueezeBreakoutHtfFilter,
)

CONTRACT_PATH = (
    Path(__file__).resolve().parents[4]
    / "knowledge" / "strategies" / "S23_squeeze_breakout_htf_filter" / "strategy.json"
)


def make_evaluator() -> S23SqueezeBreakoutHtfFilter:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S23SqueezeBreakoutHtfFilter("S23", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def squeeze_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.5, price - 0.5, price) for i in range(n)]


def make_context(
    bars: list[dict], compress_flags: list[bool], atr: float | None = 1.0, h4_trend_up: bool | None = True  # type: ignore[type-arg]
) -> dict:  # type: ignore[type-arg]
    history = [{"compress": f} for f in compress_flags]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {
            "M15": {"features": {"m_atr": atr, "h4_trend_up": h4_trend_up}, "bars": bars, "feature_history": history}
        },
    }


class TestNoSetup:
    def test_missing_htf_trend_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = squeeze_bars(4, 2000.0)
        ctx = make_context(bars, [True, True, True, True], h4_trend_up=None)
        assert ev.evaluate(ctx).setup_forming is False

    def test_squeeze_not_sustained_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = squeeze_bars(3, 2000.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2000.0, 2003.0, 1999.5, 2002.5))  # breaks 0.5-range squeeze
        history = [True, True, False, True]  # only 2 of the last 3 compressed -- not sustained
        ctx = make_context(bars, history, atr=1.0, h4_trend_up=True)
        assert ev.evaluate(ctx).setup_forming is False

    def test_no_breakout_beyond_squeeze_range_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = squeeze_bars(4, 2000.0)  # last bar itself stays inside the squeeze range
        history = [True, True, True, True]
        ctx = make_context(bars, history, atr=1.0, h4_trend_up=True)
        assert ev.evaluate(ctx).setup_forming is False

    def test_breakout_against_htf_trend_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = squeeze_bars(3, 2000.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2000.0, 2003.0, 1999.5, 2002.5))  # upside breakout
        history = [True, True, True, True]
        ctx = make_context(bars, history, atr=1.0, h4_trend_up=False)  # HTF is DOWN -- long breakout rejected
        assert ev.evaluate(ctx).setup_forming is False


class TestActionable:
    def test_sustained_squeeze_upside_breakout_with_uptrend_is_actionable_long(self) -> None:
        ev = make_evaluator()
        bars = squeeze_bars(3, 2000.0)  # 3-bar squeeze range: high=2000.5, low=1999.5
        bars.append(bar(bars[-1]["ts_close"] + 900, 2000.0, 2003.0, 1999.5, 2002.5))  # closes beyond 2000.5
        history = [True, True, True, True]
        ctx = make_context(bars, history, atr=1.0, h4_trend_up=True)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 2002.5
        assert result.stop is not None and result.stop < result.entry
        assert result.target is None  # trailing-exit only, no fixed price target
        assert result.risk_R is None
        assert ev.trailing_stop_atr_mult == 1.5

    def test_sustained_squeeze_downside_breakout_with_downtrend_is_actionable_short(self) -> None:
        ev = make_evaluator()
        bars = squeeze_bars(3, 2000.0)  # 3-bar squeeze range: high=2000.5, low=1999.5
        bars.append(bar(bars[-1]["ts_close"] + 900, 2000.0, 2000.5, 1997.0, 1997.5))  # closes beyond 1999.5
        history = [True, True, True, True]
        ctx = make_context(bars, history, atr=1.0, h4_trend_up=False)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present
        assert result.direction == "SHORT"
        assert result.entry == 1997.5
        assert result.stop is not None and result.stop > result.entry

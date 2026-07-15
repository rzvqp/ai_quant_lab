"""Unit tests for S43 -- Momentum Divergence (RSI/Price): hand-constructed bar sequences plus
hand-constructed ``feature_history`` (the Phase 6.8 Wave B historical-features window), no live
data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s43_momentum_divergence_rsi_price import (
    S43MomentumDivergenceRsiPrice,
)

CONTRACT_PATH = (
    Path(__file__).resolve().parents[4]
    / "knowledge" / "strategies" / "S43_momentum_divergence_rsi_price" / "strategy.json"
)

LB = 14  # LOOKBACK_BARS


def make_evaluator() -> S43MomentumDivergenceRsiPrice:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S43MomentumDivergenceRsiPrice("S43", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def flat_bars(n: int, price: float, start_ts: int = 1000) -> list[dict]:  # type: ignore[type-arg]
    return [bar(start_ts + i * 900, price, price + 0.2, price - 0.2, price) for i in range(n)]


def make_context(bars: list[dict], rsi_history: list[float], atr: float | None = 1.0) -> dict:  # type: ignore[type-arg]
    history = [{"m_rsi": r} for r in rsi_history]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"m_atr": atr, "m_rsi": rsi_history[-1]}, "bars": bars, "feature_history": history}},
    }


def _bearish_divergence_setup() -> tuple[list[dict], list[float]]:  # type: ignore[type-arg]
    """LB+2 flat bars (RSI oscillating around 55, never a fresh divergence) followed by ONE bar
    that makes a new price HIGH while RSI stays below its own recent high -- a fresh bearish
    divergence, onset-only (not present the bar before)."""
    bars = flat_bars(LB + 2, 2000.0)
    rsi = [55.0] * (LB + 2)
    breakout = bar(bars[-1]["ts_close"] + 900, 2000.0, 2010.0, 1999.5, 2001.0)  # new LB-bar price high
    bars.append(breakout)
    rsi.append(50.0)  # RSI well below its own recent high (55) -- bearish divergence
    return bars, rsi


class TestNoSetup:
    def test_insufficient_history_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(4, 2000.0)
        ctx = make_context(bars, [50.0, 51.0, 52.0, 53.0])
        assert ev.evaluate(ctx).setup_forming is False

    def test_missing_atr_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars, rsi = _bearish_divergence_setup()
        ctx = make_context(bars, rsi, atr=None)
        assert ev.evaluate(ctx).setup_forming is False

    def test_new_price_high_with_confirming_rsi_is_no_setup(self) -> None:
        """No divergence: RSI ALSO makes a new high alongside price -- momentum confirms, not weakens.
        Low stays inside the prior range (1999.9 > the flat bars' own 1999.8 low) so this bar does
        not ALSO register as a fresh price low and accidentally trip the bullish-divergence branch."""
        ev = make_evaluator()
        bars = flat_bars(LB + 2, 2000.0)
        rsi = [55.0] * (LB + 2)
        breakout = bar(bars[-1]["ts_close"] + 900, 2000.0, 2010.0, 1999.9, 2001.0)
        bars.append(breakout)
        rsi.append(60.0)  # RSI makes a fresh high too -- no divergence
        ctx = make_context(bars, rsi, atr=1.0)
        assert ev.evaluate(ctx).setup_forming is False

    def test_divergence_already_present_last_bar_is_not_fresh_no_setup(self) -> None:
        ev = make_evaluator()
        bars, rsi = _bearish_divergence_setup()
        # extend one more bar that STILL has a new price high with lagging RSI -- divergence
        # persists, so the second occurrence is not a fresh onset.
        bars.append(bar(bars[-1]["ts_close"] + 900, 2001.0, 2011.0, 2000.5, 2002.0))
        rsi.append(49.0)
        ctx = make_context(bars, rsi, atr=1.0)
        assert ev.evaluate(ctx).setup_forming is False


class TestActionable:
    def test_fresh_bearish_divergence_is_actionable_short(self) -> None:
        ev = make_evaluator()
        bars, rsi = _bearish_divergence_setup()
        ctx = make_context(bars, rsi, atr=1.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"
        assert result.entry == 2001.0
        assert result.stop is not None and result.stop > result.entry
        assert result.target is not None and result.target < result.entry  # rr2, SHORT
        assert result.risk_R == 2.0

    def test_fresh_bullish_divergence_is_actionable_long(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(LB + 2, 2000.0)
        rsi = [45.0] * (LB + 2)
        breakout = bar(bars[-1]["ts_close"] + 900, 2000.0, 2000.5, 1990.0, 1999.0)  # new LB-bar price low
        bars.append(breakout)
        rsi.append(50.0)  # RSI well above its own recent low (45) -- bullish divergence
        ctx = make_context(bars, rsi, atr=1.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present
        assert result.direction == "LONG"
        assert result.entry == 1999.0
        assert result.stop is not None and result.stop < result.entry
        assert result.target is not None and result.target > result.entry  # rr2, LONG
        assert result.risk_R == 2.0

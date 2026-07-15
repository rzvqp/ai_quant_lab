"""Unit tests for S39 -- Trend-Efficiency-Gated Continuation: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s39_trend_efficiency_gated_continuation import (
    S39TrendEfficiencyGatedContinuation,
)

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S39_trend_efficiency_gated_continuation" / "strategy.json"


def make_evaluator() -> S39TrendEfficiencyGatedContinuation:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S39TrendEfficiencyGatedContinuation("S39", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], m_trend_up: bool | None = True, rmax20: float = 2100.0, rmin20: float = 1900.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {
            "features": {"m_trend_up": m_trend_up, "rmax20": rmax20, "rmin20": rmin20, "m_atr": atr},
            "bars": bars,
        }},
    }


def _clean_uptrend_bars(n: int, start: float, step: float) -> list[dict]:  # type: ignore[type-arg]
    """A perfectly straight-line move -- efficiency ratio == 1.0 (maximally efficient)."""
    bars = []
    price = start
    for i in range(n):
        price += step
        bars.append(bar(1000 + i * 900, price - step, price, price - step - 0.05, price))
    return bars


class TestNoSetup:
    def test_choppy_market_below_er_threshold_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = []
        price = 2000.0
        for i in range(22):
            price += 1.0 if i % 2 == 0 else -1.0  # zig-zag -- net move ~0, ER near 0
            bars.append(bar(1000 + i * 900, price, price + 0.2, price - 0.2, price))
        assert ev.evaluate(make_context(bars)).setup_forming is False


class TestActionable:
    def test_efficient_trend_expansion_bar_is_actionable_long(self) -> None:
        ev = make_evaluator()
        bars = _clean_uptrend_bars(20, 2000.0, 1.0)  # ER == 1.0 over the 20-bar window
        # final expansion bar, range > 1.5*ATR=3.0, closes bullish, in the trend direction.
        last_open = bars[-1]["close"]
        bars.append(bar(bars[-1]["ts_close"] + 900, last_open, last_open + 5.0, last_open - 0.5, last_open + 4.5))
        result = ev.evaluate(make_context(bars, m_trend_up=True, rmax20=2100.0, rmin20=1900.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.risk_R == 2.0

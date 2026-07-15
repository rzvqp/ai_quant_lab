"""Unit tests for S7 -- Trend Pullback Continuation: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s07_trend_pullback_continuation import S07TrendPullbackContinuation

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S07_trend_pullback_continuation" / "strategy.json"


def make_evaluator() -> S07TrendPullbackContinuation:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S07TrendPullbackContinuation("S7", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], h4_trend_up: bool | None = True, ema20: float = 2000.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"h4_trend_up": h4_trend_up, "m_ema20": ema20, "m_atr": atr}, "bars": bars}},
    }


def flat_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


class TestNoSetup:
    def test_no_pullback_is_no_setup(self) -> None:
        ev = make_evaluator()
        assert ev.evaluate(make_context(flat_bars(10, 2010.0), h4_trend_up=True, ema20=2000.0)).setup_forming is False

    def test_pullback_without_confirmation_yet_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(10, 2010.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2005.0, 2005.5, 1995.0, 1998.0))  # pulled below ema
        assert ev.evaluate(make_context(bars, h4_trend_up=True, ema20=2000.0)).setup_forming is False


class TestActionable:
    def test_pullback_then_confirmation_is_actionable_long(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(10, 2010.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2005.0, 2005.5, 1995.0, 1998.0))  # pulled below ema20=2000
        bars.append(bar(bars[-1]["ts_close"] + 900, 1998.0, 2003.0, 1997.0, 2002.0))  # confirms back above
        result = ev.evaluate(make_context(bars, h4_trend_up=True, ema20=2000.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.risk_R == 2.0

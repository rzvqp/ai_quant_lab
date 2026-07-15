"""Unit tests for S14 -- Momentum Exhaustion: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s14_momentum_exhaustion import S14MomentumExhaustion

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S14_momentum_exhaustion" / "strategy.json"


def make_evaluator() -> S14MomentumExhaustion:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S14MomentumExhaustion("S14", contract, frozenset({"XAUUSD"}))


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
    def test_no_acceleration_is_no_setup(self) -> None:
        ev = make_evaluator()
        closes = [2000.0, 2000.5, 2001.0, 2001.2, 2001.3, 2001.4]
        assert ev.evaluate(make_context(closes)).setup_forming is False


class TestActionable:
    def test_acceleration_then_stall_is_actionable_short_with_time_stop(self) -> None:
        ev = make_evaluator()
        # 3-bar ROC sequence: roc(t-2)=0.01, roc(t-1)=0.02 (still accelerating, not stalling yet),
        # roc(t)=0.012 (stalls relative to t-1) -- a fresh stall onset, not present on the prior bar.
        closes = [1990.0, 1995.0, 2000.0, 2010.0, 2020.0, 2020.0, 2050.2, 2044.24]
        result = ev.evaluate(make_context(closes, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"
        assert result.target is None
        assert ev.time_stop_bars == 24

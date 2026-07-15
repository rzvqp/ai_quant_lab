"""Unit tests for S42 -- Short-Term Return Reversal: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s42_short_term_return_reversal import S42ShortTermReturnReversal

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S42_short_term_return_reversal" / "strategy.json"


def make_evaluator() -> S42ShortTermReturnReversal:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S42ShortTermReturnReversal("S42", contract, frozenset({"XAUUSD"}))


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
    def test_small_move_is_no_setup(self) -> None:
        ev = make_evaluator()
        closes = [2000.0 + i * 0.1 for i in range(8)]
        assert ev.evaluate(make_context(closes)).setup_forming is False


class TestActionable:
    def test_fresh_overreaction_up_is_actionable_short(self) -> None:
        ev = make_evaluator()
        # 6-bar return at t: 2040.5/2000-1=0.02025 > 0.012 threshold; at t-1: 2010/1995-1=0.0075, not yet over.
        closes = [1990.0, 1995.0, 2000.0, 2005.0, 2015.0, 2025.0, 2010.0, 2040.5]
        result = ev.evaluate(make_context(closes, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"
        assert result.risk_R == 2.0

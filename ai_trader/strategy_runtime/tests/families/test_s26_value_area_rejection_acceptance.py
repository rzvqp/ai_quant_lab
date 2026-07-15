"""Unit tests for S26 -- Value-Area Rejection / Acceptance: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s26_value_area_rejection_acceptance import (
    S26ValueAreaRejectionAcceptance,
)

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S26_value_area_rejection_acceptance" / "strategy.json"


def make_evaluator() -> S26ValueAreaRejectionAcceptance:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S26ValueAreaRejectionAcceptance("S26", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], vwap: float = 2000.0, std: float = 5.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"vwap": vwap, "m_std": std, "m_atr": atr}, "bars": bars}},
    }


class TestNoSetup:
    def test_no_excursion_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2000.0, 2001.0, 1999.0, 2000.0), bar(1900, 2000.0, 2001.0, 1999.0, 2000.0)]
        assert ev.evaluate(make_context(bars, vwap=2000.0, std=5.0)).setup_forming is False

    def test_already_rejecting_before_this_bar_is_no_setup(self) -> None:
        ev = make_evaluator()
        # value area lo = 2000-2*5=1990; both bars wick below and close back inside.
        rejects = bar(1000, 1991.0, 1992.0, 1985.0, 1992.0)
        assert ev.evaluate(make_context([rejects, rejects], vwap=2000.0, std=5.0)).setup_forming is False


class TestActionable:
    def test_fresh_lower_edge_rejection_is_actionable_long(self) -> None:
        ev = make_evaluator()
        flat = bar(1000, 2000.0, 2000.5, 1999.5, 2000.0)
        reject = bar(1900, 1991.0, 1992.0, 1985.0, 1992.0)  # wicks below va_lo=1990, closes back above
        result = ev.evaluate(make_context([flat, reject], vwap=2000.0, std=5.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.target == 2000.0  # reverts to vwap
        assert result.risk_R is None

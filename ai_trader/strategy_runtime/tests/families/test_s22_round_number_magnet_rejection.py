"""Unit tests for S22 -- Round-Number Magnet / Rejection: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s22_round_number_magnet_rejection import S22RoundNumberMagnetRejection

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S22_round_number_magnet_rejection" / "strategy.json"


def make_evaluator() -> S22RoundNumberMagnetRejection:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S22RoundNumberMagnetRejection("S22", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"m_atr": atr}, "bars": bars}},
    }


class TestNoSetup:
    def test_no_band_change_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 1990.0, 1990.5, 1989.5, 1990.2), bar(1900, 1990.2, 1990.7, 1989.7, 1990.5)]  # both floor(x/100)==19
        assert ev.evaluate(make_context(bars)).setup_forming is False

    def test_missing_atr_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 1995.0, 1995.5, 1994.5, 1995.2), bar(1900, 1995.2, 2005.7, 1995.0, 2005.5)]
        assert ev.evaluate(make_context(bars, atr=None)).setup_forming is False


class TestActionable:
    def test_upward_band_cross_is_actionable_long(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 1995.0, 1995.5, 1994.5, 1995.2), bar(1900, 1995.2, 2005.7, 1995.0, 2005.5)]  # floor 19 -> 20
        result = ev.evaluate(make_context(bars, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 2005.5
        assert result.risk_R == 3.0

    def test_downward_band_cross_is_actionable_short(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2005.0, 2005.5, 2004.5, 2005.2), bar(1900, 2005.2, 2005.7, 1994.0, 1995.5)]  # floor 20 -> 19
        result = ev.evaluate(make_context(bars, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"
        assert result.entry == 1995.5

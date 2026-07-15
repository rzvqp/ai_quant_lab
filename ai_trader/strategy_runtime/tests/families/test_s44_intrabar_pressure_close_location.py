"""Unit tests for S44 -- Intrabar Pressure / Close-Location: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s44_intrabar_pressure_close_location import (
    S44IntrabarPressureCloseLocation,
)

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S44_intrabar_pressure_close_location" / "strategy.json"


def make_evaluator() -> S44IntrabarPressureCloseLocation:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S44IntrabarPressureCloseLocation("S44", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"m_atr": atr}, "bars": bars}},
    }


def strong_buy_bar(ts: int) -> dict:  # type: ignore[type-arg]
    # CLV=((C-L)-(H-C))/(H-L): close near the high -> CLV close to +1.
    return bar(ts, 2000.0, 2001.0, 2000.0, 2000.95)


def flat_bar(ts: int) -> dict:  # type: ignore[type-arg]
    return bar(ts, 2000.0, 2000.6, 1999.4, 2000.0)  # CLV == 0


class TestNoSetup:
    def test_no_pressure_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [flat_bar(1000 + i * 900) for i in range(4)]
        assert ev.evaluate(make_context(bars)).setup_forming is False

    def test_already_in_pressure_before_this_bar_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [strong_buy_bar(1000 + i * 900) for i in range(4)]  # pressure the whole window
        assert ev.evaluate(make_context(bars)).setup_forming is False


class TestActionable:
    def test_fresh_buy_pressure_onset_is_actionable_long(self) -> None:
        ev = make_evaluator()
        # 3 flat bars then 2 strong-buy bars: mclv_now (last 3: flat,buy,buy)=0.6 crosses the
        # threshold; mclv_before (flat,flat,buy)=0.3 does not -- a genuine fresh onset.
        bars = [flat_bar(1000 + i * 900) for i in range(3)] + [strong_buy_bar(1000 + i * 900) for i in range(3, 5)]
        result = ev.evaluate(make_context(bars, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.risk_R == 2.0

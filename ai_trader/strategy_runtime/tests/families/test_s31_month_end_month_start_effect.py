"""Unit tests for S31 -- Month-End / Month-Start Effect: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s31_month_end_month_start_effect import S31MonthEndMonthStartEffect

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S31_month_end_month_start_effect" / "strategy.json"

JAN31_LAST_BAR = int(datetime(2024, 1, 31, 23, 45, tzinfo=UTC).timestamp())
FEB1_FIRST_BAR = int(datetime(2024, 2, 1, 0, 0, tzinfo=UTC).timestamp())
FEB1_SECOND_BAR = int(datetime(2024, 2, 1, 0, 15, tzinfo=UTC).timestamp())
FEB3_FIRST_BAR = int(datetime(2024, 2, 3, 0, 0, tzinfo=UTC).timestamp())
FEB2_LAST_BAR = int(datetime(2024, 2, 2, 23, 45, tzinfo=UTC).timestamp())


def make_evaluator() -> S31MonthEndMonthStartEffect:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S31MonthEndMonthStartEffect("S31", contract, frozenset({"XAUUSD"}))


def bar(ts_open: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts_open, "ts_close": ts_open + 900, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"m_atr": atr}, "bars": bars}},
    }


class TestNoSetup:
    def test_second_bar_of_month_start_day_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(FEB1_FIRST_BAR, 2000.0, 2000.5, 1999.5, 2000.2), bar(FEB1_SECOND_BAR, 2000.2, 2000.7, 1999.7, 2000.4)]
        assert ev.evaluate(make_context(bars)).setup_forming is False

    def test_first_bar_of_day_outside_window_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(FEB2_LAST_BAR, 1998.0, 1998.5, 1997.5, 1998.2), bar(FEB3_FIRST_BAR, 2000.0, 2000.5, 1999.5, 2000.2)]
        assert ev.evaluate(make_context(bars)).setup_forming is False


class TestActionable:
    def test_first_bar_of_month_start_day_is_actionable_short(self) -> None:
        ev = make_evaluator()
        bars = [bar(JAN31_LAST_BAR, 1998.0, 1998.5, 1997.5, 1998.2), bar(FEB1_FIRST_BAR, 2000.0, 2000.5, 1999.5, 2000.2)]
        result = ev.evaluate(make_context(bars, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"
        assert result.entry == 2000.2
        assert result.stop is not None and result.stop > result.entry
        assert result.target is not None and result.target < result.entry
        assert result.risk_R == 3.0

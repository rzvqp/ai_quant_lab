"""Unit tests for S29 -- Day-of-Week Effect: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s29_day_of_week_effect import S29DayOfWeekEffect

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S29_day_of_week_effect" / "strategy.json"

# 2024-01-04 is a Thursday (weekday()==3); 2024-01-03 is a Wednesday.
WED_LAST_BAR = int(datetime(2024, 1, 3, 23, 45, tzinfo=UTC).timestamp())
THU_FIRST_BAR = int(datetime(2024, 1, 4, 0, 0, tzinfo=UTC).timestamp())
THU_SECOND_BAR = int(datetime(2024, 1, 4, 0, 15, tzinfo=UTC).timestamp())


def make_evaluator() -> S29DayOfWeekEffect:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S29DayOfWeekEffect("S29", contract, frozenset({"XAUUSD"}))


def bar(ts_open: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts_open, "ts_close": ts_open + 900, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"m_atr": atr}, "bars": bars}},
    }


class TestNoSetup:
    def test_second_bar_of_thursday_is_no_setup(self) -> None:
        """Only the FIRST bar of the target weekday qualifies."""
        ev = make_evaluator()
        bars = [bar(THU_FIRST_BAR, 2000.0, 2000.5, 1999.5, 2000.2), bar(THU_SECOND_BAR, 2000.2, 2000.7, 1999.7, 2000.4)]
        assert ev.evaluate(make_context(bars)).setup_forming is False

    def test_first_bar_of_a_different_weekday_is_no_setup(self) -> None:
        ev = make_evaluator()
        wed_bar = int(datetime(2024, 1, 3, 0, 0, tzinfo=UTC).timestamp())
        bars = [bar(wed_bar - 86400, 1998.0, 1998.5, 1997.5, 1998.2), bar(wed_bar, 2000.0, 2000.5, 1999.5, 2000.2)]
        assert ev.evaluate(make_context(bars)).setup_forming is False


class TestActionable:
    def test_first_bar_of_target_weekday_is_actionable(self) -> None:
        ev = make_evaluator()
        bars = [bar(WED_LAST_BAR, 1998.0, 1998.5, 1997.5, 1998.2), bar(THU_FIRST_BAR, 2000.0, 2000.5, 1999.5, 2000.2)]
        result = ev.evaluate(make_context(bars, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 2000.2
        assert result.target is not None and result.target > result.entry
        assert result.risk_R == 2.0

"""Unit tests for S18 -- Time-of-Day Edge: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s18_time_of_day_edge import S18TimeOfDayEdge

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S18_time_of_day_edge" / "strategy.json"

MIDNIGHT_UTC = int(datetime(2024, 1, 4, 0, 0, tzinfo=UTC).timestamp())
QUARTER_PAST_UTC = int(datetime(2024, 1, 4, 0, 15, tzinfo=UTC).timestamp())


def make_evaluator() -> S18TimeOfDayEdge:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S18TimeOfDayEdge("S18", contract, frozenset({"XAUUSD"}))


def bar(ts_open: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts_open, "ts_close": ts_open + 900, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"m_atr": atr}, "bars": bars}},
    }


class TestNoSetup:
    def test_not_the_target_hour_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(QUARTER_PAST_UTC, 2000.0, 2000.5, 1999.5, 2000.2)]
        assert ev.evaluate(make_context(bars)).setup_forming is False

    def test_missing_atr_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(MIDNIGHT_UTC, 2000.0, 2000.5, 1999.5, 2000.2)]
        assert ev.evaluate(make_context(bars, atr=None)).setup_forming is False


class TestActionable:
    def test_bar_opening_exactly_at_target_hour_is_actionable_with_time_stop(self) -> None:
        ev = make_evaluator()
        bars = [bar(MIDNIGHT_UTC, 2000.0, 2000.5, 1999.5, 2000.2)]
        result = ev.evaluate(make_context(bars, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 2000.2
        assert result.stop is not None and result.stop < result.entry
        assert result.target is None
        assert ev.time_stop_bars == 24

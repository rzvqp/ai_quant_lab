"""Unit tests for S30 -- Kill-Zone Time-Window: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s30_kill_zone_time_window import S30KillZoneTimeWindow

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S30_kill_zone_time_window" / "strategy.json"

KZ_TS = int(datetime(2024, 1, 4, 13, 0, tzinfo=UTC).timestamp())  # inside NY kill-zone (12-15 UTC)
OUTSIDE_KZ_TS = int(datetime(2024, 1, 4, 18, 0, tzinfo=UTC).timestamp())


def make_evaluator() -> S30KillZoneTimeWindow:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S30KillZoneTimeWindow("S30", contract, frozenset({"XAUUSD"}))


def bar(ts_open: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts_open, "ts_close": ts_open + 900, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"m_atr": atr}, "bars": bars}},
    }


def prior_flat_bars(n: int, price: float, start_ts: int) -> list[dict]:  # type: ignore[type-arg]
    return [bar(start_ts - (n - i) * 900, price, price + 0.2, price - 0.2, price) for i in range(n)]


class TestNoSetup:
    def test_outside_kill_zone_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = prior_flat_bars(4, 2000.0, OUTSIDE_KZ_TS) + [bar(OUTSIDE_KZ_TS, 2000.0, 2010.0, 1999.0, 2009.0)]
        assert ev.evaluate(make_context(bars)).setup_forming is False

    def test_inside_kill_zone_no_range_break_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = prior_flat_bars(4, 2000.0, KZ_TS) + [bar(KZ_TS, 2000.0, 2000.1, 1999.9, 2000.0)]
        assert ev.evaluate(make_context(bars)).setup_forming is False


class TestActionable:
    def test_upward_range_break_inside_kill_zone_is_actionable_long(self) -> None:
        ev = make_evaluator()
        bars = prior_flat_bars(4, 2000.0, KZ_TS) + [bar(KZ_TS, 2000.0, 2010.0, 1999.0, 2009.0)]  # closes above prior 4-bar high
        result = ev.evaluate(make_context(bars, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 2009.0
        assert result.target is not None and result.target > result.entry
        assert result.risk_R == 2.0

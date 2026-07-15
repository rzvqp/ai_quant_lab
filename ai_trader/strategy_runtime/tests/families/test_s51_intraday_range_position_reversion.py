"""Unit tests for S51 -- Intraday Range-Position Reversion: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s51_intraday_range_position_reversion import (
    S51IntradayRangePositionReversion,
)

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S51_intraday_range_position_reversion" / "strategy.json"


def make_evaluator() -> S51IntradayRangePositionReversion:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S51IntradayRangePositionReversion("S51", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], bar_in_sess: int = 10, sess_high: float = 2020.0, sess_low: float = 1980.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {
            "features": {"bar_in_sess": bar_in_sess, "sess_high": sess_high, "sess_low": sess_low, "m_atr": atr},
            "bars": bars,
        }},
    }


class TestNoSetup:
    def test_range_not_formed_yet_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2000.0, 2000.5, 1999.5, 2019.0), bar(1900, 2019.0, 2019.5, 2018.5, 2019.0)]
        assert ev.evaluate(make_context(bars, bar_in_sess=3, sess_high=2020.0, sess_low=1980.0)).setup_forming is False

    def test_mid_range_is_no_setup(self) -> None:
        ev = make_evaluator()
        mid = bar(1000, 2000.0, 2000.5, 1999.5, 2000.0)
        assert ev.evaluate(make_context([mid, mid], sess_high=2020.0, sess_low=1980.0)).setup_forming is False


class TestActionable:
    def test_fresh_near_bottom_position_is_actionable_long(self) -> None:
        ev = make_evaluator()
        mid = bar(1000, 2000.0, 2000.5, 1999.5, 2000.0)
        near_bottom = bar(1900, 2000.0, 2000.5, 1981.0, 1983.0)  # position=(1983-1980)/40=0.075 <= 0.15
        result = ev.evaluate(make_context([mid, near_bottom], bar_in_sess=10, sess_high=2020.0, sess_low=1980.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.risk_R == 2.0

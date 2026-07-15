"""Unit tests for S11 -- Structure-Break Reversal (CHoCH): hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s11_structure_break_reversal_choch import S11StructureBreakReversalChoch

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S11_structure_break_reversal_choch" / "strategy.json"


def make_evaluator() -> S11StructureBreakReversalChoch:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S11StructureBreakReversalChoch("S11", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(
    bars: list[dict], h4_trend_up: bool | None, rmax20: float = 2020.0, rmin20: float = 1980.0,  # type: ignore[type-arg]
    atr: float | None = 2.0,
) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {
            "features": {"h4_trend_up": h4_trend_up, "rmax20": rmax20, "rmin20": rmin20, "m_atr": atr},
            "bars": bars,
        }},
    }


def flat_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


class TestNoSetup:
    def test_uptrend_but_no_break_below_rmin20_is_no_setup(self) -> None:
        ev = make_evaluator()
        ctx = make_context(flat_bars(3, 2000.0), h4_trend_up=True, rmin20=1980.0)
        assert ev.evaluate(ctx).setup_forming is False

    def test_already_broken_before_this_bar_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, 1970.0)  # every bar already below rmin20=1980
        ctx = make_context(bars, h4_trend_up=True, rmin20=1980.0)
        assert ev.evaluate(ctx).setup_forming is False


class TestActionable:
    def test_h4_uptrend_fresh_break_below_rmin20_is_actionable_short(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, 2000.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2000.0, 2000.5, 1970.0, 1975.0))  # fresh close below rmin20
        ctx = make_context(bars, h4_trend_up=True, rmin20=1980.0, atr=2.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"
        assert result.entry == 1975.0
        assert result.risk_R == 2.0

    def test_h4_downtrend_fresh_break_above_rmax20_is_actionable_long(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, 2000.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2000.0, 2030.0, 1999.5, 2025.0))  # fresh close above rmax20
        ctx = make_context(bars, h4_trend_up=False, rmax20=2020.0, atr=2.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 2025.0

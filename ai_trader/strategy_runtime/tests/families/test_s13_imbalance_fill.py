"""Unit tests for S13 -- Imbalance Fill: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s13_imbalance_fill import S13ImbalanceFill

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S13_imbalance_fill" / "strategy.json"


def make_evaluator() -> S13ImbalanceFill:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S13ImbalanceFill("S13", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], fvg_bull: bool | None, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"fvg_bull": fvg_bull, "m_atr": atr}, "bars": bars}},
    }


def flat_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


class TestNoSetup:
    def test_no_fvg_is_no_setup(self) -> None:
        ev = make_evaluator()
        assert ev.evaluate(make_context(flat_bars(3, 2000.0), fvg_bull=False)).setup_forming is False

    def test_missing_flag_is_no_setup(self) -> None:
        ev = make_evaluator()
        assert ev.evaluate(make_context(flat_bars(3, 2000.0), fvg_bull=None)).setup_forming is False


class TestActionable:
    def test_bullish_fvg_is_actionable_long_with_time_stop(self) -> None:
        ev = make_evaluator()
        result = ev.evaluate(make_context(flat_bars(3, 2000.0), fvg_bull=True, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.stop is not None and result.stop < result.entry  # type: ignore[operator]
        assert result.target is None
        assert ev.time_stop_bars == 24

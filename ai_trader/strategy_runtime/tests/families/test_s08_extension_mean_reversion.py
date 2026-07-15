"""Unit tests for S8 -- Extension Mean-Reversion: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s08_extension_mean_reversion import S08ExtensionMeanReversion

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S08_extension_mean_reversion" / "strategy.json"


def make_evaluator() -> S08ExtensionMeanReversion:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S08ExtensionMeanReversion("S8", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], vwap: float = 2000.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"vwap": vwap, "m_atr": atr}, "bars": bars}},
    }


class TestNoSetup:
    def test_no_extension_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2000.0, 2000.5, 1999.5, 1999.0), bar(1900, 1999.0, 1999.5, 1998.5, 1998.5)]
        assert ev.evaluate(make_context(bars, vwap=2000.0, atr=2.0)).setup_forming is False

    def test_already_extended_before_this_bar_is_no_setup(self) -> None:
        ev = make_evaluator()
        far = bar(1000, 1993.0, 1993.5, 1992.5, 1993.0)  # vwap-close=7 > 3*atr=6
        assert ev.evaluate(make_context([far, far], vwap=2000.0, atr=2.0)).setup_forming is False


class TestActionable:
    def test_fresh_extension_below_vwap_is_actionable_long(self) -> None:
        ev = make_evaluator()
        near = bar(1000, 1998.0, 1998.5, 1997.5, 1998.0)
        far = bar(1900, 1998.0, 1998.5, 1992.0, 1993.0)  # vwap-close=7 > 3*atr=6, fresh
        result = ev.evaluate(make_context([near, far], vwap=2000.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.risk_R == 2.0

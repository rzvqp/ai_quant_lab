"""Unit tests for S40 -- Regime Router: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s40_regime_router import S40RegimeRouter

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S40_regime_router" / "strategy.json"


def make_evaluator() -> S40RegimeRouter:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S40RegimeRouter("S40", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], m_trend_up: bool | None = True, rmax20: float = 2100.0, rmin20: float = 1900.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {
            "features": {"m_trend_up": m_trend_up, "rmax20": rmax20, "rmin20": rmin20, "m_atr": atr},
            "bars": bars,
        }},
    }


class TestActionable:
    def test_efficient_uptrend_expansion_routes_to_trend_continuation_long(self) -> None:
        ev = make_evaluator()
        bars = []
        price = 2000.0
        for i in range(21):
            price += 1.0
            bars.append(bar(1000 + i * 900, price - 1.0, price, price - 1.05, price))
        last_close = bars[-1]["close"]
        bars.append(bar(bars[-1]["ts_close"] + 900, last_close, last_close + 5.0, last_close - 0.5, last_close + 4.5))
        result = ev.evaluate(make_context(bars, m_trend_up=True, rmax20=2100.0, rmin20=1900.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.regime == "TREND_UP"

    def test_choppy_range_dip_below_low_routes_to_range_fade_long(self) -> None:
        ev = make_evaluator()
        bars = []
        # 21 bars alternating 2000/2001 (net move over the 20-bar ER window stays tiny), then a
        # SMALL dip (3 points) below rmin20 -- keeps the Kaufman efficiency ratio well below 0.5
        # (net~2 / sum-of-moves~20 = 0.1), a genuine range regime, unlike a dominant directional move.
        for i in range(21):
            price = 2001.0 if i % 2 == 1 else 2000.0
            bars.append(bar(1000 + i * 900, price, price + 0.2, price - 0.2, price))
        dip = bar(bars[-1]["ts_close"] + 900, 2000.0, 2000.5, 1997.0, 1999.0)  # low<rmin20=1998, close back above
        bars.append(dip)
        result = ev.evaluate(make_context(bars, m_trend_up=True, rmax20=2100.0, rmin20=1998.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.regime == "RANGE"

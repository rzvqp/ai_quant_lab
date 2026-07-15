"""Unit tests for S10 -- Displacement Continuation: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s10_displacement_continuation import S10DisplacementContinuation

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S10_displacement_continuation" / "strategy.json"


def make_evaluator() -> S10DisplacementContinuation:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S10DisplacementContinuation("S10", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"m_atr": atr}, "bars": bars}},
    }


def flat_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


class TestNoSetup:
    def test_no_displacement_is_no_setup(self) -> None:
        ev = make_evaluator()
        assert ev.evaluate(make_context(flat_bars(10, 2000.0))).setup_forming is False

    def test_displacement_without_pullback_yet_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(10, 2010.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2010.0, 2011.0, 2001.0, 2002.0))  # bearish displacement, range=10>1.5*2=3
        assert ev.evaluate(make_context(bars)).setup_forming is False


class TestActionable:
    def test_displacement_then_pullback_touch_is_actionable_short_with_trailing(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(10, 2010.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2010.0, 2011.0, 2001.0, 2002.0))  # bearish displacement, close=2002
        bars.append(bar(bars[-1]["ts_close"] + 900, 1999.0, 1999.5, 1997.0, 1998.5))  # not yet a pullback touch (high < 2002)
        bars.append(bar(bars[-1]["ts_close"] + 900, 1998.5, 2003.0, 1998.0, 2001.0))  # pulls back up to touch 2002
        result = ev.evaluate(make_context(bars, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"
        assert result.target is None
        assert ev.trailing_stop_atr_mult == 1.5

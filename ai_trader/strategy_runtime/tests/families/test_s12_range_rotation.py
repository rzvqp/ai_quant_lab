"""Unit tests for S12 -- Range Rotation: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s12_range_rotation import S12RangeRotation

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S12_range_rotation" / "strategy.json"


def make_evaluator() -> S12RangeRotation:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S12RangeRotation("S12", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], rmax20: float = 2020.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"rmax20": rmax20, "m_atr": atr}, "bars": bars}},
    }


def flat_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


class TestNoSetup:
    def test_far_from_extreme_is_no_setup(self) -> None:
        ev = make_evaluator()
        ctx = make_context(flat_bars(3, 2000.0), rmax20=2020.0)
        assert ev.evaluate(ctx).setup_forming is False

    def test_already_touching_before_this_bar_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, 2019.9)  # already within 0.1% of rmax20=2020 the whole time
        ctx = make_context(bars, rmax20=2020.0)
        assert ev.evaluate(ctx).setup_forming is False


class TestActionable:
    def test_fresh_touch_of_rolling_high_is_actionable_short_at_rr15(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, 2000.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2000.0, 2019.95, 1999.0, 2010.0))  # touches within 0.1% of 2020
        ctx = make_context(bars, rmax20=2020.0, atr=2.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"
        assert result.entry == 2010.0
        assert result.risk_R == 1.5
        # rr=1.5 (target=='center' override), NOT the literal executable_default exit=rr2 value.
        risk_distance = abs(result.stop - result.entry)  # type: ignore[operator]
        assert abs(abs(result.target - result.entry) - 1.5 * risk_distance) < 1e-9  # type: ignore[operator]

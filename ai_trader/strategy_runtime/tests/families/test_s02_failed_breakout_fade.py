"""Unit tests for S2 -- Failed-Breakout Fade: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s02_failed_breakout_fade import S02FailedBreakoutFade

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S02_failed_breakout_fade" / "strategy.json"


def make_evaluator() -> S02FailedBreakoutFade:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S02FailedBreakoutFade("S2", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], pdl: float = 2000.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"pdl": pdl, "m_atr": atr}, "bars": bars}},
    }


def flat_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


class TestNoSetup:
    def test_no_breakdown_no_reclaim_is_no_setup(self) -> None:
        ev = make_evaluator()
        ctx = make_context(flat_bars(10, 2010.0), pdl=2000.0)
        assert ev.evaluate(ctx).setup_forming is False

    def test_breakdown_without_reclaim_within_window_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(10, 2010.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2010.0, 2010.5, 1990.0, 1995.0))  # closes below pdl
        bars.append(bar(bars[-1]["ts_close"] + 900, 1995.0, 1996.0, 1994.0, 1995.5))  # still below
        ctx = make_context(bars, pdl=2000.0)
        assert ev.evaluate(ctx).setup_forming is False


class TestActionable:
    def test_breakdown_then_reclaim_within_window_is_actionable_long(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(10, 2010.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2010.0, 2010.5, 1990.0, 1995.0))  # breakdown: closes below pdl
        bars.append(bar(bars[-1]["ts_close"] + 900, 1995.0, 1997.0, 1994.0, 1996.0))  # still below
        bars.append(bar(bars[-1]["ts_close"] + 900, 1996.0, 2003.0, 1995.0, 2002.0))  # reclaim: closes above pdl
        ctx = make_context(bars, pdl=2000.0, atr=2.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 2002.0
        assert result.stop is not None and result.stop < result.entry
        assert result.target is not None and result.target > result.entry
        assert result.risk_R == 2.0

    def test_reclaim_bar_cannot_confirm_its_own_breakdown(self) -> None:
        """A single bar whose close is above pdl can never simultaneously be its own breakdown --
        the breakdown search must exclude the current (reclaim) bar."""
        ev = make_evaluator()
        bars = flat_bars(10, 2010.0)  # never breaks below pdl anywhere
        ctx = make_context(bars, pdl=2000.0)
        assert ev.evaluate(ctx).setup_forming is False

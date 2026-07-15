"""Unit tests for S3 -- Breakout Retest Continuation: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s03_breakout_retest_continuation import (
    S03BreakoutRetestContinuation,
)

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S03_breakout_retest_continuation" / "strategy.json"


def make_evaluator() -> S03BreakoutRetestContinuation:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S03BreakoutRetestContinuation("S3", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], level: float = 2000.0, atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"rmax50": level, "m_atr": atr}, "bars": bars}},
    }


def flat_bars(n: int, price: float) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


class TestNoSetup:
    def test_no_breakout_no_retest_is_no_setup(self) -> None:
        ev = make_evaluator()
        assert ev.evaluate(make_context(flat_bars(10, 1990.0), level=2000.0)).setup_forming is False

    def test_breakout_without_retest_yet_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(10, 1990.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2005.0, 2006.0, 2004.0, 2005.0))  # breakout, no retest yet
        assert ev.evaluate(make_context(bars, level=2000.0)).setup_forming is False

    def test_second_retest_after_first_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(5, 1990.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2005.0, 2006.0, 2004.0, 2005.0))  # breakout
        bars.append(bar(bars[-1]["ts_close"] + 900, 2005.0, 2005.5, 1999.0, 2004.0))  # first retest touch
        bars.append(bar(bars[-1]["ts_close"] + 900, 2004.0, 2004.5, 1998.5, 2003.0))  # second retest touch -- stale
        assert ev.evaluate(make_context(bars, level=2000.0)).setup_forming is False


class TestActionable:
    def test_breakout_then_first_retest_is_actionable_long(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(7, 1990.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 2005.0, 2006.0, 2004.0, 2005.0))  # breakout
        bars.append(bar(bars[-1]["ts_close"] + 900, 2004.0, 2004.5, 2001.0, 2003.0))  # holds above, no retest
        bars.append(bar(bars[-1]["ts_close"] + 900, 2003.0, 2003.5, 1999.0, 2002.0))  # first retest touch
        result = ev.evaluate(make_context(bars, level=2000.0, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 2002.0
        assert result.risk_R == 3.0

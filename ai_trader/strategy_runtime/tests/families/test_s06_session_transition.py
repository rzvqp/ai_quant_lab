"""Unit tests for S6 -- Session-Transition: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s06_session_transition import S06SessionTransition

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S06_session_transition" / "strategy.json"


def make_evaluator() -> S06SessionTransition:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S06SessionTransition("S6", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(
    bars: list[dict], session: str = "ny", bar_in_sess: int = 2,  # type: ignore[type-arg]
    prev_sess_high: float | None = 2010.0, atr: float | None = 2.0,
) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {
            "features": {"session": session, "bar_in_sess": bar_in_sess, "prev_sess_high": prev_sess_high, "m_atr": atr},
            "bars": bars,
        }},
    }


def flat_bars(n: int, price: float = 2000.0) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


class TestNoSetup:
    def test_wrong_session_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, price=2020.0)
        ctx = make_context(bars, session="london")
        assert ev.evaluate(ctx).setup_forming is False

    def test_late_in_session_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, price=2020.0)
        ctx = make_context(bars, bar_in_sess=15)
        assert ev.evaluate(ctx).setup_forming is False

    def test_close_below_prev_sess_high_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, price=2000.0)
        ctx = make_context(bars, prev_sess_high=2010.0)
        assert ev.evaluate(ctx).setup_forming is False

    def test_missing_prev_sess_high_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, price=2020.0)
        ctx = make_context(bars, prev_sess_high=None)
        assert ev.evaluate(ctx).setup_forming is False


class TestActionable:
    def test_ny_breakout_above_prev_session_high_is_actionable(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(3, price=2015.0)
        ctx = make_context(bars, session="ny", bar_in_sess=2, prev_sess_high=2010.0, atr=2.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.entry == 2015.0
        assert result.stop is not None and result.stop < result.entry
        assert result.target is not None and result.target > result.entry
        assert result.risk_R == 2.0

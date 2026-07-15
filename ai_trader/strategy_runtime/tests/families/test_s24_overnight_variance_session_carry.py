"""Unit tests for S24 -- Overnight Variance / Session Carry: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s24_overnight_variance_session_carry import S24OvernightVarianceSessionCarry

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S24_overnight_variance_session_carry" / "strategy.json"


def make_evaluator() -> S24OvernightVarianceSessionCarry:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S24OvernightVarianceSessionCarry("S24", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(
    bars: list[dict], session: str = "ny", bar_in_sess: int = 1,  # type: ignore[type-arg]
    prev_sess_high: float = 2010.0, prev_sess_low: float = 1990.0, prev_sess_close: float = 1995.0,
    atr: float | None = 2.0,
) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {
            "features": {
                "session": session, "bar_in_sess": bar_in_sess, "prev_sess_high": prev_sess_high,
                "prev_sess_low": prev_sess_low, "prev_sess_close": prev_sess_close, "m_atr": atr,
            },
            "bars": bars,
        }},
    }


class TestNoSetup:
    def test_wrong_bar_index_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2000.0, 2000.5, 1999.5, 2000.2)]
        assert ev.evaluate(make_context(bars, bar_in_sess=0)).setup_forming is False

    def test_wrong_session_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2000.0, 2000.5, 1999.5, 2000.2)]
        assert ev.evaluate(make_context(bars, session="london")).setup_forming is False


class TestActionable:
    def test_prior_session_closed_lower_half_fades_long(self) -> None:
        """mode=fade: prior session closed in the LOWER half of its range (bias_up=False) -> fade
        means trade LONG (against the bearish-close bias)."""
        ev = make_evaluator()
        bars = [bar(1000, 2000.0, 2000.5, 1999.5, 2000.2)]
        ctx = make_context(bars, prev_sess_high=2010.0, prev_sess_low=1990.0, prev_sess_close=1992.0)  # closed near the low
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.target is None
        assert ev.time_stop_bars == 24

    def test_prior_session_closed_upper_half_fades_short(self) -> None:
        ev = make_evaluator()
        bars = [bar(1000, 2000.0, 2000.5, 1999.5, 2000.2)]
        ctx = make_context(bars, prev_sess_high=2010.0, prev_sess_low=1990.0, prev_sess_close=2008.0)  # closed near the high
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "SHORT"

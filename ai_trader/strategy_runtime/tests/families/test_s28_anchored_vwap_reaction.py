"""Unit tests for S28 -- Anchored-VWAP Reaction: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s28_anchored_vwap_reaction import S28AnchoredVwapReaction

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S28_anchored_vwap_reaction" / "strategy.json"

# A Tuesday mid-week base timestamp -- comfortably far from any week boundary for this test's
# short (~110-bar, ~27h) window.
BASE_TS = 1_704_240_000


def make_evaluator() -> S28AnchoredVwapReaction:
    contract = parse_contract(json.loads(CONTRACT_PATH.read_text(encoding="utf-8")))
    return S28AnchoredVwapReaction("S28", contract, frozenset({"XAUUSD"}))


def bar(ts_open: int, o: float, h: float, l: float, c: float, vol: float = 1.0) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts_open, "ts_close": ts_open + 900, "open": o, "high": h, "low": l, "close": c, "volume": vol}


def make_context(bars: list[dict], atr: float | None = 2.0) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"m_atr": atr}, "bars": bars}},
    }


def _flat_history(n: int) -> list[dict]:  # type: ignore[type-arg]
    """n flat bars at typical price 2000 -- dominates the cumulative anchor toward ~2000."""
    return [bar(BASE_TS + i * 900, 2000.0, 2000.0, 2000.0, 2000.0) for i in range(n)]


class TestNoSetup:
    def test_no_departure_no_bounce_is_no_setup(self) -> None:
        ev = make_evaluator()
        bars = _flat_history(20)
        assert ev.evaluate(make_context(bars)).setup_forming is False

    def test_no_prior_departure_disqualifies_even_a_shaped_bounce(self) -> None:
        ev = make_evaluator()
        bars = _flat_history(19)
        last = bar(bars[-1]["ts_open"] + 900, 1999.0, 2005.0, 1999.5, 2003.0)  # shaped like a bounce
        bars.append(last)
        assert ev.evaluate(make_context(bars)).setup_forming is False


class TestActionable:
    def test_departure_then_bounce_onset_is_actionable(self) -> None:
        ev = make_evaluator()
        bars = _flat_history(100)
        # 7 more flat bars, then one genuine departure bar (>=0.75*ATR=1.5 away from the ~2000 anchor).
        idx = len(bars)
        bars += [bar(BASE_TS + (idx + i) * 900, 2000.0, 2000.0, 2000.0, 2000.0) for i in range(7)]
        idx = len(bars)
        bars.append(bar(BASE_TS + idx * 900, 1995.0, 1996.0, 1988.0, 1990.0))  # departure: close 1990, |1990-~2000|>=1.5
        idx = len(bars)
        bars.append(bar(BASE_TS + idx * 900, 1990.0, 1993.0, 1989.0, 1993.0))  # still below anchor, not a bounce itself
        idx = len(bars)
        bars.append(bar(BASE_TS + idx * 900, 1993.0, 2005.0, 1998.0, 2003.0))  # bounce: low touches anchor, closes above
        result = ev.evaluate(make_context(bars, atr=2.0))
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.direction == "LONG"
        assert result.stop is not None and result.stop < result.entry  # type: ignore[operator]
        assert result.target is None
        assert ev.time_stop_bars == 24

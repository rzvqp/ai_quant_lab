"""Unit tests for the S1 reference-slice evaluator: hand-constructed bar sequences, no live data."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.families.s01_confirmed_liquidity_sweep_reversal import (
    S01LiquiditySweepReversal,
)

S1_CONTRACT_PATH = Path(__file__).resolve().parents[4] / "knowledge" / "strategies" / "S01_confirmed_liquidity_sweep_reversal" / "strategy.json"


def make_evaluator() -> S01LiquiditySweepReversal:
    contract = parse_contract(json.loads(S1_CONTRACT_PATH.read_text(encoding="utf-8")))
    return S01LiquiditySweepReversal("S1", contract, frozenset({"XAUUSD"}))


def bar(ts: int, o: float, h: float, l: float, c: float) -> dict:  # type: ignore[type-arg]
    return {"ts_open": ts - 900, "ts_close": ts, "open": o, "high": h, "low": l, "close": c}


def make_context(bars: list[dict], pdl: float, atr: float | None = 2.0, as_of: int | None = None) -> dict:  # type: ignore[type-arg]
    return {
        "meta": {"as_of": as_of if as_of is not None else bars[-1]["ts_close"], "symbol": "XAUUSD"},
        "data_quality": {"level": "OK"},
        "timeframes": {"M15": {"features": {"pdl": pdl, "m_atr": atr}, "bars": bars}},
    }


def flat_bars(n: int, price: float = 100.0) -> list[dict]:  # type: ignore[type-arg]
    return [bar(1000 + i * 900, price, price + 0.1, price - 0.1, price) for i in range(n)]


class TestNoSetup:
    def test_insufficient_history_is_no_setup(self) -> None:
        ev = make_evaluator()
        ctx = make_context(flat_bars(3), pdl=100.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming is False

    def test_missing_pdl_is_no_setup(self) -> None:
        ev = make_evaluator()
        ctx = make_context(flat_bars(15), pdl=None)  # type: ignore[arg-type]
        result = ev.evaluate(ctx)
        assert result.setup_forming is False
        assert result.reason == "pdl unavailable"

    def test_no_sweep_in_window_is_no_setup(self) -> None:
        ev = make_evaluator()
        # PDL far below the whole price range -- never swept.
        ctx = make_context(flat_bars(15, price=200.0), pdl=100.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming is False


class TestWaiting:
    def test_sweep_without_confirmation_is_waiting(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(10, price=105.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 105.0, 105.2, 99.0, 104.8))  # sweeps pdl=100, closes above
        bars.append(bar(bars[-1]["ts_close"] + 900, 104.8, 105.0, 104.5, 103.0))  # bearish -- breaks the pair
        bars.append(bar(bars[-1]["ts_close"] + 900, 103.0, 103.5, 102.5, 103.2))  # bearish close -- no confirm yet
        ctx = make_context(bars, pdl=100.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming is True
        assert result.present is True
        assert result.confirmations_met is False
        assert result.direction == "LONG"


class TestActionable:
    def test_sweep_then_two_bullish_closes_confirms(self) -> None:
        ev = make_evaluator()
        bars = flat_bars(10, price=105.0)
        bars.append(bar(bars[-1]["ts_close"] + 900, 105.0, 105.2, 99.0, 104.8))  # sweep bar
        bars.append(bar(bars[-1]["ts_close"] + 900, 104.8, 106.0, 104.5, 105.5))  # bullish close 1
        bars.append(bar(bars[-1]["ts_close"] + 900, 105.5, 107.0, 105.3, 106.5))  # bullish close 2
        ctx = make_context(bars, pdl=100.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming is True
        assert result.present is True
        assert result.confirmations_met is True
        assert result.direction == "LONG"
        assert result.entry == 106.5
        assert result.stop is not None and result.stop < result.entry
        assert result.target is not None and result.target > result.entry
        assert result.risk_R == 2.0

    def test_regression_stop_never_above_entry_when_price_dips_after_sweep(self) -> None:
        """The exact bug a Checkpoint 1 end-to-end run caught: a sweep bar whose own low is HIGHER
        than a later, lower low reached before confirmation completes must never produce a stop above
        entry (the stop must clear the TRUE extreme of the whole sweep-to-confirmation sequence, not
        just the nominal sweep bar's own low)."""
        ev = make_evaluator()
        bars = flat_bars(10, price=110.0)
        # Sweep bar: dips just below pdl=100 and closes back above -- but only marginally.
        bars.append(bar(bars[-1]["ts_close"] + 900, 108.0, 108.5, 99.5, 100.3))
        # Price then makes a MUCH lower low before finally confirming -- the real-data scenario.
        bars.append(bar(bars[-1]["ts_close"] + 900, 100.3, 100.5, 90.0, 95.0))
        bars.append(bar(bars[-1]["ts_close"] + 900, 95.0, 96.0, 93.0, 94.0))
        bars.append(bar(bars[-1]["ts_close"] + 900, 94.0, 97.0, 93.5, 96.5))   # bullish close 1
        bars.append(bar(bars[-1]["ts_close"] + 900, 96.5, 99.0, 96.0, 98.5))   # bullish close 2
        ctx = make_context(bars, pdl=100.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming and result.present and result.confirmations_met
        assert result.stop < result.entry, (result.entry, result.stop)
        # the stop must clear the TRUE extreme (90.0), not the nominal sweep bar's own low (99.5).
        assert result.stop < 90.0

    def test_no_retrigger_search_window_respects_confirmation_bars_exclusion(self) -> None:
        """The two confirming bars themselves must never be treated as candidate sweep bars (a
        strategy cannot confirm its own sweep)."""
        ev = make_evaluator()
        bars = flat_bars(10, price=110.0)
        # No real sweep anywhere -- just two bullish closes in a row, both ABOVE pdl the whole time.
        bars.append(bar(bars[-1]["ts_close"] + 900, 110.0, 111.0, 109.5, 110.5))
        bars.append(bar(bars[-1]["ts_close"] + 900, 110.5, 112.0, 110.2, 111.5))
        ctx = make_context(bars, pdl=100.0)
        result = ev.evaluate(ctx)
        assert result.setup_forming is False  # no PDL sweep anywhere, confirmation pair is irrelevant

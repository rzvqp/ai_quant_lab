"""`RawAxesBuilder` tests -- real OHLC arrays through the real vendored detectors
(`structural_observer.vendor_bridge`), never a stubbed/mocked detector. Deliberately does not assert
exact numeric equality against the vendored detectors' internals (that is `structural_observer`'s own
test suite's job) -- these tests prove the GLUE: symbol validation, insufficient-history fail-closed
behavior, and that a clean, deterministic uptrend produces an UP-family reading, never a DOWN one."""

from __future__ import annotations

import pytest

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_bridge.tests.conftest import BOS_BULL_CONFIRMED_AT_INDEX, bos_bull_bars

_SYMBOL = "XAUUSD"


def _bar(i: int, *, open_: float, high: float, low: float, close: float) -> Bar:
    return Bar(symbol=_SYMBOL, ts_open=i * 900, ts_close=(i + 1) * 900, open=open_, high=high, low=low,
               close=close, volume=100.0)


def test_a_bar_for_a_different_symbol_is_rejected() -> None:
    builder = RawAxesBuilder(_SYMBOL)
    wrong_symbol_bar = Bar(symbol="EURUSD", ts_open=0, ts_close=900, open=1.0, high=1.1, low=0.9,
                            close=1.0, volume=None)
    with pytest.raises(ValueError, match="XAUUSD"):
        builder.observe(wrong_symbol_bar)


def test_insufficient_history_yields_uncertain_axes_not_a_fabricated_default() -> None:
    """A single bar cannot produce a confirmed swing/break (K_DEFAULT=2 needs 2 bars each side) --
    structure/direction must be honestly None, not a guessed value."""
    builder = RawAxesBuilder(_SYMBOL)
    axes = builder.observe(_bar(0, open_=2400.0, high=2401.0, low=2399.0, close=2400.5))
    assert axes.structure is None
    assert axes.direction is None
    # compression needs a 460-bar trailing window -- also honestly unresolved this early
    assert axes.is_compressed is None


def test_a_clean_staircase_uptrend_never_reads_as_a_down_family_direction() -> None:
    """A monotonic sequence of strictly higher highs and higher lows, spaced past the K_DEFAULT=2
    fractal window, must never produce a bearish/weak_bearish reading -- whatever the exact BOS/CHoCH
    classification, the direction axis cannot contradict the price action driving it."""
    builder = RawAxesBuilder(_SYMBOL)
    axes = None
    price = 2400.0
    for i in range(40):
        step = 2.0
        o = price
        h = o + step + 0.5
        low_ = o - 0.3
        c = o + step
        axes = builder.observe(_bar(i, open_=o, high=h, low=low_, close=c))
        price = c

    assert axes is not None
    assert axes.direction in (None, "up", "weak_up")
    assert axes.structure in (None, "strong", "weak")


def test_a_large_range_bar_after_calm_history_reads_as_displacement() -> None:
    """`expansion()`'s own formula: range > 1.5x the PRIOR bar's ATR14 AND |close-open| >= 0.5x range.
    16 calm, small-range bars establish a low ATR14; the 17th bar's range/body deliberately clears both
    thresholds by a wide margin so the test isn't sensitive to ATR's own exact smoothing constant."""
    builder = RawAxesBuilder(_SYMBOL)
    price = 2400.0
    for i in range(16):
        o = price
        h = o + 0.3
        low_ = o - 0.3
        c = o + 0.05
        builder.observe(_bar(i, open_=o, high=h, low=low_, close=c))
        price = c

    displacement_bar = _bar(16, open_=price, high=price + 20.0, low=price - 1.0, close=price + 19.0)
    axes = builder.observe(displacement_bar)

    assert axes.is_displacement is True


def test_a_verified_confirmed_bos_bull_reads_as_strong_up_exactly_at_and_after_confirmation() -> None:
    """The precise counterpart to the loose staircase test above -- `conftest.bos_bull_bars()` was
    independently verified (see its own docstring) to make the REAL vendored detectors report exactly
    one `BOS_BULL` break at index 14. Before that bar, structure/direction must still be honestly
    unresolved (`None`); from that bar on, they must read `("strong", "up")` -- not merely "not down"."""
    builder = RawAxesBuilder(_SYMBOL)
    axes = None
    for i, bar in enumerate(bos_bull_bars(_SYMBOL)):
        axes = builder.observe(bar)
        if i < BOS_BULL_CONFIRMED_AT_INDEX:
            assert axes.structure is None, f"bar {i}: expected no structure yet, got {axes.structure!r}"
        else:
            assert axes.structure == "strong"
            assert axes.direction == "up"


def test_bars_observed_counts_every_call() -> None:
    builder = RawAxesBuilder(_SYMBOL)
    for i in range(5):
        builder.observe(_bar(i, open_=2400.0, high=2401.0, low=2399.0, close=2400.0))
    assert builder.bars_observed == 5
    assert builder.symbol == _SYMBOL

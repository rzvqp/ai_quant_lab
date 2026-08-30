"""Causal M15-to-H1 aggregation and EMA-50 tracking (CEO mandate: durable Q4 P007 prospective
detection gate, section 3). PATTERN-007's frozen reference is the H1 EMA-50 -- NOT the M15 EMA-50
`ema.py` computes (that module stays test-only, non-decision-critical, per E103/E104's own
correction: `"'EMA50' in this log has always meant the H1 EMA50 (never M15)"`). This module is the
first real (not test-only) causal H1 reference this package computes.

**Aggregation rule**: standard streaming hour-bucket resampling -- an M15 bar's hour is
`ts_open // 3600`. Feeding a bar whose hour differs from the currently-accumulating bucket's hour
means the PREVIOUS bucket is now complete (all bars for that hour that will ever arrive have
arrived) and gets folded into the EMA; a new bucket then starts for the current bar's hour. This
does NOT require exactly four M15 sub-bars per hour -- a bucket with fewer (an hour partially
inside a maintenance/weekend gap) still aggregates whatever is present, open=first sub-bar's open,
close=last sub-bar's close, high/low across all of them. This is deliberately simpler than a
minute-45-triggered rule and more robust to the real, documented gap structure in this data (GAP-151
..154 and friends) -- an hour missing its 45-minute sub-bar due to a gap would never close under a
minute-45 rule, silently freezing the H1 EMA at exactly the kind of moment (post-gap) prospective
detection matters most.

**Causal boundary, precisely**: `CausalH1EmaTracker.current_ema` after `feed(bar)` reflects the EMA
through the LAST bucket that has been closed BY THAT CALL -- i.e. it never includes anything from
`bar`'s own (possibly still-open) hour. Feeding bar 378 (2020-10-07T02:15 UTC, inside the still-open
02:00-03:00 hour) yields the EMA through the 01:00-02:00 H1 candle, matching mandate section 3's
"use only completed causal H1 candles" and RT-Q4-P007-004's own independently-reconstructed
`1901.160 @ bar 378` figure exactly (verified by `tests/test_causal_h1.py` against the real sealed
fixture, not merely asserted here).
"""

from __future__ import annotations

import dataclasses
from typing import Iterator

from ai_trader.csv_causal_replay.types import Bar

H1_EMA_PERIOD = 50
_SECONDS_PER_HOUR = 3600


@dataclasses.dataclass(frozen=True, slots=True)
class _H1Bucket:
    hour_start: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    sub_bar_count: int

    def extend(self, bar: Bar) -> "_H1Bucket":
        return dataclasses.replace(
            self, high=max(self.high, bar.high), low=min(self.low, bar.low), close=bar.close,
            volume=self.volume + (bar.volume or 0.0), sub_bar_count=self.sub_bar_count + 1,
        )


def _hour_start(ts_open: int) -> int:
    return (ts_open // _SECONDS_PER_HOUR) * _SECONDS_PER_HOUR


class CausalH1EmaTracker:
    """Stateful, incremental. `feed(bar)` must be called with M15 bars in strictly increasing
    `ts_open` order (the same order `SealedReader`/`engine.py` already enforce elsewhere in this
    package) -- this class does not re-sort or buffer out-of-order input."""

    def __init__(self, *, period: int = H1_EMA_PERIOD) -> None:
        self._period = period
        self._alpha = 2.0 / (period + 1)
        self._current_bucket: _H1Bucket | None = None
        self._closed_h1_count = 0
        self._seed_closes: list[float] = []
        self._ema: float | None = None

    @property
    def current_ema(self) -> float | None:
        """EMA-50 through the last CLOSED H1 candle -- `None` until at least `period` H1 candles
        have closed (mirrors `ema.py::causal_ema`'s own `< period` convention)."""
        return self._ema

    @property
    def closed_h1_count(self) -> int:
        return self._closed_h1_count

    def _close_bucket(self, bucket: _H1Bucket) -> None:
        self._closed_h1_count += 1
        if self._ema is None:
            self._seed_closes.append(bucket.close)
            if len(self._seed_closes) == self._period:
                self._ema = sum(self._seed_closes) / self._period
        else:
            self._ema = (bucket.close - self._ema) * self._alpha + self._ema

    def feed(self, bar: Bar) -> None:
        hour = _hour_start(bar.ts_open)
        if self._current_bucket is None:
            self._current_bucket = _H1Bucket(
                hour_start=hour, open=bar.open, high=bar.high, low=bar.low, close=bar.close,
                volume=bar.volume or 0.0, sub_bar_count=1,
            )
            return
        if hour == self._current_bucket.hour_start:
            self._current_bucket = self._current_bucket.extend(bar)
            return
        # `bar` starts a new hour -- the previous bucket is now complete.
        self._close_bucket(self._current_bucket)
        self._current_bucket = _H1Bucket(
            hour_start=hour, open=bar.open, high=bar.high, low=bar.low, close=bar.close,
            volume=bar.volume or 0.0, sub_bar_count=1,
        )


def replay_causal_h1_ema(bars: Iterator[Bar] | list[Bar], *, period: int = H1_EMA_PERIOD) -> CausalH1EmaTracker:
    """Convenience: feeds an ordered sequence of M15 bars through a fresh tracker and returns it,
    ready to read `.current_ema` -- the "rebuild from scratch" pattern this whole mandate's gate
    uses (mandate section 2: minimal, no new persisted state) rather than persisting tracker state
    separately from the sealed fixtures it is trivially, cheaply re-derivable from."""
    tracker = CausalH1EmaTracker(period=period)
    for bar in bars:
        tracker.feed(bar)
    return tracker

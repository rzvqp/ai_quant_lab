"""Prospective PATTERN-007 detection (CEO mandate: durable Q4 P007 prospective detection gate).

**Frozen definition used, not invented** (`GOLD_BEHAVIOR_MODEL_V1.md` PATTERN-007): "a sharp,
volume-confirmed close breaks... the H1 EMA50 itself... price does NOT sustain the break... a
reclaim follows." The mechanical, prospectively-checkable PART of that definition -- the part every
real historical instance (Q4-P007-003 @ bar 340, Q4-P007-004 @ bar 787) actually shares and that a
detector can evaluate bar-by-bar without inventing new thresholds -- is the crossing itself: an M15
close moves from at-or-above to strictly below the causal H1 EMA50 (`causal_h1.py`, section 3's
required reference; never the M15 `ema.py` helper). Volume/structural-level context (the rest of the
frozen definition) is the REASONING layer's job when it classifies a flagged candidate -- exactly
mirroring how `MGMT004_TRIGGER`/`P007_PRECLASSIFICATION` already separate a mechanical trigger from
a reasoning-dependent judgment elsewhere in this package. This is deliberately OVER-inclusive (every
EMA break gets flagged, not only ones that also look "severe" by volume) -- mandate section 4: "the
system must not silently pass such bars as routine," which a narrower, volume-gated trigger risks
doing on a break that turns out severe by some other measure.

`P007Detector` never assigns a catalog name like "Q4-P007-004" -- that numbering is the
apprenticeship's own ledger-keeping convention (`AI_TRADER_Q4_PATTERN_LEDGER.md`), not something a
bar-crossing detector can know (it would need the full prior catalog, which is out of this mandate's
minimal scope). It reports the trigger bar's index instead; the reasoning layer assigns the catalog
number when it prospectively classifies the candidate, exactly as it always has.
"""

from __future__ import annotations

import dataclasses
from typing import Iterator, Literal

from ai_trader.csv_causal_replay.causal_h1 import CausalH1EmaTracker
from ai_trader.csv_causal_replay.types import Bar

P007EventType = Literal["TRIGGER", "RESOLUTION"]


@dataclasses.dataclass(frozen=True, slots=True)
class P007Event:
    event_type: P007EventType
    bar_index: int
    bar_ts_open: int
    close: float
    h1_ema50: float
    """The causal H1 EMA50 in effect at this bar -- through the last CLOSED H1 candle, never
    including this bar's own (possibly still-open) hour."""


class P007Detector:
    """Stateful. `feed(bar, bar_index)` must be called with bars in strictly increasing index
    order, starting from Q4 bar 1 (or from wherever the caller's own causal H1 EMA50 warm-up window
    should start -- see `replay_p007_detection` for the convention this package uses: the same
    2000-bar M15 pre-Q4 warm-up every sealed fixture already carries)."""

    def __init__(self) -> None:
        self._h1 = CausalH1EmaTracker()
        self._prev_close: float | None = None
        self._prev_ema: float | None = None
        self._open_since_bar_index: int | None = None

    @property
    def is_open(self) -> bool:
        return self._open_since_bar_index is not None

    @property
    def open_since_bar_index(self) -> int | None:
        return self._open_since_bar_index

    def feed_warmup(self, bar: Bar) -> None:
        """Feeds a pre-Q4 warm-up bar for H1/EMA seed context ONLY -- never evaluated as a P007
        decision input (mirrors `ema.py`'s own warm-up-vs-decision distinction). Public method, not
        a reach into `_h1` directly, so `replay_p007_detection` (and any other caller) does not
        depend on this class's private internals."""
        self._h1.feed(bar)

    def feed(self, bar: Bar, bar_index: int) -> P007Event | None:
        ema_before = self._h1.current_ema  # causal: reflects H1 candles closed strictly before `bar`
        self._h1.feed(bar)

        event: P007Event | None = None
        if ema_before is not None and self._prev_close is not None and self._prev_ema is not None:
            was_at_or_above = self._prev_close >= self._prev_ema
            now_below = bar.close < ema_before
            now_at_or_above = bar.close >= ema_before

            if not self.is_open and was_at_or_above and now_below:
                self._open_since_bar_index = bar_index
                event = P007Event(
                    event_type="TRIGGER", bar_index=bar_index, bar_ts_open=bar.ts_open,
                    close=bar.close, h1_ema50=ema_before,
                )
            elif self.is_open and now_at_or_above:
                event = P007Event(
                    event_type="RESOLUTION", bar_index=bar_index, bar_ts_open=bar.ts_open,
                    close=bar.close, h1_ema50=ema_before,
                )
                self._open_since_bar_index = None

        self._prev_close = bar.close
        self._prev_ema = ema_before if ema_before is not None else self._prev_ema
        return event


def replay_p007_detection(rows: Iterator, *, upto_q4_bar_index: int | None = None) -> list[P007Event]:
    """`rows` is a `sealed_reader.SealedReader.iter_rows()` iterator (or anything yielding objects
    with `.bar`/`.q4_bar_index`) -- feeds warm-up rows (q4_bar_index is None) through the H1/EMA
    tracker for seed context exactly as `causal_h1.py`'s own docstring requires (verified against 4
    independent real anchor points, not merely asserted), then feeds Q4 rows through the detector,
    stopping after `upto_q4_bar_index` if given. Returns every TRIGGER/RESOLUTION event observed, in
    order -- the caller decides what to do with them (see `p007_gate.py` for the durable-state
    integration; this function itself never touches any state file).

    Breaks out immediately AFTER processing the row whose index EQUALS `upto_q4_bar_index` --
    deliberately never a check of "is this new row already past the limit", which would require the
    underlying `rows` generator to have already tried producing the NEXT row first. If that
    generator is a `SealedReader` bounded at a ceiling equal to `upto_q4_bar_index` (as
    `tests/test_p007_detector.py::_events_through` does), asking it for one row too many raises
    `SealedBoundaryError` from inside `next()`, before this function's own body ever runs for that
    row -- caught during development, fixed by breaking on equality instead of on overshoot."""
    detector = P007Detector()
    events: list[P007Event] = []
    for row in rows:
        if row.q4_bar_index is None:
            detector.feed_warmup(row.bar)
            continue
        event = detector.feed(row.bar, row.q4_bar_index)
        if event is not None:
            events.append(event)
        if upto_q4_bar_index is not None and row.q4_bar_index == upto_q4_bar_index:
            break
    return events

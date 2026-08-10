"""`LiveBarFeed` (Piesa 1): emits a `Bar` only at candle CLOSE, never a forming/in-progress bar.

Motivated by a concrete failure the data-acquisition division found today (CEO, 2026-07-26): the
TradingView replay cursor's own bar carries a PROVISIONAL close/volume while still active, which
corrupted 1,186 of 355,716 bars in one historical file. The same error class live -- reading a bar
before its close time has actually passed -- would produce signals on values that can still change
after being read.

`poll()` computes each candidate bar's own close time (`ts_open + bar_seconds`) and compares it against
the injected clock; a bar whose close time has not yet passed is filtered out, silently -- this is not
an error, it simply is not closed yet. Dedup against `_last_emitted_ts_open` ensures a bar already
returned by a prior `poll()` is never returned twice.

**Mandate 2 (2026-07-27), persistence**: an optional injected `SqliteStateStore` makes the watermark
survive a process restart -- without one, behavior is byte-for-byte the prior in-memory-only version
(every pre-Mandate-2 test still passes unmodified). With one, the watermark is loaded from the store at
construction (instead of starting at `None`) and written through on every `poll()` that emits new bars,
keyed per `(symbol, mt5_timeframe)` so two feeds sharing one store never collide.

**Mandate 3, Element 1 (2026-07-27), gap continuity detection**: `poll()` now also checks that each
newly emitted bar's `ts_open` is exactly one `bar_seconds` after the previous one (either the last bar
emitted earlier in this same `poll()` batch, or `_last_emitted_ts_open` carried over from before --
including a value LOADED from the persisted watermark, so a gap that occurred while the process was
down is detected exactly the same way as one that occurred mid-run, no special-casing). A violation is
reported as a `GapRecord` (classified via `gap_classification.classify_gap`) -- never filled, never
interpolated, never estimated. `last_gaps()` returns whatever gaps were found during the MOST RECENT
`poll()` call only (empty before the first `poll()`, and reset to empty on any `poll()` that finds no
new gap).

**Backfill, added 2026-08-10** (CEO, after a 6-day operator pause left every live process's own history
cold: "Barele istorice se pot trage retroactiv din MT5... la reconectare, fiecare proces trage barele
lipsa din watermark pana la prezent"): when the persisted watermark is stale by more than what a normal
`lookback_count`-sized fetch would cover, `poll()` switches to `copy_rates_range` for the ENTIRE missing
window instead of `copy_rates_from`'s small fixed lookback -- fetching the REAL history MT5 already has,
never inventing a value (this is not the "imputation"/"interpolation" `GapRecord`'s own docstring rules
out; it's the opposite -- reading genuine past data that was simply never asked for yet). Every bar
recovered this way carries `Bar.is_backfilled=True`. Capped at `MAX_BACKFILL_SECONDS` (30 days, CEO's
own limit) -- beyond that, `poll()` deliberately does NOT backfill (falls back to the normal small
lookback, same as today), and the resulting `GapRecord.backfill_capped=True` makes that omission visible
rather than silent. Still exactly one gap detection pass either way -- backfilling only changes how many
of the missing bars get recovered, never whether the gap itself is reported.

**Clock fix, 2026-08-11** (CEO, priority maxima, after the "blocked feed" diagnostic turned out to be a
false alarm): MT5 reports every timestamp -- ticks and historical bars alike -- in the broker/terminal's
own server time, not true UTC. Every one of the 5 live entrypoints constructed `LiveBarFeed` without an
explicit `clock=`, so all of them fell back to `_default_clock` (true system UTC) -- meaning `poll()`'s
"still-forming" filter compared a broker-labeled `ts_close` against a system-labeled `now`, holding back
every genuinely closed bar for a full offset period (measured at +3h against XAUUSD/FusionMarkets, same
across M1/M5/M15, same on EURUSD -- a terminal-wide convention, not a feed or symbol issue). See
`make_broker_clock` below for the fix and why it re-reads every call rather than memoizing an offset.
"""

from __future__ import annotations

import numbers
import time
from typing import Any, Callable

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway
from ai_trader.live_signal_source.gap_classification import classify_gap
from ai_trader.live_signal_source.types import Bar, BarFeedError, GapRecord
from ai_trader.persistent_state.store import SqliteStateStore

MAX_BACKFILL_SECONDS = 30 * 86_400
"""30 days, CEO's own explicit limit (2026-08-10): "maxim 30 de zile inapoi. Peste, raporteaza si nu
umple." A gap longer than this is reported via the normal `GapRecord` mechanism (with
`backfill_capped=True`) but its bars are never fetched."""


def _default_clock() -> int:
    """True system UTC. NOT what any of the 5 live entrypoints should actually use in production --
    see `make_broker_clock` below. Kept as the parameter default only so every existing test/fake that
    never cared about wall-clock alignment (constructing a `LiveBarFeed` with an injected `clock=`
    lambda of its own) keeps working unchanged."""
    return int(time.time())


def make_broker_clock(gateway: MT5Gateway, symbol: str) -> Callable[[], int]:
    """CEO instruction, 2026-08-11: MT5 reports every timestamp it returns -- ticks AND historical
    bars alike -- in the broker/terminal's OWN server time, not true UTC. Measured directly against
    XAUUSD/FusionMarkets as a constant +3h offset (consistent with EEST), confirmed identically across
    M1/M5/M15 and on a second, unrelated symbol (EURUSD) -- a terminal-wide clock convention, not a
    feed-specific anomaly.

    `LiveBarFeed`'s prior default (`_default_clock`, true system UTC) meant `poll()`'s own
    "still-forming" filter (`ts_close > now`) compared a broker-labeled `ts_close` against a
    system-labeled `now` -- so every genuinely closed bar was held back and reported as "not yet
    closed" for a full offset period after it actually closed. Not a feed outage; a clock mismatch,
    present since this system's very first bar (self-consistent and invisible until directly comparing
    `symbol_info_tick().time` against system `time.time()`, which is what surfaced it).

    Returns a clock function that reads `symbol_info_tick(symbol).time` FRESH on every single call --
    never memoizes an offset, never reads it once at construction. This is deliberate, not just
    simplicity: broker server time shifts with DST twice a year, so a live run spanning a DST
    transition would silently be wrong again if the offset were computed once and added as a constant
    thereafter. The only correct answer is to ask the terminal what time it is, every time.

    Fail-closed: raises `BarFeedError` if the terminal can't produce a tick right now, rather than
    falling back to system time -- a silent fallback would quietly reintroduce the exact bug this
    fixes."""

    def clock() -> int:
        tick = gateway.symbol_info_tick(symbol)
        if tick is None:
            raise BarFeedError(
                f"make_broker_clock({symbol!r}): symbol_info_tick returned None -- cannot read broker time"
            )
        return int(tick.time)

    return clock


def _read_field(rate: object, name: str) -> int | float | None:
    """MT5's real `copy_rates_from`/`copy_rates_range` return a numpy STRUCTURED ARRAY -- each row's
    fields are reached via `rate[name]` (item access), NOT `rate.name` (attribute access) -- unlike every
    other MT5 terminal call this codebase reads (`symbol_info_tick`, `account_info`, etc., all namedtuples
    supporting attribute access). Discovered against the real terminal (2026-07-30): `getattr`-only field
    reads silently returned `None` for every OHLC field, since a numpy structured scalar has no such
    attributes, which `poll()` correctly treated as a genuine gateway failure -- but the real cause was
    this file never having been exercised against the real return shape before, only against fake
    fixtures built as attribute-accessible dataclasses. Tries attribute access first (so every existing
    namedtuple-shaped fake keeps working unchanged), then item access (the real shape) -- duck-typed, so
    this file never needs to import numpy directly.

    Return type narrowed to `int | float | None` (not the raw `object | None` a fully generic reader
    would have) -- every field this is ever called with (`time`/`open`/`high`/`low`/`close`/
    `tick_volume`) is numeric by construction on both the real numpy shape and every fake used in
    tests; validated with a `numbers.Real` check (NOT a plain `isinstance(value, (int, float))` --
    confirmed by direct check that `numpy.int64` is NOT a Python `int` instance, though it IS
    registered as a `numbers.Integral`/`numbers.Real` virtual subclass, as `numpy.float64` already is
    via genuine inheritance from `float`) so a genuinely malformed value (a string, an object) is
    treated as absent -- fail-closed -- not silently miscoerced, while every real numpy scalar type
    this file actually receives is still accepted."""
    value: object = getattr(rate, name, None)
    if value is None:
        try:
            value = rate[name]  # type: ignore[index]
        except (TypeError, IndexError, KeyError, ValueError):
            # ValueError: numpy's own error for an unknown structured-array field name (confirmed
            # directly -- distinct from the TypeError a non-subscriptable fake raises, and from the
            # IndexError/KeyError a list/dict-shaped fake would raise for a bad key).
            return None
    if isinstance(value, numbers.Real):
        return value  # type: ignore[return-value]  # numbers.Real is not statically int|float, but every
        # concrete member this file ever sees (int, float, numpy.int64, numpy.float64) genuinely is
    return None


class LiveBarFeed:
    def __init__(
        self, gateway: MT5Gateway, symbol: str, mt5_timeframe: int, bar_seconds: int,
        lookback_count: int = 10, clock: Callable[[], int] = _default_clock,
        state_store: SqliteStateStore | None = None,
    ) -> None:
        if bar_seconds <= 0:
            raise ValueError(f"LiveBarFeed: bar_seconds must be > 0, got {bar_seconds!r}")
        if lookback_count <= 0:
            raise ValueError(f"LiveBarFeed: lookback_count must be > 0, got {lookback_count!r}")
        self._gateway = gateway
        self._symbol = symbol
        self._mt5_timeframe = mt5_timeframe
        self._bar_seconds = bar_seconds
        self._lookback_count = lookback_count
        self._clock = clock
        self._state_store = state_store
        self._watermark_key = f"live_signal_source.bar_feed:{symbol}:{mt5_timeframe}"
        self._last_emitted_ts_open: int | None = (
            None if state_store is None else self._load_persisted_watermark(state_store)
        )
        self._last_gaps: tuple[GapRecord, ...] = ()

    def _load_persisted_watermark(self, state_store: SqliteStateStore) -> int | None:
        persisted = state_store.get_value(self._watermark_key)
        return None if persisted is None else int(persisted)

    def last_gaps(self) -> tuple[GapRecord, ...]:
        """Gaps found during the most recent `poll()` call only -- not an accumulated history (the
        journal, via `CandidateSignalProducer`, is responsible for retaining that)."""
        return self._last_gaps

    def _fetch_rates(self, now: int) -> tuple[bool, bool, Any]:
        """Decides which of `copy_rates_from` (small fixed lookback, the steady-state case) or
        `copy_rates_range` (the full missing window, the backfill case) to call. Returns
        `(is_backfill, backfill_capped, rates)` -- `is_backfill` is `True` only when a range fetch for
        the missing window was actually issued; `backfill_capped` is `True` only when the gap was too
        large to backfill (>`MAX_BACKFILL_SECONDS`) and the normal small lookback was used instead."""
        if self._last_emitted_ts_open is not None:
            next_expected = self._last_emitted_ts_open + self._bar_seconds
            missing_seconds = now - next_expected
            if missing_seconds > self._lookback_count * self._bar_seconds:
                if missing_seconds > MAX_BACKFILL_SECONDS:
                    return False, True, self._gateway.copy_rates_from(
                        self._symbol, self._mt5_timeframe, now, self._lookback_count,
                    )
                return True, False, self._gateway.copy_rates_range(
                    self._symbol, self._mt5_timeframe, next_expected, now,
                )
        return False, False, self._gateway.copy_rates_from(
            self._symbol, self._mt5_timeframe, now, self._lookback_count,
        )

    def poll(self) -> tuple[Bar, ...]:
        """Returns every newly CLOSED bar since the previous `poll()` call, oldest first. Never returns
        the currently-forming bar. Raises `BarFeedError` on a genuine gateway failure -- never returns a
        stale/partial result silently."""
        now = self._clock()
        is_backfill, backfill_capped, rates = self._fetch_rates(now)
        if rates is None:
            raise BarFeedError(f"copy_rates_from/copy_rates_range({self._symbol!r}) returned None")

        closed_bars: list[Bar] = []
        for rate in rates:
            ts_open = _read_field(rate, "time")
            open_ = _read_field(rate, "open")
            high = _read_field(rate, "high")
            low = _read_field(rate, "low")
            close = _read_field(rate, "close")
            volume = _read_field(rate, "tick_volume")
            if ts_open is None or open_ is None or high is None or low is None or close is None:
                raise BarFeedError(
                    f"copy_rates_from/copy_rates_range({self._symbol!r}) returned a rate missing an OHLC field"
                )

            ts_open = int(ts_open)
            ts_close = ts_open + self._bar_seconds
            if ts_close > now:
                continue  # still forming -- never emitted; not an error
            if self._last_emitted_ts_open is not None and ts_open <= self._last_emitted_ts_open:
                continue  # already emitted in a prior poll() -- dedup

            closed_bars.append(Bar(
                symbol=self._symbol, ts_open=ts_open, ts_close=ts_close,
                open=float(open_), high=float(high), low=float(low), close=float(close),
                volume=float(volume) if volume is not None else None,
                is_backfilled=is_backfill,
            ))

        closed_bars.sort(key=lambda b: b.ts_open)

        bars_backfilled = sum(1 for b in closed_bars if b.is_backfilled)

        gaps: list[GapRecord] = []
        previous_ts_open = self._last_emitted_ts_open
        for bar in closed_bars:
            if previous_ts_open is not None and bar.ts_open != previous_ts_open + self._bar_seconds:
                gaps.append(GapRecord(
                    symbol=self._symbol, gap_start=previous_ts_open, gap_end=bar.ts_open,
                    duration_seconds=bar.ts_open - previous_ts_open,
                    classification=classify_gap(previous_ts_open, bar.ts_open),
                    bars_backfilled=bars_backfilled, backfill_capped=backfill_capped,
                ))
            previous_ts_open = bar.ts_open
        self._last_gaps = tuple(gaps)

        if closed_bars:
            self._last_emitted_ts_open = closed_bars[-1].ts_open
            if self._state_store is not None:
                self._state_store.set_value(self._watermark_key, float(self._last_emitted_ts_open))
        return tuple(closed_bars)

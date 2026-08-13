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

**Clock fix, 2026-08-11, take 1 (superseded below)**: MT5 reports every timestamp -- ticks and
historical bars alike -- in the broker/terminal's own server time, not true UTC. The first fix injected
a `clock=` that read broker time directly (`make_broker_clock`, now removed) -- correct for `poll()`'s
own forming-bar check, but it left every DOWNSTREAM consumer (`day_boundary_start_utc`, `session_of`,
`gap_classification`'s `_is_maintenance_window`) still silently assuming its input epoch was true UTC,
which it wasn't -- broker time reached them unconverted.

**Clock fix, take 2, translate at the source (CEO decision, "Optiunea A")**: `LiveBarFeed` now converts
every raw MT5 timestamp it reads into true UTC BEFORE constructing a `Bar` -- so `Bar.ts_open`/`ts_close`
(and everything derived from them: `GapRecord.gap_start`/`gap_end`, `day_boundary_start_utc`,
`session_of`) are true UTC, unconditionally, for every consumer, with zero changes needed anywhere
downstream. The alternative (fixing every consumer individually) was rejected: more call sites, more
chances to miss one.

`clock=` goes back to meaning true system UTC (`_default_clock`) -- that's `poll()`'s own "now" again,
unchanged from before the broker-time detour. `broker_offset=` (new, see `make_broker_offset`) supplies
`broker_epoch - true_utc_epoch`, read fresh every `poll()` call, never memoized -- broker server time
shifts with DST twice a year, so the only correct answer is asking the terminal every time. Every raw
`rate["time"]` read from MT5 has `- offset` applied before it becomes a `Bar.ts_open`; every OUTGOING
query timestamp this file sends back to MT5 (`copy_rates_from`/`copy_rates_range`'s `date_from`/`date_to`
arguments) has `+ offset` applied first, since MT5's own API still expects broker-epoch inputs -- the
translation is a boundary shim around this file, not a claim that MT5 itself changed.

Backward compatible by construction: `broker_offset=None` (the default) makes `offset` a plain `0` for
every poll -- byte-for-byte the pre-broker-clock behavior, so no existing test needed to know about any
of this.

**Old observations stay, but get a marker, not a rewrite** (CEO: "Cele inregistrate sub decalaj au
etichete gresite... NU le sterge. Marcheaza-le cu un flag"): rather than adding a per-record boolean to
every downstream type that carries a clock-derived label (`GapRecord.classification`,
`SpreadObservation.session`/`day_boundary_label`, `structural_observer`'s REGIME `session`,
`zone_observer`'s `session_label`) -- four separate packages, each needing its own schema/serialization
change -- `poll()` persists ONE watermark per `(symbol, mt5_timeframe)`, the true-UTC `now` at the moment
`broker_offset` was first successfully used for this feed (written once, never overwritten). Any record
whose own timestamp predates that watermark was computed while the raw epoch was still being fed to
UTC-assuming label logic unconverted -- session/day-boundary/MAINTENANCE labels on it may be wrong. Any
record at or after it is correct. Raw timestamps on old records are NOT wrong (a constant offset cancels
in bar-to-bar duration math) -- only labels derived by treating one single epoch as an absolute
UTC-hour-of-day are; they can be recomputed later against the same raw timestamp if it's ever worth it.

**Duplicate-bar bug, 2026-08-11, found in production and fixed (CEO, urgent stop-and-repair order)**:
"read fresh every call, never memoized" (the paragraph above) was itself the bug. `make_broker_offset`'s
raw formula (`latest_closed_ts_open + 60 - system_now`) is only exactly correct at the INSTANT the anchor
M1 bar closes -- it decays by up to 60s as real time elapses while that same bar remains "most recently
closed". Reading it fresh every `poll()` meant the SAME real M15 bar got a strictly SMALLER broker_offset
on each successive poll within one 60s window, hence a strictly LARGER converted `ts_open` -- which passed
`poll()`'s own dedup check (`ts_open <= last_emitted_ts_open`) and was re-emitted as if new, every
`POLL_INTERVAL_SECONDS` (30s), for as long as the process ran. Confirmed live on two independent
processes: paired journal entries exactly 30s apart, every M15 bar, for ~10 hours.

The two constraints the CEO posed as apparently opposed -- "the same raw timestamp must convert to the
same UTC value no matter when it's read" vs. "must not reintroduce yesterday's bug of a memoized offset
that stops tracking DST" -- are resolved together below: the offset is cached, but the cache key is the
anchor M1 bar's own identity (`ts_open`), not wall-clock time. It is recomputed (and re-cached) only when
that identity changes -- which still happens at least once per ~60s of active trading, every bit as fast
as the old "fresh every call" DST responsiveness -- and returns the frozen, already-computed value for
every call in between. See `make_broker_offset`'s own docstring for the caching and rounding design.

**Stale-probe auto-recovery, 2026-08-14 (CEO, after the fix above shipped)**: the stale-probe fail-closed
check (`make_broker_offset`, added 2026-08-11) was correct to refuse a wrong offset -- but WRONG in HOW
it refused. It raised the same generic `BarFeedError` a genuinely broken gateway raises, which propagates
uncaught through `poll()` -> the entrypoint's own `tick()` -> `run_forever()`'s while loop, killing the
whole process. Confirmed in production: all 5 live processes died simultaneously on a genuine 62-minute
MT5 data gap (2026-08-12 20:58-22:00 UTC, a nightly pattern -- the SAME gap the bar-continuity gap
detector already handles gracefully, classifying it MAINTENANCE and continuing). Two different reactions
to the same phenomenon: the CEO's own words, "acelasi fenomen, doua reactii diferite."

The fix keeps fail-closed exactly as approved -- `poll()` still refuses to emit any bar or compute any
offset while the probe is stale, the watermark is never touched, nothing is ever guessed -- but changes
what "refuse" means from "crash" to "return no bars this cycle and let the NEXT scheduled poll try
again." Requires distinguishing STALE (an expected, eventually-self-healing condition -- see
`StaleProbeError`, `live_signal_source/types.py`) from a genuinely broken gateway (empty probe, missing
field -- still a bare `BarFeedError`, still fatal, unchanged): `poll()` catches only the former. The
retry loop needed is already free -- the entrypoint's own existing poll cadence (`run_forever()`'s
`sleep()`) becomes the retry, no new scheduler.

**Visible, not silent**: `poll()` prints once when blocking begins and once on recovery (with the
elapsed duration) -- proportionate (a multi-hour outage does not spam a line every 30s) but never the
previous "nothing at all forever" silence. On recovery, a `GapRecord` for the exact outage window
(`gap_start`=the moment blocking was first detected, `gap_end`=the moment the probe was fresh again) is
added to `last_gaps()` -- the SAME channel every entrypoint already journals through (`record_gap`), so
this needed zero changes to any of the 5 entrypoint files. Classified via the SAME `classify_gap` every
bar-continuity gap already uses -- a nightly ~62-minute block during hour 20-21 UTC lands MAINTENANCE,
identical to how the bar-level gap detector already classifies the same real-world event. This can
produce a SECOND, separate `GapRecord` from the bar-continuity check in the same `poll()` (if the M15
series itself also shows a discontinuity once backfill runs) -- disclosed, not suppressed: two different
instruments (the offset probe, the bar sequence) observing the same real event is not a bug, and
guessing when to merge them would be more error-prone than reporting both honestly.

**The CEO's own design question, answered**: is there a threshold past which waiting becomes abnormal?
Yes -- reused, not invented: `gap_classification.MAX_REAL_WEEKEND_SECONDS` (72h), the SAME
empirically-derived threshold that already separates a real weekend (measured at exactly 49.25h, five
times, zero variance) from an operator-caused `EXTENDED_PAUSE` (the 6-day pause measured 131.5h, 2.67x
that line). Past 72h of continuous blocking, the recovery print's own wording flags it as exceeding any
known real closure -- the process still WAITS (stopping would reintroduce the exact bug this fix closes;
a pure read-only poller sitting idle costs nothing while genuinely waiting), it does not auto-stop and
does not page anyone -- proactive alerting (Telegram, matching the news monitor's own HIGH-impact
channel) is a separate, not-yet-requested capability, not built here. The eventual `GapRecord`, once
recovery happens, classifies to `UNEXPECTED` on its own for any non-weekend block this long (`
_is_maintenance_window` only accepts <=75 minutes) -- this project's own existing "only UNEXPECTED is a
problem" signal already covers it, no new classification value needed.
"""

from __future__ import annotations

import numbers
import time
from typing import Any, Callable

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway
from ai_trader.live_signal_source.gap_classification import MAX_REAL_WEEKEND_SECONDS, classify_gap
from ai_trader.live_signal_source.types import Bar, BarFeedError, GapRecord, StaleProbeError
from ai_trader.persistent_state.store import SqliteStateStore

MAX_BACKFILL_SECONDS = 30 * 86_400
"""30 days, CEO's own explicit limit (2026-08-10): "maxim 30 de zile inapoi. Peste, raporteaza si nu
umple." A gap longer than this is reported via the normal `GapRecord` mechanism (with
`backfill_capped=True`) but its bars are never fetched."""


def _default_clock() -> int:
    """True system UTC -- `poll()`'s own "now", used for the forming-bar check. Correct as-is; the
    broker/UTC mismatch this file corrects for lives entirely in `broker_offset` (see
    `make_broker_offset` below), not here."""
    return int(time.time())


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


_OFFSET_PROBE_MT5_TIMEFRAME = 1
"""MT5's M1 timeframe constant -- equals 1 by the same "M1-M30 constant == minute count" convention
this codebase already relies on for `MT5_TIMEFRAME_M15 = 15` in every entrypoint. Used only by
`make_broker_offset`'s own probe, independent of whatever timeframe the `LiveBarFeed` this offset feeds
is actually tracking."""
_OFFSET_PROBE_BAR_SECONDS = 60
_OFFSET_PROBE_FUTURE_MARGIN_SECONDS = 24 * 3600
"""Generously larger than any plausible real broker/UTC offset -- guarantees the probe query lands
after whatever the broker's actual current epoch is, so MT5 returns its own genuinely most recent
CLOSED M1 bar, not an artifact of this file not yet knowing what the offset is."""
_OFFSET_PROBE_MAX_STALE_LAG_SECONDS = _OFFSET_PROBE_BAR_SECONDS
"""Derived, not chosen (CEO instruction, 2026-08-11: "pragul il derivi, nu-l alegi"). At any probe call
`i`, the latest CLOSED M1 bar's own "raw staleness" `r_i := true_broker_now_i - latest_ts_open_i`
satisfies `r_i in [T, 2T)` where `T = _OFFSET_PROBE_BAR_SECONDS` -- the returned bar is the one BEFORE
whichever bar is currently forming, so it closed at least one full period ago, and less than two (M1
bars close on a fixed 60s TIME cadence during open market, not on price activity -- CEO's own framing).

`lag` (elapsed real time minus elapsed bar-epoch time between two calls) reduces algebraically to
`r_2 - r_1` when no bar was actually missed in between -- NOT `r_1 + r_2`, because both readings are
biased in the SAME direction and the bias cancels in the subtraction, not adds. Since each `r_i in [T,
2T)` independently, `r_2 - r_1 in (-T, T)`, so under continuous trading `|lag| < T` always, with `T - 1`
the largest value integer seconds can actually produce. `lag >= T` is therefore never achievable while
the market keeps producing bars -- it proves at least one bar period was skipped between the two calls,
i.e. the market stopped trading. Not `2 * T`: that was this function's own first-draft derivation,
caught as an over-count by a failing test (`test_make_broker_offset_staleness_accumulates_across_many_
quiet_polls`) before it shipped -- summing each end's jitter instead of recognizing they subtract.

Left UNCHANGED by the 2026-08-11 duplicate-bar fix below: this comparison is computed from the RAW anchor
fields (`system_now`, `ts_open` at the last genuine bar advance), never from the cached, rounded offset
value -- caching the offset does not touch this derivation or its threshold."""


def make_broker_offset(
    gateway: MT5Gateway, symbol: str, system_clock: Callable[[], int] = _default_clock,
) -> Callable[[], int]:
    """Returns a function computing `broker_epoch - true_utc_epoch` (positive when the broker is ahead),
    read fresh -- never cached -- on every single call.

    **Not measured via `symbol_info_tick(...).time`** (the first version of this function, reverted):
    discovered empirically (2026-08-11) that a tick's `.time` is the timestamp of the LAST PRICE TICK,
    not a live server clock -- during a quiet stretch it can lag the terminal's actual current time by
    tens of minutes, observed directly (offset estimates swinging by over 2500 seconds within the same
    session, with no real broker/UTC relationship changing that fast). A per-poll offset that noisy
    would make consecutive polls disagree about the SAME bar's own corrected timestamp, and could make
    a perfectly continuous bar sequence look like it had a gap that never happened.

    **Measured via a dedicated M1 probe instead**: `copy_rates_from(symbol, M1, system_clock() + 24h,
    1)` -- querying deliberately far in the future (relative to true UTC, before the offset is even
    known) forces MT5 to return its own genuinely most recent CLOSED M1 bar, whatever timeframe this
    feed itself tracks. Since M1 bars close every 60 real seconds during active trading, the returned
    bar's own `ts_open` pins down the broker's current epoch to within about one minute -- `+ 60` steps
    forward to the currently-forming bar's own boundary, which is the working offset estimate. Far
    tighter and far more stable than tick staleness ever demonstrated.

    Re-reading fresh every call also means DST transitions (or, per this session's own finding, whatever
    slower continuous drift produced the swing above -- worth separate investigation on the
    terminal/broker side, not something this function can diagnose) are absorbed automatically: whatever
    the terminal's own clock says right now is what gets used, never a value computed once and reused.

    Fail-closed against an EMPTY probe: raises `BarFeedError` if `copy_rates_from` returns nothing at
    all, rather than falling back to a zero offset -- a silent fallback would quietly reintroduce the
    broker/UTC mismatch this exists to eliminate.

    **Fail-closed against a STALE probe too, added 2026-08-11** (CEO's own question and decision: "ce se
    intampla cand piata e inchisa... optiunea A, sonda ridica eroare daca bara e stale"): a genuine
    market closure -- weekend, holiday -- still returns a NON-EMPTY M1 probe (MT5's own last bar before
    the closure), so the empty-result check alone doesn't catch it; silently using that stale bar would
    reintroduce the exact same bug this function exists to eliminate, on the timescale of a closure
    instead of a single measurement.

    Detected by comparing THIS call's real time and raw M1 timestamp against the last call where the M1
    bar had genuinely advanced (small closure-local state -- NOT the offset itself, never reused as the
    offset, purely a freshness reference updated only when a new bar actually appears, so staleness
    correctly ACCUMULATES across many quiet polls rather than resetting every call). If real time has
    outrun bar advancement by more than `_OFFSET_PROBE_MAX_STALE_LAG_SECONDS`, raises `BarFeedError`
    instead of returning a wrong offset. The very FIRST call ever (nothing to compare against yet) is
    accepted unvalidated -- this project's own restart discipline only starts a process when the CEO
    already knows the market is open, so a fresh process's first probe should already be fresh; this
    check's value is catching the TRANSITION into a closure on an ALREADY-RUNNING process (Friday
    evening rolling into the weekend), not the cold start.

    **Known limitation, disclosed not solved**: a DST "fall back" transition (broker wall-clock loses an
    hour) can make ONE poll's raw M1 timestamp appear to move BACKWARD relative to the previous call,
    which this check cannot distinguish from staleness -- it would raise for that single poll, then
    self-heal on the next one once real bar advancement catches back up. Rare (once a year, one
    transition direction only) and not something this function attempts to special-case.

    **Duplicate-bar fix, 2026-08-11: the offset is now CACHED per anchor bar, not recomputed fresh every
    call.** The raw formula (`latest_closed_ts_open + 60 - system_now`) is exact only at the instant the
    anchor bar closes, and decays by up to 60s across the rest of the window that bar remains "most
    recently closed" -- reading it fresh on every `poll()` therefore gave the SAME real M15 bar a strictly
    smaller offset (hence a strictly larger converted `ts_open`) on each successive 30s poll, silently
    defeating `LiveBarFeed`'s own dedup check and re-emitting it as if new. Confirmed live in production
    on two independent processes: every M15 bar re-emitted in a pair exactly `POLL_INTERVAL_SECONDS`
    apart, for as long as the process ran.

    The fix: the offset is computed, and CACHED, only at the moment this function first detects the
    anchor bar has changed -- every subsequent call that still sees that SAME anchor bar returns the
    frozen cached value, not a fresh recomputation. This directly satisfies "the same raw timestamp
    converts to the same UTC value no matter when it's read" for any two calls within one anchor window
    (the actual bug scenario). It does NOT reintroduce yesterday's memoized-offset-that-ignores-DST bug:
    the cache still refreshes automatically whenever the anchor bar itself advances -- at least once
    every ~60s of active trading, identical responsiveness to the old "fresh every call" design, just no
    longer decaying in between.

    **Rounded to the nearest `_OFFSET_PROBE_BAR_SECONDS` (60) on each refresh.** The value cached at
    first-detection is `true_offset - detection_delay`, where `detection_delay` is however many seconds
    elapsed between the anchor bar's TRUE close and the poll that first noticed it -- 0 up to just under
    one polling interval, never negative (detection cannot happen before the bar closes). Real broker/UTC
    offsets are always a whole number of minutes (every timezone offset in use today is a multiple of 15
    minutes), so rounding to the nearest 60 snaps this one-sided latency noise back to the true, clean
    value -- correct as long as `detection_delay` stays under 30s, true for any poll cadence at or below
    the probe's own 60s bar period (every entrypoint in this codebase polls at 30s)."""

    _anchor: dict[str, int] = {}
    """Two roles in one dict, updated together: (1) the freshness reference for the staleness check above
    (`system_now`/`ts_open` at the last genuine bar advance -- unchanged from before this fix); (2) the
    cached, rounded offset value (`offset`) computed at that same moment. Both are refreshed ONLY when the
    anchor bar's own `ts_open` genuinely changes -- never on every call -- so staleness keeps accumulating
    across a multi-poll closure (the reason this design already existed) and the cached offset stays
    frozen for every call that sees the same anchor bar (the reason it was extended, 2026-08-11)."""

    def offset() -> int:
        system_now = system_clock()
        rates = gateway.copy_rates_from(
            symbol, _OFFSET_PROBE_MT5_TIMEFRAME, system_now + _OFFSET_PROBE_FUTURE_MARGIN_SECONDS, 1,
        )
        if rates is None or len(rates) == 0:
            raise BarFeedError(
                f"make_broker_offset({symbol!r}): M1 probe returned no bars -- cannot determine offset"
            )
        latest_closed_ts_open = _read_field(rates[0], "time")
        if latest_closed_ts_open is None:
            raise BarFeedError(
                f"make_broker_offset({symbol!r}): M1 probe rate is missing its own time field"
            )
        latest_closed_ts_open = int(latest_closed_ts_open)

        if "system_now" in _anchor:
            elapsed_real = system_now - _anchor["system_now"]
            bar_advance = latest_closed_ts_open - _anchor["ts_open"]
            lag = elapsed_real - bar_advance
            if lag >= _OFFSET_PROBE_MAX_STALE_LAG_SECONDS:
                raise StaleProbeError(
                    f"make_broker_offset({symbol!r}): M1 probe is stale -- real time advanced "
                    f"{elapsed_real}s since the last fresh bar but the latest M1 bar only advanced "
                    f"{bar_advance}s (lag={lag}s >= {_OFFSET_PROBE_MAX_STALE_LAG_SECONDS}s) -- "
                    f"market appears closed"
                )

        if latest_closed_ts_open != _anchor.get("ts_open"):
            # Only refresh (freshness reference AND cached offset) when the bar has genuinely moved
            # forward -- if every call refreshed it, a multi-poll closure would never accumulate staleness
            # (Mandate: 2026-08-11 stale-probe fix), and the offset would decay within the window again
            # (Mandate: 2026-08-11 duplicate-bar fix, this change).
            raw_offset = latest_closed_ts_open + _OFFSET_PROBE_BAR_SECONDS - system_now
            _anchor["system_now"] = system_now
            _anchor["ts_open"] = latest_closed_ts_open
            _anchor["offset"] = _round_to_nearest_probe_bar(raw_offset)

        return _anchor["offset"]

    return offset


def _round_to_nearest_probe_bar(raw_offset: int) -> int:
    """Snaps a freshly-measured offset to the nearest multiple of `_OFFSET_PROBE_BAR_SECONDS` (60) --
    see `make_broker_offset`'s own docstring, "Rounded to the nearest..." section, for the full
    derivation of why this is correct (real broker/UTC offsets are always whole minutes; the raw
    measurement's only error is one-sided detection latency bounded well under 30s)."""
    return round(raw_offset / _OFFSET_PROBE_BAR_SECONDS) * _OFFSET_PROBE_BAR_SECONDS


class LiveBarFeed:
    def __init__(
        self, gateway: MT5Gateway, symbol: str, mt5_timeframe: int, bar_seconds: int,
        lookback_count: int = 10, clock: Callable[[], int] = _default_clock,
        state_store: SqliteStateStore | None = None,
        broker_offset: Callable[[], int] | None = None,
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
        self._broker_offset = broker_offset
        """`None` (the default) means every raw MT5 timestamp is already true UTC as far as this feed
        is concerned -- `offset` is treated as `0` every poll, byte-for-byte the pre-broker-clock-fix
        behavior. Set via `make_broker_offset(gateway, symbol)` in production, where MT5 timestamps are
        actually broker-server time."""
        self._state_store = state_store
        self._watermark_key = f"live_signal_source.bar_feed:{symbol}:{mt5_timeframe}"
        self._clock_corrected_since_key = f"{self._watermark_key}.clock_corrected_since"
        self._last_emitted_ts_open: int | None = (
            None if state_store is None else self._load_persisted_watermark(state_store)
        )
        self._last_gaps: tuple[GapRecord, ...] = ()
        self._probe_blocked_since: int | None = None
        """True-UTC `now` at the poll where a `StaleProbeError` was FIRST seen, `None` when not
        currently blocked -- see this module's own "Stale-probe auto-recovery" docstring section."""

    def _load_persisted_watermark(self, state_store: SqliteStateStore) -> int | None:
        persisted = state_store.get_value(self._watermark_key)
        return None if persisted is None else int(persisted)

    def last_gaps(self) -> tuple[GapRecord, ...]:
        """Gaps found during the most recent `poll()` call only -- not an accumulated history (the
        journal, via `CandidateSignalProducer`, is responsible for retaining that)."""
        return self._last_gaps

    def _fetch_rates(self, now: int, offset: int) -> tuple[bool, bool, Any]:
        """Decides which of `copy_rates_from` (small fixed lookback, the steady-state case) or
        `copy_rates_range` (the full missing window, the backfill case) to call. Returns
        `(is_backfill, backfill_capped, rates)` -- `is_backfill` is `True` only when a range fetch for
        the missing window was actually issued; `backfill_capped` is `True` only when the gap was too
        large to backfill (>`MAX_BACKFILL_SECONDS`) and the normal small lookback was used instead.

        `now` and the watermark-derived `next_expected` are true UTC; MT5's own API still expects
        broker-epoch query timestamps, so `+ offset` is applied only on the way OUT here -- the raw
        rates that come back are converted `- offset` by the caller (`poll()`), not here."""
        if self._last_emitted_ts_open is not None:
            next_expected = self._last_emitted_ts_open + self._bar_seconds
            missing_seconds = now - next_expected
            if missing_seconds > self._lookback_count * self._bar_seconds:
                if missing_seconds > MAX_BACKFILL_SECONDS:
                    return False, True, self._gateway.copy_rates_from(
                        self._symbol, self._mt5_timeframe, now + offset, self._lookback_count,
                    )
                return True, False, self._gateway.copy_rates_range(
                    self._symbol, self._mt5_timeframe, next_expected + offset, now + offset,
                )
        return False, False, self._gateway.copy_rates_from(
            self._symbol, self._mt5_timeframe, now + offset, self._lookback_count,
        )

    def _offset_now(self) -> int:
        if self._broker_offset is None:
            return 0
        return self._broker_offset()

    def _record_clock_correction_watermark(self, now: int) -> None:
        """Persists, once, the true-UTC `now` at which this feed first ran with a real
        `broker_offset`. Never overwritten once set -- it marks the point after which every record
        this feed's own downstream journals produced can be trusted to carry correctly-converted
        timestamps; anything before it was computed while the raw epoch was broker time, unconverted."""
        if self._broker_offset is None or self._state_store is None:
            return
        if self._state_store.get_value(self._clock_corrected_since_key) is None:
            self._state_store.set_value(self._clock_corrected_since_key, float(now))

    @property
    def probe_blocked_since(self) -> int | None:
        """True-UTC timestamp of the poll where the CURRENTLY ONGOING stale-probe block was first
        detected, or `None` if not currently blocked -- lets a caller distinguish "polled, nothing new
        yet" from "polled, refusing to emit because the offset probe is stale" without inspecting logs."""
        return self._probe_blocked_since

    def poll(self) -> tuple[Bar, ...]:
        """Returns every newly CLOSED bar since the previous `poll()` call, oldest first, with
        `ts_open`/`ts_close` in true UTC regardless of what convention MT5 itself uses internally (see
        `broker_offset` on `__init__`). Never returns the currently-forming bar.

        While the broker-offset probe is stale (`StaleProbeError`), returns `()` -- no bars, no watermark
        change, no offset computed -- and retries on the next scheduled poll instead of raising (see this
        module's own "Stale-probe auto-recovery" docstring section). Still raises plain `BarFeedError` on
        a genuine gateway failure -- never returns a stale/partial result silently for THAT case."""
        now = self._clock()
        try:
            offset = self._offset_now()
        except StaleProbeError as exc:
            if self._probe_blocked_since is None:
                self._probe_blocked_since = now
                print(
                    f"LiveBarFeed({self._symbol!r}): broker-offset probe is stale -- refusing to emit, "
                    f"will retry every poll until fresh again ({exc})",
                    flush=True,
                )
            self._last_gaps = ()
            return ()

        probe_recovery_gap: tuple[GapRecord, ...] = ()
        if self._probe_blocked_since is not None:
            blocked_duration = now - self._probe_blocked_since
            recovery_gap = GapRecord(
                symbol=self._symbol, gap_start=self._probe_blocked_since, gap_end=now,
                duration_seconds=blocked_duration, classification=classify_gap(self._probe_blocked_since, now),
                bars_backfilled=0, backfill_capped=False,
            )
            anomaly_note = (
                f" -- exceeds {MAX_REAL_WEEKEND_SECONDS}s (72h), any known real closure duration"
                if blocked_duration > MAX_REAL_WEEKEND_SECONDS else ""
            )
            print(
                f"LiveBarFeed({self._symbol!r}): broker-offset probe fresh again after {blocked_duration}s "
                f"blocked, classified {recovery_gap.classification.value}{anomaly_note}",
                flush=True,
            )
            self._probe_blocked_since = None
            probe_recovery_gap = (recovery_gap,)

        self._record_clock_correction_watermark(now)
        is_backfill, backfill_capped, rates = self._fetch_rates(now, offset)
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

            ts_open = int(ts_open) - offset  # broker epoch -> true UTC, before anything else touches it
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
        self._last_gaps = probe_recovery_gap + tuple(gaps)

        if closed_bars:
            self._last_emitted_ts_open = closed_bars[-1].ts_open
            if self._state_store is not None:
                self._state_store.set_value(self._watermark_key, float(self._last_emitted_ts_open))
        return tuple(closed_bars)

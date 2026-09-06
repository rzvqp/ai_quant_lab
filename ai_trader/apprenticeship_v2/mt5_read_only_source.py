"""The SOLE `import MetaTrader5` point in this package (mirrors the repo's own established, CEO-
authorized `mt5_connectivity_probe.py` discipline). READ-ONLY.

**Authorized calls, and the only ones used anywhere in this module**: `initialize`, `shutdown`,
`last_error`, `symbol_info_tick`, `copy_rates_from_pos`.

**Never imported or called anywhere in this file**: `order_send`, `order_check`,
`order_calc_margin`, `order_calc_profit`, `positions_get`, `positions_close`, `orders_get`, or any
other write/position/order function. This is a structural fact checkable by reading this file --
not merely a convention.

Causal-safety technique (identical to the already-audited `soak_loop.py`/`gateway_ext.py` pattern,
reproduced independently here rather than importing that module, to avoid pulling in the
execution-adjacent `mt5_demo_execution`/`gateway_ext` stack at all):

1. Position-based fetch (`copy_rates_from_pos(symbol, timeframe, 0, count)`), never date-based --
   `start_pos=0` may include the still-forming bar; callers MUST filter by `ts_close <= true_utc_now`
   before treating any bar as closed.
2. Broker-clock offset correction (`broker_time - true_utc_time`, measured fresh from a live tick
   every call) -- MT5 bar/tick timestamps are the BROKER's own server clock, not necessarily true UTC
   (a live-discovered defect this exact repo's own `broker_clock.py` documents: this broker measured
   ~+3.0h offset). Every timestamp this module returns has already been corrected to true UTC.
"""

from __future__ import annotations

import dataclasses
import time
from typing import Callable

import MetaTrader5 as mt5

XAUUSD = "XAUUSD"

# MT5 API timeframe constants, used exactly as the package defines them -- never redefined.
TIMEFRAME_M5 = mt5.TIMEFRAME_M5
TIMEFRAME_M15 = mt5.TIMEFRAME_M15
TIMEFRAME_H1 = mt5.TIMEFRAME_H1
TIMEFRAME_H4 = mt5.TIMEFRAME_H4

BAR_SECONDS = {
    TIMEFRAME_M5: 5 * 60,
    TIMEFRAME_M15: 15 * 60,
    TIMEFRAME_H1: 60 * 60,
    TIMEFRAME_H4: 4 * 60 * 60,
}


@dataclasses.dataclass(frozen=True, slots=True)
class ReadOnlyBar:
    symbol: str
    timeframe: int
    ts_open: int
    ts_close: int
    open: float
    high: float
    low: float
    close: float
    volume: float | None


class MT5ReadOnlyUnavailable(Exception):
    """Raised when the live terminal cannot be reached read-only -- never silently substituted with
    stale or fabricated data."""


def _default_now() -> float:
    return time.time()


_offset_cache: dict[str, tuple[float, float]] = {}
"""Caches the last successfully-measured `(tick_time, offset_seconds)` pair per symbol -- see
`measure_broker_offset_seconds`'s own docstring below for why this exists. Module-level, not a
per-call/per-session value: the bug it fixes spans separate `fetch_causal_closed_bars` calls (and
separate `mt5_session()` blocks) within the same long-running process, so the cache must survive
across both to be effective. Single-threaded, process-local usage only (this entire module already
assumes that -- one local MT5 terminal connection, never concurrent access)."""


def measure_broker_offset_seconds(*, symbol: str = XAUUSD, now_fn: Callable[[], float] = _default_now) -> float:
    """`broker_time - true_utc_time`. `0.0` (no correction) if no tick is currently available -- never
    fabricated. Assumes `mt5.initialize()` has already been called by the caller in this same process
    (this function performs no connection management itself).

    **Cached per symbol, keyed on the tick's own `time` field -- live-discovered defect, fixed
    2026-09-06.** `tick.time` is the timestamp of the LAST PRICE TICK, not a continuously-advancing
    broker-clock reading: during a quiet market moment (no new tick arriving between two calls), it
    stays frozen while `now_fn()` keeps advancing, so recomputing `tick_time - now_fn()` fresh on
    every call made the result drift by approximately however long the market had been quiet --
    reproduced directly: two `fetch_causal_closed_bars` calls taken seconds apart, with no new tick in
    between, computed the SAME already-closed historical bar's own `ts_close` values one whole second
    apart, climbing further with each additional call for as long as the tick stayed stale (General
    Observer's own `last_processed_m15_ts_close` watermark, which compares this value for exact
    equality across ticks, surfaced this as an intermittent "already-processed bar looks new" failure
    -- General Observer's own dedup-by-level/price/direction, not by raw timestamp, happened to absorb
    the resulting reprocessing without ever creating a duplicate episode, but the watermark itself was
    not stable). This is not a clock-skew change -- the real broker/UTC relationship does not move
    second to second -- it was purely an artifact of treating a stale reference as fresh. (An
    independent, unrelated implementation of the same "broker clock offset" idea exists elsewhere in
    this repo, `live_signal_source/bar_feed.py::make_broker_offset` -- its own docstring documents the
    same root-cause class of bug, found and fixed there first, via a different, more involved
    mechanism this function does not adopt; see this function's own fix below for what IS adopted from
    it and why the narrower version suffices here.)

    The fix: the offset is recomputed only the first time (or the first time again after) a given
    `tick.time` is observed for a symbol; every subsequent call that sees the SAME `tick.time` reuses
    that cached value unchanged, rather than recomputing it against a `now_fn()` that has moved on
    without the market. A genuinely new tick (any change in `tick.time`) still triggers an immediate,
    fresh recomputation -- this is not a staleness tolerance applied to the comparison or the result;
    it computes the exact same formula this function always computed, from the exact same input,
    exactly once per distinct input, instead of silently recomputing (and drifting) against identical
    input. No bar-closure detection, no dedup check, and no market-structure value anywhere in this
    file is touched -- only how this one internal measurement is cached."""
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return 0.0
    tick_time = getattr(tick, "time", None)
    if tick_time is None:
        return 0.0
    tick_time = float(tick_time)

    cached = _offset_cache.get(symbol)
    if cached is not None and cached[0] == tick_time:
        return cached[1]

    offset = tick_time - now_fn()
    _offset_cache[symbol] = (tick_time, offset)
    return offset


def _bar_from_rate(rate, symbol: str, timeframe: int, *, offset_seconds: float) -> ReadOnlyBar:
    bar_seconds = BAR_SECONDS[timeframe]
    true_ts_open = int(round(float(rate["time"]) - offset_seconds))
    return ReadOnlyBar(
        symbol=symbol, timeframe=timeframe, ts_open=true_ts_open, ts_close=true_ts_open + bar_seconds,
        open=float(rate["open"]), high=float(rate["high"]), low=float(rate["low"]), close=float(rate["close"]),
        volume=float(rate["tick_volume"]) if "tick_volume" in rate.dtype.names else None,
    )


def fetch_causal_closed_bars(
    *, symbol: str = XAUUSD, timeframe: int, count: int, now_fn: Callable[[], float] = _default_now,
) -> list[ReadOnlyBar]:
    """The sole bar-reading entrypoint this package uses. Returns only bars whose (offset-corrected)
    `ts_close` is at or before true UTC now, sorted ascending by `ts_close`, deduplicated by
    `ts_close` (MT5 can return the same closed bar across consecutive `start_pos=0` calls). Raises
    `MT5ReadOnlyUnavailable` rather than returning a partial/fabricated result if the terminal cannot
    be read from -- callers must not silently substitute anything for a genuine read failure.

    Caller is responsible for `mt5.initialize()`/`mt5.shutdown()` lifecycle (see `mt5_session`
    context manager below) -- this function assumes an already-initialized terminal connection."""
    offset = measure_broker_offset_seconds(symbol=symbol, now_fn=now_fn)
    # start_pos=0 may include the still-forming bar; fetch a few extra and filter, matching the
    # already-audited soak_loop.py pattern exactly (count=4 there for M15 polling; this module is
    # called less frequently so fetches a slightly larger window to tolerate longer gaps between ticks).
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    if rates is None:
        raise MT5ReadOnlyUnavailable(f"copy_rates_from_pos returned None for {symbol}/{timeframe}: {mt5.last_error()}")
    now = now_fn()
    bars = [_bar_from_rate(r, symbol, timeframe, offset_seconds=offset) for r in rates]
    closed = sorted({b.ts_close: b for b in bars if b.ts_close <= now}.values(), key=lambda b: b.ts_close)
    return closed


class mt5_session:
    """Context manager: `mt5.initialize()` on entry, `mt5.shutdown()` on exit, always -- mirrors
    `mt5_connectivity_probe.py`'s own `try/finally` discipline. Raises `MT5ReadOnlyUnavailable` if
    `initialize()` fails; never proceeds with a half-open connection."""

    def __enter__(self) -> "mt5_session":
        if not mt5.initialize():
            raise MT5ReadOnlyUnavailable(f"mt5.initialize() failed: {mt5.last_error()}")
        return self

    def __exit__(self, *_exc_info: object) -> None:
        mt5.shutdown()

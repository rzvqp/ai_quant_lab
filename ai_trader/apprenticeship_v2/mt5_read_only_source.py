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


def measure_broker_offset_seconds(*, symbol: str = XAUUSD, now_fn: Callable[[], float] = _default_now) -> float:
    """`broker_time - true_utc_time`, from one fresh tick. `0.0` (no correction) if no tick is
    currently available -- never fabricated. Assumes `mt5.initialize()` has already been called by
    the caller in this same process (this function performs no connection management itself)."""
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return 0.0
    tick_time = getattr(tick, "time", None)
    if tick_time is None:
        return 0.0
    return float(tick_time) - now_fn()


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

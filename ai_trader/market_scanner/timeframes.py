"""Canonical timeframe <-> seconds mapping shared by every Market Scanner component.

Per ``MARKET_SCANNER_ARCHITECTURE.md`` §4.1: "all timestamps are UTC epoch seconds. Bars are keyed
by ``ts_open``; ``ts_close = ts_open + tf_seconds``." This module is the single source of truth for
that conversion so every component (clock, bar store, timeframe sync) agrees.
"""

from __future__ import annotations

from ai_trader.market_scanner.exceptions import UnknownTimeframeError

#: Timeframe code -> duration in seconds. Extend here only (never invent a per-component mapping).
TIMEFRAME_SECONDS: dict[str, int] = {
    "M1": 60,
    "M5": 5 * 60,
    "M15": 15 * 60,
    "M30": 30 * 60,
    "H1": 60 * 60,
    "H4": 4 * 60 * 60,
    "D1": 24 * 60 * 60,
    "W1": 7 * 24 * 60 * 60,
}


def timeframe_seconds(timeframe: str) -> int:
    """Return the duration of ``timeframe`` in seconds.

    Args:
        timeframe: a canonical timeframe code, e.g. ``"M15"``.

    Returns:
        The timeframe's duration in seconds.

    Raises:
        UnknownTimeframeError: if ``timeframe`` is not a recognised canonical code (also a
            ``ValueError`` — callers may catch either).
    """
    try:
        return TIMEFRAME_SECONDS[timeframe]
    except KeyError as exc:
        raise UnknownTimeframeError(timeframe) from exc


def snap_to_grid(ts: int, timeframe: str) -> int:
    """Snap a UTC epoch-second timestamp down to its canonical bar-open boundary.

    The canonical grid is anchored at the UTC epoch (1970-01-01T00:00:00Z), which is consistent for
    every timeframe up to and including ``D1``. ``W1`` is anchored so that week boundaries fall on
    Monday 00:00 UTC (the epoch, 1970-01-01, was a Thursday, so a fixed 4-day offset realigns the
    grid to Monday).

    Args:
        ts: a UTC epoch-second timestamp.
        timeframe: a canonical timeframe code.

    Returns:
        The UTC epoch-second timestamp of the bar-open boundary at or before ``ts``.
    """
    secs = timeframe_seconds(timeframe)
    if timeframe == "W1":
        # 1970-01-01 was a Thursday; Monday of that week was 1969-12-29 (4 days earlier).
        monday_epoch_offset = 4 * 24 * 60 * 60
        return ((ts + monday_epoch_offset) // secs) * secs - monday_epoch_offset
    return (ts // secs) * secs

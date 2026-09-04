"""Shared primitives (design doc Section 4, "Shared primitives used below") -- defined once,
referenced by every one of the 4 event contracts. Nothing here is a new rule; every function is
either a verbatim reuse of existing code or a direct, literal transcription of the frozen doc text.
"""

from __future__ import annotations

import bisect
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_trader.apprenticeship_v2.mt5_read_only_source import ReadOnlyBar


def atr14(bars: "list[ReadOnlyBar]") -> float | None:
    """Verbatim reuse of `loop.py::_atr14()`'s own formula (design doc: "reused verbatim... No new
    ATR formula introduced") -- the formula is copied here rather than imported, ONLY because
    `loop.py` transitively imports `mt5_read_only_source.py`, whose own module-level `import
    MetaTrader5` makes the whole chain unimportable in any environment without that package
    installed (confirmed by trying the import first, not assumed -- the exact same class of
    transitive-dependency problem already found and worked around this same way in
    `csv_causal_replay`'s own `types.py`, see that module's docstring for the precedent). This
    function's BODY is byte-for-byte identical to `loop.py::_atr14()` -- any future change to that
    formula must be mirrored here by hand; nothing about General Observer V1.1 changes what ATR14
    means, only where its source code physically lives to avoid an unrelated import chain.
    `atr14(h1_bars)` for `ATR14_H1[t]` is a direct, zero-ambiguity extension (the function is
    timeframe-agnostic), exactly as the design doc's Section 10/1c states."""
    if len(bars) < 15:
        return None
    trs = []
    for i in range(1, len(bars)):
        prev_close = bars[i - 1].close
        b = bars[i]
        tr = max(b.high - b.low, abs(b.high - prev_close), abs(b.low - prev_close))
        trs.append(tr)
    window = trs[-14:]
    return sum(window) / len(window)


def session_for_hour(hour_utc: int) -> str:
    """`hh<8→ASIA, hh<13→LONDON, hh<21→NY, else→LATE` -- reused verbatim from `code/mtf.py` and every
    report in this project's own thread (design doc Section 4 shared primitives)."""
    if hour_utc < 8:
        return "ASIA"
    if hour_utc < 13:
        return "LONDON"
    if hour_utc < 21:
        return "NY"
    return "LATE"


def session_for_ts(ts_utc: int) -> str:
    hour = datetime.datetime.fromtimestamp(ts_utc, tz=datetime.timezone.utc).hour
    return session_for_hour(hour)


def utc_day_for_ts(ts_utc: int) -> datetime.date:
    """UTC calendar day boundary (00:00-23:59:59 UTC) -- design doc Section 4 shared primitives."""
    return datetime.datetime.fromtimestamp(ts_utc, tz=datetime.timezone.utc).date()


def h1_confirmed_swing_highs(h1_bars: list[ReadOnlyBar]) -> list[tuple[int, float]]:
    """The 3-bar fractal (design doc Section 4): H1 bar `i`'s high is a confirmed swing high iff
    `bar[i-1].high < bar[i].high > bar[i+1].high`, confirmed at the close of bar `i+1`. Returns
    `[(confirmed_at_ts_close, swing_price), ...]` in ascending order -- `confirmed_at_ts_close` is
    `bar[i+1].ts_close` (the earliest moment this swing is causally knowable), NOT `bar[i].ts_close`
    (which would be a lookahead: bar `i`'s own close alone does not yet confirm it is a swing high --
    that requires seeing bar `i+1` too)."""
    out: list[tuple[int, float]] = []
    for i in range(1, len(h1_bars) - 1):
        if h1_bars[i - 1].high < h1_bars[i].high > h1_bars[i + 1].high:
            out.append((h1_bars[i + 1].ts_close, h1_bars[i].high))
    return out


def h1_confirmed_swing_lows(h1_bars: list[ReadOnlyBar]) -> list[tuple[int, float]]:
    """Symmetric to `h1_confirmed_swing_highs`, using lows."""
    out: list[tuple[int, float]] = []
    for i in range(1, len(h1_bars) - 1):
        if h1_bars[i - 1].low > h1_bars[i].low < h1_bars[i + 1].low:
            out.append((h1_bars[i + 1].ts_close, h1_bars[i].low))
    return out


def causally_available_swings(swings: list[tuple[int, float]], *, as_of_ts_close: int) -> list[float]:
    """Filters a `(confirmed_at_ts_close, price)` list down to only those confirmed at-or-before
    `as_of_ts_close` -- the causal-availability gate every major-level computation must apply (a
    swing that confirms only 2 bars from now must not be usable as a major level for the bar being
    evaluated right now)."""
    idx = bisect.bisect_right([s[0] for s in swings], as_of_ts_close)
    return [price for _, price in swings[:idx]]

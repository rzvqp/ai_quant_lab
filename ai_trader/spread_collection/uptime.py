"""Per-session uptime measurement (CEO instruction, 2026-08-04): "Fara ea, o celula goala nu se
distinge intre 'eveniment rar' si 'colectorul nu rula'."

`bars_passed` is measured from an INDEPENDENT ground truth -- `copy_rates_range` against the real MT5
history, never from `SpreadObservationLog` itself (a source that reports on its own uptime cannot detect
its own downtime: if the collector was dead, its own journal has nothing to say about what it missed).
`bars_recorded` comes from `SpreadObservationLog` for the same window. The ratio between them is the
uptime measurement the Statistician needs; it is undefined (`None`), not `0.0` or `1.0`, when a session
had no bars in the window at all -- a window that never touched a session says nothing about whether the
collector was running.

Only fully CLOSED bars (`ts_close <= now`) are counted on the ground-truth side, matching
`LiveBarFeed`'s own "never count a forming bar" rule -- this module counts history, but must count the
SAME thing the collector itself is entitled to have recorded, not a currently-forming bar it could not
possibly have observed yet."""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway
from ai_trader.spread_collection.journal import SpreadObservationLog
from ai_trader.spread_collection.vendor_bridge import sessions

_SESSIONS_IN_ORDER = ("asia", "london", "ny", "late")


@dataclass(frozen=True, slots=True)
class SessionUptimeReport:
    session: str
    window_start: int
    window_end: int
    bars_passed: int
    """Ground truth: real M15 bars that closed in this session within the window, per MT5 history --
    independent of whether the collector was running to see them."""
    bars_recorded: int
    """How many of those bars the collector actually captured, per `SpreadObservationLog`."""
    ratio: float | None
    """`bars_recorded / bars_passed`, or `None` if `bars_passed == 0` (undefined, not zero -- the
    window simply never touched this session)."""
    computed_as_of: int


def _read_field(rate: object, name: str) -> int | float | None:
    """Same duck-typed numpy-structured-array-or-namedtuple reader as `live_signal_source.bar_feed`
    (not imported from there to avoid pulling in `LiveBarFeed`'s clock/state-store machinery for a
    read-only history query) -- identical field-access behavior, deliberately duplicated at this small
    a size rather than adding a cross-package dependency for one helper."""
    value: object = getattr(rate, name, None)
    if value is None:
        try:
            value = rate[name]  # type: ignore[index]
        except (TypeError, IndexError, KeyError, ValueError):
            return None
    if isinstance(value, (int, float)):
        return value
    return None


def _true_closed_bar_count_by_session(
    gateway: MT5Gateway, symbol: str, mt5_timeframe: int, bar_seconds: int,
    window_start: int, window_end: int, now: int,
) -> dict[str, int]:
    """`window_start`/`window_end` bound each bar's CLOSE time (`ts_close`), matching
    `SpreadObservation.as_of` on the recorded side -- the MT5 fetch range is shifted back by
    `bar_seconds` on the front so a bar whose open falls just before `window_start` but whose close
    falls inside it is not missed at the boundary."""
    counts = {s: 0 for s in _SESSIONS_IN_ORDER}
    rates = gateway.copy_rates_range(symbol, mt5_timeframe, window_start - bar_seconds, window_end)
    if rates is None:
        return counts
    for rate in rates:
        ts_open = _read_field(rate, "time")
        if ts_open is None:
            continue
        ts_open = int(ts_open)
        ts_close = ts_open + bar_seconds
        if ts_close > now:
            continue  # still forming (or not yet closed) -- the collector could not have observed it
        if not (window_start <= ts_close <= window_end):
            continue
        session = str(sessions([ts_open])[0])
        if session in counts:
            counts[session] += 1
    return counts


def _recorded_bar_count_by_session(
    journal: SpreadObservationLog, symbol: str, window_start: int, window_end: int,
) -> dict[str, int]:
    counts = {s: 0 for s in _SESSIONS_IN_ORDER}
    for obs in journal.entries:
        if obs.symbol != symbol:
            continue
        if not (window_start <= obs.as_of <= window_end):
            continue
        if obs.session in counts:
            counts[obs.session] += 1
    return counts


def compute_session_uptime(
    gateway: MT5Gateway, journal: SpreadObservationLog, symbol: str, mt5_timeframe: int, bar_seconds: int,
    window_start: int, window_end: int, now: int,
) -> tuple[SessionUptimeReport, ...]:
    passed = _true_closed_bar_count_by_session(gateway, symbol, mt5_timeframe, bar_seconds, window_start, window_end, now)
    recorded = _recorded_bar_count_by_session(journal, symbol, window_start, window_end)
    reports = []
    for session in _SESSIONS_IN_ORDER:
        bars_passed = passed[session]
        bars_recorded = recorded[session]
        ratio = None if bars_passed == 0 else bars_recorded / bars_passed
        reports.append(SessionUptimeReport(
            session=session, window_start=window_start, window_end=window_end,
            bars_passed=bars_passed, bars_recorded=bars_recorded, ratio=ratio, computed_as_of=now,
        ))
    return tuple(reports)

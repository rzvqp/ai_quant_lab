"""Calendar Engine — date/day-of-week/day-of-month/week/month boundaries, holiday and weekend-gap
flags, and economic-event surfacing (``MARKET_SCANNER_ARCHITECTURE.md`` §7).

``is_new_day`` uses plain UTC calendar-date changes (``ts // 86400``), matching the frozen research
engine's own day-boundary convention (``mstrat_ext._new_day``) used by the calendar-effect families
(S18/S29/S31) — this is deliberately NOT the NY-17:00 session anchor (that anchor governs
*sessions*, via ``session.py``; calendar-day boundaries are plain UTC dates in the researched
system, and parity requires reproducing that exactly).

Holiday detection: ``is_holiday`` is set ONLY from a confirmed
:class:`~ai_trader.market_scanner.types.CalendarEvent` with ``kind="holiday"`` for that date — never
inferred from a day-count gap. A day-count gap larger than the normal weekend gap (Fri->Mon = 3
days) looks IDENTICAL from the bar feed alone whether it was a genuine market holiday or an
ordinary multi-day data outage; inferring "holiday" from that gap would silently fabricate a
calendar fact the scanner cannot actually know, in violation of the "never invent; always disclose"
policy (architecture §8) — a real outage of that shape is already honestly reported as an
unexplained gap via ``data_quality`` (see :mod:`~ai_trader.market_scanner.bar_store`), which is
where that signal belongs. Without an explicit holiday feed, ``is_holiday`` is simply ``False``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from typing import Any

from ai_trader.market_scanner.types import CalendarEvent, ImpactLevel


@dataclass(slots=True, frozen=True)
class EventFlag:
    """One calendar event surfaced within the configured window of ``as_of``."""

    ts: int
    impact: ImpactLevel
    kind: str | None


@dataclass(slots=True, frozen=True)
class CalendarSnapshot:
    """Everything the Calendar Engine knows as of the bar just processed."""

    date: date
    dow: int
    dom: int
    is_new_day: bool
    is_new_week: bool
    is_month_boundary: bool
    is_holiday: bool
    is_weekend_gap: bool
    dst_offset_seconds: int
    event_flags: list[EventFlag] = field(default_factory=list)

    def to_schema_dict(self) -> dict[str, Any]:
        """Render as the ``calendar`` object from ``MARKET_CONTEXT_SCHEMA.json``."""
        return {
            "date": self.date.isoformat(),
            "dow": self.dow,
            "dom": self.dom,
            "is_holiday": self.is_holiday,
            "is_weekend_gap": self.is_weekend_gap,
            "dst_offset_seconds": self.dst_offset_seconds,
            "event_flags": [
                {"ts": f.ts, "kind": f.kind, "impact": f.impact.value} for f in self.event_flags
            ]
            or None,
        }


def _monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


class CalendarEngine:
    """Per-symbol calendar state machine. Feed closed base bars, in order, via :meth:`update`."""

    __slots__ = ("_prev_date", "_prev_dow", "_events", "_confirmed_holidays")

    def __init__(self) -> None:
        self._prev_date: date | None = None
        self._prev_dow: int | None = None
        self._events: list[CalendarEvent] = []
        self._confirmed_holidays: set[date] = set()

    def ingest_event(self, event: CalendarEvent) -> None:
        """Register an economic/holiday calendar event."""
        self._events.append(event)
        if event.kind == "holiday":
            self._confirmed_holidays.add(datetime.fromtimestamp(event.ts, tz=UTC).date())

    def update(self, ts_open: int, event_flag_window_seconds: int) -> CalendarSnapshot:
        """Advance the calendar state by one closed base bar and return its snapshot.

        Args:
            ts_open: the bar's open timestamp (UTC epoch seconds).
            event_flag_window_seconds: events within this many seconds of ``ts_open`` (either
                direction) are surfaced in ``event_flags``.

        Returns:
            The :class:`CalendarSnapshot` valid as of this bar.
        """
        dt = datetime.fromtimestamp(ts_open, tz=UTC)
        today = dt.date()
        dow = dt.weekday()  # Monday=0 .. Sunday=6
        dom = dt.day

        is_new_day = self._prev_date is None or today != self._prev_date
        is_new_week = self._prev_date is None or _monday_of(today) != _monday_of(self._prev_date)
        is_month_boundary = self._prev_date is None or (
            (today.year, today.month) != (self._prev_date.year, self._prev_date.month)
        )

        # is_holiday reflects ONLY a confirmed CalendarEvent for this date (see module docstring):
        # a bar-feed gap alone cannot distinguish a genuine holiday from a data outage, so it is
        # never used to infer is_holiday. Day-count gaps are reported honestly via data_quality.
        is_holiday = today in self._confirmed_holidays
        is_weekend_gap = (
            is_new_day and self._prev_dow is not None and self._prev_dow == 4 and dow != 4
        )

        flags = [
            EventFlag(ts=e.ts, impact=e.impact, kind=e.kind)
            for e in self._events
            if abs(e.ts - ts_open) <= event_flag_window_seconds
        ]

        self._prev_date = today
        self._prev_dow = dow

        return CalendarSnapshot(
            date=today,
            dow=dow,
            dom=dom,
            is_new_day=is_new_day,
            is_new_week=is_new_week,
            is_month_boundary=is_month_boundary,
            is_holiday=is_holiday,
            is_weekend_gap=is_weekend_gap,
            dst_offset_seconds=0,
            event_flags=flags,
        )

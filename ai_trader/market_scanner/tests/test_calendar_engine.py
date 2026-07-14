"""Unit tests for ai_trader.market_scanner.calendar_engine."""

from ai_trader.market_scanner.calendar_engine import CalendarEngine
from ai_trader.market_scanner.types import CalendarEvent, ImpactLevel

_DAY = 86400
# 1970-01-01 (epoch 0) was a Thursday (weekday()==3).
_THURSDAY = 0
_FRIDAY = _THURSDAY + _DAY
_MONDAY = _FRIDAY + 3 * _DAY  # weekend gap: Fri -> Mon


def test_first_bar_is_always_new_boundaries() -> None:
    engine = CalendarEngine()
    snap = engine.update(_THURSDAY, event_flag_window_seconds=1800)
    assert snap.is_new_day and snap.is_new_week and snap.is_month_boundary
    assert snap.dow == 3  # Thursday


def test_normal_next_day_is_not_a_holiday_or_weekend_gap() -> None:
    engine = CalendarEngine()
    engine.update(_THURSDAY, 1800)
    snap = engine.update(_FRIDAY, 1800)
    assert snap.is_new_day
    assert not snap.is_holiday
    assert not snap.is_weekend_gap
    assert snap.dow == 4


def test_weekend_gap_friday_to_monday() -> None:
    engine = CalendarEngine()
    engine.update(_THURSDAY, 1800)
    engine.update(_FRIDAY, 1800)
    snap = engine.update(_MONDAY, 1800)
    assert snap.is_weekend_gap is True
    assert snap.is_holiday is False  # exactly the expected 3-day weekend gap, not a holiday
    assert snap.dow == 0


def test_unexplained_extra_gap_is_not_inferred_as_a_holiday() -> None:
    """A gap larger than the normal 3-day weekend gap (e.g. Thu -> Tue-after-next) looks identical
    whether caused by a genuine holiday or a data outage; is_holiday must stay False absent an
    explicit CalendarEvent (that honest ambiguity is reported via data_quality gaps instead)."""
    engine = CalendarEngine()
    engine.update(_THURSDAY, 1800)
    engine.update(_FRIDAY, 1800)
    # a 4-day gap instead of the normal 3-day weekend gap (e.g. Monday holiday, or an outage)
    snap = engine.update(_MONDAY + _DAY, 1800)
    assert snap.is_holiday is False


def test_explicit_holiday_event_confirms_is_holiday() -> None:
    engine = CalendarEngine()
    engine.update(_THURSDAY, 1800)
    engine.ingest_event(CalendarEvent(ts=_FRIDAY + 1000, impact=ImpactLevel.HIGH, kind="holiday"))
    snap = engine.update(_FRIDAY, 1800)
    assert snap.is_holiday is True


def test_is_new_week_only_on_monday_boundary_crossing() -> None:
    engine = CalendarEngine()
    engine.update(_THURSDAY, 1800)
    fri = engine.update(_FRIDAY, 1800)
    assert fri.is_new_week is False  # same week as Thursday
    mon = engine.update(_MONDAY, 1800)
    assert mon.is_new_week is True


def test_is_month_boundary() -> None:
    engine = CalendarEngine()
    jan_31 = 30 * _DAY  # 1970-01-31 (day index 30, 0-based from Jan 1 = day 0)
    feb_1 = jan_31 + _DAY
    engine.update(jan_31, 1800)
    snap = engine.update(feb_1, 1800)
    assert snap.is_month_boundary is True


def test_event_flags_within_window_only() -> None:
    engine = CalendarEngine()
    near_ts = 1000
    far_ts = 100_000
    engine.ingest_event(CalendarEvent(ts=near_ts, impact=ImpactLevel.MEDIUM, kind="cpi"))
    engine.ingest_event(CalendarEvent(ts=far_ts, impact=ImpactLevel.HIGH, kind="nfp"))
    snap = engine.update(ts_open=near_ts + 500, event_flag_window_seconds=600)
    kinds = {f.kind for f in snap.event_flags}
    assert kinds == {"cpi"}


def test_dst_offset_always_zero_documented() -> None:
    engine = CalendarEngine()
    snap = engine.update(_THURSDAY, 1800)
    assert snap.dst_offset_seconds == 0

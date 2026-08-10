"""`classify_gap` tests -- the CEO's own three categories, MAINTENANCE reused verbatim from
`code/gapfind.py`'s "mins <= 75 and hour in (20, 21)", WEEKEND checked separately and first,
UNEXPECTED as the only classification that is ever a problem."""

from __future__ import annotations

from ai_trader.live_signal_source.gap_classification import classify_gap
from ai_trader.live_signal_source.types import GapClassification

_M15 = 15 * 60


def _ts(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    import datetime

    return int(datetime.datetime(year, month, day, hour, minute, tzinfo=datetime.timezone.utc).timestamp())


def test_short_gap_starting_at_hour_20_is_maintenance() -> None:
    """The exact `code/gapfind.py` rule: duration <= 75 minutes AND the last-good-bar's own hour is
    20 or 21 UTC."""
    gap_start = _ts(2026, 7, 27, 20, 30)  # Monday, 20:30 UTC
    gap_end = gap_start + 60 * 60  # 60 minutes later -- within the 75-minute allowance
    assert classify_gap(gap_start, gap_end) == GapClassification.MAINTENANCE


def test_short_gap_starting_at_hour_21_is_maintenance() -> None:
    gap_start = _ts(2026, 7, 27, 21, 0)
    gap_end = gap_start + 45 * 60
    assert classify_gap(gap_start, gap_end) == GapClassification.MAINTENANCE


def test_gap_longer_than_75_minutes_at_hour_20_is_not_maintenance() -> None:
    """Duration is part of the verbatim rule -- exceeding 75 minutes disqualifies it even at the right
    hour."""
    gap_start = _ts(2026, 7, 27, 20, 0)
    gap_end = gap_start + 76 * 60
    assert classify_gap(gap_start, gap_end) == GapClassification.UNEXPECTED


def test_gap_at_the_wrong_hour_is_not_maintenance_even_if_short() -> None:
    gap_start = _ts(2026, 7, 27, 14, 0)  # mid-session, not the daily break window
    gap_end = gap_start + 30 * 60
    assert classify_gap(gap_start, gap_end) == GapClassification.UNEXPECTED


def test_a_gap_spanning_saturday_is_weekend() -> None:
    """Friday evening close to Sunday evening reopen -- the classic ~48h weekend closure, nowhere near
    the 75-minute maintenance allowance, and must not be classified UNEXPECTED."""
    gap_start = _ts(2026, 7, 24, 21, 0)  # Friday 21:00 UTC, 2026-07-24 is a Friday
    gap_end = _ts(2026, 7, 26, 21, 0)  # Sunday 21:00 UTC
    assert classify_gap(gap_start, gap_end) == GapClassification.WEEKEND


def test_a_gap_entirely_within_a_weekday_is_never_weekend() -> None:
    gap_start = _ts(2026, 7, 27, 10, 0)  # Monday
    gap_end = gap_start + 3 * 60 * 60
    assert classify_gap(gap_start, gap_end) != GapClassification.WEEKEND


def test_a_multi_hour_midweek_gap_is_unexpected() -> None:
    """Exactly the connection-drop scenario the CEO named -- not maintenance (wrong hour/too long), not
    weekend (no Saturday in range)."""
    gap_start = _ts(2026, 7, 28, 10, 0)  # Tuesday
    gap_end = gap_start + 4 * 60 * 60
    assert classify_gap(gap_start, gap_end) == GapClassification.UNEXPECTED


def test_weekend_takes_priority_even_if_it_happens_to_start_at_hour_20() -> None:
    gap_start = _ts(2026, 7, 24, 20, 0)  # Friday 20:00 UTC -- coincides with maintenance-hour
    gap_end = _ts(2026, 7, 26, 22, 0)  # Sunday, well past 75 minutes and spans a Saturday
    assert classify_gap(gap_start, gap_end) == GapClassification.WEEKEND


# -- EXTENDED_PAUSE, 2026-08-10: "131,5 ore etichetat WEEKEND. Mecanic corect, dar nu distinge pauza de
# operator... adauga o clasa: gol care depaseste durata maxima a unui weekend real." --


def test_a_real_length_weekend_is_still_weekend_not_extended_pause() -> None:
    """The empirically measured real-weekend length (49.25h) must stay WEEKEND -- the new class must
    never reclassify an ordinary weekend closure."""
    gap_start = _ts(2026, 7, 24, 23, 45)  # Friday close, the empirically measured real pattern
    gap_end = gap_start + int(49.25 * 3600)  # exactly the measured real-weekend duration
    assert classify_gap(gap_start, gap_end) == GapClassification.WEEKEND


def test_a_gap_just_under_the_72h_threshold_is_still_weekend() -> None:
    gap_start = _ts(2026, 7, 24, 21, 0)  # Friday
    gap_end = gap_start + 72 * 3600 - 1
    assert classify_gap(gap_start, gap_end) == GapClassification.WEEKEND


def test_a_gap_just_over_the_72h_threshold_is_extended_pause() -> None:
    gap_start = _ts(2026, 7, 24, 21, 0)  # Friday
    gap_end = gap_start + 72 * 3600 + 1
    assert classify_gap(gap_start, gap_end) == GapClassification.EXTENDED_PAUSE


def test_the_actual_six_day_operator_pause_is_extended_pause_not_weekend() -> None:
    """The exact real gap this feature was built for: a Tuesday-to-Monday, 131.5h operator pause. Spans
    multiple Saturdays, mechanically WEEKEND-shaped under the old rule, but must now be EXTENDED_PAUSE."""
    gap_start = _ts(2026, 8, 4, 22, 45)  # last bar before the 6-day pause
    gap_end = gap_start + int(131.5 * 3600)
    assert classify_gap(gap_start, gap_end) == GapClassification.EXTENDED_PAUSE


def test_a_long_gap_with_no_saturday_is_unexpected_not_extended_pause() -> None:
    """EXTENDED_PAUSE is checked only inside the `_spans_a_saturday` branch -- a long midweek-only gap
    (impossible on a real 24/5 market, but the classifier must still be exercised at the boundary) stays
    UNEXPECTED, never EXTENDED_PAUSE, since the two are never independent conditions."""
    gap_start = _ts(2026, 7, 27, 0, 0)  # Monday
    gap_end = gap_start + 73 * 3600  # long, but Monday 00:00 + 73h lands Thursday -- no Saturday crossed
    assert classify_gap(gap_start, gap_end) == GapClassification.UNEXPECTED

"""`day_boundary_start_utc` tests. Full numerical equivalence against `resample_ny.py`'s own pandas
computation was verified separately over all 83,279 real OANDA XAUUSD M15 bars (2023-01-01 through
2026-07-13, 7+ US DST transitions) -- zero mismatches (CEO instruction, 2026-08-03: "Verifica numeric
ancora contra resample_ny.py inainte sa te bazezi pe ea"). These tests pin specific, hand-checkable
facts from that verification, not a re-run of the full sweep."""

from __future__ import annotations

from datetime import datetime, timezone

from ai_trader.pdh_pdl_demo.day_index import day_boundary_start_utc


def _epoch(y: int, mo: int, d: int, h: int, mi: int = 0) -> int:
    return int(datetime(y, mo, d, h, mi, tzinfo=timezone.utc).timestamp())


def test_boundary_hour_standard_time_is_22_utc() -> None:
    """17:00 NY = 22:00 UTC when NY observes EST (standard time, e.g. mid-January)."""
    assert day_boundary_start_utc(_epoch(2024, 1, 15, 22, 0)) == _epoch(2024, 1, 15, 22, 0)


def test_boundary_hour_daylight_time_is_21_utc() -> None:
    """17:00 NY = 21:00 UTC when NY observes EDT (daylight time, e.g. mid-July)."""
    assert day_boundary_start_utc(_epoch(2024, 7, 15, 21, 0)) == _epoch(2024, 7, 15, 21, 0)


def test_a_bar_one_second_before_the_boundary_belongs_to_the_prior_day() -> None:
    boundary = _epoch(2024, 1, 15, 22, 0)
    assert day_boundary_start_utc(boundary - 1) == _epoch(2024, 1, 14, 22, 0)


def test_a_bar_at_the_boundary_belongs_to_the_new_day() -> None:
    boundary = _epoch(2024, 1, 15, 22, 0)
    assert day_boundary_start_utc(boundary) == boundary


def test_bars_across_the_spring_forward_transition_get_the_correct_new_boundary_hour() -> None:
    """US spring-forward 2024: 2024-03-10, 02:00 EST -> 03:00 EDT. Before: 22:00 UTC anchor (EST).
    After: 21:00 UTC anchor (EDT). Both confirmed against the real resample_ny.py sweep."""
    before = _epoch(2024, 3, 9, 22, 0)  # still EST
    after = _epoch(2024, 3, 11, 21, 0)  # already EDT
    assert day_boundary_start_utc(before) == before
    assert day_boundary_start_utc(after) == after


def test_bars_across_the_fall_back_transition_get_the_correct_new_boundary_hour() -> None:
    """US fall-back 2024: 2024-11-03, 02:00 EDT -> 01:00 EST."""
    before = _epoch(2024, 11, 2, 21, 0)  # still EDT
    after = _epoch(2024, 11, 4, 22, 0)  # already EST
    assert day_boundary_start_utc(before) == before
    assert day_boundary_start_utc(after) == after


def test_result_is_idempotent() -> None:
    ts = _epoch(2024, 6, 1, 12, 30)
    once = day_boundary_start_utc(ts)
    assert day_boundary_start_utc(once) == once

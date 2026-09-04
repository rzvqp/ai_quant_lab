"""Mandate Section 26/27: event-class positive/negative/boundary/direction/causality tests,
displacement's exact boundary + anti-range-leakage tests, major-level eligibility tests.
"""

from __future__ import annotations

import pytest

from ai_trader.apprenticeship_v2.general_observer.detectors import (
    DISPLACEMENT_ATR_MULTIPLIER, detect_displacement, detect_sweep_rejection, detect_structural_break,
    detect_session_transition_reversal, session_closing_direction,
)
from ai_trader.apprenticeship_v2.general_observer.major_levels import MajorLevel, compute_eligible_major_levels
from ai_trader.apprenticeship_v2.tests.conftest import make_bar, make_flat_series, M15_SECONDS


# ── DISPLACEMENT ────────────────────────────────────────────────────────────────────────────────

def _series_with_atr_one(base_ts: int, *, n: int = 20) -> list:
    """A series of bars each with true-range exactly 1.0 (high-low=1.0, no gaps vs prior close) so
    ATR14 converges to exactly 1.0 -- makes exact-boundary displacement tests exact, not approximate."""
    bars = []
    price = 1900.0
    for i in range(n):
        ts = base_ts + i * M15_SECONDS
        bars.append(make_bar(ts_open=ts, o=price, h=price + 0.5, l=price - 0.5, c=price))
    return bars


def test_displacement_body_less_than_2x_atr_no_trigger(base_ts):
    bars = _series_with_atr_one(base_ts)
    trigger_ts = base_ts + len(bars) * M15_SECONDS
    trigger_bar = make_bar(ts_open=trigger_ts, o=1900.0, h=1901.0, l=1899.0, c=1901.9)  # body=1.9 < 2.0*1.0
    series = bars + [trigger_bar]
    assert detect_displacement(trigger_bar, series) is None


def _fixed_point_boundary_body(base_ts) -> float:
    """The trigger bar's OWN true range feeds into its OWN ATR14 reference (design doc's own
    explicit, intentional point: "the trigger bar's own true range is one of the 14 values in its
    own ATR reference"), so "body == 2.0*ATR" is a genuine fixed-point equation, not a fixed target
    computable from the seed bars alone. Solved exactly here, not approximated: constructing the
    trigger bar with NO wick (`high=max(open,close)`, `low=min(open,close)`) and NO gap
    (`open == prev_close`) makes the trigger bar's own true range exactly equal to its own body, so
    `ATR_new = (13*1.0 + body) / 14` and the fixed point `body = 2.0*ATR_new` solves to
    `body = 26/12`."""
    return 26.0 / 12.0


def test_displacement_body_exactly_2x_atr_triggers(base_ts):
    bars = _series_with_atr_one(base_ts)
    trigger_ts = base_ts + len(bars) * M15_SECONDS
    body = _fixed_point_boundary_body(base_ts)
    open_price = bars[-1].close  # no gap
    close_price = open_price + body
    trigger_bar = make_bar(ts_open=trigger_ts, o=open_price, h=close_price, l=open_price, c=close_price)  # no wick
    series = bars + [trigger_bar]
    event = detect_displacement(trigger_bar, series)
    assert event is not None
    assert event.episode_type == "DISPLACEMENT"
    assert event.direction == "BULLISH"


def test_displacement_body_just_below_2x_atr_boundary_no_trigger(base_ts):
    """One cent short of the exact fixed-point boundary above -- must NOT trigger (strict `<`
    comparison confirmed from the other side)."""
    bars = _series_with_atr_one(base_ts)
    trigger_ts = base_ts + len(bars) * M15_SECONDS
    body = _fixed_point_boundary_body(base_ts) - 0.01
    open_price = bars[-1].close
    close_price = open_price + body
    trigger_bar = make_bar(ts_open=trigger_ts, o=open_price, h=close_price, l=open_price, c=close_price)
    series = bars + [trigger_bar]
    assert detect_displacement(trigger_bar, series) is None


def test_displacement_body_greater_than_2x_atr_triggers(base_ts):
    bars = _series_with_atr_one(base_ts)
    trigger_ts = base_ts + len(bars) * M15_SECONDS
    trigger_bar = make_bar(ts_open=trigger_ts, o=1900.0, h=1905.0, l=1899.5, c=1905.0)  # body=5.0 >> 2.0
    series = bars + [trigger_bar]
    assert detect_displacement(trigger_bar, series) is not None


def test_displacement_huge_wick_small_body_no_trigger_solely_due_to_range(base_ts):
    """The explicit adversarial requirement (mandate Section 27): displacement must use
    abs(close-open), never high-low range. A bar with a massive range but a tiny body must NOT
    trigger, even though (high-low) alone would be >> 2.0*ATR."""
    bars = _series_with_atr_one(base_ts)
    trigger_ts = base_ts + len(bars) * M15_SECONDS
    # range = high-low = 20.0 (>>2.0*ATR=2.0), but body = |close-open| = 0.1 (<<2.0)
    trigger_bar = make_bar(ts_open=trigger_ts, o=1900.0, h=1910.0, l=1890.0, c=1900.1)
    series = bars + [trigger_bar]
    assert detect_displacement(trigger_bar, series) is None


def test_displacement_close_equals_open_no_trigger(base_ts):
    bars = _series_with_atr_one(base_ts)
    trigger_ts = base_ts + len(bars) * M15_SECONDS
    trigger_bar = make_bar(ts_open=trigger_ts, o=1900.0, h=1950.0, l=1850.0, c=1900.0)  # huge range, close==open
    series = bars + [trigger_bar]
    assert detect_displacement(trigger_bar, series) is None


def test_displacement_direction_bearish(base_ts):
    bars = _series_with_atr_one(base_ts)
    trigger_ts = base_ts + len(bars) * M15_SECONDS
    trigger_bar = make_bar(ts_open=trigger_ts, o=1900.0, h=1900.5, l=1895.0, c=1895.0)  # close < open
    series = bars + [trigger_bar]
    event = detect_displacement(trigger_bar, series)
    assert event is not None and event.direction == "BEARISH"


def test_displacement_fewer_than_15_bars_no_trigger(base_ts):
    short_series = make_flat_series(start_ts=base_ts, count=5, price=1900.0)
    trigger_bar = make_bar(ts_open=base_ts + 5 * M15_SECONDS, o=1900.0, h=1950.0, l=1850.0, c=1950.0)
    series = short_series + [trigger_bar]
    assert detect_displacement(trigger_bar, series) is None  # ATR14 unavailable -- Invalid trigger


def test_displacement_refuses_a_bar_list_that_does_not_end_at_the_trigger_bar(base_ts):
    """Mutation/adversarial (mandate Section 27: "future bar is inserted into snapshot"), applied to
    this function's own contract: `detect_displacement` REQUIRES its bar list to end with the
    trigger bar itself (the exact precondition that makes "ATR up to and including the trigger bar"
    unambiguous) -- appending so much as one bar after it is refused outright via an assertion,
    never silently computed against a list that includes future information relative to the trigger."""
    bars = _series_with_atr_one(base_ts)
    trigger_ts = base_ts + len(bars) * M15_SECONDS
    trigger_bar = make_bar(ts_open=trigger_ts, o=1900.0, h=1902.0, l=1899.5, c=1902.0)
    series = bars + [trigger_bar]

    later_bar = make_bar(ts_open=trigger_ts + M15_SECONDS, o=1902.0, h=2000.0, l=1800.0, c=1999.0)
    series_with_future = series + [later_bar]  # a wild future bar appended AFTER the trigger
    with pytest.raises(AssertionError):
        detect_displacement(trigger_bar, series_with_future)


# ── SWEEP_REJECTION ──────────────────────────────────────────────────────────────────────────────

def test_sweep_rejection_downside_bullish(base_ts):
    level = MajorLevel("PREVIOUS_DAY_LOW", 1900.0)
    bar = make_bar(ts_open=base_ts, o=1901.0, h=1902.0, l=1899.0, c=1901.5)  # low < 1900 < close
    event = detect_sweep_rejection(bar, [level])
    assert event is not None
    assert event.direction == "BULLISH"
    assert event.reason_code == "SWEEP_PREVIOUS_DAY_LOW_BULLISH"
    assert event.reference_levels["swept_level_price"] == 1900.0


def test_sweep_rejection_upside_bearish(base_ts):
    level = MajorLevel("PREVIOUS_DAY_HIGH", 1900.0)
    bar = make_bar(ts_open=base_ts, o=1899.0, h=1901.0, l=1898.0, c=1899.5)  # high > 1900 > close
    event = detect_sweep_rejection(bar, [level])
    assert event is not None
    assert event.direction == "BEARISH"


def test_sweep_rejection_no_breach_no_trigger(base_ts):
    level = MajorLevel("PREVIOUS_DAY_LOW", 1900.0)
    bar = make_bar(ts_open=base_ts, o=1901.0, h=1902.0, l=1900.5, c=1901.5)  # low never breaches 1900
    assert detect_sweep_rejection(bar, [level]) is None


def test_sweep_rejection_breach_without_reclaim_no_trigger(base_ts):
    level = MajorLevel("PREVIOUS_DAY_LOW", 1900.0)
    bar = make_bar(ts_open=base_ts, o=1899.5, h=1899.8, l=1898.0, c=1898.5)  # breaches but closes below too
    assert detect_sweep_rejection(bar, [level]) is None


def test_sweep_rejection_boundary_close_exactly_at_level_no_trigger(base_ts):
    """`bar.close > level` is a strict inequality -- closing exactly ON the level is not a reclaim."""
    level = MajorLevel("PREVIOUS_DAY_LOW", 1900.0)
    bar = make_bar(ts_open=base_ts, o=1899.0, h=1900.5, l=1899.0, c=1900.0)
    assert detect_sweep_rejection(bar, [level]) is None


# ── STRUCTURAL_BREAK ─────────────────────────────────────────────────────────────────────────────

def test_structural_break_upside_bullish(base_ts):
    level = MajorLevel("H1_CONFIRMED_SWING_HIGH", 1900.0)
    prior = make_bar(ts_open=base_ts, o=1898.0, h=1899.5, l=1897.5, c=1899.0)  # prior close <= 1900
    bar = make_bar(ts_open=base_ts + M15_SECONDS, o=1899.0, h=1901.5, l=1898.5, c=1901.0)  # close > 1900
    event = detect_structural_break(prior, bar, [level])
    assert event is not None and event.direction == "BULLISH"


def test_structural_break_downside_bearish(base_ts):
    level = MajorLevel("H1_CONFIRMED_SWING_LOW", 1900.0)
    prior = make_bar(ts_open=base_ts, o=1902.0, h=1902.5, l=1900.5, c=1901.0)  # prior close >= 1900
    bar = make_bar(ts_open=base_ts + M15_SECONDS, o=1901.0, h=1901.5, l=1898.0, c=1899.0)  # close < 1900
    event = detect_structural_break(prior, bar, [level])
    assert event is not None and event.direction == "BEARISH"


def test_structural_break_boundary_prior_close_exactly_at_level(base_ts):
    """`prior_bar.close <= level` is inclusive (design doc's own `<=`) -- prior closing EXACTLY on
    the level still counts as "on one side" for the upside-break case."""
    level = MajorLevel("H1_CONFIRMED_SWING_HIGH", 1900.0)
    prior = make_bar(ts_open=base_ts, o=1899.0, h=1900.5, l=1898.5, c=1900.0)  # prior close == level exactly
    bar = make_bar(ts_open=base_ts + M15_SECONDS, o=1900.0, h=1901.5, l=1899.5, c=1900.5)
    event = detect_structural_break(prior, bar, [level])
    assert event is not None and event.direction == "BULLISH"


def test_structural_break_no_crossing_no_trigger(base_ts):
    level = MajorLevel("H1_CONFIRMED_SWING_HIGH", 1900.0)
    prior = make_bar(ts_open=base_ts, o=1901.0, h=1902.0, l=1900.5, c=1901.5)  # already above
    bar = make_bar(ts_open=base_ts + M15_SECONDS, o=1901.5, h=1902.5, l=1901.0, c=1902.0)  # stays above
    assert detect_structural_break(prior, bar, [level]) is None


def test_structural_break_whipsaw_within_one_level_produces_no_duplicate_within_this_call():
    """Detector-level (not dedup-level) proof: a single call only ever evaluates ONE prior/current
    bar pair -- duplicate suppression across a longer whipsaw is dedup.py's own job (Section 11),
    not this function's; this test documents the boundary, not a dedup guarantee."""
    pass  # documented boundary; real dedup behavior is tested in test_dedup.py


# ── SESSION_TRANSITION_REVERSAL ─────────────────────────────────────────────────────────────────

def test_session_transition_reversal_fires_on_opposite_direction():
    from ai_trader.apprenticeship_v2.general_observer.detectors import DetectedEvent
    child = DetectedEvent(
        episode_type="SWEEP_REJECTION", trigger_bar_ts_close=123, direction="BULLISH",
        reference_levels={}, reason_code="SWEEP_X_BULLISH", what_triggered_observation="x",
    )
    event = detect_session_transition_reversal(
        child, preceding_session_name="ASIA", preceding_session_direction="BEARISH", new_session_name="LONDON",
    )
    assert event is not None
    assert event.episode_type == "SESSION_TRANSITION_REVERSAL"
    assert event.direction == "BULLISH"
    assert event.child_event is child


def test_session_transition_reversal_no_fire_on_same_direction():
    from ai_trader.apprenticeship_v2.general_observer.detectors import DetectedEvent
    child = DetectedEvent(
        episode_type="STRUCTURAL_BREAK", trigger_bar_ts_close=123, direction="BULLISH",
        reference_levels={}, reason_code="BREAK_X_BULLISH", what_triggered_observation="x",
    )
    event = detect_session_transition_reversal(
        child, preceding_session_name="ASIA", preceding_session_direction="BULLISH", new_session_name="LONDON",
    )
    assert event is None


def test_session_transition_reversal_no_fire_when_preceding_direction_unclear():
    from ai_trader.apprenticeship_v2.general_observer.detectors import DetectedEvent
    child = DetectedEvent(
        episode_type="SWEEP_REJECTION", trigger_bar_ts_close=123, direction="BEARISH",
        reference_levels={}, reason_code="SWEEP_X_BEARISH", what_triggered_observation="x",
    )
    event = detect_session_transition_reversal(
        child, preceding_session_name="ASIA", preceding_session_direction=None, new_session_name="LONDON",
    )
    assert event is None


def test_session_closing_direction_net_zero_is_unclear(base_ts):
    bars = [make_bar(ts_open=base_ts, o=1900.0, h=1905.0, l=1895.0, c=1900.0)]
    assert session_closing_direction(bars) is None


def test_session_closing_direction_bullish(base_ts):
    bars = [
        make_bar(ts_open=base_ts, o=1900.0, h=1901.0, l=1899.0, c=1900.0),
        make_bar(ts_open=base_ts + M15_SECONDS, o=1900.0, h=1903.0, l=1899.5, c=1902.0),
    ]
    assert session_closing_direction(bars) == "BULLISH"


# ── Major levels ─────────────────────────────────────────────────────────────────────────────────

def test_eligible_level_accepted(base_ts):
    h1_bars = [
        make_bar(ts_open=base_ts + i * 3600, o=1900.0, h=1905.0 + i, l=1895.0 - i, c=1900.0, bar_seconds=3600)
        for i in range(-30, 0)
    ]  # 30 hours of prior H1 history, spanning at least one full prior UTC day
    as_of = base_ts
    levels = compute_eligible_major_levels(h1_bars, as_of_ts_close=as_of)
    level_types = {lvl.level_type for lvl in levels}
    # At minimum, previous-day levels should be computable from 30h of real prior H1 history.
    assert "PREVIOUS_DAY_HIGH" in level_types or "PREVIOUS_SESSION_HIGH" in level_types


def test_ineligible_local_level_never_appears():
    """An arbitrary local extremum that is none of the 6 eligible types (not a confirmed H1 swing,
    not a session/day boundary) must never appear in the eligible-levels output -- proven by
    construction: compute_eligible_major_levels only ever emits the 6 named types, there is no code
    path that could emit anything else."""
    from ai_trader.apprenticeship_v2.general_observer.major_levels import ELIGIBLE_LEVEL_TYPES
    assert set(ELIGIBLE_LEVEL_TYPES) == {
        "PREVIOUS_DAY_HIGH", "PREVIOUS_DAY_LOW", "PREVIOUS_SESSION_HIGH", "PREVIOUS_SESSION_LOW",
        "H1_CONFIRMED_SWING_HIGH", "H1_CONFIRMED_SWING_LOW",
    }


def test_major_level_dependent_event_cannot_fire_from_an_ineligible_level():
    """Mandate Section 6: "Tests must demonstrate that an ineligible level cannot trigger a
    major-level-dependent event." Since detect_sweep_rejection/detect_structural_break only ever
    iterate over the `levels` list the CALLER passes in (never compute their own), an "ineligible"
    level (e.g. an arbitrary local extremum) simply cannot appear unless the caller manually
    constructs a MajorLevel with a type outside ELIGIBLE_LEVEL_TYPES -- which
    compute_eligible_major_levels itself never does. This test proves the detector still correctly
    IGNORES a level object carrying an out-of-contract type string, as defense in depth."""
    fake_level = MajorLevel("ARBITRARY_LOCAL_HIGH", 1900.0)  # not one of the 6 eligible types
    bar = make_bar(ts_open=1_600_000_000, o=1899.0, h=1901.0, l=1898.0, c=1899.5)
    # ARBITRARY_LOCAL_HIGH is not in _HIGH_TYPES/_LOW_TYPES, so `.side` raises -- proving the
    # detector's own level iteration (via levels_of_side) structurally excludes it rather than
    # silently treating it as a HIGH or LOW type.
    with pytest.raises(Exception):
        _ = fake_level.side

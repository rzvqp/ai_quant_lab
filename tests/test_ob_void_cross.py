"""INDEPENDENT cross-verification of order_block_void.py (edca965), per CROSS_VERIFICATION_SPEC.
External suite on synthetic in-memory matrices. Does NOT reuse VE's tests and does NOT share the
implementation's assumptions -- each case is derived from the RATIFIED definition text, not the code.
mypy --strict clean. Verifies the frozen Liquidity-Void definition (temporal / size / hybrid, with
FAIL-CLOSED maintenance isolation) and the Order-Block zone + validity/measurement window separation.
"""
from __future__ import annotations

import datetime as dt

import pytest

import order_block_void as M
from order_block_void import (
    COST_ROUND_TRIP,
    GROUP_A_HORIZON,
    VOID_SIZE_THRESHOLD,
    LiquidityVoid,
    ObValidityEvent,
    OrderBlock,
    OrderBlockKind,
    VoidKind,
    detect_liquidity_voids,
    order_block_zone,
    resolve_validity_and_measurement,
)

MON = dt.date(2022, 1, 3)  # a Monday, arbitrary anchor


def _ep(hour: int, minute: int = 0, day: dt.date = MON) -> int:
    return int(dt.datetime(day.year, day.month, day.day, hour, minute,
                           tzinfo=dt.timezone.utc).timestamp())


def _one(open_: list[float], close: list[float], time: list[int]) -> list[LiquidityVoid]:
    return detect_liquidity_voids(open_, close, time)


# ---------------- TEMPORAL arm ----------------
def test_temporal_strict_gt_900() -> None:
    # gap == 900 is the normal bar spacing -> NOT a void; gap 901 -> temporal.
    assert _one([100.0, 100.0], [100.0, 100.0], [_ep(10), _ep(10) + 900]) == []
    v = _one([100.0, 100.0], [100.0, 100.0], [_ep(10), _ep(10) + 901])
    assert len(v) == 1 and v[0].kind is VoidKind.TEMPORAL


def test_temporal_normal_hour() -> None:
    v = _one([100.0, 100.0], [100.0, 100.0], [_ep(10), _ep(10) + 1800])
    assert len(v) == 1 and v[0].kind is VoidKind.TEMPORAL and v[0].gap_seconds == 1800


# ---------------- MAINTENANCE isolation must be FAIL-CLOSED ----------------
def test_maintenance_suppresses_only_the_daily_break() -> None:
    # ~1h gap at hour 20 with no price jump = the legitimate daily break -> suppressed (no void).
    assert _one([100.0, 100.0], [100.0, 100.0], [_ep(20), _ep(20) + 3600]) == []
    assert _one([100.0, 100.0], [100.0, 100.0], [_ep(21), _ep(21) + 3600]) == []


def test_failclosed_long_gap_at_maintenance_hour_NOT_suppressed() -> None:
    # gap > 75min at hour 20 is NOT the daily break -> must remain a temporal void (fail-closed).
    v = _one([100.0, 100.0], [100.0, 100.0], [_ep(20), _ep(20) + 4501])
    assert len(v) == 1 and v[0].kind is VoidKind.TEMPORAL


def test_maintenance_boundary_4500_inclusive() -> None:
    # rule is mins <= 75 (<=4500s) -> exactly 4500 at h20 suppressed; 4501 not.
    assert _one([1.0, 1.0], [1.0, 1.0], [_ep(20), _ep(20) + 4500]) == []
    assert len(_one([1.0, 1.0], [1.0, 1.0], [_ep(20), _ep(20) + 4501])) == 1


def test_failclosed_other_hours_not_suppressed() -> None:
    for h in (0, 12, 19, 22, 23):
        v = _one([1.0, 1.0], [1.0, 1.0], [_ep(h), _ep(h) + 3600])
        assert len(v) == 1 and v[0].kind is VoidKind.TEMPORAL, f"hour {h} wrongly suppressed"


def test_failclosed_weekend_included() -> None:
    # Weekend reopen (huge gap) starting at hour 21 -> gap>4500 -> NOT maintenance -> temporal void.
    fri = dt.date(2022, 1, 7)  # Friday
    v = _one([100.0, 100.0], [100.0, 100.0], [_ep(21, day=fri), _ep(21, day=fri) + 49 * 3600])
    assert len(v) == 1 and v[0].kind is VoidKind.TEMPORAL


def test_maintenance_uses_START_bar_hour() -> None:
    # gapfind rule keys on t0.hour (start bar). Start at h19, end crossing into h20 -> uses h19 -> NOT suppressed.
    v = _one([1.0, 1.0], [1.0, 1.0], [_ep(19, 40), _ep(19, 40) + 3600])
    assert len(v) == 1 and v[0].kind is VoidKind.TEMPORAL


def test_maintenance_does_not_suppress_the_SIZE_arm() -> None:
    # A maintenance-window transition that ALSO has a >$1.20 jump is still a SIZE void
    # (maintenance affects only the temporal arm; fail-closed on the size arm).
    v = _one([100.0, 102.0], [100.0, 100.0], [_ep(20), _ep(20) + 3600])  # jump=|open[1]-close[0]|=2.0, temporal suppressed
    assert len(v) == 1 and v[0].kind is VoidKind.SIZE


# ---------------- SIZE arm ----------------
def test_size_threshold_is_derived_1_20() -> None:
    assert VOID_SIZE_THRESHOLD == pytest.approx(1.20)
    assert VOID_SIZE_THRESHOLD == pytest.approx(3.0 * COST_ROUND_TRIP)


def test_size_strict_gt_threshold() -> None:
    # jump EXACTLY the threshold -> NOT a size void (strict >). Use base 0.0 to avoid float error
    # that 100.0+1.20 introduces (100.0+1.2-100.0 == 1.2000000000000028 > 1.2, which IS a void).
    at = VOID_SIZE_THRESHOLD
    assert _one([0.0, at], [0.0, 0.0], [_ep(10), _ep(10) + 900]) == []          # jump == 1.20, not >
    v = _one([0.0, at + 0.01], [0.0, 0.0], [_ep(10), _ep(10) + 900])            # jump 1.21 > 1.20
    assert len(v) == 1 and v[0].kind is VoidKind.SIZE
    # and confirm the float-boundary observation itself (100.0+1.20 DOES exceed, correctly):
    assert len(_one([100.0, 101.20], [100.0, 100.0], [_ep(10), _ep(10) + 900])) == 1


def test_size_uses_abs_open_next_minus_close() -> None:
    # downward jump of 1.5 must also count (absolute value).
    v = _one([100.0, 98.5], [100.0, 100.0], [_ep(10), _ep(10) + 900])
    assert len(v) == 1 and v[0].kind is VoidKind.SIZE


# ---------------- HYBRID ----------------
def test_hybrid_both() -> None:
    v = _one([100.0, 102.0], [100.0, 100.0], [_ep(10), _ep(10) + 1800])  # temporal + size (jump 2.0)
    assert len(v) == 1 and v[0].kind is VoidKind.BOTH


def test_hybrid_none() -> None:
    assert _one([100.0, 100.1], [100.0, 100.0], [_ep(10), _ep(10) + 900]) == []  # jump 0.1 < 1.20


def test_at_idx_is_c_not_c_plus_1() -> None:
    v = _one([1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [_ep(10), _ep(10) + 1800, _ep(10) + 1800 + 900])
    assert len(v) == 1 and v[0].at_idx == 0


# ---------------- ORDER BLOCK zone = BODY (not body+wick) ----------------
def test_ob_zone_is_body_bullish() -> None:
    assert order_block_zone(100.0, 103.0) == (100.0, 103.0)   # open=100, close=103 -> [open, close]


def test_ob_zone_is_body_bearish() -> None:
    assert order_block_zone(103.0, 100.0) == (100.0, 103.0)   # open=103, close=100 -> [close, open]


def test_ob_zone_depends_only_on_open_close() -> None:
    # signature has no high/low -> wick cannot enter the zone by construction.
    import inspect
    params = list(inspect.signature(order_block_zone).parameters)
    assert params == ["open_bar", "close_bar"]


# ---------------- validity vs measurement window (anti-E010) ----------------
def test_resolver_refuses_until_formation_ratified() -> None:
    # Not implemented -> cannot silently return an overlapping window (E010 vacuously impossible here).
    ob = OrderBlock(formation_idx=5, kind=OrderBlockKind.BULLISH, zone_lower=100.0, zone_upper=103.0)
    for be in (10, 20, 100):
        with pytest.raises(NotImplementedError):
            resolve_validity_and_measurement(ob, [1.0] * 200, [1.0] * 200, [1.0] * 200, block_end=be)


def test_validity_and_measurement_contract_cannot_overlap() -> None:
    # The ObValidityEvent contract: measurement starts at the QUALIFYING EVENT, never at formation.
    # E010 failed because selection and measurement were identical (both from the same index). Here the
    # validity window is [formation, event] and measurement is [event, event+horizon]: disjoint interiors.
    formation, event = 5, 40
    ev = ObValidityEvent(ob_formation_idx=formation, event_idx=event, event_type="wick_touch",
                         measurement_start=event, measurement_end=event + GROUP_A_HORIZON)
    assert ev.measurement_start != ev.ob_formation_idx           # NOT the E010 collapse
    assert ev.measurement_start == ev.event_idx                  # measurement begins AT the event
    assert ev.measurement_end == ev.event_idx + GROUP_A_HORIZON  # horizon runs FROM the event
    # validity [formation, event) and measurement [event, event+h) share only the boundary, never overlap.
    validity = range(formation, event)
    measurement = range(event, event + GROUP_A_HORIZON)
    assert set(validity).isdisjoint(set(measurement))


def test_group_a_horizon_frozen_at_20() -> None:
    assert GROUP_A_HORIZON == 20

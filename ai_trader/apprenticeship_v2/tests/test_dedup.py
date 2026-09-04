"""Mandate Section 26 (Dedup / Lessons): multiple classes same move -> one underlying_move_id; same
class duplicate suppressed; restart duplicate suppressed; independent (later, price-continuity-
broken) move allowed.
"""

from __future__ import annotations

import json

from ai_trader.apprenticeship_v2.general_observer.dedup import (
    compute_underlying_move_id, is_duplicate, per_class_dedup_key,
)
from ai_trader.apprenticeship_v2.general_observer.detectors import DetectedEvent
from ai_trader.apprenticeship_v2.tests.conftest import make_bar, M15_SECONDS


def _sweep_event(ts_close: int, level_price: float = 1900.0) -> DetectedEvent:
    return DetectedEvent(
        episode_type="SWEEP_REJECTION", trigger_bar_ts_close=ts_close, direction="BULLISH",
        reference_levels={"swept_level_type": "PREVIOUS_DAY_LOW", "swept_level_price": level_price, "breach_extreme": level_price - 1, "reclaim_close": level_price + 1},
        reason_code="SWEEP_PREVIOUS_DAY_LOW_BULLISH", what_triggered_observation="x",
    )


def _displacement_event(ts_close: int, open_price: float = 1900.0) -> DetectedEvent:
    return DetectedEvent(
        episode_type="DISPLACEMENT", trigger_bar_ts_close=ts_close, direction="BULLISH",
        reference_levels={"open": open_price, "high": open_price + 5, "low": open_price - 1, "close": open_price + 5, "atr14_reference_value": 1.0, "displacement_atr_multiplier": 2.0, "displacement_magnitude_metric": "ABS_CLOSE_MINUS_OPEN"},
        reason_code="DISPLACEMENT_BULLISH", what_triggered_observation="x",
    )


def _row_for(event: DetectedEvent, underlying_move_id: str) -> dict:
    return {
        "episode_type": event.episode_type, "frozen_at_bar_ts": str(event.trigger_bar_ts_close),
        "directional_hypothesis": event.direction, "reference_levels_json": json.dumps(event.reference_levels),
        "underlying_move_id": underlying_move_id,
    }


def test_multiple_classes_same_move_share_one_underlying_move_id(base_ts):
    """Sweep, then a displacement shortly after (same direction, no adverse close in between) --
    must join the SAME underlying_move_id, not start a second family."""
    sweep = _sweep_event(base_ts)
    existing = [_row_for(sweep, "MOVE-A")]
    m15_bars = [make_bar(ts_open=base_ts + i * M15_SECONDS, o=1901, h=1902, l=1900.5, c=1901.5) for i in range(1, 4)]

    displacement_ts = base_ts + 3 * M15_SECONDS
    displacement = _displacement_event(displacement_ts, open_price=1901.5)
    move_id = compute_underlying_move_id(displacement, existing_general_episode_rows=existing, m15_bars_since_earliest_candidate=m15_bars)
    assert move_id == "MOVE-A"


def test_same_class_exact_duplicate_suppressed(base_ts):
    sweep = _sweep_event(base_ts)
    row = _row_for(sweep, "MOVE-A")
    # A second, identical sweep (same level/price/direction) within the same family.
    second_sweep = _sweep_event(base_ts + M15_SECONDS)
    assert is_duplicate(second_sweep, underlying_move_id="MOVE-A", existing_general_episode_rows=[row]) is True


def test_restart_duplicate_suppressed_via_fresh_ledger_read(base_ts):
    """No in-memory state is used anywhere in is_duplicate -- the SAME ledger rows passed in after a
    simulated "restart" (a fresh list built from scratch, not a persisted Python object) produce the
    identical duplicate verdict."""
    sweep = _sweep_event(base_ts)
    row = json.loads(json.dumps(_row_for(sweep, "MOVE-A")))  # round-trip through JSON, simulating a restart reload
    second_sweep = _sweep_event(base_ts + M15_SECONDS)
    assert is_duplicate(second_sweep, underlying_move_id="MOVE-A", existing_general_episode_rows=[row]) is True


def test_independent_move_allowed_after_price_continuity_breaks(base_ts):
    """A displacement bar AFTER price has closed back through the sweep's own origin (adverse
    direction) must NOT join the earlier family -- a genuinely new, independent move."""
    sweep = _sweep_event(base_ts, level_price=1900.0)
    existing = [_row_for(sweep, "MOVE-A")]
    # Price closes back BELOW 1900 (the BULLISH move's origin) -- breaks continuity.
    adverse_bar = make_bar(ts_open=base_ts + M15_SECONDS, o=1901, h=1901.5, l=1898, c=1898.5)
    m15_bars = [adverse_bar]

    later_displacement = _displacement_event(base_ts + 2 * M15_SECONDS, open_price=1898.5)
    move_id = compute_underlying_move_id(later_displacement, existing_general_episode_rows=existing, m15_bars_since_earliest_candidate=m15_bars)
    assert move_id != "MOVE-A"
    assert move_id.startswith("MOVE-")


def test_independent_move_allowed_after_h8_window_elapses(base_ts):
    """A same-direction, price-continuous candidate that arrives AFTER the H8 (32-M15-bar) window
    has fully elapsed starts a new family -- the window closes on time, not indefinitely."""
    sweep = _sweep_event(base_ts, level_price=1900.0)
    existing = [_row_for(sweep, "MOVE-A")]
    too_late_ts = base_ts + 33 * M15_SECONDS  # one bar past the 32-bar window
    later_displacement = _displacement_event(too_late_ts, open_price=1905.0)
    move_id = compute_underlying_move_id(later_displacement, existing_general_episode_rows=existing, m15_bars_since_earliest_candidate=[])
    assert move_id != "MOVE-A"


def test_different_direction_never_shares_a_family(base_ts):
    sweep = _sweep_event(base_ts)  # BULLISH
    existing = [_row_for(sweep, "MOVE-A")]
    bearish_displacement = DetectedEvent(
        episode_type="DISPLACEMENT", trigger_bar_ts_close=base_ts + M15_SECONDS, direction="BEARISH",
        reference_levels={"open": 1900.0, "high": 1900.5, "low": 1895.0, "close": 1895.0, "atr14_reference_value": 1.0, "displacement_atr_multiplier": 2.0, "displacement_magnitude_metric": "ABS_CLOSE_MINUS_OPEN"},
        reason_code="DISPLACEMENT_BEARISH", what_triggered_observation="x",
    )
    move_id = compute_underlying_move_id(bearish_displacement, existing_general_episode_rows=existing, m15_bars_since_earliest_candidate=[])
    assert move_id != "MOVE-A"


def test_per_class_dedup_key_shape():
    sweep = _sweep_event(1_600_000_000)
    key = per_class_dedup_key(sweep, underlying_move_id="MOVE-X")
    assert key == ("SWEEP_REJECTION", "PREVIOUS_DAY_LOW", 1900.0, "BULLISH")

    disp = _displacement_event(1_600_000_000)
    key2 = per_class_dedup_key(disp, underlying_move_id="MOVE-X")
    assert key2 == ("DISPLACEMENT", "BULLISH", "MOVE-X")

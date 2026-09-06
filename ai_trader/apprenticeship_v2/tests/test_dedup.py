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
    """Corrected per Red Team RT-GENERAL-OBSERVER-V1-1-FINAL-AUDIT-001 (Blocker 2): SWEEP_REJECTION's
    key now includes `underlying_move_id`, exactly like DISPLACEMENT already did -- the fix for
    "same level, new independent move must be allowed" is precisely that the move_id component now
    differs across families, even though level_type/level_price/direction stay identical."""
    sweep = _sweep_event(1_600_000_000)
    key = per_class_dedup_key(sweep, underlying_move_id="MOVE-X")
    assert key == ("SWEEP_REJECTION", "PREVIOUS_DAY_LOW", 1900.0, "BULLISH", "MOVE-X")

    disp = _displacement_event(1_600_000_000)
    key2 = per_class_dedup_key(disp, underlying_move_id="MOVE-X")
    assert key2 == ("DISPLACEMENT", "BULLISH", "MOVE-X")


# ---- Red Team RT-GENERAL-OBSERVER-V1-1-FINAL-AUDIT-001, Blocker 2 -- end-to-end sweep/break dedup
# semantics: compute_underlying_move_id + is_duplicate used TOGETHER, exactly as episode_builder.py
# uses them, not is_duplicate alone with a hand-picked move_id. This is the shape of test that would
# have caught the original defect (a hardcoded, always-matching move_id on both sides never exercises
# the "two different families" case at all).

def test_duplicate_event_inside_same_move_suppressed_end_to_end(base_ts):
    sweep = _sweep_event(base_ts, level_price=1900.0)
    existing = [_row_for(sweep, "MOVE-A")]
    # Same level, shortly after, price stays continuous (no adverse close) -- still the same move.
    m15_bars = [make_bar(ts_open=base_ts + M15_SECONDS, o=1900.5, h=1901, l=1900, c=1900.8)]
    second_sweep = _sweep_event(base_ts + M15_SECONDS, level_price=1900.0)
    move_id = compute_underlying_move_id(second_sweep, existing_general_episode_rows=existing, m15_bars_since_earliest_candidate=m15_bars)
    assert move_id == "MOVE-A"  # joined the existing, still-open family
    assert is_duplicate(second_sweep, underlying_move_id=move_id, existing_general_episode_rows=existing) is True


def test_repeated_same_level_later_but_same_move_still_suppressed(base_ts):
    """Several bars later, still within the H8 window, still no adverse close -- the family is still
    open, so a re-trigger of the identical level/price/direction remains a duplicate."""
    sweep = _sweep_event(base_ts, level_price=1900.0)
    existing = [_row_for(sweep, "MOVE-A")]
    m15_bars = [make_bar(ts_open=base_ts + i * M15_SECONDS, o=1901, h=1902, l=1900.2, c=1901.5) for i in range(1, 10)]
    later_sweep = _sweep_event(base_ts + 10 * M15_SECONDS, level_price=1900.0)
    move_id = compute_underlying_move_id(later_sweep, existing_general_episode_rows=existing, m15_bars_since_earliest_candidate=m15_bars)
    assert move_id == "MOVE-A"
    assert is_duplicate(later_sweep, underlying_move_id=move_id, existing_general_episode_rows=existing) is True


def test_same_level_revisited_after_move_closure_is_a_new_episode(base_ts):
    """THE key Blocker 2 case: the level is swept, price fully round-trips through the origin
    (closing the family), and MUCH later the identical level/price/direction is swept again -- a
    genuinely new, independent interaction. Must NOT be suppressed, even though level_type/
    level_price/direction are byte-identical to the first sweep."""
    sweep = _sweep_event(base_ts, level_price=1900.0)
    existing = [_row_for(sweep, "MOVE-A")]
    # Price closes back BELOW 1900 (adverse to the BULLISH move) -- the family closes here.
    adverse_bar = make_bar(ts_open=base_ts + M15_SECONDS, o=1899, h=1899.5, l=1897, c=1897.5)
    m15_bars = [adverse_bar]

    new_sweep = _sweep_event(base_ts + 2 * M15_SECONDS, level_price=1900.0)  # identical level/price/direction
    move_id = compute_underlying_move_id(new_sweep, existing_general_episode_rows=existing, m15_bars_since_earliest_candidate=m15_bars)
    assert move_id != "MOVE-A"  # a new, independent family
    assert is_duplicate(new_sweep, underlying_move_id=move_id, existing_general_episode_rows=existing) is False  # NOT suppressed


def test_restart_preserves_identical_new_independent_move_behavior(base_ts):
    """Restart-safety for the Blocker 2 fix specifically: the SAME scenario as above, with the
    existing row round-tripped through JSON (simulating a fresh ledger reload after a restart)
    produces the identical, non-suppressed verdict."""
    sweep = _sweep_event(base_ts, level_price=1900.0)
    existing = [json.loads(json.dumps(_row_for(sweep, "MOVE-A")))]
    adverse_bar = make_bar(ts_open=base_ts + M15_SECONDS, o=1899, h=1899.5, l=1897, c=1897.5)
    m15_bars = [adverse_bar]
    new_sweep = _sweep_event(base_ts + 2 * M15_SECONDS, level_price=1900.0)
    move_id = compute_underlying_move_id(new_sweep, existing_general_episode_rows=existing, m15_bars_since_earliest_candidate=m15_bars)
    assert move_id != "MOVE-A"
    assert is_duplicate(new_sweep, underlying_move_id=move_id, existing_general_episode_rows=existing) is False


def test_lesson_evidence_sees_independent_moves_separately(base_ts):
    """The whole point of binding dedup to underlying_move_id: two genuinely independent sweeps of
    the same level (separated by a closed family) must carry two DIFFERENT underlying_move_id
    values, so lesson-vote counting (one vote per move_id) treats them as two independent
    observations, never collapsing them into one."""
    sweep = _sweep_event(base_ts, level_price=1900.0)
    existing = [_row_for(sweep, "MOVE-A")]
    adverse_bar = make_bar(ts_open=base_ts + M15_SECONDS, o=1899, h=1899.5, l=1897, c=1897.5)
    new_sweep = _sweep_event(base_ts + 2 * M15_SECONDS, level_price=1900.0)
    move_id_b = compute_underlying_move_id(new_sweep, existing_general_episode_rows=existing, m15_bars_since_earliest_candidate=[adverse_bar])
    assert move_id_b != "MOVE-A"
    assert len({"MOVE-A", move_id_b}) == 2  # two distinct families -> two distinct lesson-evidence votes

"""Mandate item 1 (STRUCTURAL_FINAL resolution, design doc Section 19.11): confirmation via a
same-direction STRUCTURAL_BREAK in the same underlying_move_id, confirmation via continuation past
`current_price`, invalidation via an adverse close through `move_origin_price`, the H8 bound, causal-
only / no-future-data, restart-safety (pure-function re-derivation), and earliest-wins ordering.
"""

from __future__ import annotations

import json

from ai_trader.apprenticeship_v2.general_observer.structural_resolution import (
    compute_structural_resolution_state, due_structural_final_for_episode,
)
from ai_trader.apprenticeship_v2.tests.conftest import M15_SECONDS, make_bar

H8_BARS = 32


def _episode_row(*, frozen_at_bar_ts, direction="BULLISH", current_price=1900.0, origin_price=1896.0, move_id="MOVE-1"):
    return {
        "frozen_at_bar_ts": str(frozen_at_bar_ts), "directional_hypothesis": direction,
        "current_price": str(current_price), "underlying_move_id": move_id,
        "episode_type": "SWEEP_REJECTION",
        "reference_levels_json": json.dumps({"swept_level_price": origin_price}),
    }


def _flat_bars(start_ts, count, price):
    return [make_bar(ts_open=start_ts + i * M15_SECONDS, o=price, h=price, l=price, c=price) for i in range(count)]


def test_unresolved_at_h8_when_price_stays_between_origin_and_current(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", current_price=1900.0, origin_price=1896.0)
    bars = _flat_bars(base_ts + M15_SECONDS, H8_BARS, 1898.0)  # strictly between origin and current -- neither triggers
    state = compute_structural_resolution_state(row, bars, [])
    assert state == "UNRESOLVED_AT_H8"


def test_confirmation_via_continuation_past_current_price_bullish(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", current_price=1900.0, origin_price=1896.0)
    bars = _flat_bars(base_ts + M15_SECONDS, 5, 1898.0) + [
        make_bar(ts_open=base_ts + 6 * M15_SECONDS, o=1901, h=1902, l=1900.5, c=1901.5),  # closes beyond current_price
    ]
    state = compute_structural_resolution_state(row, bars, [])
    assert state == "CONFIRMATION"


def test_confirmation_via_continuation_past_current_price_bearish(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BEARISH", current_price=1900.0, origin_price=1904.0)
    bars = [make_bar(ts_open=base_ts + M15_SECONDS, o=1899, h=1899.5, l=1898.5, c=1899.0)]  # closes below current_price
    state = compute_structural_resolution_state(row, bars, [])
    assert state == "CONFIRMATION"


def test_invalidation_via_adverse_close_through_origin_price_bullish(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", current_price=1900.0, origin_price=1896.0)
    bars = [make_bar(ts_open=base_ts + M15_SECONDS, o=1897, h=1897.5, l=1895.0, c=1895.5)]  # closes below origin_price
    state = compute_structural_resolution_state(row, bars, [])
    assert state == "INVALIDATION"


def test_invalidation_via_adverse_close_through_origin_price_bearish(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BEARISH", current_price=1900.0, origin_price=1904.0)
    bars = [make_bar(ts_open=base_ts + M15_SECONDS, o=1903, h=1905.0, l=1902.5, c=1904.5)]  # closes above origin_price
    state = compute_structural_resolution_state(row, bars, [])
    assert state == "INVALIDATION"


def test_confirmation_via_same_direction_structural_break_in_same_move(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", current_price=1900.0, origin_price=1896.0, move_id="MOVE-X")
    bars = _flat_bars(base_ts + M15_SECONDS, 10, 1898.0)  # price alone never confirms nor invalidates
    other_break_row = {
        "episode_type": "STRUCTURAL_BREAK", "underlying_move_id": "MOVE-X", "directional_hypothesis": "BULLISH",
        "frozen_at_bar_ts": str(base_ts + 5 * M15_SECONDS),
    }
    state = compute_structural_resolution_state(row, bars, [other_break_row])
    assert state == "CONFIRMATION"


def test_structural_break_in_a_different_underlying_move_does_not_confirm(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", current_price=1900.0, origin_price=1896.0, move_id="MOVE-X")
    bars = _flat_bars(base_ts + M15_SECONDS, 10, 1898.0)
    other_break_row = {
        "episode_type": "STRUCTURAL_BREAK", "underlying_move_id": "MOVE-DIFFERENT", "directional_hypothesis": "BULLISH",
        "frozen_at_bar_ts": str(base_ts + 5 * M15_SECONDS),
    }
    state = compute_structural_resolution_state(row, bars, [other_break_row])
    assert state == "UNRESOLVED_AT_H8"


def test_earliest_outcome_wins_invalidation_before_later_confirmation(base_ts):
    """If price invalidates FIRST and only later would have confirmed, invalidation -- the earlier,
    chronologically-first outcome -- wins; the later bar is never reached as a live possibility."""
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", current_price=1900.0, origin_price=1896.0)
    bars = [
        make_bar(ts_open=base_ts + M15_SECONDS, o=1897, h=1897.5, l=1895.0, c=1895.5),  # invalidates first
        make_bar(ts_open=base_ts + 2 * M15_SECONDS, o=1895.5, h=1902.0, l=1895.5, c=1901.5),  # would confirm, too late
    ]
    state = compute_structural_resolution_state(row, bars, [])
    assert state == "INVALIDATION"


def test_earliest_outcome_wins_confirmation_before_later_invalidation(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", current_price=1900.0, origin_price=1896.0)
    bars = [
        make_bar(ts_open=base_ts + M15_SECONDS, o=1899, h=1902.0, l=1898.5, c=1901.5),  # confirms first
        make_bar(ts_open=base_ts + 2 * M15_SECONDS, o=1901.5, h=1901.5, l=1895.0, c=1895.5),  # would invalidate, too late
    ]
    state = compute_structural_resolution_state(row, bars, [])
    assert state == "CONFIRMATION"


def test_no_future_data_leak_bar_past_window_end_is_ignored(base_ts):
    """Adversarial (mandate-style): a bar placed AFTER the H8 window boundary that would otherwise
    confirm must never be consulted -- causal-only, no lookahead past the frozen bound."""
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", current_price=1900.0, origin_price=1896.0)
    within_window = _flat_bars(base_ts + M15_SECONDS, H8_BARS, 1898.0)  # neither confirms nor invalidates
    far_future_bar = make_bar(ts_open=base_ts + (H8_BARS + 50) * M15_SECONDS, o=1901, h=1950, l=1901, c=1949)
    state_without_future = compute_structural_resolution_state(row, within_window, [])
    state_with_future = compute_structural_resolution_state(row, within_window + [far_future_bar], [])
    assert state_without_future == state_with_future == "UNRESOLVED_AT_H8"


def test_due_structural_final_none_while_pending(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", current_price=1900.0, origin_price=1896.0)
    bars = _flat_bars(base_ts + M15_SECONDS, 5, 1898.0)  # far short of H8, no early resolution
    assert due_structural_final_for_episode(row, bars, []) is None


def test_due_structural_final_resolves_early_on_confirmation(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", current_price=1900.0, origin_price=1896.0)
    bars = [make_bar(ts_open=base_ts + M15_SECONDS, o=1901, h=1902, l=1900.5, c=1901.5)]  # confirms on bar 1, well short of H8
    assert due_structural_final_for_episode(row, bars, []) == "CONFIRMATION"


def test_due_structural_final_resolves_at_h8_boundary_when_unresolved(base_ts):
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", current_price=1900.0, origin_price=1896.0)
    bars = _flat_bars(base_ts + M15_SECONDS, H8_BARS, 1898.0)  # exactly reaches the H8 boundary, still no resolution
    assert due_structural_final_for_episode(row, bars, []) == "UNRESOLVED_AT_H8"


def test_restart_safe_pure_recomputation_reproduces_identical_state(base_ts):
    """No internal state anywhere -- calling twice with freshly-constructed (not reused) inputs,
    simulating a process restart, reproduces the identical verdict."""
    row = _episode_row(frozen_at_bar_ts=base_ts, direction="BULLISH", current_price=1900.0, origin_price=1896.0)
    bars_a = [make_bar(ts_open=base_ts + M15_SECONDS, o=1901, h=1902, l=1900.5, c=1901.5)]
    bars_b = [make_bar(ts_open=base_ts + M15_SECONDS, o=1901, h=1902, l=1900.5, c=1901.5)]  # independently constructed
    assert compute_structural_resolution_state(row, bars_a, []) == compute_structural_resolution_state(row, bars_b, [])

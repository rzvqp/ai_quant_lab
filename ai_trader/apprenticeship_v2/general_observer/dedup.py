"""Dedup + underlying-move-id (design doc Sections 8, 11, 12). Two concerns, both mechanical:

1. `underlying_move_id` -- groups episodes (of any of the 4 classes) that describe the SAME
   directional market move, so a lesson's independent-move count never over-counts a sweep +
   displacement + break that are really one continuous event.
2. Per-class dedup key + restart-safe ledger lookup -- suppresses a genuine duplicate (the same
   level/price/direction re-triggering while its family is still open) without needing any in-memory
   state (every check re-reads the ledger fresh, so a process restart changes nothing).
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from ai_trader.apprenticeship_v2.general_observer.detectors import DetectedEvent
from ai_trader.apprenticeship_v2.schemas import RESOLUTION_HORIZONS_M15

if TYPE_CHECKING:
    from ai_trader.apprenticeship_v2.mt5_read_only_source import ReadOnlyBar

UNDERLYING_MOVE_WINDOW_M15_BARS = max(RESOLUTION_HORIZONS_M15)  # 32 -- same H8 boundary resolution.py already uses
UNDERLYING_MOVE_WINDOW_SECONDS = UNDERLYING_MOVE_WINDOW_M15_BARS * 900


def move_origin_price(event: DetectedEvent) -> float:
    """Design doc Section 8, rule 3 -- "the swept/broken level for A/B, the displacement bar's open
    for C, the child episode's origin for D". `reference_levels` is typed `dict[str, object]` (it
    also carries strings like level types); the specific keys read here are always floats per each
    contract's own frozen "Reference levels saved" definition (Section 4) -- `float(...)` on a value
    already known numeric, not a runtime type coercion of arbitrary input."""
    if event.episode_type == "SWEEP_REJECTION":
        return float(event.reference_levels["swept_level_price"])  # type: ignore[arg-type]
    if event.episode_type == "STRUCTURAL_BREAK":
        return float(event.reference_levels["broken_level_price"])  # type: ignore[arg-type]
    if event.episode_type == "DISPLACEMENT":
        return float(event.reference_levels["open"])  # type: ignore[arg-type]
    if event.episode_type == "SESSION_TRANSITION_REVERSAL":
        assert event.child_event is not None
        return move_origin_price(event.child_event)
    raise ValueError(f"move_origin_price: unknown episode_type {event.episode_type!r}")


def _row_move_origin_price(row: dict) -> float:
    """Same as `move_origin_price`, but reading a ledger CSV row (dict of strings) instead of a
    fresh `DetectedEvent` -- used when checking a NEW event against ALREADY-PERSISTED episodes."""
    import json

    ref = json.loads(row["reference_levels_json"])
    etype = row["episode_type"]
    if etype == "SWEEP_REJECTION":
        return float(ref["swept_level_price"])
    if etype == "STRUCTURAL_BREAK":
        return float(ref["broken_level_price"])
    if etype == "DISPLACEMENT":
        return float(ref["open"])
    if etype == "SESSION_TRANSITION_REVERSAL":
        return float(ref["child_swept_level_price"]) if "child_swept_level_price" in ref else float(ref["child_broken_level_price"])
    raise ValueError(f"_row_move_origin_price: unknown episode_type {etype!r}")


def _price_continuity_holds(
    origin_price: float, direction: str, m15_bars_between: list["ReadOnlyBar"],
) -> bool:
    """Design doc Section 8, rule 3: "price must never have closed through the earlier episode's own
    move_origin_price... in the adverse direction". For a BULLISH move, the adverse direction is a
    close back BELOW the origin; for BEARISH, a close back ABOVE it."""
    if direction == "BULLISH":
        return all(b.close >= origin_price for b in m15_bars_between)
    if direction == "BEARISH":
        return all(b.close <= origin_price for b in m15_bars_between)
    raise ValueError(f"_price_continuity_holds: direction must be BULLISH/BEARISH, got {direction!r}")


def compute_underlying_move_id(
    new_event: DetectedEvent, *, existing_general_episode_rows: list[dict], m15_bars_since_earliest_candidate: list["ReadOnlyBar"],
) -> str:
    """Finds the most recent existing general-observer episode (by `frozen_at_bar_ts`) that
    `new_event` should join -- same direction, still within its H8 resolution window, and unbroken
    price continuity between them -- and returns ITS `underlying_move_id`. If none qualifies,
    generates a fresh one. `m15_bars_since_earliest_candidate` must cover at least back to the
    earliest existing episode this function might need to check continuity against; callers that
    pass too short a window will simply find fewer/no qualifying candidates (fail toward a NEW
    family, never toward incorrectly joining one -- the safer failure direction)."""
    candidates = [
        row for row in existing_general_episode_rows
        if row.get("directional_hypothesis") == new_event.direction
        # `<=`, not `<`: two different classes co-observing the SAME trigger bar (e.g. a sweep whose
        # own bar also qualifies as a displacement) are trivially temporally-contained (zero elapsed
        # time) and trivially price-continuous (no bars between them to violate continuity) -- they
        # must share one underlying_move_id, which is Section 8's whole reason to exist. A strict `<`
        # here would silently keep same-bar siblings from ever joining, which no part of the frozen
        # algorithm text (defined only in terms of "earlier"/"later" episodes) actually intends.
        and int(row["frozen_at_bar_ts"]) <= new_event.trigger_bar_ts_close
        and new_event.trigger_bar_ts_close - int(row["frozen_at_bar_ts"]) <= UNDERLYING_MOVE_WINDOW_SECONDS
    ]
    candidates.sort(key=lambda r: int(r["frozen_at_bar_ts"]), reverse=True)  # most recent first

    for row in candidates:
        origin = _row_move_origin_price(row)
        between = [
            b for b in m15_bars_since_earliest_candidate
            if int(row["frozen_at_bar_ts"]) < b.ts_close <= new_event.trigger_bar_ts_close
        ]
        if _price_continuity_holds(origin, new_event.direction, between):
            return row["underlying_move_id"]

    return f"MOVE-{new_event.trigger_bar_ts_close}-{uuid.uuid4().hex[:8]}"


def per_class_dedup_key(event: DetectedEvent, *, underlying_move_id: str) -> tuple:
    """Design doc Section 4 (column H of each contract table) + Section 11. DISPLACEMENT keys on
    `(type, direction, underlying_move_id)` -- a second displacement bar in the SAME still-open
    family is the SAME key, hence a duplicate; SWEEP_REJECTION/STRUCTURAL_BREAK key on
    `(type, level_type, level_price, direction)` instead, independent of family, since a whipsaw
    re-crossing the identical level/price/direction is the duplicate condition for those two
    classes specifically. SESSION_TRANSITION_REVERSAL inherits its child's own key."""
    if event.episode_type == "SWEEP_REJECTION":
        return (event.episode_type, event.reference_levels["swept_level_type"], event.reference_levels["swept_level_price"], event.direction)
    if event.episode_type == "STRUCTURAL_BREAK":
        return (event.episode_type, event.reference_levels["broken_level_type"], event.reference_levels["broken_level_price"], event.direction)
    if event.episode_type == "DISPLACEMENT":
        return (event.episode_type, event.direction, underlying_move_id)
    if event.episode_type == "SESSION_TRANSITION_REVERSAL":
        assert event.child_event is not None
        return per_class_dedup_key(event.child_event, underlying_move_id=underlying_move_id)
    raise ValueError(f"per_class_dedup_key: unknown episode_type {event.episode_type!r}")


def _row_dedup_key(row: dict, underlying_move_id_field: str = "underlying_move_id") -> tuple:
    import json

    ref = json.loads(row["reference_levels_json"])
    etype = row["episode_type"]
    direction = row.get("directional_hypothesis")
    if etype == "SWEEP_REJECTION":
        return (etype, ref["swept_level_type"], ref["swept_level_price"], direction)
    if etype == "STRUCTURAL_BREAK":
        return (etype, ref["broken_level_type"], ref["broken_level_price"], direction)
    if etype == "DISPLACEMENT":
        return (etype, direction, row.get(underlying_move_id_field))
    if etype == "SESSION_TRANSITION_REVERSAL":
        if "child_swept_level_type" in ref:
            return ("SWEEP_REJECTION", ref["child_swept_level_type"], ref["child_swept_level_price"], direction)
        return ("STRUCTURAL_BREAK", ref["child_broken_level_type"], ref["child_broken_level_price"], direction)
    raise ValueError(f"_row_dedup_key: unknown episode_type {etype!r}")


def is_duplicate(
    event: DetectedEvent, *, underlying_move_id: str, existing_general_episode_rows: list[dict],
) -> bool:
    """Section 11: "a genuinely new crossing (price closed back to the original side first) is a
    legitimately new event, not a duplicate" -- for SWEEP_REJECTION/STRUCTURAL_BREAK this is already
    handled structurally (their dedup key has no `underlying_move_id` component, so once a family
    closes and a later, independent crossing of the SAME level/price/direction occurs, THIS
    function alone cannot distinguish "still the same active episode" from "a legitimately new one
    at the same level" -- that distinction is exactly what `compute_underlying_move_id` already
    resolved by assigning a NEW `underlying_move_id` when price continuity broke; `is_duplicate`
    only refuses an EXACT re-trigger within what is already known to be the same underlying move).
    Restart-safe by construction: always a fresh ledger read, never an in-memory flag (Section 11's
    own explicit restart-duplicate requirement)."""
    key = per_class_dedup_key(event, underlying_move_id=underlying_move_id)
    for row in existing_general_episode_rows:
        try:
            if _row_dedup_key(row) == key:
                return True
        except (KeyError, ValueError):
            continue
    return False

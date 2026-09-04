"""The 4 frozen event-contract triggers (design doc Section 4). Every trigger condition, direction
rule, reference-level set, and reason code below is a literal transcription of that section's own
tables -- no threshold, metric, or magnitude term is introduced anywhere in this file beyond what
Section 4 states verbatim (DISPLACEMENT's `2.0 * ATR14` / `ABS_CLOSE_MINUS_OPEN` are themselves
CEO-declared constants the doc itself froze, reused here, not re-derived).
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from ai_trader.apprenticeship_v2.general_observer.major_levels import MajorLevel, levels_of_side
from ai_trader.apprenticeship_v2.general_observer.primitives import atr14

if TYPE_CHECKING:
    from ai_trader.apprenticeship_v2.mt5_read_only_source import ReadOnlyBar

DISPLACEMENT_ATR_MULTIPLIER = 2.0  # CEO-locked, design doc Section 6 -- not derived, not calibrated
DISPLACEMENT_MAGNITUDE_METRIC = "ABS_CLOSE_MINUS_OPEN"  # CEO-locked, design doc Section 6


@dataclasses.dataclass(frozen=True, slots=True)
class DetectedEvent:
    episode_type: str  # one of schemas.GENERAL_OBSERVER_EVENT_TYPES
    trigger_bar_ts_close: int
    direction: str  # "BULLISH" | "BEARISH" -- never NEUTRAL/UNCLEAR, structurally impossible per Section 4
    reference_levels: dict[str, object]
    reason_code: str
    what_triggered_observation: str
    child_event: "DetectedEvent | None" = None  # only ever set for SESSION_TRANSITION_REVERSAL


def detect_sweep_rejection(bar: ReadOnlyBar, levels: list[MajorLevel]) -> DetectedEvent | None:
    """Section 4A. Breach-and-reclaim within ONE bar -- no magnitude term, no second bar."""
    for level in levels_of_side(levels, "LOW"):
        if bar.low < level.price and bar.close > level.price:
            return DetectedEvent(
                episode_type="SWEEP_REJECTION", trigger_bar_ts_close=bar.ts_close, direction="BULLISH",
                reference_levels={
                    "swept_level_type": level.level_type, "swept_level_price": level.price,
                    "breach_extreme": bar.low, "reclaim_close": bar.close,
                },
                reason_code=f"SWEEP_{level.level_type}_BULLISH",
                what_triggered_observation=f"M15 low {bar.low} swept {level.level_type} {level.price} then reclaimed, close {bar.close}",
            )
    for level in levels_of_side(levels, "HIGH"):
        if bar.high > level.price and bar.close < level.price:
            return DetectedEvent(
                episode_type="SWEEP_REJECTION", trigger_bar_ts_close=bar.ts_close, direction="BEARISH",
                reference_levels={
                    "swept_level_type": level.level_type, "swept_level_price": level.price,
                    "breach_extreme": bar.high, "reclaim_close": bar.close,
                },
                reason_code=f"SWEEP_{level.level_type}_BEARISH",
                what_triggered_observation=f"M15 high {bar.high} swept {level.level_type} {level.price} then rejected, close {bar.close}",
            )
    return None


def detect_structural_break(prior_bar: ReadOnlyBar, bar: ReadOnlyBar, levels: list[MajorLevel]) -> DetectedEvent | None:
    """Section 4B. Pure crossing of consecutive M15 closes -- `prior_bar` must be the immediately
    preceding M15 bar (caller's responsibility; this function does not itself verify adjacency)."""
    for level in levels_of_side(levels, "HIGH"):
        if prior_bar.close <= level.price < bar.close:
            return DetectedEvent(
                episode_type="STRUCTURAL_BREAK", trigger_bar_ts_close=bar.ts_close, direction="BULLISH",
                reference_levels={
                    "broken_level_type": level.level_type, "broken_level_price": level.price,
                    "prior_bar_close": prior_bar.close, "breaking_bar_close": bar.close,
                },
                reason_code=f"BREAK_{level.level_type}_BULLISH",
                what_triggered_observation=f"M15 close crossed above {level.level_type} {level.price} ({prior_bar.close} -> {bar.close})",
            )
    for level in levels_of_side(levels, "LOW"):
        if prior_bar.close >= level.price > bar.close:
            return DetectedEvent(
                episode_type="STRUCTURAL_BREAK", trigger_bar_ts_close=bar.ts_close, direction="BEARISH",
                reference_levels={
                    "broken_level_type": level.level_type, "broken_level_price": level.price,
                    "prior_bar_close": prior_bar.close, "breaking_bar_close": bar.close,
                },
                reason_code=f"BREAK_{level.level_type}_BEARISH",
                what_triggered_observation=f"M15 close crossed below {level.level_type} {level.price} ({prior_bar.close} -> {bar.close})",
            )
    return None


def detect_displacement(bar: ReadOnlyBar, m15_bars_up_to_and_including: list[ReadOnlyBar]) -> DetectedEvent | None:
    """Section 4C/6. `m15_bars_up_to_and_including` must end with `bar` itself (ATR14 is computed
    "on the M15 bar list up to and including the trigger bar" -- design doc's own explicit,
    non-ambiguous statement, verbatim reuse of `_atr14`'s own trailing-window behavior)."""
    assert m15_bars_up_to_and_including[-1] is bar or m15_bars_up_to_and_including[-1] == bar
    atr = atr14(m15_bars_up_to_and_including)
    if atr is None:
        return None  # fewer than 15 bars -- Invalid trigger, Section 4C
    magnitude = abs(bar.close - bar.open)
    if bar.close == bar.open:
        return None  # DISPLACEMENT_TRIGGER = FALSE, no episode at all -- Section 4C direction rule
    if magnitude < DISPLACEMENT_ATR_MULTIPLIER * atr:
        return None
    direction = "BULLISH" if bar.close > bar.open else "BEARISH"
    return DetectedEvent(
        episode_type="DISPLACEMENT", trigger_bar_ts_close=bar.ts_close, direction=direction,
        reference_levels={
            "open": bar.open, "high": bar.high, "low": bar.low, "close": bar.close,
            "atr14_reference_value": atr, "displacement_atr_multiplier": DISPLACEMENT_ATR_MULTIPLIER,
            "displacement_magnitude_metric": DISPLACEMENT_MAGNITUDE_METRIC,
        },
        reason_code=f"DISPLACEMENT_{direction}",
        what_triggered_observation=f"abs(close-open)={magnitude:.5f} >= {DISPLACEMENT_ATR_MULTIPLIER}*ATR14({atr:.5f})",
    )


def session_closing_direction(m15_session_bars: list[ReadOnlyBar]) -> str | None:
    """"sign of (last M15 close of the session - first M15 close of the session)"; `UNCLEAR` (`None`)
    if that difference is exactly zero (design doc Section 4D)."""
    if not m15_session_bars:
        return None
    diff = m15_session_bars[-1].close - m15_session_bars[0].close
    if diff == 0:
        return None
    return "BULLISH" if diff > 0 else "BEARISH"


def detect_session_transition_reversal(
    child: DetectedEvent, *, preceding_session_name: str, preceding_session_direction: str | None,
    new_session_name: str,
) -> DetectedEvent | None:
    """Section 4D. Composed, not independent -- `child` must already be a fired SWEEP_REJECTION or
    STRUCTURAL_BREAK event; this function only decides whether it ALSO qualifies as a session-
    transition reversal (opposite direction to the preceding session's own closing direction).
    Introduces no new magnitude term -- materiality is entirely inherited from `child`."""
    if child.episode_type not in ("SWEEP_REJECTION", "STRUCTURAL_BREAK"):
        raise ValueError(f"detect_session_transition_reversal: child must be SWEEP_REJECTION or STRUCTURAL_BREAK, got {child.episode_type}")
    if preceding_session_direction is None:
        return None  # preceding session closing direction UNCLEAR -- no episode
    if child.direction == preceding_session_direction:
        return None  # not a reversal
    return DetectedEvent(
        episode_type="SESSION_TRANSITION_REVERSAL", trigger_bar_ts_close=child.trigger_bar_ts_close,
        direction=child.direction,
        reference_levels={
            "prior_session_name": preceding_session_name, "prior_session_close_direction": preceding_session_direction,
            "new_session_name": new_session_name, "child_reason_code": child.reason_code,
            **{f"child_{k}": v for k, v in child.reference_levels.items()},
        },
        reason_code=f"SESSION_REVERSAL_{preceding_session_name}_TO_{new_session_name}_{child.direction}",
        what_triggered_observation=f"{new_session_name} session opened opposite to {preceding_session_name}'s {preceding_session_direction} close, via {child.reason_code}",
        child_event=child,
    )

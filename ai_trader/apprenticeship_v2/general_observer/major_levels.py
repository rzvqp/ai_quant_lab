"""Major-level computation (design doc Section 5) -- exactly the 6 eligible types, computed
causally from already-closed H1 data only. No arbitrary local highs/lows, no visually-selected
levels, no weekly boundary, no round numbers, no OB/FVG (those remain tag-only context per the
frozen doc, never a trigger-defining level -- not implemented as levels here at all).
"""

from __future__ import annotations

import dataclasses
import datetime
from typing import TYPE_CHECKING

from ai_trader.apprenticeship_v2.general_observer.primitives import (
    causally_available_swings, h1_confirmed_swing_highs, h1_confirmed_swing_lows, session_for_ts, utc_day_for_ts,
)

if TYPE_CHECKING:
    from ai_trader.apprenticeship_v2.mt5_read_only_source import ReadOnlyBar

ELIGIBLE_LEVEL_TYPES = (
    "PREVIOUS_DAY_HIGH", "PREVIOUS_DAY_LOW", "PREVIOUS_SESSION_HIGH", "PREVIOUS_SESSION_LOW",
    "H1_CONFIRMED_SWING_HIGH", "H1_CONFIRMED_SWING_LOW",
)
"""Locked eligible set, exactly 6 (design doc Section 5) -- M15 swings, weekly high/low, arbitrary
local highs/lows, round numbers, OB, and FVG are all explicitly excluded, not deferred."""

_HIGH_TYPES = frozenset({"PREVIOUS_DAY_HIGH", "PREVIOUS_SESSION_HIGH", "H1_CONFIRMED_SWING_HIGH"})
_LOW_TYPES = frozenset({"PREVIOUS_DAY_LOW", "PREVIOUS_SESSION_LOW", "H1_CONFIRMED_SWING_LOW"})


@dataclasses.dataclass(frozen=True, slots=True)
class MajorLevel:
    level_type: str  # one of ELIGIBLE_LEVEL_TYPES
    price: float

    @property
    def side(self) -> str:
        if self.level_type in _HIGH_TYPES:
            return "HIGH"
        if self.level_type in _LOW_TYPES:
            return "LOW"
        raise ValueError(
            f"MajorLevel.side: {self.level_type!r} is not one of the 6 eligible major-level types "
            f"({ELIGIBLE_LEVEL_TYPES}) -- refusing to guess a side for an out-of-contract level type"
        )


def previous_day_high_low(h1_bars: list[ReadOnlyBar], *, as_of_ts_close: int) -> tuple[float | None, float | None]:
    """"Previous UTC day" = exactly the calendar day immediately before `as_of_ts_close`'s own day --
    not "the most recently available day with data" (design doc: "the level not yet computable...
    NOT_AVAILABLE, no episode" -- a gap-shortened lookback would be a silent fabrication, not a
    documented invalid-trigger case)."""
    causal = [b for b in h1_bars if b.ts_close <= as_of_ts_close]
    if not causal:
        return None, None
    target_day = utc_day_for_ts(as_of_ts_close) - datetime.timedelta(days=1)
    day_bars = [b for b in causal if utc_day_for_ts(b.ts_close) == target_day]
    if not day_bars:
        return None, None
    return max(b.high for b in day_bars), min(b.low for b in day_bars)


def previous_session_high_low(h1_bars: list[ReadOnlyBar], *, as_of_ts_close: int) -> tuple[float | None, float | None]:
    """Walks backward from `as_of_ts_close` past every bar still in the CURRENT session, then
    collects every consecutive bar belonging to the single session type immediately before it --
    gap-tolerant (does not assume a fixed bar count per session)."""
    causal = [b for b in h1_bars if b.ts_close <= as_of_ts_close]
    if not causal:
        return None, None
    current_session = session_for_ts(as_of_ts_close)
    i = len(causal) - 1
    while i >= 0 and session_for_ts(causal[i].ts_close) == current_session:
        i -= 1
    if i < 0:
        return None, None
    prev_session = session_for_ts(causal[i].ts_close)
    prev_bars: list[ReadOnlyBar] = []
    while i >= 0 and session_for_ts(causal[i].ts_close) == prev_session:
        prev_bars.append(causal[i])
        i -= 1
    if not prev_bars:
        return None, None
    return max(b.high for b in prev_bars), min(b.low for b in prev_bars)


def compute_eligible_major_levels(h1_bars: list[ReadOnlyBar], *, as_of_ts_close: int) -> list[MajorLevel]:
    """All eligible major levels computable as of `as_of_ts_close`, causally. A level type with no
    computable value yet (e.g. no prior day in the data history) is simply absent from the returned
    list -- never a fabricated/placeholder value."""
    levels: list[MajorLevel] = []

    day_high, day_low = previous_day_high_low(h1_bars, as_of_ts_close=as_of_ts_close)
    if day_high is not None:
        levels.append(MajorLevel("PREVIOUS_DAY_HIGH", day_high))
    if day_low is not None:
        levels.append(MajorLevel("PREVIOUS_DAY_LOW", day_low))

    sess_high, sess_low = previous_session_high_low(h1_bars, as_of_ts_close=as_of_ts_close)
    if sess_high is not None:
        levels.append(MajorLevel("PREVIOUS_SESSION_HIGH", sess_high))
    if sess_low is not None:
        levels.append(MajorLevel("PREVIOUS_SESSION_LOW", sess_low))

    causal_h1 = [b for b in h1_bars if b.ts_close <= as_of_ts_close]
    for price in causally_available_swings(h1_confirmed_swing_highs(causal_h1), as_of_ts_close=as_of_ts_close):
        levels.append(MajorLevel("H1_CONFIRMED_SWING_HIGH", price))
    for price in causally_available_swings(h1_confirmed_swing_lows(causal_h1), as_of_ts_close=as_of_ts_close):
        levels.append(MajorLevel("H1_CONFIRMED_SWING_LOW", price))

    return levels


def levels_of_side(levels: list[MajorLevel], side: str) -> list[MajorLevel]:
    return [lvl for lvl in levels if lvl.side == side]

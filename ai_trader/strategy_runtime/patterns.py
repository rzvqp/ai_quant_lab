"""Shared candlestick/bar-pattern helpers for Batch B5 (S45/S50), extracted from
``code/mstrat_ext.py``'s own recurring vocabulary. Every function here is a pure function of
already-fetched bars -- no context access, no side effects, trivially unit-testable in isolation,
mirroring ``confirmations.py``'s own design.
"""

from __future__ import annotations

from typing import Any


def is_outside_bar(bar: dict[str, Any], prev_bar: dict[str, Any]) -> bool:
    """``code/mstrat_ext.py::s50_setups``'s own ``outside`` shape: this bar's range fully engulfs
    the previous bar's (``high > prev.high`` AND ``low < prev.low``)."""
    return bool(bar["high"] > prev_bar["high"] and bar["low"] < prev_bar["low"])


def is_range_expansion(bar: dict[str, Any], atr: float | None) -> bool:
    """The bar's own true range exceeds ATR -- ``s50_setups``'s own "genuine expansion" gate
    (``(hi-lo) > atr``, a stricter one-ATR threshold, distinct from ``confirmations.
    is_displacement_bar``'s configurable multiple)."""
    if atr is None or atr <= 0:
        return False
    return bool((bar["high"] - bar["low"]) > atr)


def close_to_close_direction(bar: dict[str, Any], prev_bar: dict[str, Any]) -> int:
    """``+1`` if this bar's close is above the previous bar's close, ``-1`` if below, ``0`` if
    unchanged -- ``code/mstrat_ext.py::s45_setups``'s own streak-direction primitive
    (``np.diff(cl)``), distinct from ``confirmations.bar_direction_bullish``'s open-vs-close shape."""
    if bar["close"] > prev_bar["close"]:
        return 1
    if bar["close"] < prev_bar["close"]:
        return -1
    return 0


def exact_close_to_close_streak(bars: list[dict[str, Any]], k: int) -> int | None:
    """``+1``/``-1`` if the LAST ``k`` bars (``bars[-k:]`` vs. their own predecessors) are all the
    SAME close-to-close direction AND the bar immediately preceding that window (if present) is a
    DIFFERENT direction -- the streak is EXACTLY ``k`` long, not merely at-least-``k``, mirroring
    ``s45_setups``'s own per-bar streak-length assignment (a bar mid-way through a longer streak
    never separately re-triggers a shorter-``k`` hypothesis). ``None`` if there is no such streak or
    insufficient history (``k+1`` bars needed: the window itself plus one predecessor per bar)."""
    if len(bars) < k + 1:
        return None
    directions = [close_to_close_direction(bars[i], bars[i - 1]) for i in range(len(bars) - k, len(bars))]
    first = directions[0]
    if first == 0 or any(d != first for d in directions):
        return None
    if len(bars) >= k + 2:
        breaking_direction = close_to_close_direction(bars[-k - 1], bars[-k - 2])
        if breaking_direction == first:
            return None  # the streak extends beyond k -- not an "exactly k" onset
    return first

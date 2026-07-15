"""Shared confirmation-check primitives, extracted from the recurring vocabulary across the Strategy
Library's own ``required_confirmations``/``entry_rules`` text (``consecutive2``, ``close_beyond``,
``displacement``, imbalance/FVG presence). Each strategy family composes these instead of
re-implementing the same bar-pattern check independently -- keeps every family's own evaluator short
and reduces the chance of two strategies silently drifting on what "two consecutive closes" means.

Every function here is a pure function of already-fetched bars/features -- no context access, no
side effects, trivially unit-testable in isolation.
"""

from __future__ import annotations

from typing import Any


def consecutive_same_direction_closes(recent_bars: list[dict[str, Any]], n: int, bullish: bool) -> bool:
    """The last ``n`` bars all closed in the given direction (``close > open`` for bullish,
    ``close < open`` for bearish). ``recent_bars`` must be oldest-first, as
    ``context_access.bars()`` returns them."""
    if len(recent_bars) < n or n <= 0:
        return False
    tail = recent_bars[-n:]
    return all(bool((b["close"] > b["open"]) == bullish) for b in tail)


def close_beyond_level(bar: dict[str, Any], level: float, upward: bool) -> bool:
    """The bar's close crossed back through ``level`` (upward: close > level; downward: close < level)."""
    return bool(bar["close"] > level) if upward else bool(bar["close"] < level)


def swept_level(bar: dict[str, Any], level: float, is_high_sweep: bool) -> bool:
    """A liquidity sweep: the bar's extreme took out ``level`` but its close stayed on the other
    side (``EXECUTION_SIMULATOR``-style wick-vs-body distinction) -- the defining S1 mechanism,
    reused by any strategy built on the same "sweep then reject" shape."""
    if is_high_sweep:
        return bool(bar["high"] > level and bar["close"] < level)
    return bool(bar["low"] < level and bar["close"] > level)


def is_displacement_bar(bar: dict[str, Any], atr: float | None, min_atr_multiple: float = 1.2) -> bool:
    """A bar whose true range meaningfully exceeds the prevailing ATR -- the Market Scanner's own
    ``disp`` feature already flags this per-bar (``M15_FEATURE_NAMES``); this helper is the
    fallback/explicit form for families that need a specific multiple rather than the scanner's
    fixed threshold."""
    if atr is None or atr <= 0:
        return False
    rng = bar["high"] - bar["low"]
    return bool(rng >= min_atr_multiple * atr)


def bar_direction_bullish(bar: dict[str, Any]) -> bool:
    return bool(bar["close"] > bar["open"])


def rolling_extreme_touch(bar: dict[str, Any], extreme: float | None, is_high: bool, tolerance: float = 0.0) -> bool:
    """Whether ``bar`` touches/exceeds a precomputed rolling extreme (e.g. ``rmax20``/``rmin20`` from
    ``M15_FEATURE_NAMES``) within ``tolerance`` price units -- used by round-number/level-rejection
    style families. ``extreme=None`` (not enough history yet) never matches (fail-safe)."""
    if extreme is None:
        return False
    return bool(bar["high"] >= extreme - tolerance) if is_high else bool(bar["low"] <= extreme + tolerance)

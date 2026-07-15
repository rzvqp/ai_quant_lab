"""Shared VWAP/value-area helpers for Batch B3 (S26/S27/S28), extracted from the recurring "distance
from value, reclaim/reject at value" vocabulary in the Strategy Library's own grammar
(``code/mstrat_ext.py``). Every function here is a pure function of already-fetched bars/features --
no context access, no side effects, trivially unit-testable in isolation, mirroring
``confirmations.py``'s own design.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def value_area_edges(vwap: float, std: float, k: float) -> tuple[float, float]:
    """The value-area upper/lower edge (``vwap +/- k*std``) -- ``code/mstrat_ext.py::s26_setups``'s
    own ``va_hi``/``va_lo``."""
    return vwap + k * std, vwap - k * std


def week_bucket(ts_open: int) -> int:
    """The frozen research engine's own Monday-aligned week bucket
    (``code/mstrat_ext.py::_anchored_vwap``: ``(t - 345600) // 604800`` -- epoch 0, 1970-01-01, was
    a Thursday; the 4-day/345600s shift re-aligns bucket boundaries to Monday 00:00 UTC)."""
    return (ts_open - 345_600) // 604_800


def anchored_vwap(bars: list[dict[str, Any]], bucket_of: Callable[[int], int]) -> float | None:
    """The cumulative volume-weighted typical price of every bar in ``bars`` sharing the LAST bar's
    own anchor bucket (e.g. :func:`week_bucket`) -- mirrors ``code/mstrat_ext.py::_anchored_vwap``'s
    own ``groupby(seg).cumsum()`` convention, using only bars already in the (lookahead-safe)
    context window. ``None`` if no bar carries positive volume in that bucket (never divides by
    zero)."""
    if not bars:
        return None
    last_bucket = bucket_of(bars[-1]["ts_open"])
    same_bucket = [b for b in bars if bucket_of(b["ts_open"]) == last_bucket]
    cum_pv = 0.0
    cum_vol = 0.0
    for b in same_bucket:
        typical = (float(b["high"]) + float(b["low"]) + float(b["close"])) / 3.0
        vol = float(b["volume"])
        cum_pv += typical * vol
        cum_vol += vol
    if cum_vol <= 0:
        return None
    return cum_pv / cum_vol


def distance_in_atr(price: float, anchor: float, atr: float | None) -> float | None:
    """``|price - anchor| / atr`` -- ``None`` if ``atr`` is missing/non-positive (never divides by
    zero or a non-finite value)."""
    if atr is None or atr <= 0:
        return None
    return abs(price - anchor) / atr

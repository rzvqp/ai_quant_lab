"""`SpreadObservation` -- one sample per closed M15 bar (CEO instruction, 2026-08-04): timestamp,
bid/ask/spread, session, current ATR (volatility proxy), and the day-boundary label the rest of this
project already uses for "distinct day" grouping (17:00-NY anchor, `day_index.day_boundary_start_utc`) --
so the Statistician's own "min 25 distinct DAYS per cell, not 25 observations" requirement can be
computed directly from `day_boundary_label`, without re-deriving day boundaries downstream.

**`is_level_touch`/`touch_level_kind`, disclosed reasoning**: readings sampled uniformly in time are
biased toward the ordinary case, because a real trade only ever triggers where a level is actually
touched -- and touches cluster where spread structurally widens (news, session opens, thin liquidity).
Marking these separately (CEO: "esantionarea uniforma e partinitoare in jos") lets a later consumer
build the trigger-conditioned distribution the Statistician actually needs, instead of only the
unconditional one. This module never decides which distribution matters -- it just tags the fact."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SpreadObservation:
    symbol: str
    as_of: int
    """`bar.ts_close` -- the bar this observation was sampled at, closed."""
    bid: float
    ask: float
    spread: float
    """`ask - bid`, in price units (not pips) -- same convention as `effective_spread` everywhere else
    in this project."""
    session: str
    """One of `"asia"`/`"london"`/`"ny"`/`"late"`, from the SAME ratified `market_state.sessions`
    every other component already uses."""
    atr: float | None
    """`None` during ATR14 warmup (first 14 bars) -- never fabricated, matching this project's own
    fail-closed-on-missing-data convention."""
    day_boundary_label: int
    """The 17:00-NY day boundary (`day_index.day_boundary_start_utc`) this bar belongs to -- the
    project's own established "distinct day" grouping key."""
    is_level_touch: bool
    """True if THIS bar is a fresh PDH/PDL touch (`institutional_levels.detect_level_touches`) --
    regardless of whether any policy would trade it. This is the trigger-conditioned subsample."""
    touch_level_kind: str | None
    """`"pdh"`/`"pdl"` when `is_level_touch` is True, else `None`."""

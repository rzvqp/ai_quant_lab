"""Types owned by `zone_observer` (2026-08-04). Same discipline as `structural_observer`: "Doar
observare, fara politici" -- a plain fact record, never a decision. Same generic-envelope convention
(`kind` + JSON-serializable `detail` dict) as every journal in this project.

Mid is a DIFFERENT object from High/Low (session_levels.py's own docstring): stops sit beyond
extremes, nobody puts one at the midpoint -- Mid is touched by CONTAINMENT, not breach, has no
intrinsic direction, and is never reported together with High/Low. `SESSION_LEVEL_TOUCH`'s `detail`
always carries the touched level's own `SessionLevelKind` (`session_high`/`session_low`/`session_mid`)
so a consumer can always tell them apart without a second event kind."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ZoneEventKind(str, Enum):
    SESSION_LEVEL_FORMED = "SESSION_LEVEL_FORMED"
    """One per High/Low/Mid of a just-closed session (primitive A -- expires after the next session).
    `detail.level_kind` in {"session_high","session_low","session_mid"}, `detail.session_label` names
    the SOURCE session (asia/london/ny/late)."""

    SESSION_LEVEL_TOUCH = "SESSION_LEVEL_TOUCH"
    """A formed session level is touched -- High/Low by breach, Mid by containment. `detail.level_kind`
    disambiguates; Mid touches are never merged into the same count as High/Low."""

    DEMAND_ZONE_FORMED = "DEMAND_ZONE_FORMED"
    """`order_flow.detect_demand_zones` -- the full [Low, High] of an order-block anchor bar, wick
    included. Non-consumable (a persistent, re-testable reference, not an event with a lifetime)."""

    INVERSE_FVG_FORMED = "INVERSE_FVG_FORMED"
    """A previously-formed FVG (already recorded by `structural_observer` as FVG_FORMED) inverts --
    first later bar whose CLOSE violates the far edge. `detail.original_formed_idx` links back to it."""

    BPR_COUNT = "BPR_COUNT"
    """`imbalance_mechanics.count_bpr` -- bullish x bearish FVG overlap counts at three tolerances
    (0.0/0.10/0.25), purely descriptive, no freezing rule applied here. Recorded only when a count
    increases (never every bar) -- a snapshot dict re-emitted unchanged every bar would be pure noise."""

    WEEKLY_LEVEL_FORMED = "WEEKLY_LEVEL_FORMED"
    """PWH/PWL formation only (`institutional_levels.compute_prior_week_levels`). NO touch detection --
    `institutional_levels.detect_level_touches` explicitly excludes WEEKLY_HIGH/WEEKLY_LOW ("doar
    fereastra zilnica"); no ratified weekly-touch detector exists, so none is invented here."""

    LIQUIDITY_VOID = "LIQUIDITY_VOID"
    """`order_block_void.detect_liquidity_voids` -- a bar-to-bar transition classified TEMPORAL/SIZE/BOTH.
    Disclosed overlap: a TEMPORAL-only void is the same underlying condition (span > 900s, maintenance
    window excluded) already detected independently by every live process's own `LiveBarFeed` gap
    detector -- the genuinely NEW information here is the SIZE and BOTH classifications (a price jump
    without a time gap, or with one), which nothing else currently tracks."""


@dataclass(frozen=True, slots=True)
class ZoneObservation:
    symbol: str
    as_of: int
    kind: ZoneEventKind
    detail: dict[str, object]

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("ZoneObservation.symbol must not be empty")

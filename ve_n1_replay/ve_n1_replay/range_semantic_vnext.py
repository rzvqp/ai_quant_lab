"""RANGE LIFECYCLE VNEXT -- bounded multi-candidate MACRO tracking (mandate
`VE-RANGE-LIFECYCLE-VNEXT-MULTI-CANDIDATE-RESEARCH-001`). Research prototype, NOT ratified, NOT
production-ready, NOT integrated into New Brain. Full design rationale in
`VE_RANGE_LIFECYCLE_VNEXT_ARCHITECTURE.md` -- this docstring summarizes only what a reader needs to trust
the code is doing what that document says.

CENTRAL FINDING THIS MODULE IS BUILT ON: `range_semantic_v4_4.py`'s own module docstring already states
`EPISODE_MERGED`/the MERGE branch of `_episode_identity_for_new_macro` "is implemented (not dead code, in
case a future architectural change ever allows concurrent candidates) but is structurally unreachable via
the public observe() API today" -- unreachable ONLY because `forming_macro = self._active_macro is None`
never lets a second candidate form while one is active. This module removes that single-slot gate and
generalizes v4.4's own existing IoU-based (`_iou`, the ratified blind-scorer's own convention, not
invented here) zone-overlap MERGE check from "the one active macro" to "every macro in a bounded
registry". Nothing about the geometric question is invented; the gate that made it unreachable is.

WHAT IS FIXED, not silently inherited: v4.4's own dead MERGE branch would have overwritten
`self._active_macro` without ever terminating the structure being replaced (no `end_ts`, never added to
history) -- never caught because provably unreachable. Reachable here, so fixed: a superseded macro is
properly retired (`CANDIDATE_SUPERSEDED_BY_MERGE`, appended to history) before the merging candidate takes
over its identity chain via `continued_from_id`, exactly mirroring v4.4's own CONTINUATION semantics.

A SECOND supersession mechanism (`_retire_price_abandoned_candidates`, architecture doc section 6a) was
added AFTER an exploratory measurement found overlap-merge alone leaves a moderate but real steady-state
population of candidates price has moved completely away from (nothing new ever overlaps them, so nothing
ever resolves them) -- median 12, max 22 concurrent candidates in an early sample. It retires a
never-confirmed candidate ONLY if price has moved outside its own `tol_cluster*atr_ref` acceptance
tolerance (the SAME distance `Cluster.offer` already uses, not a new threshold) AND a DIFFERENT active
candidate is structurally closer to price -- so it never fires on an isolated candidate, protecting the
exact "slow but valid" case mandate section 6 requires. This is the mechanism carrying the largest
false-positive risk in this architecture; the research report's full-history negative control is where
that claim is actually tested, not assumed from the registry-size improvement alone.

WHAT IS DELIBERATELY UNCHANGED: v4.3/v4.4's own `Cluster`, `Registry`, `Excursion`, `assign_level`,
`degeneracy_check`, `offer_swing`, `efficiency_ratio`/`traversal_count`/`relative_net_displacement`/
`alternation_rate`, `_iou`, `IOU_CONTINUE`/`GAP_MAX`/every other frozen threshold, and `StructureV44`
itself -- all reused by import, none redefined. No age/duration/timeout-based termination rule exists
anywhere in this module (mandate section 2) -- registry admission is decided by geometry (IoU/cluster
tolerance, price-distance-from-own-boundary) and a fixed resource CAP (section 7 of the architecture doc),
never by how long a candidate has existed. No P&L/WR/RR/trade-outcome data is read anywhere here (mandate
section 13)."""
from __future__ import annotations

import dataclasses as _dc
from typing import Any

from .range_semantic_v4_3 import (
    ATR_UNAVAILABLE,
    BETWEEN_EPISODES,
    BREAKOUT_ACCEPTED,
    ConfigNotRatifiedErrorV43,
    ContractErrorV43,
    Depth,
    ESTABLISHING_FEW_SWINGS,
    Excursion,
    NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT,
    OK_RANGE_MACRO,
    RangeEventV43,
    Registry,
    SNAPSHOT_CONTRACT_MISMATCH,
    SWEEP_CONFIRMED,
    Structure,
    TOO_SHORT_MACRO,
    ZONES_DEGENERATE,
    ZONES_INVERTED,
    assign_level,
    degeneracy_check,
    offer_swing,
    sweep_reversal_confirmed,
)
from .range_semantic_v4_4 import (
    ConfigV44,
    EPISODE_CONTINUATION,
    EPISODE_MERGED,
    EPISODE_REPLACEMENT,
    EXCESSIVE_NET_DISPLACEMENT,
    INSUFFICIENT_ALTERNATION_EVIDENCE,
    INSUFFICIENT_EFFICIENCY,
    INSUFFICIENT_TRAVERSAL,
    RANGE_CANDIDATE_PRESENT,
    RANGE_WEAKENING,
    REASONS_V44,
    StructureV44,
    WEAKENING_PERSISTENCE_TERMINATED,
    WEAKENING_RECOVERED,
    _as_v43_cfg,
    _iou,
    alternation_rate,
    efficiency_ratio,
    relative_net_displacement,
    traversal_count,
)

__all__ = [
    "ConfigNotRatifiedErrorV43", "ContractErrorV43", "RangeEventV43", "SNAPSHOT_CONTRACT_MISMATCH",
    "RANGE_HIERARCHICAL_VNEXT_CONTRACT_VERSION",
    "CANDIDATE_SUPERSEDED_BY_MERGE", "REGISTRY_CAPACITY_REFUSED", "CANDIDATE_ABANDONED_PRICE_MOVED_ON",
    "REASONS_VNEXT",
    "ConfigVNext",
    "RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID",
    "RangeSemanticResultVNext",
    "RangeSemanticProducerVNext",
    "RANGE_HIERARCHICAL_VNEXT_IMPLEMENTATION_FINGERPRINT",
]

# ═══════════════════════════════════ identity ═══════════════════════════════════

RANGE_HIERARCHICAL_VNEXT_CONTRACT_VERSION = "range-hierarchical-vnext-multicandidate-v1"

# 3 additive reason codes -- the 40 from v4.4 remain valid, unrenumbered.
CANDIDATE_SUPERSEDED_BY_MERGE = "CANDIDATE_SUPERSEDED_BY_MERGE"
REGISTRY_CAPACITY_REFUSED = "REGISTRY_CAPACITY_REFUSED"
CANDIDATE_ABANDONED_PRICE_MOVED_ON = "CANDIDATE_ABANDONED_PRICE_MOVED_ON"

REASONS_VNEXT: tuple[str, ...] = REASONS_V44 + (
    CANDIDATE_SUPERSEDED_BY_MERGE, REGISTRY_CAPACITY_REFUSED, CANDIDATE_ABANDONED_PRICE_MOVED_ON)
assert len(REASONS_VNEXT) == 43, f"40 V4.4 + 3 vNext = 43 expected, got {len(REASONS_VNEXT)}"
assert len(set(REASONS_VNEXT)) == 43, "duplicate reason code between V4.4 and vNext"


# ═══════════════════════════════════ configuration ═══════════════════════════════════

@_dc.dataclass(frozen=True, slots=True)
class ConfigVNext(ConfigV44):
    """All 21 v4.4-inherited fields keep their frozen values unchanged. ONE new field:
    `max_active_macro_candidates` -- a RESOURCE cap, not a behavior rule (see architecture doc section 7).
    It is never consulted by MERGE/CONTINUATION/REPLACEMENT geometry, only by whether a genuinely-new
    REPLACEMENT candidate can be admitted at all. Its default is set from the research report's own
    empirical measurement of the real maximum concurrent-candidate count over the full canonical history,
    with a documented safety margin -- not picked in advance, not tuned to shape behavior."""
    contract_version: str = RANGE_HIERARCHICAL_VNEXT_CONTRACT_VERSION
    # Evidence-derived final default (research report section 12): full canonical-history measurement
    # (2011-07-26 warmup through end of data, 355,696 M15 bars, 15+ years) with this cap held generously
    # high (500, effectively unbounded) found max concurrent active macro candidates = 4, p99 = 2, and
    # zero registry-capacity refusals. 16 = 4x the measured historical maximum: a genuine, meaningfully
    # bounded cap (not "effectively unbounded" like the measurement value), sized with headroom for market
    # conditions outside this specific 15-year window rather than picked to shape behavior.
    max_active_macro_candidates: int = 16


RANGE_HIERARCHICAL_VNEXT_NORMATIVE_CONFIG_ID = ConfigVNext().config_id()


# ═══════════════════════════════════ result ═══════════════════════════════════

@_dc.dataclass(frozen=True, slots=True)
class RangeSemanticResultVNext:
    """The CANONICAL view (mandate section 7 / architecture doc section 11): a single selected macro,
    chosen deterministically from all currently active candidates, matching the shape a MarketState
    consumer expects from any prior RANGE version. `active_macro_count`/`active_macro_ids` expose the full
    registry size for diagnostics without requiring a consumer to know the producer's internal shape --
    `RangeSemanticProducerVNext.active_macros` (a property, mirroring `macro_history`) gives full detail
    when needed."""
    available: bool
    bar_index: int
    ts_close: int
    macro_id: int | None
    macro_reason: str
    macro_state: str | None
    macro_weakening_reason: str | None
    macro_boundary_upper: float | None
    macro_boundary_lower: float | None
    macro_confirm_ts: int | None
    macro_role: str | None
    macro_continued_from_id: int | None
    regime: str | None
    internal_id: int | None
    internal_reason: str | None
    internal_state: str | None
    internal_boundary_upper: float | None
    internal_boundary_lower: float | None
    internal_role: str | None
    active_macro_count: int
    active_macro_ids: tuple[int, ...]
    active_internal_count: int
    config_id: str
    contract_version: str


def _state_label_vnext(reason: str) -> str | None:
    """Shared MACRO/INTERNAL state label -- `TOO_SHORT_MACRO`/`TOO_SHORT_INTERNAL` and
    `OK_RANGE_MACRO`/`OK_RANGE_INTERNAL` are the only depth-specific reason codes; every other reason code
    used here is depth-agnostic already (shared between the two depths in v4.3/v4.4)."""
    if reason == BETWEEN_EPISODES:
        return None
    if reason in (ESTABLISHING_FEW_SWINGS, ATR_UNAVAILABLE, RANGE_CANDIDATE_PRESENT):
        return "CANDIDATE"
    if reason in (TOO_SHORT_MACRO, "TOO_SHORT_INTERNAL"):
        return "FORMING"
    if reason in (OK_RANGE_MACRO, "OK_RANGE_INTERNAL"):
        return "CONFIRMED"
    if reason in (RANGE_WEAKENING, WEAKENING_RECOVERED, NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT, SWEEP_CONFIRMED):
        return "WEAKENING"
    if reason in (ZONES_DEGENERATE, ZONES_INVERTED, BREAKOUT_ACCEPTED, WEAKENING_PERSISTENCE_TERMINATED,
                 CANDIDATE_SUPERSEDED_BY_MERGE, CANDIDATE_ABANDONED_PRICE_MOVED_ON):
        return "TERMINATED"
    return None


# ═══════════════════════════════════ producer -- fresh, not a v4.4 subclass (see architecture doc section 1) ═══════════════════════════════════

class RangeSemanticProducerVNext:
    """Bounded multi-candidate MACRO registry. See `VE_RANGE_LIFECYCLE_VNEXT_ARCHITECTURE.md` for the full
    design rationale of every decision below -- this class implements it, not re-derives it."""

    def __init__(self, config: ConfigVNext) -> None:
        self._cfg = config
        self._n = 0
        self._last_atr: float | None = None
        k = config.K_struct
        from collections import deque
        self._wh: deque[float] = deque(maxlen=2 * k + 1)
        self._wl: deque[float] = deque(maxlen=2 * k + 1)
        self._registry = Registry()

        # ── the bounded multi-candidate MACRO registry (architecture doc section 3) ──
        self._active_macros: dict[int, StructureV44] = {}
        self._macro_excursions: dict[int, Excursion] = {}
        self._macro_reversal_watches: dict[int, dict[str, Any]] = {}

        # ── per-macro INTERNAL (architecture doc section 8): at most one internal per active macro ──
        self._active_internals: dict[int, Structure] = {}
        self._internal_excursions: dict[int, Excursion] = {}
        self._internal_reversal_watches: dict[int, dict[str, Any]] = {}

        self._pending_up: tuple[int, float] | None = None
        self._pending_dn: tuple[int, float] | None = None

        # promotion/regime: single global window, unchanged from v4.3/v4.4 (architecture doc section 9)
        self._promo_direction: int | None = None
        self._promo_broken_boundary: float | None = None
        self._promo_external_count = 0
        self._promo_original_id: int | None = None
        self._promo_fired = False
        self._regime: str | None = None

        self._macro_history: deque[StructureV44] = deque(maxlen=64)
        self._internal_history: deque[Structure] = deque(maxlen=64)
        self._awaiting_role: dict[int, StructureV44 | Structure] = {}
        self._last_ended_macro_id: int | None = None
        self._last_ended_internal_id: int | None = None

        # episode identity for CONTINUATION (sequential, unchanged from v4.4 -- architecture doc section 5.2)
        self._last_terminated_macro_zone: tuple[float, float] | None = None
        self._last_terminated_macro_end_ts: int | None = None
        self._last_terminated_macro_id: int | None = None
        self._last_terminated_macro_end_reason: str | None = None

    # ── diagnostics: full registry detail, mirrors `macro_history`'s own property convention ──
    @property
    def active_macros(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._active_macros[mid].snapshot() for mid in sorted(self._active_macros))

    @property
    def macro_history(self) -> tuple[dict[str, Any], ...]:
        return tuple(s.snapshot() for s in self._macro_history)

    @property
    def internal_history(self) -> tuple[dict[str, Any], ...]:
        return tuple(s.snapshot() for s in self._internal_history)

    # ── fractal swing detection -- byte-identical to v4.3/v4.4, global, not per-candidate ──
    def _detect_confirmed_swings(self, i: int) -> list[tuple[int, float, bool]]:
        k = self._cfg.K_struct
        out: list[tuple[int, float, bool]] = []
        if len(self._wh) == 2 * k + 1:
            c = k
            ch = self._wh[c]
            if ch == max(self._wh) and list(self._wh).count(ch) == 1:
                out.append((i - k, ch, True))
            cl = self._wl[c]
            if cl == min(self._wl) and list(self._wl).count(cl) == 1:
                out.append((i - k, cl, False))
        return out

    def _clear_pending(self) -> None:
        self._pending_up = None
        self._pending_dn = None

    # ── generalized episode identity (architecture doc section 5): MERGE now reachable ──
    def _episode_identity_for_new_macro_multi(self, candidate_zone: tuple[float, float], i: int
                                              ) -> tuple[str, int | None]:
        best_iou = 0.0
        best_id: int | None = None
        for mid in sorted(self._active_macros):
            st = self._active_macros[mid]
            lz_lower, lz_upper = st.boundary_lower, st.boundary_upper
            if lz_lower is None or lz_upper is None:
                continue
            v = _iou(candidate_zone, (lz_lower, lz_upper))
            if v >= self._cfg.IOU_CONTINUE and v > best_iou:
                best_iou = v
                best_id = mid
        if best_id is not None:
            return "MERGE", best_id
        if (self._last_terminated_macro_zone is not None
                and self._last_terminated_macro_end_reason != BREAKOUT_ACCEPTED
                and self._last_terminated_macro_end_ts is not None
                and (i - self._last_terminated_macro_end_ts) <= self._cfg.GAP_MAX):
            if _iou(candidate_zone, self._last_terminated_macro_zone) >= self._cfg.IOU_CONTINUE:
                return "CONTINUATION", self._last_terminated_macro_id
        return "REPLACEMENT", None

    # ── retire a macro candidate that a newer, overlapping one has superseded (architecture doc section 6) ──
    def _supersede_macro(self, mid: int, i: int, events: list[RangeEventV43],
                         reason: str = CANDIDATE_SUPERSEDED_BY_MERGE) -> None:
        st = self._active_macros.pop(mid)
        st.end_ts = i
        st.end_reason = reason
        self._registry.kill(mid)
        self._macro_history.append(st)
        events.append(RangeEventV43(kind=reason, bar_index=i, structure_id=mid, depth=Depth.MACRO.name,
                                    reason_codes=(reason,), not_yet_available=()))
        self._macro_excursions.pop(mid, None)
        self._macro_reversal_watches.pop(mid, None)
        self._retire_internal_for(mid, i, reason, events, is_kill=False)

    # ── structural (NOT age-based) supersession: candidate abandoned by current price action
    # (architecture doc section 6-extension; mandate section 5's own "has current structure causally
    # superseded the old candidate?" question) -- see research report for why this was added after the
    # exploratory measurement found registry occupancy higher than the pure overlap-merge mechanism alone
    # resolves. Reuses ONLY the existing `tol_cluster*atr_ref` acceptance-tolerance distance (the same
    # quantity `Cluster.offer` already uses to decide whether a swing extends a cluster) -- no new
    # threshold. Never fires on the sole active candidate (protects the isolated slow-candidate case this
    # whole mandate exists for), and never fires unless a DIFFERENT active candidate is structurally
    # closer to the current price -- "superseded BY current structure", not "expired by elapsed time". ──
    def _retire_price_abandoned_candidates(self, i: int, close: float, events: list[RangeEventV43]) -> None:
        if len(self._active_macros) < 2:
            return
        distances: dict[int, float] = {}
        for mid, st in self._active_macros.items():
            if st.atr_ref is None or st.boundary_upper is None or st.boundary_lower is None:
                continue
            if close > st.boundary_upper:
                distances[mid] = close - st.boundary_upper
            elif close < st.boundary_lower:
                distances[mid] = st.boundary_lower - close
            else:
                distances[mid] = 0.0
        abandoned = []
        for mid in sorted(self._active_macros):
            st = self._active_macros[mid]
            if st.reached_confirmed or mid not in distances or st.atr_ref is None:
                continue
            tol = self._cfg.tol_cluster * st.atr_ref
            if distances[mid] <= tol:
                continue  # still within the same acceptance-tolerance band -- not abandoned
            closer_exists = any(oid != mid and distances.get(oid, float("inf")) < distances[mid]
                                for oid in distances)
            if closer_exists:
                abandoned.append(mid)
        for mid in abandoned:
            self._supersede_macro(mid, i, events, reason=CANDIDATE_ABANDONED_PRICE_MOVED_ON)

    def _retire_internal_for(self, macro_id: int, i: int, reason: str, events: list[RangeEventV43],
                             *, is_kill: bool) -> None:
        internal = self._active_internals.pop(macro_id, None)
        if internal is None:
            return
        internal.end_ts = i
        internal.end_reason = reason
        if is_kill:
            self._registry.kill(internal.structure_id)
        self._internal_history.append(internal)
        events.append(RangeEventV43(kind=reason, bar_index=i, structure_id=internal.structure_id,
                                    depth=Depth.INTERNAL.name, reason_codes=(reason,), not_yet_available=()))
        self._internal_excursions.pop(macro_id, None)
        self._internal_reversal_watches.pop(macro_id, None)
        self._last_ended_internal_id = internal.structure_id

    def _offer_swing_everywhere(self, i: int, price: float, is_high: bool, events: list[RangeEventV43]) -> None:
        side = "high" if is_high else "low"

        # step 1 (architecture doc section 4.1): try every active macro, oldest first, stop at first accept
        accepted_by_macro_id: int | None = None
        for mid in sorted(self._active_macros):
            st = self._active_macros[mid]
            ok, _ = offer_swing(st, price, side, _as_v43_cfg(self._cfg))
            if ok:
                st.record_touch_v44(i, is_high)
                accepted_by_macro_id = mid
                break

        # each macro's own internal (if any) also gets offered the swing -- unchanged per-structure mechanic
        for mid, internal in self._active_internals.items():
            offer_swing(internal, price, side, _as_v43_cfg(self._cfg))

        if self._promo_direction is not None and self._promo_broken_boundary is not None:
            beyond = (price > self._promo_broken_boundary if self._promo_direction == 1
                     else price < self._promo_broken_boundary)
            if beyond:
                self._promo_external_count += 1
                self._maybe_promote(i, events)

        if accepted_by_macro_id is not None:
            return  # absorbed by an existing candidate -- no new candidate proposed for this swing

        # step: could this swing extend/seed an INTERNAL inside some active macro instead?
        for mid in sorted(self._active_macros):
            if mid in self._active_internals:
                continue
            st = self._active_macros[mid]
            boundary = st.up.center if is_high else st.dn.center
            if boundary is not None and abs(price - boundary) <= self._cfg.tol_cluster:
                # re-test of this macro's own (possibly frozen) boundary -- not new information, same
                # filter v4.4 already applies (architecture doc section 4.3)
                return

        if is_high:
            self._pending_up = (i, price)
        else:
            self._pending_dn = (i, price)
        if self._pending_up is None or self._pending_dn is None:
            return
        cand_start = min(self._pending_up[0], self._pending_dn[0])
        cand_end = i
        cand_hi = self._pending_up[1]
        cand_lo = self._pending_dn[1]

        # try INTERNAL parent assignment first (architecture doc section 8): each active macro, ascending
        # id, via the unmodified `assign_level` containment check -- first one that actually contains wins
        for mid in sorted(self._active_macros):
            if mid in self._active_internals:
                continue
            parent = self._active_macros[mid]
            depth, refuse_reason, parent_id = assign_level(cand_start, cand_end, cand_lo, cand_hi, parent,
                                                           _as_v43_cfg(self._cfg))
            if depth is Depth.INTERNAL:
                new_id = self._registry.new_id()
                st_internal = Structure(structure_id=new_id, depth=depth, parent_structure_id=parent_id,
                                        start_ts=cand_start)
                st_internal.atr_ref = self._last_atr
                offer_swing(st_internal, self._pending_up[1], "high", _as_v43_cfg(self._cfg))
                offer_swing(st_internal, self._pending_dn[1], "low", _as_v43_cfg(self._cfg))
                self._clear_pending()
                st_internal.predecessor_id = self._last_ended_internal_id
                self._last_ended_internal_id = None
                self._active_internals[mid] = st_internal
                return

        # not contained by any active macro's own INTERNAL slot -- try forming a NEW MACRO candidate
        action, target_id = self._episode_identity_for_new_macro_multi((cand_lo, cand_hi), i)
        if action == "REPLACEMENT" and len(self._active_macros) >= self._cfg.max_active_macro_candidates:
            events.append(RangeEventV43(kind=REGISTRY_CAPACITY_REFUSED, bar_index=i, structure_id=None,
                                        depth=Depth.MACRO.name, reason_codes=(REGISTRY_CAPACITY_REFUSED,),
                                        not_yet_available=()))
            self._clear_pending()
            return

        new_id = self._registry.new_id()
        st_macro = StructureV44(structure_id=new_id, depth=Depth.MACRO, parent_structure_id=None,
                                start_ts=cand_start, trailing_window=self._cfg.W)
        st_macro.atr_ref = self._last_atr
        offer_swing(st_macro, self._pending_up[1], "high", _as_v43_cfg(self._cfg))
        offer_swing(st_macro, self._pending_dn[1], "low", _as_v43_cfg(self._cfg))
        self._clear_pending()

        if action == "MERGE":
            assert target_id is not None
            self._supersede_macro(target_id, i, events)
            st_macro.continued_from_id = target_id
            events.append(RangeEventV43(kind=EPISODE_MERGED, bar_index=i, structure_id=new_id,
                                        depth=Depth.MACRO.name, reason_codes=(EPISODE_MERGED,),
                                        not_yet_available=()))
        elif action == "CONTINUATION":
            st_macro.predecessor_id = self._last_ended_macro_id
            self._last_ended_macro_id = None
            st_macro.continued_from_id = target_id
            events.append(RangeEventV43(kind=EPISODE_CONTINUATION, bar_index=i, structure_id=new_id,
                                        depth=Depth.MACRO.name, reason_codes=(EPISODE_CONTINUATION,),
                                        not_yet_available=()))
        else:
            st_macro.predecessor_id = self._last_ended_macro_id
            self._last_ended_macro_id = None
            events.append(RangeEventV43(kind=EPISODE_REPLACEMENT, bar_index=i, structure_id=new_id,
                                        depth=Depth.MACRO.name, reason_codes=(EPISODE_REPLACEMENT,),
                                        not_yet_available=()))
        self._active_macros[new_id] = st_macro
        self._regime = None

    # ── per-candidate termination helpers (architecture doc section 6) ──
    def _kill_macro(self, mid: int, i: int, reason: str, events: list[RangeEventV43]) -> None:
        st = self._active_macros.pop(mid)
        st.end_ts = i
        st.end_reason = reason
        self._registry.kill(mid)
        self._macro_history.append(st)
        events.append(RangeEventV43(kind=reason, bar_index=i, structure_id=mid, depth=Depth.MACRO.name,
                                    reason_codes=(reason,), not_yet_available=()))
        self._last_ended_macro_id = mid
        self._record_macro_termination_for_episode_identity(st, reason)
        self._macro_excursions.pop(mid, None)
        self._macro_reversal_watches.pop(mid, None)
        self._retire_internal_for(mid, i, "TOO_SHORT_INTERNAL", events, is_kill=True)

    def _close_macro_via_breakout(self, mid: int, i: int, side: str, events: list[RangeEventV43]) -> None:
        st = self._active_macros.pop(mid)
        st.end_ts = i
        st.end_reason = BREAKOUT_ACCEPTED
        st.breakout_side = side
        self._macro_history.append(st)
        events.append(RangeEventV43(kind=BREAKOUT_ACCEPTED, bar_index=i, structure_id=mid,
                                    depth=Depth.MACRO.name, reason_codes=(BREAKOUT_ACCEPTED,),
                                    not_yet_available=(), boundary=side))
        self._last_ended_macro_id = mid
        self._record_macro_termination_for_episode_identity(st, BREAKOUT_ACCEPTED)
        self._macro_excursions.pop(mid, None)
        self._macro_reversal_watches.pop(mid, None)
        self._retire_internal_for(mid, i, BREAKOUT_ACCEPTED, events, is_kill=False)
        self._promo_direction = 1 if side == "upper" else -1
        self._promo_broken_boundary = st.boundary_upper if side == "upper" else st.boundary_lower
        self._promo_fired = False
        self._promo_external_count = 0
        self._promo_original_id = mid
        self._awaiting_role[mid] = st

    def _terminate_macro_weakening_persistence(self, mid: int, i: int, events: list[RangeEventV43]) -> None:
        self._kill_macro(mid, i, WEAKENING_PERSISTENCE_TERMINATED, events)

    def _record_macro_termination_for_episode_identity(self, st: StructureV44, reason: str) -> None:
        if st.boundary_upper is not None and st.boundary_lower is not None:
            self._last_terminated_macro_zone = (st.boundary_lower, st.boundary_upper)
        else:
            self._last_terminated_macro_zone = None
        self._last_terminated_macro_end_ts = st.end_ts
        self._last_terminated_macro_id = st.structure_id
        self._last_terminated_macro_end_reason = reason

    # ── per-candidate MACRO step -- v4.4's own `_step_macro` body, parameterized instead of singleton ──
    def _step_macro_candidate(self, mid: int, i: int, high: float, low: float, close: float,
                              events: list[RangeEventV43]) -> str:
        st = self._active_macros[mid]
        kill = degeneracy_check(st, _as_v43_cfg(self._cfg))
        if kill in (ZONES_INVERTED, ZONES_DEGENERATE):
            self._kill_macro(mid, i, kill, events)
            return kill

        zones = st.zones(self._cfg.w_atr) if st.reached_confirmed else None
        if zones is None:
            return self._evaluate_macro_formation(st, i, events)

        (up_lo, up_hi), (lo_lo, lo_hi) = zones
        excursion = self._macro_excursions.get(mid)
        excursion_active_this_bar = False
        excursion_reported_reason: str | None = None

        if excursion is not None:
            side = "upper" if excursion.direction == 1 else "lower"
            outside = close > up_hi if side == "upper" else close < lo_lo
            kind, nya = excursion.observe(i, outside, _as_v43_cfg(self._cfg))
            excursion_active_this_bar = True
            if kind == BREAKOUT_ACCEPTED:
                self._close_macro_via_breakout(mid, i, side, events)
                return BREAKOUT_ACCEPTED
            if kind == SWEEP_CONFIRMED:
                events.append(RangeEventV43(kind=SWEEP_CONFIRMED, bar_index=i, structure_id=mid,
                                            depth=Depth.MACRO.name, reason_codes=(SWEEP_CONFIRMED,),
                                            not_yet_available=(), boundary=side))
                ref_side = "upper" if excursion.direction == -1 else "lower"
                self._macro_reversal_watches[mid] = {
                    "excursion": excursion.snapshot(), "structure_id": mid, "ref_side": ref_side,
                    "ref_swing": (st.up.center if ref_side == "upper" else st.dn.center),
                    "ref_confirm_ts": st.confirm_ts}
                self._macro_excursions.pop(mid, None)
                excursion_active_this_bar = False
                if st.weakening_reason == "EXCURSION_PENDING":
                    st.weakening_reason = None
                    events.append(RangeEventV43(kind=WEAKENING_RECOVERED, bar_index=i, structure_id=mid,
                                                depth=Depth.MACRO.name, reason_codes=(WEAKENING_RECOVERED,),
                                                not_yet_available=()))
                    excursion_reported_reason = WEAKENING_RECOVERED
                else:
                    excursion_reported_reason = SWEEP_CONFIRMED
            else:
                events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=mid, depth=Depth.MACRO.name,
                                            reason_codes=(), not_yet_available=nya, boundary=side))
                excursion_reported_reason = NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
        elif close > up_hi or close < lo_lo:
            side = "upper" if close > up_hi else "lower"
            ex = Excursion(open_bar=i - 1, direction=1 if side == "upper" else -1)
            self._macro_excursions[mid] = ex
            excursion_active_this_bar = True
            kind, nya = ex.observe(i, True, _as_v43_cfg(self._cfg))
            st.weakening_reason = "EXCURSION_PENDING"
            events.append(RangeEventV43(kind=RANGE_WEAKENING, bar_index=i, structure_id=mid,
                                        depth=Depth.MACRO.name, reason_codes=(RANGE_WEAKENING,),
                                        not_yet_available=()))
            if kind == BREAKOUT_ACCEPTED:
                self._close_macro_via_breakout(mid, i, side, events)
                return BREAKOUT_ACCEPTED
            events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=mid, depth=Depth.MACRO.name,
                                        reason_codes=(), not_yet_available=nya, boundary=side))
            excursion_reported_reason = NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT

        er = efficiency_ratio(st._trailing_closes)
        rnd = relative_net_displacement(st._trailing_closes, st.boundary_upper, st.boundary_lower)
        trailing_reported_reason: str | None = None

        if st.weakening_reason == "TRAILING_DEGRADATION":
            st._weakening_bars += 1
            recovered = (er <= self._cfg.ER_max and rnd <= self._cfg.RND_max)
            if recovered:
                st.weakening_reason = None
                st._weakening_bars = 0
                events.append(RangeEventV43(kind=WEAKENING_RECOVERED, bar_index=i, structure_id=mid,
                                            depth=Depth.MACRO.name, reason_codes=(WEAKENING_RECOVERED,),
                                            not_yet_available=()))
                trailing_reported_reason = WEAKENING_RECOVERED
            elif st._weakening_bars >= self._cfg.WEAKENING_MAX_BARS:
                self._terminate_macro_weakening_persistence(mid, i, events)
                return WEAKENING_PERSISTENCE_TERMINATED
            else:
                trailing_reported_reason = RANGE_WEAKENING
        elif not excursion_active_this_bar:
            degraded = (er > self._cfg.ER_weakening or rnd > self._cfg.RND_weakening)
            if degraded:
                st.weakening_reason = "TRAILING_DEGRADATION"
                st._weakening_bars = 1
                events.append(RangeEventV43(kind=RANGE_WEAKENING, bar_index=i, structure_id=mid,
                                            depth=Depth.MACRO.name, reason_codes=(RANGE_WEAKENING,),
                                            not_yet_available=()))
                trailing_reported_reason = RANGE_WEAKENING

        if excursion_reported_reason is not None:
            return excursion_reported_reason
        if trailing_reported_reason is not None:
            return trailing_reported_reason
        return OK_RANGE_MACRO

    # ── v4.4's own `_evaluate_macro_formation`, byte-identical body (T2/T3 gate) -- per-candidate `st`
    # already parameterized in the original, so this is a direct copy, not a redesign ──
    def _evaluate_macro_formation(self, st: StructureV44, i: int, events: list[RangeEventV43]) -> str:
        bu, bl = st.boundary_upper, st.boundary_lower
        if bu is None or bl is None or st.atr_ref is None:
            return ATR_UNAVAILABLE if st.atr_ref is None else ESTABLISHING_FEW_SWINGS
        if len(st.up.members) < self._cfg.n_touch or len(st.dn.members) < self._cfg.n_touch:
            return ESTABLISHING_FEW_SWINGS
        if not st._candidate_present_emitted:
            st._candidate_present_emitted = True
            events.append(RangeEventV43(kind=RANGE_CANDIDATE_PRESENT, bar_index=i, structure_id=st.structure_id,
                                        depth=Depth.MACRO.name, reason_codes=(RANGE_CANDIDATE_PRESENT,),
                                        not_yet_available=()))
        if i - st.start_ts < self._cfg.d_macro:
            return TOO_SHORT_MACRO
        er = efficiency_ratio(st._trailing_closes)
        if er > self._cfg.ER_max:
            return INSUFFICIENT_EFFICIENCY
        trav = traversal_count(st._trailing_closes, bu, bl)
        if trav < self._cfg.MIN_TRAVERSALS:
            return INSUFFICIENT_TRAVERSAL
        rnd = relative_net_displacement(st._trailing_closes, bu, bl)
        if rnd > self._cfg.RND_max:
            return EXCESSIVE_NET_DISPLACEMENT
        alt = alternation_rate(st.touches_in_window(i, self._cfg.W))
        if alt is None or alt < self._cfg.ALT_MIN:
            events.append(RangeEventV43(kind=INSUFFICIENT_ALTERNATION_EVIDENCE, bar_index=i,
                                        structure_id=st.structure_id, depth=Depth.MACRO.name,
                                        reason_codes=(INSUFFICIENT_ALTERNATION_EVIDENCE,), not_yet_available=()))
        st.reached_confirmed = True
        if st.confirm_ts is None:
            st.confirm_ts = i
        st.up.frozen = True
        st.dn.frozen = True
        if self._promo_direction is not None:
            self._promo_direction = None
            self._promo_broken_boundary = None
            self._promo_external_count = 0
        events.append(RangeEventV43(kind=OK_RANGE_MACRO, bar_index=i, structure_id=st.structure_id,
                                    depth=Depth.MACRO.name, reason_codes=(OK_RANGE_MACRO,), not_yet_available=()))
        self._resolve_role_if_watched(st, i)
        return OK_RANGE_MACRO

    def _resolve_role_if_watched(self, successor: StructureV44 | Structure, i: int) -> None:
        pred_id = successor.predecessor_id
        if pred_id is None or pred_id not in self._awaiting_role:
            return
        pred = self._awaiting_role.pop(pred_id)
        if pred.structure_id == self._promo_original_id and self._promo_fired:
            promo_dir_upper = self._promo_direction == 1
            role = ("TREND_CONTINUATION_CONFIRMED" if (successor.breakout_side == "upper") == promo_dir_upper
                   else "TREND_EXHAUSTION_CONFIRMED")
        else:
            role = "ACCUMULATION_CONFIRMED" if pred.breakout_side == "upper" else "DISTRIBUTION_CONFIRMED"
        pred.assign_role(role, i)

    def _maybe_promote(self, i: int, events: list[RangeEventV43]) -> None:
        if self._promo_direction is None or self._promo_fired:
            return
        if self._promo_external_count < self._cfg.n_external_swings:
            return
        from .range_semantic_v4_3 import promotion_check
        ok, reason = promotion_check(
            p1_left_frozen_boundary=True, p2_breakout_accepted=True,
            external_swings_confirmed=self._promo_external_count, p4_previous_closed_and_kept=True,
            cfg=_as_v43_cfg(self._cfg))
        if ok:
            self._promo_fired = True
            self._regime = "TREND_UP" if self._promo_direction == 1 else "TREND_DOWN"
            events.append(RangeEventV43(kind="IS_TREND_MACRO", bar_index=i, structure_id=self._promo_original_id,
                                        depth=Depth.MACRO.name, reason_codes=("IS_TREND_MACRO",),
                                        not_yet_available=()))

    def _end_ts_for_macro(self, structure_id: int) -> int | None:
        if structure_id in self._active_macros:
            return None
        for s in self._macro_history:
            if s.structure_id == structure_id:
                return s.end_ts
        return -1

    def _check_reversal_watch_macro(self, mid: int, i: int, close: float, events: list[RangeEventV43]) -> None:
        watch = self._macro_reversal_watches.get(mid)
        if watch is None:
            return
        ex = Excursion.restore(watch["excursion"])
        episode_end_ts = self._end_ts_for_macro(watch["structure_id"])
        ok, reason = sweep_reversal_confirmed(
            ex, i, close, watch["ref_swing"], watch["ref_confirm_ts"], episode_end_ts)
        if ok:
            events.append(RangeEventV43(kind="LIQUIDITY_SWEEP_REVERSAL", bar_index=i,
                                        structure_id=watch["structure_id"], depth=Depth.MACRO.name,
                                        reason_codes=("LIQUIDITY_SWEEP_REVERSAL",), not_yet_available=()))
            self._macro_reversal_watches.pop(mid, None)
        elif reason == "REVERSAL_WINDOW_EXPIRED":
            self._macro_reversal_watches.pop(mid, None)

    # ── canonical selection for the exposed MarketState view (architecture doc section 11) ──
    def _select_canonical_macro(self, close: float) -> StructureV44 | None:
        confirmed = [self._active_macros[mid] for mid in sorted(self._active_macros)
                    if self._active_macros[mid].reached_confirmed]
        if not confirmed:
            return None
        containing = [st for st in confirmed
                     if st.boundary_lower is not None and st.boundary_upper is not None
                     and st.boundary_lower <= close <= st.boundary_upper]
        if containing:
            return min(containing, key=lambda st: st.structure_id)

        def _distance(st: StructureV44) -> float:
            bl, bu = st.boundary_lower, st.boundary_upper
            if bl is None or bu is None:
                return float("inf")
            if close < bl:
                return bl - close
            if close > bu:
                return close - bu
            return 0.0
        return min(confirmed, key=lambda st: (_distance(st), st.structure_id))

    def observe(self, *, ts_close: int, open_: float, high: float, low: float, close: float,
               atr: float | None) -> tuple[RangeSemanticResultVNext, list[RangeEventV43]]:
        i = self._n
        self._n += 1
        self._wh.append(high)
        self._wl.append(low)
        self._last_atr = atr
        events: list[RangeEventV43] = []

        if atr is not None:
            for st in self._active_macros.values():
                st.atr_ref = atr
            for internal in self._active_internals.values():
                internal.atr_ref = atr

        for sw_bar, price, is_high in self._detect_confirmed_swings(i):
            self._offer_swing_everywhere(sw_bar, price, is_high, events)

        for st in self._active_macros.values():
            st.push_close_v44(i, close)
        for internal in self._active_internals.values():
            internal.push_close(close)

        # snapshot the id list BEFORE stepping -- a candidate's own step can remove OTHER candidates this
        # bar (merge supersession), never itself out from under this loop's own current entry
        macro_reasons: dict[int, str] = {}
        for mid in sorted(self._active_macros):
            if mid not in self._active_macros:
                continue  # already removed this bar (superseded by an earlier candidate's own merge)
            macro_reasons[mid] = self._step_macro_candidate(mid, i, high, low, close, events)

        for mid in list(self._macro_reversal_watches):
            self._check_reversal_watch_macro(mid, i, close, events)

        self._retire_price_abandoned_candidates(i, close, events)

        internal_reasons: dict[int, str] = {}
        for mid in sorted(self._active_internals):
            internal_reasons[mid] = self._step_internal_candidate(mid, i, high, low, close, events)

        canonical = self._select_canonical_macro(close)
        canonical_internal: Structure | None = None
        canonical_internal_reason = BETWEEN_EPISODES
        if canonical is not None and canonical.structure_id in self._active_internals:
            canonical_internal = self._active_internals[canonical.structure_id]
            canonical_internal_reason = internal_reasons.get(canonical.structure_id, BETWEEN_EPISODES)

        if canonical is not None:
            macro_reason = macro_reasons.get(canonical.structure_id, BETWEEN_EPISODES)
        elif macro_reasons:
            # no CONFIRMED macro exists this bar -- deterministically report the oldest (lowest id)
            # currently-active macro's own reason, rather than an arbitrary one
            macro_reason = macro_reasons[min(macro_reasons)]
        else:
            macro_reason = BETWEEN_EPISODES
        macro_state = (self._regime if (canonical is None and self._regime is not None)
                       else _state_label_vnext(macro_reason))

        result = RangeSemanticResultVNext(
            available=atr is not None, bar_index=i, ts_close=ts_close,
            macro_id=canonical.structure_id if canonical else None,
            macro_reason=macro_reason, macro_state=macro_state,
            macro_weakening_reason=canonical.weakening_reason if canonical else None,
            macro_boundary_upper=canonical.boundary_upper if canonical else None,
            macro_boundary_lower=canonical.boundary_lower if canonical else None,
            macro_confirm_ts=canonical.confirm_ts if canonical else None,
            macro_role=canonical.role if canonical else None,
            macro_continued_from_id=canonical.continued_from_id if canonical else None,
            regime=self._regime if canonical is None else None,
            internal_id=canonical_internal.structure_id if canonical_internal else None,
            internal_reason=canonical_internal_reason,
            internal_state=_state_label_vnext(canonical_internal_reason) if canonical_internal else None,
            internal_boundary_upper=canonical_internal.boundary_upper if canonical_internal else None,
            internal_boundary_lower=canonical_internal.boundary_lower if canonical_internal else None,
            internal_role=canonical_internal.role if canonical_internal else None,
            active_macro_count=len(self._active_macros),
            active_macro_ids=tuple(sorted(self._active_macros)),
            active_internal_count=len(self._active_internals),
            config_id=self._cfg.config_id(), contract_version=self._cfg.contract_version)
        return result, events

    def _step_internal_candidate(self, mid: int, i: int, high: float, low: float, close: float,
                                 events: list[RangeEventV43]) -> str:
        internal = self._active_internals.get(mid)
        if internal is None:
            return BETWEEN_EPISODES
        kill = degeneracy_check(internal, _as_v43_cfg(self._cfg))
        if kill in (ZONES_INVERTED, ZONES_DEGENERATE):
            self._retire_internal_for(mid, i, kill, events, is_kill=True)
            return kill
        zones = internal.zones(self._cfg.w_atr) if internal.reached_confirmed else None
        if zones is not None:
            (up_lo, up_hi), (lo_lo, lo_hi) = zones
            excursion = self._internal_excursions.get(mid)
            if excursion is not None:
                side = "upper" if excursion.direction == 1 else "lower"
                outside = close > up_hi if side == "upper" else close < lo_lo
                kind, nya = excursion.observe(i, outside, _as_v43_cfg(self._cfg))
                if kind == BREAKOUT_ACCEPTED:
                    internal2 = self._active_internals.pop(mid)
                    internal2.end_ts = i
                    internal2.end_reason = BREAKOUT_ACCEPTED
                    internal2.breakout_side = side
                    self._internal_history.append(internal2)
                    events.append(RangeEventV43(kind=BREAKOUT_ACCEPTED, bar_index=i,
                                                structure_id=internal2.structure_id, depth=Depth.INTERNAL.name,
                                                reason_codes=(BREAKOUT_ACCEPTED,), not_yet_available=(),
                                                boundary=side))
                    self._last_ended_internal_id = internal2.structure_id
                    self._internal_excursions.pop(mid, None)
                    self._awaiting_role[internal2.structure_id] = internal2
                    return BREAKOUT_ACCEPTED
                events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=internal.structure_id,
                                            depth=Depth.INTERNAL.name, reason_codes=(), not_yet_available=nya,
                                            boundary=side))
                return NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
            if close > up_hi or close < lo_lo:
                side = "upper" if close > up_hi else "lower"
                ex = Excursion(open_bar=i - 1, direction=1 if side == "upper" else -1)
                self._internal_excursions[mid] = ex
                kind, nya = ex.observe(i, True, _as_v43_cfg(self._cfg))
                events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=internal.structure_id,
                                            depth=Depth.INTERNAL.name, reason_codes=(), not_yet_available=nya,
                                            boundary=side))
                return NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
        from .range_semantic_v4_3 import evaluate_candidate_with_n_touch
        reason = evaluate_candidate_with_n_touch(internal, i, _as_v43_cfg(self._cfg))
        if reason == "OK_RANGE_INTERNAL" and not internal.reached_confirmed:
            internal.reached_confirmed = True
            if internal.confirm_ts is None:
                internal.confirm_ts = i
            internal.up.frozen = True
            internal.dn.frozen = True
            events.append(RangeEventV43(kind=reason, bar_index=i, structure_id=internal.structure_id,
                                        depth=Depth.INTERNAL.name, reason_codes=(reason,), not_yet_available=()))
            self._resolve_role_if_watched(internal, i)
        return reason

    # ── snapshot / restore ──
    def snapshot_state(self) -> dict[str, Any]:
        from collections import deque as _dq
        return {
            "contract_version": self._cfg.contract_version, "config_id": self._cfg.config_id(),
            "implementation_fingerprint": RANGE_HIERARCHICAL_VNEXT_IMPLEMENTATION_FINGERPRINT,
            "n": self._n, "wh": list(self._wh), "wl": list(self._wl), "last_atr": self._last_atr,
            "registry": self._registry.snapshot(),
            "active_macros": {mid: st.snapshot() for mid, st in self._active_macros.items()},
            "active_internals": {mid: it.snapshot() for mid, it in self._active_internals.items()},
            "macro_excursions": {mid: ex.snapshot() for mid, ex in self._macro_excursions.items()},
            "internal_excursions": {mid: ex.snapshot() for mid, ex in self._internal_excursions.items()},
            "macro_reversal_watches": {mid: dict(w) for mid, w in self._macro_reversal_watches.items()},
            "internal_reversal_watches": {mid: dict(w) for mid, w in self._internal_reversal_watches.items()},
            "pending_up": list(self._pending_up) if self._pending_up is not None else None,
            "pending_dn": list(self._pending_dn) if self._pending_dn is not None else None,
            "promo_direction": self._promo_direction, "promo_broken_boundary": self._promo_broken_boundary,
            "promo_external_count": self._promo_external_count, "promo_original_id": self._promo_original_id,
            "promo_fired": self._promo_fired, "regime": self._regime,
            "macro_history": [s.snapshot() for s in self._macro_history],
            "internal_history": [s.snapshot() for s in self._internal_history],
            "awaiting_role": {k: v.snapshot() for k, v in self._awaiting_role.items()},
            "last_ended_macro_id": self._last_ended_macro_id,
            "last_ended_internal_id": self._last_ended_internal_id,
            "last_terminated_macro_zone": (list(self._last_terminated_macro_zone)
                                           if self._last_terminated_macro_zone else None),
            "last_terminated_macro_end_ts": self._last_terminated_macro_end_ts,
            "last_terminated_macro_id": self._last_terminated_macro_id,
            "last_terminated_macro_end_reason": self._last_terminated_macro_end_reason,
        }

    def restore_state(self, st: dict[str, Any]) -> None:
        if (st.get("contract_version") != self._cfg.contract_version
                or st.get("config_id") != self._cfg.config_id()
                or st.get("implementation_fingerprint") != RANGE_HIERARCHICAL_VNEXT_IMPLEMENTATION_FINGERPRINT):
            raise ContractErrorV43(SNAPSHOT_CONTRACT_MISMATCH)
        from collections import deque
        fresh = RangeSemanticProducerVNext(self._cfg)
        k = self._cfg.K_struct
        fresh._n = st["n"]
        fresh._wh = deque(st["wh"], maxlen=2 * k + 1)
        fresh._wl = deque(st["wl"], maxlen=2 * k + 1)
        fresh._last_atr = st["last_atr"]
        fresh._registry = Registry.restore(st["registry"])
        fresh._active_macros = {int(mid): StructureV44.restore(v) for mid, v in st["active_macros"].items()}
        fresh._active_internals = {int(mid): Structure.restore(v) for mid, v in st["active_internals"].items()}
        fresh._macro_excursions = {int(mid): Excursion.restore(v) for mid, v in st["macro_excursions"].items()}
        fresh._internal_excursions = {
            int(mid): Excursion.restore(v) for mid, v in st["internal_excursions"].items()}
        fresh._macro_reversal_watches = {int(mid): dict(v) for mid, v in st["macro_reversal_watches"].items()}
        fresh._internal_reversal_watches = {
            int(mid): dict(v) for mid, v in st["internal_reversal_watches"].items()}
        pu, pd = st["pending_up"], st["pending_dn"]
        fresh._pending_up = (pu[0], pu[1]) if pu is not None else None
        fresh._pending_dn = (pd[0], pd[1]) if pd is not None else None
        fresh._promo_direction = st["promo_direction"]
        fresh._promo_broken_boundary = st["promo_broken_boundary"]
        fresh._promo_external_count = st["promo_external_count"]
        fresh._promo_original_id = st["promo_original_id"]
        fresh._promo_fired = st["promo_fired"]
        fresh._regime = st["regime"]
        fresh._macro_history = deque((StructureV44.restore(s) for s in st["macro_history"]), maxlen=64)
        fresh._internal_history = deque((Structure.restore(s) for s in st["internal_history"]), maxlen=64)
        fresh._awaiting_role = {
            int(k2): (StructureV44.restore(v) if v.get("depth") == Depth.MACRO.value else Structure.restore(v))
            for k2, v in st["awaiting_role"].items()}
        fresh._last_ended_macro_id = st["last_ended_macro_id"]
        fresh._last_ended_internal_id = st["last_ended_internal_id"]
        ltz = st["last_terminated_macro_zone"]
        fresh._last_terminated_macro_zone = tuple(ltz) if ltz else None
        fresh._last_terminated_macro_end_ts = st["last_terminated_macro_end_ts"]
        fresh._last_terminated_macro_id = st["last_terminated_macro_id"]
        fresh._last_terminated_macro_end_reason = st["last_terminated_macro_end_reason"]
        self.__dict__ = fresh.__dict__


RANGE_HIERARCHICAL_VNEXT_IMPLEMENTATION_FINGERPRINT = "vnext-implementation-freeze-2026-08-22"

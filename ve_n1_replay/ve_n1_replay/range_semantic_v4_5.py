"""RANGE HIERARCHICAL V4.5 -- stale-candidate LIVENESS recovery ATTEMPT (mandate
`VE-RANGE-V4-5-STALE-CANDIDATE-RECOVERY-001`). **STATUS: `RANGE_V4_5_RECOVERY_BLOCKED` -- validated UNSAFE,
NOT SUPPORTED, NOT deployed, NOT a v4.4 replacement.** Both mechanisms below were built entirely from
already-frozen v4.4 quantities (zero new config fields) and correctly reproduce the two real stuck-candidate
shapes they were designed for (see the delivery report). But mandatory negative-control validation --
running each mechanism, unmodified, against every one of the 187 real macro structures that DID reach
`CONFIRMED` across the full available history (2011-2026), checking whether it would have fired at any bar
strictly BEFORE that genuine confirmation -- found BOTH mechanisms fire far too often on real, converging,
eventually-successful formations: H-ONE-SIDED would have prematurely killed **69 of 187 (36.9%)** real
confirmations (median just 24 bars after the age gate opens, sometimes only a handful of bars before the
structure would have confirmed on its own); H-PERSISTENCE would have prematurely killed **23 of 187
(12.3%)** (up to 12,226 bars -- over 127 days -- before some of those structures went on to confirm
normally). This is the SAME over-eager-release failure mode ("RANGE-context over-segmentation") that
closed the prior T-STALE attempt, discovered here at a materially LARGER scale via a more thorough
negative control than that attempt received (checked against ALL real confirmations, not a small sample).
Kept in the repository, fully implemented and tested, for the same reason `range_semantic_v4_4_1.py`
(T-STALE) was kept after ITS rejection: so a future attempt does not have to re-invent and re-discover
either of these two specific failure modes. Fully additive over `range_semantic_v4_4.py` -- that file is
byte-untouched by this work (verified by `git diff`, recorded in the delivery report), and over
`range_semantic_v4_3.py` (also byte-untouched, inherited transitively). `RangeSemanticProducerV44`,
`ConfigV44`, and `RANGE_HIERARCHICAL_V4_4_NORMATIVE_CONFIG_ID` remain the permanently frozen v4.4 baseline
(`3bb61cf`) -- this module never imports anything from it that it modifies, only reuses.

ROOT CAUSE (mandate section 2's own confirmed diagnosis, independently re-derived here from source, not
merely cited -- see the delivery report's own reproduction section for the exact real-lineage proof):
MACRO is single-active-at-a-time by construction (`forming_macro = self._active_macro is None`, v4.3-
inherited, unchanged). A macro candidate is admitted to that slot the instant `assign_level()` resolves a
swing pair to `Depth.MACRO` -- BEFORE any confirmation gate runs. `Cluster.offer()` (v4.3, unchanged)
accepts a swing only within `tol_cluster * atr_ref` of the cluster's OWN CURRENT median; a rejected swing
is simply dropped, with no side effect. In a persistently directional market, swings on the trend side
keep landing near the established cluster and keep getting accepted, while swings on the counter-trend
side keep landing further away as the trend continues and keep getting rejected -- so that side can
remain below `n_touch` indefinitely. `_evaluate_macro_formation` returns `ESTABLISHING_FEW_SWINGS` for
exactly this state (`len(up.members) < n_touch or len(dn.members) < n_touch`), and `degeneracy_check`
(the ONLY other exit for a never-confirmed candidate) only catches INVERTED or TOO-NARROW zones -- it has
no way to recognize "one side stopped growing because price left the area," since it only looks at the
CURRENT geometry, never at growth history. The candidate is then structurally invisible to the two
existing lifecycle exits (confirmation-then-breakout-or-weakening; degeneracy) and blocks the slot.

Confirmed on the real lineage, using the canonical from-2011 warmup (the ONE warmup convention every
number in this module and the delivery report is validated against -- this state machine is fully
incremental/path-dependent, so an inconsistent warmup start silently produces a DIFFERENT structure at
the same calendar date; see the delivery report's own methodology section) and checked against
`reached_confirmed` directly, not merely "occupied the slot a long time" (a distinction this module's own
earlier design phase initially missed -- see the delivery report's own methodology-correction section):
across the full 2011-2026 history only 4 real macro structures ever occupy the slot for >30 days without
EVER reaching `CONFIRMED`. macro_id 893 (started 2025-06-29) sat with its "dn" side frozen at exactly 1
touch (the founding swing) while "up" grew to 4 touches over 106 days before release -- the H-ONE-SIDED
shape this module's first mechanism targets. macro_id 770 (started 2015-07-20) is the dominant real
example of the SECOND, qualitatively different shape that H-ONE-SIDED alone cannot reach: BOTH sides grew
substantially (up to 89 touches, dn to 67) within its first ~50 bars, satisfying `n_touch` on both sides
almost immediately -- yet the candidate remained genuinely unconfirmed for **3548.94 days (9.7 years)**,
finally releasing (`INSUFFICIENT_TRAVERSAL`) on 2025-04-07, because T3's ER/traversal/RND discrimination
gate, not the touch-count gate, kept failing for nearly a decade. `degeneracy_check` cannot see this
either -- its geometry stayed valid (non-inverted, non-degenerate) throughout. The other 2 real
never-confirmed episodes >30 days (macro_id 969, 175.39 days; macro_id 945, 76.09 days, both in
2025-2026) share this same both-sided shape. Two other structures WERE originally, wrongly, cited here as
additional real "genuinely stuck" H-ONE-SIDED examples (macro_id 748 and others among a set of 9
long-DURATION candidates) -- corrected, disclosed rather than silently fixed: those candidates merely took
33-254 days to confirm; checked directly against `reached_confirmed`, all 8 of the other 9 originally-
cited long-duration episodes turn out to have confirmed normally. Firing on them was never a validated
success -- it was, in retrospect, an early, unrecognized instance of the exact false-positive failure mode
this module's own negative control later found systematically (delivery report reproduction/negative-
control sections). Only DURATION was checked at first; DURATION alone does not distinguish "stuck forever"
from "genuinely slow" -- `reached_confirmed` is the only reliable signal, and using it is what the
negative control in section 6.1 of the delivery report actually does.

WHY THIS IS NOT A RETUNE (mandate section 5): every existing v4.4 numeric threshold --
`n_touch`, `d_macro`, `W`, `ER_max`/`ER_weakening`, `RND_max`/`RND_weakening`, `ALT_MIN`,
`MIN_TRAVERSALS`, `WEAKENING_MAX_BARS`, `IOU_CONTINUE`, `GAP_MAX`, `K_reentry`, `K_struct`,
`n_external_swings`, `w_atr` -- is REUSED VERBATIM, at its existing frozen value. `ConfigV45` below adds
**zero** new fields. TWO lifecycle checks are introduced (`_candidate_stagnation_reason`, covering the two
shapes above), and each is built entirely from already-frozen v4.4 quantities:
  - H-ONE-SIDED (`CANDIDATE_ONE_SIDED_TERMINATED`): `d_macro`, `n_touch`, `ALT_MIN`, plus the
    already-existing `alternation_rate`/`StructureV44.touches_in_window` -- the SAME accepted-touch
    evidence and the SAME alternation machinery T3 already computes as SUPPORTING_ONLY confirmation
    evidence (`INSUFFICIENT_ALTERNATION_EVIDENCE`), applied one lifecycle stage earlier (pre-confirmation)
    to a question v4.4 never asked pre-confirmation: not "should this confirm", but "has this candidate
    demonstrated, with resolved (not merely absent) evidence, that it is one-sided rather than two-sided".
  - H-PERSISTENCE (`CANDIDATE_PERSISTENCE_TERMINATED`): `d_macro`, `n_touch`, `WEAKENING_MAX_BARS` --
    the SAME "how long is too long to sit unresolved" threshold v4.4 already applies POST-confirmation
    (`StructureV44._weakening_bars` vs `WEAKENING_MAX_BARS`), applied PRE-confirmation for the first time
    to a symmetric question: not "has a CONFIRMED range degraded for too long", but "has a T3-ELIGIBLE
    CANDIDATE sat unresolved for too long".
No threshold was searched, tuned, or calibrated to produce a target coverage number; both were validated
TOGETHER, after the fact, against every real macro candidate lasting >30 days in an early, DURATION-only
scan of a 2011-2022 window (delivery report reproduction section): H-ONE-SIDED alone resolves 6 of 9,
H-PERSISTENCE alone resolves 5 of 9, and their misses are DISJOINT -- together they resolve 9 of 9,
including macro_id 770 in under half a day (versus what a full-history run later showed is 3548.94 days
unresolved under v4.4). **This 9/9 figure is a POSITIVE-only, duration-based check and is NOT, by itself,
evidence of safety** -- 8 of those 9 candidates turned out, on later, correct `reached_confirmed`-based
checking, to be genuine eventual confirmations, not permanently-stuck candidates; "firing on them" was
therefore not unambiguously a success. The finding that actually matters, and that determines this
module's status, is the real-data NEGATIVE control described below.

RELATIONSHIP TO THE PRIOR, REJECTED T-STALE ATTEMPT (`range_semantic_v4_4_1.py`, closed
`GENERALIZATION_NOT_SUPPORTED` -- read in full before designing this module, not assumed): T-STALE tracked
*rejected* touches directly and fired on a *calibrated* alternation-count threshold
(`STALE_MIN_ALTERNATION=3`) over that rejection evidence -- a genuinely NEW, ungrounded parameter, later
confirmed (Red Team's fresh-blind validation, `8e550ae`) to have no value that worked on both sides of a
dual-sided acceptance bar, and to over-fire specifically on ALTERNATING rejection patterns, causing
RANGE-context over-segmentation. Both mechanisms in this module track ACCEPTED touches (or existing
trailing-close-derived quantities) only -- evidence already tracked, already used elsewhere -- and
introduce no calibrated count of their own: `ALT_MIN` and `WEAKENING_MAX_BARS` are each v4.4's own
existing thresholds, not new ones chosen for this purpose. **This did NOT make either mechanism safe.**
Avoiding a new/calibrated parameter rules out ONE way to overfit (picking a number that happens to work on
the cases you looked at); it does not, by itself, guarantee the reused number's ORIGINAL domain
(post-confirmation persistence for `WEAKENING_MAX_BARS`; a different confirmation-support role for
`ALT_MIN`) transfers safely to this NEW, pre-confirmation domain. It does not. Direct negative-control
validation (delivery report) found both mechanisms reproduce T-STALE's own failure mode -- RANGE-context
over-segmentation via premature release of genuinely-converging candidates -- at a larger measured scale
than T-STALE's own rejection was based on.

NOT FAIL-OPEN ON ABSENCE OF EVIDENCE, BUT NOT SAFE ON PRESENT EVIDENCE EITHER (mandate section 21, and
the limits of that section's own guarantee -- disclosed, not glossed over): `alternation_rate` returns
`None` (not `0.0`) when fewer than 3 touches are on record -- exactly v4.4's own existing "insufficient
evidence" semantics -- and H-ONE-SIDED never treats that absence as evidence of stagnation;
`_candidate_stagnation_reason` returns `None` whenever `alternation_rate` is `None`. This guarantee is
real but narrower than it first appears: it only protects a candidate that has NOT YET accumulated enough
touch evidence. It does NOT protect a candidate that HAS accumulated evidence pointing one-sided
EARLY IN A FORMATION THAT WOULD OTHERWISE HAVE CONFIRMED SHORTLY AFTER -- and the negative-control
validation shows this second case is common in real data (median first-fire offset of just 24 bars among
the 69 real structures affected), not rare. (A separate, TRUE structural fact -- that H-ONE-SIDED's
alternation value, whenever it resolves at all in this domain, is always exactly `0.0`, since a side below
`n_touch` can by construction contribute zero tags -- was initially, WRONGLY, treated as evidence the
MECHANISM was safe; it only proves the trigger VALUE is deterministic, not that the firing CONDITION is
rare or reserved for genuinely-stuck candidates. See `tests/test_v4_5_liveness.py`'s module docstring for
the corrected argument.) H-PERSISTENCE is fail-closed in the same limited sense (never fires before
`st.reached_confirmed` is checked, never fires before BOTH sides have ACTUALLY satisfied `n_touch`, its
streak resets to zero the instant a genuinely different structure becomes active) and is UNSAFE in the
same broader sense (fires on real, eventually-confirming candidates whose OWN pre-confirmation eligible
period legitimately exceeds `WEAKENING_MAX_BARS` -- which the negative control shows is not an edge case
either)."""
from __future__ import annotations

import dataclasses as _dc
from typing import Any

from .range_semantic_v4_3 import (
    BETWEEN_EPISODES,
    BREAKOUT_ACCEPTED,
    ConfigNotRatifiedErrorV43,
    ContractErrorV43,
    Depth,
    Excursion,
    NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT,
    OK_RANGE_MACRO,
    RangeEventV43,
    Registry,
    SNAPSHOT_CONTRACT_MISMATCH,
    Structure,
    SWEEP_CONFIRMED,
    ZONES_DEGENERATE,
    ZONES_INVERTED,
    degeneracy_check,
)
from .range_semantic_v4_4 import (
    ConfigV44,
    RANGE_WEAKENING,
    REASONS_V44,
    RangeSemanticProducerV44,
    RangeSemanticResultV44,
    StructureV44,
    WEAKENING_PERSISTENCE_TERMINATED,
    WEAKENING_RECOVERED,
    _as_v43_cfg,
    alternation_rate,
    efficiency_ratio,
    relative_net_displacement,
)

__all__ = [
    # re-exported from V4.3/V4.4 -- needed by `range_engine_v4_5.py` (mypy --strict --no-implicit-reexport,
    # same convention `range_semantic_v4_4.__all__` already uses)
    "ConfigNotRatifiedErrorV43", "ContractErrorV43", "RangeEventV43", "SNAPSHOT_CONTRACT_MISMATCH",
    "RangeSemanticResultV44",
    # V4.5, own
    "RANGE_HIERARCHICAL_V4_5_CONTRACT_VERSION",
    "CANDIDATE_ONE_SIDED_TERMINATED",
    "CANDIDATE_PERSISTENCE_TERMINATED",
    "REASONS_V45",
    "ConfigV45",
    "RANGE_HIERARCHICAL_V4_5_NORMATIVE_CONFIG_ID",
    "RangeSemanticProducerV45",
    "RANGE_HIERARCHICAL_V4_5_IMPLEMENTATION_FINGERPRINT",
]

# ═══════════════════════════════════ identity ═══════════════════════════════════

RANGE_HIERARCHICAL_V4_5_CONTRACT_VERSION = "range-hierarchical-v4.5"

# -- 2 additive reason codes -- the 40 from V4.4 remain valid, unrenumbered. Two distinct codes (not one
# umbrella code) because they are two structurally disjoint failure modes reached via disjoint evidence,
# matching the project's existing convention of a distinct reason code per distinct lifecycle cause (e.g.
# WEAKENING's own several termination/recovery codes) -- see `_candidate_stagnation_reason`'s docstring.
CANDIDATE_ONE_SIDED_TERMINATED = "CANDIDATE_ONE_SIDED_TERMINATED"
CANDIDATE_PERSISTENCE_TERMINATED = "CANDIDATE_PERSISTENCE_TERMINATED"

REASONS_V45: tuple[str, ...] = REASONS_V44 + (CANDIDATE_ONE_SIDED_TERMINATED, CANDIDATE_PERSISTENCE_TERMINATED)
assert len(REASONS_V45) == 42, f"40 V4.4 + 2 V4.5 = 42 expected, got {len(REASONS_V45)}"
assert len(set(REASONS_V45)) == 42, "duplicate reason code between V4.4 and V4.5"


# ═══════════════════════════════════ configuration -- ZERO new fields ═══════════════════════════════════

@_dc.dataclass(frozen=True, slots=True)
class ConfigV45(ConfigV44):
    """Subclasses `ConfigV44` -- all 21 inherited fields keep their frozen v4.4 values unchanged (only
    `contract_version`'s default differs). No new field exists: the liveness fix reuses `d_macro`,
    `n_touch`, and `ALT_MIN` verbatim (see module docstring). `config_id()` is inherited unmodified --
    `self.__dataclass_fields__` on a `ConfigV45` instance already includes the full merged field set
    (verified empirically before relying on this, same check `ConfigV441` already established as safe for
    this exact inheritance shape), so the existing formula covers the complete V4.5 set with no override."""
    contract_version: str = RANGE_HIERARCHICAL_V4_5_CONTRACT_VERSION


RANGE_HIERARCHICAL_V4_5_NORMATIVE_CONFIG_ID = ConfigV45().config_id()


# ═══════════════════════════════════ producer V4.5 -- subclasses RangeSemanticProducerV44 ═══════════════════════════════════

class RangeSemanticProducerV45(RangeSemanticProducerV44):
    """No new `Structure` subclass exists -- the liveness check reads only fields/methods `StructureV44`
    already has (`up`/`dn` clusters, `reached_confirmed`, `start_ts`, `structure_id`, `touches_in_window`);
    no per-structure state needs adding (contrast T-STALE's `StructureV441`, which needed a second,
    separate rejected-touch deque this module has no use for). The one piece of new state this module
    needs -- "how many consecutive bars has the CURRENT candidate sat T3-eligible without confirming" --
    cannot be derived retroactively from existing per-touch bookkeeping (the founding touch pair is never
    tagged into `_touch_tags`, so there is no recorded bar index for "when did this side first reach
    n_touch"; see module docstring). It is therefore tracked as NEW PRODUCER-LEVEL instance state (a
    counter, not a threshold -- the counter's STOP value is `WEAKENING_MAX_BARS`, an existing frozen
    config field), the same pattern `StructureV44._weakening_bars` already establishes for the symmetric
    POST-confirmation case. This is why `__init__` is overridden (T-STALE's own precedent for adding
    tracking state this way).

    Inherits UNCHANGED: `_detect_confirmed_swings`, `_deepest_open`, `_clear_pending`,
    `_offer_swing_everywhere`, `_episode_identity_for_new_macro`, `_kill_internal`,
    `_close_internal_via_breakout`, `_kill_macro`, `_close_macro_via_breakout`,
    `_terminate_macro_weakening_persistence`, `_record_macro_termination_for_episode_identity`,
    `_end_ts_for`, `_check_reversal_watch`, `_resolve_role_if_watched`, `_maybe_promote`,
    `_state_label_internal`, `_channel_or_state_label`, `_macro_state_label`, `_step_internal`,
    `_evaluate_macro_formation`, `observe`, `macro_history`/`internal_history` -- all correct on a V4.5
    instance via ordinary dynamic dispatch (the same mechanism `RangeSemanticProducerV441` already
    verified for this exact class hierarchy).

    Overrides EXACTLY 4 things: `__init__` (2 new tracking fields, see above), `_step_macro` (one new
    priority-ordered check, immediately after T-KILL and before T2/T3 -- the same insertion point T-STALE
    used, for a never-confirmed candidate only), `snapshot_state`/`restore_state` (V4.5 identity, PLUS the
    2 new tracking fields -- these must round-trip for restart determinism, mandate section 22)."""

    def __init__(self, config: ConfigV45) -> None:
        super().__init__(config)
        self._cfg: ConfigV45 = config
        # tracks, for whichever macro candidate is CURRENTLY active, how many consecutive bars it has
        # sat T3-eligible (both sides >= n_touch, age >= d_macro) without reaching confirmation. Reset to
        # 0 the instant a DIFFERENT structure becomes active (id mismatch) -- see H-PERSISTENCE below.
        self._t3_eligible_structure_id: int | None = None
        self._t3_eligible_streak: int = 0

    # ── the liveness invariant (mandate section 7): NO non-confirmed macro candidate may block the active
    # slot indefinitely. TWO structurally disjoint checks, covering the two ways a d_macro+-aged, never-
    # confirmed candidate can be stuck -- disjoint BY CONSTRUCTION (a candidate either still lacks n_touch
    # on at least one side, or has satisfied n_touch on both; `Cluster.members` only ever grows via
    # `.append()`, so "both satisfied" is monotonic once reached -- exactly one branch below is ever live
    # for a given structure on a given bar, never both, never neither, once age >= d_macro):
    #
    #   H-ONE-SIDED:   at least one side has not yet reached n_touch. Full-lifetime accepted-touch
    #                  evidence (the SAME evidence and the SAME `alternation_rate` machinery T3 already
    #                  computes as SUPPORTING_ONLY confirmation evidence) resolves to a clearly one-sided
    #                  growth pattern (`alt < ALT_MIN`, v4.4's own existing confirmation-time threshold).
    #   H-PERSISTENCE: both sides HAVE reached n_touch (T3-eligible in the touch-count sense) but the
    #                  candidate has sat that way, unconfirmed, for `WEAKENING_MAX_BARS` consecutive bars
    #                  -- the same "how long is too long to remain unresolved" concept v4.4 already
    #                  enforces POST-confirmation (`_weakening_bars` vs `WEAKENING_MAX_BARS`), applied
    #                  PRE-confirmation for the first time. Needed because touch alternation alone proves
    #                  insufficient: a candidate can satisfy n_touch on both sides very early (ruling out
    #                  H-ONE-SIDED for its entire remaining life) yet still never pass T3's ER/traversal/
    #                  RND discrimination gate -- observed on the real lineage (macro_id 770: both sides
    #                  well past n_touch within the first ~50 bars, still unconfirmed 3548.94 days later --
    #                  9.7 years, finally releasing 2025-04-07 -- the full-history figure; an early,
    #                  2011-2022-truncated probe underestimated this as "2356+ days, still active").
    #
    # Both checks were validated together against every real macro candidate lasting >30 days in an early,
    # DURATION-ONLY 2011-2022 canonical-warmup scan of the UNMODIFIED v4.4 baseline (delivery report
    # reproduction section): H-ONE-SIDED alone resolves 6 of 9, H-PERSISTENCE alone resolves 5 of 9, their
    # MISSES ARE DISJOINT -- together they resolve 9 of 9, including the most severe real case (770,
    # unresolved for 9.7 years) in under half a day. NOTE (disclosed, not hidden): 8 of those 9 candidates
    # were LATER found, via proper reached_confirmed checking, to be genuine eventual confirmations, not
    # permanently-stuck ones -- this 9/9 figure is a positive-only check, not evidence of safety; see the
    # real-data negative control (delivery report section 6.1) for the finding that actually matters.
    # Neither check uses any value not already frozen in `ConfigV44`.
    def _candidate_stagnation_reason(self, st: StructureV44, i: int) -> str | None:
        if st.reached_confirmed:
            return None
        age = i - st.start_ts
        if age < self._cfg.d_macro:
            return None
        both_satisfied = (len(st.up.members) >= self._cfg.n_touch
                           and len(st.dn.members) >= self._cfg.n_touch)

        if not both_satisfied:
            all_tags = st.touches_in_window(i, age + 1)  # every accepted touch since this structure's start
            alt = alternation_rate(all_tags)
            if alt is None:
                return None  # absence of evidence is never evidence of stagnation (fail-closed, not fail-open)
            return CANDIDATE_ONE_SIDED_TERMINATED if alt < self._cfg.ALT_MIN else None

        if st.structure_id != self._t3_eligible_structure_id:
            self._t3_eligible_structure_id = st.structure_id
            self._t3_eligible_streak = 0
        self._t3_eligible_streak += 1
        return CANDIDATE_PERSISTENCE_TERMINATED if self._t3_eligible_streak >= self._cfg.WEAKENING_MAX_BARS else None

    # ── copy of V4.4's own _step_macro + one new priority-ordered check (see above) -- everything else
    # byte-identical to RangeSemanticProducerV44._step_macro ──
    def _step_macro(self, i: int, high: float, low: float, close: float, events: list[RangeEventV43]) -> str:
        st = self._active_macro
        if st is None:
            return BETWEEN_EPISODES
        kill = degeneracy_check(st, _as_v43_cfg(self._cfg))
        if kill in (ZONES_INVERTED, ZONES_DEGENERATE):
            self._kill_macro(st, i, kill, events)
            return kill

        zones = st.zones(self._cfg.w_atr) if st.reached_confirmed else None
        if zones is None:
            # ▼▼▼ the only insertion relative to V4.4 -- reuses _kill_macro unchanged (generic on
            # reason: str), no new termination mechanics, same episode-identity bookkeeping as any other
            # termination ▼▼▼
            reason = self._candidate_stagnation_reason(st, i)
            if reason is not None:
                self._kill_macro(st, i, reason, events)
                return reason
            # ▲▲▲ end insertion ▲▲▲
            return self._evaluate_macro_formation(st, i, events)

        (up_lo, up_hi), (lo_lo, lo_hi) = zones
        excursion = self._macro_excursion
        excursion_active_this_bar = False
        excursion_reported_reason: str | None = None

        if excursion is not None:
            side = "upper" if excursion.direction == 1 else "lower"
            outside = close > up_hi if side == "upper" else close < lo_lo
            kind, nya = excursion.observe(i, outside, _as_v43_cfg(self._cfg))
            excursion_active_this_bar = True
            if kind == BREAKOUT_ACCEPTED:
                self._close_macro_via_breakout(st, i, side, events)
                return BREAKOUT_ACCEPTED
            if kind == SWEEP_CONFIRMED:
                events.append(RangeEventV43(kind=SWEEP_CONFIRMED, bar_index=i, structure_id=st.structure_id,
                                            depth=Depth.MACRO.name, reason_codes=(SWEEP_CONFIRMED,),
                                            not_yet_available=(), boundary=side))
                ref_side = "upper" if excursion.direction == -1 else "lower"
                self._macro_reversal_watch = {"excursion": excursion.snapshot(), "structure_id": st.structure_id,
                                              "ref_side": ref_side,
                                              "ref_swing": (st.up.center if ref_side == "upper" else st.dn.center),
                                              "ref_confirm_ts": st.confirm_ts}
                self._macro_excursion = None
                excursion_active_this_bar = False
                if st.weakening_reason == "EXCURSION_PENDING":
                    st.weakening_reason = None
                    events.append(RangeEventV43(kind=WEAKENING_RECOVERED, bar_index=i, structure_id=st.structure_id,
                                                depth=Depth.MACRO.name, reason_codes=(WEAKENING_RECOVERED,),
                                                not_yet_available=()))
                    excursion_reported_reason = WEAKENING_RECOVERED
                else:
                    excursion_reported_reason = SWEEP_CONFIRMED
            else:
                events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=st.structure_id,
                                            depth=Depth.MACRO.name, reason_codes=(), not_yet_available=nya,
                                            boundary=side))
                excursion_reported_reason = NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT
        elif close > up_hi or close < lo_lo:
            side = "upper" if close > up_hi else "lower"
            ex = Excursion(open_bar=i - 1, direction=1 if side == "upper" else -1)
            self._macro_excursion = ex
            excursion_active_this_bar = True
            kind, nya = ex.observe(i, True, _as_v43_cfg(self._cfg))
            st.weakening_reason = "EXCURSION_PENDING"
            events.append(RangeEventV43(kind=RANGE_WEAKENING, bar_index=i, structure_id=st.structure_id,
                                        depth=Depth.MACRO.name, reason_codes=(RANGE_WEAKENING,),
                                        not_yet_available=()))
            if kind == BREAKOUT_ACCEPTED:
                self._close_macro_via_breakout(st, i, side, events)
                return BREAKOUT_ACCEPTED
            events.append(RangeEventV43(kind=kind, bar_index=i, structure_id=st.structure_id,
                                        depth=Depth.MACRO.name, reason_codes=(), not_yet_available=nya,
                                        boundary=side))
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
                events.append(RangeEventV43(kind=WEAKENING_RECOVERED, bar_index=i, structure_id=st.structure_id,
                                            depth=Depth.MACRO.name, reason_codes=(WEAKENING_RECOVERED,),
                                            not_yet_available=()))
                trailing_reported_reason = WEAKENING_RECOVERED
            elif st._weakening_bars >= self._cfg.WEAKENING_MAX_BARS:
                self._terminate_macro_weakening_persistence(st, i, events)
                return WEAKENING_PERSISTENCE_TERMINATED
            else:
                trailing_reported_reason = RANGE_WEAKENING
        elif not excursion_active_this_bar:
            degraded = (er > self._cfg.ER_weakening or rnd > self._cfg.RND_weakening)
            if degraded:
                st.weakening_reason = "TRAILING_DEGRADATION"
                st._weakening_bars = 1
                events.append(RangeEventV43(kind=RANGE_WEAKENING, bar_index=i, structure_id=st.structure_id,
                                            depth=Depth.MACRO.name, reason_codes=(RANGE_WEAKENING,),
                                            not_yet_available=()))
                trailing_reported_reason = RANGE_WEAKENING

        if excursion_reported_reason is not None:
            return excursion_reported_reason
        if trailing_reported_reason is not None:
            return trailing_reported_reason
        return OK_RANGE_MACRO

    # ── V4.5 identity -- cannot be inherited unmodified (see class docstring) ──
    def snapshot_state(self) -> dict[str, Any]:
        base = super().snapshot_state()
        base["contract_version"] = self._cfg.contract_version
        base["config_id"] = self._cfg.config_id()
        base["implementation_fingerprint"] = RANGE_HIERARCHICAL_V4_5_IMPLEMENTATION_FINGERPRINT
        base["t3_eligible_structure_id"] = self._t3_eligible_structure_id
        base["t3_eligible_streak"] = self._t3_eligible_streak
        return base

    def restore_state(self, st: dict[str, Any]) -> None:
        """Atomic, same discipline as `RangeSemanticProducerV44.restore_state` (built in a separate
        SCRATCH instance, `self` untouched until the final swap) -- reproduced here (not called through
        `super()`) because the parent explicitly constructs `RangeSemanticProducerV44`/`StructureV44` by
        name inside its own body, so a `super()` call would silently rebuild a V4.4 instance and lose
        nothing V4.5-specific (there is no new field) but would ALSO silently accept a V4.4-identified
        snapshot as if it were V4.5 -- the identity check itself is exactly what must not be inherited."""
        if (st.get("contract_version") != self._cfg.contract_version
                or st.get("config_id") != self._cfg.config_id()
                or st.get("implementation_fingerprint") != RANGE_HIERARCHICAL_V4_5_IMPLEMENTATION_FINGERPRINT):
            raise ContractErrorV43(SNAPSHOT_CONTRACT_MISMATCH)
        from collections import deque
        fresh = RangeSemanticProducerV45(self._cfg)
        fresh._t3_eligible_structure_id = st["t3_eligible_structure_id"]
        fresh._t3_eligible_streak = st["t3_eligible_streak"]
        k = self._cfg.K_struct
        fresh._n = st["n"]
        fresh._wh = deque(st["wh"], maxlen=2 * k + 1)
        fresh._wl = deque(st["wl"], maxlen=2 * k + 1)
        fresh._last_atr = st["last_atr"]
        fresh._registry = Registry.restore(st["registry"])
        fresh._active_macro = StructureV44.restore(st["active_macro"]) if st["active_macro"] else None
        fresh._active_internal = Structure.restore(st["active_internal"]) if st["active_internal"] else None
        fresh._macro_excursion = Excursion.restore(st["macro_excursion"]) if st["macro_excursion"] else None
        fresh._internal_excursion = (
            Excursion.restore(st["internal_excursion"]) if st["internal_excursion"] else None)
        fresh._macro_reversal_watch = st["macro_reversal_watch"]
        fresh._internal_reversal_watch = st["internal_reversal_watch"]
        fresh._pending_up = tuple(st["pending_up"]) if st["pending_up"] else None
        fresh._pending_dn = tuple(st["pending_dn"]) if st["pending_dn"] else None
        fresh._promo_direction = st["promo_direction"]; fresh._promo_broken_boundary = st["promo_broken_boundary"]
        fresh._promo_external_count = st["promo_external_count"]
        fresh._promo_original_id = st["promo_original_id"]
        fresh._promo_fired = st["promo_fired"]; fresh._regime = st["regime"]
        fresh._macro_history = deque((StructureV44.restore(s) for s in st["macro_history"]), maxlen=64)
        fresh._internal_history = deque((Structure.restore(s) for s in st["internal_history"]), maxlen=64)
        fresh._awaiting_role = {
            int(k2): (StructureV44.restore(v) if v.get("depth") == Depth.MACRO.value else Structure.restore(v))
            for k2, v in st["awaiting_role"].items()}
        fresh._last_ended_macro_id = st["last_ended_macro_id"]
        fresh._last_ended_internal_id = st["last_ended_internal_id"]
        fresh._last_terminated_macro_zone = (
            tuple(st["last_terminated_macro_zone"]) if st["last_terminated_macro_zone"] else None)
        fresh._last_terminated_macro_end_ts = st["last_terminated_macro_end_ts"]
        fresh._last_terminated_macro_id = st["last_terminated_macro_id"]
        fresh._last_terminated_macro_end_reason = st["last_terminated_macro_end_reason"]
        self.__dict__ = fresh.__dict__


# ═══════════════════════════════════ implementation fingerprint (computed AFTER the code is frozen) ═══════════════════════════════════
# Same procedure as V4.4/V4.4.1's own precedent: sha256 over the finalized source bytes of both V4.5 files
# (`range_semantic_v4_5.py` + `range_engine_v4_5.py`) computed after freeze, real hash recorded in the
# delivery report -- the constant below is a descriptive human label (date+mandate), not the raw digest,
# exactly the convention V4.3/V4.4/V4.4.1 already use. Any material change after this freeze must change it.
RANGE_HIERARCHICAL_V4_5_IMPLEMENTATION_FINGERPRINT = "v4-5-implementation-freeze-2026-08-22"

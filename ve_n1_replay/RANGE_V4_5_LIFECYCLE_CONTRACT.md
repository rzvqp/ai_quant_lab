# RANGE_V4_5_LIFECYCLE_CONTRACT

**Mandate**: `VE-RANGE-V4-5-STALE-CANDIDATE-RECOVERY-001`
**Contract version**: `range-hierarchical-v4.5`
**Implementation**: `ve_n1_replay/range_semantic_v4_5.py`, `ve_n1_replay/range_engine_v4_5.py`
**Lineage**: additive over frozen `range-hierarchical-v4.4` (`3bb61cf`), which remains permanently frozen
and byte-untouched.

> **STATUS: `RANGE_V4_5_RECOVERY_BLOCKED`.** Both mechanisms defined in this contract were built entirely
> from already-frozen v4.4 quantities and correctly reproduce the two real stuck-candidate shapes they
> target (section 4.1). Mandatory negative-control validation against all 187 real macro structures that
> reached `CONFIRMED` across the full available history (2011–2026) found BOTH mechanisms would have
> prematurely released a substantial fraction of them before they confirmed — H-ONE-SIDED 69/187 (36.9%),
> H-PERSISTENCE 23/187 (12.3%). A second, independent full-history episode regression confirms this at
> even larger scale: 69.0% of v4.4's real confirmed episodes (129/187) have no corresponding v4.5
> confirmation at all, replaced by 1,080 mostly-fragmentary new ones — reproducing, at materially larger
> measured scale, the exact `RANGE-context over-segmentation` failure mode that closed the prior T-STALE
> attempt. Neither mechanism, nor their OR combination (the union of two unsafe sets is not safe), is
> deployed. **v4.4 remains the frozen baseline; this contract is not a v4.4 replacement and is not handed
> to Alpha as approved evidence** (mandate section 26 — this was already true before the negative control
> ran; it remains true, now for a stronger reason). See section 4.3/11 for the full result and section 13
> for what this means for the mandate.

This document is kept, in full, as the RECORD of what was designed, why it looked principled, and exactly
how and why it failed — the same disposition `RANGE_V4_4_1_T_STALE...` artifacts have after T-STALE's own
rejection — so a future attempt does not re-invent and re-discover either failure mode from scratch.

## 1. The liveness invariant (mandate section 7)

> **No non-confirmed MACRO candidate may block the active slot indefinitely.**

MACRO remains single-active-at-a-time by construction (`forming_macro = self._active_macro is None`,
inherited unchanged from v4.3/v4.4 — never modified by this contract). v4.5 adds exactly **two** new
lifecycle exits for a candidate that has never reached `CONFIRMED`, alongside the two v4.4 already
provides (degeneracy KILL; and, for structures that DO reach `CONFIRMED`, breakout or
WEAKENING-persistence). Two exits, not one, because the real lineage surfaced two structurally distinct
ways a candidate gets stuck (section 4 below) that neither the existing v4.4 exits nor a single new check
can both reach.

## 2. Candidate lifecycle states (unchanged from v4.4)

`CANDIDATE` → `FORMING` → `CONFIRMED` → `WEAKENING` → `TERMINATED`, exactly the 5-state `MacroStateV44`
literal v4.4 already defines. v4.5 introduces no new state — only two new **termination reasons**
(`CANDIDATE_ONE_SIDED_TERMINATED`, `CANDIDATE_PERSISTENCE_TERMINATED`), each reachable only from
`CANDIDATE`/`FORMING` (i.e., before `reached_confirmed` is ever set True).

## 3. Lifecycle event reference

| Event | Owner | Trigger | Unchanged by v4.5? |
|---|---|---|---|
| Candidate creation | v4.3/v4.4, `_offer_swing_everywhere` | a swing pair resolves to `Depth.MACRO` via `assign_level` | Yes, byte-identical |
| Candidate continuation | v4.4, `_episode_identity_for_new_macro` | new candidate's zone overlaps (IoU ≥ `IOU_CONTINUE`) a recently-terminated macro's zone within `GAP_MAX` bars, and that termination wasn't `BREAKOUT_ACCEPTED` | Yes, byte-identical |
| Candidate invalidation (degeneracy) | v4.3, `degeneracy_check` + v4.4 `_kill_macro` | `ZONES_INVERTED` or `ZONES_DEGENERATE`, checked every bar unconditionally | Yes, byte-identical |
| **Candidate one-sided release (NEW, v4.5)** | v4.5, `_candidate_stagnation_reason` (H-ONE-SIDED branch) + v4.4 `_kill_macro` (reused, not reimplemented) | see section 4.2 | **New** |
| **Candidate persistence release (NEW, v4.5)** | v4.5, `_candidate_stagnation_reason` (H-PERSISTENCE branch) + v4.4 `_kill_macro` (reused, not reimplemented) | see section 4.3 | **New** |
| Confirmation | v4.4, `_evaluate_macro_formation` | `n_touch` both sides + `d_macro` age + ER/traversal/RND (T3) gates | Yes, byte-identical |
| Breakout termination | v4.4, `_close_macro_via_breakout` | post-confirmation excursion resolves `BREAKOUT_ACCEPTED` | Yes, byte-identical (only reachable post-confirmation, so never interacts with v4.5's new checks) |
| Weakening persistence termination | v4.4, `_terminate_macro_weakening_persistence` | post-confirmation `TRAILING_DEGRADATION` sustained `WEAKENING_MAX_BARS` | Yes, byte-identical |
| Slot release → new candidate admission | v4.3/v4.4, `forming_macro = self._active_macro is None` | any of the above terminations clear `self._active_macro` | Yes, byte-identical — this is the mechanism v4.5's new exits feed into, not a new mechanism itself |

## 4. Candidate stagnation release — the two new v4.5 mechanisms

### 4.1 Why two mechanisms, not one

The real lineage (canonical from-2011-warmup reproduction; see the delivery report's reproduction
section) surfaced two structurally disjoint shapes of "stuck candidate", disjoint **by construction**
because `Cluster.members` only ever grows (`.append()`, never shrinks), so "both sides have reached
`n_touch`" is a monotonic property — once true for a structure, it stays true for that structure's entire
remaining life:

- **H-ONE-SIDED** — at least one side has never reached `n_touch`. Real example (one of only 4 real
  structures across 2011–2026 that genuinely NEVER reach `CONFIRMED` and last >30 days — see below for why
  this qualifier matters): macro_id 893 (started 2025-06-29), "dn" frozen at 1 touch (the founding swing)
  for its entire 106-day life while "up" grew to 4.
- **H-PERSISTENCE** — both sides reached `n_touch` (often almost immediately), but the candidate still
  never satisfies T3's ER/traversal/RND discrimination gate. Dominant real example: macro_id 770 (started
  2015-07-20), up grew to 89 touches and dn to 67 within roughly the first 50 bars — yet remained
  genuinely unconfirmed for **3548.94 days (9.7 years)**, finally releasing on 2025-04-07.
  `degeneracy_check` cannot see this either — its geometry stayed valid (non-inverted, non-degenerate)
  throughout. 2 further real examples share this shape (macro_id 969, 175.39 days; macro_id 945, 76.09
  days, both 2025–2026).

**A methodology correction, disclosed rather than silently fixed**: both mechanisms were originally
validated (after the fact, not tuned to fit) against every real macro candidate lasting more than 30 days
in an EARLY, DURATION-ONLY scan of the canonical run: H-ONE-SIDED alone resolved 6 of 9 such episodes,
H-PERSISTENCE alone resolved 5 of 9, and the two sets of misses were exactly disjoint — together they
resolved all 9. **This was, in retrospect, an insufficient check**: it filtered candidates by DURATION
alone, not by whether they ever actually reached `CONFIRMED`. A later, correct check found 8 of those
original 9 "long episodes" (everything except macro_id 770) went on to confirm normally — they were
genuinely slow, real ranges, not permanently-stuck ones. Firing on them was therefore not a validated
success at all; it was an early, unrecognized instance of the exact false-positive failure mode the real
negative control (section 4.3 below) later found systematically, at scale, against all 187 real
confirmations. Only 4 real structures across the full 2011–2026 history are genuinely never-confirmed and
last >30 days: 770, 969, 893, 945, listed above.

Both checks live in one method, `_candidate_stagnation_reason(st, i) -> str | None`, returning the
specific reason code to terminate on, or `None` to keep waiting — never a bare boolean, so the caller
never has to re-derive which of the two fired.

### 4.2 H-ONE-SIDED: eligibility and trigger

**Eligibility** (gate, not trigger — mirrors the "age is a gate" principle the prior, rejected T-STALE
design already established as correct):
- `st.reached_confirmed is False` (a `CONFIRMED`/`WEAKENING` structure is structurally immune — the check
  is only reached inside `_step_macro`'s `zones is None` branch, which requires exactly this).
- `i - st.start_ts >= self._cfg.d_macro` — the SAME 29-bar floor v4.4 already requires before evaluating
  T3 confirmation gates at all. No new age threshold.
- At least one side (`up` or `dn`) has fewer than `n_touch` (existing, frozen = 2) accepted touches.

**Trigger** (structural, evidence-based — never fires on absence of evidence): the candidate's own
ACCEPTED-touch history (the identical evidence `alternation_rate`/`touches_in_window` already compute for
T3's SUPPORTING_ONLY `INSUFFICIENT_ALTERNATION_EVIDENCE` signal — reused verbatim, not reimplemented) —
queried over the candidate's ENTIRE lifetime so far (not a bounded recent window; see section 8 for why)
— has accumulated at least 3 touches (the same floor `alternation_rate` itself already requires to return
a resolved value instead of `None`) AND shows `alternation_rate(...) < ALT_MIN` (existing, frozen = 0.5).

A structural property worth stating explicitly, verified by direct arithmetic (not merely observed): with
`n_touch=2`, a side that has not yet reached `n_touch` has, by definition, contributed **zero** tagged
touches (the founding touch itself is never tagged — see `range_semantic_v4_5.py`'s module docstring).
So whenever this branch's alternation value resolves at all, it necessarily resolves to exactly `0.0` —
every real H-ONE-SIDED firing in the canonical run shows `alt=0.0000`. The `< ALT_MIN` comparison is kept
(rather than hardcoding "fires whenever resolved") purely for idiom consistency with T3's own existing
alternation check, not because it discriminates a range of values in practice for this branch.

**Correction, disclosed rather than left standing**: an earlier draft of this contract treated the above
as proof the mechanism was safe ("provably safe"). It is not the same claim. The arithmetic proves the
trigger's VALUE is deterministic whenever it resolves; it says nothing about whether resolution itself is
rare or reserved for genuinely-stuck candidates. The negative control below shows it is not rare — 3+ tags
accumulating on one side before the other side's 2nd touch arrives is a common, normal pattern in real,
eventually-confirming range formation, not an unusual one.

### 4.3 H-PERSISTENCE: eligibility and trigger

**Eligibility**: identical age/confirmed gates as 4.2, but the OPPOSITE touch-count condition — both
`up` and `dn` have reached `n_touch`.

**Trigger**: the candidate has remained in this eligible-but-unconfirmed state for `WEAKENING_MAX_BARS`
(existing, frozen = 22) **consecutive** bars. Tracked via new producer-level instance state — a bar
counter, not a threshold — because this cannot be derived retroactively from existing per-touch
bookkeeping (there is no recorded bar index for "when did the lagging side first reach `n_touch`"; the
founding-touch blind spot applies here too). The counter resets to zero the instant a genuinely different
structure becomes active (`structure_id` mismatch), and is folded into `snapshot_state`/`restore_state`
so it survives a snapshot/restart identically to a continuous run (`test_live8c`).

```python
def _candidate_stagnation_reason(self, st: StructureV44, i: int) -> str | None:
    if st.reached_confirmed:
        return None
    age = i - st.start_ts
    if age < self._cfg.d_macro:
        return None
    both_satisfied = (len(st.up.members) >= self._cfg.n_touch
                       and len(st.dn.members) >= self._cfg.n_touch)

    if not both_satisfied:
        all_tags = st.touches_in_window(i, age + 1)
        alt = alternation_rate(all_tags)
        if alt is None:
            return None
        return CANDIDATE_ONE_SIDED_TERMINATED if alt < self._cfg.ALT_MIN else None

    if st.structure_id != self._t3_eligible_structure_id:
        self._t3_eligible_structure_id = st.structure_id
        self._t3_eligible_streak = 0
    self._t3_eligible_streak += 1
    return CANDIDATE_PERSISTENCE_TERMINATED if self._t3_eligible_streak >= self._cfg.WEAKENING_MAX_BARS else None
```

**Zero new numeric parameters.** `ConfigV45` adds no field beyond `ConfigV44` (mechanically verified,
`test_live12b_zero_new_config_fields_vs_v4_4`); every quantity used by either branch (`d_macro`,
`n_touch`, `ALT_MIN`, `WEAKENING_MAX_BARS`) and every function (`alternation_rate`, `touches_in_window`)
already existed in frozen v4.4, already governing a different but structurally analogous question (T3's
own supporting-evidence check for H-ONE-SIDED; POST-confirmation weakening persistence for
H-PERSISTENCE). **This did not turn out to be sufficient for safety** — see immediately below.

**Negative-control validation performed, and FAILED (mandate's own T-STALE lesson, reproduced at larger
scale)**: every one of the 187 real macro structures that DID reach `CONFIRMED` across the full available
history (2011–2026) was checked for whether H-ONE-SIDED or H-PERSISTENCE would have fired at any bar
strictly before that genuine confirmation.

| Mechanism | Structures at risk | Rate | Timing among at-risk structures |
|---|---|---|---|
| H-ONE-SIDED | 69 / 187 | **36.9%** | first-fire offset: min 13, median 24, max 7,337 bars past the age gate |
| H-PERSISTENCE | 23 / 187 | **12.3%** | peak pre-confirmation eligible streak: min 23, median well above threshold, max 12,226 bars (127+ days) |

Both rates are far above what closed T-STALE (which doubled a much smaller sample's false-positive count,
8→16). H-ONE-SIDED's own median first-fire offset (24 bars) is barely past the `d_macro=29` age floor —
in the common case it fires essentially as soon as it is ELIGIBLE to, with no margin for a genuinely
converging candidate that simply has not yet had its lagging side revisited. H-PERSISTENCE's own extreme
(12,226 bars) shows a genuine, real confirmation can legitimately take over 500× `WEAKENING_MAX_BARS` to
resolve — reusing that threshold PRE-confirmation was not the same question as using it POST-confirmation,
despite being built from the identical existing value. `tests/test_v4_5_liveness.py::test_live1h`/`1i`
illustrate the same failure class mechanically, on small hand-built fixtures, for readers who want the
mechanism without re-running the full validation. **Neither mechanism is safe to deploy as designed.**

### 4.4 Effect (both mechanisms)

`_kill_macro(st, i, reason, events)` — the SAME termination function v4.4 already uses for degeneracy
kills, unmodified, with `reason` being whichever of the two new codes fired. The candidate is added to
`_macro_history`, its zone/end-reason recorded for episode-identity purposes (so a subsequent overlapping
candidate is correctly recognized as a `CONTINUATION`, not spuriously flagged `REPLACEMENT`), and
`self._active_macro` is cleared. No new termination bookkeeping exists beyond the one streak counter
(4.3).

### 4.5 What happens next (no explicit supersession mechanism — mandate section 10)

Section 10 asked this mandate to investigate whether an independently-forming new candidate should be able
to supersede a stale one. **Not implemented as a separate mechanism**, for either release path. Once the
slot is released (4.4), the EXISTING, unmodified `forming_macro = self._active_macro is None` gate admits
the next swing pair through the IDENTICAL path any fresh candidate uses — `_episode_identity_for_new_macro`
classifies it as `CONTINUATION`/`MERGE`/`REPLACEMENT` using its own existing, unmodified rules. There is no
`SUPERSEDED_BY`/`STALE_REPLACEMENT` event kind, no special-cased admission rule for a post-release
candidate. This satisfies section 10's own requirement ("supersession must be deterministic, causal,
strategy-outcome-independent") by construction, since it is not a bespoke mechanism at all —
`test_live4_no_explicit_supersession_release_then_natural_reformation_only` proves the post-release
candidate is indistinguishable, mechanically, from any other freshly-formed candidate.

## 5. Confirmation semantics (mandate section 11) — unchanged

`_evaluate_macro_formation` is inherited from `RangeSemanticProducerV44` without override. A candidate that
survives past both release checks' eligibility windows without triggering either is judged for
confirmation by the EXACT SAME ER/traversal/RND gates as v4.4. A released candidate is **never** promoted —
release is a rejection path for both mechanisms
(`test_live6b_no_automatic_promotion_release_is_not_confirmation`).

## 6. Boundary semantics (mandate section 12) — unchanged

`boundary_upper`/`boundary_lower` remain `Cluster.center` (v4.3, the running median of accepted touches).
No rolling high/low, no Donchian/Bollinger/ATR-channel substitute — mechanically confirmed absent from
this module's source (`test_live7_boundary_construction_untouched`).

## 7. Timeframe authority (mandate section 13) — unchanged

`RangeSemanticEngineV45` requires an explicit `timeframe` argument with no default (mirrors
`RangeSemanticEngineV44`'s own signature exactly) — M15 remains the canonical authority by the caller's own
choice, not a hardcoded assumption inside this module. No H1/H4 RANGE detector exists anywhere in this
contract; M5 is never referenced (`test_live11_no_m5_timeframe_reference_anywhere_in_v4_5`).

## 8. Design note: why H-ONE-SIDED uses "entire lifetime so far" rather than a bounded recent window

The trigger's touch-history query (`st.touches_in_window(i, age + 1)`) intentionally spans the candidate's
whole life, not a fixed trailing window like `W` (29 bars). This was a deliberate choice, not an oversight:
the real lineage shows touches on the healthy side arriving at irregular, often multi-day intervals — a
fixed 29-bar (≈7-hour) window would frequently see zero touches even on an actively-growing side, making
`alternation_rate` return `None` (insufficient evidence) far too often to detect the imbalance promptly.
Using the full lifetime, bounded only by `StructureV44`'s own pre-existing `_touch_tags` memory cap
(`maxlen=64`, an implementation memory bound, not a new semantic parameter), reflects the TRUE cumulative
one-sidedness directly. This is disclosed, not hidden, as a considered design choice with a real (small)
trade-off — see the honest limitation in section 9. H-PERSISTENCE has no analogous window choice to make:
its streak counter is a plain consecutive-bar count, not a touch-history query.

## 9. Limitations (mandate section 26/27 — not hidden)

**Primary, disqualifying limitation** (see the box at the top of this document and section 4.3): both
mechanisms fire far too often on real, genuinely-converging, eventually-confirming candidates —
36.9%/12.3% of all real 2011–2026 confirmations respectively. This is not an edge case; it is the central
finding of this contract, and it is why neither mechanism is deployed.

**Secondary, narrower limitation** (still true, still disclosed, but no longer the operative reason this
contract is blocked): a candidate that accumulates its founding pair (1 touch per side, from creation) and
then receives **zero** further accepted touches on **either** side for the rest of its life never reaches
`n_touch` on either side, and so never reaches EITHER mechanism's firing domain — a genuine, if now
secondary, blind spot. It is NOT the mechanism observed in either real lineage this mandate reproduces
(macro_id 893's healthy side reached 4 touches; macro_id 770's two sides reached 89 and 67).

**Why this could not be resolved by tuning within this mandate's own constraints**: mandate section 8
forbids grid-searching an arbitrary bar-count horizon and requires deriving any needed number mechanically
from existing frozen semantic windows, or stopping. Both mechanisms already do the latter (`ALT_MIN`,
`WEAKENING_MAX_BARS` are each pre-existing, not invented for this purpose) — and both still fail. The
negative-control distributions themselves suggest no simple fixed threshold, existing or new, cleanly
separates "genuinely stuck" from "genuinely slow": H-PERSISTENCE's own false-positive set spans peak
streaks from 23 (barely over the line) to 12,226 (off by two orders of magnitude), meaning even a much
larger reused or invented threshold would still misclassify some real confirmations, while a smaller one
would resolve real stagnation more slowly. This is consistent with mandate section 8's own apparent
expectation that a safe answer might not exist within the "no new parameters, no arbitrary tuning"
envelope — and per section 8's own instruction, the correct response to that outcome is to stop and report
it, not to keep searching combinations until one happens to look better on the cases already in hand.

## 10. Versioning (mandate section 25)

| Identity | Value |
|---|---|
| `RANGE_HIERARCHICAL_V4_5_CONTRACT_VERSION` | `range-hierarchical-v4.5` |
| `RANGE_HIERARCHICAL_V4_5_NORMATIVE_CONFIG_ID` | computed via `ConfigV45().config_id()`, distinct from both v4.4's and v4.4.1's (mechanically confirmed, `test_live12_identity_distinct_from_v4_4_and_v4_4_1`) |
| `RANGE_HIERARCHICAL_V4_5_IMPLEMENTATION_FINGERPRINT` | `v4-5-implementation-freeze-2026-08-22` (descriptive human label, same convention as v4.3/v4.4/v4.4.1 — not a raw digest) |
| Real sha256, both files concatenated (`range_semantic_v4_5.py` + `range_engine_v4_5.py`), computed after freeze | `11db8aebf2600368d7f8d3102cd53716bc420ad3e1dfb2ae7fb3ef05e4dabd9a` |
| New reason codes | `CANDIDATE_ONE_SIDED_TERMINATED`, `CANDIDATE_PERSISTENCE_TERMINATED` (41st/42nd, additive — the 40 from v4.4 unrenumbered) |

`ve_n1_replay`'s own package version (`0.4.1`) is unchanged — matching the precedent that v4.3/v4.4/v4.4.1
additions never bumped it either (RANGE-layer additions carry their own internal contract/config/
fingerprint identity, independent of the N1-wheel-vendoring identity the package version tracks).

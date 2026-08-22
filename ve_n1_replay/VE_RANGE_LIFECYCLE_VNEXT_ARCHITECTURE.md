# VE_RANGE_LIFECYCLE_VNEXT_ARCHITECTURE

**Mandate**: `VE-RANGE-LIFECYCLE-VNEXT-MULTI-CANDIDATE-RESEARCH-001`
**Contract version**: `range-hierarchical-vnext-multicandidate-v1`
**Implementation**: `ve_n1_replay/range_semantic_vnext.py`, `ve_n1_replay/range_engine_vnext.py`
**Lineage**: additive over frozen `range-hierarchical-v4.4` (`3bb61cf`), byte-untouched. Not a subclass of
`RangeSemanticProducerV44` — see §1 for why — but reuses every v4.3/v4.4 primitive it can (Cluster,
Registry, Excursion, `assign_level`, `degeneracy_check`, `efficiency_ratio`/`traversal_count`/
`relative_net_displacement`/`alternation_rate`, `_iou`, `StructureV44`) unmodified, by import.

## 0. Status

Research prototype. Not ratified. Not production-ready. Not integrated into New Brain. See the companion
research report for the historical validation results this architecture is judged against, and the final
verdict (`RANGE_LIFECYCLE_VNEXT_CANDIDATE_READY_FOR_INDEPENDENT_VALIDATION` or
`RANGE_LIFECYCLE_VNEXT_NOT_SUPPORTED`, per mandate §20/§21).

## 1. Why a fresh producer, not a v4.4 subclass

`RangeSemanticProducerV44` itself is NOT a subclass of `RangeSemanticProducerV43` — its own module
docstring states it needed "a materially different `_step_macro`/type system for MACRO" and so is a fresh
producer that reuses v4.3's pure functions/classes by import. The same reasoning applies here, more
strongly: vNext replaces the single field `self._active_macro: StructureV44 | None` with a *registry* —
every method that reads or writes that field (`_offer_swing_everywhere`, `_step_macro`,
`_episode_identity_for_new_macro`, `observe`, snapshot/restore) needs to iterate a collection instead of
touching one value. Subclassing and overriding all of them would not be inheritance in any meaningful
sense — it would be re-declaring the entire orchestration layer under a parent class it shares almost
nothing executable with. `RangeSemanticProducerVNext` is therefore a fresh class, following v4.4's own
precedent for when to do this, while importing (never redefining) every pure primitive.

## 2. The central finding this architecture is built on

`range_semantic_v4_4.py`'s own module docstring (lines 33-37) already states: *"MERGE/EPISODE_MERGED is
implemented (not dead code, in case a future architectural change ever allows concurrent candidates) but
is structurally unreachable via the public `observe()` API today."* — proven unreachable by v4.4's own
`tests/test_v4_4_transitions.py::test_episode_merge_is_structurally_unreachable`.

`_episode_identity_for_new_macro` already contains a real, IoU-based (`_iou`, the same convention the
ratified blind-scorer uses — not invented here) zone-overlap check against `self._active_macro`, gated
"MERGE" — it is unreachable *only* because `forming_macro = self._active_macro is None` never lets a
second candidate begin forming while one is active. **This mandate's core architectural change is to
remove that single-slot gate and make v4.4's own existing MERGE branch reachable, generalized from "the
one active macro" to "every currently active macro in a bounded registry."** Nothing about the geometric
question ("do two candidates represent the same structure?") is invented here — it is the same `_iou`
comparison against the same `IOU_CONTINUE` threshold v4.4 already uses for the sequential
(terminated-then-continued) case, now also applied to the concurrent (both-still-active) case it was
always meant to cover.

## 3. Candidate registry

```
self._active_macros: dict[int, StructureV44]        # structure_id -> candidate, MACRO depth
self._macro_excursions: dict[int, Excursion]         # keyed by macro structure_id
self._macro_reversal_watches: dict[int, dict]        # keyed by macro structure_id
self._active_internals: dict[int, Structure]         # keyed by PARENT macro structure_id (at most 1/macro)
self._internal_excursions: dict[int, Excursion]      # keyed by parent macro structure_id
self._internal_reversal_watches: dict[int, dict]     # keyed by parent macro structure_id
```

Every candidate has immutable, causal identity: `structure_id` (monotonic, from the same `Registry` v4.3
already uses — dead ids are never reused, C7), `start_ts`, `boundaries` (`up`/`dn` `Cluster`, unchanged),
`touch history` (`_touch_tags`, unchanged), `formation evidence` (`_trailing_closes`, unchanged),
`confirmation eligibility` (`reached_confirmed`, unchanged), `structural age` (`i - start_ts`, tracked but
— per mandate §2 — never used to decide termination), `state transitions` (the same reason-code event
stream v4.4 already emits, per-structure), and `supersession/merge relationships` (`continued_from_id`,
already a v4.4 field, now actually populated on the concurrent path too). No P&L field exists anywhere in
`StructureV44` or this module. No future bar is ever read (see §11, causality).

## 4. Swing offering: per-swing absorption first, new-candidate formation second

Generalizes v4.4's own `_offer_swing_everywhere`. For each fractal-confirmed swing `(bar, price, is_high)`:

1. **Offer to every active macro's cluster, oldest first (ascending `structure_id`), stop at first
   acceptance.** This is `Cluster.offer(price, tol_cluster * atr_ref)` — v4.3's own, unmodified acceptance
   rule — applied across a set instead of a singleton. A swing that lands within an existing candidate's
   own tolerance simply extends that candidate; no new candidate is ever proposed for it. This is the
   *first* and cheapest line of defense against candidate explosion: most swings near an existing
   structure never reach step 2 at all.
2. Promotion/regime external-swing counting: unchanged, global (§8).
3. **INTERNAL suppression / candidate-pair accumulation**: unchanged mechanics (`_pending_up`/`_pending_dn`
   each hold only the single most recent swing per side — the same bounded, non-list, non-accumulating
   design v4.4 already uses and documents as a found-and-fixed defect class if done otherwise). The
   INTERNAL-suppression check (a swing that only re-tests an existing macro's own frozen/near boundary is
   not new information) now runs against *whichever* macro accepted-or-was-nearest, not a singleton.
4. Once a candidate pair `(cand_lo, cand_hi, cand_start, cand_end)` is ready and was **not** absorbed by
   step 1: generalized episode identity (§5) decides MERGE / CONTINUATION / REPLACEMENT.

## 5. Generalized episode identity (the reachable MERGE)

`_episode_identity_for_new_macro_multi(candidate_zone, i)`:

1. **MERGE**: compute `_iou(candidate_zone, live_zone)` against **every** active macro's own zone
   (`(boundary_lower, boundary_upper)`), not just one. If the maximum exceeds `IOU_CONTINUE` (existing,
   frozen = 0.5), that candidate is the merge target — ties broken by lowest `structure_id` (oldest,
   deterministic). This is the *second* line of defense: a swing pair whose individual prices were not
   close enough to an existing cluster's own median (step 4.1 above) can still describe a zone that
   substantially overlaps one, and is treated as the same underlying structure rather than a rival.
2. **CONTINUATION**: unchanged from v4.4 — IoU against the single most-recently-terminated (non-breakout)
   macro zone, within `GAP_MAX` bars. This case is inherently sequential (the old one is already gone by
   the time it fires), so generalizing it to a registry adds nothing; it is reused verbatim.
3. **REPLACEMENT**: neither of the above — a genuinely new, spatially distinct candidate. Only inserted if
   the registry has capacity (§7).

## 6. Merge mechanics — the one real behavioral fix over v4.4's dead code

v4.4's own MERGE branch, if it were reachable, would silently overwrite `self._active_macro = st_macro`
without ever calling `_kill_macro`/`_close_macro_via_breakout` on the structure being replaced — it would
vanish with no `end_ts`, no `end_reason`, not even added to `_macro_history`. That gap was never caught
because the branch was provably unreachable. It is reachable here, so it is fixed, disclosed rather than
silently carried over: when a new candidate zone's IoU against an active macro clears `IOU_CONTINUE`, that
active macro is **properly retired** — `end_ts=i`, `end_reason=CANDIDATE_SUPERSEDED_BY_MERGE` (new reason
code, §10), appended to `_macro_history`, removed from `self._active_macros` — *before* the new,
`continued_from_id`-linked structure is inserted. Nothing about the old structure's own accumulated
evidence is copied into the new one — the new structure starts its own touch/trailing-close accumulation
from its own founding pair, exactly as any newly-formed candidate does; only the *identity chain*
(`continued_from_id`) carries forward, matching v4.4's own existing CONTINUATION semantics exactly. This
was a deliberate design choice over the alternative (splicing the old structure's raw evidence into the
new one): splicing would let stale, pre-supersession touches silently influence a structure that is
supposed to represent newer, structurally distinct price action — the same class of problem RANGE_V2's own
`w_atr`/`s_max` anchor-monotonicity defect illustrated for this codebase's history (see `ve-brain-tower-
artifacts` memory). A merge is a *semantic handoff*, not a data union.

## 6a. Price-abandonment supersession — added after empirical measurement, not part of the original design

**Added during validation, disclosed rather than presented as originally planned.** An early exploratory
measurement (research report §12) found that overlap-merge alone (§5–6) does not resolve every source of
registry growth: a never-confirmed candidate whose zone price has moved completely away from — with no
*new* candidate ever overlapping it — has no path back to a single slot; nothing ever explicitly closes
it. Over a multi-year canonical run this left a moderate but real steady-state population (median 12,
max 22 concurrent candidates in a 3.4-year sample) of old, spatially-abandoned candidates accumulating
across every price level the market had ever visited. This is exactly mandate §5's own research question
— "has current structure causally superseded the old candidate?" — deliberately deferred at first
(architecture design favors the simplest mechanism that could work, validated before adding more), and
revisited once the measurement showed it was needed.

**The rule** (`_retire_price_abandoned_candidates`, run once per bar, after all per-candidate stepping):
a never-confirmed candidate is retired **only if both** hold —
1. the current bar's close is further than `tol_cluster * atr_ref` from *both* its own boundaries — the
   SAME distance `Cluster.offer` already uses to decide whether a swing extends a cluster, reused for the
   opposite question (has price left the band that would still extend this candidate), not a new
   threshold; and
2. a **different** active candidate exists whose own distance to the current price is smaller.

Condition 2 is the load-bearing protection: it means this rule **never fires on an isolated candidate**,
however far price has moved — there is nothing structurally "closer" to supersede it with, so it is left
exactly as v4.4 would leave a single active macro, waiting. This directly protects the exact case mandate
§6 requires ("a candidate that eventually confirms under legitimate causal structure must not be
prematurely destroyed merely because it takes a long time") for the common case of a genuinely isolated
slow range. It is NOT age-based — a candidate satisfying condition 1 the instant it forms (if price
immediately moves away) is eligible from bar one; a candidate that has existed for months is untouched if
still nearest to price or if it is the only candidate at all. New reason code
`CANDIDATE_ABANDONED_PRICE_MOVED_ON` (§10).

**Measured effect** (research report §12): registry size collapsed from median 12 / max 22 to median 1 /
max 3 over the same 3.4-year sample — directly satisfying mandate §4's "candidate explosion must be
prevented." **This is also the mechanism carrying the largest false-positive RISK of anything in this
architecture** — condition 2 alone does not prove the abandoned candidate would never have come back and
confirmed; it only proves something else is currently closer. The full-history negative control (research
report §9) is where this claim is actually tested against all real v4.4 confirmations, not assumed safe
because the registry-size number looks good — see that section before trusting this mechanism at all.

## 7. Registry bound — resource safety net, not a behavior rule

A hard cap on `len(self._active_macros)` exists purely as a DoS/resource guard, exactly the same
justification `StructureV44._touch_tags`'s `maxlen=64` already carries ("an implementation memory bound,
not a new semantic parameter"). It is **not** used to decide which candidate survives and is never
consulted by MERGE/CONTINUATION/REPLACEMENT logic — those are purely geometric/temporal. If REPLACEMENT
would exceed the cap, the new candidate is simply refused for that bar (`REGISTRY_CAPACITY_REFUSED`, new
reason code) — its founding swings are not lost, exactly like any other refused candidate today; a future
bar may see the same swings (or newer ones) succeed once the registry has room. The cap's numeric value is
set from the research report's own empirical measurement of the maximum concurrent-candidate count over
the full canonical history, with a generous safety margin — derived from evidence, not picked in advance
(mandate §4: "no parameter mining to control candidate count" — this cap does not control the count, it
only bounds worst-case memory, and its value is *reported*, not *tuned to a target*).

## 8. INTERNAL sub-structure — per-macro, not global

Each active macro may independently host at most one INTERNAL candidate (`self._active_internals[macro_id]`),
using v4.4's existing INTERNAL step logic verbatim, looped per macro instead of applied to a singleton.
Parent selection when a new INTERNAL candidate pair is ready: try each active macro as the candidate
parent, in ascending `structure_id` order, via the unmodified `assign_level` containment check (R1/R2);
the first one for which `assign_level` returns `Depth.INTERNAL` (i.e., actually contains the candidate
geometrically and temporally) is the parent. If none contains it, the candidate is refused exactly as
`assign_level` already refuses non-contained candidates today (`PARTIAL_OVERLAP_NO_CONTAINMENT`/
`LEVEL_ASSIGNMENT_UNRESOLVED`) — no new refusal logic, just applied against a set of candidate parents
instead of one. INTERNAL candidates do not merge across macros; each stays scoped to its own parent.

## 9. Promotion / trend regime — unchanged, explicitly still single-window

v4.3's own module docstring already discloses this as "a known limitation, adequate for a PROTOTYPE" —
one global promotion window (`_promo_direction`/`_promo_original_id`/etc., unchanged fields). With
multiple concurrent macro candidates, a breakout from any one of them can open the window; a second,
concurrent breakout from a *different* active macro while the first window is still open is not tracked
separately — the existing single-window guard (`_promo_fired`) applies globally, not per-macro. This is a
disclosed, inherited scope limitation, not a silent gap introduced here; the research report measures how
often concurrent breakouts actually co-occur in the historical data to characterize its real impact.

## 10. New reason codes (additive, REASONS_V44's 40 unrenumbered)

- `CANDIDATE_SUPERSEDED_BY_MERGE` — an active macro properly retired because a new, overlapping candidate
  (IoU ≥ `IOU_CONTINUE`) took over its identity chain (§6).
- `REGISTRY_CAPACITY_REFUSED` — a genuinely new (REPLACEMENT) candidate was refused because the registry
  was at its resource cap (§7); its swings are not lost.
- `CANDIDATE_ABANDONED_PRICE_MOVED_ON` — a never-confirmed candidate retired because price has moved
  outside its own acceptance tolerance AND a different, closer candidate exists (§6a).

`EPISODE_MERGED`/`EPISODE_CONTINUATION`/`EPISODE_REPLACEMENT` are REUSED from v4.4 unchanged — the first
becomes reachable for the first time; the other two behave identically to today.

## 11. Confirmation arbitration — canonical selection for the exposed MarketState view

Internally, any number of active macros may independently reach `reached_confirmed=True` and remain in
the registry (a confirmed range can still weaken/break out later, exactly as in v4.4). The single
`RangeSemanticResultVNext.macro_*` fields exposed as "the" canonical RANGE (what a MarketState/
StrategyRouter consumer would read) are chosen by a deterministic, predeclared, purely structural rule
using only already-available, zero-lookahead information: **among all currently `CONFIRMED` (and not yet
terminated) macros, prefer the one whose zone contains the current bar's close; if none contains it,
prefer the one with the smallest boundary distance to the close; ties broken by lowest `structure_id`.**
No profitability, no strategy outcome, no hindsight — only the current bar's own close price (already
read for every other purpose this bar) and each candidate's own existing boundary fields. The full
registry (every active candidate, confirmed or not) is exposed separately for diagnostics — a consumer
that only reads the canonical fields sees behavior consistent with "one RANGE at a time," matching
mandate §7's own framing, while the underlying engine tracks several.

## 12. Causality (mandate §14)

Every decision above reads only: the current bar's own OHLC, `atr_ref` as of the current bar, and
structure state built exclusively from bars already observed (`i <= current`). No structure's zone,
touch history, or confirmation status is ever recomputed retroactively using a later bar — the same
zero-lookahead discipline v4.3/v4.4 already enforce (fractal swing confirmation uses a `K_struct`-wide
*trailing* window that only reports a swing `K_struct` bars after it occurred, never earlier).

## 13. Determinism / restart (mandate §15)

`snapshot_state`/`restore_state` serialize the full registry (every active macro/internal, its excursion
and reversal-watch state, keyed exactly as in memory) plus the same scalar/deque state v4.4 already
snapshots. `contract_version`+`config_id`+`implementation_fingerprint` gate restoration exactly as every
prior RANGE version does — a v4.4 (or v4.5) snapshot is refused, fail-closed. Dict iteration order in
Python 3.7+ is insertion order, but this implementation never relies on dict iteration order for a
decision — every place that needs a deterministic order (offering, merge-tie-breaking, internal-parent
selection) explicitly sorts by `structure_id` first.

## 14. What is explicitly NOT changed

- `RangeSemanticEngineV44`, `ConfigV44`, `StructureV44`'s own class body, v4.4's fingerprints and
  artifacts — byte-untouched (verified by `git diff`, recorded in the research report).
- M15 remains the sole canonical RANGE authority; no H1/H4 detector; `RangeSemanticEngineVNext` requires
  an explicit `timeframe` argument with no default, mirroring v4.4/v4.5's own signature.
- No age/duration/timeout-based termination rule of any kind exists anywhere in this module (mandate §2).
- No Alpha, P&L, WR, RR, or trade-outcome data is read, computed, or referenced anywhere in this module or
  its validation scripts (mandate §13).
- Not integrated into New Brain/MarketState/StrategyRouter (mandate §8) — this module is standalone,
  exactly like v4.4/v4.5 before it.

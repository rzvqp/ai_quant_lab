# VE — RANGE V4.4.1 T-STALE MECHANISM FREEZE

**Mandate**: `VE-RANGE-V4_4_1-STALE-CALIBRATION-001`, §1. **Date**: 2026-08-21. **Division**: Validation
Engine (VE). Freezes the **mechanism** approved in `9aba9b7` and independently audited in `eeb082e`
(`V4_4_1_STALE_DESIGN_AUDIT_PASS_WITH_NONBLOCKING_NOTES`, 17/17 areas PASS). **Numeric values are explicitly
NOT frozen here** — all four parameters remain `UNRESOLVED_PARAMETER` pending the calibration protocol
(mandate §7) and calibration execution (mandate §8–§18), which follow as separate, later commits.

Every row below cites its exact source location in `9aba9b7` (`VE_RANGE_V4_4_1_STALE_CANDIDATE_DESIGN.md`)
or the frozen V4.4 code (`3bb61cf`), re-verified this mandate against both documents directly — nothing here
is re-derived from memory.

---

## 1 — T-STALE semantic purpose

A new pre-confirmation transition, `T-STALE`: `CANDIDATE`/`FORMING → TERMINATED`, reason
`STALE_CANDIDATE_ABANDONED`. Purpose: release a never-confirmed MACRO candidate whose own boundary no longer
represents current market structure, so that a fresh, potentially correctly-anchored candidate can be
evaluated by the unchanged discrimination gate. It changes **who remains eligible to become confirmed**, never
**how confirmation is made easier**. Source: design §8 ("Kill semantics"), design §2 ("Root-cause
mechanism").

## 2 — Eligible state(s)

Applies **only** to structures with `reached_confirmed = False` **and** an already-established boundary
(`boundary_upper`/`boundary_lower` both set — i.e. past `ESTABLISHING_FEW_SWINGS`). A candidate that has not
yet gathered its minimum touch count is **structurally** exempt (the check cannot even evaluate without a
boundary to be stale relative to), not merely policy-exempt. Never applies to `reached_confirmed = True`
structures (confirmed / `WEAKENING`) — those remain exclusively governed by T4–T9, untouched. Source: design
§7 item 3, design §8 ("Trigger").

## 3 — Staleness evidence (semantic definition)

Evidenced by an accumulation, within a bounded trailing window, of **rejected** swing touches (detected by
the unchanged `_detect_confirmed_swings`, refused by the unchanged `offer_swing`/`Cluster.offer` tolerance
check) that themselves show **genuine two-sided (alternating) character**. Chosen after working through five
candidate concepts (`NO_RECENT_ACCEPTED_TOUCH` / `PRICE_STRUCTURE_DECOUPLING` / `CLUSTER_OBSOLESCENCE` /
`STRUCTURAL_REANCHOR_REQUIRED` / combination) against the diagnostic's own evidence (design §5). **Explicitly
NOT**: touch-scarcity/silence-based, age-based, or price-distance-alone-based (design §5, §6). Source: design
§5 ("Chosen definition"), design §6 ("Distinguishing staleness from slow legitimate formation").

## 4 — Rejected-swing accumulation logic

Recorded via **one new bounded deque** on `StructureV44` — `(bar_index, side)` records of *rejected*
`offer_swing` outcomes for the currently-forming candidate — architecturally identical in kind to, but kept
**structurally separate from**, the existing accepted-touch `_touch_tags` deque (conflating the two would
corrupt the existing `SUPPORTING_ONLY` alternation signal). Rejection count and alternation count are
**computed on demand from this bounded window**, not maintained as running/incremental counters — matching
the existing project-wide convention (`efficiency_ratio`/`traversal_count`/`alternation_rate` are all pure
functions over a bounded window). No other new state: candidate age reuses `start_ts` (`i - st.start_ts`,
already existing); boundary reuses `boundary_upper`/`boundary_lower` (already existing, used only as an
eligibility gate, §2 above). Zone-overlap percentage, ATR-normalized distance, a separate boundary-age field,
and any incremental counter are **explicitly rejected as unnecessary**. Source: design §7 ("Required state
variables").

## 5 — Alternation requirement

Staleness requires **both** a minimum count of rejected touches **and** a minimum count of alternating (H/L
flip) transitions within that rejected evidence, using the identical flip-counting logic already proven in
`alternation_rate`/`traversal_count` — no new counting algorithm. This is not a secondary refinement; it is
the mechanism's central, load-bearing property (§6 below). Source: design §5, design §10.

## 6 — Anti-churn principle

The alternation requirement **is** the anti-churn safeguard, not a separate cooldown mechanism. A clean,
one-directional trend produces predominantly **one-sided** rejected swings by definition — they never satisfy
the alternation requirement, so a stale candidate sitting in a trend's path is not repeatedly killed and
reformed; it simply persists (a known, non-blocking limitation — no worse than today's V4.4 behavior in that
specific case, since no genuine RANGE TP is being missed during a genuine trend). Directly checked against
the diagnostic's own traced FB14-003 rejection sequence
(`LHLHLHLLHLHLHHLHLHHLHLHHLHLLHLHLLHLHLH`), which is genuinely alternating throughout the CEO's labeled
range. No numeric cooldown parameter is introduced to solve churn; if calibration later finds this
insufficient alone, any additional parameter becomes its own new `UNRESOLVED_PARAMETER`, not assumed
necessary here. Independently re-verified by Red Team (`eeb082e` §3 area 5, `ANTI_CHURN_SUPPORTED`; §5,
"No churn risk found"). Source: design §10.

## 7 — Next-causal-bar replacement

**Decision (B), resolved explicitly, not left to implementation discretion**: a fresh candidate may only
begin forming from the next causal observation onward. The swing that contributed to an abandonment decision
is never replayed to seed the replacement in the same bar. Verified against `observe()`'s actual per-bar
order (`_offer_swing_everywhere` runs before `_step_macro`, confirmed by direct code re-read both in the
design and independently in the RT audit): by the time `T-STALE` could fire at bar `i`, that bar's own swing
has already been offered-and-rejected by the (still-alive, at that point) stale candidate — there is no
pending, unconsumed swing to hand to a hypothetical same-bar successor. Matches the **only** existing pattern
in this codebase for every other slot-freeing path (`_kill_macro`/T-KILL, `_close_macro_via_breakout`/T8,
`_terminate_macro_weakening_persistence`/T9 — none of them re-offer the triggering bar's evidence to an
immediate successor). Independently re-verified by Red Team (`eeb082e` §3 area 7,
`NEXT_BAR_REPLACEMENT_VALID`). Source: design §9.

## 8 — Transition priority

`T-STALE` is checked **immediately after `T-KILL`** (`degeneracy_check`, `range_semantic_v4_4.py:889–892`)
and **before `T2`/`T3`** (`_evaluate_macro_formation`, entered at line 896), inside `_step_macro`'s existing
`zones is None` branch (lines 894–896). It is structurally disjoint from T4–T9 via `reached_confirmed` — no
priority conflict with `WEAKENING` is possible. Source: design §8 ("Priority"), independently re-verified by
Red Team (`eeb082e` §3 area 11).

## 9 — Termination mechanics

Identical mechanics to the existing `_kill_macro` (`range_semantic_v4_4.py:609`): `end_ts`/`end_reason` set,
structure pushed to `_macro_history`, `_registry.kill` called, `_active_macro = None`,
`_macro_excursion = None`. One `RangeEventV43(kind=STALE_CANDIDATE_ABANDONED, ...)` emitted, matching the
existing event shape used by every other termination reason. Reachability of the new code must be **proven**
by a dedicated test (mirroring the `EPISODE_MERGED`-reachability precedent), not merely asserted by wiring it
in. Source: design §8 ("Destination", "Emitted event", "Reachability").

## 10 — Interaction with episode identity

**No new episode-identity rule.** `T-STALE` calls the existing, **unmodified**
`_record_macro_termination_for_episode_identity` (`range_semantic_v4_4.py:645`) exactly as `_kill_macro`
already does. A genuinely stale zone naturally fails IoU-overlap against its replacement (both traced FB14
cases showed exactly `0.000` price-IoU), so `CONTINUATION`-vs-`REPLACEMENT` resolves correctly through the
existing, unmodified priority logic. Independently re-verified by Red Team (`eeb082e` §3 area 12,
`EPISODE_IDENTITY_REUSE_VALID`) — **flagged as argued-not-tested (RT note 3)**: the general property (not
just the two traced cases) must be explicitly verified by a dedicated IoU-continuation test at
implementation, not assumed. Source: design §8 ("Destination"), design §18 (preservation matrix row
"Episode identity").

## 11 — ER / RND / traversal preservation

Completely untouched. `T-STALE` never reads or writes `efficiency_ratio`, `relative_net_displacement`,
`traversal_count`, `MIN_TRAVERSALS`, `W`, or any trailing-closes computation. A candidate formed after a
`T-STALE` abandonment is exactly as new a candidate as any other and must independently satisfy the complete,
**unmodified** `_evaluate_macro_formation` gate before ever confirming — the correction changes who is
evaluated, never how evaluation works. Independently re-verified by Red Team (`eeb082e` §3 areas 8/9/10,
`DIRECTIONAL_PROTECTION_PRESERVED`; §4, "no code path by which T-STALE causes a directional structure to
confirm... structural, not empirical-hopeful"). Source: design §11, design §12.

## 12 — Confirmed RANGE lifecycle preservation

Completely untouched. `WEAKENING` (T4–T9), the excursion/breakout machinery, and all confirmed-structure
semantics are structurally unreachable from `T-STALE`'s trigger condition (`reached_confirmed = False`
required). Source: design §8 ("Priority"), design §18.

## 13 — Snapshot / versioning plan

- New `contract_version = "range-hierarchical-v4.4.1"`, distinct from `"range-hierarchical-v4.4"`.
- `StructureV44`'s successor gains one new `v441_*`-prefixed snapshot key pair (the rejected-touch deque),
  following the exact existing `v44_*`-prefix convention.
- `ConfigV441` (name illustrative) reproduces the identical sha256-over-sorted-fields `config_id()` formula
  already used by `ConfigV43`/`ConfigV44`, now covering the four new fields once resolved.
- `REASONS_V441 = REASONS_V44 + (STALE_CANDIDATE_ABANDONED,)` — 41 total, additive, unrenumbered.
- Cross-version restore remains fail-closed via the **same, already-existing** mechanism (V4.4's
  `restore_state` already refuses on `contract_version`/`config_id` mismatch) — given a new value to check
  against, not a new code path.
- Implementation fingerprint: **not computed here** (no implementation exists yet); computed only after the
  future implementation mandate finalizes code, matching the established `PENDING_FREEZE`-until-actually-
  frozen discipline.

Source: design §16.

## 14 — Reason-code semantics

One new code, `STALE_CANDIDATE_ABANDONED` (name as proposed in the CEO mandate, adopted as-is — no
alternative name was found necessary). Additive to the existing 40; total 41. No renumbering of the existing
29 (V4.3) + 11 (V4.4) codes. Must be mechanically proven reachable, not merely asserted, at implementation.
Source: design §8, design §16.

## 15 — Test semantics

Ten named tests (`STALE-1` through `STALE-10`) plus one mutation test (disabling the alternation requirement
specifically, which must reopen the churn risk, proving the requirement is load-bearing and not vacuous) —
full content in design §17, independently re-verified as complete and appropriately scoped by Red Team
(`eeb082e` §3 area 17, PASS). Reproduced here as a locked commitment, not restated in full (see design doc
§17 for exact content; nothing here supersedes it).

---

## Preservation boundary (restated, locked)

Unchanged by this mechanism, confirmed by both VE (design §4/§18) and Red Team (`eeb082e` §3 areas 3/9/10,
§4): ER, RND, traversal definition, `MIN_TRAVERSALS`, `W` as used by frozen V4.4 directional confirmation,
alternation's `SUPPORTING_ONLY` role in V4.4 confirmation, `WEAKENING`, confirmed-RANGE lifecycle, episode
identity's own priority logic (reused, not amended), INTERNAL semantics, the scorer.

---

## Known risks carried into calibration (not resolved here)

Restated from Red Team's four non-blocking notes (`eeb082e` §8), inherited as-is, not diluted:

1. **Dual-sided calibratability is unproven — the principal residual risk.** The calibration protocol
   (mandate §7, next commit) must attempt to prove one parameter set satisfies both stale-release (§8.A) and
   slow-range-protection (§8.B), and must **honestly disclose**, not force, if it cannot — matching the
   `898f149` shallow-channel precedent.
2. Minimum-age floor not yet derived.
3. Episode-identity IoU-continuation property argued from two cases, not yet proven general — flagged for the
   eventual implementation test plan, not this calibration mandate.
4. The adjacent forced-`EPISODE_REPLACEMENT`-after-`BREAKOUT_ACCEPTED` over-fragmentation observation
   (`b1dcf92` §8) remains explicitly out of scope.

---

```
V4_4_1_T_STALE_MECHANISM_FROZEN = TRUE
V4_4_1_NUMERIC_VALUES_FROZEN = FALSE
```

Every one of the fifteen elements above is locked. No numeric value for any of the four parameters is fixed
by this document. The next commit precommits the calibration protocol; only after that may calibration
results be treated as final.

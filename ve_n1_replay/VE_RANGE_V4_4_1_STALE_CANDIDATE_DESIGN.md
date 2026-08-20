# VE — RANGE V4.4.1 STALE-CANDIDATE DESIGN + CALIBRATION PLAN

**Mandate**: `VE-RANGE-V4_4_1-STALE-CANDIDATE-DESIGN-001`. **Date**: 2026-08-21. **Division**: Validation
Engine (VE). **Scope**: design + calibration-plan only — no implementation, no numeric parameter selection,
no FB14/MB3 calibration use.

Structured against the mandate's own §20 (19-item decision package) + §21 (final verdict).

---

## 1 — Authoritative provenance

| Artifact | Role |
|---|---|
| `b1dcf92` — VE-RANGE-V4_4-TRAVERSAL-DIAG-001 | this mandate's entire factual foundation; re-cited, not re-derived from memory |
| `3bb61cf` — V4.4 implementation | the frozen code this design integrates against (`range_semantic_v4_4.py`, `_step_macro`/`_evaluate_macro_formation`/`_kill_macro` re-read line-by-line this mandate, not recalled) |
| `845a03c` — RT implementation audit | independently confirmed `degeneracy_check`/T3 fidelity, cited in §5 below |
| `dfebe8f` — RT FB14 validation | source of the H1–H5 gains this design must preserve (§2) |

Every code-structure claim below (line numbers, call order, existing field names) was re-read directly from
`range_semantic_v4_4.py` this mandate (`_step_macro` lines 885–896, `_kill_macro` line 609,
`_record_macro_termination_for_episode_identity` line 645, `_episode_identity_for_new_macro` line 483) — not
recalled from the prior diagnostic's prose.

---

## 2 — Exact stale-candidate root-cause restatement

From `b1dcf92`, re-stated precisely because this design must target it exactly: in all three FB14 losses, a
single MACRO candidate forms early, is *correctly* rejected by T3 during a genuinely directional phase of its
own life, and then persists **unconfirmed and un-killed** for the remainder of the window — because
`degeneracy_check` (T-KILL) checks only geometric validity (width, inversion), never whether the candidate's
boundary still reflects current price action. New alternating swings continue to be detected by
`_detect_confirmed_swings` throughout (38 and 66 confirmed in the two traced regions) but are rejected by
`offer_swing`'s tolerance check against the stale, frozen-in-place cluster median. Because
`forming_macro = self._active_macro is None` is the sole precondition for any new MACRO candidate to begin
forming, the stale occupant permanently blocks a fresh, correctly-anchored candidate — which, on identical
bars, is exactly what V4.3's weaker (width+touch+duration-only) confirmation criterion allowed to happen,
producing V4.3's matched TP.

---

## 3 — Current V4.4 state-machine gap

Precisely: there is **no transition out of `CANDIDATE`/`FORMING` other than** (a) `T-KILL` via
`degeneracy_check` (width/inversion only) or (b) `T3` success (`OK_RANGE_MACRO`, requiring duration + the
full discrimination gate). Nothing evaluates whether an unconfirmed candidate remains **relevant** — whether
the market it is meant to describe has moved on. This gap is not new in V4.4 (`degeneracy_check` is
byte-identical to V4.3, confirmed in `b1dcf92` §6) but was inert in V4.3 because V4.3's confirmation
criterion cycles bad candidates through `ZONES_DEGENERATE` quickly enough that the gap rarely mattered. V4.4's
stronger, more patient discrimination gate made a wide, non-degenerate, but perpetually-non-confirming
candidate common — and for that specific case, the state machine has no exit at all.

---

## 4 — Scope confirmation

This design touches only: pre-confirmation candidate lifecycle (`_step_macro`'s `zones is None` branch,
`_evaluate_macro_formation`'s entry), one new bounded field on `StructureV44`, one new reason code, and the
snapshot/config fields directly required by that new field. It does **not** touch: the discrimination gate
itself (ER/RND/traversal/`MIN_TRAVERSALS`/`W`), `WEAKENING`/T4–T9, the confirmed-structure excursion/breakout
machinery, `_offer_swing_everywhere`'s acceptance logic (`Cluster.offer`/`offer_swing` themselves — untouched,
still imported from V4.3), INTERNAL-depth code, or the scorer. No `V4_4_1_SCOPE_EXPANSION_REQUIRED` condition
was encountered — every question this mandate raised was answerable within the stated scope.

---

## 5 — Normative staleness definition

Mandate §5 offers five concepts (A–E) to examine, not to assume. Working through them against the actual
failure mechanism (§2):

- **(A) `NO_RECENT_ACCEPTED_TOUCH`**, read literally ("candidate receives detected swings, but none accepted"),
  is **not** the same as touch-scarcity (silence) — it specifically requires swings to be *detected and
  rejected*, not merely absent. This distinction is the one already flagged as a **binding constraint** in
  `b1dcf92` §10 (self-falsification scenario 7/11): a trigger keyed on absence-of-touches would risk killing a
  genuinely slow, quiet, valid range; a trigger keyed on repeated-rejection requires the market to be actively
  probing outside the candidate's tolerance, which silence cannot produce.
- **(C) `CLUSTER_OBSOLESCENCE`** is the same underlying fact as (A), phrased as a structure-property instead
  of an event-count. Not a distinct mechanism.
- **(B) `PRICE_STRUCTURE_DECOUPLING`** (closing price persistently outside the candidate's zone) is a
  plausible **corroborating** signal but is strictly weaker evidence than (A)/(D): a candidate could have
  price outside its zone for a while during a single strong excursion that later reverts (this is exactly what
  the *confirmed*-structure excursion/`WEAKENING` machinery already handles for confirmed structures — an
  unconfirmed analogue of "one excursion doesn't mean abandon" is equally desirable here, so price-alone is
  not chosen as the primary trigger).
- **(D) `STRUCTURAL_REANCHOR_REQUIRED`** — "sufficient new two-sided swing evidence exists outside the
  candidate geometry" — is the most semantically precise of the five, and directly targets the actual
  observed mechanism: in both traced FB14 regions, the *rejected* swings alternate H/L (§2), i.e. they
  themselves look like a forming range, just one the stale candidate cannot claim.

**Chosen definition (E, a specific combination, not an arbitrary pick)**: staleness is evidenced by an
accumulation, within a bounded trailing window, of **rejected swing touches that themselves show genuine
two-sided (alternating) character** — operationalizing (D), built from the same raw event as (A)/(C)
(rejected touches), deliberately **not** triggered by touch-scarcity or by price-distance alone. This
definition, its rationale, and the anti-churn property it produces (§12) are the central contribution of this
design.

---

## 6 — Distinguishing staleness from slow legitimate formation

By construction, the chosen definition (§5) already excludes the two failure modes mandate §6 warns against:

- **Age alone never triggers it.** No candidate is evaluated for staleness based on `i - start_ts`; age plays
  only a *gating* role (a minimum-age floor before eligibility, §8), never a triggering one.
- **Sparse/quiet candidates are protected.** A candidate that legitimately takes time to accumulate touches,
  or has temporarily low market activity, is not producing *rejected* swings in that state — it is producing
  no swings, or accepted swings — neither of which increments the staleness evidence.
- **A candidate occupying only part of its eventual zone is protected**, as long as later touches remain
  within `Cluster.offer`'s existing tolerance of the *current* median — those touches are *accepted*, not
  rejected, and accepted touches never count as staleness evidence.
- **The requirement for genuine alternation (not just any rejection)** is what protects a candidate sitting in
  the path of a clean, one-directional trend (§12) — a trend's rejected swings are predominantly one-sided,
  so they do not, by themselves, satisfy an alternation requirement.

---

## 7 — Required state variables (mandate §8)

Minimal, deliberately: one new bounded field, reusing two already-existing ones.

1. **New**: a bounded trailing deque of *rejected*-touch records `(bar_index, side)` on `StructureV44` —
   architecturally identical in kind to the existing `_touch_tags` deque (which records *accepted* touches
   for the `SUPPORTING_ONLY` alternation signal), but tracking the complementary (rejected) event, and kept
   **entirely separate** from `_touch_tags` (conflating accepted and rejected evidence would corrupt both the
   existing alternation signal and this new one).
2. **Reused, not new**: candidate age, already available as `i - st.start_ts`.
3. **Reused, not new**: `boundary_upper`/`boundary_lower`, already available, used only as the *gate* for
   eligibility (§9) — the staleness check itself does not recompute boundaries.

From (1), on demand (not as a separately-maintained running counter — matching the existing
`efficiency_ratio`/`traversal_count`/`alternation_rate` convention of pure functions over a bounded window,
not incremental accumulators): a **rejection count** within a bounded trailing sub-window, and an
**alternation count** (H/L flips) within that same evidence, using the identical flip-counting logic already
proven in `alternation_rate`/`traversal_count` (no new counting algorithm invented).

**Explicitly rejected as unnecessary**: zone-overlap percentage, ATR-normalized distance, a separate
"boundary age" field (redundant with `start_ts` + the rejected-touch timestamps already recorded), and any
running/incremental counter (the existing project-wide discipline is bounded-window-recomputed-on-demand, not
incrementally maintained state — matching the 0.4.1/RT-RANGE-0004 O(1)-slope precedent's own resolution
already cited throughout the V4.4 delivery).

---

## 8 — Transition table amendment / kill semantics (mandate §9)

**New transition, `T-STALE`**: `CANDIDATE`/`FORMING → TERMINATED`, reason `STALE_CANDIDATE_ABANDONED`.

- **Trigger**: `reached_confirmed = False`, boundary established (`boundary_upper`/`boundary_lower` both
  set — i.e. past `ESTABLISHING_FEW_SWINGS`; a candidate that has not yet gathered its minimum touches is
  structurally exempt, not merely policy-exempt, §6), candidate age past a minimum floor
  (`UNRESOLVED_PARAMETER`), and the rejected-touch evidence within the bounded window satisfies **both** a
  minimum rejection count **and** a minimum alternation count (both `UNRESOLVED_PARAMETER`).
- **Priority**: checked immediately after `T-KILL` (`degeneracy_check`) and before `T2`/`T3`
  (`_evaluate_macro_formation`), inside `_step_macro`'s existing `zones is None` branch (confirmed by direct
  re-read: `range_semantic_v4_4.py:889–896` — `T-KILL` at 889–892, the `zones is None` branch begins at 894).
  `T-STALE` never applies once `zones is not None` (i.e., never to a confirmed/`WEAKENING` structure) — the
  two are structurally disjoint via `reached_confirmed`, so there is no priority conflict with T4–T9.
- **Destination**: identical mechanics to the existing `_kill_macro` (line 609) — `end_ts`/`end_reason` set,
  pushed to `_macro_history`, `_registry.kill`, `_active_macro = None`, `_macro_excursion = None` — and,
  critically, **calls the existing, unmodified `_record_macro_termination_for_episode_identity`** (line 645)
  exactly as `_kill_macro` already does. This is not a new episode-identity rule (§9 below resolves why none
  is needed).
- **Emitted event**: one `RangeEventV43(kind=STALE_CANDIDATE_ABANDONED, ...)`, matching the existing event
  shape for every other termination reason.
- **Reachability**: exactly like `EPISODE_MERGED`'s existing precedent, this code's reachability must be
  *proven*, not asserted, by a dedicated test (§14, STALE-1) — not assumed reachable merely because it is
  wired in.
- **Deterministic**: yes — the trigger is a pure function of already-bounded, already-deterministic state
  (the rejected-touch deque, itself populated only by the existing, unmodified `offer_swing` call sequence).
  No randomness, no wall-clock, no ordering ambiguity.

---

## 9 — Same-bar vs. next-bar replacement semantics (mandate §10) — resolved, not left open

**Decision: (B) — a fresh candidate may only begin forming from the next causal observation onward. The
swing that contributed to the abandonment decision is never itself replayed to seed the replacement.**

Reasoning, worked through explicitly against each of the mandate's own listed concerns:

- **Mechanical fit**: in `observe()`'s existing per-bar order, swing offering (`_offer_swing_everywhere`,
  which is where `offer_swing`'s accept/reject happens) runs **before** `_step_macro` (where `T-STALE` would
  fire). So by the time a bar's abandonment could trigger, that same bar's own swing has already been
  offered-and-rejected by the (still-alive, at that point) stale candidate — there is no pending, unconsumed
  swing left over from the triggering bar to hand to a hypothetical fresh candidate within the same
  `observe()` call. Choosing (A) would require restructuring the swing-offering flow to re-run for the same
  bar against a newly-formed candidate — genuine added complexity for no evidenced benefit.
- **No lookahead**: (B) trivially satisfies this — the kill decision at bar `i` uses only information already
  known at `i`; the replacement forms from bar `i+1`'s swing detection, which is itself causal.
- **No double-use of a swing**: (B) guarantees the swing(s) that produced the rejection evidence are
  "spent" as rejection evidence only, never reinterpreted as acceptance evidence for a different candidate in
  the same instant. Precedent: this matches how **every existing** slot-freeing path already behaves —
  `_kill_macro` (T-KILL), `_close_macro_via_breakout` (T8), `_terminate_macro_weakening_persistence` (T9) —
  none of them re-offers the triggering bar's own evidence to an immediately-formed successor; the next
  candidate always begins from a subsequent bar's swing detection. `T-STALE` under (B) is therefore not a new
  pattern, it is consistency with the only pattern that already exists.
- **Deterministic replay / snapshot-restart / chunk invariance**: (B) leaves no complex "pending same-bar
  re-offer" partial state to serialize — immediately after bar `i`'s `observe()` returns, `_active_macro` is
  cleanly `None`, exactly like every other termination path, so the existing snapshot/restore and
  chunk-invariance guarantees extend to `T-STALE` without any new state-machine edge case to reason about.

---

## 10 — Anti-churn analysis (mandate §12) — the alternation requirement *is* the anti-churn mechanism

This is the load-bearing property of this design, not an afterthought bolted on.

A clean, one-directional trend (mandate's own churn worry — "trend/channel must not cause candidate → stale
kill → immediate new candidate → stale kill → repeated RANGE attempts without bound") produces swings that
are **predominantly one-sided** by definition (a trend that retraced enough to generate frequent alternating
highs *and* lows would not be a clean trend). Because `T-STALE`'s trigger requires the rejected-touch evidence
to show genuine **alternation** — not merely volume of rejections — a stale candidate sitting in the path of
such a trend simply **does not accumulate qualifying evidence** and is not repeatedly killed and reformed. It
stays stuck (an already-known, disclosed, non-blocking limitation — an un-killed stale candidate during a pure
trend is not worse than today's V4.4 behavior in that specific case, since no genuine RANGE TP is being missed
during a genuine trend anyway). Only when the market's character genuinely turns two-sided again — which is
exactly the FB14-003 CHANNEL_UP-then-RANGE transition this design targets — does the alternation requirement
clear, triggering **one** abandonment at approximately the right moment, not a churn cascade.

This was checked directly against `b1dcf92`'s own traced rejection sequence for FB14-003
(`LHLHLHLLHLHLHHLHLHHLHLHHLHLLHLHLLHLHLH` — genuinely alternating throughout the CEO's labeled RANGE) — the
qualifying evidence was present continuously once the true range began, not as an isolated one-off spike, so
a reasonably-set threshold would not need to sit on a knife-edge to catch this case.

No cooldown/hysteresis numeric value is introduced to solve churn in this mandate — the alternation
requirement is the structural anti-churn property; if calibration (§16) later finds edge cases where it is
insufficient alone, any additional cooldown parameter becomes its own `UNRESOLVED_PARAMETER`, not assumed
necessary here.

---

## 11 — Interaction with traversal (mandate §13)

Confirmed explicitly, after completing the full design: **traversal remains completely frozen.**
`T-STALE` never touches `traversal_count`, `MIN_TRAVERSALS`, `W`, or any trailing-closes computation. The
correction's entire effect is to let a **fresh** candidate exist and be evaluated by the **unchanged**
traversal gate — never to make the stale candidate itself pass traversal, and never to alter what traversal
means or how it is computed for any candidate, stale or fresh.

---

## 12 — Interaction with ER/RND (mandate §14)

Also confirmed explicitly: a candidate formed after a `T-STALE` abandonment is **exactly as new candidate
as any other** — it enters `_offer_swing_everywhere`'s existing MACRO-formation path, gets a fresh
`StructureV44`, and must independently satisfy the complete, unmodified `_evaluate_macro_formation` gate (ER,
traversal, RND, duration, touch count) to ever confirm. A replacement candidate that forms during a
still-continuing directional trend (§10's protected case, if it ever did occur) would still correctly fail T3
on the same directional grounds V4.4 was built to detect. Staleness abandonment changes **who gets evaluated**,
never **how evaluation works**.

---

## 13 — Self-falsification (mandate §11, 16 scenarios)

| # | Scenario | Abandonment expected? | Why |
|---|---|---|---|
| 1 | Clean RANGE, slow formation | No | touches accepted normally as they arrive; no rejection evidence accumulates |
| 2 | Sparse-touch RANGE | No | infrequent touches, if within tolerance, are accepted not rejected; silence alone never triggers (§6) |
| 3 | Genuine RANGE using only a sub-band initially | No | later touches near the current median stay in tolerance and are accepted |
| 4 | Shallow CHANNEL_UP | No new false-accept | already correctly never confirms; if it goes stale, a fresh candidate forms and *also* correctly fails T3 (§12) — behavior unchanged, only occupancy churns |
| 5 | Shallow CHANNEL_DOWN | No new false-accept | mirror of 4 |
| 6 | Strong trend | Protected from churn | predominantly one-sided rejected evidence fails the alternation requirement (§10) |
| 7 | Stair-step trend | Protected from churn | each step's rejected evidence is not genuinely alternating at the macro scale; same protection as 6 |
| 8 | Range after a directional regime | **Yes, abandonment intended** | this is the FB14-003 shape exactly — trend's stale candidate persists (protected, §10) until the market turns two-sided, at which point alternating rejections accumulate and correctly trigger `T-STALE` |
| 9 | Long low-volatility compression | No | few or no swings detected at all; no evidence either way; candidate simply continues waiting |
| 10 | Boundary-migrating RANGE | Improvement, not new risk | today's blind spot too (an early narrow anchor can itself go stale); `T-STALE` lets a correctly-wider fresh candidate form |
| 11 | Violent zigzag | Unaffected | confirms today via genuine accepted two-sided touches (disclosed, accepted risk) — its cluster keeps accepting, so it never goes stale in the first place |
| 12 | One-sided oscillation | No | quiet/absent evidence on one side never counts toward rejection-based staleness (§6) |
| 13 | Temporary breakout then re-entry | N/A to `T-STALE` | this is *confirmed*-structure territory (WEAKENING/excursion machinery), which `T-STALE` never touches (`reached_confirmed=True` structures are outside its scope entirely) |
| 14 | Candidate with long silence then valid second boundary | No premature kill | silence produces no rejection evidence; if the eventual new boundary activity is *accepted* by the same candidate, it simply matures normally; if it is genuinely a different, rejecting, alternating zone, `T-STALE` correctly hands off — either outcome is correct |
| 15 | Repeated rejected swings far away from stale candidate | **Yes, if alternating** | this is the direct target case; if the far-away rejections are one-sided (a trend), protected per 6/7 |
| 16 | New true RANGE forming after an old failed candidate | **Yes, abandonment intended** | this is the FB14-012 shape; same mechanism as 8 |

**No counterexample found that reintroduces a directional false-accept or an unbounded churn pattern.** The
weakest points, disclosed honestly: (a) scenario 9's boundary with scenario 8/16 — a compression phase that
*slowly* turns into genuine two-sided activity depends on the exact rejection-count/alternation-count
thresholds not being so loose that ordinary noise qualifies, nor so tight that genuine regime change is
missed — this is precisely what calibration (§16) must resolve on fresh evidence, not assumed safe by
argument; (b) the minimum-age floor (§8) has not been derived here, only flagged as necessary.

---

## 14 — New parameter inventory (mandate §15) — names illustrative only, none adopted

| Parameter | Purpose | Units | Role | Derivation hypothesis |
|---|---|---|---|---|
| rejected-touch window length | bounds the trailing evidence considered | bars | structural | **RATIFIED_REUSE hypothesis**: reuse `W=29`, the same trailing-window concept already governing ER/RND/traversal — to be *confirmed*, not assumed, in calibration |
| minimum rejection count | how much rejected evidence is "enough" | count | structural | likely `CALIBRATED` — no existing ratified analog; candidate for synthetic derivation similar to how `MIN_TRAVERSALS=1` was reasoned from a touch-order counterexample in `898f149` |
| minimum alternation count | how "two-sided" the rejected evidence must be | count (H/L flips) | structural, **anti-churn-critical** (§10) | possibly `DERIVED` as a natural floor (e.g. ≥1, mirroring `MIN_TRAVERSALS`'s own floor-derivation logic) rather than swept — to be tested first as a floor before treating as a free parameter |
| minimum candidate age before eligibility | protects brand-new candidates from instant staleness evaluation | bars | gating, not triggering | possibly `DERIVED` from `n_touch` and expected touch spacing (how many bars a candidate plausibly needs to reach its minimum touch count under typical conditions) rather than an independent free value |

Four candidate parameters, deliberately not five or six — each one's necessity was re-examined against
"prefer fewer parameters" (mandate §15) and the state-variable minimality already argued in §7. No parameter
here was chosen, ranked, or swept using FB14 or MB3-001→024; both were used only to observe the failure
mechanism these parameters must eventually resolve.

---

## 15 — Calibration plan (mandate §16 — design only, not executed)

Matching the established, already-successful protocol from `967222a`/`898f149` (V4.4's own original
calibration), applied fresh to this new mechanism:

1. **Pre-register before any result is seen**: for each of the four parameters (§14), fix the candidate
   family, selection method, and failure criterion *before* running any construction scenario.
2. **Eligible evidence, in priority order**: (a) synthetic construction — known-ground-truth price paths
   specifically engineered to exercise each of the 16 self-falsification scenarios (§13) at varying
   parameter values; (b) analytical/ratified-reuse derivation (e.g. testing the `W=29` reuse hypothesis
   directly against the alternation-window math); (c) **not** FB14, **not** MB3-001→024, **not**
   MB3-025→048 — all three explicitly zero-calibration-weight for this mandate and the one that follows it.
3. **Dual-sided protection, pre-registered as the actual acceptance bar** (mandate §16.A/B): every candidate
   parameter value must be checked against *both* — (A) does it release a genuinely stale candidate blocking
   a real regime change (scenarios 8/16), and (B) does it leave a legitimately slow-forming or quiet range
   undisturbed (scenarios 1/2/3/9/12/14)? A value that passes only one side is rejected, not averaged toward.
4. **No F1 optimization, no FB14 threshold sweep** — matching the mandate's explicit prohibition, and the
   same discipline already proven in `898f149` (which resolved 9 parameters via synthetic construction and
   ratified reuse, zero MB3 influence, and disclosed rather than tuned away the one risk it could not clear).
5. **Sensitivity check**: once each parameter has a candidate value, a neighborhood sweep (matching `898f149`'s
   own `W∈{22,29,45}`/`IOU_CONTINUE∈{0.4,0.5,0.6}` precedent) to classify each as STABLE / MODERATELY_SENSITIVE
   / FRAGILE, flagging any `PARAMETER_FRAGILITY_FLAG` honestly rather than silently picking a convenient point.
6. **Output**: a frozen `ConfigV441` (or equivalent) parameter registry with a computable `config_id()`,
   exactly mirroring `ConfigV44`'s own identity discipline — produced by a **separate**, future calibration
   mandate, not this one.

---

## 16 — Snapshot / versioning impact (mandate §18)

- **`StructureV44` field addition**: one new bounded deque (rejected-touch records, §7) →
  `snapshot()`/`restore()` gain one new `v441_*`-prefixed key pair, following the exact existing
  `v44_*`-prefix convention (itself following V4.3's own precedent).
- **Config schema**: the new parameters (§14) join `ConfigV441` as new fields; `config_id()` reproduces the
  identical sha256-over-sorted-fields formula already used by `ConfigV43`/`ConfigV44`, now covering the
  additional fields.
- **Reason-code registry**: `REASONS_V441 = REASONS_V44 + (STALE_CANDIDATE_ABANDONED,)` — 41 total, additive,
  unrenumbered, following the exact precedent of how `REASONS_V44` extended `REASONS_V43`.
- **Contract version**: a new `contract_version = "range-hierarchical-v4.4.1"` string, distinct from
  `"range-hierarchical-v4.4"` — required regardless of how small the change is, because the mandate's own
  §18 requirement ("V4.4 snapshots must not silently restore into incompatible V4.4.1 semantics") demands
  fail-closed separation, and the existing `restore_state()` fail-closed check (already atomic per the
  V4.4 delivery's own fix, `3bb61cf`) already refuses on any `contract_version` mismatch — this is the
  **same mechanism**, not a new one, simply given a new value to check against.
- **Implementation fingerprint**: recomputed after implementation (not before, matching the established
  `PENDING_FREEZE`-until-actually-frozen discipline) over whichever files change — expected to be
  `range_semantic_v4_4.py`'s successor file (or the same file, in-place, if the eventual implementation
  mandate chooses additive-in-file rather than a new `range_semantic_v4_4_1.py` — an open packaging
  question for that future mandate, not resolved here) plus `range_engine_v4_4.py`'s successor.
- **No silent migration**: a V4.4 snapshot fed to a V4.4.1 restorer fails closed on `contract_version`
  mismatch (existing mechanism); a V4.4.1 snapshot fed to a V4.4 restorer likewise fails closed (V4.4's own
  `restore_state` already refuses unrecognized `contract_version`/`config_id` — no new behavior required on
  the V4.4 side, since V4.4 itself is never modified).

---

## 17 — Test plan (mandate §19)

| Test | Content |
|---|---|
| STALE-1 | A failed-directional candidate (constructed to reproduce the FB14-003 shape: early one-sided formation, T3-rejected, then genuinely alternating rejected touches) is eventually abandoned; `STALE_CANDIDATE_ABANDONED` is mechanically reachable — proven, not asserted, matching the `EPISODE_MERGED`-reachability precedent |
| STALE-2 | After abandonment, a fresh candidate forms from a *subsequent* bar's swing and correctly confirms against a synthetic zone matching the "true range" the stale candidate was blocking |
| STALE-3 | A slow, genuine, quiet range (self-falsification scenarios 1/2/3/9) is never abandoned — construction-scenario regression, directly encoding the dual-sided calibration bar (§15.3) |
| STALE-4 | A clean one-directional trend (scenarios 6/7) does not churn — bounded number of `T-STALE` events over a long synthetic trend, ideally zero, certainly not unbounded |
| STALE-5 | A candidate formed immediately after abandonment still correctly fails ER/RND/traversal if the market is still genuinely directional (§12) |
| STALE-6 | Same-bar/next-bar semantics: the exact bar of abandonment never has its own triggering swing double-counted as acceptance evidence for the replacement (§9) — a direct, mechanical assertion on `observe()`'s per-bar event sequence |
| STALE-7 | Snapshot/restart exactly at, immediately before, and immediately after an abandonment bar produces identical subsequent chronology to a continuous replay |
| STALE-8 | Prefix/chunk invariance holds across an abandonment event, matching the existing 96/288/480-container and arbitrary-split-point tests already proven for V4.4 |
| STALE-9 | The full existing V4.4 adversarial suite (22/22) and transition suite re-run unchanged against V4.4.1 where no staleness condition is ever met — zero behavioral difference from V4.4 in all cases that do not involve a genuinely stale candidate |
| STALE-10 | INTERNAL-depth parity (the existing `test_v4_4_internal_parity.py` methodology) re-run against V4.4.1 — `T-STALE` is MACRO-only by construction (§4), so INTERNAL output must remain byte-identical |

Additionally (beyond the mandate's named 10, because the established V4.4 delivery discipline requires it and
this design explicitly inherits that discipline): a **mutation test** disabling the alternation requirement
specifically (leaving only the rejection-count check) must be shown to reopen the trend-churn risk (§10),
proving the alternation requirement is load-bearing and not vacuous.

---

## 18 — Preservation matrix (mandate §20 item 16)

| V4.4 component | Touched by this design? | Evidence |
|---|---|---|
| ER / RND mechanisms | No | §11/§12 |
| Traversal definition | No | §11 |
| Alternation `SUPPORTING_ONLY` role | No — a *new*, separate rejected-touch alternation measure is introduced, kept structurally distinct from the existing accepted-touch `_touch_tags`/`alternation_rate` (§7) | §7 |
| `WEAKENING` (T4–T9) | No — structurally disjoint via `reached_confirmed` (§8) | §8 |
| Confirmation timing / causality invariance | No new invariant needed beyond re-proving the existing ones hold across the new transition (STALE-7/8) | §17 |
| Confirmed-episode lifecycle | No | §8 |
| Episode identity (MERGE/CONTINUATION/REPLACEMENT) | No new rule — reuses the existing, unmodified priority logic unchanged, which naturally resolves correctly because a genuinely stale zone will not IoU-overlap its replacement (§8) | §8 |
| Snapshot architecture | Extended (new fields, new contract version), not redesigned | §16 |
| Reason-code architecture | Extended by exactly one code, unrenumbered | §16 |

---

## 19 — Versioning recommendation (mandate §17)

```
RECOMMEND: V4.4.1
```
Matches the mandate's own stated V4.4.1 threshold precisely: the state-machine concept remains fundamentally
V4.4 (5 states unchanged; one new edge into the already-existing `TERMINATED` state); directional gates are
completely unchanged (§11/§12); only pre-confirmation candidate lifecycle gains one additive, narrowly-scoped
abandonment path. No broader semantic redesign was found necessary anywhere in this design.

---

## 20 — Remaining risks (mandate §20 item 18)

1. **All four new parameters are genuinely unresolved** (§14) — none has even a provisional value; the
   calibration plan (§15) is a design, not a result.
2. **The minimum-age floor and its interaction with `d_macro`/`n_touch`** has not been derived, only flagged
   as structurally necessary.
3. **The dual-sided calibration bar (§15.3) is harder to clear than a single-sided one** — by design, since a
   value that only protects TP-recovery without protecting slow/quiet ranges would reintroduce exactly the
   kind of risk this mandate was created to avoid. This may mean no single value cleanly satisfies both sides
   across all 16 scenarios; if so, the future calibration mandate must disclose that honestly (matching the
   shallow-channel precedent in `898f149`), not force a value.
4. **The episode-identity interaction (§8) is argued, not tested** — the claim that a stale zone naturally
   fails to IoU-overlap its replacement is grounded in this mandate's own empirical evidence (both traced
   cases showed 0.000 price-IoU) but has not been proven as a general property; STALE-2/STALE-9 should include
   an explicit IoU-continuation check once implemented.
5. **The related, distinct episode-identity observation from `b1dcf92` §8** (forced `EPISODE_REPLACEMENT`
   after `BREAKOUT_ACCEPTED` possibly over-fragmenting a CEO-continuous range) remains unaddressed and
   explicitly out of scope here, as it was in the diagnostic.

---

## 21 — Exact next CEO action

Authorize a **separate, future calibration mandate** for the four parameters in §14, following the plan in
§15, producing a frozen, calibrated `ConfigV441` registry and pre-registered decision criteria — **before**
any implementation mandate is authorized for this design. That calibration mandate should explicitly inherit
this design's scope boundary (§4) and its two structural constraints that must not be loosened during
calibration: rejection-count-based (never touch-scarcity-based, §6) and alternation-gated (the anti-churn
property, §10).

---

## FINAL VERDICT

```
V4_4_1_STALE_DESIGN_READY_FOR_CALIBRATION
```

No implementation performed or authorized. No numeric parameter chosen, ranked, or swept. `FB14 =
DIAGNOSTIC_ONLY_ZERO_CALIBRATION_WEIGHT` honored throughout — used only to re-confirm the mechanism this
design targets (§2), never to shape any parameter. `MB3-025→048` sealed and untouched. Not authorized by
anything here: implementation, Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker, live trading, V4.4
promotion.

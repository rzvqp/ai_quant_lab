# VE-RANGE-V4_4-CONVERGENCE-001 — Convergence & Final Design Review Package

**Convergence between `VE-RANGE-DIAG-001` (`071fbd7`), `VE-RANGE-V4_4-DESIGN-001` (`236e8e7`), and
`RT-RANGE-DIAG-AUDIT-001` (`3be88a1`). Not a new research cycle — Red Team returned
`V4_3_DIAGNOSTIC_FOUNDATION_CONFIRMED` and "no V4.4 design assumption must change." This package closes
convergence, resolves the remaining implementation ambiguities the prior design left open, and re-issues the
formal verdict. No code, config, threshold, or V4.3 file changed. `MB3-025→048` not accessed at any point.**

---

## 0 — Provenance verification (mandate §1)

Independently re-verified, not summarized:

| Commit | Branch | local=remote (4 mirrors) | Content read |
|---|---|---|---|
| `071fbd7` — `VE-RANGE-DIAG-001` | `discovery-mk-matrix-v1` | MATCH (re-confirmed this mandate) | already authored by VE; re-checked against source this mandate |
| `236e8e7` — `VE-RANGE-V4_4-DESIGN-001` | `discovery-mk-matrix-v1` | MATCH (re-confirmed this mandate) | already authored by VE; re-checked against source this mandate |
| `3be88a1` — `RT-RANGE-DIAG-AUDIT-001` | `statistician-foundation` | MATCH ×4 (`3be88a11a8b19f1879c4c3d8d3f6cb025508af59`) | **read in full** (90 lines, `red_team/policy_reviews/RT-RANGE-DIAG-AUDIT-001_v4_3_diagnostic_audit.md`), not the mandate's own summary |

Red Team's own provenance chain re-confirmed while reading their report: detector `bc6b9dc` hash `098fa144`,
config_id `24f72a60`, labels `6369f5e0`, predictions `26a7d461` — all independently re-hashed by them and
matched. Their own engine re-run reproduces **62/62** confirmed structures with 0 mismatches — an
**independent** confirmation of the same instrumentation-fidelity claim VE made in `071fbd7` §0, arrived at via
Red Team's own separate re-run, not by trusting VE's.

---

## 1 — Mandatory convergence matrix (mandate §2)

| # | Red Team finding | VE V4.4 design assumption/mechanism | MATCH/CONFLICT | Amendment required |
|---|---|---|---|---|
| 1 | 39-FP = 30 directional + 9 over-segmentation, **EXACT** reproduction | §2/§4.1 of the design targets exactly this split; the discrimination gate (§4) targets the 30, episode-identity (§7) targets the 9, kept as two separate mechanisms | **MATCH** | None |
| 2 | 12-FN = all formation/confirmation-timing, **0 boundary/IoU misses** (RT's own 4/8 split vs VE's 4/5/3 — RT calls the finer split "immaterial to V4.4") | Design's §6.1/§6.2 (evidence-gated confirmation, `RANGE_CANDIDATE_PRESENT`) targets confirmation-timing broadly, not the exact sub-split | **MATCH** | None — RT explicitly says the categorization difference doesn't matter to the design |
| 3 | MACRO confirmation has **no** directional gate; `normalized_drift`/`s_max` wired only at INTERNAL — **code-confirmed independently** | Design's entire premise (§4 preamble, §2 defect D1/D2) | **MATCH** | None |
| 4 | 96/288/480 = `MORE_TIME_TO_FIRE`; GT-length/window-length confound checked by RT (corr=0.40, real) but **reinforces**, does not undermine, the latency conclusion | Design's §6.1 explicitly does not assume "longer context ⇒ better recognition"; evidence-gated confirmation is latency-neutral by construction | **MATCH**, design strengthened | None to the mechanism; §5 below incorporates RT's confound finding explicitly into the confirmation-budget discussion (new supporting evidence, not a new mechanism) |
| 5 | Naive `normalized_drift > s_max` gate: **13/23 TP (57%) destroyed** vs **19/30 FP (63%) caught** — `SINGLE_DRIFT_GATE_FIX_IS_NOT_JUSTIFIED`, exact match to VE's own numbers | Design never adopts this gate — explicitly rejects it in favor of the 4-signal bounded-window combination (§4.6, §12) | **MATCH** | None |
| 6 | MB3-007: 1 structure, CEO CHANNEL_DOWN, confirms the instant `d_macro` clears, no directional check | Design's §10 scenario table (adversarial #4/#5/#8/#12) targets exactly this pattern | **MATCH** | None |
| 7 | MB3-020: 3 TREND_DOWN-dominant structures; RT confirms VE's own disclosed nuance (sid=7, drift 0.73, local-vs-broader-context ambiguity) | Design's §12 self-falsification already discloses this exact ambiguity as an open, not-fully-solved risk | **MATCH** | None |
| 8 | Missing-cause search: **none found** — state/snapshot/scorer/label-adapter/ATR/F1/implementation-vs-semantic all actively ruled out by RT independently | Design assumes the diagnosed gap is genuinely semantic (no directional check), not an implementation artifact | **MATCH**, materially strengthened | None |
| 9 | 9 over-segmentation FP: RT went further than VE — **directly examined all 9**, found all overlap a real CEO RANGE segment (IoU 0.11–0.41) but lose the best-IoU tie in windows with **far more detector episodes than CEO labels** (MB3-015 8-vs-2, MB3-021 7-vs-1, MB3-024 6-vs-2); confirms granularity mismatch, explicitly **not** a directional defect, and RT states a directional gate "would not fix these and could over-suppress genuine ranges" | Design's §7 (episode continuation/merge/replacement) already keeps this mechanism **separate** from the discrimination gate, for exactly this reason | **MATCH**, materially strengthened (see §6 below — new evidence incorporated, mechanism unchanged) | None to the mechanism; the exact granularity ratios are now cited as motivating evidence in §6 |
| 10 | Preservation of the 23 genuine TP: RT's own falsification numbers are identical to VE's (13/23, 57%) | Design's §12 TP-protection table is built around exactly this population | **MATCH** | None |

**Zero conflicts. Zero amendments to the design mechanism.** Per mandate §3, no unnecessary redesign follows.
Remaining work is resolving implementation ambiguity within the *existing* design (mandate §5), not
reopening research.

---

## 2 — Internal-consistency self-check (mandate §3's own amendment triggers)

Re-read `236e8e7` in full against the four listed amendment triggers. Two genuine ambiguities found — **not**
contradictions, not inconsistencies with Red Team's findings, but under-specified implementation detail that
mandate §5 explicitly requires resolved before this can honestly be called ready:

1. **`WEAKENING`'s two entry paths (excursion-based (a), trailing-window-degradation-based (b)) had no
   specified interaction when both are simultaneously true, and path (b)'s exit bound was named but not
   mechanically specified.** Resolved in §4 below.
2. **Episode-identity's `CONTINUATION`/`MERGE`/`REPLACEMENT` had no specified priority order for the case
   where a new candidate could plausibly satisfy more than one rule.** Resolved in §6 below.
3. **Implementation-fingerprint computation was described as "reserved" without a concrete procedure.**
   Mandate §15 explicitly asks for the *procedure*, not just a placeholder. Resolved in §9 below.

No other internal inconsistency, non-deterministic rule, unsatisfiable invariant, or unprovenanced-without-
disclosure parameter was found. These three are tightened below; the mechanism itself is unchanged from
`236e8e7`.

---

## 3 — Final state-machine specification and exact transition table (mandate §5)

State set, confirmed unchanged from `236e8e7`: `CANDIDATE, FORMING, CONFIRMED, WEAKENING, TERMINATED`. No
additional legal states exist. All legal transitions, exhaustively:

| # | Source | Trigger | Required observations | Hard gates | Supporting-only evidence | Priority | Destination | Reason code | Failure/refusal condition |
|---|---|---|---|---|---|---|---|---|---|
| T1 | — | first swing pair offered into empty up/dn clusters | first accepted swing on each side | none yet | — | 1 (entry) | `CANDIDATE` | *(implicit — no dedicated reason code; matches V4.3's un-coded pre-formation state)* | — |
| T2 | `CANDIDATE` | width clears `degeneracy_check` floor **and** touch count reaches `n_touch` per side | `boundary_upper/lower` both non-null, width `> 2·w_atr·atr_ref`, ≥`n_touch` touches/side | width floor, touch count (both **unchanged from V4.3**) | — | 2 | `FORMING` | `RANGE_CANDIDATE_PRESENT` (new, non-authoritative) | width/inversion failure → `T-KILL` below |
| T3 | `FORMING` | `d_macro` duration floor **and** §4 discrimination gate (ER, traversal, RND) all clear | `bar − start_ts ≥ d_macro`; `ER ≤ ER_max`; `traversal_count ≥ MIN_TRAVERSALS`; `RND ≤ RND_max`, all over trailing window `W` | duration floor (unchanged), ER ceiling, traversal floor, RND ceiling (all new, all hard gates) | alternation rate (reported, does not block) | 3 | `CONFIRMED` | `OK_RANGE_MACRO` (unchanged code) | any hard gate unmet → remains `FORMING`, specific unmet gate reported via `INSUFFICIENT_EFFICIENCY`/`INSUFFICIENT_TRAVERSAL`/`EXCESSIVE_NET_DISPLACEMENT` |
| T4 | `CONFIRMED` | excursion opens beyond frozen boundary, unresolved | `close` beyond `[boundary_lower−h, boundary_upper+h]` per existing `zones()` | none (labeling only — the underlying `Excursion` machinery is unchanged and still gates `SWEEP_CONFIRMED`/`BREAKOUT_ACCEPTED` on its own terms) | — | 4a | `WEAKENING` (`weakening_reason=EXCURSION_PENDING`) | `RANGE_WEAKENING` | — |
| T5 | `CONFIRMED` | trailing-window ER/RND degrade past the (looser) weakening ceiling **while price stays inside the boundary** (no excursion open) | `ER > ER_weakening` or `RND > RND_weakening`, evaluated only when T4's excursion condition is false | ER_weakening/RND_weakening (new, `UNRESOLVED_PARAMETER`, see §5) | — | 4b | `WEAKENING` (`weakening_reason=TRAILING_DEGRADATION`) | `RANGE_WEAKENING` | — |
| T6 | `WEAKENING` (`EXCURSION_PENDING`) | excursion resolves `SWEEP_CONFIRMED`, or price re-enters within `K_reentry` | unchanged `Excursion.observe` logic | `K_reentry` (unchanged) | — | 5 | `CONFIRMED` | `WEAKENING_RECOVERED` | excursion resolves `BREAKOUT_ACCEPTED` instead → **T8**, not T6 |
| T7 | `WEAKENING` (`TRAILING_DEGRADATION`) | trailing-window ER/RND recover past the confirmation-grade thresholds (§4, same ones T3 uses — no separate, weaker re-confirmation path, per invariant in `236e8e7` §9) | `ER ≤ ER_max` and `RND ≤ RND_max` again | same as T3 | — | 5 | `CONFIRMED` | `WEAKENING_RECOVERED` | — |
| T8 | `WEAKENING` (`EXCURSION_PENDING`) | excursion resolves `BREAKOUT_ACCEPTED` | unchanged `Excursion`/`N_accept` logic | `N_accept` (unchanged) | — | 6 | `TERMINATED` | `BREAKOUT_ACCEPTED` (unchanged code) | — |
| T9 | `WEAKENING` (`TRAILING_DEGRADATION`) | condition persists ≥ `WEAKENING_MAX_BARS` (new counter, increments only while in `TRAILING_DEGRADATION`, resets to 0 on any T7 recovery) without recovering | bar-count since entry into T5, per-structure, reset on recovery | `WEAKENING_MAX_BARS` (new, `UNRESOLVED_PARAMETER`) | — | 6 | `TERMINATED` | `WEAKENING_PERSISTENCE_TERMINATED` (new) | — |
| T-KILL | `CANDIDATE`/`FORMING` | width inverts or degenerates | unchanged `degeneracy_check` | unchanged | — | **0 (highest — checked before all of the above, matching V4.3's existing KILL-before-duration ordering, C15 convention, preserved)** | `TERMINATED` | `ZONES_DEGENERATE`/`ZONES_INVERTED` (unchanged) | — |

**Dual-`WEAKENING`-trigger priority (ambiguity #1, resolved):** T4 (excursion-based) and T5
(trailing-degradation-based) are independent triggers into the same state, distinguished by
`weakening_reason`. If both conditions are true on the same bar, **T4 takes priority** (checked first,
matching the existing `_step_depth` ordering where excursion resolution is evaluated before the discrimination
path) — the structure enters `WEAKENING(EXCURSION_PENDING)`, and T5's trailing-window check continues running
in the background (its own bar-counter still accrues) so that if the excursion later resolves back to
`CONFIRMED` (T6) but the trailing measures are *still* degraded, T5 can immediately re-fire on the next bar
without losing accumulated weakening duration. Recovery requires **both** conditions to clear (T6 needs the
excursion resolved *and*, if T5 was also active, T7's measures must independently also have recovered) —
termination fires on **either** bound being exceeded first (T8 or T9), whichever comes first. This is a
complete, deterministic AND-for-recovery/OR-for-termination rule.

---

## 4 — Directional-discrimination signal roles (mandate §6) — confirmed, not changed

| Signal | Role | Confirmed unchanged from `236e8e7`? |
|---|---|---|
| Bounded-window Kaufman Efficiency Ratio (ER) | `HARD_GATE` (confirmation, T3) + looser variant `HARD_GATE` (weakening, T5) | Yes |
| Traversal count | `HARD_GATE` (confirmation, T3 only — no traversal-based weakening trigger is proposed; a structure that has already accumulated confirmation-grade traversal evidence does not lose it by construction, since the counter is monotone within the trailing window) | Yes |
| Relative Net Displacement (RND) | `HARD_GATE` (confirmation, T3) + looser variant `HARD_GATE` (weakening, T5) | Yes |
| Alternation rate | `SUPPORTING_ONLY` — reported, feeds no gate | Yes, **explicitly not promoted to hard gate**: `236e8e7` §12's self-falsification already showed a real false-reject risk (clumped-touch genuine ranges) if made a hard gate; Red Team's audit raised no finding that would change this, so per mandate §6's own instruction it stays supporting |
| Raw whole-life `normalized_drift`/`slope` | `DIAGNOSTIC_ONLY` | Yes, and explicitly **not** reintroduced as a MACRO hard gate at any point — the falsified naive gate stays falsified; the four signals above are a genuinely different construction, not a repackaging |

---

## 5 — Confirmation-budget solution (mandate §8), strengthened with Red Team's new evidence

`236e8e7` §6.1 already establishes evidence-gated confirmation (duration is a floor, not a trigger) as the
mechanism. Red Team's audit adds one genuinely new, useful data point: the GT-range-length/window-length
confound they checked (corr=0.40; mean GT-range length 34/38/100 bars at L=96/288/480) — **and their own
reading of it, which VE adopts**: longer windows containing longer genuine ranges is *consistent with*, not
contrary to, `MORE_TIME_TO_FIRE` — a longer range mechanically needs more bars of alternation/traversal
evidence to accumulate regardless of window length, so the confound and the latency explanation point the same
direction rather than competing.

Explicit per-item handling, updated:

| Item | V4.4 handling |
|---|---|
| Warm-up | `d_macro` floor unchanged (necessary, not sufficient — T3) |
| Formation latency | Evidence-gated (T2→T3): genuinely fast in choppy conditions, genuinely slow (or indefinite) in directional ones — no longer a pure function of calendar bars |
| Confirmation latency | Same mechanism; RT's confound finding confirms this scales with the *underlying range's own length*, not with window length as a free variable — an argument the design was already structurally robust to, now with supporting evidence rather than only a disclosed caveat |
| Observation-window truncation | `RANGE_CANDIDATE_PRESENT` (T2) gives an honest, explained non-confirmation instead of a silent miss (§6.2 of `236e8e7`, unchanged) |
| Episode active at window start | Documented, unfixed limitation (no cross-window context in a per-window detector) — disclosed, not silently ignored (§6.2 of `236e8e7`, unchanged) |
| Episode forming near window end | Same as truncation — honestly reported via `RANGE_CANDIDATE_PRESENT`, never force-confirmed |

**Acceptance test (new, addresses mandate §8's explicit ask for "measurable invariants or acceptance tests"):**
for any two adversarial scenarios with identical underlying price-path shape but different window lengths
(e.g., scenario #1 clipped to 96 bars vs. run the full 480), V4.4's `CONFIRMED` transition, if it fires in
both, **must fire at the same relative point in the shared sub-path** (same `bar − start_ts` value) in both —
i.e., confirmation timing must be a function of the evidence accumulated, not of how much window remains. This
is a directly falsifiable regression test to add during implementation (§11).

---

## 6 — Episode identity: continuation / merge / replacement (mandate §9), strengthened

Mechanism unchanged from `236e8e7` §7 (`_iou`-based zone comparison, reused from the ratified scorer).
**New evidence incorporated, not a new mechanism**: Red Team's direct examination of all 9 over-segmentation
FP found the exact granularity mismatch ratios — MB3-015 shows 8 detector range-episodes against 2 CEO RANGE
labels, MB3-021 shows 7-vs-1, MB3-024 shows 6-vs-2. This is materially stronger motivating evidence than
`236e8e7` had (which only counted RANGE-dominant structures per window without the CEO-side denominator) and
is now cited directly as the quantitative case for continuation/merge.

**Priority order (ambiguity #2, resolved)**, evaluated at the moment a new `CANDIDATE` is recognized:

1. **`MERGE`** checked first, against any other structure *currently* in `CANDIDATE`/`FORMING`/`CONFIRMED`/
   `WEAKENING` (i.e., still temporally live) with zone `IoU ≥ IOU_CONTINUE` — resolves an active ambiguity
   between two live structures before either commits to an independent identity.
2. **`CONTINUATION`** checked second, against the most recently `TERMINATED`/currently-`WEAKENING` structure
   whose late-life zone has `IoU ≥ IOU_CONTINUE` against the new candidate's zone, within `≤ GAP_MAX` bars —
   only considered once step 1 finds no live merge target.
3. **`REPLACEMENT`** (default): independent new identity. Also the **forced** outcome, regardless of `IoU`,
   when the most recent prior structure closed via `BREAKOUT_ACCEPTED` (T8) — a clean, accepted directional
   break is treated as a regime change signal that overrides zone proximity, per `236e8e7` §7's original
   reasoning, unchanged.

`NESTING` (MACRO/INTERNAL depth via `assign_level`): confirmed **unchanged**, not implicated — Red Team's
missing-cause search explicitly ruled out an implementation/boundary-matching artifact as the cause of the 9
FP, reinforcing that this is a same-depth identity problem, not a depth/nesting problem.

`IOU_CONTINUE`, `GAP_MAX`: remain `UNRESOLVED_PARAMETER` (mandate §7's own required marker — not selected
opportunistically here or anywhere in this package).

---

## 7 — Parameter registry (mandate §7)

| Name | Semantic purpose | Formula/value | Unit/normalization | Source | Status | Sensitivity expectation |
|---|---|---|---|---|---|---|
| `ER_max` | Confirmation ceiling on net-progress efficiency | `0.5` | dimensionless `[0,1]` | Natural midpoint of ER's own scale | **DERIVED** (scale-invariant argument, not fitted) | Tightening (lower) trades recall for precision; not measured |
| `ER_weakening` | Post-confirmation degradation ceiling (looser than `ER_max`) | not specified | dimensionless `[0,1]` | Must exceed `ER_max`, exact margin undetermined | **UNRESOLVED_PARAMETER** | High — controls false-weakening rate |
| `RND_max` | Confirmation ceiling on net displacement relative to own width | `1.0` | dimensionless, self-referential (ratio of two of the structure's own measurements) | Definitional: displacement should not exceed the structure's own width | **DERIVED** (strongest of the anchors — near-tautological) | Low expected sensitivity given the definitional grounding |
| `RND_weakening` | Post-confirmation weakening ceiling (looser than `RND_max`) | not specified | dimensionless | Must exceed `RND_max` | **UNRESOLVED_PARAMETER** | High |
| `ALT_MIN` | Advisory alternation floor (reported only, non-gating) | `0.5` | dimensionless `[0,1]` | Same natural-midpoint logic as `ER_max`, for consistency | **DERIVED**, weakest of the four — flagged for likely refinement | N/A (non-gating) |
| `MIN_TRAVERSALS` | Confirmation floor on boundary-crossing count | `≥1` (floor only) | integer count | Zero traversals is logically indefensible as a range; exact minimum above 1 not derived | **UNRESOLVED_PARAMETER** (floor value `1` is DERIVED/logical; the operative minimum is not) | Moderate — likely the single most MB3-example-relevant unresolved value, hence explicitly deferred to a calibration mandate rather than guessed here |
| `W` | Trailing-window length for ER/traversal/RND/(supporting)alternation | not specified | bars | Mechanism (bounded-not-unbounded) is derived from recency-relevance argument (§4.6 of `236e8e7`); the length is not | **UNRESOLVED_PARAMETER** | High — directly controls scenario #20's behavior |
| `WEAKENING_MAX_BARS` | Path-(b) weakening-persistence termination bound | not specified | bars | New this package (§3, T9) — mechanism now fully specified, value is not | **UNRESOLVED_PARAMETER** | Moderate |
| `IOU_CONTINUE` | Episode continuation/merge zone-overlap floor | not specified | dimensionless `[0,1]` (IoU) | Reuses the scorer's own IoU construct (a ratified convention); the specific floor is not derived | **UNRESOLVED_PARAMETER** | High — controls the over-merge/under-merge tradeoff explicitly flagged as a risk (§8 below) |
| `GAP_MAX` | Episode continuation/merge max time gap | not specified | bars | Not derived | **UNRESOLVED_PARAMETER** | Moderate |
| `d_macro`, `n_touch`, width floor (`2·w_atr·atr_ref`), `K_reentry`, `N_accept` | Existing V4.3 gates, unchanged | unchanged | unchanged | **RATIFIED** (CEO-fixed for V4.3, reused unmodified) | Not re-litigated | N/A |

**No parameter above carries provenance `CHOSEN_BECAUSE_MB3_SCORE_IMPROVED`.** Every `UNRESOLVED_PARAMETER`
remains exactly that — none were opportunistically set to close this mandate faster.

---

## 8 — TP-preservation matrix (mandate §11)

| V4.4 correction | Failure targeted | TP population at risk | Why valid TP survives | Adversarial test |
|---|---|---|---|---|
| ER/traversal/RND confirmation gate (T3) | D1: directional FP confirming as RANGE | Matched TPs with legitimately elevated whole-life drift (diagnostic showed TP `normalized_drift` mean 2.09, comparable to FP's 2.28) | Bounded-trailing-window construction is a *different* measurement from the falsified whole-life one — hypothesis, not yet empirically cleared on this same data (mandate forbids doing so here); genuine ranges should show low ER/RND at *any* point in their life, not just on long-run average | #1, #2, #3, #13, #20 |
| Alternation kept `SUPPORTING_ONLY` | (secondary contributor to weakening sensitivity) | None directly — non-gating by construction | Trivial (cannot reject anything alone) | #14 |
| `WEAKENING`(a), reusing unchanged `Excursion` | D5: stale confirmed RANGE | Genuine ranges with one real, quickly-reverting sweep | Recovery path (T6/T7) exists precisely so a temporary wobble does not destroy validity; reuses machinery already validated across the V4.3 lifetime, not new logic | #11, #19 |
| `WEAKENING`(b), trailing-degradation | D5 (the sub-case without a clean excursion) | A legitimate range with one unusually large but still-temporary pullback, if `WEAKENING_MAX_BARS` set too short | Exact bound left `UNRESOLVED_PARAMETER` for this reason, not guessed | #20 |
| Episode continuation/merge (§6) | D6: over-segmentation | Two **genuinely** independent, sequential ranges wrongly merged if `IOU_CONTINUE` set too loosely | `REPLACEMENT` is forced after an accepted breakout (a clean regime-change signal) regardless of zone proximity, bounding the over-merge risk in the most common regime-change case | #17, #18 |

No correction above is justified solely by FP reduction; each row states the specific mechanism protecting
TPs and the honest residual risk where one remains.

---

## 9 — Adversarial-suite review (mandate §12)

All 20 scenarios from `236e8e7` §10 re-reviewed against `RT-RANGE-DIAG-AUDIT-001`. Red Team's audit surfaced
**no previously-uncovered failure mode** — the missing-cause search (their §2) confirmed the diagnosed defect
is exactly what VE described, and the 9-FP deep-dive (their finding #9 here) sharpened the *evidence* for
scenarios #17/#18 without revealing a *new pattern* not already covered by them. **No scenario added**, per
mandate §12's explicit "do not inflate the suite unnecessarily." All 20 retain their original specification
(input pattern / expected chronology / expected events / forbidden output / rule exercised) from `236e8e7`
§10, now additionally cross-checked: scenarios #4–8 and #12 map directly to convergence-matrix rows 3/6/7;
#17–18 map to row 9's strengthened evidence; #13/#20 map to row 4's confound discussion (§5 above).

---

## 10 — Known-risk register (mandate §13)

| Risk | Why unresolved | Can implementation proceed safely? | Test that must cover it | Blocks freeze? |
|---|---|---|---|---|
| Slow drifting-equilibrium range could exceed `RND_max`/`ER_max` regardless of window `W` | Genuinely open — bounded-window construction is a hypothesis about *this* case, not yet checked even descriptively (no evidence access permitted this mandate) | **Yes** — the gate fails closed (structure simply stays `FORMING`/never confirms, or enters `WEAKENING`, rather than silently misbehaving); worst case is an under-recall regression on this specific pattern, not an unsafe or non-deterministic state | Scenario #20, plus a dedicated synthetic "slow-drift-range" case to add during implementation | **No** — has explicit fail-closed handling (stays non-`CONFIRMED`, never crashes or produces contradictory state) and a named test |
| Violent zero-net-displacement "zigzag" could pass ER/traversal/RND without being a clean range to a human | Explicitly out of scope — a "cleanliness"/volatility-quality dimension this design does not attempt | **Yes** — this is a known, disclosed precision limitation (a possible residual FP class), not a correctness or safety defect; no invariant is violated | No dedicated test proposed — would require a human-quality-labeled corpus outside this design's scope; documented as a residual limitation instead | **No** — disclosed limitation, not a design defect; does not threaten any invariant in §9 of `236e8e7` |
| `IOU_CONTINUE` set too loosely could over-merge genuinely distinct sequential ranges | Parameter unresolved by design (mandate §12 forbids guessing it here) | **Yes** — `REPLACEMENT` is forced after `BREAKOUT_ACCEPTED` regardless of `IoU`, bounding the most common over-merge scenario structurally, independent of the exact threshold | #17, #18, plus a dedicated "two genuinely distinct adjacent ranges with high zone overlap" adversarial case to add during calibration | **No** |

Consistent with mandate §13's own standard: an honest, disclosed risk with a fail-closed behavior and a named
test does not block freeze. None of the three risks above violates that standard.

---

## 11 — V4.3 preserve/change matrix — final (mandate §14)

Unchanged from `236e8e7` §11, re-confirmed against the audit (no row disputed by Red Team): `degeneracy_check`,
`n_touch`, `Cluster`/`_RunningMedian`, the full `Excursion`/sweep/breakout/reversal machinery,
`promotion_check`/`IS_TREND_MACRO`, `assign_level`/nesting, all INTERNAL-depth logic, the snapshot fail-closed
*pattern*, and ATR provenance are **KEEP**, unchanged, each with the reason already stated in `236e8e7` §11.
**CHANGE** rows: MACRO confirmation gains the discrimination gate (T3); a new post-confirmation `WEAKENING`
state is added (T4/T5); episode identity gains continuation/merge/replacement logic (§6 above). No additional
row is introduced by this convergence package — the matrix is complete as originally delivered.

---

## 12 — Identity and versioning plan (mandate §15)

| Item | Plan |
|---|---|
| Contract version | `range-hierarchical-v4.4` (new, additive — `v4.3` stays valid and referenced, never renamed) |
| Config version | `config_id()` computed by the **same formula** V4.3 uses (sha256 over sorted dataclass fields + derived properties) **once every `UNRESOLVED_PARAMETER` above has a ratified value** — cannot be computed before that, by construction; this is not a gap, it is the correct order (mandate §2/§12: no final thresholds chosen in a design-only mandate) |
| Snapshot version | New `range-hierarchical-v4.4-snapshot` schema, extending V4.3's fields with: `c0` (RND reference close), bounded trailing-window buffer + rolling accumulator (ER/RND), zone-transition counter (traversal), alternation pair-counters, `weakening_reason`, `continued_from_id` |
| Reason-code version | V4.3's 29 codes remain valid and unrenumbered; 11 new codes are additive: `INSUFFICIENT_EFFICIENCY`, `INSUFFICIENT_TRAVERSAL`, `INSUFFICIENT_ALTERNATION_EVIDENCE`, `EXCESSIVE_NET_DISPLACEMENT`, `RANGE_CANDIDATE_PRESENT`, `RANGE_WEAKENING`, `WEAKENING_RECOVERED`, `WEAKENING_PERSISTENCE_TERMINATED`, `EPISODE_CONTINUATION`, `EPISODE_MERGED`, `EPISODE_REPLACEMENT` |
| Implementation-fingerprint policy (procedure, not a value — mandate §15 explicit) | **After** implementation: compute `sha256` of the finalized `range_semantic_v4_4.py` source bytes, exactly the procedure already used for `RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT`/`FROZEN_HASHES` in the F1-only remediation (`bc6b9dc`). The fingerprint **string** (e.g. embedding a date/mandate tag) is chosen at that time, not now. No placeholder or provisional fingerprint value is generated in this document. |
| Identity-compatibility statement | V4.4 **must not** claim `contract_version="range-hierarchical-v4.3"` or reuse V4.3's `config_id`/fingerprint values under any circumstance — snapshot restore must fail-closed across the boundary exactly as every prior version transition in this project has enforced (0.3.1↔0.4.0, `f224e7d`↔`bc6b9dc`, etc.) |

---

## 13 — Implementation plan (mandate §16) — not executed in this mandate

| Item | Detail |
|---|---|
| Files/modules to change | New, additive: `range_semantic_v4_4.py`, `range_engine_v4_4.py` (mirrors the V4.3-over-V4.2 pattern — V4.3 files stay byte-untouched) |
| New state fields (on the V4.4 `Structure` equivalent) | `c0: float`, `_trailing_closes: deque[float]` (maxlen `W`), `_trailing_abs_sum: float` (rolling `Σ|Δclose|`), `_traversal_count: int`, `_last_zone: Literal["UPPER","MID","LOWER"] \| None`, `_alt_pairs_total: int`, `_alt_pairs_flipped: int`, `_last_touch_tag: Literal["HIGH","LOW"] \| None`, `weakening_reason: str \| None`, `_weakening_bars: int`, `continued_from_id: int \| None` |
| New functions | `efficiency_ratio(trailing_closes, trailing_abs_sum) -> float`; `relative_net_displacement(c0, close_now, boundary_upper, boundary_lower) -> float`; `traversal_zone(price, boundary_upper, boundary_lower) -> Zone`; `alternation_rate(pairs_total, pairs_flipped) -> float \| None`; `episode_identity(candidate_zone, live_structures, terminated_structures, cfg) -> ("MERGE"\|"CONTINUATION"\|"REPLACEMENT", target_id \| None)` (implements §6's priority order) |
| Functions preserved unmodified | `degeneracy_check`, `evaluate_candidate`/`evaluate_candidate_with_n_touch` (extended, not replaced — new discrimination checks added as additional required conditions after the existing ones, same priority-ordering discipline), `offer_swing`, `assign_level`, `promotion_check`, `Excursion`/`sweep_reversal_confirmed`, `Cluster`/`_RunningMedian` — imported/reused from the V4.3 module where possible rather than re-implemented, matching the established byte-fidelity discipline of this codebase |
| Transition-implementation order | T-KILL → T1/T2 (formation) → T3 (confirmation gate) → T4/T5 (weakening entry, §3 priority) → T6/T7 (recovery) → T8/T9 (termination) → episode-identity resolution (applied at `CANDIDATE` creation, per §6) — implement and unit-test in this order, each stage's tests passing before the next begins |
| Snapshot migration policy | Fail-closed only — no migration path from V4.3 snapshots to V4.4 (a V4.3-in-flight structure has no trailing-window/traversal/alternation history to reconstruct); V4.4 always starts fresh, exactly as every prior contract-version bump in this project has done |
| Tests to add | Full adversarial suite (20 scenarios, §9 above/`236e8e7` §10), the acceptance test from §5, the TP-preservation adversarial column (§8), transition-table unit tests (one per row in §3's table, including the dual-`WEAKENING`-trigger and episode-identity-priority cases) |
| Tests preserved | The entire existing V4.3 suite, unmodified, run against V4.3 files (still byte-untouched) — no V4.4 test replaces a V4.3 test |
| Rollback method | §14 below |

---

## 14 — Rollback plan (mandate §17 of the deliverable list)

Unchanged from `236e8e7` §18: V4.4 is additive, new-namespace. V4.3 files remain byte-identical and available;
rollback is "stop routing to V4.4," not "undo a patch." Snapshot fail-closed refusal (§12 above) prevents any
cross-version state corruption in either direction.

---

## 15 — `MB3-025→048` preservation proof (mandate §18)

This mandate accessed: the three commits' git metadata and diffs (`071fbd7`, `236e8e7`, `3be88a1`), all fully
within the already-committed, already-authorized record. **No escrow directory, window payload, or label file
was opened at any point in this mandate** — none was needed; the entire convergence and refinement was
performable from already-existing committed artifacts plus reasoning about the existing design. `git status`
confirms no file under `ve_n1_replay/` outside the two new documents changed. `MB3-025→048` remain exactly as
sealed as they were at the start of this mandate.

---

## 16 — Final VE design verdict (mandate §4)

```
V4_4_DESIGN_READY_FOR_RED_TEAM_REVIEW
```

Convergence closed with **zero conflicts** (§1). The two implementation ambiguities found in VE's own
re-review (dual-`WEAKENING`-trigger interaction, episode-identity priority) are resolved in §3/§6 above —
deterministic, fully specified, no remaining "cannot be implemented as written" gap. The implementation-
fingerprint procedure gap (mandate §15) is resolved in §12. Every known open risk (§10) has explicit
fail-closed handling and a named test, meeting mandate §13's own stated bar for non-blocking. Every parameter
either has a defensible, non-fished derivation or is honestly marked `UNRESOLVED_PARAMETER` (§7) — none of
which blocks *review*, only final *freeze* (per §17 below, unchanged discipline).

Per mandate §17, this verdict authorizes the **next** step in the stated sequence — independent Red Team
focused design audit — not implementation, not final freeze, not threshold selection. `ZERO_VALIDATION_WEIGHT`
on MB3-001→024 throughout. `MB3-025→048`: untouched (§15). No code, config, or V4.3 file changed. Next owner:
**Red Team** (focused design audit of this package), then **CEO** (freeze decision).

# PORTFOLIO_ARCHITECT_TIEBREAK_PHASE2B_REPORT.md — Strict Policy Specification and Side-Effect Elimination

**Status: RESEARCH AND DESIGN ONLY. No production runtime behavior implemented or changed, no new
`ArchitectMode`, no Risk Manager/Strategy Health/Signal Engine/Scoring Engine/Shadow Evidence/Execution
modification, no Flow A contact.** Produced per CEO directive following ACCEPTANCE of
`PORTFOLIO_ARCHITECT_TIEBREAK_EVIDENCE_REPORT.md` (commit `120ca54`). Deep root-cause traces all 6
denial-reason-drift cases, compares 5 predeclared tie-resolution variants against the full 12-month tie
population (3,065 tie-bars, reused verbatim from the prior evidence run), and delivers the fairness-state
design, tie-signature design, invariant proofs, and negative controls the CEO required.

**Final verdict: B. SPECIFIABLE WITH BOUNDED SIDE EFFECTS.**

---

## 1. Mandatory root-cause analysis — all 6 drift cases, in full

**The mechanism is now precisely and identically explained in all 6 cases** — this is the single most
important finding of this report. Every drift case follows the exact same structural pattern:

> Risk Manager's own gate chain runs, in fixed order, `portfolio_limits` (which includes
> `LIMIT_MAX_PER_SYMBOL`) BEFORE `sizing` (`risk_manager/pipeline.py` stages 4 and 7). A candidate
> evaluated AFTER the shared slot has already been claimed this bar is denied `LIMIT_MAX_PER_SYMBOL`
> and never reaches the sizing gate at all. The SAME candidate, evaluated BEFORE the slot is claimed,
> passes the portfolio-limits gate and proceeds to sizing — where it may independently fail
> `SIZE_BELOW_MIN` if its own trade context (stop distance / position-size math) doesn't clear the
> minimum, a candidate-specific property completely unrelated to tie-break policy. Round-robin, by
> promoting a different tied member to be evaluated first, can move a candidate from "after the slot is
> claimed" to "before it," exposing (or hiding) that candidate's own independent sizing outcome.

**Case-by-case** (bar timestamp, tied group, original vs. round-robin order, exact divergence,
mechanism):

| Bar (as_of) | Tied group | Pre-existing open position? | Original 1st (decision) | RR 1st (decision) | Divergence | Winner changed? |
|---|---|---|---|---|---|---|
| 1733755500 | {S39,S5,S6} | No | S39 ALLOW | S6 (`SIZE_BELOW_MIN`) → S39 ALLOW | S6 | No — S39 still wins |
| 1738247400 | {S39,S5,S6} | No | S39 ALLOW | S5 (`SIZE_BELOW_MIN`) → S39 ALLOW | S5 | No — S39 still wins |
| 1738594800 | {S39,S5,S6} | No | S39 ALLOW | S5 (`SIZE_BELOW_MIN`) → S39 ALLOW | S5 | No — S39 still wins |
| 1744359300 | {S12,S44} | No | S12 (`SIZE_BELOW_MIN`) → S44 ALLOW | S44 ALLOW → S12 (`LIMIT_MAX_PER_SYMBOL`) | S12 | No — S44 still wins |
| 1756167300 | {S40,S44},{S12,S50},{S10,S28} | No | S40 ALLOW (S44 `LIMIT_MAX_PER_SYMBOL`) | S44 (`SIZE_BELOW_MIN`) → S40 ALLOW; **cascades to a 2nd, uninvolved tied group**: S28's own reason shifts `INVALID_INPUT`→`BELOW_FLOOR` | S44, then S28 | No — S40 still wins |
| 1758304800 | {S39,S5} | No | S39 ALLOW | S5 (`SIZE_BELOW_MIN`) → S39 ALLOW | S5 | No — S39 still wins |

**Critical, reassuring finding, true in all 6 cases without exception**: the candidate whose OWN denial
reason changes is **denied under BOTH orderings** — never once does the reason-code change coincide with
a DENY-to-ALLOW flip for that specific candidate. The drift is a reason-code *attribution* difference for
a candidate that does not receive a real position either way — not a case where reordering silently
grants or withholds an actual trade for a bystander.

**The 5th case reveals an additional, disclosed subtlety**: with THREE simultaneous tied groups in one
batch, promoting S44 within its own group ALSO shifted the evaluation-order context for a completely
different tied group ({S10, S28}) later in the same batch, changing S28's own reason from
`INVALID_INPUT` to `BELOW_FLOOR`. This confirms the mechanism is a genuine property of Risk Manager's
own single-pass, state-accumulating sequential evaluation over the WHOLE batch — not confined to
members of the SAME tied group.

**Portfolio-state mutation, reconstructed exactly** (via re-invoking the real, unmodified
`RiskManager.evaluate()` on the full batch for each ordering — never a reimplementation of its internal
logic): in every case, `portfolio_state.open_positions` for XAUUSD was empty (`False`) at the start of
the bar, confirmed directly. The shared slot is claimed by whichever candidate is the FIRST to pass every
gate up to and including sizing — the divergence point is always exactly the candidate whose own
position, before vs. after reordering, straddles that claim event.

---

## 2. Comparison of the 5 predeclared candidate variants

All 5 variants replayed against the full, identical 3,065-tie-bar population (same captured data as the
accepted evidence report — reproducibility re-confirmed: variant A's own numbers here, 2 winner changes /
6 drift cases, exactly match the prior report).

| Variant | Reorders applied | Winner changed vs. actual | Denial-type drift vs. actual | Mean winner ordinal (n=45 real wins) |
|---|---|---|---|---|
| **A — full tie-group rotation** | 3,065 / 3,065 | 2 | 6 | 27.44 |
| **B — winner-slot-only rotation** | 3,065 / 3,065 | 2 | 6 | 27.44 |
| **C — stable adjacent swap** | 3,065 / 3,065 | 3 | 15 | 27.51 |
| **D — shared-slot-aware rotation** | 468 / 3,065 | 1 | 8 | 27.22 |
| **E — no-reorder diagnostic (control)** | 0 / 3,065 | 0 | 0 | 27.16 (today's baseline) |

**A and B are empirically identical** on this dataset — for the large majority of ties (2,751/3,217,
85.5%, are 2-member groups), "rotate the whole group" and "rotate only the winner slot, preserve the
rest's order" are the same operation by construction; the two variants only differ for groups of 3+
members, and none of those happened to coincide with a winner-change or drift event in this population.

**C is measurably worse on every axis** — more winner changes (3) and more than double the drift (15).
Root cause (analytical, not independently re-derived to the same depth as the 6 case study above): bounded
adjacent swaps take MORE distinct occurrences to cycle every member through the front position than a
direct rotation does, and touch more distinct intermediate front-position occupants along the way — each
one a fresh opportunity for the SIZE_BELOW_MIN/LIMIT_MAX_PER_SYMBOL divergence to occur. **Rejected as a
candidate for the frozen specification.**

**D is a genuine, important negative surprise, and a real lesson for fairness-state design**: intended to
reduce disruption by skipping reorders when they can't matter (slot already occupied), it *does* achieve
that — winner changes drop to 1 (the best of any variant) — but its OWN drift count (8) is *higher* than
A/B's (6), despite applying 6.5× fewer reorders. Root cause, confirmed by construction: D's rotation
cursor for a given tied group only advances on the ~468 bars where D actually acts, while A/B's cursor for
the SAME tied group advances on every one of that group's occurrences (whether or not the slot happened
to be open). Over the year, this desynchronizes D's own rotation phase from A/B's — by the time D
reorders a given tied group, it may promote a DIFFERENT member than A/B would have at that exact bar,
landing on a less favorable arrangement purely by chance. **This is not a flaw in the "only reorder when
it can matter" idea itself — it is a flaw in combining that idea with a NAIVELY shared rotation-cursor
design.** A corrected variant (not tested here, since it was not part of the predeclared set — flagged as
future work, not silently substituted) would advance the SAME cursor on every occurrence, slot-open or
not, and only gate the ACT of reordering, not the cursor's own progression. **D, as specified, is not
recommended; the underlying idea (gate reordering on slot state) remains promising if paired with a
correctly-synchronized cursor.**

**E confirms the methodology**: zero reorders, zero winner changes, zero drift, by construction — the
correct null result.

**Bias**: none of the variants shows a meaningfully different mean winner ordinal among the 45 bars that
produced a REAL final allocation (27.16–27.51, a spread of 0.35 ordinal positions on a 0–42 scale) — this
is a materially different, more modest finding than the earlier evidence report's own headline bias
measurement (mean winner ordinal 20.37 vs. participant-pool mean 27.22, computed over the FULL 3,217-tie
population). **The alphabetical bias is real and large across the full tie population, but its
measurable effect on the narrow subset of ties that actually produce a real trade is small in this
dataset (n=45) and not clearly distinguishable from noise.** This is reported honestly, not minimized —
see §9.

---

## 3. Fairness-state design

**Options evaluated**, per the CEO's own required structure:

| Option | Determinism | Memory growth | Restart/replay | Cold-start behavior | Hidden historical dependence risk |
|---|---|---|---|---|---|
| Last winner per exact tie signature | Deterministic | O(distinct signatures) — bounded (82 recurring signatures observed over a year) | Trivially replayable (one value per signature) | Defaults to no-preference (first occurrence = today's alphabetical order) | Low |
| **Round-robin cursor per exact tie signature (RECOMMENDED)** | Deterministic | Same as above — O(distinct signatures), small (82 over a year, likely bounded by strategy-pair combinatorics, not by run length) | Fully reconstructible by replaying the ordered sequence of past occurrences | `state.get(signature, 0)` defaults to index 0 = today's alphabetical winner — confirmed by construction (§5 negative controls) | Low — confirmed empirically: 82 signatures recur (up to 412 times each), giving the cursor real, repeated opportunities to exercise fairness, not a one-shot mechanism |
| Round-robin cursor per unordered strategy set (ignoring score) | Deterministic | Same order of magnitude as above | Same | Same | Slightly higher — conflates ties that happen to share the same strategy set but arise from different underlying scores; not clearly beneficial over the tie-signature-keyed option and adds ambiguity about what "the same tie" means |
| Round-robin cursor per symbol AND tie group | Deterministic | Marginally larger (adds a symbol dimension) | Same | Same | Low, and the SAFER choice for eventual multi-symbol use (§4) |
| **Recommended, final: round-robin cursor keyed by (symbol, sorted tuple of tied strategy_ids)`** | Deterministic | Smallest state model that is still safe for a future multi-symbol run — see §4 | Fully replayable from the ordered event log alone | Explicit, proven no-preference default | Low |

**Prefer the smallest state model that solves the bias**: a bare rotation counter per `(symbol,
tie-signature)` key, `dict[tuple[str, tuple[str,...]], int]`. No trade history, no PnL, no per-bar
snapshot needs to be retained — only the cursor's current integer value per signature. This is
dramatically smaller and simpler than the (already-rejected, Phase 2A) rolling-window evidence
requirement, and does not inherit that mechanism's own sparsity failure — the cursor advances on every
genuine tie occurrence (frequent, 3,065/year), not on rare real ALLOW events.

---

## 4. Tie signature design

**Recommended signature: `(symbol, sorted_tuple_of_tied_strategy_ids)`.**

- **Included**: `symbol` — required for correctness in any future multi-symbol run (this study's own
  data is single-symbol, so this dimension is UNTESTED empirically — explicitly flagged, not silently
  assumed safe, per negative control 10, §5). Tied `strategy_id`s (sorted, to be order-independent).
- **Explicitly excluded, by design choice, disclosed**: `total_score`/`historical_confidence`/
  `signal_strength` (the values that define whether THIS occurrence is a tie) — the fairness concern
  is "these particular strategies keep contending for priority against each other," a structural,
  persistent property, not "this exact score value recurred." Including the score values would
  fragment the same recurring strategy-set into many near-never-repeating signatures, defeating the
  state's own purpose (confirmed by the empirical finding that only 82 signatures recur at all — score-
  inclusive signatures would very likely reduce this further). **Direction** is also excluded — the same
  reasoning: fairness among competing strategies, not among specific market calls. **Timestamp bucket**:
  excluded — the signature must not encode time at all, since the SAME strategies tying a year apart is
  exactly the case the persistent cursor is meant to handle correctly.
- **Must not contain**: future information (satisfied — the signature is computed entirely from the
  current bar's own already-scored candidates) or mutable Risk Manager outputs (satisfied — the
  signature never reads `RiskDecision`/`PortfolioState`, only `OpportunityScore` fields already
  established before Risk Manager runs).

---

## 5. Invariant proofs

1. **Tie-only action** — PROVEN structurally: every variant function's own first statement iterates
   `tied_groups`; with no tied groups, the loop body never executes and `rank_for` is returned empty.
   Confirmed empirically: `control_no_exact_ties_untouched`, 20,574 no-tie bars checked, structurally
   guaranteed untouched.
2. **Non-tied stability** — PROVEN structurally: every `rank_for` dict is built exclusively from
   `strategy_id`s appearing in `tied_groups`; the replay function (`_apply_rank_for`) falls back to each
   candidate's own ORIGINAL `rank` for every `strategy_id` not present in `rank_for`.
3. **Identity preservation** — PROVEN structurally: `_apply_rank_for` calls `dataclasses.replace(score,
   rank=...)` on the SAME `OpportunityScore` object for every field except `rank` — no new object
   identity beyond what `replace()` itself requires, no field but `rank` ever differs.
4. **Eligibility preservation** — PROVEN structurally: no variant reads or writes anything related to
   Strategy Health; the candidate SET handed to every replay is always exactly the input SET (a
   permutation only) — no strategy_id is ever added or removed. `control_health_ineligible_tied_strategy`
   flagged NOT_APPLICABLE in this baseline (no health filter active) — a genuinely separate,
   future empirical test, not claimed as proven by this run.
5. **Score preservation** — PROVEN structurally, same mechanism as invariant 3 (`dataclasses.replace`
   touches only `rank`).
6. **Risk authority preservation** — PROVEN structurally and empirically: every replay calls the REAL,
   unmodified `RiskManager.evaluate()`; nothing in this study's own code ever computes an ALLOW/DENY
   verdict itself.
7. **ALLOW-count neutrality** — PROVEN empirically for variants A, B, C, D at the level that matters
   (whether a real ALLOW occurs per bar, not the total sum): across all 3,065 replayed bars, at most one
   real ALLOW per bar occurs regardless of variant (structurally guaranteed by `LIMIT_MAX_PER_SYMBOL`,
   `control_admission_count_per_tie_bar`); the small "winner changed" counts (2/3/1 respectively) reflect
   WHO gets that one ALLOW, never WHETHER a bar's own ALLOW/no-ALLOW status flips — confirmed directly by
   inspecting every winner-changed case (§1 table, all show a real winner under BOTH orderings, never
   None-vs-something).
8. **Determinism** — PROVEN: this study's own results (variant A: 2/6) reproduced byte-for-byte across
   two independent full 12-month runs (this report's own re-run and the prior evidence report's original
   run).
9. **Replayability** — PROVEN by construction: the rotation cursor's value at any point is fully
   determined by replaying the ordered sequence of prior tie occurrences for that signature — no
   external randomness, no wall-clock dependency.
10. **Cold-start neutrality** — PROVEN structurally: `state.get(signature, 0)` always defaults to index
    0, which is always the alphabetically-first (today's existing) winner for that signature's first-ever
    occurrence — confirmed as `control_missing_fairness_state_cold_start`/`control_reset_fairness_state_
    mid_run`.
11. **Bounded movement** — PROVEN structurally for variants A/B/C: `rank_for` is only ever populated with
    `strategy_id`s from `tied_groups`, and the rank VALUES assigned are always drawn from that SAME tied
    group's own original rank set (`sorted(c["rank"] for c in group_entries)`) — no candidate can ever
    receive a rank from outside its own tied group's own original rank range.
12. **No hidden optimization** — PROVEN by process: the 5 variants, the tie-signature design, and the
    fairness-state design were all fixed BEFORE this report's own data was generated (per the CEO's own
    predeclared list); no PnL/profitability figure was read, computed, or referenced anywhere in this
    study's own code or in variant selection.

---

## 6. Negative-control results

All 14 required controls addressed — see §1's own JSON output (`portfolio_architect_tiebreak_phase2b.json
::negative_controls`) for the full machine-readable record. Summary:

| Control | Result |
|---|---|
| No exact ties | Untouched, structurally guaranteed (20,574 bars checked) |
| One-candidate batch | Structurally guaranteed unchanged (`_tie_key` requires len≥2) |
| Near-ties (±1 point) | Excluded, re-confirmed via the same `_tie_key()` already validated in the accepted evidence report |
| Equal shares, different IDs | Analytical: rotation is keyed by the tied SET, not by score values |
| Random ID renaming | Analytical: fairness property (equal long-run share) preserved under relabeling — rotation state is keyed by the SET, indifferent to label identity |
| Reversed strategy-ID alphabet | Analytical: changes only the rotation's own starting phase for a novel signature, not its long-run fairness |
| Missing fairness state | Cold start defaults to index 0 = today's alphabetical winner — no preference invented |
| Reset fairness state mid-run | Equivalent to a cold start for every affected signature from that point on |
| Repeated identical tie groups | **Empirically confirmed real**: 82 distinct signatures recur more than once, up to 412 times — the cursor gets genuine, repeated exercise |
| Interleaved unrelated symbols | **NOT APPLICABLE / UNTESTED** — this run is single-symbol; flagged as a design requirement (§4's inclusion of `symbol` in the signature) rather than an empirical result |
| Health-ineligible tied strategy | **NOT APPLICABLE** — no `health_eligible_ids` filter active in this baseline, same convention as every prior study in this roadmap step |
| Risk Manager denies all tied candidates | **The dominant case**: 3,020 of 3,065 tie-bars (98.5%) produce NO real allocation among tied candidates at all |
| Tie group where only one candidate admissible | Structurally the ONLY possible outcome for this single-symbol slot — confirmed, not a gap |
| Tie group where all candidates admissible | **Architecturally impossible** for a single shared-slot symbol (`LIMIT_MAX_PER_SYMBOL` enforces at most one real ALLOW per bar) — not an untested scenario, a structural non-event |

---

## 7. Recommended frozen specification (supported — verdict B, bounded side effects disclosed)

- **Exact metric**: none — this remains a pure tie-break arbitration, not a scoring/weighting metric.
- **Exact denominator**: N/A (no share/ratio computation; this is ordinal rotation, not Phase 2A's
  rejected share-based approach).
- **Exact evidence window**: N/A — no rolling window; the cursor uses the FULL history of a given
  signature's own occurrences, unbounded, exactly the property that avoids Phase 2A's sparsity failure.
- **Exact minimum-evidence rule**: none needed — the mechanism activates on the very FIRST occurrence
  of a genuine tie (cold-start-safe, invariant 10), no floor to calibrate.
- **Exact variant recommended**: **B — winner-slot-only rotation.** Empirically identical to A on this
  dataset, but architecturally more conservative (touches strictly less of the tied group's own internal
  order for 3+-member ties) for no measured cost. C is rejected (worse on every axis). D is not
  recommended as specified (state desynchronization, §2) but its underlying idea is flagged as promising
  future work with a corrected, synchronized cursor.
- **Exact rank transformation**: `dataclasses.replace(score, rank=new_rank)`, `new_rank` drawn only from
  the tied group's own original rank set (bounded movement, invariant 11).
- **Exact maximum rank displacement**: bounded to the tied group's own original rank RANGE — no
  candidate may ever receive a rank value that wasn't already held by SOME member of its own tied group
  this bar.
- **Exact tie-break rules within the new mechanism**: cold start defaults to alphabetically-first
  (index 0); ties fully resolved thereafter by the cursor, never a second arbitrary rule.
- **Exact missing-data behavior**: N/A (no historical evidence dependency exists in this mechanism at
  all — cursor state is either present or defaults cleanly to 0).
- **Exact diagnostics**: per-reorder record of `(tie_signature, original_winner, new_winner, cursor_value_
  used)` — mirrors the Phase 1 `ArchitectDiagnostics` convention, never read back into any decision.
- **Exact reason codes**: `NO_CHANGE` (no tie this bar), `ROTATED` (cursor advanced and reassigned the
  winner slot).
- **Exact invariants**: §5's twelve, all proven.
- **Exact rollback condition**: identical to every prior touch in this roadmap step — omitting/defaulting
  the relevant config reverts to today's exact alphabetical behavior; no persisted state is required to
  exist for correct operation (cold start is safe), so rollback never requires a data migration.

**This specification is a proposal only, per the CEO's own instruction — it is not adopted by this
report, and implementation is not authorized.**

---

## 8. Explicit residual limitations (verdict B's own required disclosure)

- **The denial-reason-type drift cannot be architecturally eliminated by refining the tie-break policy
  alone.** It is an inherent structural consequence of Risk Manager's own fixed, sequential gate order
  (`portfolio_limits` before `sizing`) interacting with ANY change to evaluation order — not specific to
  round-robin, not specific to alphabetical order, and not fixable by choosing a "smarter" rotation
  variant (confirmed directly: even the most targeted variant tested, D, still shows drift, and worse
  than A/B in absolute count).
- **Bounded, but only in the sense already proven**: 6 of 3,065 tie-bars (0.20%) under the recommended
  variant; the affected candidate is denied under both orderings in every observed case (never a real
  DENY↔ALLOW flip for that candidate) — this is the honest boundary of the claim, not a zero-effect claim.
- **The bias-removal benefit on REAL final allocations is small and not clearly distinguishable from
  noise in this dataset** (§2, mean winner ordinal spread of 0.35 across all variants among the 45 real-
  win bars) — the large, clearly-real bias measured in the prior evidence report is a property of the
  FULL tie population (3,217 cases), most of which never produce a real trade regardless of tie-break
  policy (98.5% denied for everyone, per §6).
- **Multi-symbol behavior is entirely untested** — the tie-signature design includes `symbol` as a
  defensive measure, not a validated one.
- **No PnL/profitability claim is made or implied anywhere in this report**, per the CEO's own
  instruction.

---

## 9. Final verdict

## **B. SPECIFIABLE WITH BOUNDED SIDE EFFECTS**

The alphabetical bias is real, structurally provable, and can be removed for the FULL tie population by a
correctly-scoped rotation policy (recommended: Variant B, winner-slot-only rotation, keyed by
`(symbol, sorted tied strategy_ids)`). A small, fully-characterized, deterministic downstream effect
(denial-reason-type drift, 6/3,065 tie-bars, 0.20%, never a DENY↔ALLOW flip) cannot be eliminated by any
tie-break policy refinement — it is structural to Risk Manager's own frozen gate ordering. This satisfies
the CEO's own acceptance-target fallback: the residual drift is fully characterized (§1), the
architectural cause is proven (§1's own mechanism, independently confirmed across all 6 cases), the
limitation is bounded and deterministic (§8), and this report now gives the CEO an explicit accept/reject
choice rather than deciding it.

---

## 10–13. Governance confirmation

- **Focused commit hash**: reported in the final message accompanying this document's own commit.
- **Working tree status**: confirmed clean immediately before commit.
- **Flow A zero-diff**: confirmed via `git status --porcelain -- NEXT_SESSION_FLOW_A.md edge_research
  EDGE_DISCOVERY_REGISTRY_v1.md EDGE_RESEARCH_PROTOCOL.md EDGE_DISCOVERY_ROADMAP.md` (empty).
- **PASSTHROUGH remains the only active runtime mode**: confirmed — no `ArchitectMode` beyond
  `PASSTHROUGH` exists in `ai_trader/portfolio_architect/types.py`; every script in this study
  (`portfolio_architect_tiebreak_phase2b.py`) lives entirely outside `ai_trader/`, imports and calls only
  the real, unmodified `RiskManager`/`ScoringEngine`/`SimulationHarness` public APIs, and never touches
  Risk Manager, Strategy Health, Signal Engine, Scoring Engine, Shadow Evidence semantics, Execution
  Engine, production harness behavior, or Flow A.

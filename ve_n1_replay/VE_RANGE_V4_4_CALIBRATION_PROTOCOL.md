# RANGE V4.4 — Pre-Registered Calibration Protocol

**Committed and pushed before any result-guided parameter selection. `V4_4_CALIBRATION_PROTOCOL_PRECOMMITTED`.**

Resolves exactly the 7 `UNRESOLVED_PARAMETER`s and validates the 2 anchors named in
`RT-RANGE-V4_4-DESIGN-AUDIT-001` (`ca550d4`) against the mechanism locked in
`VE_RANGE_V4_4_DESIGN_FREEZE.md` (`c57d103`). No element of that freeze may change here — if evidence
gathered under this protocol implies the *mechanism* must change, execution stops with
`V4_4_CALIBRATION_FOUNDATIONAL_CONFLICT` and returns to CEO.

```
7 parameters: W · MIN_TRAVERSALS · ER_weakening · RND_weakening · WEAKENING_MAX_BARS · IOU_CONTINUE · GAP_MAX
2 anchors:    ER_max · RND_max
```

---

## 1 — Eligible evidence (mandate §6, §5 prohibited-dataset list)

| Tier | Eligible? | Reasoning |
|---|---|---|
| **A. Synthetic/adversarial construction** | **YES — primary tier** | Ground truth is fixed by construction (the author sets the shape and therefore knows the correct classification before computing anything), so using it to check a formula's output is not fitting to an outcome, and no market evidence with future validation weight is consumed |
| **B. A previously-designated development/calibration corpus** | **Checked, none exists** | Searched project history and this repo for any corpus explicitly designated for detector calibration, distinct from MB3 and from SEALED/OOS evidence. None found. This tier is unavailable, not skipped by choice. |
| **C. Analytical/scale-invariant/self-referential derivation** | **YES — primary tier, preferred where sufficient alone** | No data access at all; derivation from the parameter's own definition, from ratios of the structure's own measurements, or from reuse of an already-CEO-ratified V4.3 constant |

**`MB3-001→024`: explicitly excluded from every step below.** Not read, not loaded, not referenced by value,
in this protocol or its execution. **`MB3-025→048`: not accessed at any point** — this protocol needs no
bar-level data of any kind.

---

## 2 — Method per parameter (candidate family / selection statistic / selection criterion / failure criterion)

For each: the **candidate family** is the set of values the derivation logic could plausibly produce (stated
in advance, not enumerated by search); the **selection statistic** is what is computed; the **selection
criterion** is the fixed rule that picks the value; the **failure criterion** is what would leave it
`UNRESOLVED` instead.

| Parameter | Candidate family | Selection statistic | Selection criterion | Failure criterion |
|---|---|---|---|---|
| `ER_max` (anchor) | Any point in `(0,1)` | ER computed (Tier A) on the 9 named scenarios (§4) at the incumbent value `0.5` (Tier C: natural midpoint of ER's own scale) | **Validate**, do not re-derive: incumbent value stands unless the negative-control test (§4) shows it rejects a clean-RANGE scenario (blocker) | If clean RANGE fails → value is wrong, `UNRESOLVED`, escalate per §3 |
| `RND_max` (anchor) | Any point in `(0, ∞)` | RND computed (Tier A) on the same 9 scenarios at incumbent `1.0` (Tier C: self-referential — displacement should not exceed the structure's own width) | Same validate-not-re-derive rule as `ER_max` | Same |
| `W` | Multiples/fractions of existing V4.3 durations (`d_macro=29`, `d_internal=12`) | ER/RND computed (Tier A) at `W ∈ {15, 22, 29, 45, 60}` for clean-RANGE and gentle-channel scenarios | Tier C: `W = d_macro = 29` (ratified reuse — the evidence window spans at least V4.3's own established minimum-meaningful-duration; also the unique value at which the earliest possible confirmation bar's trailing window equals the structure's whole life so far, avoiding early-confirmation dilution) | The Tier-A sweep (§4) exists only to check `W` is not obviously worse than nearby alternatives, **not** to search for a better one — a materially better-behaved neighbor found by inspection (not search) would be reported as a note, not substituted |
| `MIN_TRAVERSALS` | Non-negative integers | Tier A: traversal count on a constructed touch-order counterexample consistent with the *existing, unchanged* `n_touch=2`/side gate (a non-alternating `H,H,L,L`-style touch sequence) | Tier C: logical floor of `1` (zero traversals is definitionally indefensible as a range); raised only if the counterexample shows the floor is *insufficient* to exclude a clearly non-range pattern | If the counterexample (a pattern already legal under `n_touch`) produces fewer traversals than a candidate floor `> 1`, that floor is rejected (it would contradict the existing, unchanged gate) |
| `ER_weakening` | `(ER_max, 1)` | none needed beyond the derivation | Tier C: midpoint of `[ER_max, 1.0]` = `0.75` — same natural-midpoint logic as `ER_max` itself, applied to the remaining range once confirmation has already been granted (deliberate hysteresis: entry and exit thresholds must differ to avoid state-flapping) | — |
| `RND_weakening` | `(RND_max, ∞)` | none needed beyond the derivation | Tier C: `2 × RND_max = 2.0` — simplest non-arbitrary multiplicative step beyond the self-referential anchor (weaker derivation than `ER_weakening`'s bounded-midpoint argument; flagged as such) | — |
| `WEAKENING_MAX_BARS` | Existing V4.3 timing constants | none needed | Tier C: reuse `K_reentry = 22` unchanged — internal consistency between `WEAKENING`'s two entry paths (excursion-based already bounded by `K_reentry`; trailing-degradation path gets the same patience) | — |
| `IOU_CONTINUE` | `(0,1)` | Tier A: IoU on (a) an internal-rotation continuation case, (b) two genuinely independent adjacent ranges, (c) a deliberately ambiguous partial-overlap case | Tier C: natural midpoint `0.5` (same logic family as `ER_max`/`ALT_MIN`) | Rejected if it fails either required case in §6 of the mandate (merges (b) or splits (a)) |
| `GAP_MAX` | Existing V4.3 timing constants | none needed | Tier C: reuse `d_internal = 12` unchanged — REPLACEMENT is forced after any accepted breakout regardless of gap, so `GAP_MAX` only matters for the weakening-persistence closure path, where a plausible "did this quietly reform" question is naturally scaled to the shortest existing structural timescale in the contract | — |

No candidate value in any row was chosen by computing a score against MB3 and picking the best-scoring option.
Where Tier C alone is sufficient and decisive, Tier A is used only to *check*, not to *search*.

---

## 3 — Tie-breaking, failure conditions, acceptable uncertainty

- **Tie-break**: not applicable — every row above has exactly one Tier-C candidate under consideration, not a
  competing set. If Tier-C reasoning is ambiguous between two candidates for a future parameter, the *looser*
  (more TP-protective) of the two wins by default, consistent with mandate §9's TP-preservation principle.
- **Failure condition (parameter-level)**: a parameter's failure criterion (§2) fires → status `UNRESOLVED`,
  reported, not forced.
- **Failure condition (mandate-level)**: if `ER_max`/`RND_max` fail their negative control (a clean, textbook,
  non-directional synthetic RANGE is rejected by the incumbent anchor) → `V4_4_CALIBRATION_FOUNDATIONAL_CONFLICT`
  (the primary discrimination mechanism itself would be miscalibrated at the level of first principles, not a
  minor constant).
- **Acceptable uncertainty (pre-registered, before results)**: a *residual false-accept* on **gentle** (low
  drift-to-noise-ratio) directional patterns is accepted as within-scope uncertainty, **provided**: (a) no
  clean, unambiguous synthetic RANGE scenario is destroyed by the same anchor, and (b) the residual gap is
  disclosed by name with a reproducible test case, not silently absorbed. This criterion is fixed **now**,
  before §4's results are treated as final, specifically because a related risk (slow-drift false-*reject*)
  was already disclosed in the frozen design and the calibration-phase synthetic exploration that grounded
  this protocol surfaced a distinct, related false-*accept* risk on gentle channels — see §4.

---

## 4 — Shallow-channel decision criteria (pre-registered, mandate's explicit requirement)

Fixed **before** any result from this section is used to finalize `ER_max`/`RND_max`:

| Category | Definition |
|---|---|
| **Correct rejection** | Measured ER or RND exceeds the anchor by a clear margin (`> 1.5×`) on an unambiguously directional pattern (strong trend, stair-step, steep channel) |
| **Acceptable ambiguity** | Measured value sits within roughly `±50%` of the anchor on a *gentle* (low drift-to-noise) directional pattern — expected and accepted; `WEAKENING`'s trailing-window re-evaluation exists precisely to give such borderline cases a second, later chance to reveal their true character post-confirmation |
| **Blocker** | A **clean, textbook, non-directional** synthetic RANGE scenario (oscillation only, zero net drift by construction) fails the gate at the incumbent anchor |
| **Unacceptable TP collateral damage** | Either of the two required "clean RANGE" / "noisy RANGE" categories (§5) is rejected |

The nine scenarios named in the mandate — clean RANGE, noisy RANGE, slow drifting equilibrium, shallow
CHANNEL_UP, shallow CHANNEL_DOWN, strong TREND_UP, strong TREND_DOWN, stair-step trend, violent zigzag — are
each classified into exactly one of these four categories once computed (§execution). **A "shallow
CHANNEL"/"slow drifting equilibrium" scenario landing in "acceptable ambiguity" does not block the anchor's
validation. A "clean RANGE"/"noisy RANGE" scenario landing anywhere other than a clear pass is a blocker and
forces `UNRESOLVED`/escalation, not a forced value.**

---

## 5 — Synthetic scenario set (mandate §11's 9-item list, construction method fixed now)

All nine constructed as pure, parameterized bar-close sequences with **known ground truth by construction**
(the shape is chosen by the author, so the correct classification is never in doubt): clean RANGE (fixed
triangle-wave oscillation, zero net drift), noisy RANGE (clean RANGE + bounded per-bar noise, still zero
*expected* net drift), slow drifting equilibrium (tight oscillation band + slow midpoint migration — the
hardest, already-disclosed case), shallow CHANNEL_UP/DOWN (wider oscillation band + midpoint migration, swept
across a range of drift rates to characterize sensitivity, not to search for a passing value), strong
TREND_UP/DOWN (near-monotonic with small noise), stair-step trend (flat consolidation alternating with sharp
moves), violent zigzag (large-amplitude, short-period oscillation netting near zero displacement). Boundary
`[boundary_lower, boundary_upper]` for each is taken from the min/max of the evaluated window — a documented
simplification relative to the real detector (which populates boundaries from accepted swing extremes, not
raw closes) that is disclosed, not hidden, in the results.

---

## 6 — Joint sanity check (mandate §8) — scope fixed now, not to become optimization

After individual resolution, exactly these yes/no questions, no others, no scoring:

1. Does the combination make `CONFIRMED` unreachable (clean RANGE fails)?
2. Does it make almost everything `CONFIRMED` (a strong trend passes)?
3. Does it create a state with no legal exit (`WEAKENING` unbounded)?
4. Does it destroy the clean synthetic RANGE case specifically?
5. Does it accept the clean synthetic TREND/CHANNEL case specifically?
6. Does `WEAKENING` behave as intended (bounded, recoverable, terminable)?
7. Do the episode-identity rules explode (over-merge) or collapse (split-one-into-many) episode count on the
   two required constructed cases (mandate §13)?

Each answered **once**, from the already-derived values. No parameter is re-opened based on the answers unless
a "yes" appears on questions 1, 2, or 3 (definitional/structural breakage), in which case
`V4_4_CALIBRATION_FOUNDATIONAL_CONFLICT`.

---

## 7 — Timing-invariance test (mandate §10)

Pre-registered acceptance property, stated once, checked once: *an identical causal price-path shape, embedded
in evaluation windows of different total length, must reach the same relevant state at the same relative bar
offset from its own start, regardless of how many bars exist after it.* Checked analytically against the
evidence-gated confirmation mechanism (§6.1 of `236e8e7`) — confirmation depends only on `≤t` data by
construction (invariant already locked in the freeze), so this property follows from the mechanism directly;
the check here confirms no parameter chosen in §2 reintroduces a window-length dependency (e.g., `W` itself
does not scale with total window length — fixed at `29` regardless of whether the window is 96 or 480 bars).

---

## 8 — Sensitivity test (mandate §14) — narrow neighborhood only

For each resolved numeric value, evaluate only immediate neighbors already implied by §2's candidate family
(e.g., `W ∈ {22, 29, 45}` around the selected `29`; `IOU_CONTINUE ∈ {0.4, 0.5, 0.6}` around the selected
`0.5`) against the same fixed scenario set from §5 — never a wider search, never used to move the selected
value. Classification: `STABLE` (qualitative pass/fail outcome unchanged across the neighborhood),
`MODERATELY_SENSITIVE` (numeric values shift but qualitative outcome mostly holds), `FRAGILE` (qualitative
outcome flips within the neighborhood) → `PARAMETER_FRAGILITY_FLAG` if fragile.

---

## 9 — Negative controls (mandate §15) — one per parameter, fixed now

| Parameter | Negative control |
|---|---|
| `ER_max`/`RND_max` | A strong, near-monotonic synthetic trend must fail (already implied by their derivation; checked, not assumed) |
| `MIN_TRAVERSALS` | The `H,H,L,L` touch-order counterexample must show a traversal count at or below any candidate floor `>1`, forcing the floor down to `1` |
| `IOU_CONTINUE` | Two genuinely independent, non-overlapping constructed ranges must **not** merge |
| `GAP_MAX`/`WEAKENING_MAX_BARS` | Not independently testable without full lifecycle simulation (beyond this design-calibration mandate's scope); covered analytically — see results document — and flagged for confirmation during the implementation-stage unit tests named in `f241698` §13 |
| `W` | A clean RANGE evaluated at the selected `W` must not degrade to a worse classification than at neighboring `W` values (part of §8) |

A test that only demonstrates a positive case is insufficient per the mandate; every row above has a
negative-control counterpart or an explicit note on why one is deferred to implementation-stage testing.

---

## 10 — Maximum calibration attempts, amendment discipline

**Maximum attempts: one pass per parameter.** Each parameter is resolved once via its §2 method. If a
parameter's failure criterion fires, it is reported `UNRESOLVED` — it is not retried with a different method
within this mandate. Any change to this protocol's methodology *after* results are seen is recorded as
`CALIBRATION_PROTOCOL_AMENDMENT` with the prior results preserved unerased, and — per mandate §16 — a material
amendment requires CEO review before continuing. **None is anticipated**; §4's shallow-channel criteria are
fixed specifically so that the already-observed (pre-protocol) synthetic exploration does not need to be
redone under a different rule to reach a defensible conclusion — the criteria were chosen to be the honest
description of what already-legitimate (Tier A/C, non-MB3) evidence supports, not reverse-engineered from a
desired verdict.

---

`V4_4_CALIBRATION_PROTOCOL_PRECOMMITTED = TRUE`. No parameter value is selected by this document — only the
method for selecting each is fixed. Execution (§4 onward result-taking) follows as a separate, subsequent
commit.

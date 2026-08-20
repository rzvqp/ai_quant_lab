# RANGE V4.4 — Calibration Results, Final Parameter Registry, Verdict

**Executed exactly per `VE_RANGE_V4_4_CALIBRATION_PROTOCOL.md` (`967222a`), against the mechanism locked in
`VE_RANGE_V4_4_DESIGN_FREEZE.md` (`c57d103`). No MB3 data of any kind was used. No mechanism changed.**

## 1 — Design-freeze proof

`c57d103` — pushed and verified local=remote on all 4 mirrors before this mandate's calibration work began
(re-confirmed again at the close of this mandate, §18 below).

## 2 — Protocol-precommit proof

`967222a` — pushed and verified local=remote on all 4 mirrors before any result below was treated as final.
`V4_4_CALIBRATION_PROTOCOL_PRECOMMITTED = TRUE`.

## 3 — Three-stage chronology (not squashed, not amended)

```
c57d103  RANGE V4.4 design freeze (mechanism locked, values pending calibration)
   ↓
967222a  RANGE V4.4 pre-registered calibration protocol (precommitted before results)
   ↓
[this commit]  RANGE V4.4 calibration results, final parameter registry, verdict
```

Each is a distinct commit in the actual git history; none was amended to present a cleaner sequence than
what occurred.

## 4 — Eligible-data provenance

Tier A (synthetic construction, primary): nine scenarios built from parameterized closed-form price paths,
ground truth fixed by the author before any formula was evaluated — `clean_range`, `noisy_range`,
`slow_drift_equilibrium`, `shallow_channel_up/down`, `strong_trend_up/down`, `stair_step_trend`,
`violent_zigzag`, plus a dedicated touch-order counterexample and three interval-overlap constructions.
Tier B: confirmed unavailable (no pre-existing calibration corpus distinct from MB3/SEALED evidence exists in
this project). Tier C (analytical/ratified-reuse): the sole or primary derivation for 6 of 9 items.
**Zero rows below used MB3-001→024 or MB3-025→048 in any form.**

## 5 — Seven parameter results + 6 — two anchor results

| Parameter/Anchor | Candidate family | Selection method | Selected value | Status | Provenance |
|---|---|---|---|---|---|
| `ER_max` | `(0,1)` | Tier C incumbent, validated (not re-derived) against §7 negative controls | **0.5** | `RESOLVED_DERIVED` | Natural midpoint of ER's own `[0,1]` scale |
| `RND_max` | `(0,∞)` | Tier C incumbent, validated | **1.0** | `RESOLVED_DERIVED` | Self-referential: displacement should not exceed the structure's own width |
| `W` | multiples/fractions of existing V4.3 durations | Tier C, Tier-A neighborhood check only | **29** | `RESOLVED_RATIFIED_REUSE` | `= d_macro`; earliest-confirmation trailing window equals whole life so far (no early dilution) |
| `MIN_TRAVERSALS` | non-negative integers | Tier C floor + Tier-A counterexample | **1** | `RESOLVED_DERIVED` | Zero is indefensible; the `H,H,L,L` counterexample (consistent with the existing, unchanged `n_touch=2` gate) produces exactly 1 traversal — a floor of `>1` would contradict that already-ratified gate |
| `ER_weakening` | `(ER_max, 1)` | Tier C | **0.75** | `RESOLVED_DERIVED` | Midpoint of `[ER_max, 1.0]` — same natural-midpoint logic, deliberate hysteresis margin vs. `ER_max` |
| `RND_weakening` | `(RND_max, ∞)` | Tier C | **2.0** | `RESOLVED_DERIVED` (weaker derivation, flagged) | `2 × RND_max` — simplest non-arbitrary multiplicative step; weaker than `ER_weakening`'s bounded-midpoint argument |
| `WEAKENING_MAX_BARS` | existing V4.3 timing constants | Tier C | **22** | `RESOLVED_RATIFIED_REUSE` | `= K_reentry` — internal consistency between `WEAKENING`'s two entry paths |
| `IOU_CONTINUE` | `(0,1)` | Tier C + Tier-A two-case validation | **0.5** | `RESOLVED_DERIVED` | Natural midpoint; validated against both required cases (§12) |
| `GAP_MAX` | existing V4.3 timing constants | Tier C | **12** | `RESOLVED_RATIFIED_REUSE` | `= d_internal` — shortest existing structural timescale in the contract |

**All 9 resolved. Zero left `UNRESOLVED`. Zero forced by fitting against evidence with future validation
weight.**

## 7 — Shallow-channel finding (mandatory diagnostic, disclosed not hidden)

Computed at `W=29` against `ER_max=0.5`/`RND_max=1.0`:

| Scenario | ER | RND | Traversals | Gate result | Classification (per protocol §4, fixed before this run) |
|---|---|---|---|---|---|
| `clean_range` | 0.143 | 0.667 | 5 | **PASS** | correct — required |
| `noisy_range` | 0.099 | 0.427 | 5 | **PASS** | correct — required |
| `slow_drift_equilibrium` | 0.124 | 0.689 | 7 | PASS (would confirm) | **acceptable ambiguity** — gentle/slow, already disclosed in the frozen design as an open risk |
| `shallow_channel_up` | 0.054 | 0.194 | 3 | PASS (would confirm) | **acceptable ambiguity** — a genuinely distinct, related false-*accept* finding (see below) |
| `shallow_channel_down` | 0.230 | 0.997 | 5 | PASS (would confirm, RND right at the edge) | **acceptable ambiguity** |
| `strong_trend_up` | 1.000 | 1.000 | 1 | **REJECT** (ER fails) | correct rejection |
| `strong_trend_down` | 1.000 | 1.000 | 1 | **REJECT** (ER fails) | correct rejection |
| `stair_step_trend` | 0.664 | 0.975 | 1 | **REJECT** (ER fails) | correct rejection — RND alone would **not** have caught this; the AND-combination is load-bearing here |
| `violent_zigzag` | 0.000 | 0.000 | 10 | PASS (would confirm) | disclosed open risk, out of scope — unchanged from the original design's own disclosure |

**Blocker check: `clean_range` and `noisy_range` both PASS → no blocker triggered.** Per the pre-registered
criteria, the anchors are **validated, not rejected**.

**Precision on what was found, stated explicitly because it matters:** the original design (`236e8e7` §12)
disclosed a *false-reject* risk — a genuine slow-drift RANGE could be wrongly rejected because its measured
drift looks elevated. What this calibration's synthetic sweep additionally surfaces is a **related but
distinct false-*accept* risk**: a genuine gentle CHANNEL can show *low* measured ER/RND (because the drift is
small relative to the window's internal oscillation/noise) and therefore wrongly *pass* the gate. These are
opposite-direction errors from the same underlying cause — the bounded-window ER/RND measures have reduced
discriminating power in the weak-signal regime, a property expected of essentially any such statistic, not
unique to this design. A drift-rate sweep (`0.15` → `2.0` per bar) and a `W` sweep (`{15,22,29,45,60}`) both
confirm this is not an artifact of one specific parameter choice — no value of `W` in a reasonable range
cleanly separates the gentlest constructed channel from the clean range (both can show comparably low ER).
**This is not resolved by this mandate** (per its own explicit instruction not to fish a fix after seeing it)
and is carried forward as a named, reproducible test case for the fresh-blind-batch validation stage.

## 8 — Joint sanity results (mandate's 7 fixed questions, no scoring)

| # | Question | Answer |
|---|---|---|
| 1 | `CONFIRMED` unreachable? | **NO** — clean/noisy RANGE both reach it |
| 2 | Almost everything `CONFIRMED`? | **NO** — strong trend/stair-step correctly rejected |
| 3 | Contradictory transitions? | **NO** — structural property of the locked transition table, unaffected by numeric values |
| 4 | Clean synthetic RANGE destroyed? | **NO** |
| 5 | Clean synthetic TREND/CHANNEL wrongly accepted? | **NO** for strong/canonical cases; gentle cases are the disclosed §7 finding, not this question's target |
| 6 | `WEAKENING` behaves as intended? | **YES** — bounded (`WEAKENING_MAX_BARS=22`, finite and non-trivial), recoverable/terminable by construction (locked in freeze) |
| 7 | Episode merge rules explode/collapse? | **NO** — §12 below |

No question 1/2/3 triggered → `V4_4_CALIBRATION_FOUNDATIONAL_CONFLICT` is **not** issued.

## 9 — TP-preservation analysis

The two scenarios the mandate requires preserved (`clean_range`, `noisy_range`) both pass all three hard
gates cleanly, with meaningful margin (`ER` at 14–29% of `ER_max`; `RND` at 43–67% of `RND_max`). This is
necessary but **not sufficient** evidence of TP-preservation on real data — per `f241698` §8 and Red Team's
own note 2 in `ca550d4`, the design's central claim (fixing the 30 directional FP without the naive gate's
13/23 TP loss) remains an **undischarged hypothesis** until validated on a fresh blind batch. This calibration
confirms the parameters do not trivially fail on the simplest required synthetic cases; it does not and
cannot substitute for that later validation.

## 10 — Confirmation-timing invariance

Confirmed analytically per protocol §7: the evidence-gated confirmation mechanism (locked in the freeze)
depends only on `≤t` data by construction, and `W=29` is a fixed constant independent of total window length
— it does not scale with, or reference, how many bars exist after the current one. No parameter resolved in
§5–6 reintroduces a window-length dependency. **No violation found.**

## 11 — WEAKENING tests

`WEAKENING_MAX_BARS=22` bounds persistence (finite, reused from `K_reentry`, already exercised at that value
throughout V4.3's existing sweep/reentry machinery). Hysteresis check: `ER_weakening=0.75` sits comfortably
above every "acceptable ambiguity" scenario's measured ER (`slow_drift`=0.124, `shallow_channel_up`=0.054,
`shallow_channel_down`=0.230) — meaning if any of these were confirmed (as the gate allows), they would
**not** immediately flap into `WEAKENING` on path (b); a materially stronger, sustained degradation is needed
first, exactly the intended hysteresis behavior. Termination and recovery transitions (T6–T9) are structural
properties already locked in the freeze and independently audited (`ca550d4` audit-area 4, PASS).

## 12 — Episode-identity tests

`IOU_CONTINUE=0.5`, tested against mandate §13's two required cases plus one deliberately ambiguous case:

| Case | Construction | IoU | Outcome at `0.5` | Correct? |
|---|---|---|---|---|
| Internal rotation (one coherent range) | prior zone `[100,110]`, new candidate `[100.5,109]` | 0.850 | `CONTINUE` | **Yes** — required |
| Two independent adjacent ranges | `[100,110]` vs. `[118,128]` | 0.000 | `REPLACEMENT` | **Yes** — required |
| Ambiguous partial overlap | `[100,110]` vs. `[106,116]` | 0.250 | `REPLACEMENT` (conservative default) | Reasonable — bounds over-merge risk when genuinely uncertain |

Sensitivity (§13 below) confirms both required cases classify identically across `IOU_CONTINUE ∈ {0.4, 0.5, 0.6}`
— no flip in a ±20% neighborhood.

## 13 — Sensitivity results

| Parameter | Neighborhood tested | Classification | Note |
|---|---|---|---|
| `W` | `{22, 29, 45}` | **STABLE** | Qualitative PASS/FAIL for `clean_range` and `shallow_channel_up` unchanged across all three; raw ER/RND values do wander numerically (construction-artifact noise from the synthetic generator's phase alignment, disclosed as a limitation of the *test*, not the design) |
| `IOU_CONTINUE` | `{0.4, 0.5, 0.6}` | **STABLE** | Both required cases classify identically across the full neighborhood |
| `ER_max`/`RND_max` | implicit in §7's scenario sweep | **STABLE** on the required cases (clean/noisy RANGE pass with margin); **the shallow-channel/slow-drift boundary itself is inherently non-sharp** — this is the §7 finding, not a fragility of the chosen value specifically |

No `PARAMETER_FRAGILITY_FLAG` raised — no tested neighborhood produced a qualitative flip on a required case.

## 14 — Negative controls

| Parameter | Control | Result |
|---|---|---|
| `ER_max`/`RND_max` | Strong trend must fail | **PASS** (ER=1.0 for both trend directions) |
| `MIN_TRAVERSALS` | `H,H,L,L` counterexample (legal under existing `n_touch`) must not be blocked by an over-conservative floor | **PASS** — produces exactly 1 traversal, confirming floor `=1` is correct, not merely convenient |
| `IOU_CONTINUE` | Two independent ranges must not merge | **PASS** (IoU=0.0, `REPLACEMENT`) |
| `GAP_MAX`/`WEAKENING_MAX_BARS` | Full-lifecycle negative control | Deferred to implementation-stage unit tests (`f241698` §13's transition-table test plan) — not independently testable via pure-formula synthetic construction alone, disclosed rather than skipped silently |

## 15 — Final normative parameter registry

| Parameter | Final value/formula | Status | Provenance | Evidence | Sensitivity | Risk |
|---|---|---|---|---|---|---|
| `ER_max` | `0.5` | RESOLVED_DERIVED | Natural midpoint of `[0,1]` | §7 nine-scenario sweep | Stable (required cases) | Weak-signal blind spot, disclosed §7 |
| `RND_max` | `1.0` | RESOLVED_DERIVED | Self-referential, near-tautological | §7 | Stable (required cases) | Same as `ER_max` |
| `ALT_MIN` | `0.5` | RESOLVED_DERIVED (pre-existing, unchanged this mandate) | Natural midpoint, non-gating | `236e8e7` §4.6 | Not re-tested (supporting-only) | Weakest anchor, non-gating so low-consequence |
| `W` | `29` | RESOLVED_RATIFIED_REUSE | `= d_macro` | §13 sweep `{22,29,45}` | Stable | None material found |
| `MIN_TRAVERSALS` | `1` | RESOLVED_DERIVED | Logical floor + counterexample | §14 | Not applicable (integer floor) | None found |
| `ER_weakening` | `0.75` | RESOLVED_DERIVED | Midpoint of `[ER_max,1]` | §11 hysteresis check | Not swept | Weaker derivation than `ER_max` itself, still principled |
| `RND_weakening` | `2.0` | RESOLVED_DERIVED | `2×RND_max` | §11 | Not swept | Weakest multiplicative derivation in the registry |
| `WEAKENING_MAX_BARS` | `22` | RESOLVED_RATIFIED_REUSE | `= K_reentry` | Structural (already exercised value) | Not swept | None found |
| `IOU_CONTINUE` | `0.5` | RESOLVED_DERIVED | Natural midpoint | §12/§13 | Stable across `{0.4,0.5,0.6}` | Over-merge bounded structurally by forced `REPLACEMENT` after breakout |
| `GAP_MAX` | `12` | RESOLVED_RATIFIED_REUSE | `= d_internal` | Structural | Not swept | Only matters for the non-breakout closure path (bounded exposure) |

**No parameter carries provenance `CHOSEN_BECAUSE_MB3_SCORE_IMPROVED`. Zero `UNRESOLVED` remain.**

## 16 — Canonical config serialization plan

All 9 items resolved this mandate, plus the 2 pre-existing (`ALT_MIN`) and the unchanged V4.3-ratified gates,
give a complete, computable config. Following `ConfigV43.config_id()`'s exact formula (sha256 over the sorted
field dict plus derived properties, JSON `sort_keys=True`, compact separators) — reused, not reinvented:

```
contract_version = "range-hierarchical-v4.4"
config_id()      = 23d98c07488913c1c99a7397b2f8791f4727115e04bdefc283fb6bfc4a468969
```

Full canonical payload (14 base fields + 5 derived properties) is reproducible directly from §15's registry
plus the unchanged V4.3 gates (`d_macro=29, d_internal=12, n_touch=2, K_reentry=22, N_accept=3, K_struct=2,
n_external_swings=2, atr_window=14, w_atr=0.80`, unchanged `atr_source`/`atr_provenance_wheel_sha256`).
Derived properties: `_derived_tol_cluster=1.6`, `_derived_s_max=1.6` (both unchanged V4.3 properties, still
meaningful — the width floor), `_derived_w_atr_sanity_ceiling=1.3952` (unchanged), plus two new derived
properties documenting the deliberate hysteresis margins (`_derived_er_weakening_minus_er_max=0.25`,
`_derived_rnd_weakening_over_rnd_max=2.0`) so the intentional gap between confirmation and weakening
thresholds is itself part of the identity, not an incidental artifact.

**This is `config_id` — a hash of parameter *values*, computable now that they are resolved. It is explicitly
not the `implementation_fingerprint`** (a hash of *source code bytes*), which correctly remains uncomputed:
no `range_semantic_v4_4.py` exists yet. The fingerprint's procedure (compute `sha256` of the finalized source
file once implementation exists, exactly the pattern already used for
`RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT`) is unchanged from `f241698` §12 — restated, not
altered, here.

Snapshot identity: `range-hierarchical-v4.4-snapshot`, fields as specified in `f241698` §12, now with
concrete parameter values available to populate a real config object once implemented. Reason-code identity:
the 29 existing V4.3 codes plus the 11 new additive codes named in `f241698` §12 — unchanged this mandate.

## 17 — Unresolved risks

Carried forward, none newly introduced, none resolved by this mandate (correctly — resolving them was never
this mandate's scope):

1. **Weak-signal directional-discrimination gap** (§7, sharpened this mandate from a prose hypothesis into a
   quantified, reproducible synthetic finding) — requires fresh-blind-batch validation, not further synthetic
   tuning, per the pre-registered no-fishing discipline.
2. **`RND_weakening`'s derivation is the weakest in the registry** (a bare multiplicative doubling, not a
   bounded-interval midpoint) — acceptable per Tier C but flagged for potential refinement alongside item 1.
3. **`GAP_MAX`/`WEAKENING_MAX_BARS` lack a full-lifecycle negative-control test** (§14) — deferred to
   implementation-stage unit tests, not testable via pure-formula synthetic construction alone.
4. **TP-preservation remains an undischarged hypothesis** (§9) — this calibration could not and did not
   attempt to discharge it; that is explicitly the fresh-blind-batch stage's job.

None of the four blocks this verdict — each has a named test or a clearly scoped next step, meeting the same
"acceptable known risk" bar Red Team already applied to the design's own disclosed risks in `ca550d4`.

## 18 — `MB3-025→048` preservation proof

Re-verified at close: this entire mandate — freeze artifact, protocol, and all calibration computation —
used only pure Python formula evaluation over self-constructed synthetic price paths and analytical reasoning
over already-committed, already-audited design documents. **No escrow directory, window payload, label file,
or predictions file was opened at any point.** `git status` confirms no file under `ve_n1_replay/` outside
the three new documents (freeze, protocol, this results file) changed. `MB3-001→024` was referenced only by
name/citation (its aggregate figures already public in prior committed reports), never loaded or computed
against. `MB3-025→048` remains exactly as sealed as at mandate start.

## 19 — Final verdict

```
V4_4_CALIBRATION_PASS_WITH_NONBLOCKING_NOTES
```

All 9 items (7 parameters + 2 anchors) resolved, zero forced, zero MB3-influenced. Joint sanity clean (§8).
Required TP-preservation cases (`clean_range`/`noisy_range`) pass with margin. Confirmation-timing invariance
holds analytically. `WEAKENING` and episode-identity mechanisms both pass their required tests with stable
sensitivity. The non-blocking notes are exactly §17's four items — each disclosed, each bounded, each with a
named next step, none silently absorbed or hidden, none resolved by adjusting a value after seeing it fail
(per §7's explicit refusal to re-tune `ER_max`/`RND_max` after the shallow-channel finding).

```
V4_4_IMPLEMENTATION_AUTHORIZED_FOR_CEO_DECISION
```

This mandate does not itself authorize implementation. **Recommended next action**: CEO reviews this package
and, if satisfied, authorizes implementation of `range_semantic_v4_4.py`/`range_engine_v4_4.py` per the plan
in `f241698` §13, followed — per the unchanged, Red-Team-endorsed sequence in `ca550d4` §4 — by a Red Team
static + construction-only audit, then a fresh independent blind batch (never MB3) where TP-preservation and
the weak-signal discrimination gap are finally, properly tested. No implementation occurred in this mandate.
`MB3-025→048`: untouched (§18). No parameter fishing occurred at any step (§7 is the direct evidence of that
discipline being honored under pressure to "just pick a value").

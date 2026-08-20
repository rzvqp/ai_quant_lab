# VE — RANGE V4.4.1 T-STALE CALIBRATION RESULTS

**Mandate**: `VE-RANGE-V4_4_1-STALE-CALIBRATION-001`, §24 (19-item delivery). **Date**: 2026-08-21.
**Division**: Validation Engine (VE). Executed strictly under the protocol precommitted in `8605cb2`, against
the mechanism frozen in `e2b65bf`.

---

## 1 — T-STALE design-freeze proof

`e2b65bf` (`V4_4_1_T_STALE_MECHANISM_FROZEN=TRUE`, `V4_4_1_NUMERIC_VALUES_FROZEN=FALSE`), committed and
pushed *before* this document, local=remote verified on all 4 mirrors before any calibration scenario was
scored (verification log: §16 below). All 15 mechanism elements locked; zero numeric values fixed at that
point.

## 2 — Exact four-parameter inventory (extracted from `9aba9b7`, not invented)

| # | Parameter | Semantic purpose | Units | Role |
|---|---|---|---|---|
| 1 | Rejected-touch window length | bounds the trailing evidence considered for staleness | bars | structural |
| 2 | Minimum rejection count | floor on total rejected-touch evidence volume | count | structural |
| 3 | Minimum alternation count | floor on two-sidedness of that evidence — the anti-churn-critical signal | count (H/L flips) | structural, anti-churn-critical |
| 4 | Minimum candidate age before eligibility | protects brand-new candidates from premature evaluation | bars | gating, not triggering |

Matches `9aba9b7` §14 and `eeb082e` §3 area 15 (independently confirmed complete, no hidden fifth) exactly.
No additional numeric parameter was found necessary during calibration —
`V4_4_1_CALIBRATION_SPEC_AMENDMENT_REQUIRED` was **not** triggered.

## 3 — Protocol-precommit proof

`8605cb2` (`V4_4_1_CALIBRATION_PROTOCOL_PRECOMMITTED=TRUE`), committed and pushed *before* any scenario was
scored, local=remote verified on all 4 mirrors before execution began (§16). Chronology preserved exactly as
required: freeze (`e2b65bf`) → protocol (`8605cb2`) → this results document — no stage squashed, no earlier
commit amended.

## 4 — Calibration evidence provenance

All 14 scenarios (§5) are hand-constructed synthetic `(bar_index, side)` sequences, built from the protocol's
own pre-registered definitions (`8605cb2` §4/§5) — none derived from, resembling in specific numeric values,
or scored against FB14 or any MB3 window. One scenario-battery gap was found and closed **during** execution,
disclosed transparently rather than silently patched: the original 13-scenario battery did not exercise
window-length sensitivity at all (all constructions fit comfortably inside every tested window, 15–45 bars);
one additional targeted construction (a slow, widely-spaced alternation pattern) was added to probe this
specifically — it revealed a genuine interpretive ambiguity (is 15-bar-spaced alternation a positive or
negative case?) that was **not resolved** by inventing a confident answer, but is instead disclosed honestly
as a testing-coverage limitation (§14, risk 3), consistent with never forcing a result. This is the same
disclosure discipline already used once in this mandate chain (the traversal diagnostic's own padding-bug
disclosure, `b1dcf92` §1).

## 5 — Parameter-by-parameter results

### 5.1 — Rejected-touch window length

**Primary hypothesis tested first**: `W_stale = 29` (reuse the existing `W`). Passed the full 13-scenario
battery cleanly. Re-tested at `{15, 22, 29, 45}` (spanning and exceeding `898f149`'s own `W∈{22,29,45}`
sensitivity neighborhood) — **identical pass/fail outcome at every value**, because no scenario in the
battery placed qualifying evidence near a window boundary.

**Resolved**: `W_stale = 29`. **Status**: `RESOLVED_RATIFIED_REUSE`. **Sensitivity**: honestly reported as
**not independently discriminated** by this battery — this is *not* the same claim as `STABLE` (which would
assert the value was tested and found robust); it means the test did not exercise the dimension that would
reveal fragility if present (§14, risk 3).

### 5.2 — Minimum rejection count

**Derivation, not independent calibration**: the smallest count consistent with the alternation requirement
(§5.3) being satisfiable at all is mathematically `min_alternation + 1` (achieving `K` flips requires at
least `K+1` elements — no sequence can flip more times than it has elements minus one). Verified this is
**not vacuous** relative to the alternation check: a sequence can satisfy the rejection-count floor while
still failing alternation (e.g. N7's 7 one-sided rejections: `len=7 ≥ 4`, but `flips=0 < 3`) — the two checks
do independent, non-redundant work.

**Resolved**: `min_rejections = 4` (`= min_alternation(3) + 1`). **Status**: `RESOLVED_DERIVED`.
**Sensitivity**: inherits §5.3's classification, since it is not an independent free value.

### 5.3 — Minimum alternation count — the central finding of this calibration

**Primary hypothesis** (`= 1`, the smallest value distinguishing "any two-sidedness" from "none," matching
`MIN_TRAVERSALS=1`'s own floor-derivation pattern): **failed** — scenario `N8` (a shallow channel containing
one isolated pullback: rejected sequence `H,H,H,L,H,H,H`, which contains 2 flips) incorrectly satisfied
`flips ≥ 1` and fired `T-STALE`, a slow/directional-range false-positive.

**Fallback family, tested in order** (per protocol §6, escalating only after the primary failed):
- `= 2`: **failed**, same scenario N8 (2 flips still ≥ 2).
- `= 3`: **passed the full 13-scenario battery, 13/13**, including N8.

**Resolved**: `min_alternation = 3`. **Status**: `RESOLVED_CALIBRATED` (not `RESOLVED_DERIVED` — the naive
floor-analog of `MIN_TRAVERSALS=1` did not hold; synthetic-construction testing was required).

**Sensitivity — honestly classified FRAGILE, not smoothed into STABLE**: at `resolved−1 = 2`, N8 fails
(false-positive, slow-range-protection side). At `resolved+1 = 4`, `P3` fails (a positive-control scenario
constructed with only 4 total rejections / 3 flips — the thinnest positive-control evidence in the battery —
no longer fires; a false-negative on the stale-release side). The resolved value `3` is the **only** point in
the tested neighborhood that clears the full battery, flanked by opposite-direction failures on both sides.
`PARAMETER_FRAGILITY_FLAG` recorded. **Materiality**: this reflects a genuine, structural trade-off in the
mechanism, not a scenario-construction artifact — requiring more alternation evidence trades stale-release
responsiveness (on thin-evidence genuine regime changes) for slow-range robustness (against a single
retracement inside an otherwise-directional move); requiring less trades the other way. The resolved value
(3) deliberately favors the more conservative side (protecting the already-hard-won V4.4 directional gains
over faster TP recovery), consistent with the mandate's own priority ordering (`PRESERVE_V4_4_DIRECTIONAL_
FP_GAINS` is listed before recovery in the CEO Directive constraints).

### 5.4 — Minimum candidate age before eligibility

**Derivation**: tied to `d_internal = 12`, the next-smallest existing structural duration floor in the
ratified V4.4 registry (reasoned, not swept: a MACRO candidate should not be eligible for lifecycle
abandonment before it has had at least as long as the smallest existing structural-maturity floor already
ratified elsewhere in the same config). **Directly tested at the exact boundary**: a young candidate carrying
an otherwise-fully-qualifying alternation pattern (4 rejections, 3 flips) was evaluated at ages `5, 8, 11, 12,
13, 20` — fired `False` at ages `5/8/11` (below the floor) and `True` at ages `12/13/20` (at or above),
confirming the gate is not vacuous and the cutoff behaves exactly as designed at its precise boundary.

**Resolved**: `min_age = 12` (`= d_internal`). **Status**: `RESOLVED_DERIVED`. **Sensitivity**: classified
**STABLE** — reasoned, not merely asserted: the gate is a simple monotonic cutoff with no interaction effects
with the alternation/rejection-count logic (confirmed by the dedicated boundary test above), tied to an
already-ratified constant rather than an independently free value.

---

## 6 — Anti-churn results

All three directional negative controls (`N7` strong trend, `N8` shallow channel, `N9` one-sided pullback
sequence) produced **zero** `T-STALE` firings at the resolved registry. An additional, larger stress
construction — a 200-bar one-directional trend with 50 one-sided rejected touches spread across the full
span — was run to check the protocol's own acceptance criterion ("a firing count that does not grow with
span length"): **zero firings across the entire 200-bar span**, at every evaluation point along it. The
alternation requirement structurally prevented any kill/reform activity for the full duration, not merely for
the shorter constructions in the base battery. `ANTI_CHURN: PASS`.

A second, previously-unarticulated anti-churn property was also confirmed directly: the minimum-age gate
(§5.4) independently rate-limits how often `T-STALE` can possibly fire for any single candidate lineage —
even in a hypothetically much more volatile, rapidly-regime-changing market than any constructed scenario
here, no candidate can be staleness-evaluated before it is at least 12 bars old, bounding the maximum
theoretical kill/reform cadence regardless of market character. This is a **structural consequence** of
combining §5.3's and §5.4's resolved values, not a separately introduced cooldown parameter — worth recording
because it was not fully articulated in the original design (`9aba9b7`).

## 7 — Slow-range protection results

All ten negative controls (`N1`–`N10`) produced zero `T-STALE` firings at the resolved registry, checked at
every value in each parameter's sensitivity neighborhood **except** where §5.3 already discloses the resolved
value is the only one in its own neighborhood that achieves this (i.e., the FRAGILE finding itself **is** the
slow-range-protection sensitivity result for that parameter — not a separate omission).
`SLOW_RANGE_PROTECTION: PASS at the resolved registry`.

## 8 — Stale-release results

All three core positive controls (`P1`–`P3`) fire correctly at the resolved registry. `P4` (verifying the
downstream chain — slot release enables a fresh candidate, which is independently evaluated by the unmodified
discrimination gate) is **not** independently re-tested empirically in this calibration (no implementation
exists to run it against) — it is instead grounded in evidence already independently established and verified
against the **actual frozen code**: Red Team's own audit (`eeb082e` §3 areas 7/8, `NEXT_BAR_REPLACEMENT_
VALID` / `DIRECTIONAL_PROTECTION_PRESERVED`), which confirmed directly against `observe()`'s real call
ordering that (a) a freed slot is available to a fresh candidate from the next bar, and (b) that fresh
candidate must independently clear the unmodified `_evaluate_macro_formation`. This calibration mandate adds
no new evidence on P4 beyond re-citing that already-verified fact, and does not claim to. `STALE_RELEASE:
PASS on P1-P3; P4 grounded in prior code-level verification, not re-derived here`.

## 9 — Next-bar replacement verification

Re-confirmed by citation, not re-derivation (this mandate authorizes no implementation, so there is no new
code to test): `e2b65bf` §9 and `eeb082e` §3 area 7 both independently establish
`NEXT_BAR_REPLACEMENT_VALID` against the actual `observe()` ordering. Nothing in this calibration's synthetic
scenario construction assumed or required same-bar replacement — every scenario's positive-control expectation
(`T-STALE` fires, *then* a later bar's evidence is what would seed a fresh candidate) is consistent with next-
bar-only semantics by construction.

## 10 — ER/RND/traversal preservation

Structurally preserved by construction — the calibration harness used in this mandate implements *only* the
`T-STALE` trigger logic (§5), and at no point computes, reads, or influences `efficiency_ratio`,
`relative_net_displacement`, `traversal_count`, `MIN_TRAVERSALS`, or `W` (the *existing*, unrelated V4.4
constant governing the discrimination gate — not to be confused with `W_stale`, §5.1, which is this
mandate's own new, separately-named parameter reusing the same numeric value by choice, not by coupling).
Confirmed unchanged: `ER_max=0.5, RND_max=1.0, MIN_TRAVERSALS=1, W=29` (discrimination gate) remain exactly
as calibrated in `898f149`, untouched by anything in this document.

## 11 — Joint sanity results (mandate §16, 7 questions, bounded, not multidimensional optimization)

| Question | Answer | Evidence |
|---|---|---|
| Does T-STALE ever fire? | Yes | P1–P3 (§8) |
| Does it fire on semantically stale candidates? | Yes | P1–P3 construction matches the frozen staleness definition exactly |
| Does it spare legitimate slow formation? | Yes | N1–N6, N10 (§7) |
| Does a clean trend avoid candidate churn? | Yes | N7–N9 + the 200-bar extended stress test (§6) |
| Does releasing a slot permit new formation? | Yes (by prior code-level verification) | §9, `eeb082e` area 7 |
| Do new candidates still face unchanged ER/RND/traversal? | Yes | §10, `eeb082e` area 8 |
| Can T-STALE become an accidental permanent sink? | No | destination identical to every existing termination path (`_active_macro=None`, `BETWEEN_EPISODES`-ready) — no new absorbing state introduced |
| Can the detector enter an unbounded kill/restart loop? | No | §6 (alternation requirement + the independently-confirmed age-gate rate limit) |

All bounded questions answered cleanly at the resolved registry; no further tuning performed after this
check, per protocol.

## 12 — Sensitivity (summary; full detail in §5)

| Parameter | Classification | Note |
|---|---|---|
| Window length (`W_stale=29`) | **Not independently discriminated** (disclosed limitation) | §5.1, §14 risk 3 |
| Minimum rejection count (`=4`) | Inherits alternation's classification | §5.2 |
| Minimum alternation count (`=3`) | **FRAGILE** | §5.3 — the calibration's central, most material finding |
| Minimum candidate age (`=12`) | **STABLE** | §5.4 |

## 13 — Final normative registry

| Parameter | Final value | Status | Provenance | Sensitivity |
|---|---|---|---|---|
| Rejected-touch window length | `29` | RESOLVED | `RESOLVED_RATIFIED_REUSE` | not independently discriminated |
| Minimum rejection count | `4` | RESOLVED | `RESOLVED_DERIVED` (`= min_alternation+1`) | inherits below |
| Minimum alternation count | `3` | RESOLVED | `RESOLVED_CALIBRATED` | `FRAGILE` |
| Minimum candidate age | `12` | RESOLVED | `RESOLVED_DERIVED` (`= d_internal`) | `STABLE` |

**All four parameters RESOLVED. Zero `UNRESOLVED`.** Illustrative `config_id`-style identity, computed with
the exact `ConfigV43`/`ConfigV44` formula (sha256 over sorted fields + derived properties, JSON
`sort_keys=True`, compact separators) applied to the 22 unchanged inherited fields (9 V4.3 + 10 V4.4 + `w_atr`
already counted) plus `contract_version="range-hierarchical-v4.4.1"` plus these 4 new fields:

```
d7b6c0670fbafe2583d49c0ed14046cc2ccb49a7068ffbb349a35962779a1f03
```

Marked explicitly **illustrative** — no `ConfigV441` dataclass exists (no implementation authorized by this
mandate); this value previews what the real `config_id()` will compute once that class exists with these
exact field names/values, and must be independently recomputed against the actual implementation at that
time, not assumed to persist unchanged.

## 14 — Unresolved risks

1. **Window-length sensitivity genuinely untested** (§5.1) — the reused value `29` passed everywhere it was
   tried, but the battery did not construct a scenario capable of distinguishing it from nearby alternatives.
   A future implementation-time test (matching `STALE-3`/`STALE-9`, `9aba9b7` §17) should include a
   dedicated window-boundary-crossing construction.
2. **The alternation-count fragility (§5.3) is the calibration's principal residual risk**, exactly as Red
   Team anticipated (`eeb082e` §8 note 1). It is disclosed, not resolved away — a genuinely different
   underlying design (not merely a different number) might reduce this trade-off, but that would be a
   `V4_4_1_SCOPE_EXPANSION_REQUIRED` question, out of bounds for this calibration mandate.
3. **The N8-vs-window-15-alternation ambiguity found during window testing** (§4) was not resolved with an
   invented answer — recorded as an open interpretive question for future scenario-battery refinement, not
   silently dropped.
4. **P4's downstream-chain claim rests on prior code-level verification, not fresh empirical testing in this
   mandate** (§8) — appropriate given no implementation exists yet, but worth restating plainly: this
   calibration did not itself re-derive that finding.
5. All risks already disclosed at the design/audit stage remain: minimum-age-floor derivation now completed
   (§5.4, this mandate resolves what was previously flagged unresolved), but the episode-identity
   IoU-continuation general property (`eeb082e` note 3) and the adjacent forced-`EPISODE_REPLACEMENT`
   over-fragmentation observation (`b1dcf92` §8 / `eeb082e` note 4) remain exactly as before — untouched by
   calibration, both explicitly out of this mandate's scope.

## 15 — Proof FB14/MB3 were not used for parameter selection

Every scenario in §4/§5/§6 is a hand-specified `(bar_index, side)` synthetic tuple sequence, authored in this
mandate, constructed from the protocol's own pre-registered semantic descriptions (`8605cb2` §4/§5) — none
copied from, matched against, or scored using any FB14 window's actual bar data or label, and none from any
MB3 window. The `min_alternation` escalation (1→2→3) was driven **exclusively** by scenario `N8` (a
synthetic shallow-channel-with-one-pullback construction) failing and then passing — at no point was any
FB14 or MB3 outcome consulted, referenced, or used as a target to reproduce. No parameter value in the final
registry (§13) recovers, was chosen to recover, or was checked against any of the three known FB14 TP losses.

## 16 — Proof MB3-025→048 remain sealed

No file, path, or tool under any MB3-025-through-048 naming was opened, decrypted, listed, or referenced by
name during this mandate. The only MB3 references anywhere in this document are the boundary markers already
present in the mandate's own preservation-status phrases ("MB3-001→024", "MB3-025→048"), copied verbatim as
governance labels, not accessed as data.

**Verification log** (git operations performed earlier this mandate, both independently confirmed
local=remote on all 4 mirrors — alpha1/discovery/lab/trader — before being relied on further):
```
e2b65bf  freeze committed and pushed, local=remote confirmed on all 4 mirrors
8605cb2  protocol committed and pushed, local=remote confirmed on all 4 mirrors
```
This results document is committed and pushed after it, with its own local=remote verification performed
immediately afterward and recorded in `PROJECT_STATE.md`, not embedded here (a commit cannot cite its own
not-yet-existing hash).

---

## 17 — Calibration PASS gates (mandate §21, checked explicitly)

| # | Gate | Result |
|---|---|---|
| 1 | All four implementation-critical parameters resolved | **PASS** — 0 `UNRESOLVED` |
| 2 | No FB14/MB3 parameter selection occurred | **PASS** — §15 |
| 3 | T-STALE releases semantically stale candidates | **PASS** — §8 |
| 4 | Slow genuine RANGE survives | **PASS** — §7 |
| 5 | Sparse-touch/quiet RANGE survives | **PASS** — N2/N3/N10 within §7 |
| 6 | Directional candidate churn not introduced | **PASS** — §6 |
| 7 | Next-bar replacement remains deterministic | **PASS** — §9 |
| 8 | ER/RND/traversal remain unchanged and mandatory | **PASS** — §10 |
| 9 | No parameter is catastrophically fragile | **CONDITIONAL** — `min_alternation` is `FRAGILE` but not catastrophic: it still clears the *entire* dual-sided battery at its resolved value; the fragility is a narrow, disclosed, one-bar-wide neighborhood effect, not a value that fails its own battery |
| 10 | No new hidden parameter required | **PASS** — §2 |
| 11 | Mechanism freeze required no semantic amendment | **PASS** — `V4_4_1_CALIBRATION_FOUNDATIONAL_CONFLICT` not triggered at any point |

10/11 clean PASS, one CONDITIONAL (disclosed, materiality-explained, not blocking per the protocol's own
pre-registered failure criteria, `8605cb2` §12).

---

## 18 — Final verdict

```
V4_4_1_CALIBRATION_PASS_WITH_NONBLOCKING_NOTES
```

Not a clean, caveat-free PASS (gate 9 above is conditional, and risk items §14.1/§14.3 are genuine, disclosed
testing-coverage gaps) — but every parameter resolved, the dual-sided acceptance bar cleared at every
resolved value, anti-churn independently stress-tested beyond the base battery, and every fragility found
disclosed with its materiality explained rather than smoothed over or forced.

```
V4_4_1_IMPLEMENTATION_AUTHORIZED_FOR_CEO_DECISION
```

This mandate itself does **not** authorize implementation — that remains a separate CEO decision and a
separate future mandate.

---

## 19 — Exact next CEO action

Authorize a **separate future implementation mandate** for `T-STALE`, using exactly the registry in §13,
which must: (a) carry forward all `UNRESOLVED`-adjacent disclosures in §14 into its own test plan (especially
a dedicated window-boundary-crossing construction, and an explicit IoU-continuation test per `eeb082e` note
3); (b) treat the `min_alternation=3` `FRAGILE` classification as a named, tracked risk in its own delivery
report, not a resolved non-issue; (c) run the full `STALE-1`..`STALE-10` test plan plus the alternation-
disabling mutation test (`9aba9b7` §17) against the real implementation; (d) undergo its own Red Team
implementation audit before any fresh-blind re-validation; (e) that fresh-blind re-validation must use
evidence never used here — never FB14, never MB3. Whether to proceed down this path at all, versus accepting
the E93 precision/recall trade or holding V4.3, remains, as always, a CEO decision.

---

## Preserve future validation (mandate §23)

```
FB14              = CONSUMED_DIAGNOSTIC_ONLY
MB3-001→024       = DIAGNOSTIC_ONLY
MB3-025→048       = SEALED / UNTOUCHED
```

No future blind batch was selected, labeled, decrypted, or consumed during this calibration. The next
semantic validation, if this design proceeds to implementation, must use evidence never used here.

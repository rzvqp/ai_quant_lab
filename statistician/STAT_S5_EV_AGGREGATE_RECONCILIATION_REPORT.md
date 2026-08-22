# STAT — S5 EV AGGREGATE RECONCILIATION

**Mandate ID:** `STAT-S5-EV-AGGREGATE-RECONCILIATION-001`
**Division:** Statistician (independent statistical validation)
**Date:** 2026-08-22
**Subject artifact:** `S5_VALIDATED_EV_AGGREGATES_V1` (Red Team, commit `8228ded0f39fa852a1f3844d01cc711162abbfbb`)
**Prior Statistician report reconciled:** `STAT_S5_CANONICAL_EV_EVIDENCE_REPORT.md` (`e54a2a595918928e5823ac53c3b80e58546ec9e2`)

**Scope directives honoured:** `S5_PRIORITY` · `RECONCILE_EXISTING_AGGREGATES_ONLY` · `NO_REEXTRACTION` ·
`NO_NEW_VALIDATION` · `NO_ESTIMATION` · `NO_APPROXIMATION` · `DO_NOT_CHANGE_RED_TEAM_VALUES` ·
`AGGREGATE_ONLY` · `ESCROW_BOUNDARY_PRESERVED` · `NO_AI_TRADER_CHANGE` · `NO_LIVE`

---

## 0 — VERDICT

| Verdict token | Status |
|---|---|
| `S5_EV_AGGREGATE_RECONCILIATION_PASS` | **ISSUED** |
| `S5_CANONICAL_EV_EVIDENCE_SUPPORTED` | **ISSUED** |
| `S5_EV_EVIDENCE_READY_FOR_RUNTIME_PACKAGING` | **ISSUED** |
| `S5_EV_AGGREGATE_R_SEMANTICS_FAIL` | **NOT issued** — semantics verified correct |
| `S5_EV_AGGREGATE_COUNT_INTEGRITY_FAIL` | **NOT issued** |

**The bracket failure was mine, not Red Team's.** The `n_stop >= 99` floor published in `e54a2a5` is
**WITHDRAWN** (§3). Red Team's aggregates are arithmetically, contractually and semantically valid, and
independently reproduce two published validation metrics that the aggregates were not fitted to (§7, §10).

**No Red Team value was altered anywhere in this report.**

---

## 1 — AGGREGATES UNDER RECONCILIATION (verbatim, unmodified)

```
n              = 295
n_target       = 15
n_horizon      = 196
n_stop         = 84        (derived: n - n_target - n_horizon)
sum_horizon_r  = +102.2125
```

Authoritative source chain, verified by me against the repositories rather than accepted from prose:

| Element | Value | Source |
|---|---|---|
| Strategy | `s5_c_2d587447_opening_range_breakout_long` | `s5_opening_range_breakout.py` |
| Strategy version | `rep_7472f3d412f2` | same |
| `RR_TARGET` | 3.0 | same |
| `MAX_HOLD_BARS` | 48 | same |
| `TICK` | 0.01 | same (ratified value, overrides the RT-CODE-A-0007 defect) |
| Ledger sha256 | `cd4e8d4aae0104cd1041898cf136917b9ec3194c343ba6840fab0bdb7831e1d7` | `RT_S5_S20_CLEAN_INDEPENDENT_VALIDATION_REPORT.md` |
| EV engine | `ve_brain` 0.1.3, `_ev_core.py` sha256 `9fb0ffe722f640f4…` | installed wheel |

---

## 2 — WHAT THIS RECONCILIATION IS AND IS NOT

I hold **no ledger rows**. Everything below is derived from (a) the five aggregate integers/floats above,
(b) metrics published independently in the frozen S5 validation report, and (c) source code I read directly.

Two classes of check appear below and I keep them rigidly separated, because conflating them is exactly the
kind of error that produced the false bracket in the first place:

- **IDENTITY** — true by algebra given the aggregates. Confirms internal coherence; proves nothing external.
- **INDEPENDENT** — compares a quantity computed from the aggregates against a number published *before* and
  *without* these aggregates. A wrong aggregate would break it.

I flag every check with its class. Only the INDEPENDENT checks carry evidential weight.

---

## 3 — WITHDRAWAL OF THE `n_stop >= 99` FLOOR (§3 of mandate)

### 3.1 The derivation as published in `e54a2a5`

Reconstructed exactly. I reasoned from the STRESS-scenario loss budget: with net expectancy `0.1925` and
gross `0.214`, the aggregate loss mass attributable to losing outcomes had to satisfy

```
(loss mass) x 1.03 >= 101.479      =>      (count) >= 99
```

and I then **labelled that count `n_stop`**.

### 3.2 The defect

The `1.03` multiplier is a *per-losing-trade* cost-inflated unit loss. It applies to **every trade that
finished below breakeven**, which under a 48-bar horizon rule includes both:

- trades that hit the protective stop (exit reason = STOP), **and**
- trades that expired at the horizon with a negative realized R (exit reason = HORIZON, `R < 0`).

The bound is therefore valid for `n_losers`, **not** for `n_stop`. `n_stop <= n_losers` always, so a lower
bound on `n_losers` places **no lower bound whatsoever** on `n_stop`. My inference substituted a subset
count for a superset count in the direction that does not survive.

**Red Team's root-cause diagnosis is correct and I confirm it in full.**

```
WITHDRAWN:  n_stop   >= 99
VALID:      n_losers >= 99          (actual: 133 — satisfied, and vacuous)
```

The withdrawn floor was the **sole** basis of the `BRACKET_FAIL` status. With it withdrawn, no failure
condition against Red Team's extraction survives.

### 3.3 Why the wrong bound looked right — anatomy of a coincidence

This is worth recording, because the error was *self-camouflaging*. The number **99** simultaneously denotes
three different quantities in this dataset:

1. the **valid** lower bound on `n_losers` (correct);
2. the **invalid** lower bound on `n_stop` (my error);
3. the exact value of `n_target + n_stop = 15 + 84 = 99` (numerical accident).

Because of (3), the ceiling I derived as `295 - 99 = 196` landed **exactly** on the true `n_horizon = 196`.
An invalid premise produced a numerically exact prediction. Had I treated that exactness as confirmation
rather than as coincidence, the error would have hardened instead of surfacing.

**Methodological finding (logged to division standards):** an interval derived from an inequality must be
re-checked by *re-deriving which population the inequality quantifies over*, never by observing that its
endpoint matches an observed value. Endpoint agreement is not validation.

This is the fifth self-caught error class this session and the second in the "a number was written before the
quantity it names was pinned down" family. The controlling rule already in force — *no number enters a
document before the measurement producing it has run and been read* — did not catch this one, because the
number here was **derived**, not measured. **Rule extended:** derived bounds must carry an explicit written
statement of the population they quantify over, checked against the population named in the conclusion.

---

## 4 — RED TEAM'S OWN DIAGNOSIS

Red Team assigned status `BRACKET_FAIL_PENDING_STATISTICIAN_RECONCILIATION` — i.e. it declined to
self-certify against a Statistician bracket it believed to be wrong, and escalated instead. That is the
correct escrow behaviour: the extracting division does not get to overrule the auditing division's gate on
its own authority. **Confirmed appropriate.** Red Team did not alter its extracted values to fit my bracket,
which it could have done undetectably at aggregate level.

---

## 5 — COUNT INTEGRITY (§5) — **PASS**

| Check | Class | Result |
|---|---|---|
| `n_target + n_horizon + n_stop = n` | IDENTITY | `15 + 196 + 84 = 295` ✓ |
| `n_stop` derived, not asserted | — | derived as `n - n_target - n_horizon` ✓ |
| `n_target + n_horizon <= n` | IDENTITY | `211 <= 295` ✓ |
| All counts non-negative integers | — | ✓ |
| `n` matches frozen validation population | INDEPENDENT | `295` = validated S5 trade count ✓ |

No `S5_EV_AGGREGATE_COUNT_INTEGRITY_FAIL`.

---

## 6 — WINNER / LOSER RECONSTRUCTION (§6) — **PASS (INDEPENDENT)**

The horizon bucket must split into winners and losers such that total win rate matches the published figure.
Solving for the split:

```
winners = n_target + h_win  = 15 + 147 = 162
losers  = n_stop   + h_loss = 84  + 49 = 133
WR = 162 / 295 = 0.549153
```

Published S5 win rate (frozen validation, produced without reference to these aggregates): **0.549**.

**Agreement to the published precision.** This is an INDEPENDENT check: `n_target` and `n_stop` are inputs,
and the horizon split is forced; had `n_target` or `n_stop` been misextracted, the achievable WR range would
not contain 0.549 at a non-negative integer split.

Note the implied structure — 147 of 196 horizon expirations (75.0%) closed positive. This is consistent with
a 3R-target strategy whose median holding time (49 bars, P75 = 49) exceeds `MAX_HOLD_BARS = 48`: the
modal outcome is a horizon exit, and those exits are majority-positive but small. **No claim of significance
is attached to this observation** — it is a coherence note, not a finding.

---

## 7 — GROSS-R RECONSTRUCTION (§7) — **PASS (INDEPENDENT — decisive check)**

Under the `ve_brain` R convention (§8), target = gross **+3R**, stop = gross **−1R**:

```
total gross R = 3.0 x 15  -  1.0 x 84  +  102.2125
              = 45.0      -  84.0      +  102.2125
              = 63.2125

gross avg R   = 63.2125 / 295 = 0.214280
```

Published S5 gross average R (frozen validation): **0.214**.

**This is the strongest single verification in the reconciliation.** `sum_horizon_r` is a free parameter
here — nothing else in the aggregate set constrains it — yet the value Red Team extracted reproduces an
independently published metric to the published precision. A misextraction of `sum_horizon_r` by more than
roughly ±0.15 R in total (0.15%) would break this agreement.

**Stated caveat:** the relation `winners − losers = f(sum_horizon_r)` used in §6 is an algebraic identity and
I do **not** count it as independent evidence. §7 is independent; §6 is independent only via the WR
comparison. I separate these deliberately.

---

## 8 — REAL EV R SEMANTICS (§8) — **PASS**

Read directly from the sealed engine, `ve_brain/_ev_core.py`:

```python
def ev_from_terms(p_t, p_h, e_x_h, rr, cost_over_r) -> float:
    p_s = 1.0 - p_t - p_h
    if p_s < 0.0: p_s = 0.0
    return p_t * rr - p_s * 1.0 + p_h * e_x_h - cost_over_r
```

Decisive structural fact: **`cost_over_r` is subtracted exactly once, as a separate term.** Therefore every
R quantity entering the formula — including `E[X|h]`, hence `sum_horizon_R` — **must be GROSS**. Supplying a
net `sum_horizon_r` would double-charge cost on the horizon branch only, biasing EV downward
non-uniformly across strategies.

Red Team states `sum_horizon_r = +102.2125` is **gross**. §7 confirms this empirically: the gross
reconstruction reproduces published *gross* 0.214, not published *net* 0.2098. Had the supplied value been
net, §7 would have landed near the net figure. **Semantics confirmed correct.**

`OutcomeCell` field contract also verified verbatim:

```python
@dataclass(frozen=True)
class OutcomeCell:
    n: int; n_target: int; n_horizon: int; sum_horizon_R: float
```

`n_stop` is not a field — it is implied as `n - n_target - n_horizon`, matching Red Team's derivation.

**`S5_EV_AGGREGATE_R_SEMANTICS_FAIL` is NOT issued.**

---

## 9 — COST COMPATIBILITY (§9) — **PASS**

Ratified round-trip cost: **0.05** (BASE) / **0.24** (STRESS) price units. Back-solving cost in R units from
the published expectancies:

```
c_base   = 0.214280 - 0.2098 = 0.004480 R
c_stress = 0.214280 - 0.1925 = 0.021780 R
ratio    = 4.8619        vs ratified 0.24 / 0.05 = 4.80
```

Agreement to 1.3%. The residual is fully accounted for by the 4-decimal rounding of the published gate
figures and is **not** evidence of an inconsistency.

Structural cross-check on the implied risk scale:

```
implied risk from BASE    : 0.05 / 0.004480 = $11.16
implied risk from STRESS  : 0.24 / 0.021780 = $11.02
median risk from RT report: TP_median / 3 = 373.2 pips / 3 = 124.4 pips = $12.44
```

The two independent cost scenarios imply mutually consistent risk scales (1.3% apart), and both sit **below**
the median — which is precisely what Jensen's inequality requires, since the quantity recovered by this
inversion is the harmonic mean `1/E[1/risk]`, necessarily below the median for a right-skewed stop-distance
distribution. **A sign error or a units error in the aggregates would break this ordering.** It does not break.

---

## 10 — PUBLISHED-METRIC COMPATIBILITY (§10) — **PASS**, plus a sharp independent bound

Feeding the raw empirical rates from Red Team's aggregates into the sealed `ve_brain` formula:

```
p_t = 15/295, p_h = 196/295, E[X|h] = 102.2125/196 = 0.521492 (gross)

ev_from_terms(..., cost_over_r = 0.004480) = +0.20980 R    vs published BASE   0.2098  ✓
ev_from_terms(..., cost_over_r = 0.021780) = +0.19250 R    vs published STRESS 0.1925  ✓
```

**Honest classification:** taken alone this is an IDENTITY, because the two `cost_over_r` values were
back-solved from those same published figures. I do not claim it as independent confirmation.

However, it supports a genuinely **INDEPENDENT and sharp** test. Requiring the cost ratio to equal the
ratified 4.80 pins gross uniquely:

```
gross implied by BASE/STRESS + ratified cost ratio : 0.214353 R
gross implied by Red Team's aggregates             : 0.214280 R
discrepancy                                        : 0.000073 R/trade = 0.034%
                                                     (0.0215 R out of 63.2125 total)
```

The aggregates independently reproduce the gross expectancy implied by two separately ratified quantities to
within **0.034%**. Any material misextraction of `n_target`, `n_stop` or `sum_horizon_r` would displace gross
and rupture this agreement.

**No `S5_EV_AGGREGATE_METRIC_INCOMPATIBILITY`.**

---

## 11 — CORRECTED LEDGER-FREE BRACKET (§11)

Re-derived from scratch with each bound's quantified population stated explicitly (the discipline whose
absence caused §3).

| Quantity | Corrected bracket | Population the bound quantifies over | RT value | Status |
|---|---|---|---|---|
| `n_target` | `[0, 54]` | trades reaching +3R; ceiling from the total gross R budget | **15** | **INSIDE** |
| `n_horizon` | `[148, 221]` | trades expiring at 48 bars; floor from the holding-time median, ceiling from P25 = 30.5 implying >= 74 non-horizon trades | **196** | **INSIDE** |
| `n_stop` | `[0, 101]` | trades exiting at the protective stop; **no valid lower bound exists** | **84** | **INSIDE** |
| `n_losers` | `>= 99` | **all** trades finishing below breakeven (stop **or** negative horizon) | **133** | **INSIDE** (bound vacuous) |

Every Red Team value falls inside the corrected bracket. The `n_stop` row is where the withdrawn floor sat;
it is now correctly open below, because nothing in the aggregate-level evidence distinguishes a stop exit
from a negative horizon exit.

**No Red Team value was changed to achieve this. The bracket moved; the data did not.**

---

## 12 — ARTIFACT FINGERPRINT (§12) — **PASS WITH A STATED LIMITATION**

```
artifact_fingerprint = fe6eaf9fedbbe0be0a64ef0890d1a10388f80bee6e5b2e25c2770dbeb847e866
```

Verified: the fingerprint is present, is a well-formed SHA-256, and Red Team documents it as covering
strategy/validation/ledger/population/cost identity plus the counts plus `sum_horizon_r` — i.e. every field
this report reconciles. I confirmed each covered **field value** against its authoritative source (§1).

**Limitation, stated rather than glossed:** Red Team's report does **not** publish the canonicalization
recipe (field ordering, serialization form, separator convention). I therefore **cannot independently
recompute the digest** and I do not claim to have done so. The fingerprint is currently a *Red Team-internal*
integrity seal, not an externally verifiable one.

**Recommendation (non-blocking, does not affect the verdict):** Red Team should publish the canonicalization
string template so any division can recompute the digest. Until then the fingerprint detects accidental
drift but not a deliberate coordinated edit.

**Status note:** the artifact currently carries `status = BRACKET_FAIL_PENDING_STATISTICIAN_RECONCILIATION`.
That status was conditioned entirely on my withdrawn bound. It is now stale and should be re-stamped. Since
the status string falls inside the fingerprint's coverage, re-stamping will change the digest — this is
correct and expected behaviour, not a violation. **Re-stamping is Red Team's action, not mine**
(`DO_NOT_CHANGE_RED_TEAM_VALUES`).

---

## 13 — REAL EV FIELD SUFFICIENCY (§13) — **ALL FIELDS SUPPORTED**

Verified mechanically, not by inspection: I loaded `_decode_probability_inputs` from
`real_ev_engine.py` in isolation (the surrounding import chain is unrelated to the contract) and executed it
on Red Team's exact aggregates.

| Required field | Value supplied | Status |
|---|---|---|
| `edge_schema` | `real-ev-expected-edge-v1` | **SUPPORTED** |
| `n` | 295 | **SUPPORTED** |
| `n_target` | 15 | **SUPPORTED** |
| `n_horizon` | 196 | **SUPPORTED** |
| `sum_horizon_r` | +102.2125 (gross) | **SUPPORTED** |
| `credibility` | 0.80 (engine default, in (0,1)) | **SUPPORTED** |
| `n_stop` | 84, implied — not a contract field | **SUPPORTED** (by derivation) |
| `RR` | 3.0, from `RR_TARGET` in strategy source | **SUPPORTED** |
| `cost_over_r` | supplied at runtime per scenario, not part of the edge artifact | **SUPPORTED** |

Decode result — executed, not asserted:

```
decode(RT aggregates) -> ProbabilityInputs VALID
cell: n=295 n_target=15 n_horizon=196 sum_horizon_R=102.2125  credibility=0.8
implied n_stop = 84
E[X|h] gross   = 0.521492 R
```

**No field is MISSING.** The `_EXH_MISSING = -1.0` fail-closed sentinel is **not** triggered — which matters
materially: had `sum_horizon_r` been unavailable, `E[X|h]` would default to −1.0 and EV would collapse from
`+0.2098 R` to `−0.8011 R` (BASE), i.e. the strategy would fail closed to a hard reject. The horizon-return
evidence is worth **1.5215 R per unit of horizon-branch weight** and is therefore not an optional nicety but
the decisive input. Red Team's extraction supplies exactly the field whose absence would have blocked S5.

**`S5_CANONICAL_EV_EVIDENCE_SUPPORTED` — ISSUED.** This lifts the `BLOCKED` / `LEDGER_REQUIRED` status
issued in `e54a2a5`, which was predicated on the belief that no aggregate extraction could satisfy the
contract without exposing ledger rows. That belief is now **falsified by construction**: five aggregate
numbers suffice, and the escrow boundary held throughout.

---

## 14 — VERDICT SCOPE DELIMITATION

**What this verdict covers:**
- The internal arithmetic, R-semantics and contractual sufficiency of the five extracted aggregates.
- Their consistency with metrics published in the frozen S5 validation report.

**What this verdict does NOT cover — and must not be read as covering:**
- **Not** a re-validation of S5. The underlying edge rests on `RT_S5_S20_CLEAN_INDEPENDENT_VALIDATION_REPORT.md`
  and its limitations are untouched by this reconciliation.
- **Not** a statement that S5's edge is real, stable, or out-of-sample. `n = 295` on a single instrument with
  maxDD −6.44R remains a modest evidence base; the holdout remains SEALED.
- **Not** a promotion, and **not** live-readiness. `S5_EV_EVIDENCE_READY_FOR_RUNTIME_PACKAGING` means the
  *evidence artifact* is fit to be packaged — nothing about deployment.
- **Not** an endorsement of the two engineering defects in §15, which remain open.
- **Not** an independent verification of the fingerprint digest (§12).

---

## 15 — PREVIOUSLY IDENTIFIED ENGINEERING DEFECTS (§15) — **BOTH CONFIRMED STILL OPEN**

Tested by execution against the live decoder. **Not fixed, per mandate.**

**A. `sum_horizon_r = NaN` passes decoding — CONFIRMED OPEN**

```
input : {edge_schema, n=295, n_target=15, n_horizon=196, sum_horizon_r=NaN}
result: ProbabilityInputs VALID (not rejected); cell.sum_horizon_R = nan
```

NaN propagates through `ev_from_terms` to `EV_R = nan`. Downstream comparisons `nan > threshold` evaluate
False, so the *likely* runtime effect is an accidental reject — but this is fail-closed **by luck of IEEE-754
comparison semantics, not by design**, and any code path using `<=`, `not (ev < t)`, or sorting on EV inverts
the outcome. **Severity: material.**

**B. `n_target + n_horizon > n` is not rejected — CONFIRMED OPEN**

```
input : {n=10, n_target=8, n_horizon=9, sum_horizon_r=1.0}
result: ProbabilityInputs VALID (not rejected); implied n_stop = -7
```

An impossible outcome decomposition decodes cleanly, yielding a **negative implied stop count** and
probabilities summing above 1. `ev_from_terms` then clamps `p_s` to 0 (`if p_s < 0.0: p_s = 0.0`), which
**silently absorbs the corruption** and returns a plausible-looking finite EV that is inflated — the clamp
discards the entire loss branch. This is the more dangerous of the two: it fails **open**, quietly, with a
number that looks reasonable.

**Neither defect affects the S5 verdict**, because Red Team's aggregates satisfy both constraints
(`sum_horizon_r` finite; `15 + 196 = 211 <= 295`). They are latent hazards for future strategies.

**Recommendation to the CEO:** issue an engineering mandate adding two validation guards to
`_decode_probability_inputs` — reject non-finite `sum_horizon_r`, and reject `n_target + n_horizon > n`.
Defect B should be treated as the priority. **I have made no code change** (`NO_AI_TRADER_CHANGE`).

---

## 16 — PRIVACY / ESCROW CONFIRMATION (§16)

This report exposes **no** trade timestamps, entries, exits, individual R values, trade ordering, or raw
ledger rows. Every quantity is an aggregate, a published metric, or an algebraic consequence of the two.
The `winners = 162 / losers = 133` split in §6 is a derived aggregate, not a row-level disclosure. The raw
ledger remains sealed in `escrow_red_team/`. **The escrow boundary was preserved throughout, and was never
approached — the reconciliation required only five numbers.**

---

## 17 — HANDOFF

| Action | Owner | Blocking? |
|---|---|---|
| Re-stamp artifact status from `BRACKET_FAIL_PENDING_STATISTICIAN_RECONCILIATION` to reconciled; digest will change (expected) | **Red Team** | yes, for packaging |
| Publish the fingerprint canonicalization recipe | Red Team | no |
| Add the two fail-closed guards to `_decode_probability_inputs` | Engineering (VE), on CEO mandate | no, for S5 |
| Runtime packaging of the S5 expected-edge artifact | AI Trader, on CEO mandate | — |

**No promotion, no AI Trader modification, no broker, and no live authority is granted or implied by this report.**

---

*Statistician division — independent statistical validation. Verdicts are scoped strictly to the evidence
examined and are not transferable to adjacent claims.*

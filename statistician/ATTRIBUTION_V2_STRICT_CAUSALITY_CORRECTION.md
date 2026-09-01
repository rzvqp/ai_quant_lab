# ATTRIBUTION V2 — STRICT DECISION-TIME CAUSALITY CORRECTION

**Decision:** `CEO DECISION — V2 F029 CAUSALITY CORRECTION`. Final protocol correction. No research, no
outcome scoring.
**Division:** Statistician. **Date:** 2026-09-02.

```
V2_STRICT_CAUSALITY_CORRECTION_COMPLETE = YES
STRICT_DECISION_TIME_DRY_RUN = PASS
READY_FOR_ALPHA_V2_RESUME    = YES
```

**The CEO's ruling is the right one, and it is stricter than my frozen wording.** The V2 question is whether
a condition *known at the original trade decision* identifies a profitable subpopulation. `f029` needs the
next-bar fill, so it cannot answer that question no matter how outcome-free it is. "Available at trade
inception" was my reading; it is now closed, and I am not defending it.

---

## 1 — RECLASSIFICATION (§1)

```
f029 : ELIGIBLE_PRE_ENTRY  ->  AT_FILL_POST_DECISION

BARRED FROM: primary winner/loser attribution · pre-entry rescue search ·
             cross-family pre-entry recurrence · cross-mechanism pre-entry recurrence ·
             pre-entry meta-state discovery
RETAINED AS: a future EXECUTION / AT-FILL diagnostic only — not analysed in this mandate.
```

---

## 2 — THE OTHER TWO TRADE-LEVEL FEATURES, RE-VERIFIED (§2, §7)

Checked mechanically against the strict standard, not re-argued:

| f-ID | why it is available at the signal decision | `AVAILABLE_AT_SIGNAL_DECISION` |
|---|---|---|
| **`f045`** | it is a field of the setup dict emitted by `setups(d, h)`, which is evaluated **at the signal bar `si`**. Inspected across S1/S3/S5/S21/S48: the field is present in every setup, and `ei > si` in all of them, so nothing at or after the entry bar is consulted. | **YES** |
| **`f025`** | a **constant column of the frozen execution universe**, fixed before any trade exists; non-null for all 115 objects. It cannot depend on a bar at all. | **YES** |
| `f029` | requires the fill price (open of `si+1`) | **NO — excluded** |

```
STRICT_DECISION_TIME_FEATURES  = 45
AT_FILL_POST_DECISION_FEATURES = [f029]
```

**A correction to my previous report.** Its summary table listed `f025` as "the trade's committed direction"
and `f045` as "the execution-universe DIRECTION column". **Those two were transposed.** The shipped
`ATTRIBUTION_V2_TRADE_LEVEL_BLIND_FEATURE_SPEC.csv` has always been correct — `f025` is the execution-universe
constant, `f045` is the setup's committed direction — so Alpha's machine-readable input was never wrong and
no execution is affected. The prose was. Corrected here and in that report.

---

## 3 — RECOMPUTED BUDGET (§3)

The count enters **two** groups, so this is not one subtraction:

| group | before | after |
|---|---|---|
| **Stage 1** — features × analysis objects | 46 × 115 = **5,290** | **45 × 115 = 5,175** |
| **Stage 2** — recurrence, one per feature | **46** | **45** |
| **Stage 3** — interactions (hard cap) | **20** | **20** — unchanged |
| **TOTAL_DECLARED_TESTS** | **5,356** | **5,240** |

`5,356 − 115 − 1 = 5,240`. Stage 3 is defined on *ranks* (the 10 pairs among the top-5, plus each top-5
crossed with ranks 6–10), not on the feature count, so it is unaffected while at least 10 eligible features
exist — 45 ≥ 10.

```
MULTIPLICITY_METHOD = hierarchical, unchanged in form; denominators updated
  stage 1 : BH-FDR, q = 0.05, m = 5,175
  stage 2 : Bonferroni, m = 45
  stage 3 : Bonferroni, m = 20
  reference bound : Bonferroni over all 5,240 requires |z| > 4.43

MULTIPLICITY_DENOMINATORS = {stage1: 5175, stage2: 45, stage3: 20, reference: 5240}
```

The recurrence criteria are unchanged in form (≥ 5 distinct `SOURCE_FAMILY_ID` **and** ≥ 3 distinct
`MECHANISM_ID`, same sign, ≥ 0.05R, 2-of-3 chronological thirds); only the stage-2 Bonferroni denominator
moves 46 → 45.

---

## 4 — ELIGIBILITY LIST, MACHINE-ENFORCED (§4, §5)

```
attribution_v2_handoff/ATTRIBUTION_V2_STAGE1_ELIGIBLE_FEATURES.csv
STAGE1_ELIGIBLE_FEATURE_LIST_HASH = 8a629d7d536f05958049f6e4a2ec50be46fd3c11984ae844e250f6191e074a99
```

46 rows — every f-ID with `STAGE1_ELIGIBLE ∈ {0,1}`, `ELIGIBILITY_CLASS`, `KIND`, `N_BINS`, `SOURCE`, and for
`f029` an explicit `NOTE` naming every stage it is barred from. **45 eligible, 1 excluded.**

**The matrix was deliberately not rebuilt.** It still physically carries 46 f-IDs and its hash is unchanged
(`2ea066c6…`), exactly as §4 permits. Eligibility is carried by the list, not by which columns happen to
exist:

> **Execution contract.** Alpha selects Stage-1 columns **by loading the eligibility list**, never by
> enumerating the matrix. `FEATURE_MATRIX_COLUMNS = 46`, `PRIMARY_SCORING_FEATURES = 45`. Scoring `f029`
> accidentally requires ignoring a file whose only purpose is to forbid it.

**The core package is untouched by design.** `FEATURE_ELIGIBILITY_TABLE.csv` inside
`attribution_v2/` still lists 46 as `ELIGIBLE_PRE_ENTRY`; editing it would break `PROTOCOL_CORE_HASH`, which
the CEO restated as authoritative. The Stage-1 eligibility list is therefore the **later and governing**
artifact for `f029`, and this document is the record of precedence. `PROTOCOL_CORE_HASH` remains
`4488f0e8…`.

---

## 5 — BLINDING (§6)

No additional semantics were revealed. The decision used only the already-disclosed fact that `f029` depends
on the fill price. `f025` and `f045` were already disclosed in the trade-level spec, which was necessary for
Alpha to compute them at all. **The other 43 remain blind.** Status unchanged:
`PRESERVED_WITH_DISCLOSED_PARTIAL_LEAKAGE`.

---

## 6 — DRY RUN (§8)

Alpha's own load path, simulated end to end — execution universe → value matrix → eligibility list → Stage-1
frame. **No outcome column was loaded and the fill price was never read.**

| object | trades | columns | joined | availability | bins within declared | `f029` in frame |
|---|---|---|---|---|---|---|
| `S1::4b7c6d5c6035` | 11,881 | **45** | 11,881 | 0.888 | ✓ | **False** |
| `S5::15be26301532` | 22,089 | **45** | 22,089 | 0.891 | ✓ | **False** |
| `S21::6ddb75c3f9b1` | 15,504 | **45** | 15,504 | 0.890 | ✓ | **False** |
| `S48::6d74b2000433` | 15,355 | **45** | 15,355 | 0.864 | ✓ | **False** |

Every frame has exactly 45 columns · every trade joins 1:1 · every observed bin index is inside its declared
range · `f029` appears in no frame · no `open[ei]` access anywhere in the run.

```
STRICT_DECISION_TIME_DRY_RUN = PASS
```

---

## 7 — FINAL AUTHORITATIVE HANDOFF (§9)

```
V2_STRICT_CAUSALITY_CORRECTION_COMPLETE = YES

STRICT_DECISION_TIME_FEATURES = 45
EXCLUDED_AT_FILL_FEATURES     = [f029]

STAGE1_TESTS               = 5,175   (45 x 115)
FINAL_TOTAL_DECLARED_TESTS = 5,240   (5,175 + 45 + 20)
MULTIPLICITY_DENOMINATORS  = {stage1: 5175, stage2: 45, stage3: 20, reference: 5240}

STAGE1_ELIGIBLE_FEATURE_LIST_HASH = 8a629d7d536f05958049f6e4a2ec50be46fd3c11984ae844e250f6191e074a99
PROTOCOL_CORE_HASH                = 4488f0e89ae8bb079bf51eb74e4a2767f072d4e368ee383bae1d875ac4359b8f
BLINDED_FEATURE_VALUES_HASH       = 2ea066c6a6a75705d7429ed9ad982430f1bfd02c5242760d43cf8f363cc7e871
TRADE_LEVEL_BLIND_FEATURE_SPEC_HASH = 03e636639012cd3e4edc6925c2b0f6c568941c7cb8060cf23ed896c7c711b4e2

STRICT_DECISION_TIME_DRY_RUN = PASS
READY_FOR_ALPHA_V2_RESUME    = YES
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

No research, no outcome scoring, no winner/loser split, no bucket searched. The blind key and the semantic
builders remain outside every repository. Not touched: **S5, Q4, AI Trader, P007, MGMT-004, MT5,
StrategyCatalog.**

# ATTRIBUTION V2 — IDENTITY RECONCILIATION ADDENDUM

**Request:** `ATTRIBUTION V2 IDENTITY RECONCILIATION` — correction / addendum only. No attribution run, no
scientific change beyond what the identity error requires.
**Division:** Statistician. **Date:** 2026-09-02.
**Amends:** `STRATEGY_ATTRIBUTION_V2_PROTOCOL_FREEZE.md` (commit `e97fe8d`).

## VERDICT

```
ATTRIBUTION_V2_IDENTITY_RECONCILED = YES
MANIFEST_HASH_STILL_VALID          = YES
MANIFEST_REQUIRES_REVISION         = NO
TEST_BUDGET_REQUIRES_CHANGE        = NO
```

**The 104 → 115 gap is real bookkeeping, not a universe expansion — but the freeze report failed to state
it, and that is a genuine reporting defect on my part.** `115` was printed under the label
`ATTRIBUTION_FAMILIES`, which is wrong: **115 is an analysis-object count, not a family count.** The label
is corrected here and in the amended protocol.

---

## 1 — THE EXACT ACCOUNTING IDENTITY (§1)

```
   104   attribution-eligible objects in the frozen manifest
 -  43   S-library SOURCE FAMILIES        (removed: replaced by representatives)
 +  56   S-library REPRESENTATIVE VARIANTS (13 families direction-split -> 26; 30 unsplit -> 30)
 -   2   factory PARENT rows              (removed: duplicates of children already counted)
 = 115   ANALYSIS OBJECTS
```

Verified against `ATTRIBUTION_UNIVERSE_V2.csv`: **115 rows — CONSISTENT.**

**The two dropped parents, named explicitly** (this is the part the freeze report omitted):

| dropped parent | its children, already present as Block-C objects |
|---|---|
| `OB_CAUSAL_EXECUTION_FACTORY_V1` | `OBR_A_limit`, `OBEXEC_B`, `OBEXEC_C`, `OBEXEC_D` |
| `SESSION_SPECIALIST_FACTORY_V1` | `SESS_A`, `SESS_B`, `SESS_C`, `SESS_D`, `SESS_E`, `SESS_Fc` |

10 of the 14 Block-C objects are the children of those two factory rows. Keeping both would double-count
those 10 trade populations. The de-duplication was performed in code but **not documented** — that omission
is exactly what made 104 → 115 unexplainable, and it is corrected here.

### Corrected vocabulary

```
SOURCE_ATTRIBUTION_FAMILIES = 102   distinct real families behind the execution universe
                                     (104 eligible - 2 duplicate parents)
ANALYSIS_OBJECTS            = 115   what Alpha actually runs (the test-budget unit)
REPRESENTATIVE_VARIANTS     =  56   S-library representatives only
DIRECTIONAL_SPLIT_OBJECTS   =  26   from 13 families -> a net addition of +13 objects
FINAL_DISTINCT_MECHANISMS   =  25   unchanged
```

**A representative is not a family and is never counted as one.** `S1::4b7c6d5c6035` and
`S1::11c4710e404e` are two analysis objects, one source family, one mechanism.

---

## 2 — NO SILENT UNIVERSE EXPANSION (§2)

```
distinct source families behind the 115 analysis objects : 102
of those, absent from the frozen manifest                :   0
MANIFEST_REQUIRES_REVISION = NO
MANIFEST_HASH = 433f1cecbbae20e1d27ce9dc47b604d5258e36702881973a0e7f5fa032a440d9   (unchanged, re-verified)
```

Every source family in the execution universe is an `OBJECT_ID` already present in the frozen manifest. **No
family was added.** The count rose only because 43 families expand into 56 representatives, and fell by 2
where parent rows duplicated their children.

---

## 3 — 56 / 57 / 58 RECONCILED (§3)

These are **three different populations**, and the freeze report used all three without distinguishing them:

```
TOTAL_REPRESENTATIVES_GENERATED = 58   all 45 implemented families
                                        = 32 unsplit x1  +  13 direction-split x2
TOTAL_REPRESENTATIVES_EXPECTED  = 58   the same 58, checked against the frozen result set
TOTAL_REPRESENTATIVES_FOUND     = 57
TOTAL_REPRESENTATIVES_MISSING   =  1
TOTAL_REPRESENTATIVES_DECLARED  = 56   what Alpha receives (58 minus the 2 INVALID families)
```

**Missing representative — the complete list, one entry:**

| family | representative id | rule | reason |
|---|---|---|---|
| `S49` | `9430e30451e1` | `GRAMMAR_INDEX_0` | S49 has **no results parquet at all**, consistent with its documented INVALID status (non-selective / non-discrete signal). It is excluded from the shipped set on independent grounds, so the absence changes nothing. |

**Does direction splitting create the 58?** Yes, in part: 32 + (13 × 2) = 58. Without splitting there would
be 45. The two excluded INVALID families (`S47` n<25, `S49` non-selective) each contribute one, giving the
shipped **56**.

---

## 4 — EXECUTION UNIVERSE, FROZEN (§4)

`statistician/attribution_v2/ATTRIBUTION_V2_EXECUTION_UNIVERSE.csv` — 115 rows, one per analysis object:

```
ANALYSIS_OBJECT_ID · SOURCE_FAMILY_ID · MECHANISM_ID · REPRESENTATIVE_VARIANT_ID · DIRECTION · SOURCE_TYPE · TIER
```

Integrity assertions, all passed: object ids unique · zero unmapped mechanisms · 102 distinct source
families · 25 mechanisms.

| | |
|---|---|
| direction | `BOTH` 89 · `LONG` 13 · `SHORT` 13 |
| source type | `S_LIBRARY_REPRESENTATIVE` 56 · `REGENERATE_EDGERESEARCH` 25 · `LOG_EXISTS` 14 · `REGENERATE_FACTORY` 14 · `REGENERATE_FROZEN_SPEC` 6 |

`DIRECTION = BOTH` means the object's grammar declares **no** direction dimension, so the setup logic
determines side per trade. It does not assert design symmetry, and `SOURCE_TYPE` disambiguates.

```
EXECUTION_UNIVERSE_HASH = 78ea539fe2f6731e5a3dc482220591133d9fc06a3585fb998791bb882839f150
```

---

## 5 — DENOMINATOR RULES, FROZEN (§5)

Binding on every coverage or recurrence statistic V2 produces:

| statistic | numerator | **denominator** | rule |
|---|---|---|---|
| `FAMILY_COVERAGE` | distinct `SOURCE_FAMILY_ID` analysed | **102** | LONG and SHORT representatives of one family are **ONE** family |
| `OBJECT_COVERAGE` | `ANALYSIS_OBJECT_ID` analysed | **115** | the only statistic where representatives count individually |
| `MECHANISM_COVERAGE` | distinct `MECHANISM_ID` analysed | **25** | parameter variants and direction splits are **never** independent mechanisms |

Additional binding rules:

1. **`FAILED_REGENERATION` objects stay in every denominator.** A coverage figure computed over "what
   loaded" is not a coverage figure — the V1 failure.
2. **The §16 recurrence criteria count families and mechanisms, not objects.** "Supported in ≥ 5 distinct
   families **and** ≥ 3 distinct mechanisms" means **distinct `SOURCE_FAMILY_ID`** and **distinct
   `MECHANISM_ID`**. Five analysis objects drawn from three families do **not** satisfy it. This was
   ambiguous in the freeze report and is now closed — it is the one place where the 104/115 confusion could
   have inflated a scientific claim rather than just a header.
3. **Direction findings must state their unit.** "LONG loses less than SHORT" computed over the 26
   direction-split objects is a statement about 13 families, and must be reported as such.

---

## 6 — TEST BUDGET (§6)

```
declared stage-1 tests in the frozen package : 5,290
46 features x 115 analysis objects           : 5,290    -> CONSISTENT
(46 x 104 = 4,784 · 46 x 56 = 2,576 — neither was used)

TEST_BUDGET_REQUIRES_CHANGE = NO
FINAL_TOTAL_DECLARED_TESTS  = 5,356   (5,290 + 46 recurrence + 20 interactions)
```

The budget was computed on **analysis objects**, which is the correct unit: one test per (object, feature).
The identity correction renames the quantity; it does not change it. The multiplicity policy therefore
stands unmodified.

---

## 7 — WHAT CHANGED IN THE PACKAGE

One file added — `ATTRIBUTION_V2_EXECUTION_UNIVERSE.csv` — as §4 requires. **No scientific content was
altered:** the universe membership, representative rule, mechanism map, feature schema, binning, budget,
multiplicity policy, placebo protocol, post-entry eligibility and reuse policy are byte-identical to the
freeze. Adding a file necessarily re-hashes the package:

```
PROTOCOL_PACKAGE_HASH (superseded) = 62852d36844d4eee8a48eec85f4102c4e1b12b4e3e039fa38272ca4f25cf8bf2
PROTOCOL_PACKAGE_HASH (current)    = 4488f0e89ae8bb079bf51eb74e4a2767f072d4e368ee383bae1d875ac4359b8f
FEATURE_MAP_HASH                   = 6cddeef6371fb42da7e4db5f5f936b7451727fae8673cc4414d5ab282ab5e943  (unchanged)
BLIND_KEY_HASH                     = 268a4f1878ff15df81adba165f1786d320c15b62a148327f440eb3cf293f146f  (unchanged)
```

---

## 8 — FINAL GATE

```
ATTRIBUTION_V2_IDENTITY_RECONCILED = YES
MANIFEST_HASH_STILL_VALID          = YES
MANIFEST_HASH                      = 433f1cecbbae20e1d27ce9dc47b604d5258e36702881973a0e7f5fa032a440d9

SOURCE_ATTRIBUTION_FAMILIES = 102
ANALYSIS_OBJECTS            = 115
REPRESENTATIVE_VARIANTS     = 56
DIRECTIONAL_SPLIT_OBJECTS   = 26  (13 families)
FINAL_DISTINCT_MECHANISMS   = 25

EXECUTION_UNIVERSE_HASH = 78ea539fe2f6731e5a3dc482220591133d9fc06a3585fb998791bb882839f150
PROTOCOL_PACKAGE_HASH   = 4488f0e89ae8bb079bf51eb74e4a2767f072d4e368ee383bae1d875ac4359b8f

FINAL_TOTAL_DECLARED_TESTS = 5,356
TEST_BUDGET_REQUIRES_CHANGE = NO

READY_FOR_ALPHA_ATTRIBUTION_V2 = YES
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

**Defect owned.** The freeze report labelled an object count as `ATTRIBUTION_FAMILIES` and used 56/57/58
interchangeably without saying they were different populations. Neither error changed a number Alpha would
have computed — the budget and the universe file were always built on 115 objects — but the recurrence
criteria in §16 were stated in terms of "families" while the shipped universe was in objects, and that
**could** have inflated a scientific claim if Alpha had counted direction splits as independent families.
Rule 2 in §5 closes it.

No attribution was run. No outcome was read. Not touched: **S5, Q4, AI Trader, P007, MGMT-004, MT5,
StrategyCatalog.**

# ATTRIBUTION V2 — BLINDED FEATURE VALUE HANDOFF

**Mandate:** `ATTRIBUTION V2 BLINDED FEATURE VALUE HANDOFF` — data handoff only. No attribution, no outcome
scoring, no unblinding.
**Division:** Statistician. **Date:** 2026-09-02.

**Alpha's stop was correct.** The freeze package declared 46 features, their bins and their eligibility, but
never contained the values. I declared the feature set and never computed it. That is my gap, and this
artifact closes it.

```
ATTRIBUTION_V2_BLINDED_FEATURE_HANDOFF_COMPLETE = YES
FEATURE_CAUSALITY_AUDIT  = PASS
TRADE_FEATURE_JOIN_AUDIT = PASS
PROTOCOL_CHANGE_REQUIRED = NO
READY_FOR_ALPHA_V2_RESUME = YES
```

---

## 1 — FROZEN IDENTITIES RE-VERIFIED (§1)

All five recomputed from the artifacts on disk — **every one MATCHES**:

| identity | value | |
|---|---|---|
| `MANIFEST_HASH` | `433f1cec…a440d9` | **MATCH** |
| `EXECUTION_UNIVERSE_HASH` | `78ea539f…39f150` | **MATCH** |
| `PROTOCOL_PACKAGE_HASH` (pre-handoff) | `4488f0e8…59b8f` | **MATCH** (12 files) |
| `FEATURE_MAP_HASH` | `6cddeef6…5e943` | **MATCH** |
| `BLIND_KEY_HASH` | `268a4f18…f146f` | **MATCH** |

No feature identity, bin, or protocol rule was changed.

---

## 2 — THE ARTIFACT (§2, §11)

```
statistician/attribution_v2_handoff/ATTRIBUTION_V2_BLINDED_FEATURE_VALUES.parquet     14.4 MB
statistician/attribution_v2_handoff/ATTRIBUTION_V2_BLINDED_FEATURE_VALUES_METADATA.csv
statistician/attribution_v2_handoff/ATTRIBUTION_V2_BLINDED_FEATURE_HANDOFF_MANIFEST.json
statistician/attribution_v2_handoff/ATTRIBUTION_V2_TRADE_LEVEL_BLIND_FEATURE_SPEC.csv
```

| | |
|---|---|
| **FEATURE_VALUE_ROWS** | **355,696** |
| **FEATURE_VALUE_COLUMNS** | **50** (4 keys + 46 blinded features) |
| keys | `PANEL_ID`, `BAR_INDEX`, `BAR_OPEN_TIME`, `BAR_CLOSE_TIME` |
| panel | `XAUUSD_M15_MSTRAT_HISTORICAL` — `htf_context_historical.load_mstrat_historical()` |
| coverage | 2011-07-26T16:30Z → 2026-07-27T16:15Z |
| timezone | UTC unix seconds; `BAR_CLOSE_TIME = BAR_OPEN_TIME + 900` |
| dtype | `Int8` (nullable) |

**Panel choice, and why it is not a protocol change.** The ratified gap-safe loader
`load_mstrat_historical()` returns **byte-identical columns and identical non-HTF values** to `mstrat.load()`,
but carries the Statistician-ratified `*_from_M15_v2` HTF/PDH context, lifting that context's coverage from
**23.7% → 55.4%** of the panel. It is the same feature definitions on a better-covered source, which is
strictly more data for the frozen features — not a redefinition.

**Values are delivered as FROZEN BIN INDICES, not raw values.** Numeric features carry their quintile index
0–4 from the frozen rule (trailing-2000-bar causal percentile rank); booleans 0/1; categoricals their
declared level index. This is a deliberate enforcement property: **Alpha cannot scan thresholds, because it
never receives a threshold.** §12's prohibition on threshold scanning becomes structural rather than
advisory.

---

## 3 — CAUSALITY AUDIT (§3) — mechanical, not asserted

**Method: the truncation test.** Rebuild the entire feature *and* binning pipeline on a panel truncated at
bar *K*, then compare the value at bar *K−1* against the full-panel value at the same bar. Any use of a
future bar changes it.

```
truncation points : 120,000 · 240,000 · 330,000
comparisons       : 43 panel features x 3 = 129
MISMATCHES        : 0
```

| criterion | result | basis |
|---|---|---|
| `NO_FUTURE_BAR` | **PASS** | truncation test, 0/129 |
| `NO_LOOKAHEAD_NORMALIZATION` | **PASS** | every rank is `rolling(2000).shift(1)`; no full-sample rank anywhere |
| `NO_OUTCOME_INFORMATION` | **PASS** | no R/PnL/win/exit column read or produced |
| `NO_EVENTUAL_EXIT` | **PASS** | same |
| `NO_MFE_MAE_LEAKAGE` | **PASS** | same |
| `NO_FUTURE_SWING` | **PASS** | all extremes are trailing rolling windows |

**One lookahead I found and fixed while building.** The declared feature "bars remaining in the session
block" would have been trivially computed as *block length − position*, but a block's length is only known
when the block **ends**. It is implemented instead from the **previous completed block's** length. The
truncation test now passes on it; computed the obvious way it would not have.

`FEATURE_CAUSALITY_AUDIT = PASS`

---

## 4 — NO OUTCOMES (§4)

The artifact contains **no** column other than the four keys and `f001…f046`. Verified mechanically:
`outcome-like columns in the artifact : NONE`. No R, PnL, win/loss, PF, MFE, MAE, exit reason, future
return, target/stop result, expectancy or ranking exists in the file or in the builder's read path.

---

## 5 — JOIN INTEGRITY (§7)

```
BAR_INDEX unique          : True        BAR_OPEN_TIME unique : True
strictly increasing       : True        PANEL_ID distinct    : 1
5,000 dummy trades joined : 5,000 / 5,000, 0 unmatched, validated many_to_one
key alignment spot-check  : PASS
TRADE_FEATURE_JOIN_AUDIT  = PASS
```

**The join rule is a causality requirement, not a convenience — Alpha must follow it exactly:**

> **Join each trade on its DECISION bar.** For M15-native objects that is the **signal bar index**
> (`si`), *not* the entry bar. The engine fills at `si+1` open, so the entry bar's own high/low is not
> known at the decision. For any object whose decision time is not an M15 boundary (M5-native, daily-anchor,
> sub-bar), use a **backward as-of join on `BAR_CLOSE_TIME ≤ decision_time`** — the convention this codebase
> already ratified. **Never join on the entry bar.**

This preserves `FEATURE_STATE_AT_DECISION → TRADE_DECISION → FUTURE_OUTCOME`. Joining on the entry bar
would invert it.

---

## 6 — COVERAGE (§8)

```
OBJECTS_FEATURE_COVERED = 115
OBJECTS_FEATURE_PARTIAL = 0
OBJECTS_FEATURE_BLOCKED = 0
source families covered = 102 / 102        mechanisms covered = 25 / 25
```

**Partiality here is per-FEATURE, not per-object**, and it is recorded rather than imputed:

| | |
|---|---|
| panel features with ≤1% missing | **33 of 43** |
| median missingness across panel features | **0.15%** |
| features with >20% missing | **10** — `f009 f012 f018 f020 f023 f024 f031 f035 f042 f046` |
| cause | the ratified `*_from_M15_v2` HTF/level context exists only inside the four ratified discovery blocks; outside them the value is a **recorded absence**, never filled |
| trade-record columns | **3** — see §7 |

Per the frozen protocol, a feature absent for an object is `NOT_AVAILABLE_FOR_FAMILY` and must be
**reported per (object, feature)**, never silently dropped from a denominator.

---

## 7 — THREE FEATURES CANNOT LIVE ON A PER-BAR PANEL

`f025`, `f029`, `f045` are **trade-level**: they are properties of the trade, not of the bar, so no per-bar
matrix can carry them. They ship as declared `SOURCE = TRADE_RECORD` null columns, and **Alpha populates
them from its own regenerated trade record**, which already contains everything required.

The alternative — materialising them per (object, trade) — would mean millions of redundant rows, which
§11 explicitly forbids. This is the correct trade-off, and it costs one disclosed unit of blinding (§8).

---

## 8 — BLINDING AUDIT (§9)

```
BLINDING_STATUS = PRESERVED_WITH_DISCLOSED_PARTIAL_LEAKAGE
```

Alpha receives `f001…f046`, `KIND`, `N_BINS`, `VALID_N`, `MISSING_N`, `BIN_COUNTS`, `SOURCE`. **No true
name, no description, no source variable name.** The blind key, the name→id map and the semantic builder
remain outside every repository. A full leak scan of the shipped package returns clean apart from the
`BLIND_KEY_HASH`, which is published deliberately so the map can be verified as fixed in advance.

**Three leakage channels, all declared. I am not claiming perfect blinding.**

1. **Unique bin counts** *(pre-existing, unchanged)* — 4 features carry a bin count no other feature has and
   are identifiable from the binning table: `f011`, `f017`, `f019`, `f039`. Alpha needs bin counts to run.
2. **Trade-record marking** *(new, forced by delivery)* — `f025`, `f029`, `f045` are visibly trade-level
   rather than bar-level. Unavoidable: Alpha cannot populate them otherwise.
3. **Missingness pattern** *(new, inherent to any value matrix)* — the 10 block-limited features are
   visibly one coherent context group.

**7 of 46 features are touched by some channel; 39 remain fully blind**, and no channel reveals a feature's
actual name or economic meaning.

---

## 9 — PLACEBO READINESS (§10)

```
PLACEBO_INPUT_READY = YES
```

| frozen placebo | requirement | met by |
|---|---|---|
| `OUTCOME_SHUFFLE_WITHIN_BLOCK` | (object × calendar-month) blocks | `BAR_OPEN_TIME` |
| `FEATURE_ASSIGNMENT_SHUFFLE` | full feature vector per trade | all 46 columns |
| `SYNTHETIC_POSITIVE_CONTROL` | an injectable top bin per feature | bins are explicit `0…k−1` |

I did not run them. They are Alpha's, and they gate its interpretation.

---

## 10 — NO PROTOCOL CHANGE (§13)

```
PROTOCOL_CHANGE_REQUIRED = NO
```

Unchanged and byte-identical: feature map, blind key, execution universe, representative map, mechanism map,
search budget, multiplicity policy, recurrence criteria, rescue thresholds, placebo design, binning,
eligibility table, historical-reuse policy.

Three files were **added**. Adding files necessarily re-hashes the package directory:

```
PROTOCOL_CORE_HASH = 4488f0e89ae8bb079bf51eb74e4a2767f072d4e368ee383bae1d875ac4359b8f  (12 files, UNCHANGED)

CORRECTED 2026-09-02: an earlier revision of this section reported a NEW package hash (36e07fb7...)
because the handoff artifacts had been written INTO the identity-bearing directory. That was a
bookkeeping error, not a protocol change. The artifacts now live in statistician/attribution_v2_handoff/
and the protocol core keeps its frozen identity. 36e07fb7... is WITHDRAWN.
See ATTRIBUTION_V2_FINAL_HANDOFF_INTEGRITY.md.
```

---

## 11 — FINAL

```
ATTRIBUTION_V2_BLINDED_FEATURE_HANDOFF_COMPLETE = YES

FEATURE_CAUSALITY_AUDIT  = PASS   (0 mismatches / 129 truncation comparisons)
TRADE_FEATURE_JOIN_AUDIT = PASS   (5,000/5,000 dummy joins, many_to_one validated)

BLINDED_FEATURES      = 46        (43 panel-sourced + 3 trade-record)
FEATURE_VALUE_ROWS    = 355,696
FEATURE_VALUE_COLUMNS = 50

OBJECTS_FEATURE_COVERED = 115     OBJECTS_FEATURE_PARTIAL = 0     OBJECTS_FEATURE_BLOCKED = 0

BLINDING_STATUS      = PRESERVED_WITH_DISCLOSED_PARTIAL_LEAKAGE
PLACEBO_INPUT_READY  = YES
PROTOCOL_CHANGE_REQUIRED = NO

BLINDED_FEATURE_VALUES_HASH           = 2ea066c6a6a75705d7429ed9ad982430f1bfd02c5242760d43cf8f363cc7e871
BLINDED_FEATURE_HANDOFF_MANIFEST_HASH = 16dbe9632f05f0409aebc01c7060773862c8cf365051b3a78b481c62599a81fa
PROTOCOL_CORE_HASH                    = 4488f0e89ae8bb079bf51eb74e4a2767f072d4e368ee383bae1d875ac4359b8f

READY_FOR_ALPHA_V2_RESUME = YES
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

No attribution was run, no winner/loser scored, no strategy outcome inspected, no semantics unblinded.
Not touched: **S5, Q4, AI Trader, P007, MGMT-004, MT5, StrategyCatalog.**

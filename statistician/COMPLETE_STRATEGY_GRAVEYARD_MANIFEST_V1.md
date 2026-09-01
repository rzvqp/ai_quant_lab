# COMPLETE_STRATEGY_GRAVEYARD_MANIFEST_V1

**Mandate:** `COMPLETE_STRATEGY_GRAVEYARD_MANIFEST_V1` — provenance and inventory only. No edge search, no
attribution, no winner/loser analysis, no rescue-condition testing.
**Division:** Statistician. **Date:** 2026-09-02.
**Artifacts:** `COMPLETE_STRATEGY_GRAVEYARD_MANIFEST_V1.csv` (120 rows) · this file ·
`ALPHA_ATTRIBUTION_V1_COVERAGE_AUDIT.md` · builder `statistician/graveyard/{build.py, cov.py}`.

```
MANIFEST_HASH = 433f1cecbbae20e1d27ce9dc47b604d5258e36702881973a0e7f5fa032a440d9
```

---

## 1 — HEADLINE

**Alpha V1 did not analyse the strategy graveyard. It analysed the four generator modules that happened to
be importable from its own working directory.**

`attr_run.py:8` imports exactly `ob_core`, `ob_exec`, `htf_setups`, `sess_core`, `sess_scan` — and nothing
else. Those five modules produce all 14 objects. **Zero of the 51-family Executable Strategy Library is
present.** That library is the largest, most rigorously audited body of trade-generating research this lab
owns: 45 implemented families, **2,432 variants**, every one of them smoke-tested with
`lookahead_safe=True` and `ledger_ok=True`, and its `simulate()` emits a per-trade ledger (`R`, `si`, `ei`).

```
COVERAGE_BY_FAMILY             = 13.5%   (14 of 104 attribution-eligible objects)
COVERAGE_BY_DISTINCT_MECHANISM = 23.1%   (6 of 26)
COVERAGE_BY_VALID_TRADES       = 27.9%   (30,703 of ~110,000 readily available)
```

The CEO's suspicion is confirmed by the import statement.

---

## 2 — CONTROL TOTALS RECONCILED (§3)

The historical inventory reported ~51 families / ~2,300 variants / 45 implemented / 2 invalid / 6 blocked on
external data. Every one of those numbers reconciles against the artifacts:

| control total | current verified state | source |
|---|---|---|
| 51 numbered families S1–S51 | **51** — S1…S51, no gaps in the numbering | `strategy_library_metadata.py` + `mstrat_ext.py` |
| 45 implemented | **45** entries in `META` (S1–S31, S38–S51) | `strategy_library_metadata.py` |
| ~2,300 variant hypotheses | **2,432** (core S1–S20 = 1,972; ext S21+ = 460) | `results/FAMILY_RESULTS.parquet` + `results/ext_families/` |
| 2 invalid | **2** — **S47** (n<25, too-rare) and **S49** (non-selective / non-discrete) | `build_strategy_library.py:318`, `docs/MECHANISM_DIVERSITY_LOG.md:56` |
| 6 not implemented (external data) | **6** — **S32–S37** (intermarket, cross-asset lead-lag, rates, COT, macro-event, sentiment/flow) | `strategy_library_metadata.py:383-388` |

**Two refinements the old totals did not capture, both verified:**

- **44 families have a results parquet, not 45.** S49 has none — consistent with it being invalid
  (non-discrete signal, nothing to score). **S47 does have one** (12 variants) despite being flagged
  invalid; its defect is population size, not implementation. Both are carried in the manifest with
  `STATUS = INVALID` and an exact reason, not omitted.
- **2,432 > ~2,300.** The old figure predates the S38–S51 batch. Per mandate §3, the current total is
  reported as found; it is not forced to match.

---

## 3 — THE UNIVERSE (§5, §15)

```
TOTAL_OBJECTS_DISCOVERED         = 120
TOTAL_FAMILIES                   = 120  (family-level objects; 51 S-library + 69 later/other)
TOTAL_VARIANTS                   = 2,446  (2,432 S-library + 14 one-variant factory objects)
TOTAL_DISTINCT_MECHANISMS        = 27     (26 among attribution-eligible objects)

VALID_CAUSAL_FAMILIES            = 104   (attribution class A or B)
VALID_TRADE_LOG_FAMILIES         = 16    (class A — a trade log exists today)
CAUSALLY_REGENERATABLE_FAMILIES  = 88    (class B — frozen spec + callable generator, no log yet)
INFORMATION_ONLY_FAMILIES        = 5
INVALID_FAMILIES                 = 4
SUPERSEDED_FAMILIES              = 1     (OBR fill-artifact -> OB_CAUSAL_EXECUTION_FACTORY_V1)
DATA_BLOCKED_FAMILIES            = 7     (S32-S37 external data + GOLD_ORDER_FLOW_DISCOVERY_V1)
NOT_IMPLEMENTED                  = 6     (S32-S37, counted above)
VALIDATED                        = 2     (S5, RANGE_LIFECYCLE_V4_4)
NEAR_MISS                        = 3
```

### Blocks

| block | contents | objects |
|---|---|---|
| **A** | Executable Strategy Library S1–S51 (ENGINE v2) | **51** |
| **B** | post-S51 named Alpha factories / frontiers | **21** |
| **C** | the 14 objects Alpha V1 actually analysed | **14** |
| **D** | frozen / independently-reviewed candidates | **9** |
| **E** | `edge_research` E-series and candidate series | **25** |

### Mechanism taxonomy (§10) — derived from the project, not imposed

Derived by collapsing the library's own `klass` labels (44 distinct strings) plus the later factories:

```
M01_LIQUIDITY_SWEEP  M02_FAILED_BREAKOUT_FADE  M03_BREAKOUT_RETEST
M04_VOLATILITY_COMPRESSION_EXPANSION  M05_OPENING_RANGE  M06_SESSION_TIME
M07_TREND_CONTINUATION  M08_EXTENSION_MEAN_REVERSION  M09_MTF_ALIGNMENT
M10_DISPLACEMENT_CONTINUATION  M11_STRUCTURE_BREAK_REVERSAL  M12_RANGE_ROTATION
M13_IMBALANCE_FVG  M14_REFERENCE_LEVEL  M15_GAP  M16_AUCTION_VALUE
M17_VOLUME_PARTICIPATION  M18_OSCILLATOR_DIVERGENCE  M19_SEQUENCE_RUNLENGTH
M20_CANDLESTICK_PATTERN  M21_META_ROUTER  M22_EXOGENOUS_DATA (S32-S37, not implemented)
M23_CROSS_MARKET  M24_EVENT_REVEALED_RESPONSE  M25_DIRECTION_AGNOSTIC_OCO
M26_CONTRAST_MINING  M27_EDGE_RESEARCH_PATTERN  M99_UNCLASSIFIED
```

Largest classes: `M06_SESSION_TIME` (17), `M14_REFERENCE_LEVEL` (10), `M04_VOLATILITY_COMPRESSION_EXPANSION`
(8), `M07_TREND_CONTINUATION` (7).

**A limitation I am flagging rather than hiding.** `M27_EDGE_RESEARCH_PATTERN` currently holds all **25**
`edge_research` families as one bucket. Those modules carry no `klass` metadata, so classifying them to
real economic mechanisms requires reading 25 files individually — out of scope for a provenance pass. The
manifest therefore **understates** mechanism diversity in Block E, and `TOTAL_DISTINCT_MECHANISMS = 27`
should be read as a **floor**. Decomposing M27 is the one piece of inventory work still outstanding.

---

## 4 — FAMILY ≠ VARIANT (§4)

The mapping is recoverable and is carried in the CSV:

```
VARIANT_ID  ->  FAMILY_ID  ->  MECHANISM_ID
```

- For Block A the variant grammar is explicit: e.g. **S1 = 1,152 grammar points → 60 signal hypotheses**,
  S21 = 48 variants, S51 = 8. The per-family variant count is the `VARIANTS` column; the grammar dimensions
  are documented per family in `strategy_library_metadata.py` (`grammar_dims`).
- **2,432 variants are 44 mechanisms, not 2,432 strategies.** They are also not discarded: the count is
  carried per family so a future attribution run can choose a variant-selection rule explicitly rather than
  implicitly.
- Blocks B–E are one object per family (single parameterisation each), so `VARIANTS` is 1 or blank there.

---

## 5 — KNOWN INVALIDS, EXPLICIT (§6)

```
EXCLUDED_INVALID_OBJECTS (4) — carried in the manifest with STATUS=INVALID, not omitted:

S47            n < 25 — population too rare to score. Results parquet exists (12 variants).
S49            non-selective / non-discrete signal. NO results parquet exists.
P2_RANGE_LOW   OVERLAP ARTIFACT — established by Alpha's own replication (8693478).
V2_4_COILED    SESSION COMPOSITION CONFOUND — established by Alpha's own replication (7d12f26).

SUPERSEDED (1), with the corrected implementation linked:
OB_RETEST_FACTORY_V1 (OBR-BULL-1)  --SUPERSEDED_BY-->  OB_CAUSAL_EXECUTION_FACTORY_V1
  reason: same-bar FILL ARTIFACT — a resting limit was cancelled by the same bar's close, dropping
  same-bar filled-then-stopped losers. Headline +0.154R; corrected causal fill -0.067R.
  (Alpha 934280a; Statistician independent review bd2a40e.)

DEFECT NOTED, OBJECT STILL ELIGIBLE:
DIRECTION_AGNOSTIC_EXPANSION_HARVEST_V1 — reproduces exactly, but (a) the stated direction-selection
  mechanism is refuted (the edge is long-side drift), (b) 8.65% of fills gap through the activation level,
  (c) the research holdout was consumed. Statistician 94dff78. Eligible as a trade population; its
  MECHANISM label must not be taken at face value.

DATA_BLOCKED (7):
S32-S37 — external data (intermarket, cross-asset lead-lag, rates, COT, macro-event, sentiment).
GOLD_ORDER_FLOW_DISCOVERY_V1 — 2-week GC sample only (Statistician af6790c).
```

---

## 6 — TRADE-LEVEL ELIGIBILITY (§7, §8, §9)

Classified per the mandate's four classes. **Profitability was not used as a criterion** — 99 of 120 objects
are `NEGATIVE` and they are retained deliberately, because §8/§9 want exactly those.

| class | meaning | count |
|---|---|---|
| **A** | `VALID_TRADE_LOG_EXISTS` | **16** |
| **B** | `NO_LOG_BUT_CAN_REGENERATE_CAUSALLY_FROM_FROZEN_SPEC` | **88** |
| **C** | `CANNOT_REGENERATE / INSUFFICIENT_ARTIFACT` | **8** |
| **D** | `INFORMATION_ONLY — NO LEGITIMATE TRADE POPULATION` | **8** |

**The critical technical fact behind class B.** For all 43 valid S-library families, trades are not merely
"probably regenerable" — the mechanism is verified:

- `code/mstrat.py:536` `backtest(d,h) → simulate(d, REGISTRY[family][1](d,h), CFG)`
- `run_ext_family.py:38` asserts `{'R','si','ei'} ⊆ simulate(...).columns` — a **per-trade ledger** with
  result, signal index and entry index.
- `results/full.log` records, for **every** family: `lookahead_safe=True  ledger_ok=True  selective=True`.

So the largest missed block is the one most cheaply recovered: a loop over the frozen grammar regenerates
trade-level populations with a lookahead audit already on record.

---

## 7 — WHAT THE MANIFEST DOES *NOT* SETTLE

Stated plainly so it is not assumed later:

1. **Variant selection is a decision, not a fact.** A family with 60 variants has no canonical trade
   population until someone picks a rule (best-`exp`? median? all pooled? one pre-registered default?).
   Pooling all 2,420 valid variants gives **1,886,244 variant-trades**, which is overlap, not evidence.
   Taking one representative variant per family gives **79,540 trades** across 42 families. Both numbers are
   in this manifest; **neither is "the" answer**, and the choice must be pre-registered before any
   attribution run, because it is a researcher degree of freedom that would otherwise be optimised.
2. **Block E mechanism classes are not resolved** (see §3).
3. **Alpha's 14 objects span 2011–2026**, i.e. they include the escrowed research holdout
   (`2025-10-23`). Any attribution program using them inherits that exposure.
4. **Nothing here says the missed families would change Alpha's conclusion.** Per §11, this establishes
   coverage only.

---

## 8 — ANTI-SEEDING PROTOCOL FOR THE NEXT ATTRIBUTION RUN (§14)

**Definition only — no discovery performed.** The concern is real: Alpha V1's headline conditions (NY, high
volatility, H4 alignment, LONG) are the four examples the mandate itself supplied.

1. **Enumerate the feature inventory from the panel, not from the prompt.** The feature set is whatever is
   causally available at entry time, enumerated programmatically from the panel builder. A feature enters
   because it exists at entry, not because anyone named it.
2. **Pre-register the full feature list and the test budget in writing, before scoring** — the discipline
   that caught my own Scout V2 breach, and now enforced in code (a scorer that raises past the budget).
3. **Blind the analyst to feature names during scoring.** Score `f01…fNN`; unblind only after the ranking
   is frozen. A named feature cannot be privileged if it has no name.
4. **All features compete under one multiplicity correction** at the full declared m, not at the number of
   features someone found interesting.
5. **Mandatory placebo**: shuffle the feature-to-trade assignment within strategy and re-rank. Any
   condition that survives shuffling is a property of the payoff shape, not of the feature.
6. **Report the rank of the four prompt-mentioned conditions among all features.** If NY/high-vol/H4/LONG
   land mid-table, that is the finding, and it should be visible.
7. **Independence**: trades from one strategy on one day are not independent observations — cluster by day,
   and report the effective N, not the raw trade count.

---

## 9 — PROTECTION (§18)

Nothing was changed, regenerated, promoted or attributed. No winner/loser analysis, no time-bucket, session,
weekday, volatility or interaction search was run. Not touched: **S5, Q4, AI Trader, P007, MGMT-004, MT5,
StrategyCatalog** — S5 appears in the manifest as a protected row and is excluded from the attribution
universe by protection, not by eligibility.

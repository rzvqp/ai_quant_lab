# STRATEGY_ATTRIBUTION_V2 — PROTOCOL FREEZE

**Mandate:** `STRATEGY ATTRIBUTION V2 PROTOCOL FREEZE` — pre-registration only. No outcome attribution, no
edge search, no analysis of winners vs losers.
**Division:** Statistician. **Date:** 2026-09-02.
**Package:** `statistician/attribution_v2/` (11 files) · builders `statistician/attribution_v2_build/`.

```
MANIFEST_HASH_VERIFIED = YES
  433f1cecbbae20e1d27ce9dc47b604d5258e36702881973a0e7f5fa032a440d9   (recomputed, matches)

PROTOCOL_PACKAGE_HASH  = 62852d36844d4eee8a48eec85f4102c4e1b12b4e3e039fa38272ca4f25cf8bf2
FEATURE_MAP_HASH       = 6cddeef6371fb42da7e4db5f5f936b7451727fae8673cc4414d5ab282ab5e943
BLIND_KEY_HASH         = 268a4f1878ff15df81adba165f1786d320c15b62a148327f440eb3cf293f146f
```

---

## 0 — THE NUMBER THAT JUSTIFIES THIS MANDATE

Alpha V1's entire feature panel (`attr_run.py:feature_panel`) was **13 features**: year, month, dow, hour,
half-hour bucket, session, ATR, ATR-percentile, vol-bucket, H1-up, H4-context, range-location, return-z.

**The four conditions the CEO offered as examples — NY, high volatility, H4 alignment, LONG — are four of
those thirteen.** Roughly 31% of the searched space was the prompt's own wording. That they came back as
"the answer" is close to arithmetically inevitable.

V2 searches **46** blinded pre-entry features. The same four are now **8.7%** of the space, and they are
scored without names.

---

## 1 — ATTRIBUTION UNIVERSE V2 (§2)

```
ATTRIBUTION_FAMILIES     = 115 objects   (all attribution-eligible objects in the frozen manifest)
REPRESENTATIVE_VARIANTS  = 56            (S-library, outcome-blind rule below)
```

| tier | objects | source |
|---|---|---|
| `T1_LOG_EXISTS` | **14** | Alpha V1's own generators — trade logs exist today |
| `T1_REGENERATE_SLIB` | **56** | S-library representatives across 43 families |
| `T2_REGENERATE_EDGERESEARCH` | **25** | `edge_research` E-series / candidate series |
| `T2_REGENERATE_FACTORY` | **14** | post-S51 factories on other panels |
| `T2_REGENERATE_FROZEN_SPEC` | **6** | frozen candidates |

Exact IDs: `attribution_v2/ATTRIBUTION_UNIVERSE_V2.csv`.

**Skipping rule (binding).** Alpha must attempt every object. A family that cannot be regenerated appears in
the output as **`FAILED_REGENERATION`** with the exact error, and is counted in the denominator of every
coverage statistic. **It may not disappear.** Silent omission is the specific failure V1 exhibited, and a
coverage figure computed over "what loaded" is not a coverage figure.

---

## 2 — REPRESENTATIVE-VARIANT RULE (§3) — the critical unresolved problem

```
REPRESENTATIVE_SELECTION_RULE =
  A. If a family has a formally frozen canonical specification, use it.                    [none exist]
  B. Else if an authoritative primary/default variant exists, use it.                      [none declared]
  C. Else: GRAMMAR_INDEX_0 — the first hypothesis emitted by the family's own frozen
     grammar function, i.e. the FIRST DECLARED VALUE of every grammar dimension.
     Refinement: for the 13 families whose grammar contains an explicit DIRECTION dimension
     (side / dir / direction), take the first variant of EACH declared direction, so a family
     is never represented by one side only.
  D. Families where no defensible representative exists are classified separately, not chosen
     retrospectively.                                                                       [none needed]
```

**Why C is outcome-blind and reproducible.** `mstrat.py:144 _grid()` builds the grammar with
`itertools.product` over the dimension dict **in declaration order**, so element 0 takes the first declared
value of every dimension — the author's default, fixed when the family was written and **before any result
existed**. The variant id is `md5(family + sorted(items))[:12]`, so the choice is verifiable by anyone.

**Verification performed:** 57 of 58 generated representatives are present in the frozen result set. The one
absent is **S49**, which has no results parquet at all — consistent with its documented INVALID status.
S47 and S49 are excluded as INVALID, leaving **56 eligible representatives across 43 families** (13 families
contribute 2 for direction symmetry; 30 contribute 1).

**Explicitly prohibited, and not used anywhere in this construction:**
`BEST_VARIANT` · `BEST_OOS_VARIANT` · `BEST_EXPECTANCY_VARIANT` · `MEDIAN_BY_PNL` ·
`TOP_REGISTRY_CANDIDATE` selected on results. **No `exp`, `pf`, `dd`, `win`, `sumR`, `val_exp`, `median`,
`trim5`, `t1/t3/t5`, `wo1`, `pos_months`, `hist_prof`, `research_worthy` or `fragile` column was read by the
selection code.** The only result-file access was an existence check on the id.

---

## 3 — WEIGHTING (§4) — three levels, reported separately, never collapsed

| level | unit | answers |
|---|---|---|
| **A — TRADE-WEIGHTED** | one trade = one observation | what happened to the pooled trade population |
| **B — FAMILY-WEIGHTED** | one family = one observation | does the condition recur across independent strategies |
| **C — MECHANISM-WEIGHTED** | one mechanism = one observation | does it recur across independent *economic bets* |

Level C matters most here and is the one V1 lacked: **21 of 115 objects and 48% of V1's trades are
`M06_SESSION_TIME`**. Under level A a session finding is partly a statement about the composition of the
pool. Under level C, `M06` gets weight 1 of 25.

A finding reported at one level must state its value at all three. A level-A result with no level-C support
is a property of the pool, not of the market.

---

## 4 — MECHANISM TAXONOMY (§5)

```
FINAL_DISTINCT_MECHANISMS  = 25
MECHANISM_MAPPING_COMPLETE = YES
UNKNOWN_MECHANISM families = 0
```

`M27_EDGE_RESEARCH_PATTERN` is **dissolved**. All 25 `edge_research` families were classified from each
module's own frozen V0 hypothesis text — e.g. E009 CHoCH-retest → `M11_STRUCTURE_BREAK_REVERSAL`, E012
inverted FVG → `M13_IMBALANCE_FVG`, E029 weekly gap fill → `M15_GAP`, CAND-0038 weekly break + displacement
→ `M10_DISPLACEMENT_CONTINUATION`. Classification used the stated economic mechanism only; no performance
field was consulted, and no example from any prior prompt shaped a class.

`M22_EXOGENOUS_DATA` (S32–S37) is excluded — not implemented, so it has no objects.

Distribution: `M06_SESSION_TIME` 21 · `M14_REFERENCE_LEVEL` 15 · `M07/M08` 8 each · `M03/M04` 7 each ·
`M01` 5 · … · `M18/M20/M25/M26` 1 each. Full map: `attribution_v2/MECHANISM_MAP.csv`.

---

## 5 — HISTORICAL REUSE (§6)

```
ATTRIBUTION_DISCOVERY_RANGE = 2011-07-26 .. 2026-07-27 (the entire governed XAU M15 record)
UNTOUCHED_VALIDATION_RANGE  = NONE
HISTORICAL_REUSE_STATUS     = MATERIALLY_EXPOSED
```

**There is no clean out-of-sample range for this universe, and I am not going to manufacture one.** Evidence:

- The program escrow `RESEARCH_HOLDOUT_CUTOFF_UTC = 2025-10-23` **has been consumed**. Alpha's
  `DIRECTION_AGNOSTIC_EXPANSION_HARVEST_V1` ran to 2026-07-27 with no truncation; those 213 in-holdout
  episodes returned **+0.2374R against +0.0442R outside** (Statistician `94dff78`).
- Alpha V1's own attribution objects span **2011–2026**, i.e. they include the escrow window.
- The S1–S51 campaign declared its own 50,491 / 16,830 / 16,831 split and that split's holdout has been
  reported on in campaign artifacts.

**Consequence, binding on V2:** every finding is **HYPOTHESIS_GENERATION ONLY**. No V2 output may be
described as validated, confirmed, or out-of-sample. Chronological thirds are used for **stability
description only** and must never be labelled independent validation. A genuinely clean validation requires
either forward data accrued **after this freeze date**, or a newly escrowed range no division has consulted.

---

## 6 — FEATURE INVENTORY AND BLINDING (§7, §8, §9)

```
BLINDED_PRE_ENTRY_FEATURES = 46      (32 numeric · 11 categorical · 3 bool)
FEATURE_MAP_HASH           = 6cddeef6371fb42da7e4db5f5f936b7451727fae8673cc4414d5ab282ab5e943
```

**Derivation.** The inventory was enumerated from the governed feature module `mstrat.load()` (54 columns,
355,696 rows, lookahead-safe by construction) plus deterministic causal derivations of it — distances to
prior-day / prior-week / opening-range / VWAP / previous-session levels in ATR units, range locations at
four horizons, volatility state and ratios, returns and efficiency at four horizons, run lengths, volume
ratios, session position, H1/H4/D1 states and their alignment count, imbalance and displacement flags, and
clock/calendar variables. **Not one feature was taken from the wording of any prompt.**

**Eligibility (§9):**

| class | count | note |
|---|---|---|
| `ELIGIBLE_PRE_ENTRY` | **46** | available at entry, causal, no future bars, no outcome input |
| `POST_ENTRY_ONLY` | 8 | `mfe_R`, `mae_R`, time-to-MFE/MAE, adverse-first, exit kind, bars held, final R |
| `INVALID_LOOKAHEAD` | 7 | later-confirmed swings, completed session ranges, eventual exit price, unconfirmed zigzag pivots, forward ATR, next-bar open |
| `NOT_AVAILABLE_FOR_FAMILY` | runtime | **must be recorded per (object, feature)** — an absent feature is a *recorded absence*, never a silently dropped test |

**Blinding mechanics.** Alpha receives `BLINDED_FEATURE_SCHEMA.csv`: `BLIND_ID`, `KIND`, `CLASS` — ids
`f001…f046`, **no names, no descriptions**. It performs the entire primary ranking, effect estimation,
stability and multiplicity work on blinded ids.

**Blinding is KEYED, and it is PARTIAL. Both statements matter.**

- *Keyed*: blind ids are assigned by sorting on `sha256(KEY + true_name)`, with the key held offline. An
  earlier draft of this freeze sorted the names **alphabetically**, which is trivially reconstructable
  from a guessed name list; that was caught and replaced before anything was committed. Only
  `FEATURE_MAP_HASH` and `BLIND_KEY_HASH` are published, so the map can be verified after the fact as
  fixed in advance and unaltered.
- *Not committed*: these repositories are mirrored and readable by every division, so a name→id map — or
  a builder script containing the name list — committed anywhere would not be blind. The feature builder
  is therefore published only as `feat_REDACTED.py`, describing the method without the names.
- *Partial, declared*: **4 of the 46 features carry a unique bin count (4, 12, 24, 48) and are therefore
  identifiable from `FEATURE_BINNING.csv` alone.** Alpha needs per-feature bin counts to run at all, so
  this cannot be closed without breaking the analysis. I am declaring it rather than claiming a blinding
  I have not delivered. **Compensating control:** for any of those four, the primary result must be
  reported with the shuffle placebo attached, and §16's requirement to publish the rank of every
  prompt-mentioned condition among all 46 applies with particular force. The other 42 are not
  individually identifiable.

Unblinding happens **only after** Alpha's ranking, effect estimates, stability metrics and multiplicity
results are frozen and hashed.

---

## 7 — SEARCH BUDGET, BINNING, TIME FEATURES (§11, §12, §13)

```
STAGE 1  per-object x per-feature omnibus test    46 x 115 = 5,290
STAGE 2  cross-family recurrence, one per feature            46
STAGE 3  bounded interactions, hard cap                      20
TOTAL_DECLARED_TESTS                                      = 5,356
```

- **Single features first.** Stage 3 may not begin until stages 1 and 2 are frozen and hashed.
- **Interactions are mechanically determined, not chosen:** all 10 pairs among the top-5 stage-2 recurrent
  features, plus each top-5 feature crossed with the next-ranked feature at matching index (ranks 6-10) — exactly 20, and **executable without unblinding any feature**. No other interaction is permitted
  inside V2.
- **Minimum N:** 30 trades **and** 20 distinct calendar days per bin. Below that the cell is `NOT_TESTED`
  and is reported as such — **it is not evidence of absence**.
- **Binning is frozen now (§12):** numeric → **5 causal quintiles** on a trailing 2,000-bar percentile rank
  (never a full-sample rank, which would leak); bool → 2; categorical → declared natural levels
  (session 4, hour 24, half-hour 48, weekday 5, month 12, week-of-month 5, each trend state 3, side 2).
  **277 declared bins in total.** Threshold scanning — `ATR > 63%`, `> 64%`, `> 65%` … — is prohibited.
- **Time features (§13):** included on equal terms, with mechanical bins fixed above. If a 10:00–10:30
  bucket looks interesting, Alpha may report it; it may **not** then search 09:55–10:25, 10:05–10:35 or any
  other sliding window. Bin edges are frozen and V2 has no authority to move them.

---

## 8 — MULTIPLICITY (§14)

```
MULTIPLICITY_METHOD = hierarchical, frozen before any outcome is read:
  stage 1  BH-FDR at q = 0.05 across all 5,290 per-object x per-feature tests
  stage 2  Bonferroni at m = 46
  stage 3  Bonferroni at m = 20
reference bound: Bonferroni over all 5,356 requires |z| > 4.43 — reported alongside every
                 stage-2 survivor so the CEO can see the strictest reading, not as the primary policy
```

FDR is the right tool for stage 1 (explicitly exploratory), Bonferroni for stage 2/3 (few tests, strong
claims). **The correction may not be revised after results are seen.**

Inference is **day-clustered** throughout: trades from one strategy on one day are not independent
observations, and effective N — not raw trade count — is what gets reported.

---

## 9 — PLACEBO (§15)

```
PLACEBO_PROTOCOL (all three run BEFORE any real result is interpreted):

1. OUTCOME_SHUFFLE_WITHIN_BLOCK — permute per-trade outcomes within (object x calendar-month)
   blocks, preserving the feature panel and timestamps; rerun the FULL stage-1 pipeline; 200 replicates.
   PASS: the BH-FDR discovery rate under the null <= q (0.05) within Monte-Carlo error.
   FAIL: if the pipeline routinely manufactures apparently-strong rescue cells on shuffled outcomes,
         V2 STOPS and no result is interpreted.
2. FEATURE_ASSIGNMENT_SHUFFLE — permute feature-vector-to-trade assignment within each object,
   200 replicates. Anything that survives is a property of the payoff shape, not of the feature.
3. SYNTHETIC_POSITIVE_CONTROL — inject +0.3R on one randomly chosen blinded feature's top bin and
   confirm recovery at the declared power; 50 replicates.
```

---

## 10 — CROSS-FAMILY RECURRENCE (§16)

A blinded feature qualifies as a **RECURRING DISCRIMINATOR** only if **all** hold:

1. supported in **≥ 5 distinct families**;
2. supported in **≥ 3 distinct mechanisms** (level C, not level A);
3. **same sign** of the expectancy shift in every supporting family;
4. **|mean effect| ≥ 0.05R** at family-weighted level B;
5. sign-consistent in **≥ 2 of 3 chronological thirds** (stability, *not* validation — §5);
6. survives **Bonferroni at m = 46** at stage 2.

Anything short of all six is `SUGGESTIVE`, never `RECURRING`.

---

## 11 — RESCUE CLASSIFICATION (§17)

| tier | criteria (all required) |
|---|---|
| **NONE** | subset expectancy ≤ 0, **or** fails min-N (30 trades / 20 days) |
| **WEAK** | subset expectancy > 0, but incremental vs excluded trades < 0.05R, **or** N < 100, **or** fails stage-1 FDR |
| **MODERATE** | subset exp > 0 · incremental ≥ 0.05R · N ≥ 100 · ≥ 50 independent days · survives FDR · sign-consistent in ≥ 2 of 3 chronological thirds |
| **STRONG** | MODERATE **and** incremental ≥ 0.10R **and** survives Bonferroni at the full declared m **and** the top 1% of subset trades contribute < 40% of subset PnL **and** the same blinded feature recurs in ≥ 2 other families |

**A positive small cell cannot become STRONG.** Effect concentration is a gate, not a footnote — this is the
lesson of OBR-BULL-1 (a fill artifact that looked like the campaign's first positive) and of Family E
(top 1% = 80% of PnL).

---

## 12 — THE TWO QUESTIONS MUST NOT BE MERGED (§18)

```
Q1  DOES A FAILED STRATEGY CONTAIN A PROFITABLE CONDITIONAL SUBPOPULATION?
    -> reported ONLY as: subset expectancy > 0 (absolute, after cost)

Q2  DO MULTIPLE DIFFERENT STRATEGIES SHARE THE SAME PROFITABLE MARKET STATE?
    -> reported ONLY as: Q1 satisfied in >= 5 families and >= 3 mechanisms, same sign
```

**"They lose less in state X" is not an answer to either question.** It is a separate, third statistic and
must be labelled `LOSE_LESS_TILT`. V1's headline — NY × high-vol × H4-aligned × LONG at **−0.052R** — is a
`LOSE_LESS_TILT`, not a rescue, and V2 may not present that shape as a rescue at any effect size.

---

## 13 — POST-ENTRY (§19)

```
POST_ENTRY_ELIGIBLE_FAMILIES (10, verified from path data present today):
  HTF_PBK_TREND · HTF_RANGE_FADE · HTF_RECLAIM · HTF_TGT_BREAK
  SESS_A · SESS_B · SESS_C · SESS_D · SESS_E · SESS_Fc

EXCLUDED — no path data: OBR_A_limit · OBEXEC_B · OBEXEC_C · OBEXEC_D
CONDITIONALLY ELIGIBLE: the 56 S-library representatives. simulate() emits (R, si, ei) but not MFE/MAE;
  they become eligible once path is recomputed causally from (si, ei) + bars, and NOT before.
```

Post-entry conclusions may be stated **only** over the families that carry path data, with that denominator
printed. V1 generalised a 10-of-14 result without saying so; V2 may not.

---

## 14 — S5 (§20)

S5 is **read-only**. It may be used as a positive reference/benchmark only. **No S5 filter, no S5 subset
search, no S5 improvement, no S5 entry into rescue optimisation.** It appears in the manifest as protected,
and it is absent from `ATTRIBUTION_UNIVERSE_V2.csv`.

---

## 15 — PACKAGE (§21, §22)

`statistician/attribution_v2/` — 11 files:

```
ATTRIBUTION_UNIVERSE_V2.csv     REPRESENTATIVE_VARIANT_MAP.csv   MECHANISM_MAP.csv
BLINDED_FEATURE_SCHEMA.csv      FEATURE_ELIGIBILITY_TABLE.csv    FEATURE_BINNING.csv
SEARCH_BUDGET.json              MULTIPLICITY_POLICY.json         PLACEBO_PROTOCOL.json
POST_ENTRY_ELIGIBILITY.csv      HISTORICAL_REUSE_POLICY.json
```

**Deliberately excluded from the package:** the feature name→id map (held by the Statistician; only its hash
is published — see §6).

```
STRATEGY_ATTRIBUTION_V2_PROTOCOL_FREEZE_COMPLETE = YES
MANIFEST_HASH_VERIFIED       = YES
ATTRIBUTION_FAMILIES         = 115
REPRESENTATIVE_VARIANTS      = 56
FINAL_DISTINCT_MECHANISMS    = 25   (MECHANISM_MAPPING_COMPLETE = YES, 0 unknown)
BLINDED_PRE_ENTRY_FEATURES   = 46
POST_ENTRY_ELIGIBLE_FAMILIES = 10   (+56 conditional on path recomputation)
TOTAL_DECLARED_TESTS         = 5,356
MULTIPLICITY_METHOD          = hierarchical BH-FDR(q=.05, m=5290) / Bonferroni(m=46) / Bonferroni(m=20)
HISTORICAL_REUSE_STATUS      = MATERIALLY_EXPOSED — no clean OOS exists; V2 output is HYPOTHESIS_GENERATION ONLY
PROTOCOL_PACKAGE_HASH        = 62852d36844d4eee8a48eec85f4102c4e1b12b4e3e039fa38272ca4f25cf8bf2
READY_FOR_ALPHA_ATTRIBUTION_V2 = YES
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

**Protection.** No outcome was attributed, no expectancy compared, no winner/loser split computed, no time
bucket, session, weekday, volatility state or interaction searched. Not touched: **S5, Q4, AI Trader, P007,
MGMT-004, MT5, StrategyCatalog.** No promotion.

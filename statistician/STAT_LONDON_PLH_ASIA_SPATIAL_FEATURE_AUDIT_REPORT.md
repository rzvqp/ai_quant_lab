# STAT — LONDON PLH ↔ ASIA HIGH SPATIAL FEATURE AUDIT

**Mandate ID:** `STAT-LONDON-PLH-ASIA-SPATIAL-FEATURE-AUDIT-001`
**Division:** Statistician (independent statistical validation)
**Date:** 2026-08-22
**Subject:** `ALPHA-XAUUSD-LONDON-PLH-CAUSAL-FEATURE-MAP-001`, Alpha commit `677ecfd687e93be6428a77a7072d2849609d3fac`
**Parent lineage:** commit `50b099dd5d2632154ec3aba6cf0432f9857ec9e2`
**Feature under audit:** `plh_minus_asiahigh` = (Pre-London High − Asia High), pips

**Scope directives honoured:** `INDEPENDENT_AUDIT_ONLY` · `LONDON_PRE_LONDON_HIGH_ONLY` ·
`PLH_MINUS_ASIAHIGH_PRIMARY` · `CONTINUOUS_RELATIONSHIP_FIRST` · `NO_THRESHOLD_PROMOTION` ·
`SELECTION_BIAS_AUDIT_REQUIRED` · `AVAILABLE_ROOM_CONTROL_REQUIRED` · `LABEL_GEOMETRY_CONTROL_REQUIRED` ·
`NEW_HIGH_FIRST_REQUIRED` · `NO_CLASSIFIER` · `NO_EXECUTION` · `NO_AI_TRADER` · `NO_LIVE`

---

## 0 — TERMINAL VERDICT

```
PLH_ASIA_SPATIAL_FEATURE_AUDIT_FAIL
PLH_ASIA_SPATIAL_FEATURE_NOT_SUPPORTED
```

**Scope of this verdict, stated before the evidence:** the *audit* completed successfully — the
**feature** failed it. Alpha's arithmetic is not in question. **Every number in Alpha's report reproduced
exactly**, to the last decimal it published. The failure is not a computational error; it is that the
quantity Alpha identified as a predictive spatial feature is, on this data, an algebraic re-expression of
the distance from the event to the target, and the outcome label mechanically awards `CLEAN` to events
whose distance is zero or negative.

Three controls the CEO designated **mandatory** (§17 available-room, §18 label-geometry) and **essential**
(§19 new-high-first) all fail. No threshold research is justified on this evidence.

---

## 1 — LINEAGE

| Item | Value | Verified |
|---|---|---|
| Alpha feature-map commit | `677ecfd` | ✓ read from repo |
| Parent commit | `50b099d` | ✓ |
| Parent builder | `reports/alpha_discovery/frank_london.py` | ✓ read, 124 lines |
| Feature map | `reports/alpha_discovery/plh_feature_map.py` | ✓ read, 120 lines |
| Alpha report | `ALPHA_XAUUSD_LONDON_PLH_CAUSAL_FEATURE_MAP_REPORT.md` | ✓ read, 86 lines |
| Family | `FAM_LPL` = `L_PreLondonHigh` (`rowsLPL`) | ✓ |

Everything below was recovered by importing and executing Alpha's own modules. Nothing was rebuilt from the
mandate prose.

---

## 2 — PARENT REPRODUCTION (§2, §3) — **EXACT**

```
N = 133      unique trading days = 133      duplicate (day, bar) rows = 0
A_clean            n=49   p=0.3684
B_newhi_then_mid   n=37   p=0.2782
C_continuation     n=46   p=0.3459
D_stalled          n= 1   p=0.0075
sum = 133
years: 2021 n=27 · 2022 n=47 · 2023 n=59
date span: 2021-11-01 09:30 UTC .. 2023-12-27 08:00 UTC
```

Matches Alpha's published `N=133`, `unique_days=133`, and class balance `A 0.368 / B 0.278 / C 0.346 /
D 0.008` exactly. **One event per canonical parent day by construction** (`sweeps()` breaks after the first
`high > L` per day). No duplicate event rows.

**One discrepancy found, minor and non-material:** Alpha's §11 states the sample is *"partial-2021 from
2021-07."* The first parent event is **2021-11-01**. 2021 contributes **two months**, not six. This does not
change any statistic, but it overstates the temporal coverage of the earliest year and is corrected here.

---

## 3 — FEATURE IDENTITY AND CAUSALITY (§4) — **PASS**

| Component | Construction | Frozen before event? |
|---|---|---|
| `PLH` | max native-M5 `high` over London-local **[07:00, 08:00)**, same day, `utc>=7` | **YES** |
| `AsiaHigh` | max M15 `high` over **[00:00, 07:00) UTC**, same day | **YES** |
| Event | first M5 bar with `high > PLH` in London-local **[08:00, 10:00)** | after both |

Verified mechanically: **0 of 133** events fall outside London-local `[8,10)`; **0** have UTC hour `< 7`;
observed event London-hours span exactly `{8, 9}`. Both levels close strictly before the event window opens.

**`plh_minus_asiahigh` is strictly causal. It contains no post-event information. No leakage found.**
This is the one strong structural property Alpha claimed that survives audit intact.

---

## 4 — CLASS BALANCE AND THE OUTCOME DEFINITION

Read verbatim from `frank_london.classify()`:

- **objective** = Asia **mid** = `(AsiaHigh + AsiaLow)/2` — a *fixed price level*, identical for all events on a given day
- **A_clean** = low ≤ mid within 48 M5 bars, **and** no `high > sweep_hi` strictly before that bar
- **B** = reached mid, but a new high came first
- **C** = never reached mid, new high occurred
- **D** = neither (n=1)

The objective is a **fixed level, not a fixed distance**. This single design choice is the origin of
everything in §6–§8 below.

---

## 5 — CONTINUOUS ANALYSIS (§5, §6, §7) — nominally strong

Direction convention throughout: AUC is computed on the **raw** feature. **AUC < 0.5 means more negative
`plh_minus_asiahigh` → higher P(label).** Rank-biserial `r = 2·AUC − 1`.

| Contrast | n | AUC | r_rb | 95% CI (event bootstrap) |
|---|---|---|---|---|
| A vs B (both reached mid) | 86 | 0.220 | −0.559 | [0.129, 0.322] |
| A vs C | 95 | 0.126 | −0.747 | [0.061, 0.202] |
| **A vs B+C (Alpha's primary)** | 132 | **0.168** | −0.663 | [0.103, 0.241] |
| A vs all non-A | 133 | 0.167 | −0.667 | [0.102, 0.243] |
| (A+B) vs (C+D) — *reached mid at all* | 133 | 0.198 | −0.604 | [0.120, 0.282] |

Continuous, un-binned: **Spearman ρ(x, A) = −0.557, p = 1.6 × 10⁻¹⁴**. Cochran-Armitage trend across the
four ordered bins: **z = −6.60, p = 4.0 × 10⁻¹¹**.

**Monotonicity (§7), tested on deciles rather than Alpha's four bins:**

| decile | x range (p) | n | P(A) | P(B) | P(C) | median room |
|---|---|---|---|---|---|---|
| D1 | [−155, −59) | 14 | 0.929 | 0.000 | 0.071 | **−24.3** |
| D2 | [−59, −37) | 13 | 0.692 | 0.231 | 0.077 | **−4.6** |
| D3 | [−37, −29) | 13 | 0.538 | 0.231 | 0.231 | +6.8 |
| D4 | [−29, −21) | 13 | 0.462 | 0.385 | 0.154 | +6.9 |
| D5 | [−21, −13) | 13 | 0.308 | 0.462 | 0.231 | +12.1 |
| D6 | [−13, −8) | 14 | 0.357 | 0.429 | 0.214 | +21.4 |
| D7 | [−8, −0) | 13 | 0.231 | 0.308 | 0.462 | +43.0 |
| D8 | [−0, +6) | 13 | 0.077 | 0.308 | 0.538 | +39.3 |
| D9 | [+6, +13) | 13 | 0.000 | 0.308 | 0.692 | +33.8 |
| D10 | [+13, ∞) | 14 | 0.071 | 0.143 | 0.786 | +60.3 |

The gradient is smooth and near-monotone at decile resolution — it is **not** an artifact of Alpha's bin
edges. **But note the last column**: median available room rises monotonically from −24p to +60p in lockstep.
That is the subject of §6.

**Taken at face value, the relationship is real, continuous, monotone and highly significant.** The rest of
this audit establishes what it is a relationship *with*.

---

## 6 — AVAILABLE-ROOM CONTROL (§17) — **MANDATORY — FAIL**

Alpha's report line 37 lists `dist_asia_mid` (DISC AUC 0.06 / CONF 0.15) and **excludes** it as *"trivial
proximity-to-target; inversely tied to remaining room."* Line 30 and line 69 claim `plh_minus_asiahigh` is
*"position-independent by construction"* and *"needs no adjustment."*

**The two variables are algebraically the same quantity.** Measured on all 133 events:

```
room  =  x  +  dist_close_plh_E0  +  asia_range/2        max |residual| = 0.0000000000
median dist_close_plh_E0 = −0.1p          (the E0 close sits ON the swept PLH)
=>    x  ≈  room − asia_range/2           corr(x, room) = 0.765
```

The exclusion criterion Alpha applied to `dist_asia_mid` therefore applies to `plh_minus_asiahigh` as well.
**Alpha excluded the confound and retained a proxy for it.**

### 6.1 The retained variable is *weaker* than the excluded one

| variable | A vs B+C | (A+B) vs (C+D) | A vs B | A given room>0 |
|---|---|---|---|---|
| `plh_minus_asiahigh` **(kept)** | 0.168 | 0.198 | 0.220 | 0.286 |
| `dist_asia_mid` = room **(excluded)** | **0.099** | **0.146** | **0.136** | **0.208** |

On every contrast the discarded variable is further from 0.5, in the same direction. Alpha discarded the
stronger measurement of the same thing and reported the weaker one as the discovery.

### 6.2 Joint model — the feature contributes nothing

Logistic regression used strictly as an audit tool (§23), A vs B+C, n=132:

| model | coefficient | z |
|---|---|---|
| x alone | b_x = −0.05657 | **−5.09** |
| room alone | b_room = −0.08529 | **−5.56** |
| **x + room** | b_x = −0.00493 | **−0.32** |
| | b_room = −0.08060 | **−3.83** |

`room` retains 94% of its univariate coefficient when `x` is added. `x` loses 91% of its own and its z-score
collapses to −0.32. **Conditional on available room, `plh_minus_asiahigh` carries no information.**

### 6.3 Stratified

| stratum | n | AUC(x) | base P(A) | | stratum | n | AUC(room) | base P(A) |
|---|---|---|---|---|---|---|---|---|
| low room | 44 | 0.309 | 0.841 | | x low | 44 | **0.055** | 0.705 |
| mid room | 44 | **0.457** | 0.182 | | x mid | 44 | **0.150** | 0.318 |
| high room | 44 | 0.362 | 0.091 | | x high | 44 | 0.463 | 0.091 |

Room survives strongly inside strata of x (0.055, 0.150). x is materially weakened inside strata of room,
and is uninformative in the middle stratum.

**§17 verdict: the apparent CLEAN relationship is a consequence of available room. FAIL.**

---

## 7 — LABEL-GEOMETRY CONTROL (§18) — **MANDATORY — FAIL**

This is the decisive finding, and it is mechanical rather than statistical.

```
                     bars-to-mid (1 bar = 5 minutes)
  A_clean   n=49     P25 = 1    median = 1     P75 = 1
  B_newhi   n=37     P25 = 6    median = 18    P75 = 27
```

**The median class-A "CLEAN_BEARISH_REVERSAL" reaches its objective within ONE M5 bar.**
38 of 49 (77.6%) reach it in one bar; 43 of 49 (87.8%) within three.

```
  E0 close ALREADY AT/BELOW the Asia-mid objective (room ≤ 0):
      among A : 26/49 = 0.531        among B : 0/37 = 0.000        among C : 0/46 = 0.000

  P(A | room ≤ 0) = 1.000   (n = 26)
  P(A | room > 0) = 0.215   (n = 107)
```

**26 events — 19.5% of the parent and 53.1% of every class-A event — are labelled `CLEAN_BEARISH_REVERSAL`
because the price was already at or past the objective when the event fired.** Their P(A) is not 0.87 or
0.95; it is exactly **1.000**, and it is 1.000 by definition, not by behaviour: if `l ≤ mid` on the very
next bar, no `high > sweep_hi` can possibly precede it.

The mechanism generalises:

| bars-to-mid | n | P(B \| reached) | P(A \| reached) | median x | median room |
|---|---|---|---|---|---|
| 1 | 38 | **0.000** | **1.000** | −43.1p | −6.5p |
| 2–3 | 8 | 0.375 | 0.625 | −23.7p | +12.3p |
| 4–9 | 13 | 0.769 | 0.231 | −17.5p | +21.1p |
| 10–24 | 15 | 0.867 | 0.133 | −6.6p | +28.4p |
| 25–48 | 12 | 0.917 | 0.083 | −8.2p | +30.9p |

A-versus-B is decided by **how fast** the target is reached; speed is set by **distance**; distance is the
feature. Conditioning on bars-to-mid removes the effect entirely:

```
  bars-to-mid == 1  : n=38, P(A)=1.000  -> AUC undefined (no variation to explain)
  bars-to-mid >= 2  : n=48, P(A)=0.229  -> AUC(x)=0.522   AUC(room)=0.528     BOTH DEAD
```

**Answer to the CEO's §18 question — "Could the geometry make PLH far below AsiaHigh easier to label CLEAN
even with no predictive behavioral edge?"  Yes, and it demonstrably does. Quantified above. FAIL.**

---

## 8 — NEW-HIGH-FIRST (§19) — **ESSENTIAL — FAIL**

The CEO asked specifically whether the feature *reduces* P(NEW_HIGH_FIRST), or merely increases eventual
bearish labelling. Tested directly.

```
  Unconditional P(new high above sweep_hi at ANY point in the 48-bar horizon) = 0.902
```

| bin | N | **P(new high EVER)** | P(B) = new-high-*before*-mid |
|---|---|---|---|
| < −40 | 23 | **0.957** | 0.087 |
| [−40, −20) | 31 | 0.903 | 0.290 |
| [−20, 0) | 39 | 0.846 | 0.410 |
| ≥ 0 | 40 | 0.925 | 0.250 |

```
  AUC(x, "new high EVER") = 0.464    95% CI [0.332, 0.600]      permutation p = 0.34
```

**There is no relationship between the feature and whether the market actually trades above the sweep high.**
The CI straddles 0.5 and the permutation test is non-significant. The most extreme bin (`< −40`) has the
**highest** rate of eventual new highs, 0.957.

The feature does not reduce the probability of an adverse up-move. It changes only whether that up-move is
*recorded as having come first* — which, per §7, is a timing consequence of the target already being at hand.

**§19 verdict: the feature does NOT specifically reduce NEW_HIGH_FIRST. FAIL.**

---

## 9 — CONTINUATION (§20) — reproduced, and explained

```
  P(C | x >= 0) = 0.675   (n=40)     Alpha reported 0.675    MATCH
```

Independently confirmed. But 27 of 27 class-C events in that bin have `room > 0`, and median room in the
`x ≥ 0` bin is **+41.9p** versus **−20.7p** in the `x < −40` bin. "Continuation" here means *the fixed target
41.9 pips away was not reached within four hours*. That is a statement about distance and horizon, not about
bullish continuation behaviour.

---

## 10 — DESCRIPTIVE BIN VERIFICATION (§8) — **EXACT MATCH, all four bins**

| bin | N | A | B | C | D | P(A) | P(B) | P(C) | P(D) | Alpha P(A) | |
|---|---|---|---|---|---|---|---|---|---|---|---|
| < −40 | 23 | 20 | 2 | 1 | 0 | 0.870 | 0.087 | 0.043 | 0.000 | 0.870 | **MATCH** |
| [−40, −20) | 31 | 15 | 9 | 7 | 0 | 0.484 | 0.290 | 0.226 | 0.000 | 0.484 | **MATCH** |
| [−20, 0) | 39 | 12 | 16 | 11 | 0 | 0.308 | 0.410 | 0.282 | 0.000 | 0.308 | **MATCH** |
| ≥ 0 | 40 | 2 | 10 | 27 | 1 | 0.050 | 0.250 | 0.675 | 0.025 | 0.050 | **MATCH** |

Class medians also reproduce exactly: A −32.55p (Alpha −32.6), B −12.15p (−12.2), C +4.42p (+4.4).
DISC AUC 0.124 (Alpha 0.12), CONF AUC 0.226 (Alpha 0.23). **Alpha's reported arithmetic is impeccable.**

Treated as descriptive only. No threshold promoted.

---

## 11 — EXTREME-CELL AUDIT (§9) — "HOW FRAGILE IS THE 87%?"

The mandate asks one question. It has **two different answers**, and conflating them would be the error.

**As a descriptive proportion, the 87% is NOT fragile:**

```
  successes / failures = 20 / 3            P(A) = 0.8696
  Wilson 95% CI                          = [0.679, 0.955]
  event bootstrap 95% CI (8000 resamples) = [0.739, 1.000]
  leave-1-out worst  = 0.864   (cost 0.006)
  leave-2-out worst  = 0.857   (cost 0.012)
  year composition: 2021 n=5 · 2022 n=7 · 2023 n=11        unique days = 23 of 23
  DISC n=12 P(A)=0.917   |   CONF n=11 P(A)=0.818
```

Not driven by one year, not temporally clustered, 23 distinct days, stable across the chronological split,
and insensitive to removing one or two events. On resampling grounds this cell is sound.

**As evidence of predictive skill, it is almost entirely tautological:**

```
  of the 23 events, 17 are ALREADY at/below the objective at E0 (room <= 0)
  17 of the 20 successes come from that definitionally-certain set
  removing it:  n = 6    P(A) = 0.500    Wilson [0.188, 0.812]
```

**The 87% cell is a stable measurement of a definitional property.** Strip the events that had already
arrived at the target and six events remain, at a coin flip. The number is robust; what it measures is not
a behavioural edge.

---

## 12 — THRESHOLD SENSITIVITY (§10) — diagnostic only, no promotion

| cut | n | P(A) | Wilson 95% | n (room>0) | P(A \| room>0) |
|---|---|---|---|---|---|
| x < −10 | 73 | 0.562 | [0.448, 0.670] | 47 | 0.319 |
| x < −20 | 54 | 0.648 | [0.515, 0.762] | 30 | 0.367 |
| x < −30 | 38 | 0.737 | [0.580, 0.850] | 16 | 0.375 |
| x < −40 | 23 | 0.870 | [0.679, 0.955] | 6 | 0.500 |
| x < −50 | 17 | 0.882 | [0.657, 0.967] | 5 | 0.600 |
| x < −60 | 13 | 0.923 | [0.667, 0.986] | 2 | 0.500 |

The headline column rises smoothly — the phenomenon is **not** confined to one convenient cut, which is
what §10 asked. But the right-hand column shows the sample of non-tautological events collapses to
**6, 5, 2** exactly where the headline is strongest. The broad-region robustness and the tautology
strengthen together, because they are the same thing.

**No threshold selected, recommended, or promoted.**

---

## 13 — DISC → CONF (§12) — reproduced; direction survives, meaning does not

Chronological 60/40 split reproduced from Alpha's recipe, cut at bar `2023-01-16 09:50 UTC`.

| split | n | P(A) | P(B) | P(C) | AUC(x) | AUC(room) | AUC(x \| room>0) |
|---|---|---|---|---|---|---|---|
| DISC | 79 | 0.367 | 0.266 | 0.367 | 0.124 | **0.056** | 0.203 |
| CONF | 54 | 0.370 | 0.296 | 0.315 | 0.226 | **0.147** | 0.399 |

No shuffling. Direction is consistent across the split — but `room` is the stronger variable in **both**
halves. The feature confirms out-of-sample as a proxy for room, not as an independent discriminator.

---

## 14 — YEAR BY YEAR (§13)

| year | n | A | B | C | P(A) | AUC(x) | 95% CI | n(x<−40) | n(room≤0) |
|---|---|---|---|---|---|---|---|---|---|
| 2021 (Nov–Dec only) | 27 | 11 | 9 | 7 | 0.407 | 0.068 | [0.000, 0.179] | 5 | 8 |
| 2022 | 47 | 18 | 10 | 19 | 0.383 | 0.174 | [0.067, 0.310] | 7 | 8 |
| 2023 | 59 | 20 | 18 | 20 | 0.339 | 0.222 | [0.104, 0.363] | 11 | 10 |

Direction consistent in all three, as Alpha reported. **2021 is two months (2021-11-01 → 2021-12-30), not
six** — it should be labelled a partial-quarter sample, not a year. No single year dominates: the
tautological `room ≤ 0` events are spread 8 / 8 / 10.

---

## 15 — TEMPORAL BLOCKS (§14)

Four equal chronological blocks, boundaries set by event order only — never by outcome.

| block | n | span | P(A) | P(B) | P(C) | AUC(x) | n(room≤0) |
|---|---|---|---|---|---|---|---|
| B1 | 34 | 2021-11-01 → 2022-01-14 | 0.382 | 0.382 | 0.235 | 0.077 | 9 |
| B2 | 33 | 2022-01-17 → 2022-12-19 | 0.394 | 0.152 | 0.455 | 0.219 | 5 |
| B3 | 33 | 2022-12-20 → 2023-03-08 | 0.333 | 0.273 | 0.394 | 0.116 | 8 |
| B4 | 33 | 2023-03-09 → 2023-12-27 | 0.364 | 0.303 | 0.303 | 0.321 | 4 |

Direction holds in all four blocks; magnitude varies 0.077–0.321. **No short temporal cluster explains the
result** — the effect is present throughout, consistent with it being structural rather than episodic.

---

## 16 — EFFECTIVE N / CLUSTERING (§15)

```
  raw N = 133      unique trading days = 133      events/day = 1.000  (one per day by construction)
  calendar gaps between consecutive events: 1d:62  2d:21  3d:21  4d:13  5d:4  6d:5  7d:2  9d:1
  adjacent trading-day pairs = 62/132 = 0.470      runs of consecutive days: 71, longest 5, mean 1.87
  lag-1 autocorrelation:  outcome A  +0.059      feature x  +0.096
```

Nearly half of consecutive events fall on adjacent trading days, so clustering deserved the check. But
serial dependence is negligible at lag 1 in both the feature and the outcome. **Effective N ≈ raw N = 133**;
the extreme-dependence lower bound (treating each run of adjacent days as one observation) is **71**. Both
figures are reported; neither changes any conclusion.

---

## 17 — SELECTION MULTIPLICITY (§11)

Counted mechanically from `plh_feature_map.py`:

```
  E0 static features screened            : 16   (E0F list, lines 80-82)
  landmark path features screened        : 7 x 3 landmarks = 21
  total univariate screens               : 37
  survivors under Alpha's stability rule : plh_minus_asiahigh + its ATR twin = 1 DISTINCT variable
```

Alpha's stability rule (line 88) is sign-agreement **and** |AUC − 0.5| > 0.07 on **both** halves — a genuine
two-sample filter, not a single-sample cherry-pick, which materially limits the inflation.

**Nominal evidence:** Spearman p = 1.6 × 10⁻¹⁴; within-year permutation p = 5 × 10⁻⁵ (§18 below).

**Selection-aware interpretation:** even a crude Bonferroni over 37 screens leaves p < 10⁻¹² — the nominal
significance is far too large to be produced by searching 37 variables. **Multiplicity is not the problem
with this finding, and I decline to use it as an objection.** The finding survives selection-aware scrutiny
comfortably. It fails for the entirely different reason set out in §6–§8: the association is real and the
p-value is honest, but the variable is a re-expression of distance-to-target.

This distinction matters. A selection-inflation verdict would imply "measure more data and it may hold up."
That is **not** my finding.

---

## 18 — BOOTSTRAP AND PERMUTATION (§21, §22)

Bootstrap is event-level, which is day-level here (one event per day, §16) — no naive bar-level resampling
was used anywhere. CIs appear inline in §5, §11, §12, §14.

Permutation: labels shuffled **within year**, preserving chronology and the year-level base rates
(20,000 draws each).

| test | observed | permutation p |
|---|---|---|
| AUC(x, A), all 133 | 0.167 | **0.00005** |
| AUC(x, A), room > 0 only | 0.286 | **0.00125** |
| AUC(x, new-high-EVER), all 133 | 0.464 | 0.341 (n.s.) |

The association with the label is not a chance artifact. The association with *whether the market actually
goes up* does not exist.

---

## 19 — RESIDUAL SIGNAL AFTER REMOVING THE TAUTOLOGY

The fairest possible test for Alpha: delete the 26 definitionally-certain events and re-run.

```
  n = 107      base P(A) = 0.215
  AUC(x)    = 0.286   95% CI [0.181, 0.400]    permutation p = 0.00125
  AUC(room) = 0.208   95% CI [0.102, 0.328]
  joint logistic:  b_x = -0.00567 (z = -0.34)      b_room = -0.05309 (z = -2.52)
  Spearman(x, A | room>0) = -0.305, p = 0.0011
```

**A residual association survives — and it is still not the feature's.** Even on the tautology-free subset,
`room` dominates and `x` adds nothing (z = −0.34). The residual is the *continuous* form of the same
distance effect: shorter distance to a fixed target within four hours is easier to reach, whether the
distance is zero or thirty pips.

---

## 20 — OTHER PRE-EVENT CONTROLS (§16)

Using variables already present and causal. No new feature mining was performed.

| control | AUC(A) | corr with x | b_x z | b_ctrl z |
|---|---|---|---|---|
| asia_range | 0.468 | −0.355 | −5.62 | −3.40 |
| sweep_excursion | 0.438 | +0.014 | −5.10 | −0.23 |
| london hour | 0.522 | −0.031 | −5.10 | +0.76 |
| ~~headroom_up~~ | 0.850 | **−0.977** | +0.26 | +2.01 |

`plh_minus_asiahigh` survives sweep-excursion, session-time, and Asia-range controls. **It fails only the
room control** — which is the one the CEO made mandatory, and the one that is not really a control at all
but the same measurement.

**`headroom_up` must be struck from the control list**: I verified `headroom_up = AsiaHigh − c[E0] =
−(x + dist_close_plh)` with max residual `0.0000000000` and corr(headroom_up, −x) = 0.977. It is the feature
sign-flipped, not an independent variable. I report it here only to prevent it being cited as corroboration.

---

## 21 — LIMITATIONS OF THIS AUDIT

1. **Single parent, single instrument, single family.** Findings apply to XAUUSD London/Pre-London-High
   sweeps, 2021-11 → 2023-12, N=133. Nothing here generalises to other families.
2. **The Asia-mid objective is inherited, not chosen by me.** My §7/§8 conclusions are conclusions about
   *this label definition*. A different objective could yield a different — and possibly genuine — answer.
   I did not test one; that would be new research, outside `INDEPENDENT_AUDIT_ONLY`.
3. **No claim that PLH↔AsiaHigh geometry is economically meaningless.** I claim only that *against this
   label* it carries no information beyond distance-to-target. Those are different statements.
4. **The n=6 and n=2 residual cells** in §12 are too small to support any conclusion, and I draw none from
   them beyond noting the collapse.
5. `logit` was used strictly as an audit instrument per §23. No classifier was built, fitted for prediction,
   tuned, or retained.

---

## 22 — REQUIRED CONCLUSIONS (§25) — direct answers

| # | Question | Answer |
|---|---|---|
| 1 | Parent reproduced exactly? | **YES** — N=133, 133 unique days, A49/B37/C46/D1, all four bins to 3 dp |
| 2 | Feature strictly causal? | **YES** — both levels frozen before the event window; no leakage |
| 3 | Continuous relationship real? | **YES as measured, NO as interpreted** — ρ=−0.557, p=1.6e−14, but it is a relationship with distance-to-target |
| 4 | Monotonic? | **YES** — smooth at decile resolution, not a bin artifact; median room is monotone alongside it |
| 5 | Survives DISC→CONF? | **YES in direction** — but `room` is stronger in both halves |
| 6 | Survives 2021/2022/2023? | **YES in direction** — 2021 is 2 months, not a year |
| 7 | Survives temporal blocking? | **YES** — all 4 blocks, no short cluster explains it |
| 8 | Survives selection-aware scrutiny? | **YES** — 1 of 37 screens, but p survives Bonferroni by 12 orders of magnitude. Multiplicity is *not* the defect |
| 9 | Survives available-room / label-geometry controls? | **NO — FAILS BOTH.** b_x z=−0.32 with room in the model; P(A\|room≤0)=1.000 on 53% of all A events; median class-A "reversal" completes in 1 bar |
| 10 | Specifically reduces NEW_HIGH_FIRST? | **NO** — AUC 0.464, CI [0.332, 0.600], p=0.34. The `<−40` bin has the *highest* rate of eventual new highs (0.957) |
| 11 | Is the <−40p / 87% cell robust or fragile? | **Robust as a proportion** (Wilson [0.679,0.955], LOO −0.006, 23 distinct days, both splits) — **but 17 of its 20 successes are definitional; strip them and n=6, P(A)=0.500** |
| 12 | Enough to justify threshold-discovery research? | **NO** |
| 13 | Enough to justify execution research? | **NO** |

---

## 23 — WHAT ALPHA GOT RIGHT

Stated because a fair audit reports both directions.

- The parent was recovered **unchanged**; no retuning to fit the finding.
- Every published number is **exactly correct**. Not one figure failed reproduction.
- Alpha **did** apply position controls — and they worked, correctly killing every path feature.
- Alpha **identified `dist_asia_mid` as a proximity-to-target confound and excluded it on its own initiative.**
  It was one algebraic step from this audit's conclusion.
- Alpha refused to promote a threshold, refused to build a classifier, and explicitly declined to emit
  `PLH_FEATURE_SET_READY_FOR_CLASSIFIER_RESEARCH`. Those disciplines held.
- Alpha routed this to independent audit rather than self-certifying. That is the process working.

**The error was narrow and specific:** the claim that `plh_minus_asiahigh` is *"position-independent by
construction"* and *"needs no adjustment"* (report lines 30, 69). It is `room − asia_range/2`. The exemption
was granted on a structural argument that the data contradicts exactly.

---

## 24 — RECOMMENDATION (statistical only; no authorization granted)

The productive finding here is **not** the feature — it is the diagnosis of why the feature appeared.

**The Asia-mid objective is a fixed price level, so the difficulty of the target varies event to event, and
19.5% of events start at or past it.** Any pre-event variable correlated with position will "predict" this
label. That is a property of the label, not of the market, and it will contaminate *every* feature-mapping
exercise built on this parent — not merely this one.

For the CEO's consideration, as a possible future Alpha mandate (**I am not authorizing it**):

1. Redefine the outcome so difficulty is constant — a target at fixed distance, or normalized by ATR or by
   the event's own risk unit — and require `room > 0` at E0 for an event to be admissible at all.
2. Re-run the *existing* feature map against the corrected label. Features that failed may pass, and this
   one may fail differently.
3. Treat `NEW_HIGH_FIRST` reduction as the primary endpoint, since P(new-high-ever) = 0.902 makes it the
   binding constraint for any short thesis in this family.

---

## 25 — TERMINAL VERDICT

```
PLH_ASIA_SPATIAL_FEATURE_AUDIT_FAIL
PLH_ASIA_SPATIAL_FEATURE_NOT_SUPPORTED
```

**No threshold-discovery mandate is justified. No execution research is justified. No execution
authorization is granted or implied.**

The parent is sound, the feature is causal, and Alpha's arithmetic is exact. The feature is nonetheless
not supported: it is `dist_asia_mid` minus half the Asia range, it contributes nothing once room is
modelled (z = −0.32), it does not reduce the probability of an adverse up-move (p = 0.34), and the
label awards `CLEAN` with certainty to the 26 events that had already arrived at the objective — which
supply 53% of all class-A observations.

---

*Statistician division — independent statistical validation. Verdicts are scoped strictly to the evidence
examined and are not transferable to adjacent claims.*

# STAT_GOVERNED_Sx_REAL_COST_INDEPENDENT_VALIDATION_V1

**Mandate:** Statistician independent validation of three Alpha candidates from the governed S1–S51 grammar
re-scored at ratified live-shadow cost.
**Source:** `ai_quant_lab-alpha-automation` @ `d2e76cd` (branch `alpha-automation-v1`), queue section
"GOVERNED-Sx-GRAMMAR REAL-COST SURVIVORS".
**Division:** Statistician. **Date:** 2026-09-22.
**Code:** `statistician/gov_sx/` — `repro.py`, `leak.py`, `s49.py`, `sanity.py`, `fwer.py`, `robust.py`,
`null2.py`, `final.py`.

## VERDICTS

| candidate | label |
|---|---|
| **CAND-HTFSX-01** — S1 PDH sweep + displacement | **CURRENT_REGIME_ONLY_PENDING_PROSPECTIVE** |
| **CAND-HTFSX-02** — S9 H4-trend + H1-align | **STATISTICAL_VALIDATION_FAIL** |
| **CAND-HTFSX-03** — S20 H4-up + breakout | **STATISTICAL_VALIDATION_FAIL** |

**No promotion. No strategy definition was altered.** All protections untouched.

---

## 1 — REPRODUCTION (§2): EXACT, all three

| id | family | N | WR | BASE | STRESS | PF | recent | reproduced |
|---|---|---|---|---|---|---|---|---|
| `85dfa65a9ce1` | S1 | 322 | 0.391 | **+0.2221** | +0.1662 | 1.390 | +0.2851 | **YES** |
| `047d776a1bcb` | S9 | 665 | 0.460 | **+0.1646** | +0.1462 | 1.368 | +0.2516 | **YES** |
| `601e20753a4a` | S20 | 777 | 0.323 | **+0.1609** | +0.1189 | 1.238 | +0.1935 | **YES** |

Every claimed figure reproduces to the reported precision on `mstrat.simulate`, TICK=0.01,
`spread_ticks = rt/(2·TICK)`, `slip=0`, round-turn 0.05 BASE / 0.24 STRESS. The cost arithmetic is correct:
cost/side = 0.025, and R subtracts 2·cost = 0.05.

**Two corrections to the hand-off, both mechanically verified.**

1. **L2 is worse than Alpha disclosed.** The hand-off says CAND-HTFSX-01 "concentrates post-2021". It does
   not — **all three candidates trade only from 2023-01-03 onward.** In `mstrat.load()`, `pdh`, `pdl`,
   `h4_trend_up`, `h1_trend_up` and `d1_trend_up` are **all 23.7% non-null with an identical first value at
   2023-01-03**. S1's `liq_ref=pdh_pdl` therefore has the same 2023 wall as S9/S20. Trade-year distribution
   for all three: 2023/2024/2025/2026 only.
2. **Trade frequency is understated ~4.3×.** The screen computes `tpy = N / 15.00 years` while every trade
   lies inside a 3.5-year active window. True rates: **S1 ≈ 91/yr** (not 21), **S9 ≈ 189/yr** (not 44),
   **S20 ≈ 221/yr** (not 52). This matters for capacity and for prospective-test feasibility, and it is a
   correction *in the candidates' favour* on the latter.

---

## 2 — S49 REJECTION (§2): INDEPENDENTLY CONFIRMED, mechanism restated

Alpha rejected 4 gate-passing S49 configs. I confirm the rejection and identify the mechanism precisely —
it is not "median hold 0.0 bars" but an **inverted stop**:

```
S49 N=4/mode=fade/stop=bar/exit=time  (74,615 setups)
  stop on the WRONG SIDE of entry      : 97.2%  (stop >= entry for a long)
  stop touched on the ENTRY BAR itself : 99.7%
  R distribution                        : [-9.54 … median +0.90 … max +225.68]
```

With the stop on the wrong side the risk denominator is degenerate, is caught by the ENGINE-v2 floor, and
R becomes a ratio against an artificial denominator. `PF 3.455` on `WR 0.786` is an arithmetic consequence,
not an edge. **REJECTION CONFIRMED.**

**The same pathology does not touch the three candidates** — checked directly on their setup dicts:

| | wrong-side stop | caught by floor | stop hit on entry bar | median risk |
|---|---|---|---|---|
| S1 | 3.73% | 1.24% | 13.69% | 6.99 USD (70 pips) |
| S9 | 0.04% | 0.00% | 0.48% | 14.22 USD (142 pips) |
| S20 | 0.00% | 0.00% | 6.34% | 5.24 USD (52 pips) |
| *S49 (artifact)* | *97.2%* | — | *99.7%* | — |

---

## 3 — L5 LEAKAGE AUDIT: **PASS**, verified mechanically

Two independent tests, neither by code reading:

**(A) HTF context provenance.** Rebuilt `h4_trend_up` / `h1_trend_up` independently from the raw H1/H4
files with availability forced to `bar_open + period` (strict close-time), then as-of joined:

```
h4_trend_up : 84,286 comparable bars, agreement with strictly-causal reconstruction = 1.0000
h1_trend_up : 84,294 comparable bars, agreement = 1.0000
bars where the source close_time exceeds the bar's own time (a leak) = 0  for both
pdh : agreement 0.9882, bars with avail > time = 0
```

**(B) Prefix stability of the whole `setups` + `simulate` chain under truncation.** Recomputed setups and
simulation on `d[:K]` and compared trades with exit well before K:

```
K = 330,000 / 345,000 / 353,000 × 3 candidates = 9 comparisons
IDENTICAL in 9 / 9
```

`mtf.py`'s `avail = time.shift(-1)` + `merge_asof(direction='backward')` is the **correct** pattern — the
opposite of the bucket-floor bug repaired in `91b7415`. **`LEAKAGE_VERDICT = CLEAN` for all three.**

---

## 4 — L1 MULTIPLE TESTING: all three **FAIL** FWER

Re-ran the entire grammar capturing month-clustered t-statistics per config.

**First, the effective family size.** 2,448 configs attempted, **2,270** scored with ≥100 trades — but only
**1,782 distinct result signatures**: **488 configs (21.5%) are exact duplicates of another**. The S1
candidate has an exact twin (`liq_lb=20` and `liq_lb=50` give byte-identical results — that dimension is
inert for this config). The 34 reported survivors are **24 distinct**.

```
Bonferroni FWER 5%, m = 2,270 (all)        : requires t > 4.09
Bonferroni FWER 5%, m = 1,782 (distinct)   : requires t > 4.03
BH-FDR q = 0.05 over all 2,270             : p-threshold 3.05e-03  (t > 2.74)
```

| candidate | N | mean | clustered SE | **t** | p (1-sided) | Bonferroni | BH-FDR | rank by t |
|---|---|---|---|---|---|---|---|---|
| S1 `85dfa65a9ce1` | 322 | +0.2221 | 0.0887 | **+2.50** | 6.1e-03 | **FAIL** | **FAIL** | **175 / 2270** |
| S9 `047d776a1bcb` | 665 | +0.1646 | 0.0472 | **+3.49** | 2.5e-04 | **FAIL** | PASS | **113 / 2270** |
| S20 `601e20753a4a` | 777 | +0.1609 | 0.0678 | **+2.37** | 8.8e-03 | **FAIL** | **FAIL** | **188 / 2270** |

**None survives FWER.** S9's BH pass is the only positive, and BH here is a weak criterion: the p-value
distribution that sets its threshold is contaminated (the top of the whole grammar's t-ranking is the S49
artifact, t up to **77.5**). Excluding the demonstrated-artifact families changes nothing (threshold
identical at 3.05e-03), so the BH result is at least not driven by them — but a criterion that "discovers"
153 of 2,270 configs in a grammar whose own best performers are implementation bugs should not carry a
promotion.

**The candidates were not selected for significance.** By t-statistic they rank **113th, 175th and 188th**
of 2,270. They were selected by Alpha's gate (worst-era + drop-best-5% + recency), which is a reasonable
screening heuristic but is not a test.

---

## 5 — L3 MATCHED-LONG NULL: the decisive test

Alpha benchmarked against **naive long (−0.128R)**. That is the wrong null. The right one holds the
regime, the direction and the payoff geometry fixed and randomises only the **entry timing** — which is the
only thing the strategy claims to supply.

**Construction (400 replicates each):** for every real trade, draw a random bar **within the same calendar
month**, go **long**, use **that trade's own risk distance**, exit at the same **rr3**, run it through the
same `mstrat.simulate` (same fills, same stop-wins-ties, same overlap suppression, same cost).

| candidate | real mean | **matched-long null** | excess | **empirical p** |
|---|---|---|---|---|
| **S1** `85dfa65a9ce1` | +0.2221 | +0.0664 (sd 0.0855) | **+0.1557** | **0.0275** |
| **S9** `047d776a1bcb` | +0.1646 | **+0.1365** (sd 0.0491) | **+0.0281** | **0.2825** |
| **S20** `601e20753a4a` | +0.1609 | **+0.1475** (sd 0.0573) | **+0.0134** | **0.3875** |

**This is the finding that decides two of the three.** Randomly-timed long entries with the same wide stop
and rr3 target, in the same months, already earn **+0.137 R (S9)** and **+0.148 R (S20)** — i.e. **83% and
92% of those candidates' entire expectancy**. Their entry logic adds +0.028 R and +0.013 R, neither
distinguishable from noise. They beat naive-long only because naive-long was measured with different
geometry over a different window.

**S1 is genuinely different**: its matched null is +0.066 and it clears by +0.156 R at p = 0.0275. Its
entry logic carries real information — inside 2023–2026.

*Method note, disclosed:* my first null run mapped each trade's risk through a fragile zip and reported
S1 at p = 0.0000 / excess +0.2200. Rebuilt with an explicit `entry-bar → stop` mapping (S1 has 101 setups
sharing an `ei`), the honest figures are **p = 0.0275 / +0.1557**. S9 and S20 were unaffected (no duplicate
`ei`). The corrected numbers are the ones above.

---

## 6 — L2 CALENDAR ERAS: tested on the ratified historical-context panel

The screen's "eras" are chronological **thirds of a 2023–2026 trade population**, not calendar eras. To get
true eras I re-ran **the same frozen specs, unchanged**, on `htf_context_historical.load_mstrat_historical()`
— the Statistician-ratified gap-safe panel that carries the `*_from_M15_v2` context back to 2011 (coverage
23.7% → 55.4%, byte-identical columns). **This is a robustness test on an alternative ratified source, not a
redefinition of any candidate.**

| candidate | 2011-13 | 2014-16 | 2017-19 | 2020-22 | 2023-26 | eras + | full-panel mean (t) | **pre-2023 only** |
|---|---|---|---|---|---|---|---|---|
| **S1** | −0.046 | −0.078 | +0.046 | +0.138 | +0.194 | 3/5 | +0.076 (t +1.24) | **+0.015 (t +0.18)** |
| **S9** | −0.030 | +0.146 | +0.073 | −0.145 | +0.157 | 3/5 | +0.061 (t +1.87) | **+0.001 (t +0.02)** |
| **S20** | +0.133 | +0.184 | +0.160 | −0.056 | +0.145 | **4/5** | +0.123 (t +3.09) | **+0.106 (t +2.09)** |

**This inverts the ranking.** On the 2023–2026 selection window S1 looks best (+0.222). On true calendar
history **S1 and S9 have essentially nothing before 2023** (t = +0.18 and +0.02 — not weak, absent), while
**S20 is the only one with a pre-2023 signal** (+0.106, t +2.09, positive in 4 of 5 eras including the
2011–2013 gold bear).

Matched-long null repeated on the historical panel: S1 p = 0.075 (excess +0.078), S9 p = 0.613 (excess
**−0.011**, i.e. *worse* than random long), S20 p = 0.183 (excess +0.037).

---

## 7 — TAIL / OUTLIER DEPENDENCE

| | top-1% | top-5% | drop-1% | drop-3% | drop-5% | drop-10% | winsorized 5/95 |
|---|---|---|---|---|---|---|---|
| S1 | 12.7% | 67.2% | +0.196 | +0.142 | **+0.077** | **−0.084** | +0.224 |
| S9 | 16.4% | 90.3% | +0.139 | +0.081 | **+0.017** | **−0.147** | +0.165 |
| S20 | 16.8% | 91.0% | +0.135 | +0.074 | **+0.015** | **−0.151** | +0.161 |

**Winsorizing changes nothing** (±0.002) — there is no freak-trade dependence; wins are structurally capped
at 3R. But **drop-best-5% leaves S9 and S20 at +0.017 and +0.015**, i.e. essentially nothing, and
drop-best-10% turns all three negative. Alpha's gate required only `db5 > 0`; S9 and S20 clear it by
0.015 R. For a WR-32–46% rr3 payoff this concentration is expected, so it is not a defect — but it means
the margin is thin enough that the drop-5% figure carries almost no information about robustness.

---

## 8 — COST SENSITIVITY

| round-turn USD | 0.05 (BASE) | 0.16 | 0.24 (STRESS) | 0.50 | 1.00 | 2.00 |
|---|---|---|---|---|---|---|
| S1 | +0.2221 | +0.1890 | +0.1662 | +0.0939 | −0.0452 | −0.2325 |
| S9 | +0.1646 | +0.1539 | +0.1462 | +0.1209 | +0.0723 | −0.0249 |
| S20 | +0.1609 | +0.1366 | +0.1189 | +0.0614 | −0.0492 | −0.2660 |

Break-even round-turn ≈ **0.9 USD (S1)**, **1.8 USD (S9)**, **0.9 USD (S20)** — 18×–36× the BASE model.

**But this is a weaker result than it looks, and the reason matters.** The modelled cost is only
**0.004–0.010 R** because the stops are 52–142 pips wide. STRESS moves expectancy by just 0.04–0.05 R.
**These strategies are cost-insensitive because they risk a lot per trade, not because they are efficient** —
and a 52–142-pip structural stop shifts the real execution risk from spread onto slippage and gap
exposure, neither of which the shadow cost model captures. `AI_TRADER_SHADOW_COST_MODEL_v1` itself records
that commission is never captured and there are no real fills.

---

## 9 — PER-CANDIDATE VERDICTS

### CAND-HTFSX-01 — S1 `85dfa65a9ce1` → **CURRENT_REGIME_ONLY_PENDING_PROSPECTIVE**
Reproduced exact · leakage clean · **beats the matched-long null (p = 0.0275, +0.156 R)** — the only one of
the three whose entry logic demonstrably carries information. But: **fails FWER** (t 2.50 vs 4.03) and BH,
ranks 175/2270; **pre-2023 expectancy is +0.015 at t = +0.18** — the edge does not exist outside the
selection regime; drop-best-10% negative. The p = 0.0275 is a **post-selection** p-value from a
2,270-config search and cannot be read at face value.

### CAND-HTFSX-02 — S9 `047d776a1bcb` → **STATISTICAL_VALIDATION_FAIL**
Reproduced exact · leakage clean · but **83% of its expectancy is reproduced by randomly-timed long entries
with the same geometry** (null +0.1365 vs real +0.1646, p = 0.28), and on the historical panel it is
**worse than its own null** (excess −0.011, p = 0.61). Pre-2023: **t = +0.02**. Fails FWER. Its BH pass is
the only surviving positive and it is not enough. **The candidate is long-beta plus rr3 geometry.**

### CAND-HTFSX-03 — S20 `601e20753a4a` → **STATISTICAL_VALIDATION_FAIL**
Reproduced exact · leakage clean · **best cross-era behaviour of the three** (4/5 calendar eras positive,
pre-2023 t = +2.09). But on the window it was actually selected on, it **adds +0.013 R over a matched-long
null (p = 0.39)** — 92% of its expectancy is the null. Fails FWER and BH. The failure mode is
long-beta explanation, not regime confinement — which is why it is a FAIL rather than a pending-prospective.
**Flagged for the CEO:** its pre-2023 behaviour is the one genuinely interesting signal in this batch and
would justify a *separately specified* hypothesis, tested against a matched null from the start. As
submitted, it fails.

---

## 10 — MINIMUM PATH FOR ANYTHING PENDING (CAND-HTFSX-01 only)

L4 stands: the full governed record is consumed, data ends 2026-07-27, **no untouched holdout exists**;
everything above is HYPOTHESIS_ONLY.

```
Minimum clean validation for CAND-HTFSX-01:
  data      : M15 XAUUSD strictly AFTER 2026-07-27, governed and hash-frozen before any look
  primary   : excess over the SAME matched-long null (same month, same risk, same rr3), not over zero
              and not over naive-long
  power     : to detect the in-sample excess (+0.156 R, clustered SE 0.0887 at N=322) at 80% / one-sided
              5% requires ~640 trades -> ~7 years at the true 91 trades/yr. A 2-year window gives ~180
              trades and is UNDERPOWERED.
  pre-reg   : the spec, the null construction and the stopping rule frozen and hashed before the window opens
  correction: the post-selection status must be carried -- this is one config drawn from 2,270
```

The power figure is the uncomfortable number and I am not going to soften it: **a prospective test of this
candidate at the required power is a multi-year commitment.** The alternative that is not multi-year is
independent-data replication (a second venue's XAUUSD M15, or a correlated instrument) — cheaper, weaker,
and it would not resolve the regime question.

---

## 11 — FINAL

```
CAND-HTFSX-01  S1   reproduced YES | FWER FAIL | BH FAIL | eras 3/5, pre-2023 t +0.18 |
                    matched-null p 0.0275 (+0.156R) | tail drop10% neg | leakage CLEAN
                    -> CURRENT_REGIME_ONLY_PENDING_PROSPECTIVE

CAND-HTFSX-02  S9   reproduced YES | FWER FAIL | BH pass (contaminated criterion) | eras 3/5, pre-2023 t +0.02 |
                    matched-null p 0.2825 (+0.028R), historical p 0.613 (-0.011R) | leakage CLEAN
                    -> STATISTICAL_VALIDATION_FAIL

CAND-HTFSX-03  S20  reproduced YES | FWER FAIL | BH FAIL | eras 4/5, pre-2023 t +2.09 |
                    matched-null p 0.3875 (+0.013R) | leakage CLEAN
                    -> STATISTICAL_VALIDATION_FAIL

S49 rejection      : INDEPENDENTLY CONFIRMED (97.2% wrong-side stops, 99.7% same-bar stop, R max +225.7)
Same pathology on the three: NO
L6                 : Part B (rr3 on structural/ATR stop + ENGINE-v2 floor) is NOT a ratified structural
                     primitive -- routed to the risk layer, not treated as validated here.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

Nothing promoted, nothing added to StrategyCatalog, no strategy definition altered. Untouched: **S5, AI
Trader, P007, MGMT-004, MT5, StrategyCatalog, CTS, GC, COT**. Alpha's own artifacts were read-only.

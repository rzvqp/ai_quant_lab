# ALPHA_XAUUSD_H1_PROTREND_DISCOVERY_REPORT

**Mandate:** `ALPHA-XAUUSD-H1-PROTREND-DISCOVERY-001` · **Date:** 2026-08-21
**Terminal status:** `H1_PROTREND_ALPHA_CANDIDATES_READY_FOR_CEO_REVIEW` — **exactly ONE** modest, regime-conditioned candidate survives the full deep-robustness battery (`H1-B-bo-acc-SHORT`); the headline "21 fast-survivors" is shown to be largely illusory.
**VALIDATION_ACCESS_COUNT = 0. FINAL_HOLDOUT_ACCESS_COUNT = 0.** Manifest-gated H1 population only; per-block (no cross-gap); RATIFIED cost; no retuning; broker disabled.

---

## 1. Question and one-line answer
**Question (item 24):** Does H1 XAUUSD pro-trend continuation offer a *materially stronger and more robust* edge-to-cost relationship than M15?
**Answer:** **Partially, and less than the surface suggests.** H1 improves the *per-trade cost fraction* (STRESS cost = **1.3%** of median risk on H1 vs **3.1%** on M15) and produces a dramatic *fast-falsification* uplift (**21/28** H1 IDs clear STRESS vs **1/44** on M15). But under a deep-robustness battery (best-5/10%-removed tail, within-block temporal concentration, execution degradation, out-of-DEV CALIBRATION), **20 of 21 collapse** with the identical catastrophic tail/event-concentration signature seen on M15. **Exactly one** genuine, H4-gate-validated candidate emerges — a modest short-continuation mechanism whose edge is concentrated in the 2011–2013 secular gold downtrend. H1 does **not** materially and broadly beat M15; it surfaces **one** candidate M15 could not.

## 2. Provenance / data integrity (item 5 — prerequisite satisfied)
| field | value |
|---|---|
| population file | `data/market/OANDA_XAUUSD_H1_from_M15_v2.csv` (M15→H1 aggregation ×4, **block-existence rule**, manifest-gated) |
| **why not native H1** | native `OANDA_XAUUSD_H1` is `AWAITING_REGIME_MAP` (no ratified manifest split) → **rejected**, not used |
| discovery blocks (DEV) | block0 `2011-07-26→2013-09-27` (13,397 H1 bars) + block1 `2016-01-11→2018-04-06` (13,213 H1 bars) |
| **DEV bars** | **26,610** · sha256(open/high/low/close, first 16) = **`1dd43c1187d01428`** |
| CALIBRATION (block2) | `2020-08-11→2021-09-05`, 6,310 bars — used **only** to stress survivors out-of-DEV |
| VALIDATION (block3) / FINAL_HOLDOUT | **never loaded, never evaluated** |
| cross-gap guard | evaluation is **strictly per-block** (b0 and b1 run on separate slices) → the 2013→2016 unratified gap is **never bridged** |
| leak assert | `h1.loc[DEV,"dt"].max() < 2018-05-01` enforced at load (passed) |

## 3. Cost model (RATIFIED, unchanged)
`AI_TRADER_SHADOW_COST_MODEL_v1` — **BASE round-trip 0.05**, **STRESS round-trip 0.24** (price units). Applied via `spread_ticks=0`, `slip_ticks=round_trip/(2·TICK)`, TICK=0.01; stop floor `max(2·spread, 0.05, 0.10·ATR14)`; entry **next-bar open**; full round-trip debited in R. **STRESS 0.24 was NOT lowered** despite larger H1 targets — the whole experiment is whether larger targets earn their way past the *same absolute* cost.

## 4. HTF pro-trend context (causal)
H4 and D1 trend = **EMA20 > EMA50** on each HTF's own closes (`OANDA_XAUUSD_H4_from_M15_v2.csv`, `_D1_from_M15_v2.csv`), merged onto H1 by causal `merge_asof(direction="backward")` (last **closed** HTF bar only). Pro-trend candidate = **H4-aligned** (long only in H4-up, short only in H4-down). Unconditional and D1-aligned variants recorded for gate-value analysis (§7).

## 5. Hypothesis IDs — 28 new H1 IDs, 9 families, both directions (item cap: ≤100)
| Family | Mechanism | LONG | SHORT |
|---|---|---|---|
| A pullback | depth-2 / depth-3 continuation | ✓✓ | ✓✓ |
| B breakout+accept | 20-bar breakout, raw + acceptance | ✓✓ | ✓✓ |
| C breakout+retest | 20-bar breakout, retest-and-go | ✓ | ✓ |
| D displacement+accept (NEW ids) | ≥1.0 / ≥1.5 ATR body + 2-bar accept | ✓✓ | ✓✓ |
| E compression→expansion | ATR-contraction then in-trend expansion | ✓ | ✓ |
| F failed-counter | failed counter-move + resume | ✓ | ✓ |
| G momentum | 3/4 consecutive closes, path-efficiency | ✓✓✓ | ✓✓✓ |
| H structure | HL/LH structure continuation | ✓ | ✓ |
| L acceleration | rising displacement + shortening pullbacks | ✓ | ✓ |

**Early-stop rationale (28 of ≤100):** the binding constraint is **deep robustness, not family breadth**. Across 9 families × 2 directions, every fast-survivor except one dies the *same* deep-tail death; adding families I/J/K/M (session/flag variants already shown cost-fragile on M15) would add fast-survivors that reproduce the identical collapse. Info-gain collapsed → stopped. LONG IDs 14, SHORT IDs 14.

## 6. Fast-falsification results (STRESS, H4-aligned)
| status | count | ids |
|---|---|---|
| **SURVIVE (fast)** | **21** | 8 LONG + 13 SHORT |
| COST_FRAGILE | 3 | pb3-SHORT, bo-retest-LONG, consec3-LONG |
| FAIL | 4 | pb3-LONG, da-w1.5-LONG, failcnt-LONG, consec4-LONG |
| SPARSE | 0 | — |

**This is the "H1 looks great" illusion**: 21/28 clear STRESS vs 1/44 on M15. §12 shows why it does not hold.

## 7. Does the pro-trend (H4) gate earn its value? (item 7) — **YES for the one survivor, decisively**
For the lone deep-survivor `H1-B-bo-acc-SHORT` the H4-down gate is **the entire edge**:
| gate | STRESS avg_R | n |
|---|---|---|
| **unconditional** | **−0.008** | 331 |
| **H4-aligned (short in H4-down)** | **+0.098** | 179 |
| D1-aligned | −0.011 | 160 |
Without the H4-trend context there is **no edge**; H4 alignment converts a negative unconditional mechanism into a positive one. This is the defining property of a genuine pro-trend continuation edge — and it is exactly what the M15 pro-trend campaign systematically *lacked* (there the trend gate usually did **not** add value). D1 alignment does **not** work — the effective horizon is H4, not D1.

## 8–11. Survivor queue / cost-fragile / fails
- **Fast-survivors (21):** A-pb2 (L/S), B-bo-acc (L/S), B-bo-raw (L/S), C-bo-retest (S), D-da-w1.0 (L/S), D-da-w1.5 (S), E-comp (L/S), F-failcnt (S), G-eff (L/S), G-consec3 (S), G-consec4 (S), H-hllh (L/S), L-accel (L/S).
- **Cost-fragile (BASE+ / STRESS−):** pb3-SHORT, bo-retest-LONG, consec3-LONG.
- **Fail:** pb3-LONG, da-w1.5-LONG, failcnt-LONG, consec4-LONG.

## 12. DEEP ROBUSTNESS BATTERY — the 21 collapse to 1 (the core scientific result)
Each fast-survivor was subjected to: **deep tail** (best-5% and best-10% of trades removed), **within-block temporal concentration** (max single-year share of total R), **per-block average** (both DEV blocks positive?), **execution degradation** (+1-bar entry delay; 1.5× stop floor), and **out-of-DEV CALIBRATION** (block2). ROBUST ⇔ best-5%-removed > 0 **and** max-year-share ≤ 0.60 **and** both-blocks-avg > 0 **and** execution-robust.

| id | STRESS avg | **best5_rem** | best10_rem | maxYr% | pb_avg b0 / b1 | CALIB STRESS | exec Δ / floor | verdict |
|---|---|---|---|---|---|---|---|---|
| **H1-B-bo-acc-SHORT** | **+0.098** | **+0.022** | −0.028 | 0.43 | **+0.169 / +0.008** | **+0.057** | +0.117 / +0.098 | **ROBUST** |
| H1-C-bo-retest-SHORT | +0.313 | **−0.270** | −0.589 | 0.53 | +0.334 / +0.508 | +0.081 | +0.631 / +0.313 | FRAGILE (tail) |
| H1-E-comp-SHORT | +0.340 | −0.014 | −0.218 | 0.67 | +0.412 / +0.342 | −0.087 | +0.305 | FRAGILE (tail, CALIB−) |
| H1-G-eff-SHORT | +0.185 | −0.126 | −0.275 | 0.55 | +0.317 / +0.146 | +0.050 | +0.290 | FRAGILE (tail) |
| H1-G-consec4-SHORT | +0.120 | −0.141 | −0.300 | 0.53 | +0.229 / +0.103 | −0.174 | +0.091 | FRAGILE (tail, CALIB−) |
| H1-F-failcnt-SHORT | +0.116 | −0.128 | −0.267 | 0.89 | +0.133 / +0.201 | −0.189 | +0.325 | FRAGILE (tail, conc) |
| H1-L-accel-SHORT | +0.111 | −0.172 | −0.315 | 1.21 | +0.345 / −0.063 | −0.201 | +0.317 | FRAGILE (tail, b1<0) |
| H1-H-hllh-SHORT | +0.103 | −0.201 | −0.364 | 0.60 | +0.214 / +0.099 | −0.091 | +0.032 | FRAGILE (tail) |
| H1-D-da-w1.5-SHORT | +0.091 | −0.035 | −0.125 | 1.52 | +0.149 / +0.045 | +0.054 | +0.096 | FRAGILE (tail, conc) |
| H1-A-pb2-SHORT | +0.081 | −0.315 | −0.527 | 0.68 | +0.204 / +0.094 | −0.127 | +0.017 | FRAGILE (tail) |
| H1-B-bo-raw-SHORT | +0.070 | −0.017 | −0.077 | 0.47 | +0.130 / +0.031 | +0.156 | +0.046 | FRAGILE (tail) |
| H1-G-consec3-SHORT | +0.021 | −0.250 | −0.402 | 1.82 | +0.125 / +0.010 | +0.043 | +0.097 | FRAGILE (tail) |
| H1-D-da-w1.0-SHORT | +0.001 | −0.196 | −0.291 | 104 | +0.049 / −0.004 | +0.060 | −0.022 | FRAGILE (≈0 net) |
| H1-G-eff-LONG | +0.083 | −0.126 | −0.264 | 0.76 | +0.048 / +0.210 | −0.177 | +0.050 | FRAGILE (tail, CALIB−) |
| H1-D-da-w1.0-LONG | +0.050 | −0.096 | −0.189 | 1.34 | −0.041 / +0.185 | +0.103 | −0.038 | FRAGILE (tail, b0<0) |
| H1-E-comp-LONG | +0.048 | −0.233 | −0.403 | 2.20 | −0.096 / +0.356 | −0.162 | +0.028 | FRAGILE (tail, b0<0) |
| H1-B-bo-acc-LONG | +0.048 | −0.007 | −0.045 | 0.62 | +0.005 / +0.112 | −0.051 | +0.034 | FRAGILE (tail, CALIB−) |
| H1-A-pb2-LONG | +0.039 | −0.315 | −0.501 | 0.64 | +0.041 / +0.176 | −0.059 | −0.008 | FRAGILE (tail, exec−) |
| H1-B-bo-raw-LONG | +0.029 | −0.046 | −0.095 | 0.82 | +0.001 / +0.077 | −0.086 | +0.019 | FRAGILE (tail, conc) |
| H1-L-accel-LONG | +0.007 | −0.213 | −0.325 | 4.76 | +0.014 / +0.086 | −0.377 | −0.074 | FRAGILE (all) |
| H1-H-hllh-LONG | +0.005 | −0.293 | −0.446 | 10.7 | −0.064 / +0.179 | −0.070 | −0.006 | FRAGILE (all) |

**Read-out:** every FRAGILE row shares one killer — **best-5%-removed is negative** (often violently: −0.20 to −0.59). The STRESS *average* is carried by a thin sliver of trades clustered in the 2013 gold crash and 2016–18 declines. `maxYr%` > 1 rows are degenerate (net R ≈ 0). This is the **same signature** that failed M15's `PT-C-bo50-UP` and `Candidate-001`.

## 13. The lone survivor — `H1-B-bo-acc-SHORT`, full evidence
**Mechanism:** in H4-downtrend, price closes below the prior 20-bar low **and the next bar accepts** (closes lower still) → enter short next open, stop at the broken low, time-exit 10 H1 bars.

| test | result | read |
|---|---|---|
| STRESS baseline | avg **+0.098**, n=179, win 49.7%, **PF 1.63**, median −0.002 | positive-expectancy trend-follower (few big wins) |
| BASE / GROSS | +0.109 / +0.112 | cost drag is small — H1 targets clear it |
| **deep tail** | best1_rem +0.084, best2_rem +0.064, **best5_rem +0.022**, best10_rem −0.028 | survives 5%-removed (unlike all others); thins at 10% |
| top-1% share | 0.151; max-year share **0.43** | **not** a single-event artifact |
| **H4-gate value** | uncond −0.008 → H4 **+0.098** (§7) | the gate **is** the edge |
| param neighborhood (lb) | 15:+0.119, 20:+0.098, 25:+0.093, 30:+0.119 | flat/positive — **no knife-edge** |
| param neighborhood (hold) | 6:+0.085, 8:+0.097, 10:+0.098, 12:+0.104, 15:+0.114 | monotone-positive |
| accept filter | accept +0.098 vs raw +0.070 | acceptance **earns ~40%** |
| execution degrade | +1-bar entry +0.117; 1.5× floor +0.098 | robust to worse fills |
| **out-of-DEV CALIB** (block2, 2020-21) | STRESS **+0.057**, n=35, best5_rem +0.022 | positive on data **not** used to select it |
| median per-trade risk | **$17.88** | vs $7.71 on M15 (§16) |

## 14. Honest limitations of the survivor (do NOT over-sell)
1. **Modest magnitude:** STRESS +0.098 R/trade — real but small.
2. **Best-10%-removed is negative (−0.028):** passes best-5% but not best-10%; the edge is thin and partly tail-assisted (not catastrophic like the others, but not bulletproof).
3. **Regime-conditioned:** by-year R = 2011 +3.6, 2012 +5.8, **2013 +7.5**, 2016 +1.1, 2017 −1.0, 2018 +0.5. b1 average is essentially **flat (+0.008)**. The edge is concentrated in the **2011–2013 secular gold downtrend**; in 2016–18 it barely works. This is a bear-regime short-continuation edge, not an all-weather one.
4. **Small CALIB n (35):** the out-of-DEV positive is encouraging but low-powered.

## 15. Temporal / block stability
Both DEV blocks positive on average (b0 +0.169, b1 +0.008), and CALIB (block2) positive (+0.057). But the b0/b1 asymmetry (§14.3) means stability is **regime-dependent**, strongest in sustained downtrends.

## 16. MANDATORY M15-vs-H1 cost-wall comparison (item 24)
| metric | M15 pro-trend | H1 pro-trend |
|---|---|---|
| IDs tested | 44 | 28 |
| **fast-survivors (STRESS)** | **1** | **21** |
| **deep-robust survivors** | **0** | **1** |
| median per-trade risk (20-breakout+accept short) | **$7.71** | **$17.88** |
| **STRESS cost (0.24) as % of median risk** | **3.1%** | **1.3%** |
| median H1 ATR14 | ~$1.43 (M15) | b0 $4.34 / b1 $2.66 |
| tail signature of survivors | outlier-dependent (best-1%-removed −0.015) | 20/21 outlier/event-dependent; **1** legit (best-5%-removed +0.022) |

**Does H1 materially improve edge/cost vs M15?** — **Modestly and selectively, not materially and broadly.**
- **Cost fraction: yes** — H1 roughly **halves** the STRESS cost drag per trade (1.3% vs 3.1% of risk), because larger bars → larger risk/target for the *same absolute* 0.24 round-trip.
- **Fast survival: dramatically, but illusory** — 21 vs 1 clear STRESS, yet 20 of 21 are carried by a thin tail of crash/trend trades; the lower cost fraction lets *noise + a few big trends* pass the mean test, not a broad-based edge.
- **Genuine robust edge: one** — H1 surfaces exactly one gate-validated, param-stable, execution-robust, out-of-DEV-positive candidate (short 20-breakout+accept) that M15 (0 deep-survivors) could not. Net: a **narrow, real** improvement, not a regime change.

## 17. Overlap with existing candidates (item 25)
| pair | Jaccard (trading-day) | direction | classification |
|---|---|---|---|
| H1-B-bo-acc-SHORT vs **S5** | **0.062** | cand SHORT vs S5 LONG | **INDEPENDENT** (opposite direction; 59 same-day co-occurrences are *opposing* trades) |
| H1-B-bo-acc-SHORT vs **S20** | 0.0* | cand SHORT vs S20 LONG | **INDEPENDENT** (directionally orthogonal) |
| vs Candidate-001 / S9 | — | SHORT vs LONG-continuation | directionally orthogonal |
*S20's M15 generator returned 0 setups in the isolated DEV slice (spec/column mismatch outside its native pipeline); independence is argued from direction, not a clean count. The candidate is a **SHORT** continuation alpha — it **diversifies** the existing S5/S20 LONG breakout-continuation sources rather than duplicating them.

## 18. LONG vs SHORT (item 18)
Consistent with every prior XAUUSD finding: **short-continuation is where the gold-specific edge sits in this population** (the DEV blocks span the 2011–2013 bear market). All 8 LONG fast-survivors are FRAGILE; the one deep-survivor and most of the strong-gross fast-survivors are SHORT. Long-side continuation is weaker here — but note this is partly a *sampling* effect of the DEV window's regimes, reinforcing §14.3's regime caveat.

## 19. Mechanism-cluster view (why 21 ≠ 21 independent alphas)
The 21 fast-survivors collapse into ~5 mechanism clusters (breakout±accept/retest, momentum/efficiency, displacement+accept, structure/pullback, compression). Treating them as independent would be a multiple-testing error. After deep robustness only **one representative** (breakout+accept short) stands — the cleanest, lowest-turnover, gate-validated member of the breakout cluster.

## 20. Turnover / capacity
Survivor turnover **6.73 trades / 1,000 DEV bars** (low). n=179 over 26,610 DEV H1 bars ≈ one trade per ~150 H1 bars. Low-frequency, selective — appropriate for a regime-conditioned continuation signal.

## 21. Governance / integrity ledger
**VALIDATION_ACCESS_COUNT = 0. FINAL_HOLDOUT_ACCESS_COUNT = 0.** Native H1 (`AWAITING_REGIME_MAP`) rejected. Per-block evaluation → no 2013→2016 cross-gap bridging. CALIBRATION used **only** to stress the survivor (never to select). No VALIDATION/SEALED/FB14/F441/MB3 evidence touched; V4.4 frozen (`23d98c07…`) untouched; no Market-Intelligence / N1–N6 / RANGE retune; S5/S20 fresh-validation evidence not accessed; `BROKER_ORDER_SUBMISSION = DISABLED`; no AI Trader / Strategy Catalog / LIVE. No `H1_PROTREND_ALPHA_DISCOVERY_INTEGRITY_STOP` condition encountered. Checkpoints: `h1_checkpoint_at25.json`, `h1_checkpoint_final.json`.

## 22. Reproducibility
Committed under `reports/alpha_discovery/`: `h1_protrend.py` (campaign), `deepen_h1.py` (deep battery), `verify_h1_candidate.py` (survivor verification), `m15_vs_h1_costwall.py` (item-24 cost-wall), plus `h1_records.json`, `h1_deepen.json`, checkpoints. Population sha `1dd43c1187d01428`; deterministic; RATIFIED cost model `AI_TRADER_SHADOW_COST_MODEL_v1` (BASE 0.05 / STRESS 0.24). HTF context via the same causal `_from_M15_v2` sources ratified in VE `ed57853`.

## 23. What survived / what died
- **Survived (1):** `H1-B-bo-acc-SHORT` — modest, H4-gate-validated, param-stable, execution-robust, out-of-DEV-positive, INDEPENDENT of S5/S20, but **regime-conditioned** (2011–2013-heavy) and thin (best-10%-removed −0.028).
- **Died (20):** every other fast-survivor — **event/tail-concentrated** (best-5%-removed negative). The spectacular ones (bo-retest-SHORT +0.31, comp-SHORT +0.34, eff-SHORT +0.19) are the *most* concentrated, not the most robust.

## 24. Strongest surviving H1 pro-trend candidate
**`H1-B-bo-acc-SHORT`** — 20-bar breakdown + acceptance, short, H4-downtrend-gated, 10-bar time exit. STRESS **+0.098 R/trade**, PF 1.63, best-5%-removed **+0.022**, CALIB (out-of-DEV) **+0.057**. Classification: **MODEST_REGIME_CONDITIONED_CANDIDATE** — genuinely more robust than anything the M15 pro-trend search produced, but not a strong all-weather PASS. **Not validated. Not promoted.**

## 25. Recommendation for independent validation
1. **Forward exactly one candidate — `H1-B-bo-acc-SHORT` — to the Statistician/Red Team queue** as a *modest, regime-conditioned, SHORT* pro-trend continuation alpha, explicitly flagged: (a) edge concentrated in 2011–2013 secular downtrend, b1/2016–18 nearly flat; (b) best-10%-removed negative; (c) small CALIB n. It **diversifies** the S5/S20 LONG sources (opposite direction, Jaccard 0.06).
2. **Structural conclusion for the CEO (item 24):** H1 does **not** deliver a broadly stronger edge/cost than M15. It halves the per-trade cost fraction (1.3% vs 3.1%) and inflates fast-survival (21 vs 1), but deep robustness reveals both timeframes' continuation edges are **tail/event-concentrated**; H1's only durable gain is **one** narrow, gate-validated short-continuation signal. The next higher-information step is **not** more continuation-variant mining on either timeframe (cosmetic) — it is either (i) a *regime-explicit* study of *why* the H4-gate earns value on H1 for shorts (mechanism, not pattern), or (ii) a different edge class (mean-reversion / liquidity-sweep) rather than more trend-continuation.
3. **Robust Alpha inventory unchanged in count, +1 conditional:** S5 (LONG, PASS-reproduced), S20 (LONG, new survivor) remain the two robust sources; `H1-B-bo-acc-SHORT` joins as a **third, conditional, SHORT** candidate pending validation. Nothing promoted to Strategy Catalog / AI Trader / LIVE by Alpha Discovery.
4. **Graveyard (provenance, do not rediscover):** the 20 deep-fragile H1 fast-survivors — recorded with their tail-collapse profiles in `h1_deepen.json`.

**Terminal status:** `H1_PROTREND_ALPHA_DISCOVERY_COMPLETE` · `H1_PROTREND_ALPHA_CANDIDATES_READY_FOR_CEO_REVIEW` (1 modest candidate). **STOP.**

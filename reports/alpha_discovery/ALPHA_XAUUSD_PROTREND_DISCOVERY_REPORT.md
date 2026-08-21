# ALPHA_XAUUSD_PROTREND_DISCOVERY_REPORT

**Mandate:** `ALPHA-XAUUSD-PROTREND-DISCOVERY-001` · **Date:** 2026-08-21 · **Terminal status:** `NO_ROBUST_PROTREND_ALPHA_FOUND_IN_CURRENT_SEARCH_SPACE`.
Bounded autonomous campaign, **early-stopped at 44 of 150 IDs** (info gain collapsed: 12 families × both directions, one fast-survivor that fails deep robustness). Zero robust survivors is an accepted scientific outcome.

## 1–3. Provenance / context / cost
XAUUSD M15. Market-Intelligence context = **N1 canonical trend** (`ve_n1_replay` incremental ledger, TREND_UP/TREND_DOWN) — used read-only, unmodified. Cost = RATIFIED `AI_TRADER_SHADOW_COST_MODEL_v1`: BASE round-trip 0.05, **STRESS round-trip 0.24**; entry next-open; floor `max(2·spread,0.05,0.10·ATR)`; TICK 0.01; full bid-ask. Data: DEVELOPMENT (2011→2018) + bounded CALIBRATION (2020-01→2022-01), 247,739 bars total. **VALIDATION never loaded; FINAL_HOLDOUT_ACCESS = 0.** V4.4 untouched; S5 fresh-validation evidence not accessed.

## 4–5. Hypothesis IDs + mechanism-family taxonomy (44 IDs, both directions)
| Family | Mechanisms (LONG + SHORT) |
|---|---|
| A pullback | depth 2/3/4, vol-contraction pullback |
| B displacement+acceptance (NEW IDs) | w1.0/1.2 × {no-retest, retest} |
| C breakout | 20-/50-extreme, +acceptance, +retest |
| D flag/compression | impulse+flag breakout |
| E structure-retest | break+retest+continue |
| F failed-counter | failed counter-move + resume |
| G momentum | 3/4 consecutive closes, path-efficiency, body-dominance |
| H vol-expansion-with-trend | compression→expansion in trend |
| J session | pullback continuation NY session |
| K acceleration | rising displacement + shortening corrections |
*(Family I — explicit H1/H4 alignment — NOT run: HTF features exist only from 2023 = VALIDATION window; N1 trend used as the available context instead.)*

## 6–8. Fast-falsification results
| status | count |
|---|---|
| FAIL | 40 |
| COST_FRAGILE (BASE+ / STRESS−) | 2 |
| INSUFFICIENT/SPARSE | 1 |
| **SURVIVE (fast)** | **1** (PT-C-bo50-UP) |
LONG IDs 22, SHORT IDs 22.

**Structural findings:**
1. **Almost every pro-trend continuation mechanism dies at STRESS cost on M15** — pullback, momentum, vol-expansion, acceleration, session, flag, retest, failed-counter all fail STRESS; the displacement+acceptance family (B, new IDs) is BASE-positive but STRESS-negative in both directions (same cost-fragility that sank Candidate-001).
2. **The pro-trend N1 gate mostly does NOT earn its value (item 7)** — for a majority of mechanisms the *unconditional* BASE ≥ the trend-gated BASE (e.g. disp+accept +0.076 unconditional vs +0.031 gated; pullback-3 SHORT +0.058 unc vs −0.029 gated). Trend conditioning is not automatically beneficial; several mechanisms are *worse* when gated.
3. **Short-side is structurally weaker (item 18)** — nearly all SHORT variants fail worse than their LONG counterparts (e.g. breakout-50 LONG survives, SHORT fails; momentum LONG marginal, SHORT negative-gross). XAUUSD long-side continuation is stronger, consistent with prior findings.

## 9–11. Survivor queue / failures / cost-fragile
- Fast-survivor: **PT-C-bo50-UP** (50-bar high breakout, LONG, N1-TREND_UP gated) — B +0.025 / STRESS +0.003.
- Cost-fragile (real gross, cost-eaten): **PT-C-bo20-UP** (B +0.021, S −0.015); **PT-A-pb4-DOWN** (deep pullback short, B **+0.148**, S −0.021 — the strongest BASE result, killed by STRESS).
- 40 fails across all families.

## 12–15. Deep robustness on the lone survivor (PT-C-bo50-UP) → **fails the serious-candidate bar**
| test | result |
|---|---|
| baseline | BASE +0.025 / **STRESS +0.003** (razor-thin), n=2158, win 48% |
| temporal | DEV +0.022 AND CALIB +0.022 (stable ✓) |
| **tail** | median −0.026; top-1% share **1.60** (160% of total R); **best-1%-removed −0.015**, −2% −0.041, −5% −0.100 → **UNSTABLE_OUTLIER_DEPENDENCE** ✗ |
| param neighborhood (lb) | 40 +0.024, 50 +0.025, 60 +0.017, 70 +0.006 (decays) |
| hold | 30 +0.013, 40 +0.025, 60 +0.029 |

**Verdict:** although PT-C-bo50-UP passes *fast* falsification and is time-stable, its edge is **entirely in the top 1%** (removing it goes negative) — the identical catastrophic tail-dependence profile that failed Candidate-001, and the opposite of S5's legitimate positive skew. Per item 24 (survivor requires *non-catastrophic tail dependence*), it is **not a serious pro-trend candidate.** STRESS is also razor-thin (+0.003).

## 16. LONG vs SHORT findings
Long-side is clearly stronger. The only fast-survivor and both cost-fragile-with-real-gross ideas are LONG (except PT-A-pb4-DOWN, a deep-pullback short with strong gross but STRESS-negative). No robust SHORT pro-trend edge found.

## 17–19. Overlap / historical cross-check / independence
PT-C-bo50-UP vs **S5**: Jaccard 0.09, 1,534 simultaneous same-bar signals → borderline `INDEPENDENT`, but **economically RELATED** — both are LONG breakout-continuation mechanisms (same family as S9/S20). It is **RELATED_BUT_DISTINCT** (a rolling-high breakout, N1-gated), **not a genuinely new independent Alpha source**. No mechanism in this campaign is both robust and independent.

## 20–23. Governance / checkpoints
CALIBRATION used only on the survivor deepening. **VALIDATION_ACCESS_COUNT = 0. FINAL_HOLDOUT_ACCESS_COUNT = 0.** No SEALED/FB14/F441/MB3; V4.4 frozen (`23d98c07…`); S5 fresh-validation evidence untouched; no MI mutation; broker disabled; no AI Trader. Checkpoints: `protrend_checkpoint_at25` (1 fast-survivor), `protrend_checkpoint_final` (44 tested). No integrity stop.

## 24. Strongest surviving pro-trend candidates
**None meet the serious-candidate bar.** The single fast-survivor (PT-C-bo50-UP) fails deep tail robustness (outlier-dependent) and is razor-thin at STRESS and economically related to the existing breakout family. The strongest *gross* pro-trend effect observed was **deep-pullback-short (PT-A-pb4-DOWN, BASE +0.148)** — a genuine gross edge entirely eaten by the 0.24 STRESS cost, flagged as cost-fragile, not advanced.

## 25. Recommendation for independent validation
1. **No new pro-trend candidate is recommended for validation.** The program's only robust Alpha remains **S5** (from the prior deep-research mandate) — this campaign did not find a second robust pro-trend source.
2. **Structural conclusion for the CEO:** on XAUUSD M15, standalone pro-trend continuation mechanisms face a **realistic-cost wall** (STRESS 0.24) that only very-large-target or opening-range-style mechanisms (S5) clear; entry-continuation setups are almost uniformly cost-fragile, and the N1 trend gate does not reliably add value. This argues that the next higher-information step is likely **a higher timeframe (H1)** — where target/cost ratios are more favorable — rather than more M15 continuation variants (which would be cosmetic).
3. **Preserved separately:** PT-C-bo50-UP (fast-survivor, outlier-dependent) and PT-A-pb4-DOWN (cost-fragile gross edge) are recorded in the graveyard for provenance; not to be rediscovered.

**Terminal status:** `XAUUSD_PROTREND_ALPHA_DISCOVERY_COMPLETE` · `NO_ROBUST_PROTREND_ALPHA_FOUND_IN_CURRENT_SEARCH_SPACE`. STOP.

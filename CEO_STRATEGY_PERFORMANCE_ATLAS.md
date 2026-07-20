# CEO Strategy Performance Atlas

**Date**: 2026-07-20. **Scope**: pure consolidation and presentation. No new backtest was run, no
production code was touched, no checkpoint was started, no algorithm was modified, and no metric,
verdict, classification, or ranking below was recalculated or altered — every value is copied directly
from the two already-existing, already-audited artifacts:

- `ceo_strategy_performance_study_data.json` (Strategy Historical Performance Study, all 43 strategies)
- `ceo_strategy_constraint_root_cause_data.json` (Strategy Constraint Root-Cause Study, the six
  A-Candidates: S1, S13, S39, S40, S46, S48)

The only operations performed on these numbers were: extraction, formatting, sorting (unchanged from
the prior version of this document), and — new in this revision — attaching a purely descriptive
**Evidence Level** label based on isolated trade count. No new statistic was introduced; the Evidence
Level is a label, not a metric.

## Evidence Level — definition

Reflects **only** how much confidence the isolated trade count itself supports — nothing about
direction, quality, or profitability. Fixed classification by number of isolated trades, as specified:

| Level | Isolated trades | Interpretation used below |
|---|---|---|
| A | over 100 | Highly reliable |
| B | 50–99 | Well supported |
| C | 25–49 | Moderate evidence |
| D | 10–24 | Early evidence |
| E | under 10 | Insufficient evidence |

This label does not change any ranking, does not penalize any strategy, and does not affect the
Verdict final column — it is presented purely as an interpretation aid alongside the existing,
unchanged values.

---

## Executive Summary

**1. Highest Expectancy with sufficient statistical evidence (B/A level, ≥50 isolated trades):**
**S1** (Expectancy 0.249, 54 trades, Evidence B) and **S39** (0.202, 66 trades, Evidence B) are the
only Top-10-Expectancy strategies backed by a well-supported sample. No strategy combines a Top-10
Expectancy result with "Highly reliable" (A, >100 trades) evidence — the sole A-level strategy in the
entire atlas, S10 (117 trades), has a *negative* expectancy (-0.029), so higher trade count here does
not coincide with higher Expectancy.

**2. Strategies that look excellent but have too few trades for firm conclusions (D/E evidence,
Top-10 Expectancy or Profit Factor):** **S8** (Expectancy 1.250, PF 6.46, only 4 trades — Insufficient),
**S50** (0.500, PF 2.20, 2 trades — Insufficient), **S41** (0.500, PF 1.66, 8 trades — Insufficient),
**S5** (0.401, 9 trades — Insufficient), **S18** (0.289, 6 trades — Insufficient), **S42** (0.571,
PF 2.27, 21 trades — Early), **S45** (0.370, PF 1.95, 10 trades — Early), **S30** (0.253, PF 1.55, 19
trades — Early). These are exactly the atlas's own "PROMISING" (category B classification) strategies —
the original study's own "profitable but under-sampled" label is directly corroborated by the Evidence
Level here, not contradicted by it.

**3. Most robust strategies:** **S42** tops the Robustness leaderboard outright (68.86, health state
ACTIVE) but only carries "Early evidence" (21 trades). The most robust strategy with well-supported
evidence is **S1** (65.96, WATCHLIST, 54 trades, Evidence B), followed by **S48** (61.64, WATCHLIST, 61
trades, Evidence B) and **S39** (57.49, WATCHLIST, 66 trades, Evidence B).

**4. Highest Total Realized R:** **S1** (13.43), **S39** (13.30), **S40** (13.30), and **S46** (12.97)
occupy the top four spots — all four are Evidence Level B (well supported) and all four are the same
four strategies carrying the Root-Cause Study's PORTFOLIO-LIMITED verdict. **S42** is fifth (11.99) but
only Evidence Level D (21 trades).

**5. Strategies that need more data before being considered real candidates:** the same set identified
in Q2 — **S8, S42, S50, S41, S5, S45, S18, S30**, plus the remaining two PROMISING-classified strategies
not in the Top-10 lists, **S28** (19 trades, D) and **S6** (8 trades, E). All ten of the atlas's
PROMISING-classified strategies carry Evidence Level D or E — none has reached even "Moderate evidence"
(25+ trades) — which is an internal consistency check on the original classification, not a new
finding: the "under-sampled" reasoning behind the PROMISING category is exactly what the Evidence Level
column now makes visible at a glance.

---

## Reading notes (so the table isn't misread)

- **Win Rate / Profit Factor / Expectancy (R) / Average R / Average RR / Total Realized R / Max
  Drawdown / Recovery Factor / Sharpe** all come from the **isolated** scenario (each strategy running
  alone, unconstrained by the shared-slot portfolio rule) — this is the performance study's own "true
  per-strategy quality" scenario. The **competitive** scenario is reflected only in the separate
  "Trades (competitive)" column, to show the volume contrast, exactly as requested.
- In the source data, "Average R" and "Expectancy (R)" are the same underlying field
  (`research_summary.average_r` == `window_metrics.expectancy_r`) — shown as two columns per the
  request, but they are identical numbers, not independently-derived figures. This is disclosed rather
  than silently duplicated.
- **Status** reuses the original study's own A-E classification labels verbatim (A→CANDIDATE,
  B→PROMISING, C→RELIABLE-UNPROFITABLE, D→INACTIVE, E→INCONCLUSIVE). It does not reuse the separate
  Strategy Health state machine (ACTIVE/WATCHLIST/PROBATION/SUSPENDED), which is a different,
  differently-scoped label already used verbatim in the Robustness leaderboard at the bottom of this
  document — both are shown, from their own original sources, never blended into one invented label.
- **Evidence Level** (new in this revision) is computed purely from the "Trades (isolated)" column
  already in this table, per the fixed A-E thresholds above. It is an interpretation label, not a
  statistic — it changes no value, verdict, classification, or ranking.
- **Principal constraint** reuses the performance study's own `principal_loss_reason` field (the
  denial-reason category whose count increased the most under competition) for all 43 strategies.
- **Verdict final** = the classification category for all 43 strategies; for the six strategies that
  went through the dedicated Root-Cause Study (S1, S13, S39, S40, S46, S48), the Root-Cause Study's own
  verdict is appended (all six: PORTFOLIO-LIMITED).
- Rows with zero isolated trades (category D — Inactive) show "n/a" for every ratio metric, since no
  ratio is computed by the source study when there are no trades — never a fabricated zero. All such
  rows are, unsurprisingly, Evidence Level E.

---

## Master table — all 43 strategies

Sorted by Expectancy (R) descending, then Profit Factor descending, then Trades (isolated) descending —
**unchanged from the prior version of this document.**

| # | Strategy ID | Status | Evidence Level | Trades (isolated) | Trades (competitive) | Win Rate | Profit Factor | Expectancy (R) | Average R | Average RR | Total Realized R | Max Drawdown | Recovery Factor | Sharpe | Principal constraint | Verdict final |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | S8 | PROMISING | E | 4 | 2 | 75.0% | 6.46 | 1.250 | 1.250 | 2.15 | 5.00 | 2.06 | 5.46 | 0.962 | LIMIT_MAX_PER_SYMBOL (+99) | B-PROMISING |
| 2 | S42 | PROMISING | D | 21 | 1 | 52.4% | 2.27 | 0.571 | 0.571 | 2.06 | 11.99 | 10.47 | 3.26 | 0.381 | LIMIT_MAX_PER_SYMBOL (+23) | B-PROMISING |
| 3 | S50 | PROMISING | E | 2 | 0 | 50.0% | 2.20 | 0.500 | 0.500 | 2.20 | 1.00 | 1.97 | 1.20 | 0.333 | LIMIT_MAX_PER_SYMBOL (+1044) | B-PROMISING |
| 4 | S41 | PROMISING | E | 8 | 0 | 50.0% | 1.66 | 0.500 | 0.500 | 1.66 | 4.00 | 4.23 | 1.79 | 0.333 | BELOW_FLOOR (+325) | B-PROMISING |
| 5 | S5 | PROMISING | E | 9 | 2 | 44.4% | 1.32 | 0.401 | 0.401 | 1.65 | 3.61 | 8.25 | 0.49 | 0.288 | LIMIT_MAX_PER_SYMBOL (+1110) | B-PROMISING |
| 6 | S45 | PROMISING | D | 10 | 0 | 60.0% | 1.95 | 0.370 | 0.370 | 1.30 | 3.70 | 3.74 | 2.32 | 0.321 | LIMIT_MAX_PER_SYMBOL (+185) | B-PROMISING |
| 7 | S18 | PROMISING | E | 6 | 1 | 33.3% | 1.56 | 0.289 | 0.289 | 3.12 | 1.74 | 7.31 | 0.78 | 0.150 | LIMIT_MAX_PER_SYMBOL (+149) | B-PROMISING |
| 8 | S30 | PROMISING | D | 19 | 2 | 42.1% | 1.55 | 0.253 | 0.253 | 2.13 | 4.80 | 13.08 | 1.09 | 0.184 | LIMIT_MAX_PER_SYMBOL (+740) | B-PROMISING |
| 9 | S1 | CANDIDATE | B | 54 | 14 | 42.6% | 1.59 | 0.249 | 0.249 | 2.15 | 13.43 | 20.65 | 2.40 | 0.171 | LIMIT_MAX_PER_SYMBOL (+221) | A-CANDIDATE; Root-Cause Study: PORTFOLIO-LIMITED |
| 10 | S39 | CANDIDATE | B | 66 | 36 | 40.9% | 1.29 | 0.202 | 0.202 | 1.86 | 13.30 | 39.63 | 1.29 | 0.138 | LIMIT_MAX_PER_SYMBOL (+32) | A-CANDIDATE; Root-Cause Study: PORTFOLIO-LIMITED |
| 11 | S40 | CANDIDATE | B | 69 | 3 | 40.6% | 1.29 | 0.193 | 0.193 | 1.88 | 13.30 | 46.17 | 1.10 | 0.133 | BELOW_FLOOR (+376) | A-CANDIDATE; Root-Cause Study: PORTFOLIO-LIMITED |
| 12 | S28 | PROMISING | D | 19 | 2 | 36.8% | 1.43 | 0.183 | 0.183 | 2.45 | 3.49 | 7.29 | 1.34 | 0.107 | LIMIT_MAX_PER_SYMBOL (+643) | B-PROMISING |
| 13 | S46 | CANDIDATE | B | 79 | 47 | 29.1% | 1.18 | 0.164 | 0.164 | 2.87 | 12.97 | 71.91 | 0.72 | 0.090 | BELOW_FLOOR (+49) | A-CANDIDATE; Root-Cause Study: PORTFOLIO-LIMITED |
| 14 | S13 | CANDIDATE | C | 37 | 1 | 45.9% | 1.18 | 0.100 | 0.100 | 1.39 | 3.71 | 23.15 | 0.32 | 0.089 | LIMIT_MAX_PER_SYMBOL (+1485) | A-CANDIDATE; Root-Cause Study: PORTFOLIO-LIMITED |
| 15 | S48 | CANDIDATE | B | 61 | 4 | 47.5% | 1.28 | 0.041 | 0.041 | 1.41 | 2.51 | 5.86 | 1.43 | 0.079 | BELOW_FLOOR (+426) | A-CANDIDATE; Root-Cause Study: PORTFOLIO-LIMITED |
| 16 | S6 | PROMISING | E | 8 | 0 | 37.5% | 1.13 | 0.021 | 0.021 | 1.88 | 0.17 | 4.50 | 0.30 | 0.017 | LIMIT_MAX_PER_SYMBOL (+570) | B-PROMISING |
| 17 | S10 | RELIABLE-UNPROFITABLE | A | 117 | 1 | 41.9% | 0.84 | -0.029 | -0.029 | 1.16 | -3.43 | 18.58 | -0.79 | -0.046 | LIMIT_MAX_PER_SYMBOL (+656) | C-RELIABLE-UNPROFITABLE |
| 18 | S14 | INCONCLUSIVE | D | 14 | 1 | 35.7% | 0.94 | -0.071 | -0.071 | 1.69 | -1.00 | 15.49 | -0.08 | -0.063 | BELOW_FLOOR (+74) | E-INCONCLUSIVE |
| 19 | S25 | RELIABLE-UNPROFITABLE | C | 43 | 4 | 41.9% | 0.63 | -0.116 | -0.116 | 0.87 | -4.99 | 23.18 | -0.78 | -0.149 | LIMIT_MAX_PER_SYMBOL (+367) | C-RELIABLE-UNPROFITABLE |
| 20 | S43 | INCONCLUSIVE | D | 19 | 2 | 26.3% | 0.50 | -0.211 | -0.211 | 1.40 | -4.01 | 21.89 | -0.99 | -0.160 | BELOW_FLOOR (+1044) | E-INCONCLUSIVE |
| 21 | S4 | RELIABLE-UNPROFITABLE | C | 33 | 2 | 30.3% | 0.36 | -0.247 | -0.247 | 0.83 | -8.16 | 19.82 | -1.00 | -0.514 | BELOW_FLOOR (+808) | C-RELIABLE-UNPROFITABLE |
| 22 | S21 | INCONCLUSIVE | E | 4 | 2 | 25.0% | 0.45 | -0.250 | -0.250 | 1.34 | -1.00 | 9.68 | -0.55 | -0.193 | LIMIT_MAX_PER_SYMBOL (+500) | E-INCONCLUSIVE |
| 23 | S24 | INCONCLUSIVE | E | 7 | 2 | 28.6% | 0.57 | -0.259 | -0.259 | 1.44 | -1.81 | 11.24 | -0.52 | -0.215 | LIMIT_MAX_PER_SYMBOL (+122) | E-INCONCLUSIVE |
| 24 | S44 | RELIABLE-UNPROFITABLE | C | 41 | 7 | 24.4% | 0.61 | -0.269 | -0.269 | 1.88 | -11.02 | 37.14 | -0.82 | -0.209 | LIMIT_MAX_PER_SYMBOL (+1655) | C-RELIABLE-UNPROFITABLE |
| 25 | S16 | INCONCLUSIVE | D | 11 | 1 | 27.3% | 0.34 | -0.338 | -0.338 | 0.91 | -3.71 | 12.69 | -0.95 | -0.352 | LIMIT_MAX_PER_SYMBOL (+594) | E-INCONCLUSIVE |
| 26 | S22 | INCONCLUSIVE | D | 19 | 1 | 15.8% | 0.54 | -0.360 | -0.360 | 2.87 | -6.85 | 22.56 | -0.72 | -0.296 | LIMIT_MAX_PER_SYMBOL (+354) | E-INCONCLUSIVE |
| 27 | S26 | INCONCLUSIVE | D | 24 | 4 | 16.7% | 0.09 | -0.370 | -0.370 | 0.43 | -8.88 | 25.65 | -1.00 | -0.884 | LIMIT_MAX_PER_SYMBOL (+1238) | E-INCONCLUSIVE |
| 28 | S2 | INCONCLUSIVE | D | 18 | 0 | 5.6% | 0.08 | -0.776 | -0.776 | 1.39 | -13.96 | 44.67 | -1.00 | -1.089 | LIMIT_MAX_PER_SYMBOL (+296) | E-INCONCLUSIVE |
| 29 | S29 | INCONCLUSIVE | E | 1 | 0 | 0.0% | 0.00 | -1.000 | -1.000 | n/a | -1.00 | 2.92 | -1.00 | n/a | LIMIT_MAX_PER_SYMBOL (+46) | E-INCONCLUSIVE |
| 30 | S3 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | none (no denial category increased under competition) | D-INACTIVE |
| 31 | S7 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | none (no denial category increased under competition) | D-INACTIVE |
| 32 | S9 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | none (no denial category increased under competition) | D-INACTIVE |
| 33 | S11 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | none (no denial category increased under competition) | D-INACTIVE |
| 34 | S12 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | LIMIT_MAX_PER_SYMBOL (+713) | D-INACTIVE |
| 35 | S15 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | none (no denial category increased under competition) | D-INACTIVE |
| 36 | S17 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | none (no denial category increased under competition) | D-INACTIVE |
| 37 | S19 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | none (no denial category increased under competition) | D-INACTIVE |
| 38 | S20 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | none (no denial category increased under competition) | D-INACTIVE |
| 39 | S23 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | none (no denial category increased under competition) | D-INACTIVE |
| 40 | S27 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | none (no denial category increased under competition) | D-INACTIVE |
| 41 | S31 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | none (no denial category increased under competition) | D-INACTIVE |
| 42 | S38 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | none (no denial category increased under competition) | D-INACTIVE |
| 43 | S51 | INACTIVE | E | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | 0.00 | n/a | n/a | LIMIT_MAX_PER_SYMBOL (+943) | D-INACTIVE |

---

## Top 10 by Expectancy (R)

Ranking unchanged from the prior version of this document.

| Rank | Strategy ID | Expectancy (R) | Trades (isolated) | Evidence Level | Interpretation |
|---|---|---|---|---|---|
| 1 | S8 | 1.250 | 4 | E | Insufficient evidence |
| 2 | S42 | 0.571 | 21 | D | Early evidence |
| 3 | S50 | 0.500 | 2 | E | Insufficient evidence |
| 4 | S41 | 0.500 | 8 | E | Insufficient evidence |
| 5 | S5 | 0.401 | 9 | E | Insufficient evidence |
| 6 | S45 | 0.370 | 10 | D | Early evidence |
| 7 | S18 | 0.289 | 6 | E | Insufficient evidence |
| 8 | S30 | 0.253 | 19 | D | Early evidence |
| 9 | S1 | 0.249 | 54 | B | Well supported |
| 10 | S39 | 0.202 | 66 | B | Well supported |

## Top 10 by Profit Factor

Ranking unchanged from the prior version of this document.

| Rank | Strategy ID | Profit Factor | Trades (isolated) | Evidence Level | Interpretation |
|---|---|---|---|---|---|
| 1 | S8 | 6.46 | 4 | E | Insufficient evidence |
| 2 | S42 | 2.27 | 21 | D | Early evidence |
| 3 | S50 | 2.20 | 2 | E | Insufficient evidence |
| 4 | S45 | 1.95 | 10 | D | Early evidence |
| 5 | S41 | 1.66 | 8 | E | Insufficient evidence |
| 6 | S1 | 1.59 | 54 | B | Well supported |
| 7 | S18 | 1.56 | 6 | E | Insufficient evidence |
| 8 | S30 | 1.55 | 19 | D | Early evidence |
| 9 | S28 | 1.43 | 19 | D | Early evidence |
| 10 | S5 | 1.32 | 9 | E | Insufficient evidence |

## Top 10 by Robustness (Health Score, isolated scenario — reused verbatim from the performance study's own `rankings.robustness_isolated`, not recomputed)

Ranking unchanged from the prior version of this document.

| Rank | Strategy ID | Robustness Score | Health State | Trades (isolated) | Evidence Level | Interpretation |
|---|---|---|---|---|---|---|
| 1 | S42 | 68.86 | ACTIVE | 21 | D | Early evidence |
| 2 | S1 | 65.96 | WATCHLIST | 54 | B | Well supported |
| 3 | S45 | 63.83 | WATCHLIST | 10 | D | Early evidence |
| 4 | S41 | 63.42 | WATCHLIST | 8 | E | Insufficient evidence |
| 5 | S30 | 61.85 | WATCHLIST | 19 | D | Early evidence |
| 6 | S48 | 61.64 | WATCHLIST | 61 | B | Well supported |
| 7 | S8 | 58.72 | WATCHLIST | 4 | E | Insufficient evidence |
| 8 | S13 | 58.71 | WATCHLIST | 37 | C | Moderate evidence |
| 9 | S5 | 58.39 | WATCHLIST | 9 | E | Insufficient evidence |
| 10 | S39 | 57.49 | WATCHLIST | 66 | B | Well supported |

## Top 10 by Total Realized R

Ranking unchanged from the prior version of this document.

| Rank | Strategy ID | Total Realized R | Trades (isolated) | Evidence Level | Interpretation |
|---|---|---|---|---|---|
| 1 | S1 | 13.43 | 54 | B | Well supported |
| 2 | S39 | 13.30 | 66 | B | Well supported |
| 3 | S40 | 13.30 | 69 | B | Well supported |
| 4 | S46 | 12.97 | 79 | B | Well supported |
| 5 | S42 | 11.99 | 21 | D | Early evidence |
| 6 | S8 | 5.00 | 4 | E | Insufficient evidence |
| 7 | S30 | 4.80 | 19 | D | Early evidence |
| 8 | S41 | 4.00 | 8 | E | Insufficient evidence |
| 9 | S13 | 3.71 | 37 | C | Moderate evidence |
| 10 | S45 | 3.70 | 10 | D | Early evidence |

---

## Verification (performed before commit)

- Every metric value, verdict, classification, and ranking position in this revision was diffed
  against the prior version of this document — **identical**; the only additions are the Executive
  Summary section, the Evidence Level definition, the Evidence Level column in the master table, and
  the Evidence Level + Interpretation columns in the four Top-10 tables.
- Every Evidence Level label was derived solely from the already-present "Trades (isolated)" column in
  this same document, applying the fixed A-E thresholds above — no value was looked up again from the
  source JSON files, and no source JSON file was modified.
- Row order in the master table and rank order in all four Top-10 tables are byte-identical to the
  prior version.

## Sources

- `ceo_strategy_performance_study_data.json` — `isolated_metrics`, `blocking`, `classification`,
  `rankings.robustness_isolated` fields, for all 43 strategies.
- `ceo_strategy_constraint_root_cause_data.json` — `phase5` verdicts, for S1/S13/S39/S40/S46/S48 only.
- No file was modified other than this one. No new file was created. No backtest was run.

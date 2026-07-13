# EXPLORATORY CORRELATION REPORT — workstream B (diagnostic only)

Read-only. **Diagnostic only — no weight optimization, no validated-portfolio claim, holdout SEALED.**
Purpose: identify redundant vs complementary candidates among the 11 shortlisted, with honest uncertainty.

## Method
For each shortlisted representative, the official `MS.backtest` was re-run on the research segment; monthly
**summed-R** streams were built and aligned over the **26 common months (2022-12 → 2025-02)**. Pairwise
Pearson correlations with **2,000-sample bootstrap 95% CIs**. This deliberately repairs the earlier RETRACTED
"S1/S5/S9 are decorrelated" claim, which used a single unstable point estimate with no CI.

## Headline: correlations are UNCERTAIN (only ~26 months)
Most pairwise CIs are wide and **straddle 0** — "low correlation" between most pairs is **not statistically
distinguishable from zero** at this sample size. Only a few relationships are resolved (CI excludes 0):

### Redundant (positively correlated — same economic bet), CI excludes 0
| pair | r | 95% CI |
|---|---|---|
| S17/pw_high/breakout ↔ S9/c4h=up/any | **+0.71** | [+0.48, +0.86] |
| S9/any ↔ S9/align | **+0.70** | [+0.48, +0.84] |
| S17/pw_high/breakout ↔ S9/align | **+0.66** | [+0.33, +0.86] |
| S20/breakout ↔ S9/any | **+0.60** | [+0.17, +0.82] |
| S1/low/swing ↔ S5/ny/up | +0.53 | [+0.16, +0.77] |

→ **S9(any), S9(align), S20(breakout), S17(pw_high/breakout)** form one **long-momentum / trend-continuation
cluster**. Keep ONE representative for validation, not four. (Economically obvious: all are "buy strength in
an uptrend".)

### Complementary (negatively correlated), only one CI excludes 0
| pair | r | 95% CI |
|---|---|---|
| S1/high/pdh_pdl (SHORT) ↔ S8/vwap/up (long MR) | **−0.38** | [−0.58, −0.12] ✓ resolved |
| S1/low/pdh_pdl ↔ S1/low/swing | −0.39 | [−0.70, +0.06] (crosses 0) |
| S20/breakout ↔ S6/london/fade/down | −0.28 | [−0.61, +0.08] (crosses 0) |

→ The only statistically resolved diversifier is the **S1 SHORT** candidate vs the long book. All other
"complementary" pairs are unresolved at 26 months.

## Exposure & concentration
- **Directional: 10 of 11 long, 1 short** (S1/high/pdh_pdl). The book is a near-pure long-gold exposure →
  heavy shared drift/beta; genuine diversification is minimal.
- **Temporal concentration (top-year R / total R)**: S8/vwap **1.97** (other years net-negative), S1/low/pdh
  1.41, S2/low/pdh 1.19 — these lean on one good year. S5/ny/up **0.44** and S20 **0.54** are the most time-
  diversified.
- Common active window ~26 months; candidates with <25 trades excluded upstream.

## Implications for validation
1. Collapse the momentum cluster to **one** representative before matched-null (avoid four correlated
   "passes" that are one bet). Suggested representative: **S5/ny/up** (most time-consistent) or **S9/any**
   (largest n) — test one, not all four.
2. The **long-only tilt** means the whole shortlist shares drift-beta; the matched-null drift control is the
   decisive filter (see the validation branch's adversarial fix).
3. Do NOT build portfolio weights or claim diversification — correlations are too uncertain (26 months).
   Portfolio Architect stays deferred until more data / validated factors exist.

# EXPERIMENT_PRIORITY_MATRIX — Information-Value scoring (NOT expectancy / prior)

Per ETAPA 4, experiments are prioritized by INFORMATION VALUE, never by estimated expectancy or prior_plausibility
(the latter is hidden from this stage). Ten factors, 0–3 each (max 30): uncertainty_reduction · kg_updates ·
contradiction_resolution · novelty · feasibility · low_compute · low_multiple_testing_risk · addresses_beta ·
matched_control_available · interpretable_if_negative.

## Scores of the selected 10 (from planner_summary.json / EXPERIMENT_REGISTRY.jsonl)
| exp | type | iv_score | why high info |
|---|---|---|---|
| EXP-01 confirmation contribution | B | 26 | resolves C1; updates P001/P011/I1/I2; matched control; interpretable if negative |
| EXP-02 efficiency contribution | B | 26 | resolves C2; updates P005/P012/I1; gate on/off control |
| EXP-07 round-number vs breakout | C | 25 | resolves C4; factorial separates 3 effects; updates P004/P013/I8 |
| EXP-08 return-ranked vs value reversion | C | 25 | resolves C5; genuinely new; updates P006/P014/I5 |
| EXP-03 sweep beta diagnostic | D | 23 | directly attacks I7 (beta confound); matched control; negative is informative |
| EXP-04 opening-range beta diagnostic | D | 23 | attacks I7 on the strongest candidate |
| EXP-05 sweep level placebo | E | 23 | negative control on P001/P010/I8; builds reusable shuffle harness |
| EXP-06 fade level placebo | E | 23 | negative control on P002/I8 |
| EXP-09 rescue value-reaction (alpha) | A | 18 | tests I1/I2 generalization to a negative base; interpretable if negative |
| EXP-10 rescue router (alpha) | A | 18 | tests I3 stand-aside on the router |

Note: mechanism (B) and contradiction (C) experiments score highest because they can UPDATE the most Knowledge-
Graph edges and resolve a named contradiction with a matched control. Alpha (A) scores lower on info-value even
though its potential profitability is higher — by design, we do not prioritize by profitability.

## Hierarchical family-wise multiplicity plan (Codex's batch-risk mitigation — CRITICAL)
The 10 experiments reuse correlated events/levels/regimes → running them as 10 independent tests would inflate
false discovery. Predeclared plan:
- **Primary contrasts (1 per experiment):** the treatment-vs-matched-control difference named in each spec. These
  are the ONLY confirmatory tests; everything else is secondary/diagnostic.
- **Family-wise correction:** apply ONE global multiplicity procedure across all 10 primary contrasts (the same
  validated matched-null → global-FDR machinery, when the CEO opens that phase), NOT per-experiment.
- **No promotion on a secondary/exploratory result.** Alpha (Wave 3) promotes only if its primary contrast passes
  AND its Wave-1 placebo/beta context is clean.
- **Freeze before inspection:** all randomization rules, metrics, margins, and stopping rules are frozen (this
  document) before any result is read; no post-hoc reinterpretation.

## Selection quota (ETAPA 5) — used
mechanism(B) 2 · contradiction(C) 2 · beta(D) 2 · placebo(E) 2 · alpha(A) 2 = 10 (≤ 12 cap). scope(F) deferred.

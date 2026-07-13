> ⚠️ **STALE / HISTORICAL / NON-AUTHORITATIVE** (marked 2026-07-13). This registry covers only S1–S10 and its
> `p` / `passed_stat` columns come from the **analytic p-value engine that was later INVALIDATED** (see
> MONTE_CARLO_AUDIT.md, PROJECT_STATE §9). Do NOT treat `passed_stat=True` or these p-values as verdicts.
> Authoritative campaign results = `results/FAMILY_RESULTS.parquet` + `results/full.log` (S1–S20, ENGINE v2).
> Kept for audit trail; not deleted. Update/archive deferred per CEO.

# ALPHA_REGISTRY (provisional, holdout SEALED)

Unit = alpha FACTOR (economic mechanism). Portfolio objective = max expectancy at min inter-factor correlation.

| alpha_id | family | economic_hypothesis | side | exp(R) | PF | maxDD | n | p | passed_stat | novelty | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A_S1 | S1 | liquidity-sweep mean-reversion | long | 0.253 | 1.42 | 10.3 | 141 | 1.72e-03 | True | 0.58 | PROVISIONAL SUB-FDR |
| A_S2 | S2 | failed-breakout fade | long | 0.075 | 1.11 | 46.5 | 513 | 1.00e+00 | False | 0.72 | PROVISIONAL NO CANDIDATE |
| A_S3 | S3 | breakout-retest momentum | long | 0.063 | 1.09 | 40.6 | 761 | 1.00e+00 | False | 0.45 | PROVISIONAL NO CANDIDATE |
| A_S4 | S4 | volatility-regime expansion | - | - | - | - | 0 | - | - | - | PROVISIONAL NO SIGNAL |
| A_S5 | S5 | opening-range momentum | long | 0.135 | 1.4 | 7.3 | 295 | 2.82e-03 | True | 0.54 | PROVISIONAL SUB-FDR |
| A_S6 | S6 | session-transition momentum | long | 1.196 | 1.86 | 89.8 | 244 | 1.00e+00 | False | 0.58 | PROVISIONAL NO CANDIDATE |
| A_S7 | S7 | trend-pullback continuation | - | - | - | - | 0 | - | - | - | PROVISIONAL NO SIGNAL |
| A_S8 | S8 | extension mean-reversion | long | 0.029 | 1.04 | 49.3 | 304 | 1.00e+00 | False | 0.58 | PROVISIONAL NO CANDIDATE |
| A_S9 | S9 | MTF-trend momentum | long | 0.068 | 1.15 | 16.2 | 545 | 1.00e+00 | False | 0.45 | PROVISIONAL NO CANDIDATE |
| A_S10 | S10 | displacement continuation | - | - | - | - | 0 | - | - | - | PROVISIONAL NO SIGNAL |

## Inter-factor monthly-R correlation (research)

```
      S1    S2    S3    S5    S6    S8    S9
S1  1.00  0.00 -0.29 -0.42  0.07 -0.02 -0.35
S2  0.00  1.00 -0.04  0.11  0.11  0.28  0.21
S3 -0.29 -0.04  1.00  0.38  0.15  0.03  0.55
S5 -0.42  0.11  0.38  1.00  0.23 -0.12  0.46
S6  0.07  0.11  0.15  0.23  1.00 -0.42 -0.02
S8 -0.02  0.28  0.03 -0.12 -0.42  1.00 -0.11
S9 -0.35  0.21  0.55  0.46 -0.02 -0.11  1.00
```

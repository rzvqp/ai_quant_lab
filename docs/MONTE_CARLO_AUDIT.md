# MONTE_CARLO_AUDIT — p-value engine pilot + S6 case (2026-07-13)

## 1. S6 extreme-case audit (proven cause, not assumed)
Hyp S6 7a86a38610f8 (london/fade/down/stop=prev_ext/exit=time): exp=1.196R, n=244, maxDD=89.8R.
- R distribution: mean 1.196, **sd 15.27, skew 8.27, kurtosis 77.63**, max=+166.45R (one trade), min=−3.16.
- **Profit concentration: top-5 trades = 71% of gross profit.** Remove them → sum R = −155.8 (NEGATIVE),
  mean = −0.65R. The "edge" IS 5 outliers.
- **Tiny stops: risk/ATR median 0.407, min 0.047; 72 trades with stop < 0.3×ATR (mean R 4.40).**
  `prev_ext` stop can sit ~0.19 price units from entry → R=pnl/risk explodes on a normal move.
- No overlap bug (244 unique monotonic entries).
- **CAUSE: tiny-stop outliers + profit concentration = an R-NORMALIZATION artifact, NOT clean heavy-tail
  alpha.** The analytic normal-approx then reads the skewed sample as z≈16 → spurious p=2.1e-54.
- Correctly rejected by Screen V1 (maxDD 89.8R > 25R). But the tiny-stop/R-normalization issue affects
  any structure-stop family (beyond_sweep/prev_ext/structural) → FLAGGED for engine review (min-stop floor).

## 2. Pilot: 4 p-value methods (B=50,000; p_hat=(k+1)/(B+1))
| case | mean | skew | p_analytic (retracted) | p_IID_boot | p_block_boot | p_matched_null |
|---|---|---|---|---|---|---|
| S6 extreme | 1.196 | 8.3 | 2.1e-54 | 0.116 | 0.124 | 0.0000* |
| S1 rep RC | 0.399 | 11.6 | 2.3e-7 | 0.184 | 0.200 | 0.0000* |
| SYNTH null (mean 0) | 0.019 | 0.1 | n/a | 0.403 | 0.421 | 0.0002*⚠ |
| SYNTH edge (mean .25, clean) | 0.256 | ~0 | n/a | 0.0019 | 0.0004 | 0.0000* |

## 3. Findings / decisions
- **Analytic p = artifact** → retracted from verdict role (diagnostic only).
- **Block-bootstrap of trade-R = well-calibrated** (synthetic null→0.42, clean edge→4e-4) → adopted as
  INTERIM OFFICIAL empirical test of mean>0 robustness. Under it, S1/S6 exploratory signals are
  **NOT significant** (p≈0.12–0.20) — consistent with the S6 audit (outlier-driven).
- **Matched-null (*)**: current implementation miscalibrated — gives ~0 even for the synthetic null
  (compares synthetic R's to a real-price null with a mean mismatch). MUST be fixed (per-null mean
  matching + proper null construction) and re-validated on synthetic controls before official use.
- Net: with a VALID p-value, none of the current Research Candidates are statistically significant;
  the apparent S1/S5/S9 signals were an artifact of the invalidated analytic engine + skewed R.

## 4. TODO before full-campaign FDR
- Fix + validate matched-null; decide official null (A vs B) BEFORE running (no post-hoc selection).
- Consider min-stop floor to remove R-normalization explosions (engine change → CEO gate).
- Implement adaptive MC (MC-1/2/3) with CI + seeds; apply global-FDR over full eligible universe after S20.

# EMPIRICAL_PVALUE_SPEC — v1 (FROZEN before full-campaign FDR)

## Status of prior engine
Analytic normal-approximation p-value is **INVALIDATED for verdicts** (diagnostic/ranking only).
Reason proven (MONTE_CARLO_AUDIT): trade-R distributions are extremely skewed/heavy-tailed
(S6 skew=8.3, kurt=77.6; S1 skew=11.6) so the CLT/normal approx is meaningless in the tail
(S6 analytic p=2.1e-54 vs empirical ~0.12). All prior strict verdicts → **STRICT VALIDATION PENDING**.

## Primary test statistic (FROZEN, chosen before seeing which gives smaller p)
- **Statistic = mean expectancy per trade (R/trade)** on the research segment.
- **One-sided**, H0: mean_R ≤ 0 vs alt: mean_R > 0. Justification: the lab seeks positive-expectancy
  alpha; a two-sided test would waste power on the irrelevant left tail.
- Secondary DIAGNOSTIC stats (not for the verdict): profit factor, Sharpe, max-DD-adjusted return,
  profit-concentration (top-k share), skew/kurtosis. Frozen as diagnostics only.

## Null models (report separately; official = matched-null once validated)
- **A. Matched null (target official):** random ENTRY TIMING, preserving direction, #signals,
  and the realized RISK/stop-distance profile + exit rule + costs + one-position overlap. Tests
  whether the setup TIMING beats random with the same risk profile. NOTE: current implementation
  miscalibrated (fails synthetic-null); MUST be fixed+re-validated before official use.
- **B. Block bootstrap of the trade-R series (INTERIM OFFICIAL, VALIDATED):** resample contiguous
  blocks (length 5-10) of the realized R series, center at 0, one-sided. Preserves autocorrelation.
  Validated on synthetic controls: null→p≈0.42, clean edge(mean .25)→p≈0.0004. Tests robustness of
  mean>0 to trade sampling. Correctly rejects outlier-driven S1/S6 (p≈0.12-0.20).
- **C. IID bootstrap of trade-R:** diagnostic; ignores autocorrelation.

## p-value estimator & uncertainty (mandatory per hypothesis)
- p_hat = (k+1)/(B+1), k = #null draws ≥ observed. Never report p=0.
- Report: k, B, p_hat, Monte-Carlo CI (Wilson), null method, seed, statistic, relevant BH threshold.

## Adaptive Monte-Carlo (resolution vs BH threshold)
- BH first threshold at m valid hyps: alpha/m. For m=1552, alpha=0.05 → 3.2e-5.
- **MC-1 TRIAGE** B=20k (res≈5e-5): eliminate clearly-nonsignificant; CANNOT confirm an FDR pass.
- **MC-2 REFINEMENT** B≥200k for hyps near a BH threshold; compute CI; drop if CI wholly above threshold.
- **MC-3 CONFIRMATION** B≥1e6 (or sequential MC / stopping bounds) for hyps that can actually pass;
  MC resolution must be clearly below the individual BH threshold; save seed + exact sim count.
- If p CI intersects the BH threshold → status **UNRESOLVED — MORE SIMULATIONS REQUIRED**.

## FDR universe (frozen)
- Global-FDR over the **full eligible canonical universe** (all VALID hyps; invalids = ineligible,
  excluded from m with justification, NOT assigned fabricated p). Report m=1552 (valid) and
  conservative m=1704 (incl invalid) as diagnostic. NOT applied to only the screen-selected 106.
- Applied ONCE after S20, on the frozen deduped universe.

## Interaction with Discovery Screen V1 (unchanged)
- Screen V1 (n≥25, exp_research>0, PF≥1.02, maxDD≤25R, research-only, no OOS) produces RESEARCH
  CANDIDATES only. Strict validation (empirical p → global-FDR → OOS → walk-forward → Red Team →
  terminal holdout) is separate and computes p for the full eligible universe, not just RCs.

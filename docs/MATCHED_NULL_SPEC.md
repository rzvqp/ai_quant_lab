# MATCHED_NULL_SPEC — Test B (primary alpha-existence test) — FROZEN before implementation

Status: written BEFORE the fixed engine is run on any real hypothesis. Branch `matched-null-validation`,
base commit `1bc0ffb`. This spec fixes the design so the null cannot be tuned post-hoc to favor a result.

## 0. Question the test answers
"Do a hypothesis's signals pick BETTER moments than comparable counterfactual signals — same direction,
same number of trades, same realized risk/reward profile, same exit rule, same costs, same overlap policy,
same backtester — whose only difference is RANDOM entry timing?"

If the strategy's timing carries no edge, observed expectancy is a typical draw from the matched-null
distribution → p ~ Uniform(0,1). If timing carries edge, observed lands in the right tail → small p.

## 1. Primary statistic (FROZEN — chosen before seeing any p)
- Statistic = **mean expectancy per executed trade (R/trade)** on the research segment.
- **One-sided**, H0: mean_R ≤ 0 vs H1: mean_R > 0. (Same frozen statistic as EMPIRICAL_PVALUE_SPEC.)
- Diagnostics only (never the verdict): median R, trimmed mean, top-1/top-5 profit share, skew, n.

## 2. What is EXACTLY matched (held identical between observed and null)
Both observed and null trades are executed by the **same** `code/mstrat.py` `simulate()` (ENGINE v2), same `CFG`:
- entry rule = fill at `open[ei]`, ei = signal_bar + 1 (next-bar-open), identical to the engine;
- stop rule = pre-registered v2 stop-floor `max(2·spread·tick, 5·tick, 0.10·ATR[si])` applied by `simulate`;
- exit rule = same mechanism family (see §4 for the encoding);
- costs = `(spread_ticks+slip_ticks)·TICK`, charged 2× per round trip, identical;
- one-position overlap policy = `simulate`'s sequential `ei > last_exit` rule, identical;
- R unit = `(dir·(exit−entry) − 2·cost)/risk`, identical;
- number of executed trades = observed **k** is the target count for each null replicate (see §5);
- direction = the realized multiset of executed-trade directions (joint-bootstrapped, §4);
- realized risk/stop-distance profile = the realized executed-trade `|entry−stop|` distribution (§4);
- reward profile = the realized target distance in R-units (§4);
- research/OOS separation = null is generated and evaluated on the SAME segment as observed (research for
  calibration & the research p; validation reported separately). **Terminal holdout is NEVER touched.**

## 3. What is APPROXIMATELY matched (documented approximations)
- **Entry-timing pool**: null entries are drawn uniformly from the "eligible" bars = `{i : ATR[i] finite>0,
  2<i<n−2}` (the same bars the engine can trade). OPTIONAL stratification (real strategies only): restrict
  the pool to bars matching the strategy's realized strata — session/hour, calendar month, and ATR-quintile
  (volatility regime) — so the null shares the strategy's opportunity backdrop. Stratification is declared
  per-hypothesis BEFORE computing p; default = session+vol-regime strata for real hyps, none for synthetic
  homogeneous series.
- **Executed-trade count**: entries are drawn WITHOUT replacement with a small oversample so `simulate`'s
  overlap policy yields ≈ k executed trades; the primary statistic (mean R) is trade-count-robust. Any
  residual count drift is absorbed by the Monte-Carlo null and is CONSERVATIVE (fewer trades → wider null).
- **Opposite-liquidity/structure exits**: their absolute target price cannot be transplanted to a random
  entry, so they are matched by their realized **target distance in R-units** and executed via `simulate`'s
  `rr` branch (see §4). This preserves the reward geometry; it is an approximation of the exit *mechanism*.

## 4. Null signal construction (per replicate)
From the observed executed trades extract, per trade j: `risk_j = |open[ei_j] − stop_j|` (pre-floor),
`dir_j`, and an exit encoding `exit_enc_j`:
- `rr`   → (`rr`,  ep)                      (ep = the RR multiple)
- `time` → (`time`, ep)                     (ep = timeout bars)
- `trailing` → (`trailing`, None)
- `opp_liq`/`opp_struct` → (`rr`, clip(|target_price − open[ei_j]| / risk_j, 0.25, 10.0))
Form the joint sample `T = {(risk_j, dir_j, exit_enc_j)}_{j=1..k}`.

Per replicate b (seeded): draw k tuples from `T` (bootstrap, with replacement) and k entry bars `i` from the
eligibility pool (without replacement + oversample to hit ≈k executed). Build null setups
`{si=i, ei=i+1, dir, stop=open[i+1]−dir·risk, exit_kind, exit_param}` and run **`MS.simulate`**. Null statistic
= mean R of the executed null trades.

## 5. p-value estimator (FROZEN)
- `p = (k_ge + 1) / (B + 1)`, `k_ge` = #{null replicate mean ≥ observed mean}. **Never report p = 0.**
- Report per hypothesis: observed mean, n=k, k_ge, B, p, Monte-Carlo 95% CI (Wilson on k_ge/B), null mean/sd,
  seed, statistic, and (for real hyps) the BH threshold context — but NO significance verdict in this phase.

## 6. Adaptive Monte-Carlo (pilot only)
- MC-1 TRIAGE B = 20,000. MC-2 REFINEMENT B = 200,000 for hypotheses whose p CI is near a decision band.
- MC-3 CONFIRMATION B ≥ 1,000,000 only if resolution is still insufficient. Save seed + exact counts.
- If the p CI straddles the relevant threshold → status **UNRESOLVED — MORE SIMULATIONS REQUIRED**.
- Calibration/power batteries use B = 2,000 (calibration) / B = 1,000 (power) per series — sufficient for
  distributional (uniformity/power) tests over ≥100 / ≥50 independent series; justified by measured
  throughput (~10–22 ms/replicate). These B's are for VALIDATION, not for issuing real-strategy p verdicts.

## 7. Calibration criteria (engine accepted only if ALL hold)
On ≥100 independent synthetic NULL price series (no injected edge), each with a structured synthetic
hypothesis run through the full pipeline:
- p-value distribution ≈ Uniform(0,1): KS test p_KS > 0.05 (fail if < 0.01); no mass spike at 0.
- FPR(0.05) ∈ [0.02, 0.08]; FPR(0.01) ∈ [0.002, 0.02]; FPR(0.10) ∈ [0.06, 0.15] (95% binomial CIs must
  cover the nominal level).
- No p = 0; results stable across two disjoint master-seed halves (FPR difference within CI).

## 8. Power criteria (engine accepted only if ALL hold)
On ≥5 injected-edge magnitudes {0, tiny, small, moderate, large} × ≥3 signal frequencies × ≥50 series each:
- power is **monotonically non-decreasing** in edge magnitude at α=0.05 and α=0.01;
- power at edge=0 equals the FPR (≈ α) — consistency with calibration;
- power → high (≥0.8 target, reported not gated) at large edge for moderate n;
- estimator bias (observed mean − injected edge) small and documented; sensitivity to n, skew/outliers,
  and regime reported.

## 9. Adversarial robustness (must not break calibration)
Calibration re-checked (p uniform under NULL) on price series with: strong long drift; short trend; range;
volatility clustering; regime shifts; signals concentrated in one year; signals concentrated in one session;
variable structural stops; rr / time / trailing exits; low- and high-frequency strategies; single-outlier
and top-5-dominant P&L; missing months; high overlap. A pass = FPR stays within the §7 band under each.

## 10. Engine acceptance verdict (end of validation)
- **A. MATCHED-NULL VALIDATED** — §7 + §8 + §9 all pass; parity (§11) confirmed; reproducible; no critical defect.
- **B. CONDITIONALLY VALID** — passes for some strategy classes only; limitations documented explicitly.
- **C. INVALID** — FPR/power/parity unacceptable; not usable for verdicts.
No strategy verdict is issued in this phase regardless of engine verdict.

## 11. Parity requirement
Observed and null BOTH execute via `MS.simulate` with the shared `CFG`. Automated tests assert: (a) the
engine's observed R equals `MS.backtest` R for the same hypothesis; (b) null setups are executed by
`MS.simulate` (same cost/floor/overlap/intrabar/R); (c) only the research (or declared) segment is passed —
the terminal holdout slice is never included.

## 12. Invalidation conditions (stop + CEO gate)
Anything that would change `mstrat.simulate`/setups/CFG/stop-floor/screen/S1–S20 definitions, open the
holdout, or issue a strategy verdict is OUT OF SCOPE for this phase and requires a new CEO approval.

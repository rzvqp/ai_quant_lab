# MATCHED_NULL_VALIDATION — Test B engine validation report (branch matched-null-validation)

Base commit 1bc0ffb. Engine + batteries + pilot all on the reproducible baseline. **No strategy verdict is
issued here** — this validates the matched-null ENGINE, not any strategy. Holdout SEALED throughout.

## 1. What was fixed (root cause of the prior miscalibration)
The old matched-null (`pilot_pvalue.py`) compared **bare synthetic R-series** to a null built from **real
XAUUSD prices** — two different data-generating processes at different scales → spurious p≈0.0002 on a
synthetic null. The fix (docs/MATCHED_NULL_SPEC.md): validate on synthetic **PRICE** series where observed
AND null both execute through the **same `mstrat.simulate` (ENGINE v2)**; the null preserves direction,
executed-trade count, exit rule, costs, overlap, and the **risk/ATR profile** (rescaled to local ATR at the
counterfactual entry), randomizing only entry TIMING. p=(k+1)/(B+1), one-sided H0: mean_R≤0.

## 2. A second defect found DURING validation (adversarial battery)
First engine version bootstrapped **absolute** risk. The adversarial battery exposed catastrophic false
positives under trend: **drift_long FPR=0.975, trend_short=0.925, regime_shift=0.25**. Cause: absolute risk
sampled from a late high-ATR bar applied at an early low-ATR bar mismatches local volatility, diluting the
null's drift capture so observed always "won". Fix: bootstrap **risk/ATR ratio** and rescale to the ATR at the
null entry. Post-fix: drift_long **0.00**, trend_short **0.00**, regime_shift **0.00**. (This is exactly the
drift-beta control that matters for the long-biased real strategies.)

## 3. Calibration (§7) — PASS
120 synthetic NULL price series (mixed vol-clustering, 4 exit/stop templates), B=2000:
- p ~ Uniform: mean p=0.499, **KS p=0.113** (cannot reject uniformity), no p=0, min p=0.023.
- FPR(0.10)=0.058 CI[0.029,0.116] ✓ · FPR(0.05)=0.025 CI[0.009,0.071] ✓ · FPR(0.01)=0.000 CI[0,0.031] ✓
- split-half FPR05 stable [0.017, 0.033]. **CALIBRATED = True.** (Slightly conservative — safe direction.)

## 4. Power (§8) — PASS
5 edge magnitudes × 3 frequencies × 50 series, B=1000, edge injected as forward ATR-bumps:
- **Monotone in edge at every frequency**; power at edge=0 ≈ α (0.00–0.06); power at edge=1.0·ATR = 0.98–1.00.
- Higher trade-frequency → more power at the same edge (freq 200/400 > 80 at mid edges). Estimator gap
  (observed−null) rises monotonically with injected edge. `monotonic_all05 = power_at_zero_ok = high_edge_power_ok = True`.

## 5. Adversarial robustness (§9) — PASS (all 12 scenarios)
Under strong long drift, short trend, range/AR(1), vol-clustering, regime shift, heavy gaps, structural stops,
time & trailing exits, low- and high-frequency, and signals concentrated in one year: **FPR(0.05) ≤ 0.075 in
every scenario** (most 0.00–0.05). `ALL_SCENARIOS_CALIBRATED = True`.

## 6. Parity (§11) — PASS
`tests/test_matched_null_parity.py`: observed R **exactly equals** `MS.backtest` R (k=415, max abs diff <1e-12);
null setups execute via `MS.simulate` with the v2 stop-floor; only the research/validation slice is passed
(research ends idx 50490 < holdout start 67321). Synthetic-generator + fast-calibration guards also pass.

## 7. Pilot on 10 pre-registered real hypotheses (§6) — engine behaves correctly
Ids pre-registered in `pilot_prereg.json` BEFORE any p. Unstratified ATR-scaled config (the validated one).
Research B=20k (refined to 200k if research p<0.05), validation B=10k, reported SEPARATELY. **NO verdict.**

| hypothesis | family | res k | res obs | **res p** | val obs | val p |
|---|---|---|---|---|---|---|
| S1_representative | S1 | 399 | +0.032 | 0.0049 | −0.061 | 0.527 |
| S5_representative | S5 | 406 | +0.076 | **0.0323** | +0.237 | **0.0382** |
| S9_representative | S9 | 687 | +0.062 | 0.229 | +0.171 | 0.301 |
| S6_extreme (tiny-stop) | S6 | 240 | +0.497 | 0.0050 | +0.685 | 0.147 |
| unprofitable_S6 | S6 | 347 | −0.801 | 0.998 | −0.455 | 0.453 |
| unprofitable_S6 | S6 | 327 | −0.796 | 0.861 | −0.695 | 0.706 |
| fragile_profitable_S14 | S14 | 118 | +0.285 | 0.0216 | −0.148 | 0.258 |
| fragile_profitable_S1 | S1 | 175 | +0.142 | 0.115 | +0.196 | 0.297 |
| research_worthy_S20 | S20 | 469 | +0.055 | 0.277 | +0.137 | 0.362 |
| research_worthy_S20 | S20 | 456 | +0.075 | 0.099 | +0.087 | 0.424 |

Sanity signals (engine, not strategies):
- **Unprofitable hypotheses correctly get high p (0.86, 0.998)** — the test does not flag losers.
- 4 hypotheses are research-significant (p<0.05); **only S5 is ALSO validation-significant** (+0.237 OOS,
  p=0.038). S1, S6-extreme, S14 are research-significant but **fail out-of-sample** — the honest, expected
  pattern (most apparent edges do not survive OOS), consistent with the lab's retracted-conclusions history.
- Note S6-extreme: low matched-null p (good *timing*) yet known outlier/tiny-stop fragile — matched-null (Test B,
  timing) and block-bootstrap (Test A, outlier robustness) answer DIFFERENT questions; a low Test-B p does NOT
  imply robustness. Both tests are needed.

## 8. Reproducibility
`seeds.json`, `runtime_versions.json` (python 3.14.6, numpy 2.5.1, pandas 3.0.3, pyarrow 25.0.0), data
sha256, base commit recorded. All batteries are seeded and deterministic.

## 9. Limitations (explicit)
1. Validated in the **unstratified + ATR-scaled** configuration only. Session×vol **stratified** nulls are NOT
   separately validated → deferred (the pilot used the validated unstratified config).
2. Slightly **conservative under strong drift** (mean p>0.5) — this is the desired safe direction (it removes
   drift-beta) but means the test is a touch harder to pass for genuinely-timed edges in a trending market.
3. Pilot p-values are **per-hypothesis and PRE-FDR**. Under the frozen global-FDR (m=1552, BH first threshold
   ≈3.2e-5) **none of these would be significant**. No strategy verdict follows from this pilot.
4. Calibration/power B (2000/1000) sized for distributional tests, not for individual-hypothesis FDR
   resolution; the pilot uses adaptive MC (20k→200k) for that.

## 10. ENGINE VERDICT (§10)

# ✅ A — MATCHED-NULL VALIDATED
Calibration, power, and adversarial robustness all PASS on the corrected (ATR-scaled) engine; parity with
`mstrat.simulate` is proven; the engine is reproducible and behaves correctly on real data (rejects losers,
gives low p to timed edges, exposes OOS failure). It is fit to serve as **Test B (primary alpha-existence
test)** in the frozen pipeline, in its validated unstratified configuration.

**No strategy verdict issued. Global-FDR, walk-forward, Red Team, and the sealed holdout remain gated on a new
CEO decision.** Next: apply the validated matched-null within global-FDR over the frozen eligible universe.

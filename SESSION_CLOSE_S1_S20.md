# SESSION_CLOSE_S1_S20 — 2026-07-13

## A. Executive summary
This session pivoted the lab to ALPHA-FACTOR portfolio discovery, built the XAUUSD MTF dataset (verified vs
TradingView), built ONE common multi-strategy backtest engine (mstrat.py, engine v2), implemented and
historically backtested all 20 families S1-S20 (1,972 canonical hypotheses), and began a rigorous statistical
remediation. Historical (in-sample) results: **357 profitable, 130 research-worthy variants across 14/9 families**
— NOT collapsed to zero. All statistical significance is **PENDING** (analytic p-value proven invalid; empirical
engine under validation). Holdout SEALED throughout. Everything is saved durably in this folder.

## B. Progress this session
- XAUUSD data via TradingView Replay: M15 84,151 bars 2023-01-02→2026-07-13; H1 20,832; H4 5,450; D1 909; NY-17:00 anchored; cross-check vs native = 0 mismatches.
- Common engine mstrat.py: shared simulate + parity ref + 20 families + shared null; grammar 1,972; parity+smoke PASS; lookahead-safe.
- Engine v1→v2: pre-registered stop-floor.
- Full S1-S20 historical backtest (results/full.log, FAMILY_RESULTS.parquet).
- Statistical audit: analytic-p invalidated; S6 & S1 outlier audits; p-engine pilot; specs frozen.

## C. Decision timeline (CEO directives, in order)
1. Multi-strategy campaign mandated (common engine, global-FDR, holdout sealed). 2. Discovery Screen / Strict
Validation separation. 3. Portfolio reframe → alpha FACTORS (permanent). 4. Screen = recall (5-15% diagnostic,
not quota); freeze Screen V1; remove OOS from screen; global-FDR over full universe. 5. Approve p-value fix with
strict MC spec (adaptive MC, matched-null, frozen statistic). 6. PRIORITY: finish S1-S20 historical backtest;
stats PENDING; don't let strict filters produce "0". 7. Session close & official save (this deliverable).

## D. Strategies / families discussed (all experimental)
S1 liquidity-sweep mean-rev · S2 failed-breakout fade · S3 breakout-retest · S4 vol-regime expansion ·
S5 opening-range momentum · S6 session-transition · S7 trend-pullback · S8 extension mean-rev · S9 MTF-momentum ·
S10 displacement continuation · S11 structure-break reversal · S12 range rotation · S13 imbalance fill ·
S14 momentum exhaustion · S15 trend acceleration · S16 previous-day levels · S17 weekly levels · S18 time-of-day ·
S19 session gap · S20 hybrid sweep+MTF. Most robust research-worthy: **S5, S17, S9, subset of S1** (see PROJECT_STATE §6).

### Central table (verified, results/full.log; ENGINE v2; stats PENDING; A=hist-profitable? B=research-worthy count; C=STRICT VALIDATION PENDING)
| S | econ | gen | valid | profit | bestExp | bestPF | RW(B) | A |
|---|---|---|---|---|---|---|---|---|
| S1 | liquidity-sweep mean-rev | 1152 | 1000 | 261 | 0.391 | 24.63 | 90 | Yes |
| S2 | failed-breakout fade | 144 | 144 | 18 | 0.075 | 1.11 | 6 | Yes |
| S3 | breakout-retest | 96 | 96 | 2 | 0.063 | 1.09 | 0 | Yes |
| S4 | vol-regime expansion | 32 | 32 | 0 | −0.145 | 0.81 | 0 | No |
| S5 | opening-range momentum | 96 | 96 | 20 | 0.166 | 1.48 | 12 | Yes |
| S6 | session-transition | 32 | 32 | 7 | 0.497 | 1.37 | 3 | Yes |
| S7 | trend-pullback | 24 | 24 | 0 | −0.099 | 0.87 | 0 | No |
| S8 | extension mean-rev | 48 | 48 | 4 | 0.029 | 1.04 | 2 | Yes |
| S9 | MTF-momentum | 32 | 32 | 12 | 0.068 | 1.15 | 6 | Yes |
| S10 | displacement continuation | 48 | 48 | 0 | −0.051 | 0.94 | 0 | No |
| S11 | structure-break reversal | 24 | 24 | 0 | −0.052 | 0.88 | 0 | No |
| S12 | range rotation | 48 | 48 | 0 | −0.036 | 0.96 | 0 | No |
| S13 | imbalance fill | 24 | 24 | 5 | 0.041 | 1.08 | 0 | Yes |
| S14 | momentum exhaustion | 16 | 8 | 6 | 0.579 | 2.42 | 1 | Yes |
| S15 | trend acceleration | 24 | 24 | 0 | −0.050 | 0.92 | 0 | No |
| S16 | previous-day levels | 40 | 40 | 1 | 0.032 | 1.04 | 0 | Yes |
| S17 | weekly levels | 24 | 24 | 6 | 0.424 | 1.43 | 5 | Yes |
| S18 | time-of-day | 24 | 24 | 5 | 0.177 | 1.31 | 0 | Yes |
| S19 | session gap | 12 | 0 | 4 | 0.915 | 3.69 | 0 | Yes* |
| S20 | hybrid sweep+MTF | 32 | 32 | 6 | 0.099 | 1.24 | 5 | Yes |
(*S19 profitable variants have n<25 → not research-worthy; %-profit display bug noted in PROJECT_AUDIT D5.)
Full top-20 lists (profitable / monthly-stability / profit-DD / fragile) are in results/full.log.

## E. Architecture changes
- ONE common backtester (mstrat.simulate) for all families + parity ref. Engine v2 stop-floor.
- Discovery Screen / Strict Validation separation. Frozen primary statistic. Data splits with sealed holdout.

## F. Statistical validation status
STRICT VALIDATION PENDING — P-VALUE ENGINE INVALIDATED. No significance / FDR / final verdicts. See PROJECT_AUDIT §B.

## G. Discovery Screen status
V1 FROZEN (n≥25, exp>0, PF≥1.02, maxDD≤25R, research-only, no OOS). Development-tuned; S11-S20 = prospective test. Produces RESEARCH CANDIDATES only.

## H. p-value engine status
Analytic normal-approx INVALIDATED for verdicts. IID/block bootstrap = Test A (robustness) METHOD UNDER VALIDATION.
Matched-null = Test B (primary alpha test) MISCALIBRATED, fix pending. Primary statistic frozen = expectancy, one-sided.

## I. Holdout status
Terminal holdout = last 20% of M15 (16,831 bars) SEALED; NEVER opened this session. Opening = CEO gate.

## J. Complete TODO (see NEXT_SESSION.md for order)
1. Fix+validate matched-null on synthetic PRICE series (≥100 nulls uniform p; power curve; FPR; seeds).
2. Choose official p-method before results; adaptive MC (MC-1/2/3, CI, seeds); p=(k+1)/(B+1).
3. Wire INVALID-EXECUTION + finalize stop-floor; re-run S1-S20 if execution changes.
4. Global-FDR over full eligible universe; then walk-forward + Red Team.
5. Portfolio Architect: factor correlation with CI/stability → low-correlation shortlist.
6. CEO gate before opening terminal holdout. No live trading.

## K. Files created/modified this session (durable copies in this folder)
- code/ (29 .py): OFFICIAL mstrat.py (engine v2, 20 families), run_lot.py, run_full_campaign.py; MTF/pipeline
  (mtf.py, run_mtf.py, run_prod.py, families.py, campaign.py, alpha_lab.py, s1.py[deprecated], run_s1.py, run_lot2_factors.py);
  data build (resample_ny.py, quality_and_resample.py, build_gc_bars.py); audits (s6_audit.py, robustness_s1.py,
  drift_core.py, audit_s1_diff.py, pilot_pvalue.py, calibrate_screen.py, freeze_screen_v1.py, validate_*, diag*, gapfind.py, gate*/probe*/prep_probe/normcheck/synth_dualtest/reconstruct_and_build).
- data/market/: OANDA_XAUUSD_{M15,H1,H4,D1}.csv (verified vs native).
- docs/: ALPHA_REGISTRY.md, EMPIRICAL_PVALUE_SPEC.md, MIN_STOP_FLOOR_PREREG.md, MONTE_CARLO_AUDIT.md.
- results/: FAMILY_RESULTS.parquet, PROJECT_STATE_v1.0.json, run logs (full/lot1/lot2/pilot/frozen/calib), gap_dates.json.
- pullers/: pull_replay_m15.mjs, pull_gapfill.mjs, pull_native.mjs, pull_data.mjs, pull_h1.mjs.
- foundation_gc/engine.py (Phase-B GC order-book reconstruction).
- Root: PROJECT_STATE_v1.0.md, PROJECT_AUDIT.md, NEXT_SESSION.md, CHANGELOG.md, SESSION_CLOSE_S1_S20.md, requirements.txt.

## L. Commit summary (no Git used)
feat(data): XAUUSD M15/H1/H4/D1 via Replay, NY-17:00 anchored, cross-checked vs native (0 mismatch)
feat(engine): common multi-strategy backtester mstrat.py v2 (stop-floor) + 20 families S1-S20 (1972 hyps)
feat(campaign): full S1-S20 historical backtest → 357 profitable / 130 research-worthy / 14 families
fix(screen): freeze Discovery Screen V1 (research-only, no OOS)
audit(stats): invalidate analytic p-value; prove S6/S1 outlier cause; pilot empirical engine (matched-null pending)
docs(save): durable ai_quant_lab/ with full official state + specs
NOTE: strict validation PENDING; holdout SEALED; no live trading.

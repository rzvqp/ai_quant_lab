# PROJECT_AUDIT — open defects, debts, method validity (2026-07-13)

## A. Confirmed defects
| id | severity | description | status |
|---|---|---|---|
| D1 | HIGH | Analytic normal-approx p-value invalid in extreme tail (heavy-tailed R) → spurious tiny p / false FDR passes. Proven: S6 analytic 2.14e-54 vs empirical bootstrap ~0.12. | retracted from verdict role; needs official empirical engine |
| D2 | HIGH | R-normalization / tiny-stop explosion: structure stops (prev_ext/beyond_sweep/structural) can be ~0 from entry → R=pnl/risk explodes (S6 R up to +166; top-5=71% profit; maxDD 89.8R v1 → 85R v2). | partially mitigated by v2 stop-floor; INVALID-EXECUTION not wired |
| D3 | HIGH | Matched-null (Test B, PRIMARY alpha test) miscalibrated: p≈0 on synthetic-null (construction/scale mismatch). | **RESOLVED 2026-07-13.** Original commits `28c35b6`→`aa5bee3`→`69747fd` (branch matched-null-validation / flow-c-foundation, base `1bc0ffb`), cherry-picked onto `statistician-foundation` 2026-07-25. Rebuilt on synthetic PRICE series routed through mstrat.simulate; a 2nd defect (absolute-risk bootstrap → FPR 0.97 under drift) fixed via risk/ATR rescaling. Calibration+power+adversarial+parity all PASS → **VALIDATED (Verdict A)**, unstratified + ATR-scaled config ONLY. See docs/MATCHED_NULL_VALIDATION.md. **Scope caveat (2026-07-25):** validated regime = 1.5×ATR stops on generic signals; structural-stop families (the D2 sources) were never in the calibration battery → matched-null is NOT validated for them. D2 remains HIGH/OPEN and gates any structural-stop use. |
| D4 | MED | Discovery Screen V1 thresholds calibrated on S1-S10 results = DEVELOPMENT-TUNED (selection-bias). | frozen; S11-S20 = prospective test |
| D5 | LOW | run_full_campaign.py %-profitable display bug (÷valid=0 → 400% for S19). Counts correct. | cosmetic |
| D6 | MED | Top-by-expectancy / top-by-profit-DD lists dominated by low-n flukes (S1 n=3-5, PF≈99). | use RESEARCH_WORTHY + monthly-stability lists |
| D7 | INFRA | Lab code+data were only in ephemeral Temp scratchpad. | fixed: copied to durable ai_quant_lab/; GC MBO raw (data2) still Temp-only (re-downloadable) |
| D8 | INFRA | Secondary hardcoded Temp paths remain in NON-campaign scripts: resample_ny.py, quality_and_resample.py, run_prod.py (data-rebuild), run_cycle.py, build_gc_bars.py, foundation_gc/engine.py (GC foundation). | deferred: not on the official S1–S20 campaign path; repoint only if those scripts are rerun. Campaign path (mtf.py) FIXED 2026-07-13. |
| D9 | INFRA | requirements.txt omits a parquet engine (pyarrow) though the campaign writes/reads FAMILY_RESULTS.parquet. | add `pyarrow` to requirements.txt (installed manually this session). |
| D10 | DOC | Docs state M15=84,151 bars; actual file = 84,152 (wc off-by-one, no trailing newline). Proven benign (exact reproduction; holdout 16,831 matches). | correct the figure in docs; no data/result change. |

## A.1 Reproducibility status (2026-07-13)
- Portability fix (D-critical `mtf.py`) applied; official campaign re-run on a fresh venv (pandas 3.0.3/numpy 2.5.1, newer than original) reproduced the baseline **EXACTLY** (Verdict A): 1972/1800/357/130/14/9; per-hypothesis parquet max abs diff 0.0; total trades 1,300,740 identical; boolean verdicts identical; 0 Temp reads; holdout SEALED. Baseline not overwritten (new run in results/reproduction_v2/). Pre-fix git checkpoint `85857234`. See PORTABILITY_AUDIT.md, REPRODUCIBILITY_AUDIT.md.

## B. Method validity status (ALL under validation)
- Analytic p-value: INVALID for verdicts (diagnostic only).
- IID bootstrap (Test A robustness): H0-centering proven correct; METHOD UNDER VALIDATION.
- Block bootstrap (Test A robustness): well-calibrated on 2 synthetic controls; METHOD UNDER VALIDATION (needs full battery).
- Matched-null (Test B, primary): MISCALIBRATED; fix required.
- Global-FDR: NOT yet run with a valid p-value. Universe = full eligible valid (m=1552; 1704 conservative diagnostic).

## C. Retracted conclusions (audit trail)
1. "S1 = mostly long-bias/drift" — REFUTED (drift_core.py: random-long baseline −0.087R; S1 excess +0.31R).
2. "S1/S5/S9 decorrelated" — RETRACTED (single unstable monthly-R point estimate; no CI/stability/canonical representative).
3. "No Research Candidate significant" — RETRACTED (only S1-rep + S6 tested under pilot; reformulated to those two only).
4. S1-standalone "6 Discovery Candidates" (s1.py) — SUPERSEDED (family-favorable ATR-null + per-family FDR; not a candidate under mstrat.py unified engine + global FDR).

## D. Frozen decisions (do not change without CEO gate)
- Primary statistic = mean expectancy R/trade, one-sided (H0: mean≤0).
- Discovery Screen V1 = n≥25 & exp_research>0 & PF≥1.02 & maxDD≤25R & research-only (no OOS).
- Stop-floor formula = max(2×spread, 5×tick, 0.10×ATR) (pre-registered).
- Data splits research 60% / validation 20% / terminal holdout 20% SEALED (never opened).

## E. Governance
- Holdout terminal: SEALED, never opened this session. Opening = CEO gate only.
- No live trading. No candidate optimization. No REJECTED verdicts while p-engine invalidated.

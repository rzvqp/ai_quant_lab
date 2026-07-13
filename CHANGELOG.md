# CHANGELOG — AI Quant Research Lab

## Session 2026-07-13 (b) — Portability fix + reproducibility test (CEO-approved, scope-limited)
- **Git checkpoint:** folder was un-versioned → `git init` + baseline commit `85857234bad5172634e9c2b603e873976a204470` (pre-fix, 58 files). Added `.gitignore` (venv/, __pycache__/).
- **Portability (class A only):** `code/mtf.py` `D` repointed from hardcoded Temp → `Path(__file__).resolve().parents[1]/"data"/"market"` (str-typed, env override `AI_QUANT_DATA_DIR`). This single constant feeds the whole campaign chain (mstrat/s1/mtf). Secondary Temp paths (data-rebuild + GC-foundation scripts) classified and DEFERRED as debt D8 (not on campaign path).
- **Environment:** created `venv` (Python 3.14.6); installed requirements + pyarrow (parquet engine missing from requirements = debt D9). Versions newer than original (pandas 3.0.3/numpy 2.5.1/pyarrow 25.0.0).
- **Reproduction = EXACT (Verdict A):** re-ran `run_full_campaign.py` (ENGINE v2) into `results/reproduction_v2/` → bit-exact vs baseline: 1972/1800/357/130/14/9; per-hypothesis parquet max abs diff 0.0; total trades 1,300,740 identical; boolean verdicts identical; 0 Temp reads; holdout SEALED; baseline untouched.
- **Data note (D10):** M15 file has 84,152 bars (docs said 84,151 = wc off-by-one, no trailing newline); proven identical to baseline data. No data/result change.
- New artifacts: PORTABILITY_AUDIT.md, REPRODUCIBILITY_AUDIT.md, results/reproduction_v2/{full.log, FAMILY_RESULTS.parquet, ENGINE_RUNTIME_PATHS.json, comparison.json}. Marked stale (non-destructive): results/PROJECT_STATE_v1.0.json, docs/ALPHA_REGISTRY.md.
- **Unchanged:** methodology, S1–S20 definitions, thresholds, holdout, p-value engine. Matched-null NOT started (awaits a new CEO gate).

---

## Session 2026-07-12 → 2026-07-13 (AI Quant Research Lab)

Chronological, verified from code/logs. Earlier foundation (COMEX GC) summarized; main work is the pivot to alpha discovery.

## Foundation (closed)
- COMEX GC MBO acquired (Databento, legacy normalization, GCQ6 iid=42011464, 2026-06-29→07-10).
- Phase B: order-book reconstruction validated **bit-exact vs MBP-10** (foundation_gc/engine.py); dual-compatible legacy/new parser.
- MBO micro-structure discovery (trajectory-divergence design): **NEGATIVE** — no reproducible pre-price MBO edge (60k+ hypotheses).

## Pivot → AI Quant Research Lab (alpha discovery)
- Designed 6-AI separation-of-powers architecture (Director/Generator/Backtest/Statistician/RedTeam/Portfolio).
- Built MVP alpha pipeline (code/alpha_lab.py, families.py, campaign.py, run_mtf.py, mtf.py); validated with positive/negative controls.

## Data (XAUUSD)
- Built M15 history 2023→2026 via TradingView **Replay** (pullers/pull_replay_m15.mjs): 84,151 bars.
- Gap-filled ~5,000 missing M15 bars at replay-window boundaries (pull_gapfill.mjs).
- Resampled H1/H4/D1 anchored **17:00 NY (DST-aware)** (code/resample_ny.py).
- **Cross-check vs native TradingView OANDA = PASS** (0 OHLC mismatches, 2023-2026, all DST changes).

## Multi-strategy campaign
- Built ONE common engine `code/mstrat.py` (shared simulate + simulate_ref parity + 20 families + shared null).
- Implemented families **S1-S20**; grammar = 1,972 canonical hyps; parity + smoke PASS; lookahead-safe.
- Discovery Screen V1 **FROZEN**: n≥25, exp_research>0, PF≥1.02, maxDD≤25R, research-only (no OOS). Development-tuned.
- **Engine v1 → v2**: added pre-registered stop-floor `executable_stop=max(strategy_stop, max(2×spread,5×tick,0.10×ATR))`.
- Ran **full S1-S20 historical backtest on engine v2** → results/FAMILY_RESULTS.parquet + full.log:
  **1,972 gen · 1,800 valid · 357 HIST-PROFITABLE · 130 RESEARCH-WORTHY · 14 families profitable · 9 research-worthy.**

## Statistical remediation (in progress)
- Proved **analytic normal-approx p-value INVALID in tail** (S6: 2.1e-54 analytic vs ~0.12 empirical) → retracted from verdicts.
- **S6 audit**: extreme p caused by tiny-stop outliers + profit concentration (skew 8.3, kurt 77.6; top-5=71% profit) = R-normalization artifact.
- **S1-rep robustness**: NOT tiny-stop (risk/ATR 2.12) but outlier/time-concentrated (remove top-1→exp −0.02; edge only 2024). NOT rejected.
- Pilot p-engine (docs/MONTE_CARLO_AUDIT.md): block-bootstrap well-calibrated (synthetic controls) but METHOD UNDER VALIDATION; matched-null miscalibrated (fix pending).
- Pre-registered stop-floor spec (docs/MIN_STOP_FLOOR_PREREG.md); frozen primary statistic = expectancy, one-sided (docs/EMPIRICAL_PVALUE_SPEC.md).

## Retractions
- "S1=drift", "S1/S5/S9 decorrelated", "no RC significant", S1-standalone "6 candidates" — all RETRACTED/superseded (see PROJECT_STATE §9).

## Session close (2026-07-13)
- Consolidated lab (code + data + docs + results + pullers) to durable `C:\Users\MEDION GAMING\ai_quant_lab\`.
- Wrote PROJECT_STATE_v1.0.md, PROJECT_AUDIT.md, NEXT_SESSION.md, CHANGELOG.md, SESSION_CLOSE_S1_S20.md.

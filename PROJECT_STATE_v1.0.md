# PROJECT_STATE — AI Quant Research Lab — v1.0 (session close 2026-07-13)

Mission (CEO, permanent): discover and build a PORTFOLIO of INDEPENDENT ALPHA FACTORS.
Unit of research = alpha FACTOR (economic mechanism), not a single strategy. Falsification-first.
Everything below is verified from on-disk code/artifacts in this folder — nothing reconstructed from memory.

Durable project home (this folder): `C:\Users\MEDION GAMING\ai_quant_lab\`
- `code/` = 29 Python modules  · `data/market/` = XAUUSD OHLCV CSVs  · `docs/` = spec/audit docs
- `results/` = FAMILY_RESULTS.parquet + run logs  · `pullers/` = TradingView CDP data pullers (.mjs)
- `foundation_gc/engine.py` = Phase-B order-book reconstruction engine (GC, closed track)
Runtime: Python 3.14 venv (recreate: `pip install -r requirements.txt` = databento, pandas, numpy, sortedcontainers, zstandard). Original venv was in ephemeral Temp; not copied.

## 1. WHAT IS ACTUALLY IMPLEMENTED
- **Data pipeline (XAUUSD)**: M15 history built via TradingView **Replay** stepping (pullers/pull_replay_m15.mjs) + gap-fill (pull_gapfill.mjs). Resampled to H1/H4/D1 anchored to **17:00 America/New_York (DST-aware)** (code/resample_ny.py). **Cross-checked bit-exact vs native TradingView OANDA bars** (0 OHLC mismatches over 2023-2026). Files: `data/market/OANDA_XAUUSD_{M15,H1,H4,D1}.csv`.
  - Verified bar counts: **M15=84,151 · H1=20,832 · H4=5,450 · D1=909**, coverage 2023-01-02 → 2026-07-13.
- **Common multi-strategy engine (OFFICIAL)**: `code/mstrat.py` — one shared backtester `simulate()` (ENGINE **v2**, pre-registered stop-floor active) + `simulate_ref()` (parity) + 20 family setup-providers (S1-S20) + features (context H4/H1/D1, session, PDH/PDL, PDopen/close/mid, PW high/low, gap, VWAP, FVG, ATR, swings, opening range, compression). Grammar = **1,972 canonical hypotheses**. Lookahead-safe; parity + smoke PASS.
- **Pipeline (code/run_lot.py, run_full_campaign.py)**: Discovery Screen V1 (frozen) → strict-validation stages. Splits research 60% / validation 20% / **holdout 20% SEALED**.
- **Full S1-S20 historical backtest executed** on engine v2 → `results/FAMILY_RESULTS.parquet` + `results/full.log`.
- **Foundation (closed track)**: COMEX GC MBO order-book reconstruction validated bit-exact (Phase B, foundation_gc/engine.py). MBO micro-structure discovery = **NEGATIVE** (no reproducible pre-price edge). GC raw data lives in ephemeral `scratchpad/phaseb/data2` (re-downloadable from Databento; not copied — large).

## 2. WHAT IS NOT YET IMPLEMENTED
- Validated **matched-null (Test B)** = the PRIMARY alpha-existence test (current impl miscalibrated).
- Official empirical **p-value engine** (all methods = METHOD UNDER VALIDATION) + adaptive MC (MC-1/2/3).
- **Global-FDR** with a valid p-value (only ran with the invalidated analytic p).
- Walk-forward + Red Team as final strict verdict (framework exists in run_lot.py but gated on p-engine).
- Portfolio Architect (factor correlation with CIs/stability; portfolio construction).
- INVALID-EXECUTION marking + full R-normalization audit wiring (spec written, not enforced in engine).
- Incremental official registries beyond ALPHA_REGISTRY / FAMILY_RESULTS.

## 3. MULTI-STRATEGY CAMPAIGN STATE
- Lots 1-4 (S1-S20) all IMPLEMENTED and BACKTESTED historically on engine v2.
- Statistical verdict: **STRICT VALIDATION PENDING** (p-engine under remediation). No significance/FDR verdicts issued. No family marked REJECTED.

## 4. S1-S20 STATUS (verified from results/full.log; research segment; stats PENDING)
Totals: generated **1,972** · valid(n≥25) **1,800** · **HISTORICALLY PROFITABLE 357** · **RESEARCH WORTHY 130**.
- Families with ≥1 historically profitable (14): S1,S2,S3,S5,S6,S8,S9,S13,S14,S16,S17,S18,S19,S20.
- Families with 0 profitable (6): S4,S7,S10,S11,S12,S15.
- Families with ≥1 RESEARCH WORTHY (9): S1,S2,S5,S6,S8,S9,S14,S17,S20.
- Definitions: HISTORICALLY PROFITABLE = profit>0 & exp>0 & PF>1.00 & valid execution. RESEARCH WORTHY = n≥25 & exp>0 & PF≥1.02 & maxDD≤25R & not-single-trade-dependent & activity in >1 period.

## 5-6. STRATEGIES THAT EXIST vs EXPERIMENTAL
- All 20 are family templates (grammars), NOT deployable strategies. Everything is **experimental / research-stage**.
- Most robust-looking research-worthy (by trade count + monthly stability + low DD + non-outlier t1≈.01-.07): **S5 opening-range momentum** (n~290, exp .14-.17R, PF 1.40-1.48, DD 7R, 18-19/27 pos months), **S17 weekly-levels** (n~170, exp .20-.29R, PF 1.3-1.43, DD 13-16R), **S9 MTF-momentum** (n545, exp .068R, PF 1.15), some **S1 liquidity-sweep** variants (n316-399, low exp .03-.06R, t1=.01, 18-20/26 mo). These are candidate FACTORS, unvalidated.

## 7-8. RESULTS OBTAINED / PROVISIONAL
- All results are PROVISIONAL / in-sample (research segment). None validated. Holdout untouched.

## 9. CONCLUSIONS RETRACTED (do not re-assert)
- "S1 edge is mostly long-bias/drift" — REFUTED (random-long baseline = −0.087R; S1 excess +0.31R; not drift).
- "S1/S5/S9 factors are decorrelated" — RETRACTED (single unstable monthly-R point estimate; no CI/stability).
- "No Research Candidate is significant" — RETRACTED (only S1-rep + S6 were tested under the pilot).
- S1-standalone "6 Discovery Candidates" (code/s1.py) — SUPERSEDED by the unified engine (family-favorable null + per-family FDR); not a candidate under mstrat.py.

## 10. METHODOLOGY UNDER VALIDATION
- All p-value methods (analytic / IID-bootstrap / block-bootstrap / matched-null) = METHOD UNDER VALIDATION.
- Discovery Screen V1 is FROZEN but DEVELOPMENT-TUNED (calibrated on S1-S10); S11-S20 are its first prospective test.

## 11. OFFICIAL ENGINE
- **`code/mstrat.py` = ENGINE v2** (common multi-strategy backtester with pre-registered stop-floor). All families run through `mstrat.simulate`. Primary statistic FROZEN = mean expectancy (R/trade), one-sided (H0: mean≤0).

## 12. DEPRECATED
- `code/s1.py` standalone prototype (different position-overlap-skip: skips next SETUP on signal_idx vs engine v2 next-ENTRY on entry_idx). Diagnostic only.
- Analytic normal-approx p-value **as a verdict** (proven tail-invalid). Diagnostic/ranking only.
- Engine v1 (pre-stop-floor) results — invalidated for comparison; v2 is authoritative.
- `code/mtf.py` MTF single-symbol campaign engine — foundation for S9-style logic; superseded by mstrat.py for the multi-strategy campaign (still imported by s1.py for feature loading).

## 13. BUGS / TECH DEBT DISCOVERED
- **R-normalization / tiny-stop explosion**: structure stops (prev_ext/beyond_sweep/structural) can sit ~0 from entry → R=pnl/risk explodes (S6: R up to +166; top-5 trades=71% profit). Partially mitigated by v2 stop-floor but S6 still maxDD≈85R. Full INVALID-EXECUTION marking NOT wired into engine (spec only: docs/MIN_STOP_FLOOR_PREREG.md).
- **Analytic-p tail invalidity** (proven: S6 analytic 2.1e-54 vs empirical ~0.12).
- **Matched-null miscalibrated** (gives ~0 on synthetic-null due to construction/scale mismatch; needs synthetic-PRICE-series validation).
- **S19 %-profitable display bug** in run_full_campaign.py (divides by valid=0 → 400%). Counts correct.
- Top-by-expectancy / top-by-profit-DD lists dominated by low-n flukes (S1 n=3-5, PF 99) — use monthly-stability + RESEARCH_WORTHY lists instead.
- Lab code+data were in ephemeral Temp scratchpad → now copied here (durable). GC MBO raw (data2) still only in Temp.

## 14. INCOMPLETE CHANGES
- Engine v2 stop-floor active in mstrat.simulate but INVALID-EXECUTION exclusion not implemented.
- Memory file `ai-quant-research-lab.md` last append failed (anchor moved) — this doc supersedes it as truth.

## 15. FIRST TASKS NEXT SESSION (see NEXT_SESSION.md)
1. Fix + validate matched-null (Test B) on synthetic PRICE series (≥100 nulls → uniform p; power curve).
2. Choose official p-value method BEFORE results; wire adaptive MC (MC-1/2/3) with CI + seeds.
3. Then run global-FDR over full eligible universe (m=1552 valid) + walk-forward + Red Team. Holdout stays SEALED.

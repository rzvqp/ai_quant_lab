# NEXT_SESSION — first actions (AI Quant Research Lab)

Read PROJECT_STATE_v1.0.md + SESSION_CLOSE_S1_S20.md + docs/ first. Holdout stays SEALED. No live trading.
Do NOT re-tune Discovery Screen V1. Do NOT re-run families to force a candidate count.

## PORTABILITY (required before running on a new machine)
The copied Python modules contain absolute paths to the original ephemeral Temp scratchpad. Repoint them to
THIS folder before running. Essential change (the canonical data-path constant used by mstrat.py/s1.py/mtf.py):
- `code/mtf.py` line 6: `D = r"...\scratchpad\phaseb\alpha\data_market"` → set to this folder's `data\market`.
Also repoint absolute Temp paths in (only if you run these data-build/foundation scripts): build_gc_bars.py,
quality_and_resample.py, resample_ny.py, run_cycle.py, run_prod.py. (Grep the code for `AppData.Local.Temp`.)
GC MBO raw data (`scratchpad/phaseb/data2`, ~1GB, foundation/closed track) was NOT copied — re-download from
Databento if the foundation reconstruction must be re-run; not needed for the XAUUSD alpha campaign.

## Environment setup (new machine)
1. `python -m venv venv && venv\Scripts\pip install -r requirements.txt`
2. Data already present in `data/market/` (XAUUSD M15/H1/H4/D1). If missing, rebuild:
   TradingView Desktop with CDP :9222 open on OANDA:XAUUSD, then run pullers/pull_replay_m15.mjs →
   pull_gapfill.mjs → code/resample_ny.py (and cross-check with pullers/pull_native.mjs).
3. Sanity: `venv\Scripts\python code/run_full_campaign.py` reproduces results/full.log
   (1972 hyps, 357 hist-profitable, 130 research-worthy).

## Task order (statistical remediation — must precede any strict verdict)
1. **Fix matched-null (Test B, PRIMARY alpha test).** Root cause of the pilot failure: synthetic control fed
   bare synthetic R's to a real-price null (scale mismatch). Fix = generate synthetic PRICE series with
   injected null/edge SIGNALS, run through mstrat.simulate. Validate: ≥100 independent null series →
   p-value distribution ~uniform, P(p<0.05)≈5%; 3-5 injected edge magnitudes → power curve + FPR + seed reproducibility.
2. **Choose ONE official p-value method BEFORE seeing which rejects current strategies** (per EMPIRICAL_PVALUE_SPEC.md).
   Candidates: matched-null (Test B, primary) + block-bootstrap (Test A, robustness secondary).
3. **Adaptive MC**: MC-1 triage B=20k → MC-2 B≥200k (CI) → MC-3 B≥1e6 (confirmation), p=(k+1)/(B+1), save seeds/counts.
   Status UNRESOLVED if p CI intersects the BH threshold.
4. **Wire INVALID-EXECUTION + finalize stop-floor** per docs/MIN_STOP_FLOOR_PREREG.md; re-run ALL S1-S20 uniformly if it changes execution.
5. **Global-FDR** over full eligible universe (m=1552 valid; m=1704 conservative diagnostic; invalids ineligible, NOT p=1).
6. Then walk-forward + Red Team on survivors. Only after all that, request CEO gate to open terminal HOLDOUT.
7. **Portfolio Architect**: proper factor-correlation (define horizon, common obs, CI, stability) → low-correlation shortlist.

## Do NOT
- Do not open the terminal holdout (CEO gate).
- Do not declare significance/FDR verdicts until the p-engine is validated.
- Do not re-assert retracted conclusions (see PROJECT_STATE §9).
- Do not tune stop-floor k or screen thresholds to improve results.

# REPRODUCIBILITY_AUDIT — 2026-07-13

Re-ran the official campaign (`code/run_full_campaign.py`, ENGINE v2) on the portable data path and
compared against the sealed baseline. Baseline was NOT overwritten; new run saved to
`results/reproduction_v2/`.

## Setup
- Command (run from an isolated dir so the baseline is never touched):
  ```
  cd results/reproduction_v2
  PYTHONPATH=<root>/code  <root>/venv/Scripts/python.exe  <root>/code/run_full_campaign.py > full.log 2>&1
  ```
- Engine: `code/mstrat.py` v2 (stop-floor). No randomness in the campaign (deterministic grammar via
  itertools + hashlib ids) → exact reproduction is expected if data + logic are identical.
- Runtime: Python 3.14.6, pandas 3.0.3, numpy 2.5.1, pyarrow 25.0.0 (all NEWER than the original venv).
- Compute time: **83 s** (baseline also 83 s).

## Float tolerance (defined BEFORE comparison)
- atol = 1e-9, rtol = 1e-9 for all numeric columns.
- inf–inf (profit factor with zero gross loss) and NaN–NaN treated as equal.

## Baseline headline (results/full.log) vs required baseline
| metric | required | baseline log | new run | match |
|---|---|---|---|---|
| generated | 1972 | 1972 | 1972 | ✅ |
| valid (n≥25) | 1800 | 1800 | 1800 | ✅ |
| historically profitable | 357 | 357 | 357 | ✅ |
| research worthy | 130 | 130 | 130 | ✅ |
| families ≥1 profitable | 14 | 14 | 14 | ✅ |
| families ≥1 research-worthy | 9 | 9 | 9 | ✅ |
- family lists (prof / noprof / rw) identical.

## Per-hypothesis comparison (FAMILY_RESULTS.parquet, 1972 rows × 22 cols)
- rows equal (1972), columns equal, **id order identical**, id set identical, outer-merge all "both".
- **All 16 numeric columns: max abs diff = 0.0, zero mismatches beyond tolerance.**
  (n, exp, pf, dd, win, sumR, val_exp, median, trim5, t1, t3, t5, wo1, months, pos_months, years)
- **All 3 boolean flags: 0 mismatches** (hist_prof, research_worthy, fragile).
- side (string): 0 mismatches.
- **Total trades: 1,300,740 == 1,300,740** (exact).
- warnings: 32 vs 32 (identical numpy divide-by-zero warnings); errors: 0 vs 0.
- Temp/System32/old-repo refs in new log: **0** (baseline log had 64, from the old venv paths in its
  numpy warnings — not a code dependency).

Full machine record: `results/reproduction_v2/comparison.json`.

## Bar-count note (does not affect reproduction)
Actual M15 = 84152 (docs said 84151 = wc off-by-one). Proven identical to baseline data: the exact
parquet match AND the split `research=50491 / val=16830 / holdout=16831` (sum 84152) with the
sealed-holdout 16831 matching the original session's documented 16831. The original run used 84152 too.

## VERDICT: **A — EXACT REPRODUCTION**
Same hypotheses, same order, same metrics to 0.0 abs diff, same trade ledgers (equal total trades),
same boolean verdicts, same headline. Bit-exact across a newer pandas/numpy stack. Holdout SEALED
throughout. No significance verdicts issued.

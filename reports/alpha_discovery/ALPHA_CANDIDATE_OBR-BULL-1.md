# ALPHA_CANDIDATE_OBR-BULL-1 — bullish order-block fresh first-retest (displacement-gated, LN+NY)

Status: **FALSIFIED AS A TRADEABLE STRATEGY** (2026-08-31, Statistician + OB_CAUSAL_EXECUTION_FACTORY_V1). The reported +0.154R was a
same-bar fill artifact: the resting BUY limit was cancelled when the same bar closed below the block, dropping same-bar filled-then-
invalidated LOSSES. **Corrected causal fill = −0.067R** (reproduced to the digit; regression test `test_ob_exec_fill.py`). Four causal
executions (true limit / retest-close / rejection-close / penetration-reclaim) all net-negative → SURVIVED=0. **Do NOT repair, retune, or
re-promote.** The OB *level* information is independently confirmed real (OB_INCREMENTAL_INFORMATION=YES) but
**NOT CURRENTLY MONETIZABLE** by any tested execution. See `OB_CAUSAL_EXECUTION_FACTORY_V1_REPORT.md`. The metrics below are the ARTIFACT
values, retained only for the historical record.

---
_Historical (falsified) record follows._

## Exact causal definition (M15, OANDA XAUUSD, UTC)
1. **Causal swing:** prior swing high `swH[i] = max(high[i-20:i])` (rolling, shift-1; no centered pivots).
2. **Bullish BOS at bar i:** `close[i] > swH[i]` AND `close[i-1] <= swH[i-1]` (fresh close-acceptance break).
3. **Origin order block:** the **last bearish candle** (`close<open`) in `[i-10, i-1]`. Block = `[low, high]` of that candle. Frozen at i.
4. **Displacement gate:** `disp = (close[i] - block_high) / ATR[i] >= 1.5`.
5. **Entry:** resting **limit BUY at `block_high`**, triggered on the **first** bar `k>i` with `low[k] <= block_high` (fresh first
   retest), provided no bar in `(i,k)` closed below `block_low` (else the block is invalidated → no trade).
6. **Session filter:** retest bar `k` in **London or NY** (08:00–20:00 UTC).
7. **Stop:** `block_low - 0.1*ATR[i]`, floored so risk ≥ 0.5·ATR (disclosed; see §16).
8. **Target:** **2R** (fixed). 1R and 3R also profitable (see robustness); 2R is the operating point.
9. **Optional M5 refinement (native 2021+ only):** tighten the stop to the M5 swing-low observed within the retest bar → VALUE_ADD.

## Performance (full history 2011-07 → 2026-07, price-cost $0.419/risk)
| metric | LONG (OBR-BULL-1) |
|---|---|
| N (raw trades) | 2,122 |
| independent episodes | 954 |
| net-R / trade | **+0.154** |
| win rate | 0.482 |
| profit factor | 1.86 |
| best-trade-removed net-R | +0.153 (not outlier-driven) |
| median MFE | 37 project pips |
| median risk (stop) | ~20 project pips |
| DEV (≤2018) / OOS (2019+) | +0.123 / +0.185 |
| era D / C / O | +0.123 / +0.166 / +0.206 |
| years positive | 13 / 16 (neg: 2014, 2018, 2019 — all mild) |

## Why it survived where 6 prior frontiers failed
- **Cross-era (escapes R20):** positive in the pre-2019 D era (+0.123), not just the 2023+ bull. 13/16 years positive.
- **Displacement dose-response (mechanism, not a tuned threshold):** net-R rises monotonically with displacement —
  1.0→+0.099, 1.25→+0.112, 1.5→+0.154, 1.75→+0.184, 2.0→+0.226, 2.5→+0.239. Stronger impulse from the origin block ⇒ better retest.
- **Beats matched controls (§26):** in-cell the OB level beats a generic displacement+BOS pullback (CONTROL_C) by +0.36 and a
  height-matched shifted non-OB level (CONTROL_SHIFT) by +0.21, and beta by +0.33 — cross-era.
- **Outlier-robust:** drop-best-1% +0.135, drop-best-5 +0.149.

## §27 anti-hindsight audit — ALL PASS
BLOCK_IDENTIFIED_BEFORE_RETEST=YES · BOS_KNOWN_BEFORE_RETEST=YES · BLOCK_COORDINATES_FROZEN=YES · TARGET_DEFINED_BEFORE_OUTCOME=YES ·
STOP_DEFINED_BEFORE_OUTCOME=YES · NO_CENTERED_PIVOT_LOOKAHEAD=YES · NO_FUTURE_H1H4_CANDLE=YES (M15-only cell) · FIRST_RETEST_CAUSAL=YES ·
ENTRY_CAUSAL=YES (resting limit at frozen level; no intrabar depth selection — the depth/reject "edge" was proven a limit-fill artifact
and is NOT used).

## Honest caveats (for independent review)
1. **Modest expectancy** (+0.154R). Real and stable, not spectacular.
2. **Cost sensitivity:** survives the canonical price-cost and flat-0.24R comfortably, but a harsh +0.15R extra stress brings it to
   ~break-even. Tight-stop M5 variant needs careful R-accounting.
3. **Control disentanglement:** OB beats CONTROL_SHIFT (height-matched) by +0.21, but a fully stop-matched control (isolating OB-level
   information from structural-stop-placement benefit) should be run by the Statistician.
4. **M5 value only measurable 2021+** (native M5); cannot be validated earlier (no synthesis).
5. **Bear mirror (OBR-BEAR-1) is weaker** — +0.127R but a 2017-2019 negative patch and less monotonic displacement; secondary.

## Reproduce
`ob_core.py` (detection/freeze/retest/outcome), `ob_candidate.py` (cells), `ob_falsify.py` (battery), `ob_contrast.py` (controls),
`ob_m5.py` (execution). Run `ob_falsify.py` for the exact numbers above.

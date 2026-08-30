# TEMPORAL_SEQUENCE_CONTRAST_REPORT_V1 — does PATH add information beyond final STATE?

TEMPORAL_SEQUENCE_MINING_V1 §8/§12 deliverable. Extends the Contrast Miner from static break-features to the **ordered trajectory**.
Question: among anchors with SIMILAR current state, does the preceding PATH shift the outcome? Measured as within-state-cell outcome-rate
spread (state-controlled), two framings: **up/down** absolute and **continue/reverse** relative to the path's own net direction.
`tsm_contrast.py`, `tsm_sweep.py`, `tsm_ordermotif.py`. STRESS cost 0.24R.

## 1. Baselines (RANGE_EDGE, N=38,200, 95.9% resolved)
`P(up-first) = 0.5080` · `P(continue) = 0.5056`. Near-coinflip, as five prior frontiers established for M15 direction.

## 2. Positive control — the test HAS power
A FUTURE-return "motif" (next-3-bar return sign) was run through the identical within-cell machinery. It shifts within-cell P(up) by
**+0.563** (RANGE_EDGE) / **+0.60** (VOL_TRANS), stable across DEV/OOS and all eras. **This proves the pipeline detects directional
information when it genuinely exists** — the causal negatives below are true negatives, not a powerless test.

## 3. Information test — causal path motifs (within-cell spread, state-controlled)
Every causal motif produces a within-cell outcome spread of magnitude **≤0.03**, and the sign **flips across DEV/OOS and across eras
D/C/O** — i.e. noise. Flagship ORDER features included:
- `energy_late` (early-vs-late energy composition): ALL −0.009, era signs −0.005/−0.015/−0.014 → no stable directional content.
- `argH`/`argL` (extreme-location-in-time): ALL ±0.01, DEV↔OOS sign flips.
- `eff`,`sc`,`pull`,`rc`,`net_r`: all |ALL|≤0.014, era-sign-unstable.

## 4. Scale invariance (§3 L-sweep) and anchor invariance (§7)
`tsm_sweep.py` applied a stability gate (|ALL|≥0.02 AND sign-consistent across DEV/OOS AND across D/C/O) to every causal motif × frame ×
L ∈ {8,16,32,64} × 2 anchors:
- **RANGE_EDGE: 0 causal survivors at every L** (positive control +0.56 throughout).
- **VOL_TRANS**: 4 flags, each at a **single L** (argH@L32; energy_late/argL/net_r@L64) — §17 treats single-length edges as falsified —
  on the smaller anchor only. Across 128 small-N era-split tests, ~4 sign-stable flags is consistent with multiple-comparison noise.

## 5. Monetization of every flag (§13, 2R:1R continuation, cost 0.24) — all FALSIFIED
| motif (VOL_TRANS) | L | N | net-R | D / C / O | DEV / OOS | best-rm | indep-ep net-R |
|---|---|---|---|---|---|---|---|
| argH_continue | 16/32/64 | ~2.4k | −0.26 / −0.28 / −0.31 | all neg | all neg | unch | ≈ raw |
| energy_late_continue | 32/64 | ~2.3k | −0.67 / −0.68 | all neg | all neg | unch | ≈ raw |
| argL_continue | 32/64 | ~2.3k | −1.13 / −1.07 | all neg | all neg | unch | ≈ raw |
| net_r_updown | 32/64 | ~2.3k | −0.24 / −0.22 | all neg | all neg | unch | ≈ raw |

Interpretable §6A motifs (clean-path / low-whipsaw / shallow-pullback continuation) on both anchors: net-R −0.68…−0.75 — **worse than
the driftless null (−0.24)**, because a directionally-clean approach selects already-spent moves (the Contrast-Miner "impressive break =
spent move" result, re-confirmed through the path). Driftless 2R:1R null net-R = −0.24; break-even P* = 0.413.

## 6. Pure ORDER test (§6B, 3-segment ordered-sign motif, L=32)
19 populated ordered classes. **P(up) ≈ 0.50 in every class**; 0 classes net-positive after cost; net-matched order reversals identical
(details in the atlas §5). The definitive statement that temporal ORDER carries no directional information.

## 7. Leakage / robustness checks (§18) — all clean
Lookahead: outcome strictly t+1..t+H. Normalization: ATR_t only (causal), no full-sample z-scores; the median/quantile split thresholds
are the only in-sample element and the net-R is deeply, uniformly negative regardless — no threshold could rescue it, and the chrono
DEV/OOS split confirms no temporal leak. No future-period clustering (interpretable buckets/ordered-sign, groups frozen before outcome).
Regime/HTF labels from causal EMAs and calendar, not retrospective peaks. Overlap addressed: independent-episode net-R ≈ raw net-R; best-
episode removal changes nothing. Effective independent episodes reported (RANGE_EDGE 8,756 / VOL_TRANS 4,485), not raw N.

## 8. Answer to the §23 question
**Does the path into an XAU setup contain materially useful directional information beyond the final state?** **NO.** P(up) is invariant
(~0.50) across all causal path motifs, all sequence lengths, both anchor families, and all 19 ordered trajectory classes; the only column
that separates outcome is future leakage (positive control +0.56). **Is it strong enough to monetize?** N/A — there is no causal
directional information to monetize; every monetized motif nets negative after cost, most worse than the driftless null.

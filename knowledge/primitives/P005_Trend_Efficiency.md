# P005 — Trend Efficiency (gated continuation)

## Claim
Continuation in efficient trends is weakly positive; raw continuation is negative. (SUPPORTED EXPLORATORILY, confidence low; NOT validated alpha.)

## Operational definition
Continuation entries only when the trend is CLEAN (high Kaufman efficiency ratio); skip choppy trends.

## Evidence FOR
S39 high-efficiency variant positive
Supporting families: S39 (er_thr=0.5, OOS +.02)

## Evidence AGAINST
effect ~.02R, only 2 RW, variant-dependent
Contradicting families: S15/S38 (raw continuation, negative)

## Proposed economic mechanism
Clean trends persist; efficiency filters noise.

## Context where it APPEARS
regimes trend, sessions all, direction both

## Context where it DISAPPEARS / reducibility
S15/S38 (raw continuation, negative); OOS weak-positive. Reducible to gold beta not yet ruled out.

## Status
SUPPORTED EXPLORATORILY (confidence low)

## Limitations
tiny effect; threshold-selected; 4-yr bull sample; family-wise selection not corrected; costs not stress-tested.

## Next test
efficiency-gate ablation in matched null

## Sources
results/FAMILY_RESULTS.parquet, results/ext_families/*.parquet, docs/S21_S40_IMPLEMENTATION_REPORTS.md, docs/S21_S31_TIERB_CONSOLIDATED.md, docs/MECHANISM_DIVERSITY_LOG.md, MECHANISM_REGISTRY.parquet, kb_dedup.json

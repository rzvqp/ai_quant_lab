# P001 — Confirmed Liquidity Sweep Reversal

## Claim
Sweep of a level + confirmation is followed by mean-reversion away from the swept side. (SUPPORTED EXPLORATORILY, confidence medium; NOT validated alpha.)

## Operational definition
After price sweeps a resting-liquidity level (prior-day/swing/session high/low) it must show a CONFIRMATION (displacement / close-back / consecutive-close) before a reversal entry.

## Evidence FOR
S1 confirmed variants: several RW, positive OOS on two representatives
Supporting families: S1 (low/swing OOS +0.29; high/pdh short OOS +0.35; multiple RW)

## Evidence AGAINST
S1 low/pdh OOS ~+0.01 (near null); large spec dispersion
Contradicting families: S21 (raw sweep, no confirmation, all negative)

## Proposed economic mechanism
Stop/breakout orders pooled beyond levels are triggered to fill size; confirmation filters the genuine reversal from the continuation.

## Context where it APPEARS
regimes 2022-25 bull (untested bear), sessions all, direction both

## Context where it DISAPPEARS / reducibility
S21 (raw sweep, no confirmation, all negative); OOS mixed-positive. Reducible to gold beta not yet ruled out.

## Status
SUPPORTED EXPLORATORILY (confidence medium)

## Limitations
spec-dispersion; some low OOS; 4-yr bull sample; family-wise selection not corrected; costs not stress-tested.

## Next test
confirmed vs unconfirmed sweep in a frozen side/regime-matched null

## Sources
results/FAMILY_RESULTS.parquet, results/ext_families/*.parquet, docs/S21_S40_IMPLEMENTATION_REPORTS.md, docs/S21_S31_TIERB_CONSOLIDATED.md, docs/MECHANISM_DIVERSITY_LOG.md, MECHANISM_REGISTRY.parquet, kb_dedup.json

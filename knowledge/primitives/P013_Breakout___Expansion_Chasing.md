# P013 — Breakout / Expansion Chasing (incl. volatility compression)

## Claim
Breakout chasing loses even with HTF/volume/duration gates. (REPEATEDLY NEGATIVE, confidence high; NOT validated alpha.)

## Operational definition
Enter on a breakout/expansion of a range (with HTF filter, volume gate, squeeze, or duration).

## Evidence FOR
none
Supporting families: none (round-number breakout is a distinct level mechanism, P004)

## Evidence AGAINST
S23 (HTF) -0.09; S46 (volume) OOS -.02; S48 (duration) -0.13
Contradicting families: S3, S4, S23, S46, S48 negative

## Proposed economic mechanism
Fakeout rate + chasing the move + wide stops dominate.

## Context where it APPEARS
regimes bull, sessions all, direction both

## Context where it DISAPPEARS / reducibility
S3, S4, S23, S46, S48 negative; OOS negative. Reducible to gold beta not yet ruled out.

## Status
REPEATEDLY NEGATIVE (confidence high)

## Limitations
-; 4-yr bull sample; family-wise selection not corrected; costs not stress-tested.

## Next test
none (closed); volume is NOT the missing ingredient (S46)

## Sources
results/FAMILY_RESULTS.parquet, results/ext_families/*.parquet, docs/S21_S40_IMPLEMENTATION_REPORTS.md, docs/S21_S31_TIERB_CONSOLIDATED.md, docs/MECHANISM_DIVERSITY_LOG.md, MECHANISM_REGISTRY.parquet, kb_dedup.json

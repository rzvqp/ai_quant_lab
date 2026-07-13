# P002 — Failed-Breakout Fade

## Claim
Failed break at prior-day level reverts. (SUPPORTED EXPLORATORILY, confidence medium; NOT validated alpha.)

## Operational definition
A breakout beyond a prior-day level that fails (closes back inside) is faded back into range.

## Evidence FOR
S2 low/pdh: OOS +0.26, RW
Supporting families: S2 (low/pdh OOS +0.26)

## Evidence AGAINST
high maxDD ~24R; limited independent replication
Contradicting families: S12 range-rotation (generic, negative)

## Proposed economic mechanism
Breakout buyers trapped on the failed extension are forced to unwind, feeding the fade.

## Context where it APPEARS
regimes bull, sessions all, direction long (tested)

## Context where it DISAPPEARS / reducibility
S12 range-rotation (generic, negative); OOS positive. Reducible to gold beta not yet ruled out.

## Status
SUPPORTED EXPLORATORILY (confidence medium)

## Limitations
dd high; one family; 4-yr bull sample; family-wise selection not corrected; costs not stress-tested.

## Next test
matched null; test short-side symmetry

## Sources
results/FAMILY_RESULTS.parquet, results/ext_families/*.parquet, docs/S21_S40_IMPLEMENTATION_REPORTS.md, docs/S21_S31_TIERB_CONSOLIDATED.md, docs/MECHANISM_DIVERSITY_LOG.md, MECHANISM_REGISTRY.parquet, kb_dedup.json

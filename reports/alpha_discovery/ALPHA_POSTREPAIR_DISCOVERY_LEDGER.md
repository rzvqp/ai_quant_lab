# Post-Repair Discovery Ledger (verified causal infra, VE 91b7415)

Only causally-revalidated evidence. S5 = only validated edge; current-regime survivor 0; multi-regime 0. No tainted CRS-1 evidence.
Information-first per CEO §4. Each frontier: preregister -> info -> tradeable-if-justified -> gate -> record -> next.

## Frontier A — volume DRY-UP -> expansion (vol_dryup.py) : INFO-POSITIVE (magnitude), NON-DIRECTIONAL -> no tradeable edge
Dry-up (tick-vol < 0.6x trailing for 6 bars) robustly precedes forward EXPANSION: fwdRange 16.3 ATR vs 11.1 baseline (+47%),
holds all eras. But direction is ERA-SPLIT (up-dn DISC -0.13 / CONF +1.46 / OOS +2.40) = R26 (predictable VOL, unpredictable
DIRECTION) confirmed via the volume lens. Direction-agnostic form already closed (CR-11 breakouts whipsaw). Genuine info, no edge.

## Frontier B — HAZARD/time-since-new-high (hazard.py) : effect exists but ERA-ENTANGLED -> no clean edge
Continuation decays with age (fresh 0-4 up-dn +0.27 -> mature 25-96 -0.23) but direction is era-split at EVERY age
(DISC neg / CONF+OOS pos). Age modulates strength within an era's trend, does not create era-independent direction (R20).
Info-finding only, not tradeable.

## Frontier C — event sequence compression->failed-break->response (event_seq.py) : no tradeable edge
dn-fail->UP has positive info asym across partitions (+0.25/+1.27/+0.87) but tradeable long fails (avgR -0.143, DISC -0.191:
excursion doesn't survive cost/entry). up-fail->DOWN era-split (D +0.63/C -2.03). Momentum-dominance + era-split. No edge.

## Frontier D — auction/reference-level acceptance (auction.py) : no edge
Accepted-above-PDH does NOT continue up (up-dn -0.15, reverts; era-split D -0.28/O +0.29). Tradeable acc-above LONG -0.048
(DISC -0.067), acc-below SHORT -0.089 both fail. Value-migration continuation is not a tradeable edge; extensions revert (era-split).

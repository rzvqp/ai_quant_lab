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

## Frontier E — session inheritance (session_inherit.py) : no edge
P(next-session dir == prior-session dir) = 0.484 (~coinflip, tiny reversion lean, consistent D 0.481/C 0.489/O 0.494).
No directional session inheritance. Consistent with Batch J (Asia doesn't lead NY). No edge.

## Frontier F — cross-scale range-position (xscale_rangepos.py) : momentum not reversion, era-split, no edge
M15 position in last-closed H4 range: bottom continues DOWN (up-dn -0.17), top continues UP (+0.26) = momentum, era-split.
Mean-reversion fade fails (bottom-LONG -0.110, top-SHORT -0.119). No edge. (Genuinely-new causal cross-scale, NOT CRS-1.)

## Frontier G — multi-TF momentum confluence (multi_tf.py) : era-split, no edge
H4&H1&M15 all-up forward up-dn +0.47 but era-split (D +0.18/C +0.81/O +1.56). Tradeable ALL-UP LONG -0.073 (DISC -0.104),
ALL-DOWN SHORT -0.089 both fail. Directional confluence = era-trend, not tradeable.

## Frontier H — calendar seasonality (seasonality.py, hr_long.py) : no edge
Info: many UTC hours cross-era-positive forward return = gold's secular up-drift (not hour-specific). hr21 spiked (+1.03) but
under a proper ATR-bracket it's DISC-negative (-0.019), tail-dependent (best10rm -0.176), ISOLATED (neighbors hr20 -0.045,
hr22 -0.175 fail) = noise/ATR artifact, not a coherent effect. All-hours bracketed LONG = sub-cost (fails). No seasonality edge.

## POST-REPAIR MECHANISM-SPACE COVERAGE — EXHAUSTIVE, S5-only (causally verified)
11 post-repair frontiers this program (gap, vol-breakout, vol-climax, vol-dry-up, hazard/time-in-state, event-sequence,
auction/reference, session-inheritance, cross-scale range-position, multi-TF confluence, seasonality) — ALL no tradeable edge.
Combined with the full prior campaign (universal A-J + current-regime CR-1..15 causal-replayed + 6-regime multi-regime taxonomy),
this exhaustively covers the PRICE+VOLUME mechanism repertoire: trend/momentum-continuation (era-split), mean-reversion/fade
(fails), breakout (only S5=NY opening-range works), volatility/compression/dry-up (predictable magnitude but NON-directional,
R26), volume (informs/ranks but never standalone), structural events sweep/acceptance/retest/failed-break (fail/era-split),
cross-scale divergence/confluence/range-position (fail/era-split; CRS-1 was a lookahead artifact), reference-level/auction (fail),
session inheritance/lead-lag (no edge), hazard/time-in-state (era-entangled), seasonality (drift/artifact). ROOT: R20 (direction
= era-trend, non-generalizing) + R26 (volatility predictable, direction not). **S5 (structural direction-supplying opening-range
breakout in a liquid window) remains the SINGULAR tradeable XAUUSD price+volume edge.** Genuinely-distinct next frontiers need
either new authorized data (finer M5 / exogenous — governance gate) or a genuinely-novel mechanism concept beyond this repertoire.

## Frontier I — autocorrelation-adaptive meta-strategy (autocorr_adaptive.py) : no edge
The market's own rolling lag-1 return autocorrelation does NOT predict whether momentum or reversion works next: adaptive
sided-fwdRet negative all partitions (-0.015/-0.055/-0.044); tradeable combined -0.104, every partition negative. Even the
meta-level (regime-switch by persistence character) fails. 12th post-repair frontier, no edge.

## DOMAIN-EXHAUSTION CONCLUSION (price+volume, single-instrument, causally verified)
The authorized XAUUSD price+volume single-instrument mechanism space is now EXHAUSTIVELY covered — standard TA/microstructure
repertoire (trend/reversion/breakout/volatility/volume/structure/cross-scale/reference-level/session/hazard/seasonality) PLUS a
meta-representation (autocorrelation-adaptive) PLUS the full prior campaign (universal A-J, current-regime CR-1..15 causal-replayed,
6-regime multi-regime, RANGE vNext lifecycle, unsupervised morphology). S5 (structural direction-supplying NY opening-range
breakout) is the SINGULAR tradeable edge. Deep causes: R20 (direction = era-trend, non-generalizing) + R26 (volatility predictable,
direction not). Genuinely-distinct further frontiers require NEW AUTHORIZED DATA (finer M5 / exogenous DXY-yields-news — CEO
governance gate) or a genuinely-novel mechanism concept beyond the standard+meta repertoire. Not a stop for 'negative/comprehensive';
a hypothesis-space boundary of the authorized domain.

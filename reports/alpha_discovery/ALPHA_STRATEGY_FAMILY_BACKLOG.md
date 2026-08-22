# ALPHA_STRATEGY_FAMILY_BACKLOG (S1-S20 status)

Status: RETEST_ELIGIBLE / REQUIRES_NEW_MECHANISM / FROZEN_REFERENCE / IN_PROGRESS. Do NOT run S1->S20 in order; Radar + evidence pick next.

| S | family | status | note |
|---|---|---|---|
| S1 | Liquidity Sweep (reversal+continuation) | BOUNDED_NEGATIVE | BOTH branches net-neg all 6 modes cross-era (#42/#43); displacement informative (R1) but not net-positive after cost; no robust specialist |
| S2 | Failed Breakout / Failed Sweep | RECOMMENDED_NEXT | R6: displacement/breakout FAILURE is a ~3x discriminator -> trade the failure/reversal side (distinct from bounded continuation families) |
| S3 | Breakout Retest Continuation | RETEST_ELIGIBLE | |
| S4 | Volatility Compression Expansion | ALT_NEXT | vol-expansion cross-era-stable; conditioned on directional mode + HOLD filter may exceed breakeven (breakout target > continuation retest) |
| S5 | Opening Range Breakout | RETEST_ELIGIBLE | session-open burst seen (M15 NY-open bilateral) |
| S6 | Session Transition | RETEST_ELIGIBLE | |
| S7 | Trend Pullback | RETEST_ELIGIBLE | COMP-CONT-L (frozen) is a pullback/continuation edge; correction modes relevant |
| S8 | Mean Reversion | RETEST_ELIGIBLE | |
| S9 | Multi-Timeframe Alignment | RETEST_ELIGIBLE | H4-M15 path-shape bounded (regime-conditional) |
| S10 | Displacement Continuation | BOUNDED_NEGATIVE | displacement carries cross-era-CONSISTENT positive INFO (#44) + HOLD~3x discriminator (#45/R6) but no tradeable entry converts net-positive (#47); pullback-fill candidate FALSIFIED as sim artifact |
| S11 | Structure Break Reversal | RETEST_ELIGIBLE | |
| S12 | Range Rotation | RETEST_ELIGIBLE | NEUTRAL_ROTATION mode available |
| S13 | Liquidity Void / Imbalance Fill | RETEST_ELIGIBLE | |
| S14 | Momentum Exhaustion | RETEST_ELIGIBLE | |
| S15 | Trend Acceleration | RETEST_ELIGIBLE | |
| S16 | Previous Day Levels | RETEST_ELIGIBLE | |
| S17 | Weekly Levels | RETEST_ELIGIBLE | |
| S18 | Time-of-Day Edge | RETEST_ELIGIBLE | session findings exist |
| S19 | Gap / Weekend / Session Gap | REQUIRES_NEW_MECHANISM | synthesized D1 has no overnight gaps (prior finding) |
| S20 | Hybrid Families | RETEST_ELIGIBLE | |
| - | S5(strat)/COMP-CONT-L-rr2/H4-bo-raw-S | FROZEN_REFERENCE | do not modify |

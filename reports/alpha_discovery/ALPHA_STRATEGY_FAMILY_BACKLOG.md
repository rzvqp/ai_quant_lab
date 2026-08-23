# ALPHA_STRATEGY_FAMILY_BACKLOG (S1-S20 status)

Status: RETEST_ELIGIBLE / REQUIRES_NEW_MECHANISM / FROZEN_REFERENCE / IN_PROGRESS. Do NOT run S1->S20 in order; Radar + evidence pick next.

| S | family | status | note |
|---|---|---|---|
| S1 | Liquidity Sweep (reversal+continuation) | BOUNDED_NEGATIVE | BOTH branches net-neg all 6 modes cross-era (#42/#43); displacement informative (R1) but not net-positive after cost; no robust specialist |
| S2 | Failed Breakout / Failed Sweep | BOUNDED_NEGATIVE | failed-break failure carries weak/rare reversal info; only signal is opposite displacement (R8=R1/R6, S10-redundant); wick branch S1_EQUIVALENT; tradeability thin/not cross-era (#48/#49); 0 survivors |
| S3 | Breakout Retest Continuation | RETEST_ELIGIBLE | |
| S4 | Volatility Compression Expansion | BOUNDED_NEGATIVE | no stable directional alpha (primary cells sign-reverse); payoff rationale falsified (MFE~=MAE); correction-resume cells are ~70% ASIA-session ARTIFACT (#50-#52); 0 survivors |
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
| S18 | Time-of-Day Edge | RECOMMENDED_NEXT | R11: Asia-session compression is where S4's apparent edge lived -> session structure may be the real driver; prior NY-open/London/Asia findings; genuinely different info class |
| S19 | Gap / Weekend / Session Gap | REQUIRES_NEW_MECHANISM | synthesized D1 has no overnight gaps (prior finding) |
| S20 | Hybrid Families | RETEST_ELIGIBLE | |
| - | S5(strat)/COMP-CONT-L-rr2/H4-bo-raw-S | FROZEN_REFERENCE | do not modify |

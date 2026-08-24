# ALPHA_BROAD_SCREEN_RESULTS — BATCH E (multi-day/day-level) + BATCH F (state/sequence)

Novel-mechanism discovery (CEO 2026-08-23: move from known-family search to novel mechanisms; economic-event novelty). Engine `bscreen.py`, STRESS 0.24, eras b0/b1/DEV/CAL. Ledger (§36): 16 hyps, all counted.

## Batch E — multi-day / day-level (causal, prev completed days; decision once/day at NY open; §24-safe, no D1 features)
| hypothesis | axis | side | poolN | poolR | best1 | verdict |
|---|---|---|---|---|---|---|
| MULTIDAY_MOM_L/S | level-migration | L/S | 657/586 | −0.081 / −0.103 | − | NEG_STRESS |
| INSIDE_DAY_BREAK_L | multiday-structure | L | 951 | +0.040 | +0.019 | SIGN_REVERSAL (b1+ DEV/CAL−) |
| INSIDE_DAY_BREAK_S | multiday-structure | S | 857 | −0.075 | − | NEG_STRESS |
| VOLMEM_CONT_L/S | volatility-memory | L/S | 149/143 | +0.006 / −0.001 | − | IMMATERIAL/NEG (tiny N) |
| MULTIDAY_REVERT_L/S | daily-overreaction | L/S | 468/542 | −0.165 / −0.151 | − | NEG_STRESS |
| OPENDRIVE_CONT_L/S | trend-day-persistence | L/S | 268/202 | −0.009 / +0.025 | − | NEG/IMMATERIAL |

**Batch E = 0 survivors.** Multi-day momentum, inside-day breakout, vol-memory, daily overreaction reversion, trend-day persistence all modern-negative/immaterial. Daily-scale reversion loses like intraday MR; inside-day breakout sign-reverses.

## Batch F — state/sequence (delayed/failed-follow-through/exhaustion; causal, decision after the observation window)
| hypothesis | axis | side | poolN | poolR | best1 | verdict |
|---|---|---|---|---|---|---|
| FAILED_FT_S/L | failed-follow-through (delayed) | S/L | 2045/1848 | −0.175 / −0.351 | − | NEG_STRESS |
| ACCEL_EXH_S/L | acceleration-exhaustion (climax fade) | S/L | 748/831 | **−2.788 / −1.850** | − | NEG (CATASTROPHIC) |
| DELAYED_RETEST_L/S | delayed breakout-retest | L/S | 4308/4074 | −0.226 / −0.274 | − | NEG_STRESS |

**Batch F = 0 survivors.** Delayed failed-break fade loses (stalled breakouts resume more than reverse); delayed-retest loses after cost; **ACCEL_EXH catastrophic −2.8R** = fading acceleration/climax gets destroyed.

## Findings (R19)
- **Momentum-dominance reconfirmed at maximum strength.** Every counter-momentum/fade mechanism (streak-fade Batch B −2.6, ACCEL_EXH Batch F −2.8, MR Batch A −0.74, daily-revert Batch E −0.16) is negative-to-catastrophic. XAUUSD punishes counter-trend entries severely across all eras.
- **Continuation is sub-cost except S5.** Multi-day momentum, delayed-retest, inside-day breakout all near-breakeven-to-negative; only S5's NY session-open structure clears cost.
- Novel economic LEVELS (multi-day, day-level) and novel STATES (delayed, sequence, exhaustion) tested — none robust. Within all mechanisms tested so far (Batches A-F, ~65 hyps), S5 remains the sole robust independent price-only edge reproduced (scoped, not universal).

## Next
Per CEO ("when ideas run thin, OBSERVE → CLUSTER → HYPOTHESIZE → PREDECLARE → TEST; causal variables, not P&L-mined"): Batch G = an INFORMATION-FIRST forward-path scan over a panel of novel CAUSAL state variables (measure P(+70/−50) L/S asymmetry cross-era, NOT P&L) to surface any state with stable material directional asymmetry not already = S5.

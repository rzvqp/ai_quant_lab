# ALPHA_FAILURE_MODE_MAP

Cumulative class-level negatives under **modern governance** (ratified STRESS cost 0.24 + multi-era b0/b1/DEV/CAL + cross-era sign-consistency + tail/session checks). Purpose (§40): record class-level conclusions so research budget is not spent re-proving the same failure. "Modern-falsified" = negative or era-inconsistent under this bar; distinct from the old single-regime/cost-naive corpus.

| info class | mechanisms tested | modern verdict | evidence | note |
|---|---|---|---|---|
| REVERSAL (liquidity sweep, structure-break) | S1 sweep reversal+continuation | BOUNDED_NEGATIVE | mode-family #42/#43 | displacement info real (R1) but not net-positive |
| FAILED-BREAK / FADE | S2, PDH/PDL fade (A7/A8) | BOUNDED_NEGATIVE | #48/#49, Batch A A7/A8 | only signal = opposite displacement (R8=R10) |
| VOLATILITY compression→expansion | S4 | BOUNDED_NEGATIVE | #50-52 | payoff falsified (MFE≈MAE); correction cells = Asia artifact (R11) |
| DISPLACEMENT continuation | S10 | BOUNDED_NEGATIVE | #44-47 | HOLD/FAIL discriminator real (R6) but no tradeable net-positive entry |
| REFERENCE-LEVEL break (prev-day) | PDH_break_L/PDL_break_S (A5/A6) | MODERN_FALSIFIED | Batch A: −0.22 both, cross-era | breakout continuation at PDH/PDL loses after cost |
| REFERENCE-LEVEL break (weekly) | PWH/PWL break = CAND-0037 (A9/A10) | MODERN_FALSIFIED | Batch A: −0.16/−0.33, neg b0/b1/DEV | existing "first robust candidate" fails multi-era + STRESS |
| REFERENCE-LEVEL reaction/fade | PDH_fade_S/PDL_fade_L (A7/A8) | MODERN_FALSIFIED | Batch A: −0.17/−0.15 | mean-revert at prior-day level negative |
| MEAN-REVERSION (extension 2σ) | MR_ext L/S (A11/A12) | MODERN_FALSIFIED (worst class) | Batch A: −0.74 both, all eras | naive stretch-reversion catastrophic (stops hit) |
| TREND-PULLBACK (EMA) | PB_trend_L (A13) | MODERN_FALSIFIED | Batch A: −0.78, all eras | naive EMA20 pullback-resume loses |
| SESSION-TIME (fixed hour) | TOD_NYopen_L (A14), S18 dir | MODERN_FALSIFIED | Batch A −0.65; R12 | session=vol-timing not directional; clock ≠ edge |
| SESSION opening-range (non-NY / short) | ORB_LON L/S, ORB_NY_S (A2-A4) | MODERN_FALSIFIED | Batch A | ORB edge is NY+long-specific (=S5) |

## Batch B/C additions (untested classes + timeframe study)
| info class | mechanisms | modern verdict | evidence |
|---|---|---|---|
| STRUCTURE-BREAK (BOS/Donchian) | SB_break M15/H1/H4 | MODERN_NEGATIVE (near-breakeven L, era-inconsistent) | Batch B −0.015; Batch C H1 +0.021 breakeven (DISC−, 2024-only), H4 sign-reversal |
| RANGE-ROTATION | RANGE_fade L/S | MODERN_NEGATIVE (Asia-concentrated) | Batch B −0.26/−0.34, ~52% Asia |
| MOMENTUM / HOLD-DISPLACEMENT (R6) | HOLDdisp L/S | MODERN_NEGATIVE | Batch B −0.22/−0.33 (info≠expectancy, =S10) |
| MULTI-TIMEFRAME alignment | MTF_align_L | MODERN_NEGATIVE (near-breakeven) | Batch B −0.026 |
| EXHAUSTION (streak fade) | STREAKfade L/S | MODERN_NEGATIVE (CATASTROPHIC −2.6R) | Batch B; counter-momentum destroyed (R4) |
| VOLATILITY-ONSET | VOLonset L/S | MODERN_NEGATIVE (NY-session artifact) | Batch B −0.03/−0.07; Batch C H1 +0.051 = 72% NY artifact |
| TREND-CONTINUATION (trend-filtered breakout) | TREND_break L/S H1/H4 | MODERN_NEGATIVE (ERA-TREND LEAKAGE) | Batch C: short-cont +0.111 but b0-bear-dominated, CONF≈0, 2024 neg |
| NARROW-RANGE breakout | NR_break L/S | MODERN_NEGATIVE | Batch B −0.22/−0.26 |

**Dominant failure mode for directional continuation = ERA-TREND LEAKAGE:** a directional breakout/continuation "works" in the era whose trend matches its side (short-cont in the 2011-13 bear, long-cont in the 2023-24 bull), then flips → SIGN_REVERSAL / CONF≈0 across the full multi-era set. Only S5's session-open STRUCTURE escapes this (regime-agnostic, all 4 eras +).

## SURVIVING price-only edges (modern bar)
- **S5 (NY opening-range breakout, LONG, rr3)** — validated A-H; now also cross-era-positive 2011-2018 (Batch A). FROZEN.
- **COMP-CONT-L-rr2** — FROZEN pending validation.
- (H4-bo-raw-S — reference/overlap only, not alpha.)

## Meta-conclusion (running)
Across the S1-S51 corpus + Batch A cross-class screen, XAUUSD price-only edge that survives ratified-cost multi-era screening is **narrow and concentrated in session-open momentum STRUCTURE (opening-range breakout), directionally asymmetric (long/NY)**. Reversal, level-interaction, mean-reversion, trend-pullback, volatility-regime, and session-time classes are all bounded/modern-negative. Open untested classes → Batch B: structure-break (BOS/CHoCH), range-rotation, momentum/HOLD-displacement (R6), MTF-alignment, acceleration/exhaustion, volatility-onset.

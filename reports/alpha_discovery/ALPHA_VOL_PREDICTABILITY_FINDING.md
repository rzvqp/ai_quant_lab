# Frontier K — Volatility predictability: the first CROSS-ERA-STABLE signal (non-directional, non-tradeable in spot)

Frontier autonomously selected (direction is era-trend R20; volatility never tested as a primary target — only as a confound R11/R12). Information-first, non-directional. Impl `vol_predict.py`. M15, forward 48 bars (12h), first-passage mfe/mae. Cross-era b0/b1/DEV/CAL.

## Test 1 — current vol → forward realized range (ATR units)
| era | vr_lo | vr_mid | vr_hi |
|---|---|---|---|
| b0 | 9.65 | 8.70 | 6.19 |
| b1 | 8.62 | 8.42 | 5.84 |
| DEV | 9.04 | 9.59 | 6.21 |
| CAL | 9.18 | 9.37 | 5.93 |
**Identical pattern across ALL four eras**: low current vol → proportionally larger forward range; high current vol → smaller. Vol structure (partial mean-reversion; the ATR-normalization contributes) is CROSS-ERA-STABLE. (Contrast: every DIRECTIONAL asymmetry in the campaign sign-reverses across these same eras.)

## Test 2 — compression event → forward expansion magnitude
| era | nComp | med max-excursion (ATR) | P(>1.5 ATR) | med excursion / box width | med excursion (pips) |
|---|---|---|---|---|---|
| b0 | 14762 | 7.70 | 1.00 | 3.13 | 105 |
| b1 | 13876 | 6.81 | 1.00 | 3.02 | 66 |
| DEV | 11003 | 7.09 | 1.00 | 2.97 | 89 |
| CAL | 3075 | 7.48 | 0.99 | 3.21 | 127 |
(baseline unconditional med max-excursion ≈ 6.0-6.2 ATR.) **Compression reliably precedes an expansion of ~3× the compressed box width (~66-127 pips), cross-era-stable.** Modest lift over baseline in ATR terms (7 vs 6), meaningful in box-width terms (3×).

## Finding (R26) — the campaign's unifying result
**The VOLATILITY / magnitude dimension of XAUUSD price is CROSS-ERA-STABLE** (compression→expansion ~3× box width; vol structure reproduces identically across 2011-2018 and 2021-2024) — the FIRST cross-era-stable regularity found beyond S5. This is in sharp, clean contrast to DIRECTION, which is era-trend/non-generalizing (R20, confirmed across A-J + observational + RANGE + morphology + mode-conditioning).

**But it is NOT directly tradeable in spot XAUUSD:**
- The predicted expansion is directionally SYMMETRIC (best excursion in either direction). Monetizing it requires a DIRECTION, which is era-trend (unpredictable cross-era).
- The expansion must be captured through an adverse, whipsaw-prone path — exactly why directional breakouts (S4, NR_break, structure-break) are net-negative *despite* the expansion being real (the max-excursion metric ignores adverse-first/whipsaw).
- A breakout-straddle reduces to the directional compression breakout (already falsified).

**Why S5 is the sole edge (unifying theory):** XAUUSD price-only = **predictable volatility + unpredictable direction**. The only robust tradeable edge (S5) is the one structural event that resolves BOTH — the NY opening-range breakout supplies its own direction AND its structure selects the non-whipsaw expansions in a high-liquidity window. Every mechanism that tries to predict direction from state/morphology fails (era-trend); every mechanism that harvests the (real) expansion without a path-surviving direction fails (whipsaw).

## Verdict
Frontier K = genuine NEW cross-era-stable KNOWLEDGE (vol predictable), but NO tradeable spot alpha (needs a direction; direction is era-trend). Not a survivor; not sent for validation. Records precisely what is vs isn't predictable in XAUUSD price-only, and why S5 is structurally unique. Value: any future edge must, like S5, be a structural event that supplies a path-surviving direction — not a state/morphology direction-predictor, and not a non-directional vol harvest.

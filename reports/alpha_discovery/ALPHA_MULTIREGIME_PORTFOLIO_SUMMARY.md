# Multi-Regime Specialist Portfolio — Summary (regimes #1-#6, single-axis causal taxonomy COVERED)

Mandate: MULTI-REGIME SPECIALIST PORTFOLIO (CEO 2026-08-23). Causal H4 taxonomy = TREND{up/down/range} x VOL{low/mid/high},
each regime FROZEN before P&L with causal trailing normalization (no global percentile). Files `*_regime.py`, `*_LEDGER.md`.

| # | regime (frozen) | pop% | result | reason |
|---|---|---|---|---|
| 1 | RANGE_REGIME_V1 | 31.6% | no survivor (RS-2 near-miss) | mean-reversion fade fails (boundaries break); cross-scale breakout too sparse/CONF-neg |
| 2 | HIGHVOL_BULL_V1 | 6.6% | no survivor | direction ERA-AMBIGUOUS (pre-2021 blowoff reverts, post-2022 continues); D1 doesn't separate |
| 3 | LOWVOL_BULL_V1 | 8.2% | no survivor | era-CONSISTENT +drift but SUB-COST (~0.2 ATR/24h, un-bracketable) |
| 4 | MIDVOL_BEAR_V1 | 9.0% | no survivor | ERA-SPLIT (CONF 22-24 bull reverts the dips) |
| 5 | MIDVOL_BULL_V1 | 11.0% | no survivor | era-consistent +drift but SUB-COST |
| 6 | LOWVOL_BEAR_V1 | 5.9% | NEAR-MISS | era-consistent down-bias + regime-specific BUT tail-dependent (best-5%rm neg) + per-year/neighbor fragile |
| - | HIGHVOL_BEAR | ~6% | COVERED by CRS-1 | (cross-scale divergence fade, in validation) |

## Meta-conclusion (robust across 6 regimes)
Regime-gating ALONE does not yield era-consistent tradeable directional specialists in XAUUSD: within-regime forward direction
is dominated by the era's secular trend (R20) -> flips sign in whichever partition contradicts it; low-vol regimes have
era-consistent but SUB-COST drift; the one era-consistent tradeable direction (LOWVOL_BEAR wide-short) is tail-dependent/fragile.
The only robust tradeable specialists (S5 breakout, CRS-1 high-vol-correction cross-scale divergence) come from STRUCTURAL /
CROSS-SCALE mechanisms that SUPPLY their own direction, not from regime-conditioned bias. Router state: S5 (trend/breakout),
CRS-1 (high-vol correction), NO_TRADE in the other 5 regimes. 2 near-misses (RS-2, LOWVOL_BEAR) both tail-dependent.
Next: test whether a DIFFERENT cross-scale EVENT (acceptance/retest, per mandate §5 — not the CRS-1 bounce-fade) converts a near-miss.

## Continued discovery — acceptance-event (§5) extension
- LOWVOL_BEAR x M15 acceptance short: tail-dependence REMOVED (best-5%rm +0.033), DISC/CONF+, regime-specific — but OOS n=17 negative (regime rare 2025-26). Strongest near-miss.
- BROAD BEAR (any-vol) x acceptance short: OOS+ (+0.151) but CONF -0.134 (mid/high-vol bear reverts in bull era) + tail-dependent. Fail.
=> The §5 acceptance/retest lesson genuinely reduces tail-dependence (validated), but the clean-direction subset (low-vol bear) is OOS-thin and the broad bear is era-split. No new clean survivor.

## FINAL multi-regime portfolio result
6 single-axis regimes frozen (causal, pre-P&L) + cross-scale D1 confluence + §5 acceptance-event + broad-bear all tested.
CLEAN SURVIVORS: S5 (trend/breakout, universal), CRS-1 (high-vol correction, in independent validation). NEAR-MISSES (documented,
NOT promoted): RS-2 (range breakout+D1), LOWVOL_BEAR wide-short, LOWVOL_BEAR x acceptance (tail-dep removed, OOS-thin). ROUTER:
S5 + CRS-1 active; NO_TRADE in RANGE / HIGHVOL_BULL / LOWVOL_BULL / MIDVOL_BULL / MIDVOL_BEAR (+ low-vol-bear as watch-list).
ROBUST META: regime-gating alone does not beat R20 (era-trend dominance); tradeable specialists require STRUCTURAL/CROSS-SCALE
direction-supplying mechanisms (S5, CRS-1). The acceptance-event is a validated tail-dependence-reducer for future candidates.

## BLS-1 bull-side cross-scale divergence LONG (generalization test of CRS-1 principle) — FAIL
D1-trend-UP (bull context) + H4-trend-DOWN (counter-dip) -> M15 LONG (mirror of CRS-1). avgR -0.116, DISC -0.188, 14/16 neg
years, best-10%rm -0.347. The CRS-1 cross-scale-divergence principle does NOT generalize to the bull side: counter-trend
bounces reliably FAIL only in the high-vol DOWN-correction (dominant down-flow), whereas D1-up is era-ambiguous (blowoffs) and
uptrend dips don't reliably bounce. Confirms CRS-1 is genuinely a down-correction specialist, not a general cross-scale rule.
=> Multi-regime portfolio + cross-scale generalization search EXHAUSTIVELY complete. Survivors remain S5 + CRS-1.

## ALS-1 long acceptance-above (resistance-break retest-HOLD -> long) — FAIL
Mirror of the validated acceptance-short. avgR -0.118 all-context (15/16 neg yrs), D1-up -0.117 (16/16 neg), high-vol -0.038
(DISC -0.124). Long-side acceptance does NOT work: upside breakout-retests get faded. Confirms LONG side has NO edge except S5
(BLS-1 dip-buy, ALS-1 acceptance-above, all regime-longs fail). Asymmetry: down-acceptance is a tail-reducer, up-acceptance fails.

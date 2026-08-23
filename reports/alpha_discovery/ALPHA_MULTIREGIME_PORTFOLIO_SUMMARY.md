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

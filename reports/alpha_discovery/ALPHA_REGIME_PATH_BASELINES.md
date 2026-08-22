# ALPHA_REGIME_PATH_BASELINES

Regime-conditional forward-path base rates (§10) — the correct baseline for regime-conditional lift (§2). H1, H=48h, first-passage P(+X before -Y). Any state must beat ITS OWN REGIME base rate materially (§17).

## DEV 2021-2023 P(+X/-Y) by regime (L=long, S=short)
| regime | N | +70/-70 L/S | +100/-70 L/S | +100/-100 L/S |
|---|---|---|---|---|
| UP | 1350 | 0.51/0.48 | 0.38/0.38 | 0.46/0.50 |
| DOWN | 1004 | 0.48/0.50 | 0.41/0.41 | 0.49/0.48 |
| QUIET | 2503 | 0.50/0.49 | 0.43/0.40 | 0.51/0.47 |
| CHOP | 3294 | 0.52/0.46 | 0.44/0.38 | 0.52/0.45 |
| TRANSITION | 1997 | 0.50/0.49 | 0.41/0.40 | 0.50/0.47 |

## Same-regime cross-era baselines (b0+b1 2011-2018), +100/-70
| regime | N | LONG | SHORT |
|---|---|---|---|
| UP | 3378 | 0.369 | 0.377 |
| DOWN | 3125 | 0.339 | **0.402** |
| QUIET | 6346 | 0.365 | **0.413** |
| CHOP | 8026 | 0.390 | 0.399 |
| TRANSITION | 5715 | 0.375 | 0.391 |

**Observations:** regime base rates are fairly STABLE across eras (unlike the raw state->path lifts that inverted). DOWN-regime SHORT base ~0.40-0.41 both eras; QUIET SHORT ~0.40-0.41. **Discovery target:** a causal STATE, evaluated WITHIN a regime, that lifts path materially above the same-regime base AND holds across same-regime occurrences (DEV vs b0/b1). Priority: DOWN & QUIET regimes (SHORT), where cross-era base rates are most consistent.

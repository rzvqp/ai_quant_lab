# ALPHA_CONTRAST_MINER_REPORT_V1 — ex-ante discriminators for structural-break outcomes

Central Factory engine (§5). Question: among structurally-similar STRUCTURAL_BREAK events, what OBSERVABLE-BEFORE-ENTRY feature
discriminates winners (continue to +2R) from losers (fail/reverse)? Ex-ante features only (bars≤break; outcome NEVER an input).
`behavior_contrast.py`, N=15,962 events, base netR=−0.425 / WR 0.272. STRESS 0.24, cross-era D/C/O.

## Discriminator results — NO feature flips the sign (every bin net-negative)
| discriminator | best bin | best-bin netR | cross-era | reading |
|---|---|---|---|---|
| TARGET_SPACE (room to 100b extreme) | <1 ATR (price-discovery) | −0.341 | stable-neg | MORE room = WORSE (−0.49) → room = late-stage/exhaustion, not opportunity |
| PRIOR_TEST_COUNT (level freshness) | 1-2 tests | −0.424 | stable-neg | freshness does not help |
| BREAK_VELOCITY (impulse) | 0.5-1 ATR | −0.405 | stable-neg | impulsive breaks WORSE (−0.44) — momentum already spent |
| BREAK_DEPTH (close beyond level) | <0.2 ATR | −0.388 | stable-neg | deeper break = WORSE (−0.49) |
| LOCATION (premium/discount) | discount | −0.375 | stable-neg | discount mildly less-bad, never positive |
| HTF_ALIGN | aligned=1 | −0.379 | — | alignment helps (vs −0.493) but never crosses zero |
| SESSION | Asia | −0.391 | — | Asia less-bad; NY worst (−0.562, NOT S5's config) |
| DIRECTION | both ~−0.42 | — | — | no long/short asymmetry |

## Findings
- **CONTRAST_DISCRIMINATOR_FOUND = NO (cost-surviving).** Every ex-ante feature shifts the loss but none produces a net-positive,
  cross-era-stable cell. The strongest *relative* discriminators — HTF-alignment (+0.11 vs mis-aligned) and location=discount (+0.05) —
  are directionally sensible but insufficient: a break aligned with the higher-timeframe trend at a discount still nets −0.37.
- **Counter-intuitive but consistent:** deeper/faster/roomier breaks perform WORSE — the "impressive" break has already consumed its
  move (VOLPATH double-break geometry), so the ex-ante magnitude of the break is anti-predictive of continuation. This is why breakout
  strategies fail: the observable break quality does not carry the continuation signal.
- **Interpretation:** the discriminating information is NOT present in price-derived ex-ante features. Winners vs losers are separated
  only by what happens AFTER entry (VOLPATH: post-break follow-through predicts continuation, but that is unavailable ex-ante and
  redundant with the already-failed breakout). **The signal that would discriminate is orthogonal to price** (order flow / positioning /
  real-yield regime) — see the DATA_NEED in the Factory report.

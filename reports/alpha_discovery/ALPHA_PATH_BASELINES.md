# ALPHA_PATH_BASELINES

Unconditional forward-path base rates (§12), for lift comparison. Population: 2021-2023 native gated H1 DEV (N=10,168), causal (state at bar close, path from next bar). Reference = close[i]; first-passage to +X vs -Y (project pips, 10p=$1) within horizon H. Price-only.

## P(+X before -Y) unconditional base rates
| label | H=24h LONG | H=24h SHORT | H=48h LONG | H=48h SHORT |
|---|---|---|---|---|
| +50/-50 | 0.500 | 0.481 | 0.501 | 0.483 |
| +70/-70 | 0.491 | 0.462 | 0.507 | 0.482 |
| **+100/-70** | **0.376** | **0.349** | **0.418** | **0.391** |
| +100/-100 | 0.430 | 0.392 | 0.506 | 0.467 |
| +150/-75 | 0.242 | 0.205 | 0.329 | 0.282 |
- MFE median: 95p (H24) / 143p (H48). MAE median: 89p (H24) / 128p (H48).
- LONG base > SHORT base everywhere (the 2021-2023 up-trend bias). A useful SHORT state must lift SHORT above these.
- **Any conditional claim must beat these base rates materially (§12); small lifts (<~0.03-0.05 abs) are noise.**

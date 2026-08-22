# ALPHA_DXY_INFORMATION_MAP

Mandate `ALPHA-XAUUSD-DXY-CAUSAL-INCREMENTAL-INFORMATION-001`. Causal DXY state -> XAUUSD future-path INFORMATION, measured as INCREMENTAL lift over the XAUUSD price-only parent-state base rate (§7), LONG/SHORT separate (§13), event-deduped (§14), cross-era b0/b1/y2123 (§9), predeclared lag curve {0,1,2,4}H (§12). Aligner frozen in `ALPHA_DXY_ALIGNER_CONTRACT.md`. STRATEGY_SECOND.

## Status
- **Cycle 1 (foundation, checkpoint #35):** `dxy_data.py` causal loader/aligner built + coverage verified == ratified report (b0 97.4% / b1 97.8% / y2123 99.9% same-hour), causal-leak assertion passes. Predeclared DXY feature set + lag set frozen. **Foundation finding:** past DXY return has ~0 linear corr with XAUUSD forward return in every era -> the DXY<->gold inverse relationship is CONTEMPORANEOUS not predictive; naive lagged DXY-return carries no edge. NEXT = Stage A DXY information map + incremental test.

## Hypotheses (predeclared, §6)
- X1 DXY directional impulse -> XAUUSD downside (strength) / upside (weakness), L/S separate.
- X2 DXY acceleration/deceleration (more info than level/direction?).
- X3 XAUUSD/DXY disagreement (divergence -> continuation or reversal?).
(no DXY trading rules until information survives §16)

## Stage A — univariate DXY -> XAUUSD path map (checkpoint #36)
`dxy_infomap.py`. DXY state (impulse/accel/efficiency, USD strength vs weakness) -> XAUUSD P(+70/-50 & +100/-70) lift vs era-global XAUUSD base, directed hypothesis side (§13), lag {0,1,2,4}H, cross-era, deduped (6h). H=24h.
| DXY state -> side | b0 | b1 | y2123 | read |
|---|---|---|---|---|
| dxyImpUp -> S | +0.036 | -0.009 | +0.013 | b1 flips -> not stable |
| dxyImpDn -> L | +0.023 | +0.017 | -0.001 | y2123 ~0 -> fails |
| dxyAccUp/Dn | ~0 | ~0 | ~0 | no info |
| **dxyEffUp -> S** | +0.022 | +0.023 | **-0.022** | inverse in b0/b1, **REVERSES 2021-2023** |
| **dxyEffDn -> L** | +0.025 | +0.033 | **-0.039** | inverse in b0/b1, **REVERSES 2021-2023** |
Lag curve: lift decays from lag0 (l0 strongest, l2/l4 weaker) — no better lag; effect weak throughout.
**Finding:** NO cross-era-stable univariate DXY directional information. The classic inverse-DXY->gold signal (persistent DXY efficiency) holds in 2011-2018 (b0/b1, +0.02..+0.03) but **INVERTS in the 2021-2023 inflation/safe-haven regime (-0.02..-0.04)** — gold & USD rose together. DXY's directional link to gold is REGIME-CONDITIONAL, not stationary (same program-wide pattern, now on the exogenous axis). Lifts are small (<=0.04) consistent with ~0 linear corr. NEXT: X3 divergence (XAUUSD/DXY disagreement) + §7 incremental-over-price-only test + interactions before any conclusion.

# ALPHA_DXY_INFORMATION_MAP

Mandate `ALPHA-XAUUSD-DXY-CAUSAL-INCREMENTAL-INFORMATION-001`. Causal DXY state -> XAUUSD future-path INFORMATION, measured as INCREMENTAL lift over the XAUUSD price-only parent-state base rate (§7), LONG/SHORT separate (§13), event-deduped (§14), cross-era b0/b1/y2123 (§9), predeclared lag curve {0,1,2,4}H (§12). Aligner frozen in `ALPHA_DXY_ALIGNER_CONTRACT.md`. STRATEGY_SECOND.

## Status
- **Cycle 1 (foundation, checkpoint #35):** `dxy_data.py` causal loader/aligner built + coverage verified == ratified report (b0 97.4% / b1 97.8% / y2123 99.9% same-hour), causal-leak assertion passes. Predeclared DXY feature set + lag set frozen. **Foundation finding:** past DXY return has ~0 linear corr with XAUUSD forward return in every era -> the DXY<->gold inverse relationship is CONTEMPORANEOUS not predictive; naive lagged DXY-return carries no edge. NEXT = Stage A DXY information map + incremental test.

## Hypotheses (predeclared, §6)
- X1 DXY directional impulse -> XAUUSD downside (strength) / upside (weakness), L/S separate.
- X2 DXY acceleration/deceleration (more info than level/direction?).
- X3 XAUUSD/DXY disagreement (divergence -> continuation or reversal?).
(no DXY trading rules until information survives §16)

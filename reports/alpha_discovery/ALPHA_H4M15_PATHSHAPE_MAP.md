# ALPHA_H4M15_PATHSHAPE_MAP

Mandate `ALPHA-XAUUSD-H4-M15-PATH-SHAPE-DISCOVERY-001`. M15 multi-bar PATH-SHAPE / SEQUENCE information conditional on causal H4 parent state (frozen in `ALPHA_H4_PARENT_STATE_CONTRACT.md`). Lift measured vs the per-H4-state/per-era M15 base rate (§8), LONG/SHORT separate (§9), event-deduped (§11), same-H4-state cross-era gate (§10). Bounded windows 4/8/16 M15 bars (§6); max complexity H4 state + 1-3 M15 descriptors (§7). Material lift only (§13).

## Status
- **Cycle 1 (foundation, checkpoint #26):** H4 parent-state taxonomy FROZEN + per-state M15 base rates established (DEV/b0/b1), all states EffN>=500 -> cross-era gate viable. Established that instantaneous H4 state alone gives era-dependent directional bias (not cross-era-stable); QUIET is the symmetric neutral. NEXT frontier = M15 path-shape families conditional on H4 state.

## Path-shape families (to screen)
1. directional run length / persistence-vs-alternation (window 4/8)
2. impulse -> retracement geometry (retrace depth vs preceding move)
3. path cleanliness / efficiency evolution across bars
4. recovery speed after adverse excursion
5. successive MFE/MAE asymmetry
6. volatility acceleration -> controlled retracement
7. HH/HL vs LH/LL sequence behavior
8. failed directional sequence / recent curvature

(no named strategies until information survives §14)

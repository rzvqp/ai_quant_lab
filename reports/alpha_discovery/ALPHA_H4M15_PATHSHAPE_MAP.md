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

## Family 1 — run-length / persistence-vs-alternation (checkpoint #27)
`h4m15_runlen.py`. Descriptors: signed run-length (>=3,>=4 up/dn), path-efficiency pe8 (persistUp/persistDn/altern), pe4 (cleanUp/cleanDn). Cross each H4 state x descriptor x side x {70/50,100/70}; lift vs same-H4-state deduped base; DEV DISC/CONF + per-year + b0 + b1. **Result: NO cross-era-stable POSITIVE tradeable lift.**
| cell | lift | D/C | b0/b1 | read |
|---|---|---|---|---|
| QUIET x runUp>=4 -> S 70/50 | -0.055 | -0.02/-0.11 | -0.02/-0.03 | only CROSS_STABLE flag, but NEGATIVE (short-avoidance) + per-year sign flip (2021 +0.02 / 2023 -0.09) -> weak, not a trade |
| DOWN x persistDn -> S 100/70 | +0.059 | +0.08/+0.04 | +0.03/**-0.00** | strongest positive; era-conditional continuation, **b1 absent** -> fails cross-era |
| UP x runUp>=3 -> S 70/50 | +0.048 | +0.10/**-0.03** | +0.02/+0.02 | DISC/CONF disagree (fails firewall); mean-revert/exhaustion in DEV-disc only |
| DOWN x cleanUp -> L 70/50 | +0.045 | +0.04/+0.05 | +0.01/+0.01 | positive all cells but b0/b1 <0.02 (immaterial) |
| UP x runDn>=4 -> L 70/50 | -0.037 | | +0.04/-0.02 | "pullback-in-uptrend -> LONG" NOT supported (negative) |
**Verdict:** run-length/persistence adds no cross-era-stable positive directional lift over the H4-state base. Continuation edges (DOWN persistDn short) remain era-conditional (fail b1 low-vol era); mean-reversion/exhaustion signals weak/DISC-CONF-inconsistent; pullback-in-trend not supported. PIVOT -> Family 2 (impulse->retracement geometry / retracement depth).

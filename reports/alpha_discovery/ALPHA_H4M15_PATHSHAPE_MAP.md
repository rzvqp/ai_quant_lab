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

## Family 2 — impulse -> retracement geometry (checkpoint #28) — FIRST CROSS-ERA-STABLE CANDIDATE
`h4m15_impretr.py`. Descriptors: impulse magnitude (ATR-norm, W=8/16) x retracement depth (close position in window range): shallow (near extreme=continuation geom) vs deep (bounced=reversal geom). Lift vs same-H4-state base, deduped, cross-era.
| cell | lift | D/C | b0/b1 | read |
|---|---|---|---|---|
| **DOWN x impDn8&shallow -> S 70/50** | **+0.055** | +0.03/+0.08 | **+0.04/+0.03** | **CROSS_STABLE incl b1** — down-impulse continuation short in DOWN H4; per-yr 2021 +0.12/2023 +0.05; +100/-70 also + (b0+0.04/b1+0.02) |
| DOWN x impDn16&shallow -> S 70/50 | +0.040 | -0.00/+0.07 | +0.03/+0.03 | same mechanism neighboring window (b0/b1 +) -> definition-stable support |
| DOWN x impUp8/16&shallow -> S | -0.054/-0.088 | neg | mixed | coherent MIRROR: counter-trend bounce makes shorts worse (mechanism-consistent) |
| QUIET x impUp16&shallow -> S 100/70 | +0.049 | +0.05/+0.04 | **-0.03/-0.02** | REVERSES cross-era -> era-transient, fails |
| UP x impUp16&shallow -> S 70/50 | +0.031 | +0.04/+0.02 | +0.02/+0.00 | weak, b1~0 |
**Verdict:** Family 2 yields the FIRST cross-era-stable positive candidate of this mandate: DOWN-H4 + M15 down-impulse-shallow-retrace -> SHORT continuation (survives DISC/CONF + b0 + b1 + neighboring-window + coherent mirror). Registered ST-H4DN-M15DNIMP-SHALLOW-SHORT, PENDING full §8/§14/§15 characterization + tradeability (structural stop, not the research bracket) + §17 independence vs S5/COMP-CONT-L. NOTE: the +0.055 research-bracket lift is INFORMATION, not yet tradeable expectancy.

## Family 2 candidate CHARACTERIZED (checkpoint #29) — NOT a tradeable survivor
`h4m15_dnimp_char.py`. ST-H4DN-M15DNIMP-SHALLOW-SHORT, structural stop = recent 8-bar M15 swing high (med 42/62/30p DEV/b0/b1). Net STRESS expectancy:
| era | best avgR | WR | best10 | verdict |
|---|---|---|---|---|
| b0 (strong-downtrend, high-vol) | +0.200 (rr3) / +0.089 (rr1) | .43-.55 | ~0 to -0.11 | **tradeable** |
| DEV 2021-2023 | -0.015 (rr3) | .38-.48 | -0.18..-0.36 | breakeven-negative (losing 2022, DISC/CONF disagree) |
| b1 (low-vol) | -0.020 (rr3) | .38-.52 | -0.15..-0.35 | negative |
**Verdict:** tradeable ONLY in the b0 high-vol strong-downtrend era; net-negative DEV+b1 -> EXPECTANCY is era-conditional though the relative INFO lift was cross-era-stable. Root cause: DOWN-state base rate + follow-through scale with era volatility (b1 MFE med 32p vs b0 59p), so a stable +0.03 hit-rate lift converts to positive expectancy only where absolute moves are large. Fails robust-survivor bar (§22); NOT frozen; NOT rescued by vol-sub-cutting (would re-tune frozen H4 taxonomy, §3). **Central lesson: cross-era-stable relative info != cross-era-stable tradeable expectancy.** PIVOT -> Family 3 (recovery-after-adverse / successive MFE-MAE asymmetry / volatility-expansion->controlled-retracement).

## Family 3 — recovery / MFE-MAE asymmetry / vol-expansion->calm (checkpoint #30)
`h4m15_recovery.py`. Descriptors: dipRecovUp (deep dip recovered to/above start=absorption), popFadeDn (pop faded=reversal), asymUp/asymDn (intrabar excursion asymmetry over W=8), volExpCalmUp/Dn (expansion then calm=continuation). Lift vs same-H4-state base, deduped, cross-era. **Result: NO cross-era-stable candidate.**
| cell | lift | D/C | b0/b1 | read |
|---|---|---|---|---|
| UP x dipRecovUp -> L 70/50 | +0.059 | +0.06/+0.06 | +0.02/**-0.01** | absorption long, DEV-robust (all years +, coherent mirror) but b1 negative -> era-conditional, fails |
| DOWN x asymDn -> S 70/50 | +0.047 | +0.05/+0.04 | +0.02/**+0.00** | sellers-won-intrabar short, b1 flat -> fails |
| DOWN x popFadeDn -> S 70/50 | +0.036 | +0.01/+0.06 | +0.01/+0.01 | pop-fade reversal short, small/immaterial |
| QUIET x popFadeDn -> L 70/50 | +0.039 | +0.06/+0.01 | +0.01/-0.00 | fade-recover long, b0/b1 <0.02 |
**Verdict:** no cross-era-stable positive candidate. Strongest (UP dipRecovUp LONG +0.059) is DEV-robust + b0-marginal but b1-negative. Meta-pattern across F1-F3: continuation edges work in high-vol/trend eras (b0/DEV) & fail b1; reversal/absorption edges work in DEV & fail hist. Binding constraint = b1 low-vol lacks directional follow-through. PIVOT -> Family 4 (HH/HL structural swing-sequence + wick/body asymmetry).

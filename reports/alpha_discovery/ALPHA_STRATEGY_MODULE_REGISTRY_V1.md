# ALPHA_STRATEGY_MODULE_REGISTRY_V1 — coverage denominator (MODULAR_STRATEGY_DISCOVERY_PROGRAM_V1)

Taxonomy: ALPHA_STRATEGY_MODULE_TAXONOMY_V1 (14 modules RATIFIED 2026-08-23). This registry is the ONLY authoritative coverage
denominator; no "exhaustion" claim is valid without reference to it. Coverage is MECHANISM-based (not hypothesis count). Status
codes: UNTESTED · LIGHT (lightly) · SUBST (substantially) · BNEG (bounded-negative) · NEAR (near-miss) · SURV (survivor found) ·
IVAL (independently validated). All prior evidence causal-verified where applicable (post VE 91b7415). Maintained continuously.

## Module dashboard (§17)
| module | module status | sub-mechanisms (branches) | tested | untested | near-miss | survivor | last result | next action |
|---|---|---|---|---|---|---|---|---|
| **M01 trend/continuation** | BNEG | impulse-cont · fresh-extreme-cont · MTF-align · persistence-hold | 3 | persistence-hold sizing | — | — | multi-TF confluence era-split (post-repair G) | low priority (bounded) |
| **M02 pullback/retest** | BNEG (near-miss resolved) | MA/structure-pullback · broken-level-retest-hold · Fib/measured · depth-continuation | 3 | measured-retrace | CAND-G0037 RESOLVED = not a survivor | — | **CAND-G0037 NET resolved: NET +0.41 recent (cost negligible) but FAILS gate — best-10%rm -0.29, CONF 2020-22 -0.096, era-dependent (R20)** | low priority (resolved) |
| **M03 breakout/expansion** | SURV | prior-extreme-brk · coil-brk · opening-range-brk · measured-move | 4 | — | — | **S5 (IVAL)** | S5 validated; other breakouts fade | low priority |
| **M04 range/mean-reversion** | BNEG | boundary-fade · nσ-reversion · return-to-center · range-rotation | 3 | range-rotation | RS-2 (range-brk, sparse) | — | fade fails (boundaries break>reject) | low priority |
| **M05 liquidity/sweep** | LIGHT | swing-pool-sweep · equal-H/L-sweep · session-extreme-sweep · failed-break-liq | 1-2 | equal-H/L, session-extreme (proper pool+reclaim) | — | — | sweep-reversal neg (but not the strict pool+reclaim def) | MED (MK-02 detector unrun to profitability) |
| **M06 volatility/compression** | BNEG | compression→expansion-magnitude · vol-onset · vol-clustering · vol-regime-MR | 3 | vol-regime-MR | — | — | R26: magnitude predictable, NON-directional | low priority (bounded) |
| **M07 session/opening-range** | SURV | opening-range-brk · session-extreme · session-transition · session-inheritance | 4 | non-NY-session-ORB independence | Batch-D (S5-redundant) | **S5 (IVAL)** | S5 validated; others S5-redundant/neg | low priority |
| **M08 auction/reference** | BNEG | level-touch-reject · break-accept-cont · value-migration · reclaim-reversal | 3 | value-migration (causal, non-circular) | — | — | extensions revert, era-split | MED (acceptance suite untested causally) |
| **M09 cross-scale** | **LIGHT/OPEN** | divergence-fade · confluence-amplify · nested-align · HTF-state×LTF-event | 2 (invalid/null) | **causal divergence & confluence largely open** | — | — (CRS-1 INVALIDATED) | CRS-1 lookahead; BLS-1 neg; MTF era-split | MED (class open, but era-dependent risk) |
| **M10 market-state/transition** | BNEG | CHoCH-change · range→expansion-ignition · trend→range-exhaustion · mode-onset | 3 (as regimes) | **MK-01 CHoCH/BOS transition EVENTS (unrun)** | — | — | 6-regime taxonomy 0 survivors; vNext R23 | MED (transition-EVENT policies unrun) |
| **M11 path/hazard/survival** | SUBST(3/4) | time-since-event-hazard · duration-in-state · survival-no-invalidation · excursion-ordering | 3 | survival-no-invalidation | — | — | **duration-in-state: P(target-first)~coinflip (0.485-0.507) all bands & eras — no duration ordering edge** | survival-without-invalidation |
| **M12 event sequencing** | SUBST(2/4) | compress→brk→fail→rev · sweep→reclaim→retest→hold · brk→retest→cont · multi-leg | 2 | sweep→reclaim→retest, multi-leg | — | — | **brk→retest→hold: sequence (+0.30) does NOT beat component (+0.32), era-split (§10 fail)** | sweep→reclaim→retest, multi-leg |
| **M13 imbalance/FVG** | SUBST(2/4) | FVG-edge/CE50 · IFVG-flip · BPR · FVG-stack/density | 2 | BPR, FVG-stack/density | — | — | **CAND-0003 FVG-CE50 NET-neg all partitions (-0.41); IFVG era-split — polarity→era-trend not predictive** | BPR + stack (remaining 2 branches) |
| **M14 order-block/S-D** | SUBST(2/4) | OB-rejection · OB-mitigation/breaker · demand/supply-reentry · liquidity-void | 2 | OB-mitigation, demand-zone | — | — | **OB-rejection polarity->era-trend (DEM DISC -0.75/OOS +0.15), era-split; void ELIM** | OB-mitigation + demand-zone |

## Existing frozen/validated assets classified in the taxonomy
- **S5** → PRIMARY **M07** (session/opening-range), SECONDARY M03. Status: **INDEPENDENTLY_VALIDATED**, frozen. Do not modify.
- **CRS-1** → PRIMARY **M09** (cross-scale divergence). Status: **STATISTICAL_VALIDATION_FAIL / INVALIDATED_BY_TEMPORAL_LOOKAHEAD**. Do not resurrect. M09 remains OPEN (candidate invalidated, not the module).

## Module-selection priority (§5) — ranked, with WHY
1. **M02 pullback3-LONG NET resolution** — an UNRESOLVED near-miss with a real GROSS+ signal; §7 mandates testing the exact old candidate first; cheapest highest-value information (resolves a hanging verdict). **← FIRST.**
2. **M13 imbalance/FVG** — ratified distinct primitive, ZERO Alpha profitability tests; high unexplored space + mechanistic novelty + portfolio independence.
3. **M14 order-block/supply-demand** — same: ratified distinct primitive, Alpha-unrun; high unexplored space.
4. **M12 event sequencing** & **M11 path/hazard** — shallow coverage, genuinely open branches, moderate effective-N.
5. **M09 cross-scale (causal)** — class open post-CRS-1, but era-dependent-direction risk + M5-window single-era limit → temper expectations.
6. **M05 sweep (strict pool+reclaim)** & **M08 acceptance-suite (causal)** & **M10 transition-EVENTS** — detector-defined but Alpha-unrun in their strict forms.
LOW priority (SUBST/bounded): M01, M03(beyond S5), M04, M06, M07(beyond S5) — materially tested, bounded-negative.

**Next action: execute priority #1 — resolve M02 pullback3-LONG NET on the exact historical definition (no retuning, §7).**

## Modular-discovery results log
- **M02-1 CAND-G0037 pullback3-LONG NET resolution (m02_pullback3_net.py, exact §7 replay):** GROSS control reproduces history exactly (recent-primary +0.4206, n534). NET (canonical CFG cost, gross=False): recent-primary **+0.4136** — cost negligible (wide 2.5ATR stop). FULL GATE: best-10%-removed **-0.29** (tail-dependent), DISC≤2018 +0.12 / CONF 2020-22 **-0.096** / OOS 2023+ +0.40 (era-dependent, R20 — fails in 2020-21 chop). VERDICT: NET-positive on recent estimand but **NOT a robust survivor**. The hanging NEAR_MISS is resolved: not cost, but tail+era dependence. No retuning; no new identity (did not survive).
- **M13-1/2 FVG-CE50 + IFVG (m13_fvg.py, m13_fvg_trade.py, ratified MK-03 detectors):** INFO: FVG polarity does NOT predict direction — bull & bear FVGs both resolve in the ERA-TREND (bull-FVG asym DISC -0.36/OOS +0.62; bear mirror). CAND-0003 exact tradeable (FVG-CE50, stop=far edge, target=near edge, + required min-stop floor): NET **-0.41 all partitions** (Statistician's documented R:R-collapse-on-small-gaps confirmed). IFVG inversion also era-split. VERDICT: FVG-CE50 + IFVG branches BOUNDED-NEGATIVE (era-trend, not polarity-predictive). Remaining M13 branches: BPR, FVG-stack/density. CAND-0003 DEMO hypothesis resolved NET-negative.
- **M14-1 OB-rejection (m14_ob.py, ratified Mod.5 order_flow):** INFO: OB polarity does NOT predict direction — demand & supply OBs both resolve in the ERA-TREND (demand-OB->LONG asym DISC -0.75/CONF +0.75/OOS +0.15; supply mirror). BOUNDED-NEGATIVE (era-split, R20). Remaining M14 branches: OB-mitigation, demand-zone-reentry. **PATTERN SO FAR (empirical, not a law) across M13/M14/M08/M09: every directional-polarity primitive TESTED SO FAR -> era-trend, not mechanism-direction. The only edge remains S5 (structural session breakout, direction self-supplied).**
- **M11-duration (m11_hazard.py):** target-before-stop ordering P(up-1.5ATR-first) in ema-up state is ~coinflip (0.485-0.507) across ALL duration bands AND all eras — duration carries NO material hazard/ordering edge. Non-directional negative. M11 -> 3/4; remaining: survival-without-invalidation.
- **M12-brk→retest→hold (m12_seq.py):** the gated break→retest→hold SEQUENCE (up-dn +0.30) does NOT beat the bare break COMPONENT (+0.32); both era-split (DISC -0.06/-0.20, OOS +1.1). §10 incremental test FAILS + era-trend. No sequence edge. M12 -> 2/4; remaining sweep→reclaim→retest, multi-leg.
- **M04-rotation (m04_rotation.py):** range boundary-to-boundary rotation P(reach opposite first) = 0.10-0.12 (all partitions ~0.06-0.13) — gold ranges BREAK, don't rotate. M04 now COMPLETE (fade/nσ/return-to-center/rotation all bounded-negative).

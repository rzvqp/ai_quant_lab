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
| **M11 path/hazard/survival** | **LIGHT** | time-since-event-hazard · duration-in-state · survival-no-invalidation · excursion-ordering | 2 (weak) | **duration, survival, ordering-as-signal** | — | — | CR-7 age weak; post-repair B era-entangled | MED (shallow, mostly untested) |
| **M12 event sequencing** | **LIGHT** | compress→brk→fail→rev · sweep→reclaim→retest→hold · brk→retest→cont · multi-leg | 1 | **sweep→reclaim→retest, multi-leg (gated, incremental)** | — | — | post-repair C failed-break cost-killed | MED (shallow, mostly untested) |
| **M13 imbalance/FVG** | **LIGHT (Alpha)** | FVG-edge/CE50 · IFVG-flip · BPR · FVG-stack/density | 0 by Alpha | **all (MK-03 detectors ratified, Alpha-unrun to profitability)** | — | — | CAND-0003/0005/0010 DEMO/SCREEN, unrun | **HIGH (distinct primitive, unrun)** |
| **M14 order-block/S-D** | **LIGHT (Alpha)** | OB-rejection · OB-mitigation/breaker · demand/supply-reentry · liquidity-void | 0 by Alpha | **all (Mod.5 detectors ratified, Alpha-unrun)** | — | — | CAND-0011/0013/0014 SCREEN; CAND-0004 void ELIM | **HIGH (distinct primitive, unrun)** |

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

# Alpha Strategy-Module Definition & Coverage Audit

Mandate: MODULE_DEFINITION_AUDIT (CEO 2026-08-23). Reconstructed from authoritative repository artifacts (not memory).
**No new discovery performed.** Purpose: establish the research map before the next campaign. Deliver-then-stop.

## 0. Authoritative-taxonomy finding (§3) — does a complete taxonomy already exist? NO.
Four PARTIAL / differently-organized taxonomies exist; none is the complete economic strategy-module space:
- **`edge_research/flowb_generator.py` MECHANISM clusters (CEO-ratified 2026-08-16)** — the closest thing to canonical Alpha
  mechanism definitions: `pullback`, `momentum`, `continuation`, `compression_breakout`, `breakout` (bos+bos_retest), each with a
  one-line RATIONALE. Identity = `cluster_of(regime, mechanism)`; entry-timing/stop/hold differences are NOT new mechanisms.
  Covers ~5 mechanisms only (trend/pullback/breakout/vol family); NOT reversion, liquidity, session, cross-scale, hazard, sequence.
- **`code/mstrat.py` + `mstrat_ext.py` S1-S51 families** — the canonical backtest engine's signal families (S1 trend/EMA, S4 NR/vol,
  S5 NY-ORB [VALIDATED], S6 reversion, S9 HTF-context, S18 session, S20, … S51). Organized by SIGNAL, not economic module; overlaps.
- **`CANDIDATE_QUEUE.md` MK-detector policy families** (CAND-0001..0037) — organized by DETECTOR primitive: MK-01 structure
  (BOS/CHoCH), MK-02 liquidity (sweep), MK-03 imbalance (FVG/BPR/density), MK-04 institutional/session reference levels, Mod.5
  order-block/void/zone, Mod.7 confluence. Organized by detector, not by economic mechanism.
- **`ai_trader/market_intelligence/` modules** — structure, liquidity, momentum, expansion, session_behavior, trend, volatility
  (+ agreement, confidence). **These are MARKET-INTELLIGENCE / market-STATE detectors (the N1-N6 read-only layer), NOT Alpha
  strategy-mechanism modules** (§3). A strategy module asks "what tradeable edge"; an MI module asks "what state is the market in".
**Conclusion: the proposed M01-M12 economic strategy-module taxonomy is NEW (not yet canonical). Most modules are only
PARTIALLY_DEFINED via the fragments above; several are NOT_DEFINED as economic modules.** No canonical terminology overwritten.

## 1. Per-module audit (§4-§6) + additional modules found
Legend DEFINITION_STATUS: CANON=canonically defined · PART=partially · AMB=ambiguous · NONE=not defined. Coverage per §8.

### M01 TREND / CONTINUATION — PART
- Sources: flowb `momentum`/`continuation` clusters (rationale: "enter on trend-direction impulse" / "buy a fresh breakout of the
  recent extreme within the trend"); mstrat S1; MI `trend.py`. Economic hypothesis: a directional impulse continues.
- Qualifies: entry WITH an established higher-TF trend direction on impulse/fresh-extreme. Not: counter-trend, range, reversion.
- Prior research: batches A/E/F continuation (neg); Phase-A grid TREND_UP×momentum/continuation (GROSS+, NET-pending); multi-TF
  confluence (post-repair G, era-split); hazard/time-since-break (post-repair B). **Coverage SUBSTANTIALLY_TESTED → BOUNDED_NEGATIVE**
  (direction=era-trend, R20). Survivors: none (S5 is breakout not trend). Near-miss: TREND_UP×pullback3 GROSS (cost-unresolved — see M02).

### M02 PULLBACK / RETEST — CANON (flowb `pullback`)
- Sources: flowb `pullback` (pullback2/3/4 = one cluster, rationale "buy the retracement, resume the trend"). Boundary: pullback =
  counter-trend retrace WITHIN a trend, re-entered on resumption; distinct from M04 reversion (no trend) by the trend precondition.
- Prior research: Phase-A grid CAND-G0037 pullback3/atr2/time40 recent-GROSS +0.42 trimmed +0.33 (PROVISIONAL, **NET/cost UNRESOLVED**);
  trend-pullback batches (neg after cost); CR-5 retest-failure (causal null); M5-1/M5-3 (pullback-fade + M5 trigger, neg, era-dependent).
- **Coverage SUBSTANTIALLY_TESTED but the flagship pullback3-LONG NET result is genuinely OPEN (GROSS-positive, never cost-cleared).** NEAR-MISS.

### M03 BREAKOUT / EXPANSION — CANON (flowb `breakout`,`compression_breakout`)
- Sources: flowb `breakout` ("confirmed structural break as a regime transition") + `compression_breakout` ("range compresses then
  expands; trade the expansion"); mstrat S4/S5; MK-01 structure_break_retest. Boundary vs M06: breakout = a LEVEL is crossed (directional);
  M06 vol = magnitude expansion regardless of level.
- Prior research: **S5 (NY opening-range breakout LONG) = VALIDATED SURVIVOR** (only independently-validated edge). Batch NR/weekly-OR
  (weaker S5 echo); CR-9/11 vol-expansion (tail-dep/whipsaw); vol-breakout post-repair (neg); M5-4 coil-breakout (coinflip).
- **Coverage SUBSTANTIALLY_TESTED → SURVIVOR_FOUND (S5); non-session breakout variants BOUNDED_NEGATIVE (breakouts fade, R19).**

### M04 RANGE / MEAN REVERSION — PART
- Sources: mstrat S6 (2σ reversion); RANGE_REGIME_V1 (`range_regime.py`, causal). Boundary vs M02 pullback = NO trend precondition (fade
  extremes in a balanced/range regime). Boundary vs M06 compression = range is CONTAINMENT (low efficiency), compression is low VOL.
- Prior research: S6 (neg, tiny-stop artifact); reversal/MR batches (neg, "WORST −0.74"); RANGE program RS-1 fade / RS-3 pullback (FAIL,
  boundaries break>reject); auction reversion (post-repair D). **Coverage SUBSTANTIALLY_TESTED → BOUNDED_NEGATIVE** (fade fails in XAUUSD).

### M05 LIQUIDITY / SWEEP / FAILED BREAK — PART
- Sources: MK-02 `liquidity_sweep_reversal` (RATIFIED detector, CAND-0020); D7 consumption. Boundary vs M03 breakout = sweep is a
  breakout that FAILS/reverses (liquidity grab); boundary vs M08 = sweep is about STOP-runs at prior extremes, not value/reference acceptance.
- Prior research: sweep_reversal (post-repair, strongly neg — sweeps CONTINUE not reverse); CR-12 fade-breakout (one-sided); event_seq
  failed-break (post-repair C, cost-killed); CAND-0020/0032 (SURVIVED_RED_TEAM_A, weekly-structure signal, NOT run to profitability by Alpha).
- **Coverage LIGHTLY-to-SUBSTANTIALLY_TESTED → BOUNDED_NEGATIVE on reversal form; the MK-02 detector-based sweep policies are Part-B-pending, NOT profitability-tested.**

### M06 VOLATILITY / COMPRESSION — PART
- Sources: flowb `compression_breakout`; `market_state.py` compression/expansion (RATIFIED Statistician v2.6.1); mstrat S4 (NR). Boundary:
  M06 asks about MAGNITUDE/vol-state (direction-agnostic); becomes M03 only when a directional break is traded.
- Prior research: Frontier K vol-predictability (R26: compression→expansion cross-era-STABLE but DIRECTIONALLY SYMMETRIC → not spot-tradeable);
  vol_dryup (post-repair A, same: real expansion, non-directional); CR-3 vol-exp-down (tail-dep). **Coverage SUBSTANTIALLY_TESTED →
  BOUNDED (magnitude predictable R26, but non-directional → no standalone spot edge).** This is the deepest characterized module.

### M07 SESSION / OPENING-RANGE STRUCTURE — PART
- Sources: S5 (NY ORB); mstrat S18; MI `session_behavior.py`; MK-04 session-level policies (CAND-0026-0036). Boundary vs M08 = session is
  about TIME-window structure (open, session extremes); M08 is about price-level REFERENCE interaction regardless of time.
- Prior research: **S5 SURVIVOR** lives here; Batch D session-range-inheritance (3 all-era-positive but §30-KILLED as S5-redundant, 64-78%
  overlap); CR-6 session-ordering (causal ~0.53 ceiling, not tradeable); session_inherit (post-repair E, ~coinflip); seasonality (post-repair
  H, drift/artifact). **Coverage SUBSTANTIALLY_TESTED → SURVIVOR (S5); other session structure S5-redundant or negative.**

### M08 AUCTION / REFERENCE-LEVEL INTERACTION — PART
- Sources: MK-04 `institutional_reference_levels` (PDH/PDL, partial-ratified); `session_levels.py` (RATIFIED v2.7.39). Boundary: reference =
  a horizontal price MEMORY level; interaction = touch/reject/accept/break. "Auction/acceptance-vs-rejection" concept NOT canonically defined.
- Prior research: CAND-0001 PDH-PDL (DEMO_BASELINE, Statistician criteria defined); CAND-0006 weekly levels; CR-10 PDL/PDH (causal: PDL-break
  reverts, PDH-reject weak); auction acceptance (post-repair D, extensions revert). **Coverage SUBSTANTIALLY_TESTED → BOUNDED_NEGATIVE
  (reference extensions revert, era-split); the acceptance/value-migration sub-concept is AMB and DEFINITION_REQUIRED.**

### M09 CROSS-SCALE STRUCTURE — AMB → DEFINITION_REQUIRED_FROM_CEO
- Sources: NONE canonical. Instances: CRS-1 (cross-scale H4-divergence — **INVALIDATED, lookahead**); CR-13/15 causal-replay (null); the last
  CEO mandate explicitly kept "cross-scale CLASS OPEN" (CRS-1 failure ≠ class failure). Boundary vs M01/M02 = cross-scale conditions the
  entry-TF signal on an INDEPENDENT higher-TF STATE (divergence or confluence between scales), not a single-scale trend/pullback.
- Prior research: CRS-1 (invalidated); BLS-1 bull-side divergence (post-repair, neg); xscale_rangepos (F, momentum not reversion); multi-TF
  confluence (G, era-split); M5-1/M5-4 (M5×HTF, marginal). **Coverage LIGHTLY_TESTED as a CAUSAL class → OPEN.** The one positive was a
  lookahead artifact; the genuinely-causal cross-scale space is barely explored. **Needs a canonical definition before systematic search.**

### M10 MARKET-STATE / STRUCTURAL TRANSITION — PART
- Sources: MK-01 `market_structure` BOS/CHoCH (RATIFIED, CAND-0009/0021/0022); MARKET_OPERATING_MODE_V1; RANGE_LIFECYCLE vNext (research-ratified);
  the causal regime taxonomy (6 regimes). Boundary vs M12 = transition is a STATE CHANGE (regime A→B) as the event; M12 is an ORDERED SEQUENCE
  of sub-events. Boundary vs M03 breakout = a break can BE a transition, but transition also includes trend→range, vol-regime shifts.
- Prior research: multi-regime taxonomy (6 regimes frozen, 0 survivors, era-split/sub-cost); morphology unsupervised (46 archetypes = known
  families, 0 new); RANGE vNext lifecycle (events amplify era-trend, R23); CHoCH/BOS candidates (Part-B pending, not profitability-tested).
  **Coverage SUBSTANTIALLY_TESTED as regimes → BOUNDED_NEGATIVE; the MK-01 transition-EVENT policies are detector-defined but NOT run to profitability.**

### M11 PATH / HAZARD / SURVIVAL — NONE → DEFINITION_REQUIRED_FROM_CEO
- Sources: NONE canonical. Instances: CR-7 episode-age (causal weak); hazard/time-since-break (post-repair B, era-entangled); path-survival
  prose in CR ledgers. Boundary vs "entry timing" (§10) = hazard is about how forward EVENT PROBABILITY changes with ELAPSED TIME/duration/
  survival-without-invalidation; entry-timing is about the best moment to enter a FIXED setup.
- Prior research: CR-7, post-repair B only. **Coverage LIGHTLY_TESTED.** Elapsed-time/duration/survival conditioning is largely UNTESTED as a
  systematic module. Needs canonical definition.

### M12 EVENT SEQUENCING — NONE → DEFINITION_REQUIRED_FROM_CEO
- Sources: NONE canonical. Instances: event_seq compression→failed-break→response (post-repair C); morphology sequence scan (batch I, no stable
  archetype); CR retest sequences. Boundary vs M10 = a sequence is >=2 ORDERED causal sub-events with acceptance/failure between them; a
  transition is a single state change. Boundary vs M02 = retest is a 2-step sequence but canonically folded into breakout (flowb bos_retest).
- Prior research: post-repair C + batch I only. **Coverage LIGHTLY_TESTED.** Multi-event ordered sequences (beyond retest) largely UNTESTED. Needs definition.

### ADDITIONAL MODULES FOUND IN PROJECT HISTORY (§4) — genuinely distinct, in the candidate queue, NOT in the CEO's 12:
### M13 IMBALANCE / FVG (order-flow imbalance reaction) — PART [ALPHA_PROPOSED as a distinct module]
- Sources: MK-03 `imbalance_mechanics` (FVG/BPR, CLOSED v2.5.6, RATIFIED); CAND-0003 FVG-CE50, 0005 BPR, 0010 FVG-stack-density. Economic
  hypothesis: price reacts to its own displacement-created imbalance (fair-value gap) on revisit. Distinct from M05 (liquidity=stop-runs) and
  M08 (reference=horizontal memory levels): FVG is a RANGE/zone left by a displacement, mechanically different. **Coverage: detector-ratified,
  policies DEMO_BASELINE/SCREENING, but Alpha has NOT run them to profitability (Part-B/Statistician pending). LIGHTLY_TESTED by Alpha.**
### M14 ORDER-BLOCK / SUPPLY-DEMAND ZONE — PART [ALPHA_PROPOSED as a distinct module]
- Sources: Mod.5 `order_block_void` / `order_flow` (RATIFIED); CAND-0004 void, 0011/0014 OB-rejection/mitigation, 0013 demand-zone. Economic
  hypothesis: price reacts at institutional order-block / supply-demand / liquidity-void zones. **Coverage: detectors ratified, policies
  SCREENING/Part-B-pending, NOT profitability-tested by Alpha. LIGHTLY_TESTED.** (Could fold under M05/M08 but mechanically distinct primitive.)

NOTE (§11): M5-1..M5-4 are NOT a module — they are M02(pullback/M5-1,M5-3), M03(breakout/M5-4), M08/M02(M5-2) instances at M5 resolution.
NOTE: VOLUME (displacement/breakout/climax/dry-up) is an INFORMATION dimension (like M5), mapped into M01/M03/M06, not a module.
NOTE: MORPHOLOGY (unsupervised archetypes) and CONFLUENCE (Mod.7 multi-primitive) are METHODS/combination-axes, not economic modules.

## 2. Machine-readable coverage matrix (§13)
| module | def_status | major_mechanisms | mechanisms_tested | mechanisms_untested | survivors | near_misses | boundary_clarity | ceo_def_required | coverage_confidence |
|---|---|---|---|---|---|---|---|---|---|
| M01 trend/continuation | PART | impulse-continuation; fresh-extreme-continuation; MTF-aligned | both continuation forms; MTF | trend-strength-conditioned sizing | none | pullback3-adjacent | clear vs M02(no-retrace) | no | qualitative HIGH-neg |
| M02 pullback/retest | CANON | pullback-depth(2/3/4); retest-hold | pullback3(GROSS); retest-fail(causal); M5-timed | NET/cost resolution of pullback3-LONG | none | **CAND-G0037 pullback3-LONG (GROSS+, NET-open)** | clear (flowb) | no | qualitative MED (NET-gap) |
| M03 breakout/expansion | CANON | level-break; compression-breakout; session-ORB | all three | — | **S5 (validated)** | — | clear vs M06 | no | HIGH |
| M04 range/mean-reversion | PART | boundary-fade; extreme-reversion | both | range-regime-specific vol-conditioned fade untested cleanly | none | RS-2 (range-breakout, sparse) | AMB vs M02/M06 | partial | qualitative HIGH-neg |
| M05 liquidity/sweep/failed-break | PART | sweep-reversal; failed-break-fade | reversal(neg); failed-break | MK-02 detector-policies (Part-B, unrun) | none | — | AMB vs M03/M08 | partial | LIGHT-MED |
| M06 volatility/compression | PART | compression→expansion; vol-onset; dry-up | all (info) | direction-agnostic straddle re-forms | none | — | clear | no | HIGH (bounded non-dir) |
| M07 session/opening-range | PART | opening-range-breakout; session-inheritance; session-levels | all | non-NY session ORB independence | **S5** | Batch-D (S5-redundant) | clear vs M08 | no | HIGH |
| M08 auction/reference-level | PART | touch-reject; break-accept; value-migration | PDH/PDL/weekly/session; acceptance | acceptance/value-migration as canonical concept | none | — | AMB (auction undefined) | **yes** | MED |
| M09 cross-scale structure | AMB | divergence; confluence; range-position | CRS-1(invalid); confluence; MTF | **causal cross-scale largely unexplored** | none (CRS-1 invalidated) | — | AMB vs M01/M02 | **yes** | LIGHT (OPEN) |
| M10 market-state/transition | PART | regime-classification; BOS/CHoCH transition; range-lifecycle | 6-regime taxonomy; morphology; vNext | MK-01 transition-EVENT policies (unrun); vol-regime transition | none | RS-2 | AMB vs M12 | partial | MED-HIGH (regimes bounded) |
| M11 path/hazard/survival | NONE | time-since-event; duration-in-state; survival-hazard | episode-age; time-since-break | **duration/survival hazard systematic** | none | — | needs def vs entry-timing | **yes** | LIGHT |
| M12 event sequencing | NONE | ordered A→accept/fail→B | failed-break sequence | **multi-event ordered sequences** | none | — | needs def vs M10/M02 | **yes** | LIGHT |
| M13 imbalance/FVG (+) | PART | FVG-reaction; BPR; imbalance-density | detector-defined, Alpha-unrun | profitability of MK-03 policies | none | — | distinct primitive | partial | LIGHT (Alpha) |
| M14 order-block/S-D (+) | PART | OB-rejection; mitigation; void; demand-zone | detector-defined, Alpha-unrun | profitability of Mod.5 policies | none | — | AMB vs M05/M08 | partial | LIGHT (Alpha) |

## 3. Exhaustion-claim audit (§9) — VERDICT: EXHAUSTION_CLAIM_OVERSTATED
Alpha's recent "price+volume mechanism repertoire exhaustively covered / S5-singular" statements were made WITHOUT a predefined
comprehensive module/mechanism taxonomy or an explicit denominator. Per the strict standard (§9), a large count of negative tests is
NOT sufficient. Concretely, several module-mechanism cells are LIGHT/UNRUN: M09 causal cross-scale (explicitly OPEN; the one positive
was a lookahead artifact), M11 hazard/survival and M12 event-sequencing (only 1-2 ad-hoc tests each, no canonical definition), M13
imbalance/FVG and M14 order-block (detector-ratified policies never run to profitability by Alpha), and M02's flagship pullback3-LONG
whose NET/cost result is unresolved (GROSS-positive). **The supported claim is only: no ADDITIONAL robust edge was found among the
mechanisms actually tested; the space is NOT demonstrably exhausted.** This audit supplies the denominator that was missing.

## 4. Executive output (§14)
**A. MODULES READY FOR SYSTEMATIC DISCOVERY (canon/well-bounded def):** M02 pullback, M03 breakout, M06 volatility, M07 session.
**B. PARTIALLY DEFINED:** M01 trend, M04 range/reversion, M05 liquidity/sweep, M08 auction/reference, M10 market-state/transition, M13 imbalance/FVG, M14 order-block.
**C. AMBIGUOUS:** M09 cross-scale (definition + boundary vs M01/M02 unclear); M04↔M02↔M06 and M05↔M03↔M08 boundaries need arbitration.
**D. NOT DEFINED (DEFINITION_REQUIRED_FROM_CEO):** M11 path/hazard/survival; M12 event sequencing; the M08 "auction/acceptance/value-migration" sub-concept; a canonical M09 cross-scale definition.
**E. ADDITIONAL MODULES FOUND (ALPHA_PROPOSED, not auto-canonical):** M13 IMBALANCE/FVG (MK-03); M14 ORDER-BLOCK/SUPPLY-DEMAND (Mod.5).

**TOP UNEXPLORED MECHANISM GAPS (highest information value, from the map — NOT to be tested yet):**
1. **M02 pullback3-LONG NET/cost resolution** — the single genuine near-miss with an unresolved NET verdict (GROSS +0.42); resolve before declaring trend/pullback closed.
2. **M13 imbalance/FVG + M14 order-block profitability** — RATIFIED detectors with SURVIVED_RED_TEAM_A policies that Alpha never ran to profitability (Part-B/cost gate). A whole tested-by-Statistician-but-not-by-Alpha branch.
3. **M09 causal cross-scale (divergence/confluence)** — barely explored under the repaired alignment; the only prior positive was a lookahead artifact, so the class is genuinely open (per CEO §6).
4. **M11 duration/hazard/survival conditioning** — whether forward edge probability changes with time-in-state; only 2 ad-hoc tests.
5. **M12 multi-event ordered sequences** (beyond single retest/failed-break) — largely unrepresented.
6. **M05 MK-02 sweep + M10 MK-01 BOS/CHoCH transition policies** — Part-B/Statistician-pending, never profitability-tested by Alpha.

## 5. ALPHA_PROPOSED definitions offered for CEO approval (NOT canonical until approved) — for M09, M11, M12, M08-auction
- **M09 cross-scale (proposed):** a strategy whose entry-timeframe signal is CONDITIONED on the state of a strictly-higher, fully-closed
  timeframe that is INDEPENDENT of the entry signal (divergence = scales disagree; confluence = scales agree). Excludes single-scale trend/pullback.
- **M11 path/hazard/survival (proposed):** a strategy whose activation depends on ELAPSED TIME or DURATION since a causal anchor (regime entry,
  structural break, vol expansion) or on survival-without-invalidation — i.e., the conditioning variable is TIME/duration, not a price event.
- **M12 event sequencing (proposed):** a strategy defined by >=2 ORDERED causal sub-events with an explicit acceptance/failure test between
  them (A → hold/fail → B → response), preregistered as a sequence; distinct from a single transition (M10) or a folded retest (M03).
- **M08 auction/acceptance (proposed):** interaction with a reference level classified as ACCEPTANCE (sustained trade beyond the level = value
  migration) vs REJECTION (return inside), measured causally at a point-in-time (no forward-window overlap — cf. the M5-2 circularity lesson).

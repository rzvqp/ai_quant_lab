# ALPHA_STRATEGY_MODULE_DEFINITIONS_V1_DRAFT

Mandate: CANONICAL_MODULE_DEFINITION_DRAFT (CEO 2026-08-23). Definition task only — NO discovery, NO P&L, NO hypotheses tested.
`EXISTING_AUTHORITATIVE_CONTENT` and `ALPHA_PROPOSED_CANONICAL_DEFINITION` are separated; CEO ratifies. Deliver-then-stop.

**Governing rules encoded here:** TIMEFRAME_IS_NOT_MODULE · M5_IS_NOT_MODULE · every hypothesis has ONE PRIMARY_MECHANISM_MODULE
(the source of expected edge); other modules are CONDITIONER/TRIGGER/CONTEXT/EXECUTION. Overlap is allowed; boundaries are explicit.
Sub-mechanism branches are the future discovery DENOMINATOR and must be economically distinct (NOT split by RR/lookback/threshold/timeframe).

---

## M01 — TREND / CONTINUATION  [PART — authoritative fragments: flowb `momentum`/`continuation`; MI `trend.py`; mstrat S1]
- **CANONICAL DEFINITION (proposed):** The edge is the *persistence* of an already-established directional state — entering WITH the prevailing direction on an in-trend impulse or fresh in-trend extreme, expecting continuation.
- ECONOMIC PREMISE: order-flow/positioning momentum persists once a directional regime is established.
- CORE CAUSAL MECHANISM: autocorrelation of returns / trend-follower + momentum inflow while the regime holds.
- ENTRY-SIDE RESEARCH QUESTION: "Given an established trend, does entering in its direction (impulse or fresh extreme) beat random?"
- WHAT QUALIFIES: pro-trend impulse entry; fresh N-bar extreme in the trend direction (flowb `continuation`); trend-direction MTF alignment as the *edge source*.
- WHAT DOES NOT QUALIFY: counter-trend entries (M02/M04); a level-boundary resolution that supplies the trade (M03); range with no trend (M04).
- PRIMARY STRUCTURAL EVENTS: trend confirmation (EMA order / higher-highs-higher-lows), in-trend impulse bar, in-trend new extreme.
- ALLOWED INFORMATION SCALES: D1/H4/H1/M15 (trend); M5 execution only.
- ACTIVATION: directional regime confirmed AND a pro-trend impulse/extreme occurs. OFF: trend structure breaks (opposite CHoCH) or flattens.
- DISTINCTION: vs **M03** — M01 needs NO boundary crossing (rides an existing move); M03 requires a level resolution. vs **M02** — M01 enters WITH the impulse; M02 waits for a counter-move (retrace) first.
- KNOWN OVERLAPS: uses trend-state (MI trend.py) as its own premise; MTF (M09) if the trend is on a higher scale (conditioner).
- PROJECT EXAMPLES: batches A/E/F continuation; multi-TF confluence (post-repair G); Phase-A TREND_UP×momentum/continuation (GROSS).
- ANTI-EXAMPLES: S5 (breakout, not continuation); range-fade (M04); pullback3 (M02).
- SUB-MECHANISM BRANCHES: ├─ in-trend impulse-continuation ├─ in-trend fresh-extreme continuation ├─ MTF trend-alignment continuation └─ trend-persistence-conditioned holding.

## M02 — PULLBACK / RETEST  [CANON — authoritative: flowb `pullback` (pullback2/3/4 = one cluster, "buy the retracement, resume the trend")]
- **CANONICAL DEFINITION (preserve existing):** A temporary counter-move AGAINST a larger established directional structure, entered on expected RESUMPTION of that direction.
- ECONOMIC PREMISE: trends advance in waves; the retrace offers better price for the same continuation edge.
- CORE CAUSAL MECHANISM: mean-reversion of the *short-term* counter-move nested inside a *persistent* larger trend.
- ENTRY-SIDE RESEARCH QUESTION: "After a counter-trend retrace within a trend, does entry on resumption beat entering at the impulse?"
- WHAT QUALIFIES: retrace to a moving average / prior structure / retest of a broken level, THEN resumption trigger (flowb `pullback`, `bos_retest`).
- WHAT DOES NOT QUALIFY: reversion with NO dominant trend (M04); a fresh impulse with no prior retrace (M01).
- PRIMARY STRUCTURAL EVENTS: in-trend retrace completion; retest of a broken level that holds; higher-low (uptrend) / lower-high (downtrend).
- ALLOWED SCALES: trend on D1/H4/H1; retrace/trigger on M15/M5.
- ACTIVATION: established trend + completed counter-move + resumption trigger. OFF: retrace exceeds the trend-invalidation level (becomes reversal).
- DISTINCTION: vs **M04** — M02 REQUIRES a dominant trend and bets on continuation; M04 needs NO trend and bets on return-to-center. vs **M12** — a single retest is folded here (flowb bos_retest); a multi-step ordered sequence is M12.
- KNOWN OVERLAPS: trend-state (M01) is a mandatory conditioner; retest of a broken level touches M03/M08.
- PROJECT EXAMPLES: **CAND-G0037 pullback3 (recent GROSS +0.42, NET-unresolved — the near-miss)**; CR-5 retest-failure (causal null); M5-1/M5-3.
- ANTI-EXAMPLES: 2σ range-fade (M04); NY-ORB (M03/M07).
- SUB-MECHANISM BRANCHES: ├─ MA/structure pullback ├─ broken-level retest-hold ├─ Fib/measured retrace └─ pullback-depth continuation (shallow/deep as ONE mechanism, not RR-split).

## M03 — BREAKOUT / EXPANSION  [CANON — authoritative: flowb `breakout` ("confirmed structural break as a regime transition") + `compression_breakout`; mstrat S5]
- **CANONICAL DEFINITION (preserve existing):** The edge arises from price RESOLVING THROUGH a structural boundary/reference, trading in the direction of the resolution.
- ECONOMIC PREMISE: a boundary concentrates orders; its resolution releases directional flow.
- CORE CAUSAL MECHANISM: breakout of a contained range / prior extreme / opening range → expansion in the break direction.
- ENTRY-SIDE RESEARCH QUESTION: "When price closes through boundary X, does trading the resolution direction beat random?"
- WHAT QUALIFIES: close beyond a prior N-bar extreme, a coil, or an opening range (S5); enter on break or its retest.
- WHAT DOES NOT QUALIFY: riding an existing move with no boundary crossed (M01); a breakout that FAILS/reverses as the hypothesis (M05).
- PRIMARY STRUCTURAL EVENTS: range-high/low break; coil break; opening-range break; measured-move projection.
- ALLOWED SCALES: any; the boundary defines the scale. **§10 rule: if volatility/compression is merely a FILTER, PRIMARY stays M03.**
- ACTIVATION: a defined boundary + a confirmed close through it. OFF: close back inside the boundary (failed break → M05 territory).
- DISTINCTION: vs **M01** (§7 rule) — a break inside a trend is still M03 if the BOUNDARY RESOLUTION supplies the hypothesis; M01 if no boundary. vs **M06** — M03 crosses a LEVEL (directional); M06 is magnitude expansion regardless of level.
- KNOWN OVERLAPS: compression (M06) as conditioner; session open (M07) for ORB; trend (M01) as context.
- PROJECT EXAMPLES: **S5 (NY opening-range breakout LONG = VALIDATED SURVIVOR)**; CR-9/11; vol-breakout (post-repair); M5-4 coil-breakout.
- ANTI-EXAMPLES: range-fade (M04); pullback3 (M02).
- SUB-MECHANISM BRANCHES: ├─ prior-extreme breakout ├─ compression/coil breakout ├─ opening-range breakout └─ measured-move/expansion continuation.

## M04 — RANGE / MEAN REVERSION  [PART — authoritative: mstrat S6 (2σ); RANGE_REGIME_V1]
- **CANONICAL DEFINITION (proposed):** The edge is an expected RETURN TOWARD value/center within a balanced (non-trending) state — fade extremes, NO requirement of trend continuation.
- ECONOMIC PREMISE: in balance, price oscillates around fair value; extremes over-extend and revert.
- CORE CAUSAL MECHANISM: mean-reversion of price to a range center / value area when no directional regime dominates.
- ENTRY-SIDE RESEARCH QUESTION: "In a balanced range, does fading the boundary toward the center beat random?"
- WHAT QUALIFIES: fade at a range boundary / statistical extreme (2σ) targeting the mid, in a low-efficiency regime.
- WHAT DOES NOT QUALIFY: counter-move WITHIN a trend expecting continuation (M02); boundary BREAK (M03).
- PRIMARY STRUCTURAL EVENTS: range boundary touch/rejection; statistical over-extension; return-to-mid.
- ALLOWED SCALES: any; range defined on the trading scale.
- ACTIVATION: confirmed balanced/range regime + boundary touch. OFF: range breaks (regime → trend/expansion).
- DISTINCTION: vs **M02** (§8) — M04 needs NO trend and targets the CENTER; M02 needs a trend and targets CONTINUATION. vs **M06** — M04 = containment (low efficiency); M06 = low VOLATILITY (magnitude).
- KNOWN OVERLAPS: range-regime detection (M10 state) as conditioner.
- PROJECT EXAMPLES: S6 (neg, tiny-stop); RANGE RS-1 fade / RS-3 (FAIL, boundaries break>reject); auction reversion (post-repair D).
- ANTI-EXAMPLES: pullback3 (M02, trend present); coil breakout (M03).
- SUB-MECHANISM BRANCHES: ├─ boundary-rejection fade ├─ statistical-extreme reversion ├─ return-to-VWAP/center └─ range-rotation (boundary-to-boundary).

## M05 — LIQUIDITY / SWEEP / FAILED BREAK  [PART — authoritative: MK-02 `liquidity_mechanics` (pools, wick-sweep, D7 consumption)]
- **CANONICAL DEFINITION (proposed):** The edge is a hypothesis about interaction with LIQUIDITY POOLS / stop concentrations — a sweep (stop-run beyond a prior extreme) followed by reversal, i.e. the break FAILS because it was a liquidity grab.
- ECONOMIC PREMISE: resting stops beyond obvious extremes are targeted; once taken, price reverses (absorption).
- CORE CAUSAL MECHANISM: wick-sweep of a swing pool (MK-02) then reclaim → reversal.
- ENTRY-SIDE RESEARCH QUESTION: "When a prior extreme is swept and reclaimed, does fading the sweep beat random?"
- WHAT QUALIFIES (§9): a sweep that requires a LIQUIDITY-POOL/stop-concentration hypothesis (MK-02 wick-sweep + reclaim). A plain breakout failure with no liquidity hypothesis does NOT automatically qualify.
- WHAT DOES NOT QUALIFY: breakout continuation (M03); a level rejection framed as value/acceptance (M08).
- PRIMARY STRUCTURAL EVENTS: liquidity pool (equal highs/lows, swing extreme); wick-sweep beyond it; reclaim/close-back-inside.
- ALLOWED SCALES: any; pool defined by MK-02 swings.
- ACTIVATION: pool present + sweep + reclaim. OFF: acceptance beyond the pool (no reclaim → it was a real breakout, M03).
- DISTINCTION (§9): vs **M03 failed-break** — M05 requires the LIQUIDITY hypothesis (stops beyond a pool); a bare failed break without that is M03-fakeout, not M05. vs **M08** — M05 = stop-runs at extremes; M08 = acceptance/rejection at value/reference areas.
- KNOWN OVERLAPS: MK-02 depends on MK-01 swings (M10 structure); confluence with FVG/OB (M13/M14).
- PROJECT EXAMPLES: sweep_reversal (post-repair, neg — sweeps CONTINUE); CAND-0020/0032 (SURVIVED_RED_TEAM_A, Alpha-unrun).
- ANTI-EXAMPLES: coil breakout (M03); PDH reject (M08).
- SUB-MECHANISM BRANCHES: ├─ swing-pool sweep-reversal ├─ equal-highs/lows sweep ├─ session-extreme sweep └─ failed-break-with-liquidity fade.

## M06 — VOLATILITY / COMPRESSION  [PART — authoritative: `market_state.py` Compression(causal 460-bar p10)/Expansion(E010); flowb `compression_breakout`; mstrat S4]
- **CANONICAL DEFINITION (proposed):** The edge comes PRIMARILY from a volatility STATE, TRANSITION, or CLUSTERING property (compression→expansion magnitude), independent of a directional level. **§10: if volatility is merely a filter for a directional break, PRIMARY = M03.**
- ECONOMIC PREMISE: volatility is persistent/clustered and mean-reverting; compression precedes expansion.
- CORE CAUSAL MECHANISM: vol clustering — low-vol coils store energy released as an expansion of predictable MAGNITUDE (direction unspecified).
- ENTRY-SIDE RESEARCH QUESTION: "Does a volatility state/transition predict forward MAGNITUDE (and can that be monetized without a supplied direction)?"
- WHAT QUALIFIES: compression→expansion magnitude bets; vol-onset conditioning where VOL is the edge source; two-sided/straddle where direction is agnostic.
- WHAT DOES NOT QUALIFY: a directional breakout that merely uses compression as a filter (M03); range containment fade (M04).
- PRIMARY STRUCTURAL EVENTS: compression window (causal p10 range), expansion onset (E010), vol-ratio crossing.
- ALLOWED SCALES: any.
- ACTIVATION: vol-state condition met. OFF: vol reverts to baseline.
- DISTINCTION: vs **M03** (§10) — direction source: if the LEVEL supplies direction → M03; if only MAGNITUDE is the bet → M06. vs **M04** — M06 = low VOLATILITY; M04 = containment (low efficiency, may be normal vol).
- KNOWN OVERLAPS: feeds M03 (compression_breakout is a boundary M03 with a vol conditioner).
- PROJECT EXAMPLES: Frontier K vol-predictability (R26: cross-era-stable magnitude, NON-directional); vol_dryup (post-repair A); CR-3.
- ANTI-EXAMPLES: coil breakout traded directionally (M03); NY-ORB (M03/M07).
- SUB-MECHANISM BRANCHES: ├─ compression→expansion magnitude ├─ vol-onset/expansion timing ├─ vol-clustering persistence └─ vol-regime mean-reversion.

## M07 — SESSION / OPENING-RANGE STRUCTURE  [PART — authoritative: mstrat S5/S18; MI `session_behavior.py`; MK-04 session_levels]
- **CANONICAL DEFINITION (proposed):** The edge derives PRIMARILY from time/session-specific structure — the opening process, session transitions, session extremes, or recurring session behavior. **§11: merely entering a breakout during NY hours is NOT M07 unless the SESSION structure supplies the edge.**
- ECONOMIC PREMISE: liquidity/participation is time-structured; sessions have recurring opening/closing/transition behavior.
- CORE CAUSAL MECHANISM: session-open volatility injection + opening-range formation in a liquid window.
- ENTRY-SIDE RESEARCH QUESTION: "Does a session-specific structural event (open, session-extreme, transition) supply an edge tied to that time window?"
- WHAT QUALIFIES: opening-range breakout AS A SESSION EVENT (S5); prior/persistent session-level interaction (MK-04); session-transition behavior.
- WHAT DOES NOT QUALIFY: a generic breakout that happens in NY hours with no session-structure dependence (that is M03).
- PRIMARY STRUCTURAL EVENTS: session open, opening range, session high/low/mid, session transition.
- ALLOWED SCALES: intraday (M15/M5) keyed to UTC session clock; H1/H4 context.
- ACTIVATION: within the session window + session-structure event. OFF: outside the window / session ends.
- **S5 CLASSIFICATION (§11):** S5 is a NY OPENING-RANGE breakout. Repository evidence (radar R13): entering AT NY open (TOD) = −0.65, but entering on the BREAKOUT of the NY opening RANGE = +0.074 cross-era — the edge is the opening-range STRUCTURE in the NY window. **PRIMARY = M07 (session/opening-range structure); SECONDARY conditioner = M03 (breakout mechanic).** It is a SESSION strategy because the opening-range + liquid-window structure is the edge source, not a generic boundary.
- KNOWN OVERLAPS: M03 (breakout is the execution mechanic); M08 (session levels are reference levels).
- PROJECT EXAMPLES: **S5 (SURVIVOR)**; Batch-D session-range-inheritance (S5-redundant, §30-killed); CR-6 session-ordering (~0.53); seasonality (post-repair H).
- ANTI-EXAMPLES: any-time coil breakout (M03); PDH-fade (M08).
- SUB-MECHANISM BRANCHES: ├─ opening-range breakout ├─ session-extreme interaction ├─ session-transition behavior └─ session inheritance (prior-session range → next).

## M08 — AUCTION / REFERENCE-LEVEL INTERACTION  [PART — authoritative: MK-04 institutional_reference_levels (PDH/PDL), session_levels; ⚠ auction/acceptance sub-concept UNDEFINED]
- **CANONICAL DEFINITION (proposed, §12):** The edge comes from price interacting with an economically-defined REFERENCE LEVEL/AREA (a horizontal price MEMORY) via ACCEPTANCE vs REJECTION — i.e., whether price accepts beyond the level (value migration) or is rejected back (failed auction / reclaim).
- **Causal component definitions (proposed, using only project price info):**
  - REFERENCE LEVEL = a prior-period extreme kept as memory: PDH/PDL (MK-04), prior/persistent session H/L/Mid (MK-04), prior-week levels.
  - ACCEPTANCE = price CLOSES beyond the level AND sustains (K consecutive closes beyond, measured at a point-in-time, NO forward-window overlap — the M5-2 circularity lesson) → value migration.
  - REJECTION = price touches/pierces the level then CLOSES back inside within K bars → failed auction.
  - VALUE MIGRATION = a sustained acceptance shifting the traded value region from one reference to the next.
  - RECLAIM = after acceptance beyond, price returns and closes back across the level (acceptance fails).
- ECONOMIC PREMISE: market participants remember reference levels; acceptance/rejection at them signals the next value region.
- CORE CAUSAL MECHANISM: auction accepts (continuation to next level) or rejects (reversion) at a memory level.
- ENTRY-SIDE RESEARCH QUESTION: "At reference level X, does acceptance/rejection classification predict the next move?"
- WHAT QUALIFIES: touch-reject fade; break-accept continuation; value-migration between reference areas.
- WHAT DOES NOT QUALIFY (§9): a stop-run/sweep at a swing pool (M05); a boundary breakout with no reference-memory hypothesis (M03); a range-center fade (M04).
- PRIMARY STRUCTURAL EVENTS: PDH/PDL/session-level touch, close-through (acceptance), close-back-inside (rejection), reclaim.
- ALLOWED SCALES: level from D1/session; interaction on M15/M5.
- ACTIVATION: price reaches a reference level. OFF: level consumed (D7) / new session invalidates prior-session levels.
- DISTINCTION (§9,§12): vs **M05** — M08 = value/acceptance at a MEMORY LEVEL; M05 = stop-liquidity grab at a pool. vs **M03** — M08 requires the reference-memory/acceptance hypothesis; a bare break is M03. vs **M04** — M08 targets the NEXT reference (directional migration), not the range center.
- KNOWN OVERLAPS: session levels straddle M07; confluence with FVG/OB (M13/M14).
- PROJECT EXAMPLES: CAND-0001 PDH-PDL (DEMO_BASELINE); CR-10 (PDL-break reverts, PDH-reject weak); auction acceptance (post-repair D, extensions revert).
- ANTI-EXAMPLES: swing-pool sweep (M05); coil breakout (M03).
- SUB-MECHANISM BRANCHES: ├─ level touch-rejection ├─ level break-acceptance (continuation) ├─ value migration (level→level) └─ reclaim/failed-auction reversal.

## M09 — CROSS-SCALE STRUCTURE  [AMB → full proposed def; NO authoritative canonical def; instance CRS-1 was INVALIDATED (lookahead)]
- **CANONICAL DEFINITION (proposed, §13):** The edge arises PRIMARILY from a RELATIONSHIP (divergence or confluence) between INDEPENDENT structures at DIFFERENT scales — the higher-scale state and the lower-scale event carry *different* information whose interaction is the hypothesis. **Cross-scale is NOT "uses more than one timeframe."**
- ECONOMIC PREMISE: when scales disagree (divergence) or strongly agree (confluence), the resolution carries information beyond either scale alone.
- CORE CAUSAL MECHANISM: higher-TF dominant flow reasserting against a lower-TF counter-move (divergence-fade) OR multi-scale agreement amplifying a move (confluence).
- ENTRY-SIDE RESEARCH QUESTION: "Does the RELATIONSHIP between scale-A state and scale-B event predict, beyond scale-B alone?"
- WHAT QUALIFIES (§13): H4 state vs M15 event where the H4 state is an INDEPENDENT signal (not just a trend filter); higher-TF direction conflicting with lower-TF path; nested-structure divergence/confluence.
- WHAT DOES NOT QUALIFY (§13): H4 used merely as a TREND FILTER for an M15 breakout (PRIMARY stays M03/M01) — the incremental-information test must show the cross-scale RELATIONSHIP, not one scale, supplies the edge.
- PRIMARY STRUCTURAL EVENTS: scale-A/scale-B agreement or disagreement state; counter-trend bounce within a higher-TF trend.
- ALLOWED SCALES: >=2 strictly-separated, fully-closed scales (causal alignment mandatory — VE nominal-close contract).
- ACTIVATION: the defined cross-scale relationship holds. OFF: relationship dissolves (scales realign / diverge away).
- DISTINCTION: vs **M01/M02** — those are single-scale (trend/retrace on one scale); M09 needs the INTER-scale relationship as edge. vs **M10** — M10 is a within-scale STATE CHANGE; M09 is a between-scale RELATIONSHIP at a point in time.
- KNOWN OVERLAPS: uses trend-state (M01) on the higher scale as a component; the M5 layer is execution, not the cross-scale relationship.
- PROJECT EXAMPLES: **CRS-1 (H4-up bounce fade — INVALIDATED, lookahead artifact)**; CR-13/15 causal-replay (null); BLS-1 bull-side divergence (neg); multi-TF confluence (G, era-split). Class explicitly OPEN per prior CEO mandate.
- ANTI-EXAMPLES: H4-trend-filtered M15 breakout (M03); single-scale MTF-EMA trend (M01).
- SUB-MECHANISM BRANCHES: ├─ cross-scale divergence-fade ├─ cross-scale confluence-amplification ├─ nested-structure alignment └─ higher-TF-state × lower-TF-event conditioning.

## M10 — MARKET-STATE / STRUCTURAL TRANSITION  [PART — authoritative: MK-01 BOS/CHoCH; MARKET_OPERATING_MODE_V1; RANGE_LIFECYCLE vNext; regime taxonomy]
- **CANONICAL DEFINITION (proposed, §14):** The edge arises specifically from a CHANGE OF STATE (regime A → regime B) — trading the TRANSITION behavior, not merely trading after a state is already established.
- ECONOMIC PREMISE: regime changes (trend→range, range→expansion, bull→correction) release characteristic behavior at the moment of change.
- CORE CAUSAL MECHANISM: structural break of the prior regime (CHoCH / vol-regime shift / mode change) initiating a new state.
- ENTRY-SIDE RESEARCH QUESTION: "At the moment of a state change, does trading the transition beat trading the already-established state?"
- WHAT QUALIFIES: CHoCH (character change) entries; range→expansion ignition; regime-onset conditioning where the TRANSITION is the edge.
- WHAT DOES NOT QUALIFY: trading well inside an already-established trend (M01) or range (M04); a multi-event ordered sequence (M12).
- PRIMARY STRUCTURAL EVENTS: CHoCH (MK-01), BOS that flips structure, range-lifecycle transition (vNext), operating-mode change.
- ALLOWED SCALES: any; state defined causally.
- ACTIVATION: a confirmed state change. OFF: state re-established or reverts.
- DISTINCTION (§14): vs **M01/M04** — those trade an EXISTING state; M10 trades the CHANGE. vs **M12** — M10 = single state change; M12 = ordered multi-event sequence. vs **M03** — a break can BE a transition; classify as M10 only if the REGIME-CHANGE behavior (not the boundary resolution) supplies the edge.
- KNOWN OVERLAPS: regime detection feeds every module as CONTEXT; MK-01 structure underlies M02/M05.
- PROJECT EXAMPLES: 6-regime taxonomy (0 survivors, era-split); morphology archetypes (46, all known); RANGE vNext lifecycle (R23); CHoCH/BOS candidates (Alpha-unrun).
- ANTI-EXAMPLES: in-trend pullback (M02); established-range fade (M04).
- SUB-MECHANISM BRANCHES: ├─ CHoCH character-change ├─ range→expansion ignition ├─ trend→range exhaustion └─ operating-mode/regime-onset transition.

## M11 — PATH / HAZARD / SURVIVAL  [NONE → full proposed def; DEFINITION_REQUIRED_FROM_CEO]
- **CANONICAL DEFINITION (proposed, §15):** The edge arises from PATH-DEPENDENT probability that changes with ELAPSED TIME, DURATION, or SURVIVAL — the conditioning variable is a CLOCK/AGE or survival-without-invalidation, NOT a price event and NOT mere entry timing.
- ECONOMIC PREMISE: the probability of continuation/reversal/target-before-stop is not constant; it evolves with how long a state/move has persisted.
- CORE CAUSAL MECHANISM: hazard-rate dynamics — e.g., a move's reversal hazard rises with age; target-before-stop ordering depends on time-in-state.
- ENTRY-SIDE RESEARCH QUESTION: "Does forward edge probability change MATERIALLY with elapsed time / duration / survival, holding the setup fixed?"
- **Component definitions (proposed):** STATE = the causal condition being timed (regime, trend, compression); CLOCK/AGE = elapsed bars since the anchor; EVENT = the outcome whose probability is modeled (break/reversal/target); SURVIVAL = persistence without invalidation to time t; HAZARD = instantaneous P(event at t | survived to t); OUTCOME = target-before-stop / MFE-MAE ordering.
- WHAT QUALIFIES: time-since-regime-entry, time-since-break, duration-in-compression, survival-without-invalidation conditioning.
- WHAT DOES NOT QUALIFY (§15): choosing the best MOMENT to enter a fixed setup (that is entry-timing/execution, not a module); a price-event trigger (belongs to its event module).
- PRIMARY STRUCTURAL EVENTS: the ANCHOR event that starts the clock (regime entry, break, vol expansion) + the elapsed-time variable.
- ALLOWED SCALES: any; the clock is causal elapsed bars.
- ACTIVATION: setup present AND age/duration in the hypothesized band. OFF: invalidation or age outside band.
- DISTINCTION (§10): vs entry-timing — hazard conditions on TIME/duration/survival as the edge; entry-timing picks a moment within a fixed setup. vs **M12** — hazard is about DURATION; M12 is about ORDERED discrete events.
- KNOWN OVERLAPS: always rides another module's setup (the anchor); it is a TIME conditioner elevated to primary when the edge is the time dependence.
- PROJECT EXAMPLES: CR-7 episode-age (causal, weak); hazard/time-since-break (post-repair B, era-entangled). Largely UNTESTED systematically.
- ANTI-EXAMPLES: M5 entry-timing (execution); a fixed-age filter tuned post-hoc (forbidden).
- SUB-MECHANISM BRANCHES: ├─ time-since-event hazard ├─ duration-in-state dependence ├─ survival-without-invalidation └─ adverse-first vs target-first ordering dynamics.

## M12 — EVENT SEQUENCING  [NONE → full proposed def; DEFINITION_REQUIRED_FROM_CEO]
- **CANONICAL DEFINITION (proposed, §16):** The edge comes from an ORDERED SEQUENCE of >=2 DISTINCT causal events (A → accept/fail → B → response) that carries information BEYOND any single event, preregistered as a sequence.
- ECONOMIC PREMISE: the market tells a multi-step story; the ordered combination (not any step alone) is informative.
- CORE CAUSAL MECHANISM: conditional path — event B's meaning depends on A having occurred and passed an acceptance/failure test.
- ENTRY-SIDE RESEARCH QUESTION: "Does the ordered sequence A→B→C predict beyond the best single event in it?"
- WHAT QUALIFIES: compression → attempted breakout → failed acceptance → opposite displacement; sweep → reclaim → retest → hold.
- WHAT DOES NOT QUALIFY (§16): a single-event setup; a state transition (M10, one change); a folded single retest (M03 bos_retest). A sequence must have >=2 ordered events with an explicit inter-event test AND beat its best single component.
- PRIMARY STRUCTURAL EVENTS: an ordered chain of module-events (each a qualifying event of some module) with acceptance/failure gates between.
- ALLOWED SCALES: any; sequence measured causally, each step at its close.
- ACTIVATION: the full ordered sequence completes. OFF: the chain breaks (a gate fails) → no trade.
- DISTINCTION (§16): vs **M10** — one state change vs a >=2-event chain. vs **M11** — ordered EVENTS vs continuous DURATION. vs **M02** — a bare retest is folded to M03; only a multi-step gated chain is M12.
- KNOWN OVERLAPS: composes events from other modules (sweep/M05 → reclaim/M08 → retest/M02); primary is M12 only if the ORDER carries the incremental edge.
- PROJECT EXAMPLES: event_seq compression→failed-break→response (post-repair C); morphology sequence scan (batch I, no stable archetype). Largely UNTESTED beyond single retest.
- ANTI-EXAMPLES: single coil-breakout (M03); episode-age (M11).
- SUB-MECHANISM BRANCHES: ├─ compression→break→fail→reverse ├─ sweep→reclaim→retest→hold ├─ break→retest→continuation └─ multi-leg structural narrative.

## M13 — IMBALANCE / FVG  [PART — authoritative: MK-03 `imbalance_mechanics.py` v2.5.6, RATIFIED; reconstructed mechanically]
- **PROJECT PRIMITIVE (reconstructed, §17):** A Fair Value Gap (FVG) is a THREE-bar imbalance: Bullish FVG when `low[i+1] > high[i-1]` (a gap the middle displacement bar leaves unfilled), level `[high[i-1], low[i+1]]`; Bearish symmetric. `ce_50` = FVG midpoint. IFVG (inverse) = first later close beyond the far edge inverts polarity. BPR = overlapping bullish×bearish FVG within ≤3 bars. FVGs do NOT survive a block boundary. `detect_fvg_reactions` = reaction on revisit (gradient + D7 consumption).
- **CANONICAL DEFINITION (proposed):** The edge is price REACTING to a self-created imbalance/inefficiency (an unfilled FVG region) on revisit — reversion at, or continuation through, the gap.
- ECONOMIC PREMISE: rapid displacement leaves an inefficiently-traversed region; price is drawn back to rebalance it, then reacts.
- CORE CAUSAL MECHANISM: mean-revisit to the unfilled 3-bar gap + reaction at its edge/midpoint (ce_50).
- ENTRY-SIDE RESEARCH QUESTION: "When price revisits an FVG, does the reaction at its edge/CE50 predict direction?"
- WHAT QUALIFIES: reaction at an FVG edge / CE50; IFVG polarity flip; BPR reaction. Mechanically = the MK-03 `detect_fvgs`/`detect_fvg_reactions` events.
- WHAT DOES NOT QUALIFY: a horizontal memory level (M08); a swing-pool sweep (M05); a plain range fade (M04).
- PRIMARY STRUCTURAL EVENTS: FVG formation (3-bar gap), FVG revisit/touch, CE50 interaction, IFVG inversion, BPR.
- ALLOWED SCALES: any; FVG defined on the trading scale (MK-03 is scale-agnostic geometry).
- ACTIVATION: an unfilled FVG is revisited. OFF: FVG fully consumed (D7) or block boundary crossed.
- DISTINCTION: vs **M08** — FVG is a RANGE/zone left by a displacement (dynamic, geometry-derived), not a prior-period horizontal memory level. vs **M14** — FVG is the gap BETWEEN bars i-1/i+1; an order block is the BODY of a specific bar.
- KNOWN OVERLAPS: confluence with OB/levels (Mod.7 CAND-0015/0017/0024/0030/0035); shares "reaction on revisit" logic with M14.
- PROJECT EXAMPLES: CAND-0003 FVG-CE50 (DEMO_BASELINE, Statistician tightest gate), CAND-0005 BPR (borderline), CAND-0010 FVG-stack-density. **Alpha-unrun to profitability.**
- ANTI-EXAMPLES: PDH fade (M08); OB rejection (M14).
- SUB-MECHANISM BRANCHES: ├─ FVG-edge/CE50 reaction ├─ IFVG polarity-flip ├─ BPR reaction └─ FVG-stack/density.

## M14 — ORDER-BLOCK / SUPPLY-DEMAND  [PART — authoritative: Mod.5 `order_flow.py`/`order_block_void.py` v2.5.9, RATIFIED; reconstructed mechanically]
- **PROJECT PRIMITIVE (reconstructed, §18):** An Order Block is a PURELY GEOMETRIC primitive = the BODY `[min(Close,Open), max(Close,Open)]` of the last OPPOSITE-direction bar immediately before an impulse (no volume used). Interactions: Breaker / Mitigation / Rejection (the impulse engulfs the opposite bar; later price returns to the block). A Liquidity Void = a bar transition that is a gap (hybrid: size-based OR temporal, e.g. hours 20/21 UTC, weekends included).
- **CANONICAL DEFINITION (proposed):** The edge is price REACTING at an institutional order-block / supply-demand zone (the geometric body preceding a displacement) on return — rejection/continuation from the zone.
- ECONOMIC PREMISE: the origin candle of an impulse marks unfilled institutional interest; price returning to it reacts (mitigation/rejection).
- CORE CAUSAL MECHANISM: return-to-origin-zone + rejection (supply/demand imbalance at the block body).
- ENTRY-SIDE RESEARCH QUESTION: "When price returns to an order-block body, does the reaction (rejection/mitigation) predict direction?"
- WHAT QUALIFIES: OB rejection, OB mitigation, breaker, demand/supply-zone re-entry, liquidity-void reaction. Mechanically = Mod.5 detectors.
- WHAT DOES NOT QUALIFY: a 3-bar FVG gap (M13); a horizontal memory level (M08); a stop-pool sweep (M05).
- PRIMARY STRUCTURAL EVENTS: OB formation (opposite bar before impulse), OB return/mitigation, breaker flip, void reaction.
- ALLOWED SCALES: any; OB is scale-agnostic geometry (Mod.5).
- ACTIVATION: price returns to an unmitigated OB. OFF: OB mitigated/consumed (D7) or breaker-flipped.
- DISTINCTION (§18): vs **M08** — OB is a dynamic zone from a specific origin bar's BODY, not a prior-period horizontal reference level. vs **M05** — OB is a supply/demand origin reaction, not a stop-run at a liquidity pool. vs **M13** — OB = a bar's body; FVG = the gap between bars.
- KNOWN OVERLAPS: confluence with FVG/levels (Mod.7); shares "return-and-react" with M13.
- PROJECT EXAMPLES: CAND-0004 void (ELIMINATED, 29 events), CAND-0011/0014 OB-rejection/mitigation, CAND-0013 demand-zone (SCREENING). **Alpha-unrun to profitability.**
- ANTI-EXAMPLES: FVG-CE50 (M13); PDH reject (M08).
- SUB-MECHANISM BRANCHES: ├─ OB rejection ├─ OB mitigation/breaker ├─ demand/supply-zone re-entry └─ liquidity-void reaction.

---

## 14×14 OVERLAP / BOUNDARY MATRIX (§20)
Codes: **D**=DISTINCT · **C**=CONDITIONER_OVERLAP · **E**=COMMON_EVENT_DIFFERENT_MECHANISM · **A**=POTENTIALLY_AMBIGUOUS. Lower triangle (symmetric).

| | M01 | M02 | M03 | M04 | M05 | M06 | M07 | M08 | M09 | M10 | M11 | M12 | M13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|M02| A |  |  |  |  |  |  |  |  |  |  |  |  |
|M03| A | E |  |  |  |  |  |  |  |  |  |  |  |
|M04| D | **A** | E |  |  |  |  |  |  |  |  |  |  |
|M05| D | D | **A** | E |  |  |  |  |  |  |  |  |  |
|M06| C | D | **A** | A | D |  |  |  |  |  |  |  |  |
|M07| C | C | E | D | E | C |  |  |  |  |  |  |  |
|M08| D | E | **A** | A | **A** | D | E |  |  |  |  |  |  |
|M09| **A** | **A** | C | D | D | D | C | C |  |  |  |  |  |
|M10| E | C | **A** | E | C | C | C | C | A |  |  |  |  |
|M11| C | C | C | C | C | C | C | C | C | C |  |  |  |
|M12| C | E | E | C | E | C | C | E | C | **A** | A |  |  |
|M13| D | C | D | D | E | D | D | **A** | D | D | C | E |  |
|M14| D | C | D | D | **A** | D | D | **A** | D | D | C | E | **A** |

**Ambiguous pairs explained:** M01/M02 (impulse vs retrace-then-resume — resolved §7/§8); M01/M03 & M03/M04 & M03/M06 & M03/M08 & M03/M10 (does the LEVEL/boundary supply the edge? → M03; else the other — §7/§10); M02/M04 (trend present? → M02; else M04 — §8); M05/M03 & M05/M08 (liquidity-pool hypothesis? → M05; value/reference? → M08; bare fakeout? → M03 — §9); M08/M04 (target next reference vs center); M09/M01 & M09/M02 (inter-scale RELATIONSHIP vs single-scale filter — §13); M10/M12 (single state-change vs ordered chain); M13/M14/M08 (FVG gap vs OB body vs horizontal memory level — §17/§18); M05/M14 (stop-pool vs supply zone).

## CLASSIFICATION CONSISTENCY TEST (§21) — 20 historical strategies
| # | strategy/hypothesis | PRIMARY | SECONDARY conditioners | why |
|---|---|---|---|---|
| 1 | **S5** NY opening-range breakout LONG | **M07** | M03 (breakout mechanic), M06 (session vol) | edge = NY opening-range STRUCTURE (R13: TOD alone −0.65, ORB +0.074) |
| 2 | **pullback3** (CAND-G0037) TREND_UP long | **M02** | M01 (trend context) | counter-move within a trend, resume |
| 3 | compression→continuation LONG (COMP-CONT) | **M03** | M06 (compression filter), M01 | boundary resolution supplies direction; vol is filter (§10) |
| 4 | 2σ range fade (S6) | **M04** | M10 (range-state) | fade to center, no trend |
| 5 | liquidity sweep reversal (CAND-0020) | **M05** | M10 (MK-01 swings) | stop-run at a pool + reclaim |
| 6 | failed-breakout fade (CR-12 / event_seq) | **M03** (fakeout) or **M12** if gated sequence | M05 if liquidity-pool hypothesis | bare failed break = M03; only a gated chain = M12 |
| 7 | opening-range families (Batch D session-range) | **M07** | M03 | session inheritance/opening structure (S5-redundant) |
| 8 | **CRS-1** historical (H4-up bounce fade short) | **M09** | M01 (H4 trend state), M10 (current-like regime) | edge hypothesized from H4×M15 divergence (now invalidated) |
| 9 | FVG-CE50 reaction (CAND-0003) | **M13** | M08 if at a level (confluence) | reaction at 3-bar imbalance on revisit |
| 10 | order-block rejection (CAND-0011) | **M14** | M05/M08 confluence | reaction at OB body on return |
| 11 | M5-1 (H1-down + M15-bounce + M5 down-break short) | **M02** | M09 (H1×M15), M5 execution | pullback-fade of a counter-trend bounce; M5 = execution (§11) |
| 12 | M5-2 (M15 breakout + M5 acceptance) | **M03** | M08 (acceptance), M5 execution | breakout continuation; acceptance conditioner |
| 13 | M5-3 (pullback-completion + M5-structural stop) | **M02** | M11 (path), M5 execution | same pullback, M5 stop = execution |
| 14 | M5-4 (coil-breakout + M5 displacement) | **M03** | M06 (compression), M5 execution | coil boundary resolution |
| 15 | PDH/PDL touch-reaction (CAND-0001) | **M08** | M07 (if session level) | reference-level acceptance/rejection |
| 16 | volatility dry-up → expansion (post-repair A) | **M06** | M03 (if traded directionally) | magnitude edge, non-directional |
| 17 | multi-TF momentum confluence (post-repair G) | **M09** | M01 | inter-scale agreement as edge (era-split) |
| 18 | episode-age / time-since-break (CR-7 / post-repair B) | **M11** | M10 (regime anchor) | duration-conditioned probability |
| 19 | session inheritance (post-repair E) | **M07** | M12 (sequence) | prior-session→next-session structure |
| 20 | BOS-retest (CAND-0021) / CHoCH (CAND-0022) | **M10** (CHoCH) / **M02** (BOS-retest) | M03 | character change vs retest-of-break |

## CEO DECISION TABLE (§22)
| MODULE | proposed def | boundary confidence | existing authority | CEO decision |
|---|---|---|---|---|
| M01 trend/continuation | proposed | HIGH | flowb momentum/continuation, MI trend | READY_TO_RATIFY |
| M02 pullback/retest | preserve+proposed | HIGH | flowb `pullback` | READY_TO_RATIFY |
| M03 breakout/expansion | preserve+proposed | HIGH | flowb `breakout`/`compression_breakout`, S5 | READY_TO_RATIFY |
| M04 range/mean-reversion | proposed | MED (vs M02/M06) | mstrat S6, RANGE_REGIME_V1 | CEO_ARBITRATION_REQUIRED (M02/M06 boundary) |
| M05 liquidity/sweep | proposed | MED (vs M03/M08) | MK-02 (ratified) | CEO_ARBITRATION_REQUIRED (§9 boundary) |
| M06 volatility/compression | proposed | HIGH | market_state (ratified), flowb | READY_TO_RATIFY |
| M07 session/opening-range | proposed | HIGH | S5, MK-04, MI session_behavior | READY_TO_RATIFY (confirm S5→M07) |
| M08 auction/reference | proposed (auction sub-concept NEW) | MED | MK-04 (ratified levels); auction UNDEFINED | CEO_ARBITRATION_REQUIRED (acceptance/value-migration def) |
| M09 cross-scale | proposed (new) | LOW-MED | none (CRS-1 invalidated) | CEO_ARBITRATION_REQUIRED (§13 def + boundary) |
| M10 market-state/transition | proposed | MED (vs M12) | MK-01, MODE_V1, vNext | CEO_ARBITRATION_REQUIRED (M12 boundary) |
| M11 path/hazard/survival | proposed (new) | MED | none | CEO_ARBITRATION_REQUIRED (ratify def) |
| M12 event sequencing | proposed (new) | MED (vs M10/M11) | none | CEO_ARBITRATION_REQUIRED (ratify def) |
| M13 imbalance/FVG | reconstructed+proposed | HIGH (primitive) | MK-03 (ratified) | READY_TO_RATIFY (confirm module status) |
| M14 order-block/S-D | reconstructed+proposed | MED (vs M05/M08) | Mod.5 (ratified) | CEO_ARBITRATION_REQUIRED (vs M05/M08) |

**STOP per §23** — no discovery activated. Awaiting CEO ratification / arbitration of the flagged modules before MODULAR_STRATEGY_DISCOVERY_PROGRAM_V1.

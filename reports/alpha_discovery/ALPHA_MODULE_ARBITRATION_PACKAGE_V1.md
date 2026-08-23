# ALPHA_MODULE_ARBITRATION_PACKAGE_V1 — 8 pending modules

Mandate: CEO_ARBITRATION (2026-08-23). Ratified already: M01/M02/M03/M06/M07/M13. This package covers ONLY the 8 pending:
M04, M05, M08, M09, M10, M11, M12, M14. Definition-only — NO discovery, NO P&L. Grounded in project primitives; no external ICT
doctrine. CEO_DECISION per module: **A** = ratify as written · **B** = ratify with a specified boundary change · **C** = redefine.

The unifying arbitration principle used throughout: **PRIMARY_MECHANISM_MODULE = the source of the EXPECTED EDGE**, provable
(where two modules could claim a hypothesis) by an INCREMENTAL-INFORMATION test — the claimed mechanism must add edge beyond the
competing module's simpler reading. Everything else is a CONDITIONER/TRIGGER/CONTEXT/EXECUTION.

---

## M04 — RANGE / MEAN REVERSION
- **PROPOSED ONE-SENTENCE DEFINITION:** The edge is an expected RETURN TOWARD value/center inside a NON-DIRECTIONAL (balanced) structure — fade an extreme back to the middle, with NO requirement of trend continuation.
- **CORE SOURCE OF EDGE:** mean-reversion of price to a range center when no directional regime dominates.
- **WHAT QUALIFIES:** fade at a range boundary / statistical extreme (2σ) targeting the mid, in a confirmed low-efficiency/balanced regime.
- **WHAT DOES NOT QUALIFY:** a counter-move within a trend expecting continuation (M02); a boundary BREAK (M03); an edge that is only a volatility STATE with no directional return hypothesis (M06).
- **PRIMARY BOUNDARY CONFLICT:** M02 (pullback) and M06 (volatility compression).
- **EXACT DISTINGUISHING RULE (§4 decisive test):** Ask what the edge return depends on. (1) If a DOMINANT DIRECTIONAL TREND exists on the trade scale AND the target is CONTINUATION of that trend after a counter-move → **M02**. (2) If NO dominant trend (balanced/low-efficiency regime) AND the target is the range CENTER/value → **M04**. (3) If the hypothesis is only that VOLATILITY is low/compressed (magnitude), with no return-to-center directional claim → **M06**. Decisive: *return-to-value in a non-directional structure (M04) vs continuation after a directional pullback (M02) vs a mere volatility state (M06).*
- **SUB-MECHANISM BRANCHES:** ├─ boundary-rejection fade ├─ statistical-extreme (nσ) reversion ├─ return-to-center/VWAP └─ range-rotation (boundary-to-boundary).
- **PROJECT EXAMPLE:** S6 2σ reversion; RANGE_REGIME_V1 RS-1 boundary fade.
- **ANTI-EXAMPLE:** pullback3 in an uptrend (M02).
- **CEO_DECISION:** ☐A ☐B ☐C

## M05 — LIQUIDITY / SWEEP / FAILED BREAK
- **PROPOSED ONE-SENTENCE DEFINITION:** The edge is a hypothesis that a LIQUIDITY POOL (resting stops at equal highs/lows or a swing extreme) is SWEPT (wick beyond + reclaim) to trigger stops, then price reverses because the move was a liquidity grab.
- **CORE SOURCE OF EDGE:** absorption/reversal after stop-liquidity beyond an obvious extreme is taken (MK-02 wick-sweep + reclaim).
- **WHAT QUALIFIES (§5 mechanical):** the hypothesis must reference a LIQUIDITY POOL = project-defined resting-stop cluster: equal highs/lows or a swing extreme (MK-01 Swing/Block; MK-02 pool), AND a SWEEP = a wick beyond the pool (`low[c]`/`high[c]` pierces) followed by a RECLAIM = close back inside within a bounded window.
- **WHAT DOES NOT QUALIFY (§5):** merely crossing a high/low; merely wicking a level; a failed breakout — NONE of these qualify WITHOUT the explicit pool+sweep+reclaim structure.
- **PRIMARY BOUNDARY CONFLICT:** M03 (failed breakout) and M08 (reference-level rejection).
- **EXACT DISTINGUISHING RULE (§5):** (1) Pool+wick-sweep+reclaim present and hypothesized as the cause → **M05**. (2) A boundary breakout that reverses with NO liquidity-pool claim → **M03 (fakeout)**. (3) A pierce+close-back at a prior-period MEMORY reference (PDH/PDL/session level) framed as acceptance/rejection → **M08**. Decisive: *M05 requires the liquidity-pool/stop-run hypothesis (sweep+reclaim at a pool); a bare fakeout is M03; a memory-level rejection is M08.* SWEEP=take-liquidity-then-reverse; FAILED BREAK=boundary rejected with no liquidity claim; REFERENCE REJECTION=rejection at a memory level (M08).
- **SUB-MECHANISM BRANCHES:** ├─ swing-pool sweep-reversal ├─ equal-highs/lows sweep ├─ session-extreme sweep └─ failed-break-with-liquidity fade.
- **PROJECT EXAMPLE:** CAND-0020 liquidity_sweep_reversal (MK-02); CAND-0032 persistent-session-sweep.
- **ANTI-EXAMPLE:** coil breakout that fails with no pool hypothesis (M03).
- **CEO_DECISION:** ☐A ☐B ☐C

## M08 — AUCTION / REFERENCE-LEVEL INTERACTION
- **PROPOSED ONE-SENTENCE DEFINITION:** The edge is price interacting with an economically-defined REFERENCE LEVEL (a prior-period horizontal price memory) classified causally as ACCEPTANCE (value migrates beyond) vs REJECTION (returns inside).
- **CORE SOURCE OF EDGE:** the market accepts (continuation to the next reference) or rejects (reversion) at a remembered level.
- **MECHANICAL/CAUSAL COMPONENT DEFINITIONS (§6, project-only; NO external market-profile discretion):**
  - **REFERENCE LEVEL** = a ratified prior-period horizontal memory: PDH/PDL (MK-04 institutional_reference_levels), prior/persistent session High/Low/Mid (MK-04 session_levels), prior-week levels. (These are the only project-authoritative reference primitives.)
  - **ACCEPTANCE** = K consecutive CLOSES beyond the level on the trade scale, evaluated at a POINT IN TIME with NO forward-window overlap with the outcome (the M5-2 circularity lesson).
  - **REJECTION** = the level is pierced (high/low beyond) but the bar/window CLOSES back inside = failed to accept.
  - **RECLAIM** = after acceptance beyond, a later close returns back across the level = acceptance failed → reversal.
  - **VALUE MIGRATION** = a sustained acceptance carrying traded value from one reference to the next (level→level).
  - **FAILED AUCTION** = rejection at a level following an attempt to accept beyond it.
- **WHAT QUALIFIES:** touch-rejection fade; break-acceptance continuation; value-migration between references; reclaim reversal.
- **WHAT DOES NOT QUALIFY:** a swing-pool stop-run (M05); a boundary break with no reference-memory hypothesis (M03); a range-center fade (M04).
- **PRIMARY BOUNDARY CONFLICT:** M03 (breakout) and M05 (liquidity sweep).
- **EXACT DISTINGUISHING RULE (§6):** M08 requires the interaction to be with a MEMORY REFERENCE LEVEL and to be classified as ACCEPTANCE/REJECTION. vs **M03**: a bare close-through with no reference-memory/acceptance hypothesis = M03; M08 adds the memory-level + acceptance classification. vs **M05**: M08 = value/acceptance at a memory level; M05 = stop-liquidity grab at a swing POOL (equal highs/lows). Decisive: *reference-memory + acceptance/rejection (M08) vs boundary resolution (M03) vs stop-pool sweep (M05).*
- **SUB-MECHANISM BRANCHES:** ├─ level touch-rejection ├─ level break-acceptance continuation ├─ value migration (level→level) └─ reclaim / failed-auction reversal.
- **PROJECT EXAMPLE:** CAND-0001 PDH-PDL (DEMO_BASELINE); CR-10 PDL/PDH; session-level touches (CAND-0027).
- **ANTI-EXAMPLE:** equal-highs sweep-and-reverse (M05).
- **CEO_DECISION:** ☐A ☐B ☐C

## M09 — CROSS-SCALE STRUCTURE
- **PROPOSED ONE-SENTENCE DEFINITION:** The edge is generated by the RELATIONSHIP — divergence (scales disagree) or confluence (scales agree) — between an INDEPENDENT higher-scale STATE and a lower-scale EVENT; NOT merely "uses multiple timeframes."
- **CORE SOURCE OF EDGE:** the inter-scale disagreement/agreement itself carries information beyond either scale alone.
- **WHAT QUALIFIES (§7):** e.g. H4-UP while M15-structure-DOWN (divergence → fade the lower-scale counter-move with the higher-scale flow); multi-scale confluence amplification — where the RELATIONSHIP is the hypothesized edge.
- **WHAT DOES NOT QUALIFY (§7):** H4 used as a mere directional FILTER for an M15 breakout ("take M15 breakouts only when H4 up") — PRIMARY stays **M03**; a single-scale MTF-EMA trend (M01).
- **PRIMARY BOUNDARY CONFLICT:** M03 (higher-TF-filtered breakout), M01/M02 (single-scale trend/pullback).
- **EXACT DISTINGUISHING RULE (§7, incremental-information test):** M09 is PRIMARY only if the cross-scale RELATIONSHIP adds edge BEYOND the lower-scale event conditioned on a simple same-direction higher-TF filter. Operationally: compare (lower-scale event | higher-TF-agrees-as-filter) vs (the specific divergence/confluence relationship); if the relationship — especially DISAGREEMENT — is where the edge lives, → **M09**; if a plain same-direction filter captures it, PRIMARY stays with the lower-scale event's module (M03/M01/M02). Causal alignment (fully-closed higher-TF, VE nominal-close) is mandatory.
- **SUB-MECHANISM BRANCHES:** ├─ cross-scale divergence-fade ├─ cross-scale confluence-amplification ├─ nested-structure alignment └─ higher-TF-state × lower-TF-event conditioning.
- **PROJECT EXAMPLE:** CRS-1 historical (H4-up bounce fade — later INVALIDATED as lookahead; still the archetypal M09 identity).
- **ANTI-EXAMPLE:** H4-trend-filtered M15 breakout (M03).
- **CEO_DECISION:** ☐A ☐B ☐C

## M10 — MARKET-STATE / STRUCTURAL TRANSITION
- **PROPOSED ONE-SENTENCE DEFINITION:** The edge arises from a CHANGE OF STATE (regime A → regime B) — trading the transition behavior at/near the change, not trading well inside an already-established state.
- **CORE SOURCE OF EDGE:** the characteristic move released at the moment a prior regime breaks and a new one begins (CHoCH / vol-regime shift / mode change).
- **WHAT QUALIFIES:** CHoCH (character change, MK-01) entries; range→expansion ignition; trend→range exhaustion; operating-mode change — TIMED TO the transition.
- **WHAT DOES NOT QUALIFY (§8):** trading well inside an established State B (in-trend pullback = M02; in-range fade = M04); an ordered multi-event chain (M12).
- **PRIMARY BOUNDARY CONFLICT:** M12 (event sequencing) and the established-state modules (M01/M04).
- **EXACT DISTINGUISHING RULE (§8):** M10 is PRIMARY iff the entry is TIMED TO the single STATE-CHANGE event (the CHoCH/mode-flip bar or its immediate confirmation) and the edge is the transition behavior; if entry is deep inside an already-established state (transition long past), PRIMARY = that state's module. vs **M12**: M10 = ONE state change (A→B); M12 = an ORDERED CHAIN of ≥2 distinct events with inter-event gates. Decisive: *edge from the CHANGE A→B (M10) vs edge from trading inside B (M01/M04) vs edge from an ordered multi-event sequence (M12).*
- **SUB-MECHANISM BRANCHES:** ├─ CHoCH character-change ├─ range→expansion ignition ├─ trend→range exhaustion └─ operating-mode/regime-onset transition.
- **PROJECT EXAMPLE:** CAND-0022 CHoCH-reversal (MK-01); RANGE_LIFECYCLE vNext transitions.
- **ANTI-EXAMPLE:** in-trend pullback3 (M02).
- **CEO_DECISION:** ☐A ☐B ☐C

## M11 — PATH / HAZARD / SURVIVAL
- **PROPOSED ONE-SENTENCE DEFINITION:** The edge is a PATH-DEPENDENT probability that changes with a CLOCK/AGE/DURATION/SURVIVAL variable or with EXCURSION ORDERING — the time/duration/ordering quantity itself is the signal, not merely the moment of entry.
- **CORE SOURCE OF EDGE:** hazard dynamics — forward P(continuation / reversal / target-before-stop) is non-constant and evolves with how long a state or move has persisted, or with adverse-first vs target-first ordering.
- **ROLE OF THE LISTED QUANTITIES (§9):** *time-since-event* & *duration* = the CLOCK/AGE (the conditioning variable); *survival* = persistence-without-invalidation to time t; *hazard* = instantaneous P(event at t | survived to t); *event ordering / MFE-MAE ordering / target-before-stop probability* = the PATH-outcome the hazard governs. The edge is expressed as: forward probability changes MATERIALLY with the clock/survival/ordering variable, holding the setup fixed.
- **WHAT QUALIFIES:** time-since-regime-entry / time-since-break / duration-in-compression / survival-without-invalidation conditioning; a strategy whose signal IS the age band or the adverse-first/target-first ordering shift.
- **WHAT DOES NOT QUALIFY (§9):** picking the best MOMENT to enter a fixed setup (ordinary entry timing = execution); a discrete ordered event chain (M12).
- **PRIMARY BOUNDARY CONFLICT:** ordinary entry timing (execution) and M12 (event sequencing).
- **EXACT DISTINGUISHING RULE (§9):** M11 is PRIMARY iff the CONDITIONING VARIABLE generating the edge is a continuous TIME/DURATION/SURVIVAL/ORDERING quantity (the age/hazard IS the signal). vs **entry-timing**: entry-timing optimizes WHEN to enter a fixed setup and is NOT a module (execution layer); M11 makes the elapsed-time/ordering the edge. vs **M12**: M11 = CONTINUOUS duration/hazard; M12 = DISCRETE ordered events. Decisive: *duration/hazard/ordering AS the edge (M11) vs choosing an entry moment (execution) vs an ordered event chain (M12).*
- **SUB-MECHANISM BRANCHES:** ├─ time-since-event hazard ├─ duration-in-state dependence ├─ survival-without-invalidation └─ adverse-first vs target-first (excursion) ordering dynamics.
- **PROJECT EXAMPLE:** CR-7 episode-age (causal); post-repair Frontier B time-since-break hazard.
- **ANTI-EXAMPLE:** M5 momentum-onset entry (execution timing, not a module).
- **CEO_DECISION:** ☐A ☐B ☐C

## M12 — EVENT SEQUENCING
- **PROPOSED ONE-SENTENCE DEFINITION:** The edge comes from an ORDERED SEQUENCE of ≥2 DISTINCT causal events (A → gate → B → …) whose ordered combination carries information that no single event provides alone.
- **CORE SOURCE OF EDGE:** conditional path — event B's meaning depends on A having occurred and passed an explicit acceptance/failure gate.
- **MINIMUM REQUIREMENT FOR A GENUINE SEQUENCE (§10):** (a) ≥2 DISTINCT ordered events (each a qualifying event of some module), (b) an explicit acceptance/failure GATE between consecutive events, AND (c) the sequence's edge EXCEEDS the best single component event alone (incremental test). Failing (c) → it is a single-event setup with filters, not M12.
- **WHAT QUALIFIES:** compression → attempted breakout → failed acceptance → opposite displacement; sweep → reclaim → retest → hold.
- **WHAT DOES NOT QUALIFY (§10):** a single-event setup; a single state transition (M10); a folded single retest (M03 bos_retest); a set of SIMULTANEOUS filters (multi-filter strategy, not ordered).
- **PRIMARY BOUNDARY CONFLICT:** M10 (transition), M11 (path/hazard), and multi-filter strategies.
- **EXACT DISTINGUISHING RULE (§10):** M12 is PRIMARY iff there is an ORDERED chain of ≥2 distinct events with inter-event gates whose combined edge beats the best single event. vs **M10**: one state-change event ≠ a sequence. vs **M11**: ordered DISCRETE events ≠ continuous duration/hazard. vs **multi-filter**: filters are simultaneous conditions on one event; a sequence is temporally ORDERED with gates. Decisive: *ordered ≥2-event gated chain with incremental edge (M12) vs single transition (M10) vs duration/hazard (M11) vs simultaneous filters.*
- **SUB-MECHANISM BRANCHES:** ├─ compression→break→fail→reverse ├─ sweep→reclaim→retest→hold ├─ break→retest→continuation └─ multi-leg structural narrative.
- **PROJECT EXAMPLE:** post-repair Frontier C compression→failed-break→response.
- **ANTI-EXAMPLE:** single coil-breakout (M03).
- **CEO_DECISION:** ☐A ☐B ☐C

## M14 — ORDER-BLOCK / SUPPLY-DEMAND
- **PROJECT PRIMITIVE (Mod.5, RATIFIED — used verbatim, §11):** an Order Block = the geometric BODY `[min(Close,Open), max(Close,Open)]` of the last OPPOSITE-direction bar immediately before an impulse (no volume). Interactions: Breaker / Mitigation / Rejection. (No external/ICT doctrine imported.)
- **PROPOSED ONE-SENTENCE DEFINITION:** The edge is price REACTING at an unmitigated order-block body (the origin bar of an impulse) on RETURN — rejection/mitigation from that supply/demand zone.
- **CORE SOURCE OF EDGE:** the origin candle of a displacement marks unfilled institutional interest; price returning to that specific body reacts.
- **WHAT MAKES THE OB THE EDGE SOURCE (§11):** the hypothesis is a reaction specifically at the Mod.5 OB BODY (origin bar before the impulse) on first return, before it is mitigated/consumed (D7) — the zone's ORIGIN is the causal claim, not a generic level.
- **WHAT DOES NOT QUALIFY:** a 3-bar FVG gap (M13); a prior-period horizontal memory level (M08); a stop-pool sweep (M05); a generic MA/structure retrace (M02).
- **PRIMARY BOUNDARY CONFLICT:** M08 (reference level), M05 (liquidity), M02 (pullback/retest).
- **EXACT DISTINGUISHING RULE (§11):** M14 is PRIMARY iff the reacting zone is specifically the Mod.5 OB body (origin-of-impulse bar) and the edge is the return-and-react at that zone. vs **M08**: OB is a DYNAMIC zone from a specific origin bar's body, not a prior-period horizontal reference memory. vs **M05**: OB is a supply/demand-origin reaction, not a stop-run at a liquidity pool. vs **M02**: OB-return may resemble a pullback, but M14 requires the specific OB body as the edge source, not a generic MA/structure retrace. Decisive: *reaction at the impulse-origin body (M14) vs memory level (M08) vs stop pool (M05) vs generic retrace (M02).*
- **SUB-MECHANISM BRANCHES:** ├─ OB rejection ├─ OB mitigation / breaker flip ├─ demand/supply-zone re-entry └─ liquidity-void reaction.
- **PROJECT EXAMPLE:** CAND-0011 OB-rejection; CAND-0014 OB-mitigation (Mod.5).
- **ANTI-EXAMPLE:** FVG-CE50 reaction (M13); PDH rejection (M08).
- **CEO_DECISION:** ☐A ☐B ☐C

---

## Cross-cutting arbitration decisions summarized (for quick CEO sign-off)
1. **M04 vs M02 vs M06:** trend+continuation→M02 · balanced+return-to-center→M04 · magnitude-only→M06.
2. **M05 vs M03 vs M08:** pool+sweep+reclaim→M05 · bare fakeout→M03 · memory-level acceptance/rejection→M08.
3. **M08 acceptance suite:** reference level (MK-04 PDH/PDL/session), acceptance=K causal closes-beyond (no forward overlap), rejection=pierce+close-back, reclaim=return across after acceptance, value-migration=level→level, failed-auction=rejection after attempted acceptance.
4. **M09:** primary ONLY if the inter-scale RELATIONSHIP (esp. divergence) adds edge beyond a same-direction higher-TF filter; else the lower-scale event's module.
5. **M10 vs M12:** single state-change→M10 · ordered ≥2-event gated chain→M12.
6. **M11 vs entry-timing vs M12:** continuous duration/hazard/ordering AS edge→M11 · choosing an entry moment→execution (not a module) · discrete ordered events→M12.
7. **M12 minimum:** ≥2 ordered distinct events + inter-event gate + beats best single component.
8. **M14 vs M08/M05/M02:** reaction at the Mod.5 impulse-origin OB body→M14 · memory level→M08 · stop pool→M05 · generic retrace→M02.

**STOP per §12** — no discovery activated; the six ratified modules untouched. Awaiting CEO A/B/C decisions on M04, M05, M08, M09, M10, M11, M12, M14.

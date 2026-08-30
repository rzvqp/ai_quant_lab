# ALPHA_DISCOVERY_FACTORY_V2_REPORT — cycle 1

One complete Discovery Factory cycle: behavior atlas → negative-knowledge base → contrast mining → 20 raw hypotheses → dedup →
falsify 3 distinct. Deliverables: ALPHA_NEGATIVE_KNOWLEDGE_BASE_V1, GOLD_BEHAVIOR_ATLAS_V1, ALPHA_CONTRAST_MINER_REPORT_V1,
ALPHA_HYPOTHESIS_REGISTER_V2, this report. **0 new candidates.** S5 untouched; holdout unopened; no mining; canonical costs.

## §20 Discovery scoreboard
RAW_HYPOTHESES_GENERATED=20 · DEDUPED_HYPOTHESES=3 · HYPOTHESES_TESTED=3 · FALSIFIED=3 · INSUFFICIENT_EVIDENCE=0 ·
SURVIVED_INTERNAL_FALSIFICATION=0 · ALPHA_CANDIDATES_UNVALIDATED=0. NEW_ECONOMIC_MECHANISMS_TESTED=3 (failed-break fade / sweep-reverse /
structural-target-break) + the contrast-discriminator search over 8 ex-ante features. BEHAVIOR_EVENT_FAMILIES_MAPPED=12 ·
NEGATIVE_FAMILIES_INDEXED=16.

## §15 Contrast requirement — result
No cost-surviving ex-ante discriminator exists for structural breaks (every feature bin net-negative; HTF-align/discount are the
strongest but insufficient). **The information that separates winners from losers is not in price-derived ex-ante features** — it is
observable only AFTER entry (redundant momentum) or is orthogonal to price (order flow / positioning / real-yield regime).

## §22 MOST PROMISING SOURCE OF NEW XAUUSD EDGE (evidence-ranked)
1. **EXOGENOUS_INFORMATION** — highest. Price-only DIRECTION is provably efficient across 5 frontiers/all representations; the one axis
   that added *stable* incremental information was exogenous (DXY-NDX1). The DIRECTIONAL signal price lacks must come from outside price:
   **real yields** (the deeper stable driver DXY only reflects), order flow / positioning (COT, options), or auction/volume microstructure.
2. **SESSION_SPECIALIZATION** — the ONLY validated edge (S5) is a session-timed structural break. A *second* session-timed mechanism is
   the most plausible price-only avenue, but generic session ORBs already failed — it would need a specific liquidity/time structure, not
   a parameter variant.
3. **REGIME_SPECIALIZATION** — regime-gating did not beat direction-efficiency (R20), BUT a genuine regime *detector* built from the
   exogenous regime variable (real yields / inflation state) could gate a specialist. Depends on (1).
4–11 (LOW, exhausted): ENTRY_SELECTION, FAILED_BREAK/RECLAIM, STRUCTURAL_LOCATION, TARGET_SPACE, VOLATILITY_PATH, EVENT_CONDITIONING,
   MANAGEMENT — all falsified or information-only this cycle and prior.

## §19 DATA_NEED_CANDIDATE (highest priority)
- HYPOTHESIS_ID: DXY-NDX1 successor / direction-resolution. **MISSING_DATA: real yields (US 10y TIPS / real-rate series, H1 or daily).**
  WHY_REQUIRED: DXY→gold direction is regime-conditional because both are reduced-forms of the real-yield/monetary regime; real yields
  are the candidate STABLE direction driver. WHAT_IT_ADDS: a causally-available regime/direction variable price cannot supply.
  WHY_EXISTING_DATA_CANNOT: price-only direction efficient (this cycle + 5 frontiers); DXY carries only regime-conditional (inverting)
  direction. EXPECTED_INFORMATION_GAIN: the one plausible stable DIRECTION resolver. COST_COMPLEXITY: governed daily/H1 real-yield series
  + causal aligner (same discipline as the ratified DXY contract). Secondary: order-flow / options-positioning (COT, 25-delta risk-reversal).

## §23 WHAT SHOULD THE LAB DO DIFFERENTLY (honest, not a defense of the old method)
The lab's falsification/governance/causality machinery is world-class — that is NOT the bottleneck. The bottleneck is that **the search
space has been price-only M15 direction, which is efficient**, so every method (taxonomy, blind-forward, chronological, morphology,
contrast) keeps re-deriving the same negative. Continuing to generate more price-only directional hypotheses has near-zero expected value.
Concretely, change three things:
1. **Stop searching for another price-only M15 directional specialist.** Five frontiers + this contrast cycle establish direction
   efficiency beyond reasonable doubt. Re-testing price representations is confirmation, not discovery.
2. **Reorient discovery toward ORTHOGONAL DIRECTIONAL INFORMATION** (real yields first, then order-flow/positioning). The proven pattern:
   the only new stable signal came from an exogenous axis. Discovery should be *data-acquisition-led*, not representation-led.
3. **Operationalize the 5 non-directional information assets** (VOLTIME-1, DXY-NDX1, SF-3, VOLPATH-geometry, session-whipsaw) as a
   RISK / SIZING / NO-TRADE / timing layer AROUND S5 — a real deliverable that does not require a new directional edge. E.g., SF-3's
   whipsaw map and VOLTIME-1's expansion-timing can improve *when* and *how large* S5 (or any future edge) is deployed.
The Contrast Miner is the right engine; it just needs *orthogonal features* (exogenous), because price features carry no ex-ante
discriminator. This is the fundamental finding of cycle 1.

## §25 FINAL CEO REPORT
```
ALPHA_DISCOVERY_FACTORY_V2_COMPLETE = YES
BEHAVIOR_EVENT_FAMILIES_MAPPED = 12
NEGATIVE_FAMILIES_INDEXED = 16
RAW_HYPOTHESES_GENERATED = 20
DEDUPED_HYPOTHESES = 3
HYPOTHESES_ACTUALLY_TESTED = 3
FALSIFIED = 3
INSUFFICIENT_EVIDENCE = 0
SURVIVED_INTERNAL_FALSIFICATION = 0
NEW_STRATEGY_CANDIDATES = 0
CANDIDATE_IDS = none
BEST_CANDIDATE = none (H1 least-bad at netR -0.256, still FALSIFIED)
BEST_CANDIDATE_NET_EXPECTANCY = -0.256R (FALSIFIED, not a candidate)
BEST_CANDIDATE_N = 21379
BEST_CANDIDATE_REGIME_SCOPE = n/a
BEST_CANDIDATE_SESSION_SCOPE = n/a
BEST_CANDIDATE_DIRECTION = n/a
ONE_TRADE_DEPENDENT = NO (robustly negative)
CROSS_ERA_STABLE = YES (stably negative)
COST_ROBUST = n/a (no positive candidate)
CONTRAST_DISCRIMINATOR_FOUND = NO
BEST_DISCRIMINATOR = HTF-alignment (+0.11 relative, still net-negative -0.379)
NEW_DATA_REQUIRED = YES
HIGHEST_PRIORITY_DATA_NEED = real yields (US 10y TIPS/real-rate), governed H1/daily + causal aligner
MOST_PROMISING_EDGE_SOURCE = EXOGENOUS_INFORMATION (real yields), then SESSION_SPECIALIZATION
ALPHA_RECOMMENDED_NEXT_DIRECTION = data-acquisition-led exogenous direction research (real yields) + operationalize the 5 non-directional info assets as a risk/sizing layer around S5; STOP price-only M15 directional search
CANDIDATE_READY_FOR_INDEPENDENT_HANDOFF = NO
HANDOFF_CANDIDATE_IDS = none
S5_UNTOUCHED = YES
TERMINAL_HOLDOUT_OPENED = NO
AI_TRADER_Q4_TOUCHED = NO
EXECUTION_CHANGED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

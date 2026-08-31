# TEMPORAL_SEQUENCE_MINING_V1_REPORT — final

One complete bounded cycle: atlas → matched-state contrast → 15 raw hypotheses → dedup 5 → test 5 → falsify. **0 new candidates.**
Governed OANDA XAUUSD M15 UTC only. S5 untouched; holdout unopened; no external data; no GC/real-yield research; no ML. Positive control
validated the pipeline has power. Artifacts: `XAU_TEMPORAL_SEQUENCE_ATLAS_V1.md`, `TEMPORAL_SEQUENCE_CONTRAST_REPORT_V1.md`,
`TEMPORAL_SEQUENCE_HYPOTHESIS_REGISTER_V1.md`, code `tsm_core/contrast/sweep/falsify/ordermotif.py`.

## §23 CEO strategic question — answered
> **"Does the path into an XAU setup contain materially useful directional information beyond what is observable in the final setup state?"**

**NO.** Across every causal test — within-state-cell path-motif spreads, sequence lengths L∈{8,16,32,64}, two distinct anchor families
(RANGE_EDGE, VOL_TRANS), and all 19 populated 3-segment ordered-trajectory classes — the directional outcome P(up-first) stays pinned at
~0.50 and continuation stays ~0.51. The single column that *does* separate outcome is the future-return positive control (+0.563),
proving the test would detect path information if it existed. Temporal ORDER is efficient, not just static state.

> **"If yes, is that information strong enough to monetize after costs?"**

**N/A / NO.** There is no causal directional information to monetize. Every one of the 5 distinct mechanisms, mechanized as a simple
2R:1R continuation trade after the canonical 0.24R cost, nets **negative** — and the "cleanest-path" motifs net *worse* than the
driftless null (−0.68…−0.75 vs −0.24), because a directionally-clean approach selects already-spent moves.

## §24 SCOREBOARD
```
SEQUENCES_ANALYZED = 45,106 anchor-sequences (RANGE_EDGE 38,200 + VOL_TRANS 6,906; ×4 lengths in the sweep)
INDEPENDENT_EPISODES = 13,241 (RANGE_EDGE 8,756 + VOL_TRANS 4,485, H=32)

RAW_HYPOTHESES = 15
DEDUPED_HYPOTHESES = 5
TESTED_HYPOTHESES = 5

FALSIFIED = 5
INFORMATIONAL_ONLY = 0
INSUFFICIENT = 0
SURVIVED = 0

SEQUENCE_INCREMENTAL_INFORMATION_FOUND = NO

BEST_SEQUENCE_MOTIF = VOL_TRANS argH_continue (largest in-sample within-cell shift)
BASELINE_OUTCOME_RATE = P(up) 0.5080 / P(continue) 0.5056
SEQUENCE_CONDITIONAL_OUTCOME_RATE = +0.042 (in-sample, single-L, VOL_TRANS) ; <0.02 & sign-unstable on the clean RANGE_EDGE anchor
INCREMENTAL_EFFECT = ~0.00 causal (positive control +0.563 = future leakage, confirms power)

NEW_STRATEGY_CANDIDATES = 0
CANDIDATE_IDS = none

BEST_CANDIDATE = none (least-bad monetized = VT.net_r net-R -0.223, still FALSIFIED, ≈ driftless null -0.24)
BEST_CANDIDATE_N = n/a
BEST_CANDIDATE_INDEPENDENT_EPISODES = n/a
BEST_CANDIDATE_NET_EXPECTANCY = -0.223R (FALSIFIED)
BEST_CANDIDATE_SESSION = n/a
BEST_CANDIDATE_DIRECTION = n/a

CROSS_ERA_STABLE = YES (stably negative across D/C/O and DEV/OOS)
COST_ROBUST = n/a (no positive candidate)
ONE_EPISODE_DEPENDENT = NO (independent-episode net-R ≈ raw; best-episode removal changes nothing)
```

## §25 COMPANY PROTECTION
```
S5_UNTOUCHED = YES
AI_TRADER_Q4_TOUCHED = NO
CSV_REPLAY_PROJECT_TOUCHED = NO
GC_RESEARCH_REOPENED = NO
REAL_YIELD_RESEARCH_STARTED = NO
TERMINAL_HOLDOUT_OPENED = NO
EXECUTION_CHANGED = NO
```

## §21 Family closure + ranking of remaining distinct discovery spaces
**TEMPORAL_SEQUENCE family is CLOSED (negative).** The path/order axis joins the five prior frontiers in confirming the meta-finding
(now extended to trajectory order). Adding this to `ALPHA_NEGATIVE_KNOWLEDGE_BASE_V1`. Do NOT start endless motif generation.

Genuinely distinct strategy-discovery spaces still open, ranked by evidence-weighted expected value (NOT started — §26):
1. **H1/H4_SETUP_WITH_M5_EXECUTION** — the economic-profile directive's native design (HTF edge + M5 causal trigger), under-explored at
   that resolution; S5 (the sole edge) is itself HTF-context + session + structure, making HTF-context specialization the most plausible
   *price-only* remaining avenue. Requires no new data (native M5 exists, 2021-07-27+).
2. **SESSION_SPECIALIST_FACTORY** — S5 proves a session-timed structural specialist can exist; a *second*, differently-structured session
   mechanism is the next-most-plausible price-only edge. SF-3 whipsaw map already supplies a NO-TRADE overlay.
3. **EXOGENOUS_INFORMATION (real yields)** — the standing #1 for *direction* (the one axis that ever added stable info via DXY-NDX1);
   currently scoped out by CEO, blocked on a governed real-rate series.
4. **CROSS_MARKET_RELATIVE_RESPONSE** — cross-market info demonstrably exists (DXY-NDX1) but was info-only; real-yields subsumes its
   directional part.
5. **GC_FUTURES_WITH_PROPER_DATA** — blocked on data (concluded this week; needs governed multi-year GC dataset).

## Why the lab keeps landing here (honest)
Six frontiers + two contrast cycles (static features, now temporal order) all re-derive: **XAUUSD M15 direction is efficient in price**.
The falsification machinery is not the bottleneck; the *search space* is. The single validated edge (S5) is a narrow HTF-context +
session + structure specialist that self-supplies direction. The highest-value remaining price-only avenue is **specialization**
(HTF/session context), not another representation of M15 direction. The highest-value directional avenue overall remains **exogenous**
(real yields) — repeatedly the only source of stable incremental information.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED

# H1_H4_SETUP_M5_EXECUTION_V1_REPORT — final

One bounded cycle: data audit → H4/H1 setup atlas → 15 raw hypotheses → dedup 4 distinct → baseline tests → M5 comparison → falsification.
**0 new candidates.** Governed OANDA XAUUSD (M15 full history + native M5 2021+). S5 untouched; holdout unopened; no GC/real-yield research;
no synthesized M5. Code: `htf_core/setups/atlas/diag/m5.py`. Docs: atlas, contrast report, hypothesis register (this = final report).

## §28 CEO questions — answered
1. **"Does selecting XAU setups from H4/H1 context produce directional/tradeable information the previous M15-centric research did not?"**
   **NO.** The H4-context filter (HTF_ON) changes net-R by <0.02R vs no filter (HTF_OFF) across all four families — and *hurts* the best
   one. Every positive cell is direction×era (long-in-bull / short-in-bear), present with or without HTF selection, and sign-reverses
   across eras = the known R20 era-trend artifact. HTF context does not create a cross-era-stable asymmetry.
2. **"Does M5 actually improve execution, or merely add noise/complexity?"** **Adds noise.** A causal M5-pullback entry on TGT_BREAK
   signals (native 2021+) misses **87%** of signals — structurally counterproductive for a breakout thesis — and distorts risk. No clean
   improvement in MAE/R-efficiency without abandoning the higher-timeframe idea.
3. **"Are surviving opportunities large enough to justify the strategy's operational complexity?"** **NO.** The only positive cell is
   bull-era beta; ~50-pip MFE moves are economically meaningful in size, but with no cross-era-stable entry edge the complexity of a
   three-timeframe stack is not justified.

## §29 SCOREBOARD
```
H1_H4_SETUP_M5_EXECUTION_V1_COMPLETE = YES

DATA_RANGE_USED = M15 2011-07-26 → 2026-07-27 (full) ; M5 native 2021-07-27 → 2026-07-27
M5_NATIVE_RANGE = 2021-07-27 → 2026-07-27 (354,669 bars, 1,555 days)

RAW_HYPOTHESES = 15
DEDUPED_HYPOTHESES = 4
TESTED_HYPOTHESES = 4

FALSIFIED = 4
INFORMATIONAL_ONLY = 0
INSUFFICIENT = 0
SURVIVED = 0

HTF_INCREMENTAL_INFORMATION_FOUND = NO
M15_INCREMENTAL_INFORMATION_FOUND = NO
M5_EXECUTION_VALUE_FOUND = NO

NEW_STRATEGY_CANDIDATES = 0
CANDIDATE_IDS = none

BEST_CANDIDATE = TGT_BREAK LONG (O-era) — candidate-shaped but FAILS cross-era gate (R20 era-trend artifact), NOT promoted
BEST_CANDIDATE_N = 47 (O-era long) / 460 (all)
BEST_CANDIDATE_INDEPENDENT_H4_EPISODES = ~40 (O-era) / 394 (all)
BEST_CANDIDATE_INDEPENDENT_H1_SETUPS = ~40 (O-era)

BEST_CANDIDATE_NET_EXPECTANCY = +0.349R (O-era only; −0.179R in D → sign-reverses; −0.023R pooled)
BEST_CANDIDATE_WIN_RATE = 0.596 (O-era) / 0.454 (all)
BEST_CANDIDATE_PF = ~1.4 (O-era only; <1 pooled)
BEST_CANDIDATE_MAX_DD = n/a (not a promotable candidate)

BEST_CANDIDATE_MEDIAN_MFE_PIPS = ~50
BEST_CANDIDATE_MEDIAN_MAE_PIPS = ~ -20 (structural)
BEST_CANDIDATE_MEDIAN_CAPTURED_PIPS = ~ -9 pooled / positive O-era
BEST_CANDIDATE_MEDIAN_HOLD = 64 M15 bars (~16h)

BEST_CANDIDATE_SESSION = NY (O-era concentration)
BEST_CANDIDATE_DIRECTION = LONG
BEST_CANDIDATE_H4_CONTEXT = TREND_UP / BALANCE with open target space
BEST_CANDIDATE_H1_SETUP = swing-extreme break with room>1 H4-ATR
BEST_CANDIDATE_M5_EXECUTION = none (M5 refinement HARMFUL, 87% miss)

M5_VALUE_CLASSIFICATION = HARMFUL (breakout thesis) / N/A (no baseline survivor)

CROSS_ERA_STABLE = NO
COST_ROBUST = partial (survives price-cost in O-era only; fails cross-era)
ONE_EPISODE_DEPENDENT = borderline (O-era N=47; not promoted regardless)

ANSWER_HTF_ADDS_EDGE = NO (HTF_ON ≈ HTF_OFF; only era-trend cells positive; sign-reverses across eras)
ANSWER_M5_ADDS_VALUE = NO (pullback entry misses 87% of breakout signals; no clean MAE/R improvement)
ANSWER_MOVE_SIZE_JUSTIFIES_COMPLEXITY = NO (only positive cell is bull-era beta; no stable entry edge)

MOST_PROMISING_NEXT_DIRECTION = SESSION_SPECIALIST_FACTORY (S5-adjacent structural specialist) or EXOGENOUS real yields (directional)
ALPHA_RECOMMENDED_NEXT_ACTION = stop price-only HTF directional search; the recurring positive-cell = era-trend confirms DIRECTION is
  exogenous. Pursue a session-specialist factory (structural, S5-shaped) OR the standing exogenous real-yields need (CEO-gated). Do not
  auto-start; CEO decides.

S5_UNTOUCHED = YES
AI_TRADER_Q4_TOUCHED = NO
CSV_REPLAY_PROJECT_TOUCHED = NO
GC_RESEARCH_REOPENED = NO
REAL_YIELD_RESEARCH_STARTED = NO
TERMINAL_HOLDOUT_OPENED = NO
EXECUTION_CHANGED = NO

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## §26 Family closure + ranking of remaining distinct spaces
**H1_H4_SETUP family CLOSED (negative).** Adds to `ALPHA_NEGATIVE_KNOWLEDGE_BASE_V1`. The #1-ranked space from the TSM closure is now
tested: HTF selection does not rescue M15 direction-efficiency. Remaining genuinely-distinct spaces (NOT started, per §30):
1. **SESSION_SPECIALIST_FACTORY** — S5 (the sole validated edge) is a session-timed structural specialist; a *second* differently-
   structured session mechanism is the most plausible remaining price-only avenue. No new data.
2. **EXOGENOUS_INFORMATION (real yields)** — the standing #1 for *direction*; every frontier keeps re-deriving that the missing signal is
   directional and exogenous. CEO-scoped-out to date.
3. **CROSS_MARKET_RELATIVE_RESPONSE** — cross-market info exists (DXY-NDX1) but was info-only.
4. **GC_FUTURES_WITH_PROPER_DATA** — blocked on a governed multi-year dataset.

## Honest note
The best cell this cycle (TGT_BREAK LONG, O-era, beats bull-beta by +0.26R within O) is the closest a price-only setup has come to an
edge — but it exists only in the parabolic-bull era and reverses in the bear era. That is not a bug in the method; it is the finding:
**price-only XAU direction is era-trend, and HTF context selection inherits that property rather than escaping it.** The one validated
edge (S5) escapes it only by being a narrow session+structure specialist that self-supplies direction — which is why SESSION_SPECIALIST
is the highest-value price-only avenue left.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED

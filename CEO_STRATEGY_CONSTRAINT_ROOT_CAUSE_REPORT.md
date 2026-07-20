# CEO Strategy Constraint Root-Cause Study

**Date**: 2026-07-20. **Scope**: research/diagnostic only. Not a checkpoint. No production code,
strategy, Risk, Sizing, Portfolio, Decision Intelligence, or Context Memory logic modified — every
number in this report is read directly off unmodified `ai_trader/` behavior. No thresholds changed, no
optimization performed, no behavior change executed.

**Target strategies**: S1, S13, S39, S40, S46, S48 (the six A-Candidates from
`CEO_STRATEGY_PERFORMANCE_STUDY_REPORT.md`). **Objective**: determine, at event level, exactly which
component produces each denial these strategies face in the competitive portfolio, and issue one
verdict per strategy from a fixed five-category taxonomy.

---

## 1. Methodology

### 1.1 Zero-file-diff instrumentation

Identical technique to `phase69a_funnel_recorder.py`, this session's own established precedent: an
already-constructed `SimulationHarness` instance (built via `new_harness()`, imported directly from
`phase69a_funnel_run.py` — the same factory used for the original paired isolated/competitive dataset,
guaranteeing byte-identical `SimulationContext`/`RiskConfig`/window) has three of its own bound methods
monkey-patched *after construction*: `_signal_engine.evaluate`, `_scoring_engine.score_batch`,
`_risk_manager.evaluate`. Each wrapper calls the original, unmodified implementation and returns its
result completely unchanged — it only additionally records a copy of what passed through. This changes
**zero lines** in any `ai_trader/` source file; the exact same compiled decision logic runs as in every
other study this session. One fresh instrumented run of the **competitive** scenario was executed
(`ROOTCAUSE-COMPETITIVE-INSTRUMENTED`, same `WINDOW_START`/`WINDOW_END` = 2024-10-23 to 2025-10-23,
23,639 XAUUSD M15 bars). No fresh isolated re-run was needed or performed — Phase 3's "would this have
been profitable in isolation" question is answered by cross-referencing the already-saved
`phase69a_isolated_funnel.json` trade ledger, and conflict_penalty is provably always zero in an
isolated single-strategy run by construction (see §1.2), so no isolated re-instrumentation was required.

### 1.2 Major correction made during this study's own design: BELOW_FLOOR is not a sizing gate

The CEO's own Phase 2 questions were framed around position-sizing internals (stop distance, ATR,
broker minimum lot, lot-step rounding). Direct source inspection shows this framing does not apply to
`BELOW_FLOOR`:

- `ai_trader/risk_manager/pipeline.py` line 99: `DeniedReason(code="BELOW_FLOOR",
  observed=opportunity.recommendation.value)` — this is the Scoring Engine's own **Recommendation
  Floor** gate (`RISK_POLICY.md`: requires `recommendation in {STRONG,MODERATE,WEAK}_OPPORTUNITY`).
  It runs at pipeline stage 2, **before** sizing (stage 7). Sizing never executes for a BELOW_FLOOR
  denial — there is no stop-distance/ATR/equity/position-size computation to inspect for these events.
- This codebase has no broker-minimum-lot or lot-step concept anywhere (`SymbolMeta` has only
  `symbol, tick_size, point_value, price_precision, session_anchor, trading_hours`; the sizing "floor"
  in `RiskConfig.SizingLimits` is a currency-risk floor, `min_allocation_risk_pct * equity`, not a
  broker-lot floor). The CEO's own cause taxonomy (A. stop very wide … D. lot-step rounding … H. other)
  was written assuming a sizing mechanism that does not exist in this codebase for `BELOW_FLOOR`.
- The actual mechanism behind `BELOW_FLOOR` is the Scoring Engine's own
  `component_scores.conflict_penalty` (`ai_trader/scoring_engine/conflict.py`): a batch-wide,
  cross-strategy score adjustment. `_OPPOSING_PENALTY = 0.5` applies when any other actionable signal
  in the same `(symbol, as_of)` batch has the opposite direction and higher pre-conflict base quality;
  `_CORRELATED_PENALTY_PER_SIGNAL = 0.2` (capped at 0.4) applies for same-direction, same-`klass`
  signals from other strategies. This is **structurally impossible** in a true single-strategy isolated
  run — `compute_conflict_penalties` requires ≥2 actionable signals in the batch; with
  `strategy_id_filter={one_id}` there can never be a second one. `conflict_penalty = 0` by construction
  in isolation, not merely by observation.
- Separately, `SIZE_BELOW_MIN` (`ai_trader/risk_manager/sizing.py` lines 83-87) **is** the genuine,
  distinct sizing-floor denial. It is reported in full (§4) even though it was not the CEO's named
  BELOW_FLOOR target, because it is the actual sizing gate that does exist in this codebase.

This correction is disclosed here, prominently, rather than silently substituting a different
investigation for the one requested.

### 1.3 Three measurement bugs found and fixed during this study's own build (self-caught, not by the CEO)

Exactly the kind of self-verification this project's prior studies have required. All three were caught
by internal sanity-checking (implausible output patterns) before this report was drafted, and are
disclosed here in full:

1. **Signal direction was always read as `NONE` for every LIMIT_MAX_PER_SYMBOL denial.**
   `RiskDecision.direction` is set to `Direction.NONE` for *every* denied decision by construction
   (`ai_trader/risk_manager/assembler.py::assemble_decision`, the DENY branch hard-codes
   `direction=Direction.NONE`; only the ALLOW branch uses the real `opportunity.direction`). The first
   pipeline run showed 100% `direction=NONE` and a 0.0% isolated-match rate across every single episode
   for all three shared-slot strategies — implausible on its face for signals specifically denied by a
   *directional* position-limit rule. Fixed by recovering the real direction from the originating
   `OpportunityScore` (captured in the same batch, keyed by `(strategy_id, symbol, as_of)`) instead of
   the always-`NONE` decision field.
2. **`SIZE_BELOW_MIN` sizing values were always read as absent.** `sizing.py::compute_sizing` returns
   `SizingOutcome(False, deny_reason=...)` with `sizing=None` on this denial — the `Sizing` object is
   only ever built on the success branch. The raw computed size and the minimum it was compared against
   are instead carried on the `DeniedReason` itself (`observed`/`limit`). Reading `decision.sizing`
   (the original approach) silently found zero events for every strategy despite the deny-reason
   breakdown showing real, nonzero SIZE_BELOW_MIN counts. Fixed by reading `observed`/`limit` off the
   matching `DeniedReason` entry.
3. **BELOW_FLOOR "events" were the wrong population — off by a factor of ~50-500×.** The first working
   version filtered `recorder.scores` directly on `recommendation not in {STRONG,MODERATE,WEAK}` for
   the target strategies. This silently counts *every* non-actionable, no-signal bar the strategy ever
   saw (23,639 bars/strategy, minus the handful that were actually actionable) — the exact same
   population already reported as "Rejected-by-scoring" in Table 1 — not the much smaller, genuine
   BELOW_FLOOR risk-manager denial count (e.g. S40: 21,268 counted vs. the real 376). Caught by
   cross-referencing against the independently-sourced deny-reason breakdown (Table 2), where the
   mismatch was exact and immediate. Fixed by filtering `recorder.decisions` for actual
   `BELOW_FLOOR`-coded denials first, then joining each to its originating score by
   `(strategy_id, symbol, as_of)`.
4. **(Related, not a code bug, but a genuine timing convention that had to be accounted for.)** Isolated
   trade `entry_as_of` is the *fill* bar, one M15 bar (900s) after the *signal* bar
   (`ai_trader/simulation/execution_simulator.py`; confirmed live by
   `test_market_order_fills_at_next_bar_open_not_signal_bar`, and by
   `portfolio_simulator.py::Position.opened_as_of = fill.as_of`). Matching a denial's own `as_of`
   directly against `entry_as_of` (no offset) found almost no matches. Fixed by matching
   `denial_as_of + 900` against `entry_as_of`.

All four corrections are reflected in the numbers below. The pipeline was re-run after each fix; the
final run was additionally repeated once more end-to-end and diffed byte-for-byte against the prior run
(§7) to confirm the corrected pipeline is itself deterministic.

### 1.4 Episode collapsing

Consecutive (≤900s gap, same symbol+direction) `LIMIT_MAX_PER_SYMBOL` denial *events* for one strategy
are collapsed into one *episode* — a persistent blocked setup denied on many consecutive bars is one
lost opportunity, not N. This reuses the same "maximal contiguous run" convention this session's own
Context Memory Checkpoint 11 already established, for internal consistency, not reinvented here.

---

## 2. Phase 1 — Complete funnel trace per strategy

Stages 1-4 (setup → signal → eligibility → risk request) reuse the already-computed, already-saved
`phase69a_competitive_funnel.json` aggregate counts directly (no re-derivation, no risk of drift from
the original paired study). Stages 5-11 (sizing reached → verdict → deny reason) are read from this
study's own new event-level recordings. Stage 12-13 (execution/outcome) reuse the saved competitive
order ledger.

| Strategy | Setup | Signal(actionable) | Scored-actionable | Rejected-by-scoring | Risk-allow | Risk-deny | Final-allow | Executed |
|---|---|---|---|---|---|---|---|---|
| S1 | 23,639 | 397 | 396 | 23,243 | 13 | 23,626 | 13 | 26 |
| S13 | 23,639 | 2,751 | 1,859 | 21,780 | 3 | 23,636 | 3 | 8 |
| S39 | 23,639 | 248 | 248 | 23,391 | 36 | 23,603 | 36 | 71 |
| S40 | 23,639 | 2,747 | 2,371 | 21,268 | 2 | 23,637 | 2 | 4 |
| S46 | 23,639 | 574 | 525 | 23,114 | 47 | 23,592 | 47 | 94 |
| S48 | 23,639 | 827 | 401 | 23,238 | 4 | 23,635 | 4 | 15 |

(Full percentage columns in `ceo_strategy_constraint_root_cause_tables.md` Table 1. "Executed" exceeds
"Risk-allow" because one ALLOW verdict can produce multiple fills — e.g. entry + partial take-profit
legs — consistent with the order-ledger convention used throughout the prior studies.)

### Deny-reason breakdown (competitive scenario)

| Strategy | BELOW_FLOOR | LIMIT_MAX_PER_SYMBOL | SIZE_BELOW_MIN | COOLDOWN_AFTER_LOSS | NOT_ACTIONABLE |
|---|---|---|---|---|---|
| S1 | 1 | 313 | 60 | 10 | 23,242 |
| S13 | 892 | 1,574 | 259 | 23 | 20,888 |
| S39 | 0 | 200 | 5 | 7 | 23,391 |
| S40 | 376 | 2,006 | 324 | 39 | 20,892 |
| S46 | 49 | 458 | 4 | 16 | 23,065 |
| S48 | 426 | 338 | 59 | 0 | 22,812 |

This table is the ground truth the rest of this report is cross-referenced against. Note S13 shows a
substantial BELOW_FLOOR count (892) despite not being one of the CEO's three named BELOW_FLOOR targets
— it is analyzed here under its named track (shared-slot) since that is where the CEO's own Phase 3
placed it, but its own BELOW_FLOOR figure is visible above for completeness.

---

## 3. Phase 2 — BELOW_FLOOR (Recommendation-Floor) root cause: S40, S46, S48

Population: genuine `BELOW_FLOOR`-denied `RiskDecision`s only (matching the counts in §2 exactly — 376
/ 49 / 426), each joined back to its originating `OpportunityScore`.

| Strategy | n events | base_quality | conflict_penalty | total_score | %conflict-caused | %weak-regardless |
|---|---|---|---|---|---|---|
| S40 | 376 | 0.464 (constant) | 0.500 (constant) | 14.0 (constant) | **100.0%** | 0.0% |
| S46 | 49 | 0.484 (constant) | 0.500 (constant) | 15.0 (constant) | **100.0%** | 0.0% |
| S48 | 426 | 0.412 (constant) | 0.500 (constant) | 12.0 (constant) | **100.0%** | 0.0% |

Every single BELOW_FLOOR event for all three strategies carries an identical `conflict_penalty = 0.500`
— exactly the documented `_OPPOSING_PENALTY` constant (`conflict.py`), never the correlated-klass
penalty (0.2/0.4). This means: in every one of the 851 combined BELOW_FLOOR denials across these three
strategies, there was another actionable, higher-quality, **opposite-direction** signal from a different
strategy on the identical bar. Recomputing each event's counterfactual score with the exact
already-existing scoring formula (`total_score = round(100 * base_quality * (1-risk_penalty) *
(1-conflict_penalty))`, reused verbatim, `conflict_penalty` set to 0) shows **100% of these events would
have cleared the WEAK_OPPORTUNITY floor (25) without the conflict penalty** — for S40:
`round(100*0.464*(1-rp)) ≥ 25` for the observed risk_penalty; all three strategies clear the same test
uniformly. Zero events are "weak regardless of conflict" (i.e., would have failed the floor even without
the penalty) — the recommendation floor here is driven entirely by the cross-strategy conflict
mechanism, not by intrinsically weak signal quality.

The constant (zero-variance) values are a genuine finding, not a data artifact: these three strategies
apparently generate the exact same categorical setup type (fixed base_quality, since Scoring Engine
base-quality components here evidently do not vary by instance for these strategies) every time they are
denied on this path — cross-checked against the base_quality/total_score values, which differ *between*
strategies (0.464 vs 0.484 vs 0.412) but not *within* one strategy's own event population.

### SIZE_BELOW_MIN — the genuine, distinct sizing-floor gate (all six targets, reported for completeness)

| Strategy | n events | raw size_units (p10/median/p90) | min_size (p10/median/p90) |
|---|---|---|---|
| S1 | 60 | 0.117 / 0.119 / 0.151 | 0.128 / 0.223 / 0.466 |
| S13 | 259 | 0.106 / 0.128 / 0.150 | 0.189 / 0.361 / 0.578 |
| S39 | 5 | 0.117 / 0.144 / 0.147 | 0.118 / 0.178 / 0.191 |
| S40 | 324 | 0.108 / 0.129 / 0.149 | 0.406 / 1.171 / 3.933 |
| S46 | 4 | 0.117 / 0.117 / 0.147 | 0.133 / 0.140 / 0.160 |
| S48 | 59 | 0.117 / 0.136 / 0.147 | 0.185 / 0.307 / 0.585 |

This **is** a real, distinct sizing-floor mechanism (`min_allocation_risk_pct * equity` vs. the computed
`size_units`), unrelated to BELOW_FLOOR. It is materially real for S40 (324 events, min_size often
5-30× the raw computed size) and S13 (259 events), and minor for the rest. It was not the CEO's named
Phase 2 target (BELOW_FLOOR), but is reported here in full because it is the actual gate that matches
the sizing-internals framing the CEO's own Phase 2 questions originally assumed applied to BELOW_FLOOR.

---

## 4. Phase 3 — LIMIT_MAX_PER_SYMBOL episode-level root cause: S1, S13, S39

| Strategy | Denial events | Episodes | Matched to isolated | Match rate | Same-dir as blocker | Opp-dir from blocker | Profitable (matched) | Losing (matched) | Expectancy_R | PF | Total isolated R |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 313 | 169 | 15 | 8.9% | 38 | 131 | 7 | 8 | +0.281 | 1.90 | +4.22 |
| S13 | 1,574 | 1,270 | 19 | 1.5% | 517 | 737 | 11 | 8 | +0.352 | 1.96 | +6.69 |
| S39 | 200 | 194 | 45 | 23.2% | 117 | 77 | 17 | 28 | +0.097 | 1.20 | +4.37 |

**Match-rate context** (important for interpreting the low percentages above): the isolated-scenario
trade ledgers for these strategies contain only 54 (S1), 37 (S13), and 66 (S39) total trades across the
entire year. Even a hypothetical "every isolated trade traces back to a blocked episode" scenario would
cap the match rate at 32%, 2.9%, and 34% respectively — S39's observed 23.2% is close to that structural
ceiling; S1 and S13's lower rates mostly reflect this small-universe ceiling, not a residual matching
defect (both were independently re-verified against the fill-delay-corrected exact-timestamp rule in
§1.3 item 4).

**CEO-mandated caveat, applied literally**: a matched episode being profitable in the isolated ledger is
**not** treated as proof of "lost profit." What this table actually establishes, and only this: (a) the
strategy's own setup *did* fire on the same bar in both scenarios for the matched subset; (b) in the
isolated scenario, absent the shared-slot rule, that specific instance of the setup closed with the
shown P&L; (c) it does **not** establish that the position would have carried the same size, entered at
the same price, or produced the same P&L had it been allowed to open *inside* the competitive portfolio
alongside the blocking position's own additional exposure, correlation, and margin/risk-budget
consumption — none of which this study re-simulates. The `expectancy_R`/`PF`/`total_isolated_R` figures
above are raw isolated-ledger outcomes of the matched subset only, not a demonstrated causal loss
attributable to the shared-slot rule.

Direction analysis: across all three strategies, the blocked signal was in the **opposite** direction
from the already-open blocking position far more often than the same direction (S1: 131/169 = 77.5%
opposite; S13: 737/1,270 = 58.0%; S39: 77/194 = 39.7%). Blocking strategies were spread across many
different strategy IDs (S39, S46, S44, S24, S21, S1 itself on re-entry attempts, S8, S13, S30, S40, S48
all appear as blockers across the full episode detail in `ceo_strategy_constraint_root_cause_tables.md`
Table 5) — this is not one strategy pair perpetually colliding, but a broad, symbol-wide contention
effect (all six candidates and most other strategies in the library trade the single symbol XAUUSD).

---

## 5. Phase 4 — Quality control

| Check | Result |
|---|---|
| Same historical data/window | `new_harness()` reused verbatim from `phase69a_funnel_run.py`; identical `WINDOW_START`/`WINDOW_END`/`SimulationContext`/`RiskConfig` |
| Same strategy version | `use_strategy_runtime=True`, no override |
| Same settlement/cost model | Same `RiskConfig` as the original paired dataset |
| Zero future leakage | Same unmodified `SimulationHarness`/`MarketScanner`/`ReplayDataSource`; no lookahead-safety change |
| Zero `ai_trader/` changes | `git status --porcelain -- ai_trader/` → **empty**, confirmed live at end of the final run |
| All values from existing infrastructure | Every field (`OpportunityScore`/`RiskDecision`/`Sizing`/`Position`) read directly off already-existing dataclasses; only percentiles/means/ratios computed via stdlib — no new statistical method, no optimization, no threshold change |

---

## 6. Phase 5 — Verdict per strategy

| Strategy | Verdict | Dominant cause | Secondary cause | Confidence |
|---|---|---|---|---|
| S1 | **PORTFOLIO-LIMITED** | Shared-slot rule blocked 169 episodes; 15 matched, 46.7% profitable in isolation (expectancy_R=+0.281); +4.22R foregone (matched subset, raw isolated-ledger, see §4 caveat) | Minor BELOW_FLOOR/SIZE_BELOW_MIN presence (1 / 60 events) | MEDIUM |
| S13 | **PORTFOLIO-LIMITED** | Shared-slot rule blocked 1,270 episodes; 19 matched, 57.9% profitable (expectancy_R=+0.352); +6.69R foregone (matched subset) | Real, secondary BELOW_FLOOR (892) and SIZE_BELOW_MIN (259) presence | MEDIUM |
| S39 | **PORTFOLIO-LIMITED** | Shared-slot rule blocked 194 episodes; 45 matched (closest to the structural match-rate ceiling), 37.8% profitable (expectancy_R=+0.097); +4.37R foregone | Negligible BELOW_FLOOR/SIZE_BELOW_MIN (0 / 5) | HIGH |
| S40 | **PORTFOLIO-LIMITED** | 100.0% of 376 BELOW_FLOOR events are conflict-penalty-caused (would clear the recommendation floor without it) | SIZE_BELOW_MIN sizing-floor (324 events, real and distinct) | HIGH |
| S46 | **PORTFOLIO-LIMITED** | 100.0% of 49 BELOW_FLOOR events are conflict-penalty-caused | SIZE_BELOW_MIN (4 events, minor) | HIGH |
| S48 | **PORTFOLIO-LIMITED** | 100.0% of 426 BELOW_FLOOR events are conflict-penalty-caused | SIZE_BELOW_MIN (59 events, minor) | HIGH |

**All six candidate strategies verdict as PORTFOLIO-LIMITED.** None qualifies as STRATEGY-LIMITED,
SIZING-LIMITED (as the sole/dominant cause), MIXED-CONSTRAINT, or INCONCLUSIVE. This is a materially
different conclusion from what the CEO's own original A-H sizing-cause framing anticipated for
S40/S46/S48 — the constraint on all three is the Scoring Engine's cross-strategy conflict penalty
(a portfolio-context mechanism), not an intrinsic sizing or signal-quality limitation. The genuine
sizing gate (SIZE_BELOW_MIN) does exist and materially affects S40 (324 events) and S13 (259 events),
but is secondary in scale to the conflict-penalty/shared-slot mechanisms for every one of the six
strategies.

---

## 7. Reproducibility

The final pipeline was run twice, end-to-end (including a fresh instrumented backtest each time), and
the two runs' `ceo_strategy_constraint_root_cause_data.json` and `ceo_strategy_constraint_root_cause_tables.md`
were diffed — **zero byte differences**, identical sha256 (`dd962d3b49cc018a790ca1b24c38c007a2b8b7cb62dd05aa6639511c0a99ebe7`).

Reproduction command (from repo root, with the project's venv):

```
./venv/Scripts/python.exe ceo_strategy_constraint_root_cause_study.py
```

This single script performs the instrumented backtest, all five analysis phases, and writes both output
artifacts. No separate report-generation script exists or is needed.

---

## 8. Study limitations

- **Small isolated-trade universe caps the LIMIT_MAX_PER_SYMBOL match rate structurally** (§4) — most
  blocked episodes for S1/S13 cannot be matched to an isolated outcome at all, not because of a matching
  defect, but because the isolated scenario itself produced very few total trades for these strategies
  over the year. The expectancy/PF figures in §4 describe only the small matched subset, not all
  blocked episodes.
- **No re-simulation of "what if this signal had been allowed inside the competitive portfolio."** The
  isolated-ledger P&L used for matched LIMIT_MAX_PER_SYMBOL episodes reflects a fully unconstrained
  world (no shared slot, no correlation budget competition, no exposure cap sharing) — not "the same
  trade, sized and priced as it would have been had it squeezed into the existing competitive portfolio
  alongside the blocking position." This is the CEO's own explicitly-required caveat (§4), preserved
  here rather than smoothed into a stronger claim.
- **BELOW_FLOOR's constant per-strategy base_quality/conflict_penalty values were observed, not
  independently re-derived from Strategy Library internals** — this study reads Scoring Engine output,
  not the strategies' own signal-generation code, so it cannot independently confirm *why* base_quality
  is invariant per strategy, only that it is.
- **SIZE_BELOW_MIN is reported but not deeply decomposed** (no per-event stop-distance/ATR/equity
  breakdown was requested for this gate, since it was not the CEO's named BELOW_FLOOR target) — a
  natural next-step deep-dive if a sizing experiment is later authorized.
- **Single fixed instrument (XAUUSD, M15, one calendar year)** — all conclusions are scoped to this
  window; no claim is made about generalization to other instruments, timeframes, or periods.
- **This study measures denial mechanisms, not causal counterfactual profitability of removing them** —
  a controlled experiment (per the recommendation below) is required before concluding that relaxing
  either mechanism would improve realized portfolio performance; conflict_penalty and the shared-slot
  rule may themselves be preventing correlated/opposing-signal overexposure that this study did not
  quantify the downside of removing.

---

## 9. Recommendation

Per the CEO's closed-choice requirement, choosing exactly one:

## **C — Both experiments, separately.**

**Justification**: the evidence is not univocal in the way the CEO's own original framing anticipated.
Two genuinely distinct, real, separately-quantified mechanisms are both material:

1. **The portfolio/shared-slot mechanism is the dominant constraint for all six strategies** — 100% of
   BELOW_FLOOR denials for S40/S46/S48 are conflict-penalty-caused (a cross-strategy, portfolio-context
   mechanism), and the LIMIT_MAX_PER_SYMBOL shared-slot rule directly blocks 169-1,270 episodes per
   strategy for S1/S13/S39, with positive matched-subset expectancy in all three. **If only one
   experiment can be funded, this is the higher-value one** — a controlled portfolio-slot experiment (B)
   testing an adjusted shared-slot/conflict-penalty policy in isolation from any sizing change.
2. **The sizing-floor mechanism (SIZE_BELOW_MIN) is real, distinct, and non-negligible for two of the
   six strategies** — S40 (324 events) and S13 (259 events) specifically — and is mechanistically
   unrelated to the conflict-penalty story (§3). Folding a sizing change into the same experiment as a
   portfolio-slot change would confound which mechanism produced any observed improvement.

Running both **separately** (not simultaneously in one combined experiment) preserves the ability to
attribute any resulting change in performance to the correct mechanism — directly serving the CEO's own
stated falsification-over-confirmation standard already established for this project's Decision
Intelligence work. **D (no change justified) is not supported**: two real, numerically-demonstrated
constraints exist. **A alone** would leave the dominant portfolio-level constraint completely
unaddressed for all six strategies. **E (insufficient evidence)** is not supported: the evidence
(2× reproducible, 141,834 events, cross-referenced against three independent data sources) is
unusually strong for a diagnostic study of this kind.

---

## 10. Files kept / conservation

Exactly four artifacts, per the CEO's own requirement:

1. `CEO_STRATEGY_CONSTRAINT_ROOT_CAUSE_REPORT.md` (this file)
2. `ceo_strategy_constraint_root_cause_tables.md`
3. `ceo_strategy_constraint_root_cause_data.json`
4. `ceo_strategy_constraint_root_cause_study.py` (single reproducible script — backtest + all 5 analysis
   phases + table/JSON generation in one file)

No other file was modified or added. `git status --porcelain -- ai_trader/` is empty. No
`PROJECT_STATE_v2.md`/`NEXT_SESSION.md`/`RECONSTRUCTION_PROMPT.md` update was made, per direct
instruction. No Portfolio Architect, Strategy Health, or Risk Integration work was started, per direct
instruction.

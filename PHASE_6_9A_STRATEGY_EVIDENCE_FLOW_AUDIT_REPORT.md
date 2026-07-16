# Phase 6.9A — Strategy Evidence Flow Audit — Report

**Date:** 2026-07-17. **Scope: a diagnostic measurement phase only.** No strategy rule, parameter,
Strategy Health scoring, scoring weight, Risk Policy, execution policy, Research Lab logic, or the
sealed holdout was touched. No profitability optimization was attempted. This report answers exactly
one question: **why do the 43 runtime strategies fail to accumulate enough recent trading evidence?**

Analysis window: **2024-10-23 → 2025-10-23** (365 days, 23,639 M15 bars) — identical to the Current
XAUUSD 12-Month Relevance Audit's own approved, non-holdout window, for direct comparability. Same
$2,000 capital, 5% risk/trade, cost model, `run_seed=1`, execution model, market data as every prior
phase.

---

## 0. Headline answer

**The single-position XAUUSD architecture is the dominant, measured bottleneck — far more than
scoring, risk policy, or execution.** Across all 43 strategies, over the full window:

| | |
|---|---|
| Total raw setup detections | 31,409 |
| Total actionable (BUY/SELL) signals | 30,239 |
| Total signals reaching Risk Manager that were **ALLOWED** | **145** |
| Total signals **DENIED** | 1,016,332 |
| ...of which denied specifically by the shared-slot limit (`LIMIT_MAX_PER_SYMBOL`) | **18,879** |
| ...of which denied for a genuine risk-policy reason (spread/liquidity/volatility/cooldown/sizing, excluding the shared slot) | 3,919 |
| Completed trades, competitive (all 43 sharing one slot) | **142** |
| Completed trades, isolated (each of the 43 run alone, same window) — **summed across all 43** | **823** |
| Missed opportunities attributable to slot contention (823 − 142) | **681** |

**Only 0.48% of all actionable signals across the entire portfolio ever get ALLOWED by Risk Manager**
— not because they are individually poor (most are denied by the mechanical `NOT_ACTIONABLE`/
`BELOW_FLOOR` echo of non-actionable states, or by the shared slot), and if every strategy could trade
independently, the portfolio would have produced **5.8× as many trades** over the same window and same
market data.

---

## 1. Methodology

### 1.1 Instrumentation technique (CEO-approved additive change + a zero-file-diff measurement layer)

**Approved, permanent, tested library change**: `ai_trader/simulation/types.py`'s `RiskEventRecord`
gained an optional `strategy_id: str | None = None` field; `PortfolioSimulator.record_risk_event()`
and the two call sites in `ai_trader/simulation/harness.py::_run_one_bar` now forward the triggering
decision's own already-existing `strategy_id`. Additive, backward-compatible, defaults to `None` for
every pre-existing call site (the batch-level engine-state event, and the LIQUIDATION event, which can
span more than one strategy's position and is deliberately left unattributed rather than guessing).
Proven via 5 new regression tests (`test_portfolio_simulator.py::TestRiskEventAttribution`,
`test_risk_event_strategy_attribution.py`), including a real end-to-end proof that a genuine
`DENY_LIMIT_MAX_PER_SYMBOL` event over 4,000 real bars is attributed to the correct strategy, never the
slot-holder. No schema version bump was needed: `RiskEventRecord` is an internal type, never directly
serialized (only the aggregated, by-`type`-only `RiskEventSummary` reaches the wire schema, unchanged).

**Zero-file-diff funnel measurement** (for the broader funnel this report needed — signal states,
scoring conversion, risk ALLOW/DENY per bar — none of which any existing persisted structure captures):
`phase69a_funnel_recorder.py` monkey-patches the bound methods of the ALREADY-CONSTRUCTED harness
instance's own component objects (`harness._signal_engine.evaluate`, `harness._scoring_engine.
score_batch`, `harness._risk_manager.evaluate`) immediately after `harness.load()`. Every wrapper calls
the ORIGINAL, unmodified implementation and returns its result completely unchanged — it only
additionally records that same result. **This changes zero lines in any `ai_trader/` source file**;
the decision logic that actually executes is the exact same compiled code the production harness
always runs. Order-level fill/reject/expire/partial-fill counts and completed trades need no tap at
all: `ExecutionSimulator._orders` (every `WorkingOrder` already carries its own `strategy_id`) and
`PortfolioSimulator.account.trade_ledger` are read directly, after the run, with no mutation.

**Proof this technique is behaviorally invisible**: `phase69a_funnel_run.py`'s own
`verify_zero_behavior_change()` ran an INSTRUMENTED backtest and a PLAIN (unwrapped) backtest, identical
config, and asserted the trade ledger AND the full `SimulationReportData` (portfolio summary,
performance, attribution, stats, allocation, risk events — every field, not a subset) are
byte-identical. **Result: PARITY VERIFIED — both produced exactly 142 trades, byte-identical across the
full report.** (An adversarial review, §4.1, initially found this check compared only two of the
report's fields; fixed and re-verified before this claim was finalized.)

### 1.2 The funnel, mapped onto the real pipeline (verified by reading the code, not assumed)

1. **Raw setup detections** = bars where the evaluator's own `SetupResult.setup_forming` was `True` —
   derived from `StrategySignal.state` plus, for the `NO_SIGNAL` state specifically, its own
   `explanation.why_failed[0].code`: `NO_SETUP` (no raw setup at all) vs `NO_SIGNAL_PRESENT` (a setup
   WAS forming, but `generate_signal()` didn't produce a present signal) — a distinction the pipeline
   itself already preserves (`ai_trader/signal_engine/pipeline.py` lines 197–215), not invented for
   this report.
2. **Actionable strategy signals** = `SignalState` ∈ {BUY, SELL}.
3. **NO_SIGNAL outcomes** = `SignalState.NO_SIGNAL` (both sub-cases combined, per the CEO's own literal
   stage; the `NO_SETUP` vs `NO_SIGNAL_PRESENT` split feeds "raw setup detections" above instead).
4. **WAIT_CONFIRMATION outcomes** = `SignalState.WAIT_CONFIRMATION`.
5. **NEED_CONTEXT outcomes** = `SignalState.NEED_CONTEXT`.
6. **BLOCKED outcomes** = `SignalState.BLOCKED` (evaluator's own `can_trade()`/`health()` precondition
   failed — data-quality DISABLED, not a market-frequency concept).
7. **INVALID outcomes** = `SignalState.INVALID` (malformed evaluator output / `health()` INVALID).
8. **Opportunities reaching Scoring Engine** = every actionable signal receives an `OpportunityScore`;
   "scored actionable" = `recommendation` ∈ {STRONG_OPPORTUNITY, MODERATE_OPPORTUNITY,
   WEAK_OPPORTUNITY} (the same set `RiskConfig.allowed_recommendations` names).
9. **Rejected/ranked below executable candidates** = actionable signals whose own recommendation was
   NOT in that set (a genuine Scoring Engine downgrade — confirmed to actually occur: e.g. S1 shows
   397 actionable signals but only 396 scored-actionable, and several strategies show a materially
   larger gap).
10. **Risk Manager ALLOW** = `RiskDecision.decision == ALLOW`.
11. **Risk Manager DENY, by reason** = `RiskDecision.denied_reasons[].code`, tagged per strategy via
    §1.1's own new field. **Important, code-verified architectural fact**: `NOT_ACTIONABLE`
    (`ai_trader/risk_manager/pipeline.py` line 83) fires for ANY non-actionable `SignalState` reaching
    Risk Manager — it is a mechanical ECHO of stages 3–7, not an independent suppression mechanism.
    `BELOW_FLOOR` is likewise an echo of stage 9. This report reports both raw totals AND a
    "genuine risk denials" figure that excludes these two mechanical echoes and the shared slot,
    isolating the risk policy's OWN independent contribution (spread/liquidity/volatility filters,
    cooldown-after-loss, sizing floors, other portfolio limits).
12. **Blocked by the shared XAUUSD slot** = `DENY_LIMIT_MAX_PER_SYMBOL` specifically
    (`ai_trader/risk_manager/limits.py::check_max_per_symbol`), tracked separately from every other
    DENY reason.
13–17. **Order-level fills/rejects/expires/partials** = `ExecutionSimulator._orders`' own terminal
    `WorkingOrderState` per strategy. **Reconciliation note**: a single completed trade typically
    corresponds to THREE order records (the entry + two OCO bracket siblings, stop and target) — e.g.
    S46: 47 trades, 141 orders submitted (47×3), 94 filled (47×2 — entry + whichever OCO leg
    triggered), 47 cancelled (the OCO leg that never triggered). "Rejected"/"expired" counts are
    ZERO portfolio-wide in this window — every non-fill order outcome was a normal OCO-sibling
    cancellation, not a genuine execution failure.
18. **Completed trades** = `trade_ledger` (already the standard, already-used metric everywhere else
    in this project).

### 1.3 Isolated-slot counterfactual

Every one of the 43 strategies was ALSO run completely ALONE (`strategy_id_filter=frozenset({that one
id})`) over the identical window/config — 43 separate, independent, fully-instrumented backtests.
**A diagnostic counterfactual only** — it does not change, and was never used to change, the
competitive (all-43) production behavior. `missed_opportunities_due_to_slot_contention` =
`n_trades_isolated − n_trades_competitive` (never negative in this dataset).

### 1.4 Suppression classification — fixed thresholds, decided before inspecting the final table

- **A. GENUINE_LOW_MARKET_FREQUENCY**: raw setup detections < 12 over the whole window (< ~1/month).
- **B. SHARED_SLOT_SUPPRESSION**: isolated trades exceed competitive trades by ≥5 AND ≥30% relative.
- **C. SCORING_SUPPRESSION**: genuine scoring-driven downgrades (actionable signals that scored below
  the recommendation floor) ≥ 20% of the strategy's own actionable-signal count.
- **D. RISK_SUPPRESSION**: genuine (non-echo, non-slot) Risk Manager denials ≥ 20% of scored-actionable
  signals.
- **E. EXECUTION_SUPPRESSION**: rejected + expired orders ≥ 20% of submitted orders.
- **F. INSUFFICIENT_DATA**: NEED_CONTEXT outcomes ≥ 50% of all evaluated bars.
- **G. MIXED_CAUSES**: more than one of B–F crosses its own threshold, OR none does but the strategy
  has real signal volume (raw setups ≥ 12) — in the latter case the largest SUB-threshold contributors
  are reported explicitly (never hidden behind an invented 8th category).

**No strategy is classified from completed-trade count alone** — every rule reads from the funnel
counts (setups/signals/scoring/risk/execution), never from `n_trades` directly, per the CEO's own
explicit instruction.

**Confidence in diagnosis**: `HIGH` when raw setups ≥ 20 (enough volume for the ratios above to be
meaningful); `MEDIUM` when 5–19; `LOW` when < 5 (including the 8 strategies with exactly 0 — the "no
evidence at all" fact itself is certain, but a deeper diagnosis of WHY is not possible from zero data
points).

---

## 2. Full per-strategy funnel (all 43 strategies, none hidden)

| Strategy | RawSetups | Actionable | NoSignal | WaitConf | NeedCtx | Blocked | Invalid | ScoredOK | RejByScoring | RiskAllow | RiskDeny | SharedSlotDenies | GenuineRiskDenies | OrdSubmit | OrdFilled | OrdRej | OrdExp | CompTrades | IsoTrades | MissedOpp | SlotSuppr% | ZeroSetupMo | SetupNoTradeMo | Principal | Secondary | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1567 | 397 | 22072 | 1170 | 0 | 0 | 0 | 396 | 23243 | 13 | 23626 | 313 | 70 | 39 | 26 | 0 | 0 | 14 | 54 | 40 | 74% | 0 | 8 | B | — | HIGH |
| S2 | 423 | 423 | 23216 | 0 | 0 | 0 | 0 | 417 | 23222 | 0 | 23639 | 325 | 92 | 0 | 0 | 0 | 0 | 0 | 18 | 18 | 100% | 0 | 13 | G | B,D | HIGH |
| S3 | 0 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 23639 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 13 | 0 | A | — | LOW |
| S4 | 1265 | 1265 | 22374 | 0 | 0 | 0 | 0 | 457 | 23182 | 1 | 23638 | 385 | 71 | 3 | 3 | 0 | 0 | 2 | 33 | 31 | 94% | 0 | 12 | G | B,C | HIGH |
| S5 | 1358 | 1358 | 19185 | 0 | 3096 | 0 | 0 | 1358 | 22281 | 2 | 23637 | 1160 | 196 | 6 | 4 | 0 | 0 | 2 | 9 | 7 | 78% | 0 | 12 | B | — | HIGH |
| S6 | 699 | 699 | 22940 | 0 | 0 | 0 | 0 | 699 | 22940 | 0 | 23639 | 580 | 119 | 0 | 0 | 0 | 0 | 0 | 8 | 8 | 100% | 0 | 13 | B | — | HIGH |
| S7 | 0 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 23639 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 13 | 0 | A | — | LOW |
| S8 | 159 | 159 | 23480 | 0 | 0 | 0 | 0 | 130 | 23509 | 2 | 23637 | 104 | 24 | 6 | 4 | 0 | 0 | 2 | 4 | 2 | 50% | 0 | 12 | G | sub-threshold: B=50%, D=18%, C=18% | HIGH |
| S9 | 0 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 23639 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 13 | 0 | A | — | LOW |
| S10 | 1503 | 1503 | 22136 | 0 | 0 | 0 | 0 | 878 | 22761 | 6 | 23633 | 706 | 203 | 13 | 12 | 0 | 0 | 1 | 117 | 116 | 99% | 0 | 12 | G | B,C,D | HIGH |
| S11 | 0 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 23639 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 13 | 0 | A | — | LOW |
| S12 | 1245 | 1245 | 22394 | 0 | 0 | 0 | 0 | 852 | 22787 | 0 | 23639 | 713 | 194 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 0 | 13 | G | C,D | HIGH |
| S13 | 2751 | 2751 | 20888 | 0 | 0 | 0 | 0 | 1859 | 21780 | 3 | 23636 | 1574 | 282 | 8 | 8 | 0 | 0 | 1 | 37 | 36 | 97% | 0 | 12 | G | B,C | HIGH |
| S14 | 87 | 87 | 23552 | 0 | 0 | 0 | 0 | 13 | 23626 | 1 | 23638 | 8 | 4 | 2 | 2 | 0 | 0 | 1 | 14 | 13 | 93% | 2 | 10 | G | B,C,D | HIGH |
| S15 | 0 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 23639 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 13 | 0 | A | — | LOW |
| S16 | 758 | 758 | 22881 | 0 | 0 | 0 | 0 | 719 | 22920 | 1 | 23638 | 600 | 118 | 4 | 4 | 0 | 0 | 1 | 11 | 10 | 91% | 0 | 12 | B | — | HIGH |
| S17 | 0 | 0 | 0 | 0 | 23639 | 0 | 0 | 0 | 23639 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 13 | 0 | G | A,F | LOW |
| S18 | 258 | 258 | 23381 | 0 | 0 | 0 | 0 | 177 | 23462 | 2 | 23637 | 149 | 26 | 4 | 3 | 0 | 0 | 1 | 6 | 5 | 83% | 0 | 12 | G | B,C | HIGH |
| S19 | 26 | 26 | 1006 | 0 | 22607 | 0 | 0 | 0 | 23639 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 2 | 11 | G | C,F | MEDIUM |
| S20 | 0 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 23639 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 13 | 0 | A | — | LOW |
| S21 | 790 | 790 | 22849 | 0 | 0 | 0 | 0 | 636 | 23003 | 1 | 23638 | 523 | 112 | 3 | 2 | 0 | 0 | 2 | 4 | 2 | 50% | 0 | 12 | G | sub-threshold: B=50%, C=19%, D=18% | HIGH |
| S22 | 426 | 426 | 23213 | 0 | 0 | 0 | 0 | 426 | 23213 | 3 | 23636 | 382 | 41 | 9 | 6 | 0 | 0 | 1 | 19 | 18 | 95% | 1 | 11 | B | — | HIGH |
| S23 | 0 | 0 | 0 | 0 | 23639 | 0 | 0 | 0 | 23639 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 13 | 0 | G | A,F | LOW |
| S24 | 258 | 258 | 23381 | 0 | 0 | 0 | 0 | 149 | 23490 | 1 | 23638 | 122 | 26 | 4 | 4 | 0 | 0 | 2 | 7 | 5 | 71% | 0 | 12 | G | B,C | HIGH |
| S25 | 596 | 596 | 23043 | 0 | 0 | 0 | 0 | 451 | 23188 | 4 | 23635 | 375 | 79 | 14 | 14 | 0 | 0 | 4 | 43 | 39 | 91% | 0 | 9 | G | B,C | HIGH |
| S26 | 1832 | 1832 | 21807 | 0 | 0 | 0 | 0 | 1490 | 22149 | 3 | 23636 | 1241 | 246 | 9 | 6 | 0 | 0 | 4 | 24 | 20 | 83% | 0 | 12 | B | — | HIGH |
| S27 | 0 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 23639 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 13 | 0 | A | — | LOW |
| S28 | 1323 | 1323 | 22316 | 0 | 0 | 0 | 0 | 829 | 22810 | 1 | 23638 | 684 | 144 | 4 | 4 | 0 | 0 | 2 | 19 | 17 | 89% | 0 | 12 | G | B,C | HIGH |
| S29 | 53 | 53 | 23586 | 0 | 0 | 0 | 0 | 53 | 23586 | 0 | 23639 | 46 | 7 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 100% | 0 | 13 | G | sub-threshold: B=100%, D=13% | HIGH |
| S30 | 944 | 944 | 22695 | 0 | 0 | 0 | 0 | 910 | 22729 | 3 | 23636 | 753 | 154 | 9 | 6 | 0 | 0 | 2 | 19 | 17 | 89% | 0 | 12 | B | — | HIGH |
| S31 | 20 | 20 | 23619 | 0 | 0 | 0 | 0 | 0 | 23639 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 1 | 12 | C | — | MEDIUM |
| S38 | 0 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 23639 | 0 | 23639 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 13 | 0 | A | — | LOW |
| S39 | 248 | 248 | 23391 | 0 | 0 | 0 | 0 | 248 | 23391 | 36 | 23603 | 200 | 12 | 108 | 71 | 0 | 0 | 36 | 66 | 30 | 45% | 0 | 0 | B | — | HIGH |
| S40 | 2747 | 2747 | 20892 | 0 | 0 | 0 | 0 | 2371 | 21268 | 2 | 23637 | 2006 | 363 | 6 | 4 | 0 | 0 | 3 | 69 | 66 | 96% | 0 | 11 | B | — | HIGH |
| S41 | 508 | 508 | 23131 | 0 | 0 | 0 | 0 | 183 | 23456 | 0 | 23639 | 157 | 26 | 0 | 0 | 0 | 0 | 0 | 8 | 8 | 100% | 0 | 13 | G | B,C | HIGH |
| S42 | 63 | 63 | 23576 | 0 | 0 | 0 | 0 | 46 | 23593 | 2 | 23637 | 34 | 10 | 6 | 4 | 0 | 0 | 1 | 21 | 20 | 95% | 5 | 7 | G | B,C,D | HIGH |
| S43 | 2297 | 2297 | 21342 | 0 | 0 | 0 | 0 | 1253 | 22386 | 1 | 23638 | 1037 | 215 | 3 | 2 | 0 | 0 | 2 | 19 | 17 | 89% | 0 | 12 | G | B,C | HIGH |
| S44 | 2183 | 2183 | 21456 | 0 | 0 | 0 | 0 | 2076 | 21563 | 6 | 23633 | 1732 | 338 | 18 | 12 | 0 | 0 | 7 | 41 | 34 | 83% | 0 | 10 | B | — | HIGH |
| S45 | 336 | 336 | 23303 | 0 | 0 | 0 | 0 | 227 | 23412 | 0 | 23639 | 187 | 40 | 0 | 0 | 0 | 0 | 0 | 10 | 10 | 100% | 0 | 13 | G | B,C | HIGH |
| S46 | 574 | 574 | 23065 | 0 | 0 | 0 | 0 | 525 | 23114 | 47 | 23592 | 458 | 20 | 141 | 94 | 0 | 0 | 47 | 79 | 32 | 41% | 0 | 1 | B | — | HIGH |
| S48 | 827 | 827 | 22812 | 0 | 0 | 0 | 0 | 401 | 23238 | 4 | 23635 | 338 | 59 | 15 | 15 | 0 | 0 | 4 | 61 | 57 | 93% | 0 | 10 | G | B,C | HIGH |
| S50 | 1603 | 1603 | 22036 | 0 | 0 | 0 | 0 | 1223 | 22416 | 0 | 23639 | 1044 | 179 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 100% | 0 | 13 | C | — | HIGH |
| S51 | 1682 | 1682 | 21957 | 0 | 0 | 0 | 0 | 1265 | 22374 | 0 | 23639 | 943 | 449 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 0 | 13 | G | C,D | HIGH |

**Portfolio-level totals (all 43 strategies, same window):**

| | |
|---|---|
| Raw setups | 31,409 |
| Actionable signals | 30,239 |
| NO_SIGNAL outcomes | 912,087 |
| WAIT_CONFIRMATION outcomes | 1,170 |
| NEED_CONTEXT outcomes | 72,981 |
| BLOCKED outcomes | 0 |
| INVALID outcomes | 0 |
| Scored actionable | 22,717 |
| Rejected by scoring (total, includes the mechanical echo of non-actionable states) | 993,760 |
| Risk Manager ALLOW | **145** |
| Risk Manager DENY | 1,016,332 |
| ...of which shared-slot (`LIMIT_MAX_PER_SYMBOL`) | 18,879 |
| ...of which genuine risk-policy denials (excl. mechanical echo + shared slot) | 3,919 |
| Orders submitted | 434 |
| Orders filled | 310 |
| Orders rejected | 0 |
| Orders expired | 0 |
| Orders cancelled (OCO sibling, normal) | 120 |
| Completed trades (competitive) | 142 |
| Completed trades (isolated, summed across all 43) | 823 |
| Missed opportunities due to slot contention | 681 |

**Principal-cause distribution**: A (genuine low frequency) = 8; B (shared-slot) = 11; C (scoring) = 2;
D (risk) = 0; E (execution) = 0; F (insufficient data) = 0; G (mixed/diffuse) = 22.

---

## 3. Answers to the eight required questions

**1. Are strategies genuinely rare?** For 8 of 43 (S3, S7, S9, S11, S15, S20, S27, S38), yes — zero raw
setup detections across the entire 13-month, 23,639-bar window, confirmed both competitively and in
isolation. For the other 35, **no** — raw setup counts range from 20 (S31) to 2,751 (S13), and 30,239
actionable signals were generated portfolio-wide. Genuine rarity explains a minority of the strategies,
not the majority.

**2. Are they producing opportunities that are hidden by slot competition?** **Yes, extensively.** 11
strategies have shared-slot suppression as their SOLE principal cause; it appears as a contributing
factor in 20 of the 22 "mixed" (G) strategies too. Portfolio-wide, isolated trade counts (823) are 5.8×
competitive trade counts (142) — 681 trades' worth of opportunity lost specifically to slot contention.
Individual cases are stark: S10 (1 competitive trade vs 117 isolated), S13 (1 vs 37), S43 (2 vs 19),
S40 (3 vs 69).

**3. Is Scoring suppressing useful opportunities?** **Modestly, as a secondary factor for many, a
principal cause for few.** Only 2 strategies (S31, S50) have scoring suppression as their SOLE
principal cause. It appears as a secondary contributor in most of the 22 "G" strategies, but its
portfolio-wide magnitude (22,717 scored-actionable out of 30,239 actionable = a real but partial
downgrade rate) is smaller and less concentrated than the shared-slot effect.

**4. Is Risk Manager suppressing them (beyond the shared slot)?** **Minimally, on its own.** Zero
strategies have genuine risk-policy suppression (D) as a SOLE principal cause. Genuine risk denials
total 3,919 portfolio-wide — about 4.8× smaller than shared-slot denials (18,879) — and appear only as
a secondary contributor within several "G" classifications (e.g. S10, S14, S42).

**5. Is execution causing meaningful loss?** **No.** Zero rejected orders and zero expired orders
portfolio-wide. Every non-fill order outcome (120 total) was a normal OCO-sibling cancellation — the
expected, harmless accounting artifact of a bracket order's losing leg, not a genuine execution
failure. No strategy shows execution suppression (E) as principal or even meaningful secondary.

**6. Would independent slots materially increase evidence?** **Yes, dramatically and consistently.**
Every one of the 35 strategies with any real signal volume shows an isolated trade count at or above
its competitive count, most by a wide margin (e.g. S10: 1→117, S48: 4→61, S26: 4→24, S44: 7→41). Summed
across all 43, isolated trading would have produced 5.8× the actual competitive trade count over the
identical market data and window.

**7. Is the current one-position XAUUSD architecture the principal bottleneck?** **Yes.** It is the
single largest specific DENY reason (18,879, vs 3,919 for every other genuine risk reason combined),
the sole principal cause for the largest individual category (11 of 43 strategies), and a contributing
factor in the large majority of the "mixed" category. Only 0.48% of all actionable signals portfolio-
wide were ever ALLOWED — and while most of the DENY volume is the mechanical `NOT_ACTIONABLE`/
`BELOW_FLOOR` echo of upstream states (not itself evidence of slot suppression), the isolated-vs-
competitive trade-count comparison is a direct, non-mechanical, empirical measurement that confirms the
shared slot specifically costs the portfolio the majority of its addressable trade volume.

**8. What evidence-governance model is justified by the findings?** This report does not select or
implement one (per explicit CEO instruction). The data strongly indicates that among the Phase 6.10
menu already proposed (`NEXT_SESSION.md` §H), the items most directly responsive to THIS finding are
those addressing the shared-slot constraint itself: **portfolio-level rather than per-strategy Health
scoring**, a **minimum exploration allocation**, and **shadow-mode evidence accumulation** (paper-
tracking a strategy's own hypothetical signals when the real slot is occupied) would each directly
target the measured 681-trade shared-slot shortfall, whereas re-tuning Scoring Engine weights or Risk
Manager policy would address a comparatively smaller share of the measured suppression (2 and 0
strategies respectively have those as a sole principal cause). This is an observation about where the
data points, not a selection or recommendation to implement any specific one.

---

## 4. Validation

```
Focused tests (RiskEventRecord attribution): 16 passed
  ai_trader/simulation/tests/test_portfolio_simulator.py::TestRiskEventAttribution (4 new tests)
  ai_trader/simulation/tests/test_risk_event_strategy_attribution.py (1 new end-to-end test, 4000 real bars)

Full suite: pytest ai_trader/ -q -- 1576 passed (1571 baseline + 5 new)
mypy --strict ai_trader/ --exclude 'tests/' -- Success: no issues found in 165 source files
coverage run --source=ai_trader -m pytest ai_trader/ -q
coverage report --omit="*/tests/*" -- TOTAL 9649 stmts, 432 miss, 96%
```

- **Attribution accuracy**: proven both in isolation (unit tests on `record_risk_event`) and end-to-end
  (a real `DENY_LIMIT_MAX_PER_SYMBOL` event over 4,000 real bars, attributed to the actual denied
  strategy, never the slot-holder, never `None`).
- **Anti-lookahead**: the funnel counters are taps on values the pipeline computes AT each bar's own
  evaluation time, using only that bar's own `MarketContext` — no counter reads or aggregates
  information from a future bar; this is inherent to observing the SAME real-time pipeline calls the
  production harness already makes, not a new mechanism with its own lookahead surface.
- **Determinism / instrumentation-invisibility**: proven directly — the instrumented competitive run
  and a plain, unwrapped run of the identical config produced a byte-identical trade ledger and
  performance report (§1.1). This is the single most important correctness property of the
  measurement technique itself: instrumentation observes, it does not participate.
- **Isolated-slot reproducibility**: all 43 isolated runs use the same deterministic `SimulationContext`
  /`run_seed=1` convention already proven deterministic in every prior phase (Wave D, Phase 6.9, the
  relevance audit) — the same harness/data/seed machinery, differing only in `strategy_id_filter`, a
  parameter already proven not to affect determinism.
- **Protected-area verification**: `git status --porcelain -- code/ results/ knowledge/` empty (§5).
  The Strategy Health System's own scoring methodology, every strategy contract, Scoring Engine
  weights, Risk Policy, and Execution Engine rules are byte-for-byte unmodified.
- **Adversarial review**: see §4.1.

### 4.1 Adversarial review

An independent adversarial review agent examined the `RiskEventRecord.strategy_id` diff, the harness
call sites, the new tests, and the `phase69a_funnel_recorder.py`/`phase69a_funnel_run.py` measurement
technique, with explicit instructions to try to break each claim rather than confirm it. Findings,
reported honestly (not filtered to make the technique look better than it is):

- **No defects found** in the approved `RiskEventRecord.strategy_id` change itself: confirmed additive/
  backward-compatible against every call site in the repository (not just the two touched), confirmed
  `RiskDecision.strategy_id` is always a real, non-optional string at both harness call sites (traced
  to its origin in `assembler.py`/`engine.py`), confirmed the existing `performance_analyzer.py`
  aggregation (by `type` only) doesn't even see the new field, and confirmed the deliberate choice to
  leave the LIQUIDATION event and the batch-level engine-state event unattributed is sound (both can
  legitimately lack a single owning strategy).
- **No defects found** in the new tests: the end-to-end attribution test would fail loudly (not pass
  vacuously) if the harness wiring were broken, since it asserts `slot_denials` is non-empty with an
  explicit message before checking attribution.
- **One real, medium-severity gap found and fixed**: `verify_zero_behavior_change()`'s original
  "byte-identical results" claim only actually compared `portfolio_summary` and `performance`, silently
  omitting `attribution`/`stats`/`allocation`/`risk_events` from the comparison. Fixed before this
  report was finalized: `_full_report_dict()` now compares every field of `SimulationReportData`, and
  the parity check was re-run against the corrected comparison (§1.1's own headline result reflects the
  corrected, complete check, not the original narrower one).
- **One low-severity documentation inaccuracy found and fixed**: `phase69a_funnel_recorder.py`'s own
  docstring referenced a test file/function name that was never created; corrected to name the actual
  manually-invoked verification function and note explicitly that it is not pytest-collected, so it
  must be re-run by hand after any future edit to the recorder.
- **One informational-only observation, confirmed harmless**: the recorder's defensive
  `why_failed[0].code if why_failed else None` guard (for distinguishing `NO_SETUP` from
  `NO_SIGNAL_PRESENT`) can never actually hit its `else` branch given every current `NO_SIGNAL`-
  producing code path in `pipeline.py` always populates `why_failed` — dead code, not a live gap, left
  in place as a fail-safe rather than removed.
- The "UNCLASSIFIED_LOW_SIGNAL" bug (an invented 8th classification bucket, not one of the CEO's 7) was
  found and fixed during the classification script's own initial construction, BEFORE the adversarial
  review pass — disclosed here for completeness, not discovered by the reviewer.

---

## 5. Protected-area confirmation and preserved artifacts

- `code/`, `results/`, `knowledge/` — 0-diff, confirmed via `git status --porcelain`.
- `ai_trader/strategy_health/` — byte-for-byte unmodified this phase (no scoring/weight/threshold
  change).
- Every strategy contract, Scoring Engine, Risk Manager, and Execution Engine production code —
  unmodified except the one disclosed, additive `RiskEventRecord.strategy_id` change (§1.1).
- No strategy was promoted, demoted, or eliminated. No governance model was implemented. No Shadow
  Mode, Telegram, Broker Adapter, or MT5 work was started.

**Diagnostic artifacts preserved at repo root** (same precedent as Phase 6.9 and the relevance audit):
`phase69a_funnel_recorder.py` (the instrumentation technique), `phase69a_funnel_run.py` (competitive run
+ parity check), `phase69a_isolated_run.py` (the 43 isolated-slot runs), `phase69a_analysis.py`
(conversion rates + classification) — and their raw JSON outputs: `phase69a_competitive_funnel.json`,
`phase69a_isolated_funnel.json`, `phase69a_analysis.json`.

---

**No governance redesign follows this report.** No WATCHLIST strategy was activated. No multi-position
trading was implemented. No Shadow Mode, Telegram, Broker Adapter, or MT5 work has been started.
Waiting for CEO review.

# Phase 6.9A — Strategy Evidence Flow Audit — Specification (Documentation Only)

**Date:** 2026-07-16. **Status: PROPOSED SPECIFICATION, NOT APPROVED, NOT STARTED, NOT IMPLEMENTED.**
No code has been written for this phase. This document exists so a future session (or the CEO
directly) can review, revise, and explicitly approve a concrete plan before any implementation begins
— the same discipline every prior phase's own handoff document followed before its own CEO sign-off.

---

## 1. Why this phase exists

Two independent analyses this session and last converged on the same unanswered question:

- **Phase 6.9** (`PHASE_6_9_ROLLING_HEALTH_GATED_BACKTEST_REPORT.md`): a rolling Health-gate produced
  an empty ACTIVE roster for ~2.6 of its 3.6 years, because most strategies never accumulate enough
  rolling-window trade evidence to be judged.
- **The Current XAUUSD 12-Month Relevance Audit** (`CURRENT_XAUUSD_12M_RELEVANCE_REPORT.md`): over a
  fresh, independent 12-month window, 20 of 43 strategies took ZERO trades and only 4 had enough
  evidence to be judged at all (all four scoring WEAK).

Both analyses treat "how many trades did a strategy take" as a GIVEN, unexamined input. Neither asks
**why** that number is so low. A strategy could be trading rarely for any of several completely
different reasons, each implying a completely different next action:

- its own setup pattern is genuinely rare in this market (nothing to do — this is real);
- its setups occur often but get discarded before ever reaching a trade, at some specific point in the
  six-module pipeline.

Phase 6.9A's entire objective is to find out which, per strategy, by measuring — not guessing, not
inferring from aggregate trade counts alone — where in the pipeline each strategy's own opportunities
are actually going.

**This is a measurement phase, not a fix phase.** No strategy, threshold, scoring weight, risk policy,
or execution rule would be modified.

---

## 2. The real pipeline this phase would instrument (verified, not assumed)

Every stage below is an EXISTING, already-computed value in the frozen six-module pipeline — Phase
6.9A's own proposed work is to COUNT and PERSIST these values per strategy, per bar, across a backtest;
it does not propose changing what any of them mean or how they are computed.

```
Market Scanner --> Signal Engine (per-strategy, per-bar) --> Scoring Engine --> Risk Manager --> Execution Simulator --> Portfolio Simulator (trade_ledger)
```

1. **Raw setup detection** (`RuntimeEvaluator.evaluate()` → `SetupResult.setup_forming`,
   `ai_trader/strategy_runtime/evaluator.py`): does this strategy's own pattern-matching logic
   recognize ANY candidate setup on this bar at all, regardless of whether it ever becomes a signal.
   `SetupResult.no_setup()` = no. This is the earliest, most granular measure of "does this strategy's
   own edge-condition even show up in this market."
2. **Signal presence / confirmation state** (same `SetupResult`: `present`, `confirmations_met`) and
   the Signal Engine's own final per-bar `SignalState` (`ai_trader/signal_engine/types.py`):
   `BUY`/`SELL` (actionable now), `LONG_READY`/`SHORT_READY` (armed, awaiting trigger),
   `WAIT_CONFIRMATION` (setup present, confirmations not yet met), `NEED_CONTEXT` (insufficient/stale
   context — a data-availability gap, distinct from a market-frequency gap), `BLOCKED` (the
   evaluator's own `can_trade()`/`health()` precondition failed, e.g. data quality DISABLED),
   `INVALID` (malformed evaluator output), `NO_SIGNAL` (no setup at all — mirrors `setup_forming=False`
   upstream).
3. **Scoring Engine outcome** (`ai_trader/scoring_engine/engine.py`, `conflict.py`): did an actionable
   signal receive a score meeting `RiskConfig`'s `min_total_score`/`allowed_recommendations`, and if
   multiple strategies produced competing signals for the same symbol-bar, did this strategy's signal
   win or lose the Scoring Engine's own conflict resolution?
4. **Risk Manager outcome** (`ai_trader/risk_manager/engine.py`, `limits.py`, `filters.py`,
   `guards.py`): `ALLOW` vs `DENY`, with the SAME reason codes already observed in real runs this
   session (`DENY_BELOW_FLOOR`, `DENY_COOLDOWN_AFTER_LOSS`, `DENY_FILTER_VOLATILITY`,
   `DENY_INVALID_INPUT`, **`DENY_LIMIT_MAX_PER_SYMBOL`** — the single-shared-XAUUSD-slot constraint,
   `check_max_per_symbol()` in `limits.py` — `DENY_NOT_ACTIONABLE`, `DENY_SIZE_BELOW_MIN`).
   **Important architectural fact, confirmed by reading the code (not assumed)**: the "blocked by
   another open XAUUSD position" concept the CEO asked to measure separately is enforced HERE, at Risk
   Manager's own `LIMIT_MAX_PER_SYMBOL` check — NOT at the Signal Engine's `BLOCKED` state (which
   means something else, a data-quality/precondition gate). Phase 6.9A's own funnel must keep these
   two distinct, not conflate them.
5. **Execution outcome** (`ai_trader/simulation/execution_simulator.py`): an `ALLOW`ed decision becomes
   a submitted order; does it fill, get rejected, or expire unfilled (`WorkingOrderState`:
   `FILLED`/`CANCELLED`/`REJECTED`/`EXPIRED`)?
6. **Completed trade** (`ai_trader/simulation/portfolio_simulator.py`'s `trade_ledger`): the final,
   already-measured count every prior report used.

**A data-model gap this phase would need to close, minimally and additively**: `RiskDecision` already
carries its own `strategy_id` (confirmed — every call site building one, e.g.
`ai_trader/simulation/time_stop.py::build_time_stop_decision`, sets it), but
`ai_trader/simulation/portfolio_simulator.py`'s `RiskEventRecord` — the type `record_risk_event()`
stores denial reasons into — has NO `strategy_id` field, and the harness's own call sites
(`ai_trader/simulation/harness.py::_run_one_bar`) do not forward `decision.strategy_id` when recording
a DENY. This is why the relevance audit could only report AGGREGATE, portfolio-level rejection
reasons, never per-strategy ones (disclosed there as a known limitation). **Proposed minimal fix**: add
an optional `strategy_id: str | None = None` field to `RiskEventRecord` and pass `decision.strategy_id`
at the (already identified) two call sites — additive, backward-compatible (defaults to `None`,
existing callers/tests unaffected), the same class of minimal, disclosed change as the Phase 6.9
overlay-isolation fix. **Not implemented by this document — proposed only.**

---

## 3. Proposed per-strategy funnel (what would be measured, and how)

For every one of the 43 strategies, over a chosen window (proposed: the SAME 2024-10-23 → 2025-10-23
window as the relevance audit, for direct comparability, PLUS optionally the full 3.6-year Wave D
range for a lifetime view):

| Stage | Proposed source | What it counts |
|---|---|---|
| Raw setup detections | `SetupResult.setup_forming` | Bars where this strategy's own pattern is recognized at all |
| Actionable signals | `SignalState` ∈ {BUY, SELL} | Bars where the setup became a genuinely actionable signal |
| Blocked by missing context | `SignalState = NEED_CONTEXT` | Bars where a data/context gap, not a market gap, stopped evaluation |
| Blocked by shared XAUUSD slot | Risk Manager `DENY_LIMIT_MAX_PER_SYMBOL` (per-strategy, via the proposed `RiskEventRecord.strategy_id` field, §2) | Actionable signals that lost to an already-open position |
| Rejected by Scoring Engine | Scoring/conflict-resolution outcome (per-strategy; exact hook to be confirmed against `scoring_engine/conflict.py` during implementation) | Signals that scored too low or lost a same-bar conflict |
| Denied by Risk Manager (all other reasons) | `DENY_*` reason codes excluding `LIMIT_MAX_PER_SYMBOL`, per-strategy | Signals blocked by spread/liquidity/volatility/cooldown/sizing gates |
| Orders rejected/unfilled | Execution Simulator `WorkingOrderState` ∈ {REJECTED, EXPIRED} (per-strategy, via `client_order_id`/`strategy_id` already on `SimFillEvent`) | Allowed orders that never became a fill |
| Completed trades | `trade_ledger` count (already measured every prior report) | The final, already-familiar number |
| Conversion rate at every stage | `stage_n / stage_(n-1)` | Where the funnel narrows most for this strategy |
| Months with zero raw setups | Per-calendar-month count of stage-1 bars | Distinguishes "never occurs" months from "occurs but discarded" months |
| Months with setups but zero executions | Stage-1 count > 0 AND completed-trade count = 0, per month | The CEO's own specifically-requested diagnostic — pinpoints WHEN suppression (not absence) happens |
| **Hypothetical isolated-slot trade count** | A SEPARATE, additional measurement run per strategy: `SimulationHarness(..., strategy_id_filter=frozenset({that one id}))` over the SAME window | How many trades this strategy would take with ZERO competition for the shared XAUUSD slot — directly isolates shared-slot suppression from every other stage, without touching the production (all-43) run at all |

**"Without changing production behavior"** (the CEO's own explicit constraint): the isolated-slot runs
are ADDITIONAL, separate simulation runs — exactly the same technique already used to compute
per-strategy attribution in Wave D and the relevance audit's own portfolio variants — never a change
to how the real, all-43, competitive simulation behaves. The instrumentation counters (stages 1–7
above) are read-only additions that tap values the pipeline already computes every bar; none of them
change a `Decision`, a `Signal`, or a fill.

---

## 4. Proposed suppression classification (per strategy)

For each strategy, compare its own funnel shape against the six categories the CEO named. Proposed
(non-binding, to be refined during implementation) decision logic — a strategy may fall into more than
one category if its funnel narrows meaningfully at more than one stage:

| Category | Proposed signature in the funnel |
|---|---|
| **A. Genuine low market frequency** | Raw setup detections themselves are rare (few bars/month with `setup_forming=True`) — the pattern just doesn't occur often in this market. Nothing downstream to blame. |
| **B. Shared-slot suppression** | Raw setups and actionable signals are NOT rare, but `DENY_LIMIT_MAX_PER_SYMBOL` dominates this strategy's own denial reasons, AND the isolated-slot hypothetical trade count is materially higher than its actual (competitive) trade count. |
| **C. Scoring suppression** | Actionable signals occur at a normal rate but are frequently outscored/lost in Scoring Engine conflict resolution before ever reaching Risk Manager. |
| **D. Risk suppression** | Signals reach Risk Manager at a normal rate but are frequently denied for reasons OTHER than the shared slot (spread/liquidity/volatility/cooldown/sizing). |
| **E. Execution suppression** | Risk Manager `ALLOW`s the signal at a normal rate but the resulting order frequently goes unfilled/rejected/expired. |
| **F. Insufficient historical data** | `NEED_CONTEXT` dominates — the strategy's own required lookback/context isn't available often enough in this window (distinct from "the pattern doesn't occur" — the pattern might occur but can't be evaluated). |

**This classification is a diagnostic output, not a scoring change** — it would not feed back into the
Strategy Health System, would not alter any classification in Phase 6.9 or the relevance audit, and
would not itself recommend promoting, demoting, or modifying any strategy.

---

## 5. Explicitly out of scope for Phase 6.9A (per CEO instruction)

- No strategy contract, evaluator, or parameter change.
- No Research Lab (`code/`, `results/`, `knowledge/`) change.
- No Scoring Engine weight, Risk Manager policy, or Execution Engine rule change.
- No change to the Strategy Health System's own scoring methodology.
- No promotion, demotion, or elimination of any strategy based on this phase's own findings.
- No live trading, Telegram, Broker Adapter, or MT5 work.
- **No implementation at all until this specification (or a revised version of it) receives its own
  explicit CEO sign-off.**

---

## 6. Proposed validation requirements (for whenever implementation is approved)

- Every new counter must be a pure, read-only observation of an already-computed pipeline value — no
  new decision logic, mirroring the Phase 6.9 `harness.py` overlay-isolation fix's own precedent
  (additive, backward-compatible, provably a no-op on every existing code path).
- The proposed `RiskEventRecord.strategy_id` addition (§2) must default to `None` and not change the
  shape or meaning of any existing recorded event for any test that does not opt into reading the new
  field.
- Isolated-slot runs must use the identical `SimulationContext`/seed/cost model/risk config as the
  corresponding production (all-43) run, differing ONLY in `strategy_id_filter` — the same discipline
  every portfolio-variant comparison in Phase 6.9 and the relevance audit already followed.
- Determinism: two independent runs of the full instrumented funnel, same inputs, must produce
  byte-identical per-strategy funnel counts (the same standard every prior phase's own backtest met).
- A dedicated regression test proving the new counters never influence any `Decision`, `Signal`, or
  fill outcome — i.e., a run WITH instrumentation enabled and a run WITHOUT it (or with counters simply
  discarded) must produce byte-identical trade ledgers.

---

## 7. Proposed deliverable (for whenever implementation is approved)

A `PHASE_6_9A_STRATEGY_EVIDENCE_FLOW_AUDIT_REPORT.md` containing, per strategy: the full funnel table
(§3), month-level zero-setup/zero-execution flags, the isolated-slot hypothetical trade count next to
the actual competitive trade count, and the suppression-category classification (§4) — for all 43
strategies, none hidden, with the same "do not label insufficient evidence as good or bad" discipline
the relevance audit already applied.

---

**This document proposes; it does not authorize.** Implementation of any part of Phase 6.9A requires
its own explicit CEO approval of this (or a revised) specification.

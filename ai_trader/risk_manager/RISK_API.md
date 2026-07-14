# Risk Manager v1 — API (definition only)

The Risk Manager's public API. **Definition and semantics only; no implementation.** Every method is a
deterministic function of the supplied opportunity + risk context + portfolio state + config + risk state; none
signal, score, learn, execute, or read research. The safe default of every decision path is **DENY**.

- **api_version:** `1.0.0` · **emits:** `RiskDecision` (`RISK_SCHEMA.json`).
- **inputs:** `OpportunityScore` / `OpportunityScore[]` (Scoring Engine), `RiskContext` + `PortfolioState`
  (passed in / Portfolio Manager, read-only), `RiskConfig` (fixed, versioned).
- **failure model:** expected failures return `DENY` decisions or typed results, never thrown across the boundary.
  One bad opportunity never aborts a batch.

---

## 0. Types (summary; full shapes in the schema)
```
OpportunityScore  # input (SCORING_SCHEMA.json)
RiskContext       # passed-in market-risk snapshot (volatility, spread, liquidity, calendar/news, weekend/gap, data_quality)
PortfolioState    # read-only from Portfolio Manager (positions, exposure, leverage, P&L daily/weekly, drawdown, equity)
RiskDecision      # output (RISK_SCHEMA.json)
RiskDecisionBatch { as_of, decisions: RiskDecision[], counts_by_decision, engine_state, generated_at }
SizingResult      { method, risk_per_trade_pct, risk_R, size_units, min_size, max_size, notional, leverage, partial_exit_plan? }
LimitsReport      { engine_state, limits, current_utilization, breaches[] }
ValidationResult  { valid, reasons[] }
Statistics        { batches, decisions_total, allow, deny, by_reason, avg_eval_ms }
EngineHealth      { overall, state, degraded_reasons[], supported_versions }
```

---

## 1. Decision

### `evaluate(opportunities: OpportunityScore[], risk_context: RiskContext, portfolio: PortfolioState) -> RiskDecisionBatch`
The normal entry point. Applies the global state gate, then evaluates each opportunity in **rank order** against a
running portfolio view (an earlier ALLOW consumes budget/slots for later ones), producing one `RiskDecision` each.
- **returns:** `RiskDecisionBatch` (allowed decisions carry sizing + constraints; denied carry reasons).
- **semantics:** deterministic; if `engine_state ∈ {SUSPENDED, EMERGENCY_STOP}` every decision is DENY. Empty
  input → empty batch (valid).
- **failures:** unavailable/stale portfolio → all DENY(`PORTFOLIO_UNAVAILABLE`), engine → DEGRADED; never thrown.

### `allow_trade(opportunity: OpportunityScore, risk_context, portfolio) -> RiskDecision`
Evaluate a single opportunity (the atomic unit) — the policy gates only, plus sizing if allowed. Used for targeted
checks; the running-portfolio effect of a batch is not applied (documented as `single` evaluation).
- **returns:** one `RiskDecision` (ALLOW with sizing/constraints, or DENY with reasons).
- **failures:** invalid/non-actionable opportunity → DENY(`NOT_ACTIONABLE`/`INVALID_INPUT`).

### `position_size(opportunity: OpportunityScore, portfolio: PortfolioState, risk_context) -> SizingResult`
Compute the deterministic position size + caps for an opportunity **assuming it is allowed** (does not itself
apply the policy gates). Used by `evaluate`/`allow_trade` internally and available for inspection.
- **returns:** `SizingResult` (or a zero/`SIZE_BELOW_MIN` result if the budget is insufficient).
- **failures:** missing stop / non-positive stop distance → zero size with reason `INVALID_STOP`.

---

## 2. Portfolio limits & introspection

### `portfolio_limits(portfolio: PortfolioState) -> LimitsReport`
Report the configured limits, current utilization (positions, exposure, leverage, daily/weekly P&L, drawdown), and
any breaches — WITHOUT evaluating a specific opportunity. For dashboards and the Portfolio Manager.
- **returns:** `LimitsReport { engine_state, limits, current_utilization, breaches[] }`.

### `validate(decision: RiskDecision) -> ValidationResult`
Validate a decision against `RISK_SCHEMA.json` + semantic rules (ALLOW ⇒ sizing≥min + valid stop + state READY;
DENY ⇒ non-empty reasons). Pure; used internally before emit and available to consumers.
- **returns:** `ValidationResult { valid, reasons[] }`.

### `statistics() -> Statistics`
Per-batch and cumulative allow/deny counts, reasons breakdown, average evaluation time. For the Performance
Monitor.

### `health() -> EngineHealth`
Overall health (`OK`/`DEGRADED`/`FAILED`), current global state (READY/SUSPENDED/EMERGENCY_STOP), degraded
reasons, and the supported version window. Reports only.

### `versions() -> { risk_engine_version, risk_schema_version, risk_policy_version, supported: { scoring_schema_major, interface_major } }`
Version lines + support window for the end-to-end handshake (Scoring Engine → Risk Manager → Execution Engine).

---

## 3. Operational controls (operator / monitor only)
### `suspend(reason) -> EngineHealth` / `resume() -> EngineHealth`
Soft halt (`SUSPENDED`) and recovery per the recovery policy (guarded: resume only if no guard is tripped).
### `emergency_stop(reason) -> EngineHealth` / `clear_emergency() -> EngineHealth`
Hard stop (`EMERGENCY_STOP`, all-DENY, may instruct Execution to flatten) and operator clear (guarded:
PortfolioState reconciled + no guard tripped). The kill switch maps to `emergency_stop`.
> These are operator/monitor controls — they change the global state; they never place or size a trade.

---

## 4. Contract of use (invariants the caller can rely on)
1. **One decision per opportunity**, always (ALLOW or DENY).
2. **Deterministic:** identical `(opportunities in rank order, RiskContext, PortfolioState, RiskConfig, state)` ⇒
   identical `RiskDecision[]`. No randomness.
3. **Fail-safe = DENY:** any missing/invalid input, breach, or fault yields DENY (or global SUSPENDED/EMERGENCY_
   STOP); never a fabricated ALLOW.
4. **Risk-first sizing:** an ALLOW's monetary risk equals `risk_per_trade_pct × equity` by construction; caps are
   hard clamps.
5. **No signal/score/execution/learning/research** anywhere in the API.

## 5. What the API deliberately does NOT provide
- No `generate_signal`, `score`, `submit_order`, `fill`, or broker method.
- No method that mutates a strategy, contract, score, or research.
- No direct link to the Broker, Research Lab, Knowledge Base, Strategy Library, Signal Engine, or Learning Engine.

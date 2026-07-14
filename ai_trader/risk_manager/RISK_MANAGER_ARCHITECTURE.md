# Risk Manager v1 — Architecture (design)

The Risk Manager decides ALLOW/DENY per ranked opportunity and, when allowed, sets the position size and execution
constraints. It is a pure, deterministic decision function; it never signals, scores, learns, executes, or reads
research. Design only — no code.

---

## 1. Purpose
Be the **final risk gate** before execution: given a ranked opportunity, the current portfolio, and the risk
policy, decide deterministically whether the trade may proceed and under what constraints. The safe default is
**DENY**.

## 2. Responsibilities & boundaries
**Responsibilities**
1. Consume ranked `OpportunityScore`s from the Scoring Engine.
2. Read the current `PortfolioState` (Portfolio Manager) and account state.
3. Apply the deterministic risk policy (`RISK_POLICY.md`): pre-trade filters → portfolio limits → loss/drawdown
   guards → cooldowns → global state → ALLOW/DENY.
4. For ALLOW, compute position size + execution constraints (`POSITION_SIZING.md`).
5. Own the global risk state and the emergency stop / kill switch / suspension / recovery.
6. Emit `RiskDecision`s (allowed → Execution Engine; denied → back to caller with reasons). Report health/stats.

**Hard boundaries (never)**
- Never produce signals, evaluate strategies, or score opportunities.
- Never learn/adapt (limits are fixed, versioned config).
- Never execute/route orders or talk to the broker.
- Never read Research Lab / Knowledge Base / Strategy Library / Signal Engine.
- Never fetch market data itself (the market-risk context is passed in).

## 3. Inputs & outputs
**Inputs**
- `OpportunityScore[]` (Scoring Engine, `SCORING_SCHEMA.json`): `total_score`, `recommendation`, `state`,
  `direction`, `trade_context` (entry/stop/target/risk_R), `strategy_id`, `symbol`, `as_of`.
- `PortfolioState` (Portfolio Manager, read-only): open positions (symbol, direction, size, entry, age, correlation
  group), aggregate exposure, leverage, realized/unrealized P&L (intraday/daily/weekly), equity high-water mark,
  current drawdown.
- `RiskContext` (passed in by the orchestrator, assembled from the already-flowing MarketContext — NOT fetched):
  market-risk snapshot per symbol (volatility/ATR, spread, liquidity proxy, session, weekend/gap flags, calendar/
  news flags), `data_quality`, `as_of`.
- `RiskConfig` (fixed, versioned): all policy thresholds + sizing parameters.

**Outputs**
- `RiskDecision[]` (`RISK_SCHEMA.json`): per opportunity — `decision` (ALLOW/DENY), `denied_reasons[]`,
  `applied_rules[]`, `sizing` (method, risk_pct, risk_R, size, caps, leverage), `constraints` (validated entry/
  stop/target, max_hold, valid_until, max_slippage, session), `portfolio_impact`, `engine_state`.

## 4. Internal components
```
                     ┌──────────────────────────── RISK MANAGER ─────────────────────────────┐
 OpportunityScore ──▶│  Intake            (bind ranked opportunities + RiskContext + Portfolio)│
 (Scoring Engine)    │        │                                                                │
 PortfolioState ────▶│        ▼                                                                │
 (Portfolio Mgr)     │  Global State Gate   (READY / SUSPENDED / EMERGENCY_STOP · kill switch) │
                     │        │  (if not READY → all DENY)                                     │
                     │        ▼                                                                │
                     │  Pre-Trade Filters   (volatility/spread/liquidity/news/weekend/gap)     │
                     │        ▼                                                                │
                     │  Portfolio Limits    (max positions/symbol/correlated/exposure/leverage/│
                     │        │              overnight/event)                                  │
                     │        ▼                                                                │
                     │  Loss & Drawdown Guards (daily/weekly loss, max drawdown, cooldowns)    │
                     │        ▼                                                                │
                     │  Decision (ALLOW/DENY) ── DENY → assemble reasons                       │
                     │        │ ALLOW                                                          │
                     │        ▼                                                                │
                     │  Position Sizer      (risk-per-trade + vol/ATR scaling + caps)          │
                     │        ▼                                                                │
                     │  Constraint Builder  (validate entry/stop/target, max_hold, valid_until)│
                     │        ▼                                                                │
                     │  Validator / Output  (schema-validate RiskDecision)                     │
                     │        ▼   Ledger (read-only view of realized P&L/cooldowns) · Health · Statistics │
                     └───────────────┬────────────────────────────────────────────────────────┘
                                     ▼
                               RiskDecision[]  →  Execution Engine (ALLOW) / caller (DENY)
```
- **Intake** — binds the ranked opportunities with the portfolio + risk context for this `as_of`.
- **Global State Gate** — if `SUSPENDED`/`EMERGENCY_STOP` or kill-switch, every decision is DENY (short-circuit).
- **Pre-Trade Filters** — per-opportunity market-condition gates (vol/spread/liquidity/news/weekend/gap).
- **Portfolio Limits** — count/exposure/correlation/leverage/overnight/event caps against `PortfolioState`.
- **Loss & Drawdown Guards** — daily/weekly loss, max drawdown, post-loss cooldowns.
- **Position Sizer** — deterministic sizing for allowed trades (`POSITION_SIZING.md`).
- **Constraint Builder** — validates/clamps prices, sets max hold, expiry, slippage cap, session window.
- **Ledger** — a READ-ONLY internal accounting view (realized P&L, cooldown clocks) fed by the Portfolio Manager;
  the Risk Manager does not own truth of fills (it reads state, it does not book trades).
- **Validator / Output / Health / Statistics** — schema validation, emission, reporting.

## 5. Risk pipeline (evaluation order — first failing gate denies)
```
OpportunityScore
  0. Global State: READY? else DENY(SUSPENDED/EMERGENCY_STOP/KILL_SWITCH)
  1. Opportunity sanity: actionable state + valid trade_context? else DENY(NOT_ACTIONABLE/INVALID_INPUT)
  2. Recommendation floor: recommendation ∈ {STRONG,MODERATE,WEAK}_OPPORTUNITY? else DENY(BELOW_FLOOR) (WATCH/SKIP→DENY)
  3. Pre-trade filters: volatility/spread/liquidity/news/weekend/gap within policy? else DENY(FILTER_*)
  4. Portfolio limits: positions/symbol/correlated/exposure/leverage/overnight/event within caps? else DENY(LIMIT_*)
  5. Loss/drawdown guards: daily/weekly loss + max drawdown not breached? else DENY(LOSS_*/DRAWDOWN_*) → may SUSPEND
  6. Cooldowns: not in post-loss / consecutive-loss cooldown? else DENY(COOLDOWN_*)
  → ALLOW
  7. Position sizing: compute size (risk-per-trade × equity / stop-distance, vol-scaled, capped)
        size < min → DENY(SIZE_BELOW_MIN) ; size clamped to max
  8. Constraints: validate entry/stop/target (stop present & on correct side), set max_hold/valid_until/slippage
  → emit RiskDecision(ALLOW, sizing, constraints)
```
The order is fixed and deterministic; the first failing gate produces DENY with that reason. Multiple opportunities
are evaluated against a **running, deterministic view** of the portfolio (an ALLOW earlier in the ranked batch
consumes budget/slots for later ones — evaluated in rank order so the result is reproducible).

## 6. Validation
- Every emitted `RiskDecision` is validated against `RISK_SCHEMA.json` before output; a validation failure → a
  fail-safe `DENY` decision with reason `INTERNAL_VALIDATION_FAILED` (never a malformed ALLOW).
- Semantic checks: ALLOW ⇒ `sizing.size ≥ min` and a valid stop; DENY ⇒ non-empty `denied_reasons`; sizing risk
  never exceeds `risk_per_trade` cap; portfolio_impact consistent with the running portfolio view.

## 7. Failure modes & fail-safe
| condition | handling |
|---|---|
| opportunity non-actionable / invalid input | DENY(NOT_ACTIONABLE / INVALID_INPUT) |
| PortfolioState unavailable/stale | DENY(PORTFOLIO_UNAVAILABLE) + engine → DEGRADED |
| RiskContext missing/degraded data | conservative filters (treat as worst-case) → likely DENY(DATA_DEGRADED) |
| any limit breached | DENY(LIMIT_*/LOSS_*/DRAWDOWN_*) |
| daily/weekly loss or max drawdown hit | DENY(LOSS_*) + engine → SUSPENDED (all-DENY until recovery) |
| kill switch engaged | engine → EMERGENCY_STOP (all-DENY) |
| internal/sizing/validation error | DENY(INTERNAL_*) ; batch continues |

**Fail-safe policy:** the resting decision is **DENY**; abnormal global faults escalate to `SUSPENDED`/
`EMERGENCY_STOP`. The Risk Manager can only ever be MORE conservative under uncertainty, never less.

## 8. Data flow
```
Scoring Engine → RiskDecisionBatch = RiskManager.evaluate(OpportunityScore[], RiskContext, PortfolioState)
   Global State Gate → per opportunity (rank order): filters → limits → guards → cooldowns → ALLOW/DENY
       ALLOW → Position Sizer → Constraint Builder → RiskDecision(ALLOW)
       DENY  → RiskDecision(DENY, reasons)
   running portfolio view updated per ALLOW (budget/slots consumed) for subsequent opportunities
→ Execution Engine (ALLOW) ; caller (DENY) ; Health/Statistics updated
```

## 9. Determinism
- Pure function of `(OpportunityScore batch in rank order, RiskContext, PortfolioState snapshot, RiskConfig,
  risk_state)`. No ML, no randomness, no wall-clock in the logic.
- The running-portfolio view is applied in the batch's deterministic rank order, so ALLOW/DENY outcomes are
  reproducible. Identical inputs ⇒ identical `RiskDecision[]`.
- Replay parity: given the same opportunity + portfolio + context streams, replay reproduces live decisions.

## 10. Performance model
- **Batching:** one `evaluate()` per Scoring Engine batch; opportunities processed in rank order (the running
  portfolio view makes this order-dependent by design, so it is sequential, not parallel).
- **Caching:** `RiskConfig` and the per-cycle `PortfolioState`/`RiskContext` snapshots are bound once per cycle;
  no cross-cycle result caching.
- **Latency/memory:** bounded per batch; holds only the current batch + snapshots; no unbounded history. Concrete
  latency targets are a build-time concern; the design fixes that budgets exist and DENY is the timeout default.

## 11. Versioning
- **`risk_engine_version`** — module implementation/spec version.
- **`risk_schema_version`** — `RiskDecision` shape (`RISK_SCHEMA.json`). MAJOR breaking; MINOR additive/new reason
  code; PATCH clarification.
- **`risk_policy_version`** — the policy thresholds + sizing parameters (`RISK_POLICY.md`/`POSITION_SIZING.md`).
  Any limit/parameter change bumps this so every decision is reproducible against the exact policy that produced
  it.
- Echoes consumed `scoring_schema_version` + `interface_version`.
- **Compatibility:** the Execution Engine declares the `risk_schema_version` MAJOR it supports; the Risk Manager
  emits a compatible MAJOR; unknown optional fields ignored. **Migration:** a schema MAJOR ships a field mapping.
  **Deprecation:** deprecated fields/reason codes emitted one MAJOR with a note, then removed.

## 12. Startup & shutdown
**Startup**
```
1. load RiskConfig (limits, sizing params, supported scoring/risk schema versions)
2. handshake Scoring Engine (scoring_schema major) + Execution Engine (risk_schema major) + Portfolio Manager
3. reconcile initial risk_state from PortfolioState (e.g. if daily loss already breached → SUSPENDED)
4. IDLE → READY (or SUSPENDED/EMERGENCY_STOP if a guard is already tripped)
```
**Shutdown**
```
1. stop accepting new evaluations ; finish/deny the in-flight batch
2. emit final statistics()/health() ; release snapshots (hold no truth of fills)
```
Fail-safe: if the Portfolio Manager or Execution Engine handshake fails, the Risk Manager starts DEGRADED and
denies all trades until the dependency is available — it never allows a trade it cannot size or account for.

## 13. Interaction matrix (who may talk to whom)
| module | may the Risk Manager talk to it? | direction / purpose |
|---|---|---|
| **Scoring Engine** | YES | ← ranked `OpportunityScore[]` (input). |
| **Portfolio Manager** | YES | ← read `PortfolioState`/account (positions, exposure, P&L, drawdown). |
| **Execution Engine** | YES | → `RiskDecision` (ALLOW) with size + constraints. |
| **Research Lab / Knowledge Base / Strategy Library** | NO | never. |
| **Signal Engine** | NO | never (upstream of Scoring; not a Risk input). |
| **Broker Connector** | NO | never — the Execution Engine owns venue contact. |
| **Learning Engine** | NO | never — the Risk Manager does not learn. |

Rule (CEO-fixed): allowed direct = **Scoring Engine, Portfolio Manager, Execution Engine**; forbidden = **Research
Lab, Knowledge Base, Strategy Library, Signal Engine, Broker, Learning Engine**.

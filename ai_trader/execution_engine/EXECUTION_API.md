# Execution Engine v1 — API (definition only)

The Execution Engine's public API. **Definition and semantics only; no implementation, no broker integration.**
Order construction/validation are deterministic given the inputs; order outcomes depend on the (future) venue and
are always reconciled to a definite state. Every path is fail-safe (do no harm; no duplicates).

- **api_version:** `1.0.0` · **builds:** `OrderRequest` (`ORDER_SCHEMA.json`) · **emits:** `OrderStatus`,
  `ExecutionResult`, `ExecutionReport`.
- **inputs:** `RiskDecision` (Risk Manager, ALLOW only), `PortfolioState` (Portfolio Manager, read), abstract
  `BrokerCapabilities` (Broker Adapter contract).
- **failure model:** expected failures return terminal `OrderStatus`/typed results, never thrown across the
  boundary. Idempotent by `client_order_id`.

---

## 0. Types (summary; full shapes in the schema)
```
RiskDecision       # input (RISK_SCHEMA.json, decision=ALLOW)
PortfolioState     # read-only from Portfolio Manager
BrokerCapabilities # abstract: supported order types/TIF, tick_size, lot_step, min/max qty, market_status
OrderRequest       # built order (ORDER_SCHEMA.json)
OrderStatus        { order_request_id, client_order_id, state, filled_qty, remaining_qty, avg_price, reasons[] }
ExecutionResult    { order_request_id, terminal_state, filled_qty, avg_price, fees, reasons[] }
ExecutionReport    { as_of, results: ExecutionResult[], fills[], counts_by_state }
ValidationResult   { valid, reasons[] }
Statistics         { orders_total, by_state, fills, rejects, failures, avg_submit_ms }
EngineHealth       { overall, state, degraded_reasons[], broker_available, supported_versions }
```

---

## 1. Execution

### `execute(decision: RiskDecision, portfolio: PortfolioState) -> OrderStatus`
The normal entry point. Accepts an ALLOW decision, builds an idempotent `OrderRequest`, validates it, and submits
it via the Broker Adapter, returning the initial/current `OrderStatus`. A DENY/non-ALLOW decision is a no-op
(returns a status noting nothing to execute).
- **returns:** `OrderStatus` (may be `REJECTED` pre-submit, or in-flight).
- **semantics:** idempotent — calling with a decision whose `client_order_id` is already known returns the existing
  `OrderStatus` (no duplicate order).
- **failures:** validation fail → `REJECTED`; broker unavailable → `QUEUED`/`FAILED` per policy; never thrown.

### `build_order(decision: RiskDecision, portfolio: PortfolioState, caps: BrokerCapabilities) -> OrderRequest`
Deterministically construct (but do NOT submit) the `OrderRequest` from a decision: map order type/TIF, size,
prices, protective legs, and the idempotent `client_order_id`. For inspection/testing.
- **returns:** an `OrderRequest` (schema-valid) or a build error result.
- **failures:** unsupported order type/TIF for the caps → a rejected build with reason.

### `validate_order(order: OrderRequest, caps: BrokerCapabilities, portfolio: PortfolioState) -> ValidationResult`
Run the execution-mechanics validation suite (tick/lot/qty/price/slippage/time/market/direction/duplicate/
consistency) WITHOUT submitting. Pure; used internally before submit and available to tooling.
- **returns:** `ValidationResult { valid, reasons[] }`.

---

## 2. Lifecycle control & retrieval

### `cancel(client_order_id) -> OrderStatus`
Request cancellation of a working order. Confirms `CANCELLED`, or reconciles a cancel↔fill race to the true state.
- **failures:** unknown id → `NotFound`; already terminal → returns the terminal status (idempotent).

### `status(client_order_id) -> OrderStatus | NotFound`
Return the current lifecycle state + fill progress of an order from the Order Ledger.

### `reconcile(client_order_id?) -> OrderStatus | ExecutionReport`
Force a reconciliation against the Broker Adapter for one order (or all in-flight): resolve ambiguous/timeout
states to definite ones. Used on startup, after faults, and before any retry.
- **returns:** the resolved `OrderStatus` (or an `ExecutionReport` for the all-in-flight case).

### `report(as_of?) -> ExecutionReport`
Return the `ExecutionResult`s + fills for the cycle (or current), for the Portfolio Manager and audit.

---

## 3. Operational controls (Risk Manager / operator)
### `emergency_flatten(scope) -> ExecutionReport`
Executed on the Risk Manager's command: issue reduce-only closing orders for the in-scope positions, refuse new
opening orders (engine → `EMERGENCY_FLATTEN`). The Execution Engine performs the closes; it does not decide to
flatten (the Risk Manager does).

---

## 4. Introspection

### `statistics() -> Statistics`
Per-cycle and cumulative counts by order state, fills, rejects, failures, average submit latency. For the
Performance Monitor.

### `health() -> EngineHealth`
Overall health (`OK`/`DEGRADED`/`FAILED`), engine state (READY/RECONCILING/DEGRADED/EMERGENCY_FLATTEN/…), broker
availability, degraded reasons, supported version window. Reports only.

### `versions() -> { execution_engine_version, order_schema_version, broker_adapter_contract_version, supported: { risk_schema_major } }`
Version lines + support window for the end-to-end handshake (Risk Manager → Execution Engine → Broker Adapter).

---

## 5. Contract of use (invariants the caller can rely on)
1. **Idempotent:** a decision executes at most once; retries/restarts never duplicate an order.
2. **Deterministic construction/validation:** identical `(decision, portfolio, caps, config)` ⇒ identical
   `OrderRequest` and validation outcome.
3. **Definite terminal state:** every order reaches exactly one terminal state; ambiguity is reconciled, never
   assumed.
4. **Fail-safe:** any uncertainty → reconcile/hold, never a blind or duplicate order; unrecoverable → `FAILED`
   (reported), never silent.
5. **No risk/signal/score/learning/research:** the API executes approved decisions only.

## 6. What the API deliberately does NOT provide
- No `generate_signal`, `score`, `evaluate_risk`, `size` (sizing came from the Risk Manager), or learning method.
- No method that reads Research Lab / KB / Strategy Library / Market Scanner / Signal Engine / Scoring Engine.
- No direct broker method beyond the abstract Broker Adapter contract (no venue integration in v1).

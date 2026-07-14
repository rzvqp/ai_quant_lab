# Execution Engine v1 — Architecture (design)

The Execution Engine transforms an approved `RiskDecision` into a validated, idempotent `OrderRequest` and manages
its lifecycle to a terminal state through an abstract Broker Adapter. It re-decides nothing; it executes faithfully
or fails safely. Design only — no code, no broker integration.

---

## 1. Purpose
Be the **faithful, idempotent executor** of decisions already approved upstream: turn `RiskDecision(ALLOW)` into a
well-formed order, submit it, track it to a terminal state, and report the outcome — without ever re-evaluating
whether to trade.

## 2. Responsibilities & boundaries
**Responsibilities**
1. Consume approved `RiskDecision`s (Risk Manager) and read `PortfolioState` (Portfolio Manager).
2. Build an `OrderRequest` honoring the decision's `sizing` + `constraints` and the abstract `BrokerCapabilities`.
3. Validate order mechanics (`§8`) before submission.
4. Manage the order lifecycle (`ORDER_LIFECYCLE.md`) idempotently via the Broker Adapter contract.
5. Emit `OrderStatus`, `ExecutionResult`, `ExecutionReport`; report fills to the Portfolio Manager.
6. Enforce the fail-safe policy on faults; own the emergency-flatten mechanics when the Risk Manager commands them.

**Hard boundaries (never)**
- Never generate signals, evaluate strategies, or score.
- Never manage portfolio risk or re-size (executes the Risk Manager's size; its checks are consistency guards).
- Never learn/adapt.
- Never read Research Lab / KB / Strategy Library / Market Scanner / Signal Engine / Scoring Engine / Learning
  Engine.
- Never contact a venue except through the abstract Broker Adapter (future).

## 3. Inputs
- **`RiskDecision`** (Risk Manager, `RISK_SCHEMA.json`, `decision=ALLOW`): `sizing` (size_units, risk_R, caps),
  `constraints` (entry/stop/target, max_hold, valid_until, max_slippage, allowed_session, reduce_only),
  `direction`, `symbol`, `as_of`, refs. Only ALLOW decisions are actioned; DENY are ignored (nothing to execute).
- **`PortfolioState`** (Portfolio Manager, read-only): open positions, pending orders (for duplicate/consistency
  checks and reduce-only correctness), account/equity for notional checks.
- **`ExecutionConstraints`**: the constraint block carried on the `RiskDecision` (the Execution Engine adds only
  order-mechanics constraints — TIF, order type mapping — never risk constraints).
- **`BrokerCapabilities`** (abstract, from the Broker Adapter contract): supported order types + time-in-force,
  tick size, lot step, min/max quantity, market hours/status, supported contingent orders (OCO/bracket). Abstract
  in v1 — a declared capability set, not a live integration.

## 4. Outputs
- **`OrderRequest`** (`ORDER_SCHEMA.json`): the fully-specified, idempotent order to hand the Broker Adapter.
- **`OrderStatus`**: the current lifecycle state of an order (`CREATED … FILLED/…/FAILED`) + fill progress.
- **`ExecutionResult`**: the terminal outcome of one order (filled qty, avg price, fees, terminal state, reasons).
- **`ExecutionReport`**: a per-cycle/portfolio-facing report bundling results + fills to the Portfolio Manager.

## 5. Internal components
```
                    ┌──────────────────────────── EXECUTION ENGINE ─────────────────────────────┐
 RiskDecision ─────▶│  Intake              (accept ALLOW; ignore DENY; bind PortfolioState)      │
 (Risk Manager)     │        │                                                                   │
 PortfolioState ───▶│        ▼                                                                   │
 (Portfolio Mgr)    │  Order Builder       (map decision+constraints → OrderRequest; assign      │
                    │        │              client_order_id (idempotent); choose order type/TIF)  │
                    │        ▼                                                                     │
                    │  Order Validator     (tick/lot/qty/price/slippage/time/market/direction/    │
                    │        │              duplicate — §8)                                        │
                    │        ▼ valid                                                               │
                    │  Order Router / Queue (submit to Broker Adapter; enforce rate/idempotency)  │
                    │        │                                                                     │
                    │        ▼                                                                     │
                    │  Lifecycle Tracker    (ACK/fills/partials/cancel/reject/expire; reconcile)  │
                    │        │                                                                     │
                    │        ▼                                                                     │
                    │  Reconciler           (query broker on uncertainty; resolve unknown states) │
                    │        ▼                                                                     │
                    │  Result/Reporter      (ExecutionResult + ExecutionReport → Portfolio Mgr)   │
                    │        ▼   Order Ledger (own state of live orders) · Health · Statistics     │
                    └───────────────┬────────────────────────────────────────────────────────────┘
                                    ▼
                          Broker Adapter (future)  →  venue
```
- **Intake** — accepts ALLOW decisions; a DENY (or non-ALLOW) is a no-op.
- **Order Builder** — maps the decision to an `OrderRequest`, assigns an **idempotent `client_order_id`** derived
  from `decision_id` (so a retry never creates a second order), and selects order type + time-in-force from the
  constraints and `BrokerCapabilities`.
- **Order Validator** — the mechanical validation suite (§8).
- **Order Router / Queue** — submits to the Broker Adapter under rate limits and idempotency; queues if the
  adapter is momentarily unavailable (bounded), never blind-resends.
- **Lifecycle Tracker** — maps broker events to lifecycle states; handles partial fills, cancels, rejects,
  expiries.
- **Reconciler** — on timeout/ambiguity, queries order status before any resend (fail-safe against duplicates).
- **Order Ledger** — the Execution Engine's own record of live/terminal orders (source of truth for order state;
  the Portfolio Manager owns position truth via reported fills).
- **Result/Reporter, Health, Statistics** — outcome emission + reporting.

## 6. Execution pipeline (per approved decision)
```
RiskDecision(ALLOW)
  1. Intake: accept (ignore non-ALLOW)
  2. Build: OrderRequest (client_order_id = f(decision_id); order type/TIF; qty from sizing; prices from constraints)
  3. Validate (§8): fail → REJECTED (pre-submit) with reason (never sent)
  4. Duplicate guard: client_order_id already known? → do NOT resend; return existing OrderStatus (idempotent)
  5. Submit: Order Router → Broker Adapter → SUBMITTED
  6. Track: ACKNOWLEDGED → (PARTIALLY_FILLED)* → FILLED | CANCELLED | REJECTED | EXPIRED | FAILED
  7. Reconcile on uncertainty (timeout/ambiguous): query status; resolve to a definite state before any action
  8. Report: ExecutionResult (terminal) + fills → Portfolio Manager; ExecutionReport for the cycle
```

## 7. Data flow
```
Risk Manager → ExecutionEngine.execute(RiskDecision ALLOW, PortfolioState)
   Build → Validate → (duplicate guard) → Submit(Broker Adapter) → Lifecycle Tracker ⇄ Broker events
   terminal → ExecutionResult ; fills → Portfolio Manager (report_fill) ; Order Ledger updated
Health/Statistics updated per order/cycle.
```
The Execution Engine owns ORDER state (its Ledger); the Portfolio Manager owns POSITION state (updated from
reported fills). This split keeps risk/portfolio accounting and order mechanics cleanly separated.

## 8. Execution validation (mechanics, NOT risk)
Before submission the Order Validator checks (fail → pre-submit `REJECTED` with a reason; never sent to venue):
| check | rule |
|---|---|
| **direction validation** | order side matches the decision's direction (LONG⇒BUY-to-open, SHORT⇒SELL-to-open; reduce_only closes) |
| **position-limit consistency** | a *defensive* check that the order does not exceed what the `RiskDecision` authorized and is consistent with `PortfolioState` (e.g. not opening a 2nd position the decision didn't authorize) — a consistency guard, **not** a risk re-decision |
| **duplicate prevention** | `client_order_id` idempotency: an order for this `decision_id` already live/terminal ⇒ no new order |
| **price validation** | limit/stop prices present as required by the order type, on the correct side, finite |
| **tick size** | prices are multiples of `BrokerCapabilities.tick_size` (else round per policy or reject) |
| **lot size** | quantity is a multiple of `lot_step` |
| **minimum quantity** | qty ≥ `min_qty` (else `REJECTED` — matches Risk Manager's SIZE_BELOW_MIN intent) |
| **maximum quantity** | qty ≤ `max_qty` (clamp per policy or reject) |
| **slippage limits** | `max_slippage` set for market/marketable orders; reject if unset where required |
| **time restrictions** | within `allowed_session`; respect `valid_until`/`expire_time`; TIF consistent |
| **market status** | `BrokerCapabilities.market_status` open/tradable for the symbol (else queue or reject per policy) |
These are order-mechanics/consistency validations only. Risk was already decided by the Risk Manager.

## 9. Failure modes
Summarized here; full policy in `EXECUTION_FAILURE_POLICY.md`.
| condition | handling (fail-safe) |
|---|---|
| broker unavailable | queue (bounded) or `FAILED`; never blind-resend; escalate health DEGRADED |
| submit/ack timeout | Reconciler queries status before any resend (no duplicates) |
| network failure mid-flight | order state UNKNOWN → reconcile → resolve to definite state |
| broker rejection | `REJECTED` with broker reason; no auto-retry unless policy-eligible |
| partial fill | `PARTIALLY_FILLED`; manage remainder per TIF (IOC/FOK cancel remainder; GTC/DAY keep) |
| cancel request | attempt cancel; confirm `CANCELLED` (or note race with a fill) |
| internal/build/validation error | pre-submit `REJECTED`/`FAILED`; nothing sent; batch continues |

## 10. Startup & shutdown
**Startup**
```
1. load ExecConfig (retry/idempotency/rate limits, supported risk/order schema versions, BrokerCapabilities profile)
2. handshake Risk Manager (risk_schema major) + Portfolio Manager + Broker Adapter (capabilities)
3. RECONCILE: query the Broker Adapter for any live orders from a prior run; rebuild the Order Ledger (idempotent recovery)
4. IDLE → READY
```
**Shutdown**
```
1. stop accepting new decisions
2. reconcile in-flight orders to a definite state (do NOT abandon unknown orders)
3. emit final ExecutionReport / statistics()/health(); persist the Order Ledger for next-run reconciliation
```
Startup reconciliation is mandatory: the Execution Engine must never start blind and risk duplicating a
pre-existing order.

## 11. Performance model
- **Throughput/latency:** orders are handled per approved decision; submission is bounded by broker rate limits;
  latency budgets exist per stage with fail-safe timeouts → reconcile (never blind action).
- **Idempotency & retries:** every submission carries a stable `client_order_id`; retries are safe (dedup at the
  adapter). Retry policy is bounded and reconcile-first.
- **Concurrency:** distinct orders (distinct `client_order_id`) may be in flight concurrently; per-order state is
  serialized (no concurrent conflicting transitions on one order).
- **Memory:** the Order Ledger holds live + recent-terminal orders (bounded retention); no unbounded history.
- **Determinism:** order *construction and validation* are deterministic given `(RiskDecision, PortfolioState,
  BrokerCapabilities, ExecConfig)`. Order *outcomes* depend on the venue (future) and are therefore not
  deterministic — but they are always reconciled to a definite lifecycle state.

## 12. Versioning
- **`execution_engine_version`** — module implementation/spec version.
- **`order_schema_version`** — `OrderRequest` shape (`ORDER_SCHEMA.json`). MAJOR breaking; MINOR additive/new
  order type or TIF value; PATCH clarification.
- **`broker_adapter_contract_version`** — the abstract adapter contract (capabilities + event model).
- Echoes consumed `risk_schema_version`. **Compatibility:** the Broker Adapter declares the
  `order_schema_version`/contract MAJOR it supports; the Execution Engine emits a compatible MAJOR. **Migration:**
  schema MAJOR ships a field mapping. **Deprecation:** deprecated fields/types emitted one MAJOR with a note.

## 13. Interaction matrix (who may talk to whom)
| module | may the Execution Engine talk to it? | direction / purpose |
|---|---|---|
| **Risk Manager** | YES | ← approved `RiskDecision` (input); ← emergency-flatten command. |
| **Portfolio Manager** | YES | ← read `PortfolioState`; → report fills / `ExecutionReport`. |
| **Broker Adapter (future)** | YES | ↔ submit `OrderRequest`, receive acks/fills/rejects (the only venue boundary). |
| **Research Lab / Knowledge Base / Strategy Library** | NO | never. |
| **Market Scanner / Signal Engine / Scoring Engine** | NO | never (all upstream of Risk). |
| **Learning Engine** | NO | never — the Execution Engine does not learn. |

Rule (CEO-fixed): allowed direct = **Risk Manager, Portfolio Manager, Broker Adapter (future)**; forbidden =
**Research Lab, Knowledge Base, Strategy Library, Market Scanner, Signal Engine, Scoring Engine, Learning Engine**.

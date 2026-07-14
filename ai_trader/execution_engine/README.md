# Execution Engine v1 — Phase 5.6 (design)

The **Execution Engine** is the sixth module of the AI Trader. Its single responsibility is to **transform an
approved `RiskDecision` into an executable `OrderRequest`** and manage that order's lifecycle to a terminal state
through an abstract **Broker Adapter** (future). It is the mechanical hand of the system — it decides nothing about
what or whether to trade; that was already decided upstream.

**This package is documentation, architecture, and JSON Schema only.** No runtime code, no executable logic, no
broker integration, no paper trading, no simulation, no backtests, no research. It modifies nothing: Research Lab,
engine, Strategy Library, Strategy Interface, Market Scanner, Strategy Manager, Signal Engine, Scoring Engine, Risk
Manager, S1–S51, Wave 1, Knowledge Graph, holdout are all untouched. Everything is additive inside
`ai_trader/execution_engine/`.

## Responsibilities
- Receive an **approved** `RiskDecision` (ALLOW, with size + constraints) from the Risk Manager.
- Build a well-formed, idempotent `OrderRequest` (`ORDER_SCHEMA.json`) honoring the decision's constraints and the
  abstract `BrokerCapabilities`.
- Validate the order (tick/lot/qty/price/slippage/time/market-status/duplicate/direction) before submission.
- Manage the order lifecycle (`ORDER_LIFECYCLE.md`) — submit, track acknowledgements/fills, handle
  partial fills, cancels, rejects, expiries, and failures — via the Broker Adapter contract.
- Emit standardized `OrderStatus`, `ExecutionResult`, and `ExecutionReport`; report fills to the Portfolio Manager.

## What it is — and is NOT
| the Execution Engine DOES | the Execution Engine does NOT |
|---|---|
| turn an approved `RiskDecision` into an `OrderRequest` | generate signals |
| validate order mechanics (tick/lot/qty/price/slippage/time/market) | evaluate strategies or score opportunities |
| manage the order lifecycle idempotently (retries never double-execute) | manage portfolio risk (that is the Risk Manager) |
| talk to the Broker Adapter (abstract; real adapter is future) | learn or adapt |
| report fills/status to the Portfolio Manager | access Research Lab / KB / Strategy Library / upstream engines |
| enforce fail-safe on broker/network faults | change contracts, parameters, or strategies |

It is a **deterministic order-construction + lifecycle-management module**. It never re-decides risk; it can only
faithfully execute an approved decision or fail safely. Order *outcomes* depend on the venue (future), but order
*construction and validation* are deterministic given the inputs.

## Boundaries
- **Never** generates signals, evaluates strategies, or scores.
- **Never** manages portfolio risk or re-sizes (it executes the Risk Manager's size; its "position-limit
  validation" is a defensive consistency/idempotency check, not a risk decision — see architecture §8).
- **Never** learns/adapts.
- **Never** reads Research Lab / Knowledge Base / Strategy Library / Market Scanner / Signal Engine / Scoring
  Engine / Learning Engine.
- The **only** venue contact is the abstract Broker Adapter (future); v1 defines the contract, not an integration.

## Pipeline position
```
… Risk Manager → [Execution Engine] → Broker Adapter (future) → venue
     RiskDecision(ALLOW)     OrderRequest / lifecycle / ExecutionResult
             ▲                                   │ fills/status
   PortfolioState (Portfolio Manager, read) ◀────┘ ExecutionReport (fills reported to Portfolio Manager)
```

## Module interaction (fixed)
- **Allowed direct:** Risk Manager (input: approved decisions), Portfolio Manager (read state; report fills),
  Broker Adapter (future; the abstract venue boundary).
- **Forbidden (never):** Research Lab, Knowledge Base, Strategy Library, Market Scanner, Signal Engine, Scoring
  Engine, Learning Engine.

## Failure policy (fail-safe = do no harm)
The safe behavior on any uncertainty is **do not create a duplicate or ambiguous order**: idempotent
`client_order_id`, reconcile-before-resend, and never leave an order in an unknown state silently. Broker
unavailable / timeout / network fault → hold or fail cleanly (never blind resend). Details in
`EXECUTION_FAILURE_POLICY.md`.

## Package contents
| file | purpose |
|---|---|
| `README.md` | this overview |
| `EXECUTION_ENGINE_ARCHITECTURE.md` | purpose, responsibilities, boundaries, inputs, outputs, components, validation, failure modes, data flow, startup/shutdown, performance model, versioning, interaction matrix |
| `ORDER_LIFECYCLE.md` | the 11 order states, transitions, and the supported order types / time-in-force |
| `ORDER_SCHEMA.json` | JSON Schema (Draft 2020-12) for the `OrderRequest` |
| `EXECUTION_API.md` | the public API (execute/build_order/validate_order/cancel/status/reconcile/health/statistics) — definition only |
| `EXECUTION_SEQUENCE.md` | single order, bracket, partial fill, cancel, reject, broker-unavailable, emergency-flatten, startup/shutdown |
| `EXECUTION_STATE_MACHINE.md` | the engine lifecycle + the per-order state machine |
| `EXECUTION_FAILURE_POLICY.md` | broker unavailable, timeout, network, rejection, partial fill, cancel, retry policy, fail-safe rules, idempotency |

## Status
DESIGN (Phase 5.6). Deliverables complete for review. **The Portfolio Manager and Learning Engine are NOT begun**
and must wait for explicit CEO approval.

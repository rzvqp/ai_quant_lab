# Phase 3 — Order Manager (Dry-Run) — Design

**CEO scope**: `ApprovedTradeIntent`, `OrderExecutionResult`, broker payload, volume/price
normalization, SL/TP validation, idempotency key, correlation ID, magic number, controlled comment,
state machine, timeout, controlled retry, reconciliation, audit journal, anti-duplicate protection.
**No order sent to MT5 this phase.**

## 1. Critical discovery before writing any code

`ai_trader/execution_engine/` is **not** a stub — it is a complete, already-tested, already-production-
wired Order/Execution Engine (198 tests; wired live into `ai_trader/simulation/harness.py`, driving the
backtest fill path today via `ExecutionSimulator`). It already provides, unmodified and reusable without
any fabrication:

- **Broker payload** — `execution_engine.types.OrderRequest` (+ `OrderConstraints`, `OrderRefs`,
  `BrokerCapabilitiesRef`, `BracketLegs`).
- **State machine** — `execution_engine.types.OrderState` (11 states), `TERMINAL_STATES`,
  `PRE_SUBMIT_STATES`.
- **SL/TP + mechanics validation** — `execution_engine.validator.validate_order(order, caps, portfolio)`
  (direction, tick-size, lot-size, quantity bounds, slippage, market status, bracket/price sanity). Only
  needs `OrderRequest` + `BrokerCapabilities` + `PortfolioState` — no `RiskDecision` dependency.
- **Idempotency + anti-duplicate + submit + track** —
  `execution_engine.pipeline.submit_built_order(order, portfolio, caps, ledger, adapter)`. This is the
  SAME public entry point `ExecutionEngine.emergency_flatten` already uses for orders built from a
  non-`RiskDecision` source (`OpenPosition`, via `builder.build_flatten_order`) — proof this pipeline
  stage was always meant to accept externally-built orders, not only `RiskDecision`-derived ones.
- **State ledger** — `execution_engine.ledger.OrderLedger`/`OrderRecord`, keyed by `client_order_id` (the
  idempotency key).
- **Reconciliation** — `execution_engine.reconciler.reconcile_one` / `reconcile_all_open` /
  `rebuild_from_broker` / `request_cancel`, pull-based against any `BrokerAdapter`.
- **Timeout / controlled retry** — `execution_engine.adapters.base.RealBrokerAdapterBase` +
  `RetryPolicy` (Phase 1, 18-test-proven): bounded retry with backoff, idempotent
  `_submit_with_idempotency`, explicit `ConnectionState`.
- **Reference pattern for a non-real adapter** — `execution_engine.adapters.null_adapter.NullBrokerAdapter`
  is *already* a zero-network, ACKNOWLEDGE-only (never fills) adapter subclassing
  `RealBrokerAdapterBase` — exactly the shape a dry-run adapter needs, just not owned by/wired for Order
  Manager's own audit semantics.

The one genuine gap `execution_engine` does **not** fill: (a) there is no bridge from the NEW live
`risk_manager_live.LiveRiskDecision`/`TradeProposal` (Phase 2) to `OrderRequest` — the existing
`builder.build_order()` requires the OLD, scoring-engine-coupled `risk_manager.types.RiskDecision`
(needs `score_id`, `engine_state`, `decision: Decision` enum, `applied_rules`, a real `Sizing` object —
reconstructing this honestly from `LiveRiskDecision`'s flattened fields would require far more
fabrication than Phase 2's narrow, disclosed sizing shim, so it is rejected here exactly as
`RiskManager.evaluate()` was rejected in Phase 2); (b) magic number / controlled comment / correlation ID
have no existing field anywhere; (c) no audit journal exists.

## 2. Architectural decision

**Do not build a new Order Manager engine that reimplements build/validate/submit/track/reconcile.**
Build a thin package, `ai_trader/order_manager/`, that:

1. Defines `ApprovedTradeIntent` — the missing bridge type, built by a caller (Phase 9's future
   Execution Orchestrator, or a test/manual caller this phase) from a `TradeProposal` + an approved
   `LiveRiskDecision` + an `InstrumentSpecification`. Carries the genuinely new fields CEO asked for that
   have no home elsewhere: `magic_number: int`, `comment: str`, plus `correlation_id`/`proposal_id`
   threaded through from `TradeProposal` (not on `OrderRequest`, which is frozen and unmodified — these
   stay on the intent and in the audit journal; Phase 10's real MT5 payload construction is the correct,
   later place to map `magic_number`/`comment` onto MT5's own `order_send()` request dict, which is a raw
   dict, not `OrderRequest`).
2. Builds a REAL `OrderRequest` (reused type, not a duplicate) directly from `ApprovedTradeIntent` via a
   new, narrow `order_manager.builder.build_order_request()` — mirroring the established
   `execution_engine.builder.build_flatten_order()` precedent (a separate, narrower builder for a
   non-`RiskDecision` source is already this codebase's own convention, not a new pattern). Performs
   **price normalization only** (round entry/stop/target to `instrument.tick_size`) — volume/lot
   normalization already happened in Phase 2 (`risk_manager_live.engine`'s `VOLUME_STEP_ROUNDING`), so
   `calculated_volume` arrives pre-rounded; re-rounding here would be redundant, not a gap.
3. Validates via the REUSED, unmodified `execution_engine.validator.validate_order`.
4. Submits via the REUSED, unmodified `execution_engine.pipeline.submit_built_order`, against a NEW
   `DryRunBrokerAdapter` (subclasses `RealBrokerAdapterBase`, mirrors `NullBrokerAdapter`'s pattern:
   always ACKNOWLEDGES, never FILLS, zero network, structurally cannot import or call anything under
   `execution_engine.adapters.mt5_*`). This gets idempotency, anti-duplicate guard, retry/timeout, and
   the 11-state machine for free, already proven correct by the reused module's own 198 tests.
5. Reconciles via the REUSED `execution_engine.reconciler.reconcile_one`/`reconcile_all_open` (against
   the same `DryRunBrokerAdapter` — a no-op in practice since it never changes state after ACKNOWLEDGED,
   but proves the plumbing is real and will work unchanged once Phase 10 swaps in a real MT5 adapter).
6. Journals every stage to a NEW, append-only audit journal (`order_manager.journal`), mirroring the
   established `context_memory.repository` convention (one `.jsonl` stream, envelope = deterministic
   content-hash id + sequence, fsync-on-append, idempotent-duplicate vs conflicting-duplicate
   distinction, integrity re-verification on read) — scoped to Order Manager's one record type
   (`OrderAuditEvent`) rather than that module's multi-type generality.
7. Returns `OrderExecutionResult` — a NEW, Order-Manager-owned wrapper (not a duplicate of
   `execution_engine.types.ExecutionResult`, which has no `dry_run` concept) carrying `order_request_id`,
   `client_order_id`, `state: OrderState` (reused enum), `filled_qty`, `avg_price`, `dry_run: bool`
   (always `True` this phase — asserted, not merely defaulted), `reasons`, `audit_event_ids` (linking
   back into the journal).

## 3. What is genuinely new vs. reused

| CEO requirement | Source |
|---|---|
| `ApprovedTradeIntent` | NEW |
| `OrderExecutionResult` | NEW |
| broker payload | REUSED (`OrderRequest`) |
| volume normalization | already done, Phase 2 |
| price normalization | NEW (tick-rounding in `builder.build_order_request`) |
| SL/TP validation | REUSED (`validator.validate_order`) |
| idempotency key | REUSED (`client_order_id`, `OrderLedger`) |
| correlation ID | NEW field, carried on the intent + journal (not on `OrderRequest`) |
| magic number / comment | NEW fields, same disclosure as above |
| state machine | REUSED (`OrderState`, `OrderLedger`) |
| timeout / controlled retry | REUSED (`RealBrokerAdapterBase`/`RetryPolicy`, Phase 1) |
| reconciliation | REUSED (`reconciler.py`) |
| audit journal | NEW (`order_manager.journal`, mirrors `context_memory` convention) |
| anti-duplicate protection | REUSED (`pipeline._validate_and_submit`'s ledger-keyed duplicate guard) |

## 4. Safety boundary (unchanged from the sweeping authorization)

`DryRunBrokerAdapter` never imports `MetaTrader5`, never imports
`execution_engine.adapters.mt5_gateway`/`mt5_adapter`/`mt5_types`, and never calls any real broker. It is
structurally incapable of reaching MT5 — not merely configured not to. A new static test enforces both
the `MetaTrader5`-literal absence (CEO rule 9, same convention as Phase 2) and the narrower
mt5-submodule-import absence (Order Manager may depend on `execution_engine.adapters.base`/`connection`
only, never the MT5-specific submodules).

## 5. Public entry point

```python
def process_approved_intent(
    intent: ApprovedTradeIntent, portfolio: PortfolioState, caps: BrokerCapabilities,
    ledger: OrderLedger, journal: OrderManagerAuditJournal, adapter: DryRunBrokerAdapter,
    config: OrderManagerConfig | None = None,
) -> OrderExecutionResult: ...
```

Fail-closed throughout: any build failure (e.g. non-finite normalized price) journals the failure and
returns a REJECTED `OrderExecutionResult`, never raises.

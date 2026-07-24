# Phase 9 — Execution Orchestrator — Design

**CEO scope**: coordinates Market Data → Context Engine → Recognition Engine → Confidence Engine →
Trade Proposal → Risk Manager → Portfolio Manager → Order Manager → Broker Adapter; must not contain
modules' own internal logic; implements global correlation ID, idempotency, freshness checks,
fail-closed, emergency stop, audit events, dry-run mode, demo mode, LIVE mode structurally disabled,
reconciliation.

## 1. What this phase is: pure sequencing + bridging, zero new domain logic

Every stage this phase touches was already built, tested, and CEO-approved in Phases 1–8:
`context_engine.build_context_snapshot`, `recognition_engine_live.recognize`,
`confidence_engine.assess_confidence`, `risk_manager_live.evaluate_trade_proposal`,
`portfolio_manager_live.evaluate_portfolio_authorization`, `order_manager.process_approved_intent`, and
`execution_engine.reconciler.reconcile_all_open`. Phase 9 calls each UNMODIFIED, in the CEO's own
specified order, and builds the bridge objects each stage's own input contract requires
(`TradeProposal`, `PortfolioAuthorizationRequest`, `ApprovedTradeIntent`) exactly the way every prior
phase's own design doc already established this bridging pattern (a caller builds the next stage's
input from the previous stage's output; no engine constructs its own successor's input). This phase adds
NO new risk/portfolio/order/recognition logic of its own -- only sequencing, correlation-id propagation,
freshness/fail-closed/emergency-stop plumbing, and audit notification.

## 2. Genuinely missing input: `CandidateSignal`

None of Phases 1–8 produce a candidate's own `entry`/`stop`/`target`/`direction` -- that is strategy
signal generation (`signal_engine`/`strategy_runtime`), explicitly out of every prior phase's scope and
out of this phase's scope too ("must not contain modules' own internal logic" -- signal generation is
ANOTHER module's internal logic). `CandidateSignal` is therefore the one new, minimal INPUT type this
phase defines: `strategy_id, symbol, direction, entry, stop, target, session, magic_number, comment,
as_of`. The orchestrator receives it from whatever already generates strategy signals -- it does not
compute it.

## 3. Global correlation ID (deterministic, no wall-clock, no randomness)

`correlation_id = f"ORCH-{strategy_id}-{symbol}-{as_of}"` -- derived deterministically from the
candidate's own natural key, matching this project's own standing "no wall-clock, no randomness in
business logic" discipline (the same discipline `order_manager.builder`/`risk_manager_live.engine`'s own
deterministic id derivation already follows). The SAME string is threaded through every downstream
bridge object (`TradeProposal.correlation_id`, `RecognitionCandidate.correlation_id`,
`PortfolioAuthorizationRequest.correlation_id`, `ApprovedTradeIntent.correlation_id`) -- one correlation
id ties every stage's own audit trail together.

## 4. Idempotency

The orchestrator itself invents no NEW idempotency mechanism -- it relies on the ALREADY-BUILT,
ledger-keyed duplicate guard inside `execution_engine.pipeline._validate_and_submit` (reused unmodified
via `order_manager.process_approved_intent`), which is safe to call twice for the same candidate only if
the SAME `OrderLedger`/`OrderManagerAuditJournal` instances are reused across calls -- both are therefore
caller-supplied, persistent dependencies (`OrchestratorDependencies`), never constructed fresh per call
(the same "no hidden state" discipline every prior phase followed).

## 5. Freshness check

`abs(candidate.as_of - market_context_as_of) <= config.max_staleness_seconds` (default 300s) -- a new,
disclosed check this phase owns (no prior phase checks candidate-vs-market-data staleness; Context
Engine's own `is_stale` flag is about the MARKET DATA's own internal staleness, a different question).

## 6. Fail-closed, emergency stop

Every stage call is wrapped; any exception aborts the run at that stage with a stage-tagged reason,
never propagates, never proceeds to the next stage. `emergency_stop: bool` (caller-supplied, e.g. from a
persistent kill-switch state the caller owns -- the orchestrator does not invent a kill-switch
persistence mechanism) is checked FIRST, before any stage runs, and short-circuits to a DENY.

## 7. Execution modes -- LIVE structurally disabled, DEMO functionally equal to DRY_RUN this phase

`ExecutionMode.DRY_RUN | DEMO | LIVE`. `LIVE` is refused unconditionally, at the very first check, before
touching any other stage -- CEO: "Nu activa tranzacționarea LIVE." `DEMO` additionally requires
`deps.account.is_demo is True` (defense in depth) before proceeding. **Disclosed limitation**:
`order_manager.process_approved_intent` (Phase 3) is structurally dry-run-only -- its own
`OrderExecutionResult.__post_init__` raises if `dry_run` is ever anything but `True`. This means `DEMO`
mode, today, is functionally IDENTICAL to `DRY_RUN` (both route through the same dry-run-only Order
Manager) -- the `ExecutionMode` distinction exists structurally so Phase 10 can plug in a real
demo-capable adapter/order path without changing this orchestrator's own shape, but Phase 9 itself does
not, and cannot yet, send a real order to MT5 even in DEMO mode. This is the correct, intentional
boundary this phase stops at.

## 8. Audit events

Reuses `telegram_notifier.notify_fire_and_forget` (Phase 5, unmodified, non-blocking, zero coupling
back onto the orchestrator) to emit one notification per terminal outcome (approved-and-executed, denied
at any stage, emergency-stop-refused) -- `telegram_credentials` is optional; when absent, no
notification is attempted (never a hard requirement to run the pipeline). A full `CalculationTraceStep`
trace (the same shape used by every prior phase) records every stage's own pass/fail regardless of
whether Telegram is configured -- the authoritative audit record is the returned trace, Telegram is a
best-effort side notification.

## 9. Reconciliation

`reconcile_orchestrated_orders(deps) -> tuple[Fill, ...]` -- a thin wrapper calling
`execution_engine.reconciler.reconcile_all_open(deps.ledger, deps.adapter)` UNMODIFIED. A separate public
function, not folded into `orchestrate()`, matching `ExecutionEngine.reconcile()`'s own separation of
"execute" from "reconcile" in the existing, approved Phase 1/3 architecture.

## 10. Public entry point

```python
def orchestrate(
    candidate: CandidateSignal, market_context: MarketContext, deps: OrchestratorDependencies,
    mode: ExecutionMode = ExecutionMode.DRY_RUN, emergency_stop: bool = False,
    config: OrchestratorConfig | None = None,
) -> OrchestrationResult: ...
```

`OrchestratorDependencies` bundles every caller-supplied dependency (`account`, `portfolio`,
`daily_state`, `instrument`, `risk_context`, `risk_config`, `broker_caps`, `ledger`, `order_journal`,
`adapter`, `repository`, `telegram_credentials`, `portfolio_config`, `confidence_config`,
`order_manager_config`) -- a single object rather than 15 positional parameters, since this phase's own
job is coordinating every prior phase at once. **`risk_context: RiskContext` has no live producer
anywhere in Phases 1–8** (no engine computes ATR/spread/liquidity `SymbolRiskSnapshot` data) -- a
disclosed, pre-existing gap (also true of every phase that touched `risk_manager_live` so far), not
something this phase fabricates; it remains caller-supplied.

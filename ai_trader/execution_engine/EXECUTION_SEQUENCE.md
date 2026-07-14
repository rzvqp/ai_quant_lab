# Execution Engine v1 — Operational Sequences (design)

How the Execution Engine behaves over time. Sequences only — no implementation, no broker integration. Actors:
`RM`=Risk Manager, `PM`=Portfolio Manager, `EE`=Execution Engine, `BA`=Broker Adapter (abstract, future).

---

## 1. Startup (mandatory reconciliation)
```
ORCH → EE.configure(ExecConfig, supported {risk_schema_major, order_schema_major}, BrokerCapabilities profile)
EE → RM.versions() ; EE → PM handshake ; EE → BA handshake (capabilities)
EE state: IDLE → RECONCILING
   EE → BA.query_open_orders() → rebuild Order Ledger (idempotent: match by client_order_id)
   resolve any pre-existing order to a definite lifecycle state
EE: RECONCILING → READY
```

## 2. Single order (happy path)
```
RM → EE.execute(RiskDecision ALLOW, PortfolioState):
   Intake (accept ALLOW) → Build OrderRequest (client_order_id=f(decision_id); order type/TIF; qty=sizing.size_units;
        prices=constraints; bracket legs from stop/target) → CREATED
   Validate (§8) → VALIDATED  (fail → REJECTED, nothing sent)
   Duplicate guard: client_order_id new → QUEUED → Submit(BA) → SUBMITTED
   BA ack → ACKNOWLEDGED → fill → FILLED
EE → PM.report_fill(...) ; EE → ExecutionResult(FILLED) ; Order Ledger updated
```

## 3. Bracket order (entry + protective legs)
```
decision has entry + stop + target → order_type=BRACKET (parent + stop_loss + take_profit children)
Submit parent; on fill, BA activates the protective children (OCO between stop and target)
a child fill (stop or target) cancels the other; EE reports the closing fill to PM
```

## 4. Partial fill
```
ACKNOWLEDGED → partial fill event → PARTIALLY_FILLED (report the partial fill to PM immediately)
   TIF IOC/FOK → cancel remainder → CANCELLED (or FILLED if fully filled first)
   TIF GTC/DAY → remainder keeps working → subsequent fills → FILLED (or EXPIRED at DAY end)
each confirmed fill reported to PM as it occurs (position truth stays current)
```

## 5. Cancel
```
ORCH/RM → EE.cancel(client_order_id):
   working order → BA.cancel → CANCELLED
   race: a fill arrives during cancel → Reconciler resolves → FILLED/PARTIALLY_FILLED (the fill wins) ; report to PM
```

## 6. Rejection
```
Submit → BA reject (e.g. margin/instrument/market-closed) → REJECTED(broker_reason)
   business rejection → NO auto-retry ; reported ; zero position change to PM
   (validation rejection happens PRE-submit: REJECTED, nothing ever sent)
```

## 7. Broker unavailable / timeout / network fault
```
Submit → BA unavailable → engine DEGRADED ; order stays QUEUED (bounded) → recover → submit ; else FAILED(BROKER_UNAVAILABLE)
Submit → ack timeout → Reconciler: BA.query_status(client_order_id)
   found working → ACKNOWLEDGED ; found filled → FILLED ; not found → safe resubmit SAME client_order_id (idempotent) or FAILED
network drop mid-flight → state UNKNOWN → reconcile on reconnect → resolve to true state (never blind resend)
```

## 8. Emergency flatten (Risk Manager command)
```
RM → EE.emergency_flatten(scope)
   EE state → EMERGENCY_FLATTEN ; refuse new opening orders
   for each in-scope open position: build reduce_only closing order → validate → submit → track to FILLED
   report closes to PM ; EE only executes the flatten (RM decided it)
```

## 9. Duplicate / restart safety
```
retry or restart re-derives client_order_id=f(decision_id):
   EE.execute(same decision) → duplicate guard / reconcile → returns existing OrderStatus ; NO second order
startup RECONCILING rebuilds the Ledger from BA.query_open_orders → no cross-restart duplicates
```

## 10. Shutdown
```
ORCH → EE.shutdown()
EE: stop accepting decisions → DRAINING
   reconcile every in-flight order to a definite state (never abandon unknown orders)
   emit final ExecutionReport / statistics()/health() ; persist Order Ledger → STOPPED
```

## 11. End-to-end (condensed)
```
configure → RECONCILE (rebuild Ledger) → READY →
[per approved decision] build (idempotent) → validate → submit(BA) → track (ack/partials/fills) → reconcile on
uncertainty → terminal state → report fills to PM + ExecutionResult → …
faults → DEGRADED (no blind sends) ; RM command → EMERGENCY_FLATTEN (closing only) → shutdown DRAINING → STOPPED.
```
Throughout, the Execution Engine: executes only approved RiskDecisions, builds/validates deterministically and
idempotently, reconciles rather than duplicates under uncertainty, reports fills to the Portfolio Manager, talks
only to the Broker Adapter for venue contact — and never signals, scores, manages risk, learns, or reads research.

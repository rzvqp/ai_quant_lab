# Execution Engine v1 — State Machine (design)

Two levels: (A) the **engine lifecycle** (the module's operational state) and (B) the **per-order state machine**
(the eleven order states from `ORDER_LIFECYCLE.md`). Design only — no code.

---

## A. Engine lifecycle

| state | meaning | accepts decisions? |
|---|---|---|
| `IDLE` | constructed, not configured | no |
| `RECONCILING` | at startup: querying the Broker Adapter for pre-existing orders, rebuilding the Order Ledger | no |
| `READY` | operating; accepts approved decisions and manages orders | yes |
| `DEGRADED` | Broker Adapter / Portfolio Manager impaired; queues or fails safely, no blind sends | limited (queue/fail-safe) |
| `EMERGENCY_FLATTEN` | executing the Risk Manager's flatten command; only reduce-only/closing orders | closing only |
| `DRAINING` | shutdown: reconciling in-flight orders to terminal/definite states | no new |
| `STOPPED` | terminal; Order Ledger persisted for next-run reconciliation | no |

```
IDLE → RECONCILING → READY ⇄ DEGRADED
                       │  ▲        │
   Risk Manager        │  │ recover│
   flatten command     ▼  │        │
               EMERGENCY_FLATTEN ───┘
                       │
        shutdown (any) ▼
                   DRAINING → STOPPED
```
- **Startup reconciliation is mandatory** (`IDLE→RECONCILING→READY`): the engine never starts blind and risk
  duplicating a pre-existing order.
- `READY↔DEGRADED` on Broker/Portfolio availability; `DEGRADED` never blind-sends (queues or fails safely).
- `EMERGENCY_FLATTEN` (from the Risk Manager) restricts activity to reduce-only closing orders.
- `DRAINING` reconciles every in-flight order to a definite state before `STOPPED` — no order abandoned.

## B. Per-order state machine (the 11 states)
```
CREATED → VALIDATED → QUEUED → SUBMITTED → ACKNOWLEDGED → [PARTIALLY_FILLED …] → FILLED
   │fail       │fail                 │timeout                                        (terminal)
   ▼           ▼                      ▼ reconcile
REJECTED    REJECTED           (resolve to a definite state — never duplicate)
(pre-submit)(dup/consistency)
   in-flight ── cancel request/ TIF ──▶ CANCELLED (terminal)   [cancel↔fill race → reconcile]
   in-flight ── TIF/valid_until expiry ─▶ EXPIRED  (terminal)
   in-flight ── broker reject ─────────▶ REJECTED (terminal)
   in-flight ── unrecoverable fault ───▶ FAILED   (terminal, after fail-safe handling)
```
Terminal: `FILLED`, `CANCELLED`, `REJECTED`, `EXPIRED`, `FAILED`. Every order reaches exactly one; the Reconciler
resolves any ambiguous/timeout state to a definite one. Transitions are driven by validated events + reconciliation
— never by blind resend (idempotent `client_order_id`).

### Per-order transition table (key rows)
| from | to | trigger | guard |
|---|---|---|---|
| CREATED | VALIDATED | validation passes | all §8 checks pass |
| CREATED/VALIDATED | REJECTED | validation/duplicate/consistency fail | pre-submit; nothing sent |
| VALIDATED | QUEUED | admitted to router | rate-limit / adapter availability |
| QUEUED | SUBMITTED | sent to Broker Adapter | not a duplicate `client_order_id` |
| SUBMITTED | ACKNOWLEDGED | broker ack | — |
| SUBMITTED | (reconcile) | ack timeout | query status before any resend |
| ACKNOWLEDGED | PARTIALLY_FILLED | partial fill event | — |
| ACKNOWLEDGED/PARTIALLY_FILLED | FILLED | full fill | — |
| any in-flight | CANCELLED | cancel request / TIF cancel | confirm; resolve fill race |
| any in-flight | EXPIRED | TIF / valid_until | — |
| any in-flight | REJECTED | broker reject | broker reason recorded |
| any in-flight | FAILED | unrecoverable fault | after fail-safe (reconcile, bounded retry) |

## C. Determinism & fail-safe invariants
1. Order **construction + validation** are deterministic (`(RiskDecision, PortfolioState, BrokerCapabilities,
   ExecConfig)`); order **outcomes** depend on the venue and are always reconciled to a definite lifecycle state.
2. Idempotent `client_order_id` guarantees retries/restarts never create a duplicate order.
3. The safe behavior under uncertainty is **reconcile-then-resolve**, never blind resend; unrecoverable →
   `FAILED`, reported, never silently abandoned.
4. Engine-level faults degrade to `DEGRADED` (no blind sends) or, on command, `EMERGENCY_FLATTEN` (closing only);
   shutdown always `DRAINING`-reconciles before `STOPPED`.

# Execution Engine v1 — Order Lifecycle & Order Types (design)

The lifecycle of a single order, and the order types / time-in-force the Execution Engine supports (documented;
no broker integration). Design only — no code.

---

## 1. The eleven order states

| state | kind | meaning |
|---|---|---|
| `CREATED` | pre-submit | `OrderRequest` built from a `RiskDecision`, `client_order_id` assigned; not yet validated |
| `VALIDATED` | pre-submit | passed all execution-mechanics validation (§EXECUTION_ENGINE_ARCHITECTURE §8) |
| `QUEUED` | pre-submit | admitted to the router queue (rate-limit / adapter-availability wait) |
| `SUBMITTED` | in-flight | sent to the Broker Adapter; awaiting acknowledgement |
| `ACKNOWLEDGED` | in-flight | broker acknowledged receipt (working order) |
| `PARTIALLY_FILLED` | in-flight | some quantity filled; remainder still working |
| `FILLED` | terminal | fully filled |
| `CANCELLED` | terminal | cancelled (by request or TIF), no remaining quantity |
| `REJECTED` | terminal | rejected pre-submit (validation) or by the broker |
| `EXPIRED` | terminal | expired per TIF / `valid_until` without full fill |
| `FAILED` | terminal | could not be executed due to a fault (broker unavailable, unrecoverable error) after fail-safe handling |

Terminal states: `FILLED`, `CANCELLED`, `REJECTED`, `EXPIRED`, `FAILED`. Every order reaches exactly one terminal
state; none is abandoned in an unknown state (the Reconciler resolves ambiguity).

## 2. Lifecycle transitions

```
CREATED ──validate──▶ VALIDATED ──enqueue──▶ QUEUED ──submit──▶ SUBMITTED ──ack──▶ ACKNOWLEDGED
   │  fail                 │ fail(dup/consistency)                   │ timeout          │
   ▼                       ▼                                         ▼ (reconcile)      ├── partial fill ─▶ PARTIALLY_FILLED
REJECTED (pre-submit)   REJECTED                              (resolve to a definite    │                        │
                                                               state, never duplicate)   │ full fill              │ remaining fills
                                                                                          ▼                        ▼
                                                                                        FILLED ◀──────────────── FILLED
   cancel request (any in-flight) ─────────────────────────────────────────────▶ CANCELLED (or race → FILLED)
   TIF/expiry (IOC/FOK/DAY/valid_until) ───────────────────────────────────────▶ EXPIRED / CANCELLED
   broker reject (any in-flight) ──────────────────────────────────────────────▶ REJECTED
   unrecoverable fault after fail-safe ────────────────────────────────────────▶ FAILED
```

- `CREATED→VALIDATED→QUEUED→SUBMITTED→ACKNOWLEDGED` is the normal pre-fill path.
- `ACKNOWLEDGED`/`PARTIALLY_FILLED` are working states; fills accumulate until `FILLED` or a terminal cancel/
  expire/reject.
- Any in-flight state can go to `CANCELLED` (request/TIF), `REJECTED` (broker), `EXPIRED` (TIF/valid_until), or
  `FAILED` (fault). A cancel racing a fill resolves via the Reconciler to the true terminal state.
- Pre-submit failures (validation, duplicate, consistency) → `REJECTED` **before** anything is sent to the venue.

## 3. Idempotency across the lifecycle
Every order carries a stable `client_order_id = f(decision_id)`. A retry or a restart-recovery re-derives the same
id, so the Reconciler can map it to the existing order and **never create a duplicate**. State transitions are
driven by broker events + reconciliation, not by blind resend.

## 4. Supported order types (documented; abstract Broker Adapter)
| order type | meaning |
|---|---|
| **Market** | execute immediately at the best available price (requires `max_slippage`) |
| **Limit** | execute only at `limit_price` or better |
| **Stop** | becomes a market order when `stop_price` is reached |
| **Stop-Limit** | becomes a limit order (`limit_price`) when `stop_price` is reached |
| **OCO** (one-cancels-other) | two linked orders; a fill on one cancels the other (e.g. take-profit + stop) |
| **Bracket** | an entry order with attached protective stop-loss and take-profit legs (parent + two children) |

## 5. Time-in-force (documented)
| TIF | meaning |
|---|---|
| **IOC** (immediate-or-cancel) | fill what is immediately available; cancel the remainder |
| **FOK** (fill-or-kill) | fill the full quantity immediately or cancel entirely |
| **GTC** (good-till-cancelled) | remain working until filled or explicitly cancelled |
| **DAY** | remain working until the end of the trading day, then expire |

Order type and TIF are **orthogonal** fields on the `OrderRequest` (`order_type` × `time_in_force`); OCO/Bracket
are contingent structures that carry child legs. The supported combinations are constrained by
`BrokerCapabilities` — an unsupported combination is `REJECTED` at validation. v1 documents these; it integrates no
venue.

## 6. Mapping RiskDecision → order type (default policy)
- A `RiskDecision` with an entry price ≈ current market → **Market** (with `max_slippage` from constraints) or a
  marketable **Limit**, per config.
- A decision with an explicit entry level not yet reached → **Stop** / **Stop-Limit**.
- Protective `stop`/`target` from the decision → attached as a **Bracket** (or an **OCO** pair) so the position is
  protected on fill.
- `reduce_only` decisions (partial exits / emergency flatten) → reduce-only orders that can only decrease exposure.
The mapping is deterministic given the decision + config; it is recorded on the `OrderRequest` for audit.

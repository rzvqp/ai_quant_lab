# Execution Engine v1 — Failure Policy (design)

How the Execution Engine behaves under faults. The governing principle is **do no harm**: under any uncertainty,
never create a duplicate or ambiguous order — reconcile first, resolve to a definite state, and prefer inaction to
a wrong action. Design only — no code.

---

## 1. Core fail-safe principles
1. **Idempotency:** every order carries a stable `client_order_id = f(decision_id)`. Any retry or restart re-derives
   the same id, so a resend maps to the existing order and cannot double-execute.
2. **Reconcile-before-resend:** on any ambiguity (timeout, lost connection, unknown ack), the Reconciler QUERIES
   the broker for the order's true state BEFORE taking any further action. No blind resend, ever.
3. **Prefer inaction:** if the true state cannot be established, the order is held/marked and escalated, not
   re-sent. An unknown order is never abandoned silently.
4. **Definite terminal state:** every order ends in exactly one terminal state (`FILLED/CANCELLED/REJECTED/
   EXPIRED/FAILED`); ambiguity is resolved by reconciliation, not assumption.
5. **Bounded everything:** retries, queue waits, and timeouts are all bounded; exhaustion → a definite `FAILED`
   with a reason, reported to the Portfolio Manager and health.

## 2. Failure catalog

| failure | detection | handling |
|---|---|---|
| **Broker unavailable** (adapter down / not connected) | submit attempt fails / adapter health | engine → `DEGRADED`; order stays `QUEUED` (bounded wait) or → `FAILED(BROKER_UNAVAILABLE)` if the wait elapses; **never** blind-send; existing orders keep being tracked/reconciled |
| **Timeout** (no ack within budget) | submit/ack timer | Reconciler queries status: if working → `ACKNOWLEDGED`; if filled → `FILLED`; if not found → safe to resubmit the SAME `client_order_id` (idempotent) or `FAILED(SUBMIT_TIMEOUT)` per policy |
| **Network failure** mid-flight | connection error | order state UNKNOWN → reconcile on reconnect → resolve to the true state; no action until resolved |
| **Broker rejection** | reject event | `REJECTED(broker_reason)`; NO automatic retry unless the reason is policy-eligible (see §3) and attempts remain |
| **Partial fill** | fill events < quantity | `PARTIALLY_FILLED`; remainder handled per TIF: IOC/FOK → cancel remainder; GTC/DAY → keep working; report each fill to the Portfolio Manager as it occurs |
| **Cancel (requested)** | cancel API | attempt cancel; confirm `CANCELLED`; if a fill raced the cancel → reconcile to `FILLED`/`PARTIALLY_FILLED` (the fill wins) |
| **Cancel (TIF/expiry)** | TIF / `valid_until` | `EXPIRED`/`CANCELLED` per TIF |
| **Duplicate submission** | `client_order_id` already known | do NOT create a new order; return the existing `OrderStatus` (idempotent no-op) |
| **Validation failure** (pre-submit) | Order Validator | `REJECTED` before anything is sent; reason recorded; nothing reaches the venue |
| **Internal error** (build/track) | exception/guard | fail-safe `REJECTED`/`FAILED`; the batch of other orders continues; escalate health |
| **PortfolioState unavailable** | Portfolio Manager read fails | consistency checks cannot run → hold the order (`QUEUED`) / `FAILED(PORTFOLIO_UNAVAILABLE)`; engine → `DEGRADED` |
| **Emergency flatten** (Risk Manager command) | control signal | engine → `EMERGENCY_FLATTEN`; only reduce-only closing orders issued; new opening orders refused |

## 3. Retry policy (bounded, reconcile-first)
- **Eligible for retry:** transient faults only — submit timeout with "order not found", transient network errors,
  transient adapter unavailability. Retries reuse the SAME `client_order_id` (idempotent) after a reconcile
  confirms no working/filled order exists.
- **NOT eligible:** business rejections (insufficient margin, invalid instrument, market closed), validation
  failures, or any state where the order may already be working/filled — those are terminal or reconcile-only.
- **Bounds:** max N retries (config) with backoff; on exhaustion → `FAILED` with the last reason. No unbounded
  retry loops.
- **Reconcile gate:** every retry is preceded by a status query; if the order is found working/filled, the retry
  is cancelled (no duplicate).

## 4. Fill reporting under failure
- Fills are reported to the Portfolio Manager **as they are confirmed**, even for `PARTIALLY_FILLED` orders, so the
  portfolio's position/exposure truth stays current. A `FAILED`/`REJECTED` order with zero confirmed fills reports
  no position change. The Execution Engine owns ORDER state; the Portfolio Manager owns POSITION state — reconciled
  via reported fills, never by assumption.

## 5. Startup & shutdown safety
- **Startup:** mandatory reconciliation (`RECONCILING`) — query the Broker Adapter for any live orders from a prior
  run and rebuild the Order Ledger before accepting new decisions. Prevents duplicates across restarts.
- **Shutdown:** `DRAINING` — reconcile every in-flight order to a definite state and persist the Ledger; never exit
  leaving an order in an unknown state.

## 6. Escalation & health
- Repeated/severe faults (broker down beyond threshold, portfolio unavailable, reconciliation impossible) set
  engine health `DEGRADED`/`FAILED` and are surfaced via `health()`; the Risk Manager may respond with
  `EMERGENCY_FLATTEN`. The Execution Engine itself never *decides* to stop trading (that is the Risk Manager) — it
  fails safely and reports.

## 7. Determinism note
Order construction, validation, idempotency, and the retry/reconcile decision logic are deterministic given the
inputs and config. Only the venue's responses (fills/rejects/latency) are non-deterministic — and every such
response is mapped, via reconciliation, to a definite lifecycle state with a recorded reason.

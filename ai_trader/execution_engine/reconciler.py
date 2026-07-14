"""The Reconciler (``EXECUTION_ENGINE_ARCHITECTURE.md`` §5/§9; ``EXECUTION_FAILURE_POLICY.md`` §1.2):
on ANY ambiguity (timeout, restart, explicit request), QUERY the Broker Adapter for the order's true
state BEFORE any further action -- never a blind resend. Pull-based throughout, matching
``EXECUTION_SEQUENCE.md``'s own ``BA.query_status``/``BA.query_open_orders`` calls.

**Exception safety** (the same "verify EVERY entry point" lesson applied to ``pipeline.py``,
``NEXT_SESSION.md`` §6/§9): every function here is the Broker Adapter boundary for
``ExecutionEngine.cancel``/``reconcile``/``shutdown`` -- an untrusted external call the Broker Adapter
contract itself does not promise is exception-free (``broker_adapter.py``: "expected to be ... non-
raising for ordinary conditions", which leaves room for a genuinely unexpected fault). Every adapter
call below is therefore wrapped: a query/cancel exception degrades to "treat as unresolved, change
nothing" (matching the documented "prefer inaction" principle) rather than propagating past this
module's own public functions -- so a single flaky broker call during ``reconcile_all_open`` can never
abort reconciling the REST of the open orders, and ``ExecutionEngine.shutdown()`` can never get stuck
mid-``DRAINING`` because one broker call raised.
"""

from __future__ import annotations

from ai_trader.execution_engine.broker_adapter import BrokerAdapter
from ai_trader.execution_engine.ledger import OrderLedger, OrderRecord
from ai_trader.execution_engine.lifecycle import apply_broker_update
from ai_trader.execution_engine.types import BrokerOrderState, Fill


def _safe_query_status(adapter: BrokerAdapter, client_order_id: str) -> BrokerOrderState | None:
    try:
        return adapter.query_status(client_order_id)
    except Exception:  # noqa: BLE001 -- the broker call is the untrusted boundary; treat a raised
        # exception exactly like "not found" (None) -- "prefer inaction", never propagate.
        return None


def _safe_query_open_orders(adapter: BrokerAdapter) -> tuple[BrokerOrderState, ...]:
    try:
        return adapter.query_open_orders()
    except Exception:  # noqa: BLE001 -- see _safe_query_status; an unreachable broker at startup
        # degrades to "no pre-existing orders known" rather than crashing configure().
        return ()


def _safe_cancel(adapter: BrokerAdapter, client_order_id: str) -> None:
    try:
        adapter.cancel_order(client_order_id)
    except Exception:  # noqa: BLE001 -- the cancel ack is advisory only (cancel() always reconciles
        # afterward regardless of what this returns); a raised exception is treated exactly like a
        # rejected/ignored cancel ack -- the subsequent reconcile still resolves the true state.
        return


def request_cancel(ledger: OrderLedger, adapter: BrokerAdapter, client_order_id: str) -> tuple[OrderRecord | None, Fill | None]:
    """Attempt to cancel a working order, then ALWAYS reconcile to the true state
    (``EXECUTION_SEQUENCE.md`` §5: "attempt cancel; confirm CANCELLED (or note race with a fill)").
    Never raises. The single entry point ``ExecutionEngine.cancel()`` uses -- it does not call
    ``adapter.cancel_order`` directly, so this exception-safety is not duplicated at the engine layer.
    """
    record = ledger.get(client_order_id)
    if record is None or record.is_terminal:
        return record, None
    _safe_cancel(adapter, client_order_id)
    return reconcile_one(ledger, adapter, client_order_id)


def reconcile_one(ledger: OrderLedger, adapter: BrokerAdapter, client_order_id: str) -> tuple[OrderRecord | None, Fill | None]:
    """Resolve ONE order's true state. A terminal record is returned unchanged (already resolved,
    idempotent). An order the broker no longer recognizes (``query_status`` returns ``None``, INCLUDING
    when the query itself raised) is left exactly as-is -- "prefer inaction"
    (``EXECUTION_FAILURE_POLICY.md`` §1.3); the caller decides whether that means "safe to resubmit" or
    "mark FAILED", never this function silently."""
    record = ledger.get(client_order_id)
    if record is None or record.is_terminal:
        return record, None
    broker_state = _safe_query_status(adapter, client_order_id)
    if broker_state is None:
        return record, None
    updated, fill = apply_broker_update(record, broker_state)
    ledger.put(updated)
    return updated, fill


def reconcile_all_open(ledger: OrderLedger, adapter: BrokerAdapter) -> tuple[Fill, ...]:
    """Reconcile every currently-open order in the Ledger. Iterates a snapshot of ``open_orders()`` so
    a record moving to terminal mid-pass never mutates the set being iterated. A single order's broker
    call failing (see ``_safe_query_status``) never prevents reconciling the rest."""
    fills: list[Fill] = []
    for record in ledger.open_orders():
        _, fill = reconcile_one(ledger, adapter, record.client_order_id)
        if fill is not None:
            fills.append(fill)
    return tuple(fills)


def rebuild_from_broker(ledger: OrderLedger, adapter: BrokerAdapter) -> tuple[str, ...]:
    """Startup reconciliation (``EXECUTION_SEQUENCE.md`` §1: "query_open_orders -> rebuild Order
    Ledger (idempotent recovery)"). v1 has no cross-process Ledger persistence (disclosed limitation,
    see the validation report) -- a broker-reported order whose ``client_order_id`` this Ledger has no
    record of cannot be rebuilt (there is no original ``OrderRequest`` to reconstruct it from) and is
    NOT silently dropped: its id is returned so the caller can surface it as a degraded-health reason,
    never pretend the engine started with full knowledge when it didn't.

    Returns the tuple of orphaned ``client_order_id``s the broker reported that this Ledger could not
    reconcile. Never raises -- a broker unreachable at startup degrades to "no pre-existing orders
    found" rather than aborting ``configure()``.
    """
    orphaned: list[str] = []
    for broker_state in _safe_query_open_orders(adapter):
        record = ledger.get(broker_state.client_order_id)
        if record is None:
            orphaned.append(broker_state.client_order_id)
            continue
        reconcile_one(ledger, adapter, broker_state.client_order_id)
    return tuple(orphaned)

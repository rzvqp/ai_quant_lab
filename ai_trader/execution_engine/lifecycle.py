"""The Lifecycle Tracker (``EXECUTION_ENGINE_ARCHITECTURE.md`` §5): maps Broker Adapter events
(``BrokerOrderState``, pulled via ``query_status``/``query_open_orders``) onto an ``OrderRecord``'s
lifecycle state -- accumulating partial fills, detecting terminal states. Never invents a transition
the broker didn't report; never resurrects a terminal order (``ORDER_LIFECYCLE.md`` §1: "every order
reaches exactly one terminal state").
"""

from __future__ import annotations

import logging

from ai_trader.execution_engine.ledger import OrderRecord
from ai_trader.execution_engine.types import TERMINAL_STATES, BrokerOrderState, Fill, OrderState

logger = logging.getLogger(__name__)

#: In-flight states a broker-reported update may legitimately move an order out of
#: (``EXECUTION_STATE_MACHINE.md`` §B: "any in-flight -> CANCELLED/EXPIRED/REJECTED/FAILED").
_IN_FLIGHT_STATES = frozenset({
    OrderState.QUEUED, OrderState.SUBMITTED, OrderState.ACKNOWLEDGED, OrderState.PARTIALLY_FILLED,
})


def apply_broker_update(record: OrderRecord, broker_state: BrokerOrderState) -> tuple[OrderRecord, Fill | None]:
    """Apply one broker-reported ``BrokerOrderState`` onto ``record``, returning the (possibly
    unchanged) record and a :class:`Fill` event if this update represents NEW filled quantity since
    the last known state (reported to the Portfolio Manager as it occurs,
    ``EXECUTION_FAILURE_POLICY.md`` §4).

    Idempotent and fail-safe: a terminal record is NEVER moved by a further broker update (a race is
    resolved once, by whichever update reaches the terminal state first; subsequent updates for the
    same terminal order are no-ops) -- this is what makes repeated ``reconcile()`` calls safe to call
    any number of times.
    """
    if record.is_terminal:
        return record, None
    if record.client_order_id != broker_state.client_order_id:
        return record, None  # defensive: never apply a mismatched update

    if not is_valid_broker_transition(record.state, broker_state.state):
        logger.warning(
            "unexpected broker-reported transition for %s: %s -> %s (applying it anyway -- the "
            "broker is always the source of truth for its own order; this is advisory only)",
            record.client_order_id, record.state.value, broker_state.state.value,
        )

    new_qty = max(record.filled_qty, broker_state.filled_qty)
    fill: Fill | None = None
    if new_qty > record.filled_qty:
        delta = new_qty - record.filled_qty
        # IMPLEMENTATION CHOICE: a broker reporting new filled quantity WITHOUT an avg_price is a
        # malformed/incomplete report -- fabricating 0.0 (a "free trade") would be worse than a
        # best-effort reference price. Fall back to the order's own limit_price (the price the order
        # was built to trade at) when available; 0.0 only as the very last resort, never silently
        # presented as a real fill price without this fallback chain.
        fill_price = broker_state.avg_price
        if fill_price is None:
            fill_price = record.order.limit_price if record.order.limit_price is not None else 0.0
        fill = Fill(
            client_order_id=record.client_order_id, symbol=record.order.symbol,
            direction=record.order.direction, qty=delta,
            price=fill_price,
            as_of=record.order.as_of,
        )

    reasons = record.reasons if broker_state.reason is None else (broker_state.reason,)
    updated = OrderRecord(
        order=record.order,
        state=broker_state.state,
        filled_qty=new_qty,
        avg_price=broker_state.avg_price if broker_state.avg_price is not None else record.avg_price,
        reasons=reasons,
        broker_order_id=record.broker_order_id,
    )
    return updated, fill


def is_valid_broker_transition(current: OrderState, reported: OrderState) -> bool:
    """Whether ``reported`` is a state the broker may legitimately move an order FROM ``current`` TO
    (``EXECUTION_STATE_MACHINE.md`` §B's per-order transition table). Advisory ONLY -- used by
    :func:`apply_broker_update` to log an unexpected report, never to reject or drop it: the broker is
    always the source of truth for its own order, so an "invalid" transition is still applied, just
    logged for operator visibility (a real venue's behavior is not this module's to second-guess)."""
    if current in TERMINAL_STATES:
        return False
    if reported in TERMINAL_STATES:
        return True
    if current is OrderState.SUBMITTED:
        return reported in (OrderState.ACKNOWLEDGED, OrderState.PARTIALLY_FILLED)
    if current in (OrderState.ACKNOWLEDGED, OrderState.PARTIALLY_FILLED):
        return reported in (OrderState.ACKNOWLEDGED, OrderState.PARTIALLY_FILLED)
    return reported in _IN_FLIGHT_STATES

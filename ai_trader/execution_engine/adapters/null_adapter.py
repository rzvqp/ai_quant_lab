"""`NullBrokerAdapter` -- the reference implementation for `RealBrokerAdapterBase` (`BROKER_ADAPTER_
DESIGN.md` Sec4, CEO-accepted). Safe, in-memory, zero-network: exercises `RealBrokerAdapterBase`'s own
new connectivity/idempotency/retry machinery under deterministic, injectable failure modes, WITHOUT
connecting to anything real. Implements `BrokerAdapter` (unmodified, pre-existing Protocol) AND
`BrokerConnectionLifecycle` (new, additive) both -- proof both protocols compose on one real object,
exactly as `MT5ReadOnlyBrokerAdapter` will (minus `submit_order`/`cancel_order`, which that one never
implements at all).

Deliberately NOT a second `ExecutionSimulator` -- it never fills an order (`submit_order` only ever
reaches `ACKNOWLEDGED`); it exists solely to validate the NEW foundation machinery this module owns.
"""

from __future__ import annotations

from ai_trader.execution_engine.adapters.base import RealBrokerAdapterBase, TransientOperationError
from ai_trader.execution_engine.adapters.connection import ConnectionResult
from ai_trader.execution_engine.types import (
    BrokerAck,
    BrokerCapabilities,
    BrokerOrderState,
    OrderRequest,
    OrderState,
    OrderType,
    TERMINAL_STATES,
    TimeInForce,
)


class NullBrokerAdapter(RealBrokerAdapterBase):
    """`simulated_connect_failures`: how many `TransientOperationError`s `_do_connect` raises before
    succeeding -- lets tests exercise `RetryPolicy` deterministically without a real clock/network.
    `always_disconnected`: if `True`, `_do_connect` always returns a non-retryable
    `ConnectionResult(accepted=False, ...)` (a permanent, non-transient failure -- distinct from the
    retryable case above)."""

    def __init__(
        self, *, simulated_connect_failures: int = 0, always_disconnected: bool = False, **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self._simulated_connect_failures_remaining = simulated_connect_failures
        self._always_disconnected = always_disconnected
        self._orders: dict[str, BrokerOrderState] = {}

    # ------------------------------------------------------------------ RealBrokerAdapterBase hooks

    def _do_connect(self) -> ConnectionResult:
        if self._always_disconnected:
            return ConnectionResult(accepted=False, reason="SIMULATED_PERMANENT_FAILURE")
        if self._simulated_connect_failures_remaining > 0:
            self._simulated_connect_failures_remaining -= 1
            raise TransientOperationError("simulated transient connect failure")
        return ConnectionResult(accepted=True)

    def _do_disconnect(self) -> None:
        self._orders.clear()

    def _do_heartbeat_check(self) -> bool:
        return True

    # ------------------------------------------------------------------ BrokerAdapter (unmodified Protocol)

    def capabilities(self) -> BrokerCapabilities:
        return BrokerCapabilities(
            supported_order_types=frozenset({OrderType.MARKET, OrderType.LIMIT}),
            supported_time_in_force=frozenset({TimeInForce.GTC, TimeInForce.IOC}),
            tick_size=0.01, lot_step=0.01, min_qty=0.01, max_qty=100.0,
        )

    def submit_order(self, order: OrderRequest) -> BrokerAck:
        if not self.is_connected():
            return BrokerAck(accepted=False, reason="NOT_CONNECTED")

        def _do_submit() -> BrokerAck:
            self._orders[order.client_order_id] = BrokerOrderState(
                client_order_id=order.client_order_id, state=OrderState.ACKNOWLEDGED,
            )
            return BrokerAck(accepted=True, broker_order_id=f"NULL-{order.client_order_id}")

        return self._submit_with_idempotency(order, _do_submit)

    def cancel_order(self, client_order_id: str) -> BrokerAck:
        if not self.is_connected():
            return BrokerAck(accepted=False, reason="NOT_CONNECTED")
        existing = self._orders.get(client_order_id)
        if existing is None:
            return BrokerAck(accepted=False, reason="UNKNOWN_ORDER")
        self._orders[client_order_id] = BrokerOrderState(
            client_order_id=client_order_id, state=OrderState.CANCELLED,
        )
        return BrokerAck(accepted=True)

    def query_status(self, client_order_id: str) -> BrokerOrderState | None:
        return self._orders.get(client_order_id)

    def query_open_orders(self) -> tuple[BrokerOrderState, ...]:
        return tuple(s for s in self._orders.values() if s.state not in TERMINAL_STATES)

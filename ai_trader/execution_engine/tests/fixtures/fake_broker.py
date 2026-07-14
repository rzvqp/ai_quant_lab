"""A deterministic, fully in-memory ``BrokerAdapter`` test double. NOT production code -- the real
Broker Adapter contract is abstract-only in v1 (``README.md``); this fixture exists purely so the
Execution Engine's own test suite can exercise every lifecycle/failure path without a live venue.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from ai_trader.execution_engine.types import (
    TERMINAL_STATES,
    BrokerAck,
    BrokerCapabilities,
    BrokerOrderState,
    MarketStatus,
    OrderRequest,
    OrderState,
    OrderType,
    TimeInForce,
)


def make_capabilities(
    symbol: str = "XAUUSD", tick_size: float = 0.01, lot_step: float = 0.01,
    min_qty: float = 0.01, max_qty: float = 1_000_000.0, market_status: MarketStatus = MarketStatus.OPEN,
) -> BrokerCapabilities:
    return BrokerCapabilities(
        supported_order_types=frozenset({
            OrderType.MARKET, OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT,
            OrderType.OCO, OrderType.BRACKET,
        }),
        supported_time_in_force=frozenset({
            TimeInForce.IOC, TimeInForce.FOK, TimeInForce.GTC, TimeInForce.DAY,
        }),
        tick_size=tick_size, lot_step=lot_step, min_qty=min_qty, max_qty=max_qty,
        market_status={symbol: market_status},
    )


@dataclass
class FakeBrokerAdapter:
    """Configurable in-memory broker double.

    - ``accept_submits=False`` simulates every submission being broker-rejected.
    - ``fill_on_submit`` (default ``True``) simulates an immediate synchronous fill/ack at submit time
      (matching a simple, always-available venue) -- set ``False`` to leave orders at ``ACKNOWLEDGED``
      until a test explicitly drives them forward via :meth:`push_fill`/:meth:`push_state`.
    - ``fill_fraction`` controls FILLED (1.0, default) vs. PARTIALLY_FILLED (<1.0) on submit.
    - ``accept_cancels=False`` simulates a broker that refuses cancel requests.
    - :meth:`drop` simulates the broker losing all knowledge of an order (a "not found" / timeout
      scenario the Reconciler must handle without blind-resending).
    """

    caps: BrokerCapabilities
    accept_submits: bool = True
    submit_reject_reason: str = "BROKER_REJECTED"
    fill_on_submit: bool = True
    fill_fraction: float = 1.0
    accept_cancels: bool = True
    _orders: dict[str, BrokerOrderState] = field(default_factory=dict)
    _preexisting: tuple[BrokerOrderState, ...] = field(default_factory=tuple)
    submit_calls: list[str] = field(default_factory=list)
    query_status_calls: list[str] = field(default_factory=list)

    def capabilities(self) -> BrokerCapabilities:
        return self.caps

    def submit_order(self, order: OrderRequest) -> BrokerAck:
        self.submit_calls.append(order.client_order_id)
        if not self.accept_submits:
            return BrokerAck(accepted=False, reason=self.submit_reject_reason)
        if self.fill_on_submit:
            filled_qty = order.quantity * self.fill_fraction
            state = OrderState.FILLED if self.fill_fraction >= 1.0 else OrderState.PARTIALLY_FILLED
            avg_price = order.limit_price if order.limit_price is not None else 100.0
        else:
            filled_qty, avg_price, state = 0.0, None, OrderState.ACKNOWLEDGED
        self._orders[order.client_order_id] = BrokerOrderState(
            client_order_id=order.client_order_id, state=state, filled_qty=filled_qty, avg_price=avg_price,
        )
        return BrokerAck(accepted=True, broker_order_id=f"B-{order.client_order_id}")

    def cancel_order(self, client_order_id: str) -> BrokerAck:
        if not self.accept_cancels:
            return BrokerAck(accepted=False, reason="CANCEL_REJECTED")
        existing = self._orders.get(client_order_id)
        if existing is not None and existing.state not in TERMINAL_STATES:
            self._orders[client_order_id] = replace(existing, state=OrderState.CANCELLED)
        return BrokerAck(accepted=True)

    def query_status(self, client_order_id: str) -> BrokerOrderState | None:
        self.query_status_calls.append(client_order_id)
        if client_order_id in self._orders:
            return self._orders[client_order_id]
        return next((s for s in self._preexisting if s.client_order_id == client_order_id), None)

    def query_open_orders(self) -> tuple[BrokerOrderState, ...]:
        live = tuple(s for s in self._orders.values() if s.state not in TERMINAL_STATES)
        return live + self._preexisting

    # -------------------------------------------------------------- test-only control surface

    def push_state(self, client_order_id: str, state: OrderState, filled_qty: float = 0.0, avg_price: float | None = None, reason: str | None = None) -> None:
        """Directly set the broker's reported state for ``client_order_id`` -- simulates an
        asynchronous broker-side event (a later fill, a broker-initiated reject, an expiry) a test
        drives explicitly before calling ``reconcile()``."""
        self._orders[client_order_id] = BrokerOrderState(
            client_order_id=client_order_id, state=state, filled_qty=filled_qty, avg_price=avg_price, reason=reason,
        )

    def push_fill(self, client_order_id: str, filled_qty: float, avg_price: float, full: bool) -> None:
        state = OrderState.FILLED if full else OrderState.PARTIALLY_FILLED
        self.push_state(client_order_id, state, filled_qty=filled_qty, avg_price=avg_price)

    def drop(self, client_order_id: str) -> None:
        """Simulate the broker losing all knowledge of the order (a "not found" / lost-in-flight
        scenario)."""
        self._orders.pop(client_order_id, None)

    def seed_preexisting_order(self, state: BrokerOrderState) -> None:
        """Register an order the broker already knows about BEFORE ``configure()`` runs -- for startup
        reconciliation tests (``EXECUTION_SEQUENCE.md`` §1)."""
        self._preexisting = self._preexisting + (state,)

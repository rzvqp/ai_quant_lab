"""The Order Ledger (``EXECUTION_ENGINE_ARCHITECTURE.md`` §5): the Execution Engine's own record of
live/terminal orders -- source of truth for ORDER state (the Portfolio Manager, not this module, owns
POSITION truth, via reported fills). In-memory for v1; bounded by construction (v1 has no unbounded
history growth path -- every order is created once via :meth:`OrderLedger.put`).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_trader.execution_engine.types import TERMINAL_STATES, OrderRequest, OrderState


@dataclass(slots=True)
class OrderRecord:
    """Mutable -- the Ledger's own working record of one order's current lifecycle state. Never
    exposed directly outside this package; callers see the immutable ``OrderStatus``/``ExecutionResult``
    views built from it (``reporter.py``)."""

    order: OrderRequest
    state: OrderState
    filled_qty: float = 0.0
    avg_price: float | None = None
    reasons: tuple[str, ...] = ()
    broker_order_id: str | None = None

    @property
    def client_order_id(self) -> str:
        return self.order.client_order_id

    @property
    def remaining_qty(self) -> float:
        return max(0.0, self.order.quantity - self.filled_qty)

    @property
    def is_terminal(self) -> bool:
        return self.state in TERMINAL_STATES


@dataclass(slots=True)
class OrderLedger:
    """Keyed by ``client_order_id`` -- the idempotency key. Insertion order is preserved (a Python
    ``dict``'s own guarantee), and since callers always process decisions in a fixed order (Risk
    Manager's own rank order), iteration over the Ledger is itself deterministic."""

    _records: dict[str, OrderRecord] = field(default_factory=dict)

    def put(self, record: OrderRecord) -> None:
        self._records[record.client_order_id] = record

    def get(self, client_order_id: str) -> OrderRecord | None:
        return self._records.get(client_order_id)

    def all(self) -> tuple[OrderRecord, ...]:
        return tuple(self._records.values())

    def open_orders(self) -> tuple[OrderRecord, ...]:
        return tuple(r for r in self._records.values() if not r.is_terminal)

    def __contains__(self, client_order_id: str) -> bool:
        return client_order_id in self._records

    def __len__(self) -> int:
        return len(self._records)

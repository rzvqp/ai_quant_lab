"""The abstract Broker Adapter contract (``README.md``: "the only venue contact ... abstract in v1 --
a declared capability set, not a live integration"; ``EXECUTION_ENGINE_ARCHITECTURE.md`` §3/§13).

IMPLEMENTATION CHOICE: the architecture docs describe this contract in prose (submit, cancel, query
status, query open orders, declare capabilities) without publishing a schema or interface definition
for it. :class:`BrokerAdapter` is this module's own ``Protocol`` capturing exactly that prose, pull-
based (the Reconciler always QUERIES; nothing here pushes events into the engine), matching
``EXECUTION_SEQUENCE.md``'s own ``BA.query_open_orders()``/``BA.query_status(...)`` calls. No real
implementation exists in this module -- a future real adapter (or, sooner, the Execution Simulator)
implements this ``Protocol`` unmodified. A fake, deterministic test double lives in
``tests/fixtures/fake_broker.py`` (test-only; never imported by production code).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ai_trader.execution_engine.types import BrokerAck, BrokerCapabilities, BrokerOrderState, OrderRequest


@runtime_checkable
class BrokerAdapter(Protocol):
    """The venue boundary contract. Every method is expected to be synchronous and non-raising for
    ordinary (non-catastrophic) conditions -- failures are reported via the return value
    (``BrokerAck.accepted=False``, or a ``None``/empty query result), never via an exception, so the
    Execution Engine's own fail-safe handling (``EXECUTION_FAILURE_POLICY.md``) can always classify
    the outcome deterministically."""

    def capabilities(self) -> BrokerCapabilities:
        """The declared capability profile (order types/TIF supported, tick/lot/qty limits, market
        status per symbol)."""
        ...

    def submit_order(self, order: OrderRequest) -> BrokerAck:
        """Submit ``order``. Returns the immediate ack/reject -- never blocks for a fill."""
        ...

    def cancel_order(self, client_order_id: str) -> BrokerAck:
        """Request cancellation of a working order."""
        ...

    def query_status(self, client_order_id: str) -> BrokerOrderState | None:
        """The broker's current view of one order, or ``None`` if unknown to the broker."""
        ...

    def query_open_orders(self) -> tuple[BrokerOrderState, ...]:
        """Every order the broker currently considers live -- used for startup reconciliation
        (``EXECUTION_SEQUENCE.md`` §1: "rebuild Order Ledger (idempotent recovery)")."""
        ...

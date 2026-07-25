"""`MT5HistoryGateway` -- extends the frozen `MT5Gateway` (`execution_engine/adapters/mt5_gateway.py`,
Phase 1) with exactly ONE additional read-only operation, `history_deals_get`, mirroring Phase 10's own
`mt5_demo_execution/gateway.py::RealMT5DemoGateway` precedent EXACTLY: a SUBCLASS adding new methods,
calling the ALREADY-SET terminal-library reference the parent's own `__init__` establishes -- this file
never opens its own connection into the underlying trading library, is not a second entry point, only a
second method on the same, already-approved gateway object. Zero modification to the parent module.

The new read is a deal-history query, distinct from the parent's own currently-open-positions read --
this package never places, modifies, checks, or cancels an order or position of any kind, and never
receives an execution-capable adapter (CEO instruction, 2026-07-25: this package must not create another
path to the trading terminal, and must never be handed anything capable of submitting an order)."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway, RealMT5Gateway


@runtime_checkable
class MT5HistoryGateway(MT5Gateway, Protocol):
    """`MT5Gateway` plus deal history -- the one read this package needs that Phase 1's own frozen
    Protocol never declared (it had no caller that needed realized P&L)."""

    def history_deals_get(self, date_from: int, date_to: int) -> tuple[Any, ...] | None: ...


class RealMT5HistoryGateway(RealMT5Gateway):
    """Adds deal-history reading on top of the already-approved gateway, unmodified. Opens no
    connection of its own -- uses the parent's own already-set library reference."""

    def history_deals_get(self, date_from: int, date_to: int) -> tuple[Any, ...] | None:
        return self._mt5.history_deals_get(date_from, date_to)  # type: ignore[no-any-return]

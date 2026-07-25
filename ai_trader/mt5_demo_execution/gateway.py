"""`RealMT5DemoGateway` -- a SUBCLASS of the already-approved, frozen `RealMT5Gateway` (Phase 1), adding
exactly the two methods MT5 order sending needs. This file never imports the MT5 terminal API package
of its own accord -- it calls `self._mt5` (the module reference the PARENT's own, unmodified `__init__`
already sets), never opening a second entry point into the library. Zero modification to
`ai_trader/execution_engine/adapters/mt5_gateway.py`."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway, RealMT5Gateway


@runtime_checkable
class MT5DemoGateway(MT5Gateway, Protocol):
    """Additive Protocol -- extends the read-only `MT5Gateway` Protocol (Phase 1, subclassed not
    modified) with exactly two methods. Never folded into `MT5Gateway` itself (that Protocol stays
    frozen, read-only)."""

    def order_check(self, request: dict[str, object]) -> Any: ...

    def order_send(self, request: dict[str, object]) -> Any: ...


class RealMT5DemoGateway(RealMT5Gateway):
    def order_check(self, request: dict[str, object]) -> Any:
        return self._mt5.order_check(request)

    def order_send(self, request: dict[str, object]) -> Any:
        return self._mt5.order_send(request)

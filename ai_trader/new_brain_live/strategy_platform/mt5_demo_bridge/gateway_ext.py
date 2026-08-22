"""Additive `MT5DemoGateway` extension -- exactly the two more MT5 primitives S5's own risk sizing
(`order_calc_profit`, section 8) and restart reconciliation (`history_deals_get`, section 25) need,
neither of which the existing `mt5_demo_execution`/`execution_engine` packages ever wrapped (confirmed by
direct inspection before writing this file). Same additive-Protocol-subclass pattern
`mt5_demo_execution/gateway.py` itself already established: `RealMT5BridgeGateway` calls `self._mt5` (the
module reference `RealMT5Gateway.__init__` already sets, two subclass-levels up), never opening a second
`import MetaTrader5` entry point -- `ai_trader/execution_engine/adapters/mt5_gateway.py` remains the sole
choke point in the whole repository."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ai_trader.mt5_demo_execution.gateway import MT5DemoGateway, RealMT5DemoGateway


@runtime_checkable
class MT5BridgeGateway(MT5DemoGateway, Protocol):
    def order_calc_profit(
        self, action: int, symbol: str, volume: float, price_open: float, price_close: float,
    ) -> float | None: ...

    def history_deals_get(self, date_from: int, date_to: int) -> tuple[Any, ...] | None: ...


class RealMT5BridgeGateway(RealMT5DemoGateway):
    def order_calc_profit(
        self, action: int, symbol: str, volume: float, price_open: float, price_close: float,
    ) -> float | None:
        return self._mt5.order_calc_profit(action, symbol, volume, price_open, price_close)  # type: ignore[no-any-return]

    def history_deals_get(self, date_from: int, date_to: int) -> tuple[Any, ...] | None:
        return self._mt5.history_deals_get(date_from, date_to)  # type: ignore[no-any-return]

"""`LiveMT5TickReader` -- the real `LiveTickReader` implementation `PdhPdlRecognitionRule` uses to read
`effective_spread` LIVE, immediately before order submission (CEO: "singura parte care trebuie live").
Read-only (`symbol_info_tick`, already on the frozen `MT5Gateway` Protocol) -- never caches."""

from __future__ import annotations

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway
from ai_trader.pdh_pdl_demo.types import LiveTick


class LiveMT5TickReader:
    def __init__(self, gateway: MT5Gateway) -> None:
        self._gateway = gateway

    def read(self, symbol: str) -> LiveTick | None:
        tick = self._gateway.symbol_info_tick(symbol)
        if tick is None:
            return None
        bid = getattr(tick, "bid", None)
        ask = getattr(tick, "ask", None)
        tick_time = getattr(tick, "time", None)
        if bid is None or ask is None or tick_time is None:
            return None
        try:
            return LiveTick(bid=float(bid), ask=float(ask), as_of=int(tick_time))
        except (TypeError, ValueError):
            return None

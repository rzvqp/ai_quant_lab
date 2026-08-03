"""`LiveMT5FillReader` -- the real `RealizedFillReader` implementation `PdhPdlOrchestrator` uses to
detect a broker-side close and read its realized price. Read-only: `positions_get` (already on the
frozen `MT5Gateway` Protocol) and `history_deals_get` (the EXISTING, already-approved
`mt5_pnl_source.gateway.MT5HistoryGateway` Protocol / `RealMT5HistoryGateway` -- reused verbatim, not
redefined here; this package's own static import-boundary test forbids it from ever defining an
order-submission-capable gateway of its own, so history reading is composed from `mt5_pnl_source`'s own
already-approved class instead). Never submits, modifies, or cancels anything."""

from __future__ import annotations

import time
from typing import Callable

from ai_trader.mt5_pnl_source.gateway import MT5HistoryGateway

_DEAL_ENTRY_OUT = 1  # MetaTrader5's own DEAL_ENTRY_OUT constant -- a position-closing deal
_LOOKBACK_PADDING_SECONDS = 3600  # search window starts an hour before since_ts, covers clock skew


def _default_clock() -> int:
    return int(time.time())


class LiveMT5FillReader:
    def __init__(self, gateway: MT5HistoryGateway, clock: Callable[[], int] = _default_clock) -> None:
        self._gateway = gateway
        self._clock = clock

    def is_position_open(self, magic_number: int, symbol: str) -> bool | None:
        positions = self._gateway.positions_get(symbol)
        if positions is None:
            return None
        return any(int(getattr(p, "magic", -1)) == magic_number for p in positions)

    def read_close_price(self, magic_number: int, symbol: str, since_ts: int) -> float | None:
        now = self._clock()
        deals = self._gateway.history_deals_get(since_ts - _LOOKBACK_PADDING_SECONDS, now)
        if deals is None:
            return None
        closing_deals = [
            d for d in deals
            if int(getattr(d, "magic", -1)) == magic_number
            and str(getattr(d, "symbol", "")) == symbol
            and int(getattr(d, "entry", -1)) == _DEAL_ENTRY_OUT
        ]
        if not closing_deals:
            return None
        latest = max(closing_deals, key=lambda d: int(getattr(d, "time", 0)))
        price = getattr(latest, "price", None)
        return None if price is None else float(price)

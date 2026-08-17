"""Shared fakes for `new_brain_live` tests -- with fakes only, never a real terminal, mirroring
`pdh_pdl_demo/tests/test_live_deps.py`'s own `_FakeHistoryGateway` shape exactly (one gateway satisfying
`MT5AccountBridge`, `MT5PortfolioStateSource`, `LiveBarFeed`, and `LiveMT5TickReader` simultaneously,
matching production wiring where all four share one real MT5 connection)."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

SYMBOL = "XAUUSD"
TICK_VALUE = 1.0
TICK_SIZE = 0.01
CONTRACT_SIZE = 100.0


class FakeNewBrainLiveGateway:
    def __init__(self, *, rates: tuple[Any, ...] = (), tick: Any | None = None) -> None:
        self.account = SimpleNamespace(
            trade_mode=0, currency="USD", balance=10_000.0, equity=10_000.0, margin=0.0,
            margin_free=10_000.0, margin_level=None, leverage=100,
        )
        self.symbol = SimpleNamespace(
            trade_tick_size=TICK_SIZE, volume_step=0.01, volume_min=0.01, volume_max=100.0,
            trade_contract_size=CONTRACT_SIZE, trade_tick_value=TICK_VALUE, currency_margin="USD",
        )
        self._rates = rates
        self._tick = tick
        self.order_send_calls = 0

    def initialize(
        self, path: str | None = None, login: int | None = None, password: str | None = None,
        server: str | None = None,
    ) -> bool:
        return True

    def shutdown(self) -> None:
        pass

    def terminal_info(self) -> Any:
        return None

    def account_info(self) -> Any:
        return self.account

    def symbols_get(self) -> Any:
        return ()

    def symbol_info(self, symbol: str) -> Any:
        return self.symbol

    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        return True

    def symbol_info_tick(self, symbol: str) -> Any:
        return self._tick

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any:
        return self._rates

    def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any:
        return None

    def copy_ticks_from(self, symbol: str, date_from: int, count: int, flags: int) -> Any:
        return None

    def copy_ticks_range(self, symbol: str, date_from: int, date_to: int, flags: int) -> Any:
        return None

    def orders_get(self, symbol: str | None = None) -> Any:
        return ()

    def last_error(self) -> tuple[int, str]:
        return (0, "Success")

    def positions_get(self, symbol: str | None = None) -> tuple[Any, ...] | None:
        return ()

    def history_deals_get(self, date_from: int, date_to: int) -> tuple[Any, ...] | None:
        return ()

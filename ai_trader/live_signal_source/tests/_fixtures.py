"""Shared fake gateway for `live_signal_source` tests -- implements the FULL `MT5Gateway` Protocol
surface (matching the established precedent, `mt5_pnl_source`/`mt5_account_bridge`'s own fixtures)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_UNSET: Any = object()


@dataclass
class RawRate:
    """One raw MT5 `copy_rates_from` record -- field names match the real MetaTrader5 rate tuple
    exactly (`time`, `open`, `high`, `low`, `close`, `tick_volume`)."""

    time: int
    open: float
    high: float
    low: float
    close: float
    tick_volume: float = 100.0


class FakeMT5Gateway:
    def __init__(self, rates: Any = _UNSET) -> None:
        self.rates: Any = [] if rates is _UNSET else rates
        self.copy_rates_from_calls: list[tuple[str, int, int, int]] = []

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any | None:
        self.copy_rates_from_calls.append((symbol, timeframe, date_from, count))
        if self.rates is None:
            return None
        return tuple(self.rates)

    # -- the rest of `MT5Gateway`, unused here, stubbed to satisfy the Protocol structurally --

    def initialize(
        self, path: str | None = None, login: int | None = None, password: str | None = None,
        server: str | None = None,
    ) -> bool:
        return True

    def shutdown(self) -> None:
        return None

    def terminal_info(self) -> Any | None:
        return None

    def account_info(self) -> Any | None:
        return None

    def symbols_get(self) -> tuple[Any, ...] | None:
        return None

    def symbol_info(self, symbol: str) -> Any | None:
        return None

    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        return True

    def symbol_info_tick(self, symbol: str) -> Any | None:
        return None

    def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any | None:
        return None

    def copy_ticks_from(self, symbol: str, date_from: int, count: int, flags: int) -> Any | None:
        return None

    def copy_ticks_range(self, symbol: str, date_from: int, date_to: int, flags: int) -> Any | None:
        return None

    def positions_get(self, symbol: str | None = None) -> tuple[Any, ...] | None:
        return None

    def orders_get(self, symbol: str | None = None) -> tuple[Any, ...] | None:
        return None

    def last_error(self) -> tuple[int, str]:
        return (0, "no error")

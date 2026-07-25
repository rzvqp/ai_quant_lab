"""Shared fake gateway for `mt5_account_bridge` tests -- implements the FULL `MT5Gateway` Protocol
surface (matching the established precedent, `mt5_pnl_source/tests/_fixtures.py` and
`execution_engine/adapters/tests/_fixtures.py::FakeMT5Gateway`)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_UNSET: Any = object()


@dataclass
class _RawAccount:
    trade_mode: int = 0
    currency: str = "USD"
    balance: float = 10_000.0
    equity: float = 10_000.0
    margin: float = 0.0
    margin_free: float = 10_000.0
    margin_level: float = 0.0
    leverage: float = 500.0


@dataclass
class _RawSymbolInfo:
    trade_tick_size: float = 0.01
    volume_step: float = 0.01
    volume_min: float = 0.01
    volume_max: float = 100.0
    trade_contract_size: float = 100.0
    trade_tick_value: float = 1.0
    currency_margin: str = "USD"


class FakeMT5AccountGateway:
    def __init__(
        self, account: Any = _UNSET,
        symbols: dict[str, _RawSymbolInfo | None] | None = None,
    ) -> None:
        self.account: Any = _RawAccount() if account is _UNSET else account
        self.symbols: dict[str, _RawSymbolInfo | None] = symbols if symbols is not None else {}
        self.symbol_select_calls: list[str] = []
        self.account_info_calls = 0
        self.symbol_info_calls: list[str] = []

    # -- the fields this package actually reads --

    def account_info(self) -> Any | None:
        self.account_info_calls += 1
        return self.account

    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        self.symbol_select_calls.append(symbol)
        return True

    def symbol_info(self, symbol: str) -> Any | None:
        self.symbol_info_calls.append(symbol)
        return self.symbols.get(symbol)

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

    def symbols_get(self) -> tuple[Any, ...] | None:
        return None

    def symbol_info_tick(self, symbol: str) -> Any | None:
        return None

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any | None:
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

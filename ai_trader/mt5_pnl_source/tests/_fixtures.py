"""Shared fake gateway for `mt5_pnl_source` tests -- implements the FULL `MT5HistoryGateway` Protocol
surface (matching the established precedent, `execution_engine/adapters/tests/_fixtures.py::
FakeMT5Gateway`), even the methods this package never calls, so it satisfies the Protocol structurally
for mypy, not just at runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class _RawPosition:
    profit: float


@dataclass
class _RawDeal:
    profit: float
    time: int


@dataclass
class _RawAccount:
    equity: float


class FakeMT5HistoryGateway:
    def __init__(
        self, account: _RawAccount | None, positions: tuple[_RawPosition, ...] | None,
        deals: tuple[_RawDeal, ...] | None,
    ) -> None:
        self.account = account
        self.positions = positions
        self.deals = deals
        self.history_calls: list[tuple[int, int]] = []

    def set_equity(self, equity: float) -> None:
        assert self.account is not None
        self.account = _RawAccount(equity=equity)

    # -- the fields this package actually reads --

    def account_info(self) -> Any | None:
        return self.account

    def positions_get(self, symbol: str | None = None) -> tuple[Any, ...] | None:
        return self.positions

    def history_deals_get(self, date_from: int, date_to: int) -> tuple[Any, ...] | None:
        self.history_calls.append((date_from, date_to))
        return self.deals

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

    def symbol_info(self, symbol: str) -> Any | None:
        return None

    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        return True

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

    def orders_get(self, symbol: str | None = None) -> tuple[Any, ...] | None:
        return None

    def last_error(self) -> tuple[int, str]:
        return (0, "no error")


def make_gateway(
    equity: float = 10_000.0, position_profits: tuple[float, ...] = (),
    deals: tuple[tuple[float, int], ...] = (),
) -> FakeMT5HistoryGateway:
    return FakeMT5HistoryGateway(
        account=_RawAccount(equity=equity),
        positions=tuple(_RawPosition(profit=p) for p in position_profits),
        deals=tuple(_RawDeal(profit=p, time=t) for p, t in deals),
    )

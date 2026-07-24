"""Test-only double for `MT5Gateway` -- lets the entire adapter test suite run with NO dependency on a
real MT5 terminal or even the `MetaTrader5` package being importable (CEO's own explicit requirement).
Mutable public attributes, set directly by each test, matching this project's own established
test-double style (`ai_trader/execution_engine/tests/fixtures/fake_broker.py`).
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any


class FakeMT5Gateway:
    """Configurable in every dimension a test needs. Defaults describe a healthy, connected DEMO
    account with AlgoTrading enabled -- mirroring the real, verified probe result
    (`MT5_CONNECTIVITY_PROBE_REPORT.md`)."""

    def __init__(self) -> None:
        self.initialize_result: bool = True
        self.initialize_failures_before_success: int = 0
        self.terminal_info_result: SimpleNamespace | None = SimpleNamespace(
            connected=True, trade_allowed=True, build=5836,
        )
        self.account_info_result: SimpleNamespace | None = SimpleNamespace(
            trade_mode=0, trade_allowed=True, server="FusionMarkets-Demo",
        )
        self.symbols: tuple[str, ...] = ("XAUUSD", "EURUSD")
        self.symbol_info_by_name: dict[str, SimpleNamespace] = {
            "XAUUSD": SimpleNamespace(
                trade_tick_size=0.01, volume_step=0.01, volume_min=0.01, volume_max=100.0,
                digits=2, spread=7, trade_mode=4, description="Gold vs US Dollar",
            ),
        }
        self.tick_by_symbol: dict[str, SimpleNamespace] = {
            "XAUUSD": SimpleNamespace(time=1_784_908_535, bid=4054.55, ask=4054.62, last=0.0),
        }
        self.last_error_result: tuple[int, str] = (0, "no error")

        self.initialize_calls = 0
        self.shutdown_calls = 0
        self.symbol_select_calls: list[str] = []

    def initialize(
        self, path: str | None = None, login: int | None = None, password: str | None = None,
        server: str | None = None,
    ) -> bool:
        self.initialize_calls += 1
        if self.initialize_failures_before_success > 0:
            self.initialize_failures_before_success -= 1
            return False
        return self.initialize_result

    def shutdown(self) -> None:
        self.shutdown_calls += 1

    def terminal_info(self) -> Any | None:
        return self.terminal_info_result

    def account_info(self) -> Any | None:
        return self.account_info_result

    def symbols_get(self) -> tuple[Any, ...] | None:
        return tuple(SimpleNamespace(name=name) for name in self.symbols)

    def symbol_info(self, symbol: str) -> Any | None:
        return self.symbol_info_by_name.get(symbol)

    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        self.symbol_select_calls.append(symbol)
        return True

    def symbol_info_tick(self, symbol: str) -> Any | None:
        return self.tick_by_symbol.get(symbol)

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any | None:
        return None  # not exercised this phase -- disclosed as unused, not a hidden capability

    def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any | None:
        return None

    def copy_ticks_from(self, symbol: str, date_from: int, count: int, flags: int) -> Any | None:
        return None

    def copy_ticks_range(self, symbol: str, date_from: int, date_to: int, flags: int) -> Any | None:
        return None

    def positions_get(self, symbol: str | None = None) -> tuple[Any, ...] | None:
        return ()

    def orders_get(self, symbol: str | None = None) -> tuple[Any, ...] | None:
        return ()

    def last_error(self) -> tuple[int, str]:
        return self.last_error_result

"""`LiveMT5TickReader` tests -- with a fake `MT5Gateway`, never a real terminal."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from ai_trader.pdh_pdl_demo.live_tick_reader import LiveMT5TickReader
from ai_trader.pdh_pdl_demo.types import LiveTick


class _FakeGateway:
    """Stubs the FULL `MT5Gateway` Protocol surface, even the methods this reader never calls -- same
    established convention as `mt5_pnl_source/tests/_fixtures.py::FakeMT5HistoryGateway`, so this
    satisfies the Protocol structurally for mypy, not just at runtime."""

    def __init__(self, tick: object | None) -> None:
        self._tick = tick

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
        return None

    def symbols_get(self) -> Any:
        return ()

    def symbol_info(self, symbol: str) -> Any:
        return None

    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        return True

    def symbol_info_tick(self, symbol: str) -> Any:
        return self._tick

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any:
        return None

    def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any:
        return None

    def copy_ticks_from(self, symbol: str, date_from: int, count: int, flags: int) -> Any:
        return None

    def copy_ticks_range(self, symbol: str, date_from: int, date_to: int, flags: int) -> Any:
        return None

    def positions_get(self, symbol: str | None = None) -> Any:
        return ()

    def orders_get(self, symbol: str | None = None) -> Any:
        return ()

    def last_error(self) -> tuple[int, str]:
        return (0, "Success")


def test_reads_bid_ask_time_into_a_live_tick() -> None:
    reader = LiveMT5TickReader(_FakeGateway(SimpleNamespace(bid=4054.55, ask=4054.62, time=1_700_000_000)))
    tick = reader.read("XAUUSD")
    assert tick == LiveTick(bid=4054.55, ask=4054.62, as_of=1_700_000_000)


def test_none_tick_from_gateway_returns_none() -> None:
    reader = LiveMT5TickReader(_FakeGateway(None))
    assert reader.read("XAUUSD") is None


def test_missing_bid_field_returns_none_rather_than_raising() -> None:
    reader = LiveMT5TickReader(_FakeGateway(SimpleNamespace(ask=4054.62, time=1_700_000_000)))
    assert reader.read("XAUUSD") is None


def test_missing_ask_field_returns_none_rather_than_raising() -> None:
    reader = LiveMT5TickReader(_FakeGateway(SimpleNamespace(bid=4054.55, time=1_700_000_000)))
    assert reader.read("XAUUSD") is None


def test_missing_time_field_returns_none_rather_than_raising() -> None:
    reader = LiveMT5TickReader(_FakeGateway(SimpleNamespace(bid=4054.55, ask=4054.62)))
    assert reader.read("XAUUSD") is None


def test_non_numeric_field_returns_none_rather_than_raising() -> None:
    reader = LiveMT5TickReader(_FakeGateway(SimpleNamespace(bid="bad", ask=4054.62, time=1_700_000_000)))
    assert reader.read("XAUUSD") is None

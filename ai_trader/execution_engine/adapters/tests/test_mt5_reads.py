"""Controls 8-11 (CEO's own mandatory test list): reading/normalizing account_info, reading/normalizing
terminal_info, reading capabilities for XAUUSD, reading a tick with no side effects."""

from __future__ import annotations

from ai_trader.execution_engine.adapters.mt5_adapter import MT5ReadOnlyBrokerAdapter
from ai_trader.execution_engine.adapters.mt5_types import AccountTradeMode
from ai_trader.execution_engine.adapters.tests._fixtures import FakeMT5Gateway


def test_account_info_normalized_into_status() -> None:
    gateway = FakeMT5Gateway()
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    adapter.connect()
    status = adapter.status()
    assert status.account_trade_mode is AccountTradeMode.DEMO
    assert status.account_is_demo is True
    assert status.account_trade_allowed is True
    assert status.server == "FusionMarkets-Demo"


def test_terminal_info_normalized_into_status() -> None:
    gateway = FakeMT5Gateway()
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    adapter.connect()
    status = adapter.status()
    assert status.terminal_connected is True
    assert status.terminal_build == 5836
    assert status.connected is True


def test_status_before_connect_degrades_safely_never_raises() -> None:
    gateway = FakeMT5Gateway()
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    status = adapter.status()  # never connected yet -- still safe, still reads live gateway data
    assert status.connected is False
    assert status.terminal_connected is True  # the gateway itself can still be queried read-only


def test_xauusd_capabilities_read_correctly() -> None:
    gateway = FakeMT5Gateway()
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    adapter.connect()
    caps = adapter.symbol_capabilities("XAUUSD")
    assert caps is not None
    assert caps.symbol == "XAUUSD"
    assert caps.tick_size == 0.01
    assert caps.lot_step == 0.01
    assert caps.min_qty == 0.01
    assert caps.max_qty == 100.0
    assert caps.digits == 2


def test_unknown_symbol_capabilities_returns_none_not_error() -> None:
    gateway = FakeMT5Gateway()
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    adapter.connect()
    assert adapter.symbol_capabilities("NOT_A_REAL_SYMBOL") is None


def test_capabilities_unavailable_while_disconnected() -> None:
    gateway = FakeMT5Gateway()
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    assert adapter.symbol_capabilities("XAUUSD") is None  # never connected


def test_tick_read_returns_expected_data() -> None:
    gateway = FakeMT5Gateway()
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    adapter.connect()
    tick = adapter.read_tick("XAUUSD")
    assert tick is not None
    assert tick.bid == 4054.55
    assert tick.ask == 4054.62


def test_tick_read_has_no_side_effects() -> None:
    """Reading a tick twice must be idempotent and must never mutate connection state, gateway call
    counters (beyond the tick call itself), or any other adapter state."""
    gateway = FakeMT5Gateway()
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    adapter.connect()
    initialize_calls_before = gateway.initialize_calls
    shutdown_calls_before = gateway.shutdown_calls

    tick_a = adapter.read_tick("XAUUSD")
    tick_b = adapter.read_tick("XAUUSD")

    assert tick_a == tick_b
    assert gateway.initialize_calls == initialize_calls_before  # no reconnection attempted
    assert gateway.shutdown_calls == shutdown_calls_before  # no disconnection attempted
    assert adapter.is_connected()  # state unchanged


def test_list_symbols_includes_xauusd() -> None:
    gateway = FakeMT5Gateway()
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    adapter.connect()
    symbols = adapter.list_symbols()
    assert symbols is not None
    assert "XAUUSD" in symbols

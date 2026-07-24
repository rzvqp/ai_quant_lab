"""Controls 2-4 (CEO's own mandatory test list): correct lifecycle, repeatable connect/disconnect,
refusal while disconnected."""

from __future__ import annotations

from ai_trader.execution_engine.adapters.connection import ConnectionState
from ai_trader.execution_engine.adapters.mt5_adapter import MT5ReadOnlyBrokerAdapter
from ai_trader.execution_engine.adapters.null_adapter import NullBrokerAdapter
from ai_trader.execution_engine.adapters.tests._fixtures import FakeMT5Gateway
from ai_trader.execution_engine.types import BrokerAck


def test_initial_state_is_disconnected() -> None:
    adapter = NullBrokerAdapter()
    assert not adapter.is_connected()
    assert adapter.connection_state() is ConnectionState.DISCONNECTED
    assert adapter.last_heartbeat_as_of() is None


def test_connect_transitions_to_connected() -> None:
    adapter = NullBrokerAdapter()
    result = adapter.connect()
    assert result.accepted
    assert adapter.is_connected()
    assert adapter.connection_state() is ConnectionState.CONNECTED
    assert adapter.last_heartbeat_as_of() is not None


def test_disconnect_transitions_to_disconnected() -> None:
    adapter = NullBrokerAdapter()
    adapter.connect()
    adapter.disconnect()
    assert not adapter.is_connected()
    assert adapter.connection_state() is ConnectionState.DISCONNECTED


def test_repeatable_connect_disconnect_cycles() -> None:
    adapter = NullBrokerAdapter()
    for _ in range(5):
        result = adapter.connect()
        assert result.accepted
        assert adapter.is_connected()
        adapter.disconnect()
        assert not adapter.is_connected()


def test_disconnect_is_idempotent_when_already_disconnected() -> None:
    adapter = NullBrokerAdapter()
    adapter.disconnect()  # never connected -- must be a no-op, never raise
    adapter.disconnect()
    assert not adapter.is_connected()


def test_operations_refuse_cleanly_while_disconnected() -> None:
    adapter = NullBrokerAdapter()
    assert not adapter.is_connected()

    from ai_trader.execution_engine.adapters.tests._fixtures_order import make_order_request

    ack = adapter.submit_order(make_order_request())
    assert isinstance(ack, BrokerAck)
    assert ack.accepted is False
    assert ack.reason == "NOT_CONNECTED"

    cancel_ack = adapter.cancel_order("whatever-id")
    assert cancel_ack.accepted is False
    assert cancel_ack.reason == "NOT_CONNECTED"


def test_heartbeat_false_while_disconnected() -> None:
    adapter = NullBrokerAdapter()
    assert adapter.heartbeat() is False


def test_mt5_adapter_lifecycle_with_fake_gateway() -> None:
    gateway = FakeMT5Gateway()
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    result = adapter.connect()
    assert result.accepted
    assert adapter.is_connected()
    assert gateway.initialize_calls == 1
    adapter.disconnect()
    assert not adapter.is_connected()
    assert gateway.shutdown_calls == 1


def test_mt5_adapter_repeatable_connect_disconnect() -> None:
    gateway = FakeMT5Gateway()
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    for _ in range(3):
        assert adapter.connect().accepted
        assert adapter.is_connected()
        adapter.disconnect()
        assert not adapter.is_connected()
    assert gateway.initialize_calls == 3
    assert gateway.shutdown_calls == 3

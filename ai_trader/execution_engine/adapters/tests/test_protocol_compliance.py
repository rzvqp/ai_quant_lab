"""Control 1 (CEO's own mandatory test list): Protocol compliance. `NullBrokerAdapter` implements BOTH
the pre-existing `BrokerAdapter` Protocol (unmodified) and the new `BrokerConnectionLifecycle` Protocol.
`MT5ReadOnlyBrokerAdapter` implements `BrokerConnectionLifecycle` only, by deliberate design (its own
module docstring explains why it does not implement `BrokerAdapter`'s trading methods at all)."""

from __future__ import annotations

from ai_trader.execution_engine.adapters.connection import BrokerConnectionLifecycle
from ai_trader.execution_engine.adapters.mt5_adapter import MT5ReadOnlyBrokerAdapter
from ai_trader.execution_engine.adapters.null_adapter import NullBrokerAdapter
from ai_trader.execution_engine.adapters.tests._fixtures import FakeMT5Gateway
from ai_trader.execution_engine.broker_adapter import BrokerAdapter


def test_null_broker_adapter_satisfies_broker_adapter_protocol() -> None:
    adapter = NullBrokerAdapter()
    assert isinstance(adapter, BrokerAdapter)


def test_null_broker_adapter_satisfies_connection_lifecycle_protocol() -> None:
    adapter = NullBrokerAdapter()
    assert isinstance(adapter, BrokerConnectionLifecycle)


def test_mt5_adapter_satisfies_connection_lifecycle_protocol() -> None:
    adapter = MT5ReadOnlyBrokerAdapter(gateway=FakeMT5Gateway())
    assert isinstance(adapter, BrokerConnectionLifecycle)


def test_mt5_adapter_deliberately_does_not_satisfy_broker_adapter_protocol() -> None:
    """Deliberate, disclosed scope limit (mt5_adapter.py's own module docstring) -- this read-only
    adapter never implements submit_order/cancel_order/capabilities()/query_status/query_open_orders,
    so it does NOT satisfy the full BrokerAdapter Protocol shape. Asserted explicitly so any future
    accidental addition of those methods is caught by a failing test, not silently allowed to drift."""
    adapter = MT5ReadOnlyBrokerAdapter(gateway=FakeMT5Gateway())
    assert not isinstance(adapter, BrokerAdapter)
    assert not hasattr(adapter, "submit_order")
    assert not hasattr(adapter, "cancel_order")

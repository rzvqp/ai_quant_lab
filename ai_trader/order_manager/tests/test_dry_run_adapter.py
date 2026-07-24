from __future__ import annotations

from ai_trader.execution_engine.types import OrderRequest, OrderState
from ai_trader.order_manager.builder import build_order_request
from ai_trader.order_manager.dry_run_adapter import DryRunBrokerAdapter
from ai_trader.order_manager.tests._fixtures import make_capabilities, make_instrument, make_intent


def _built_order() -> OrderRequest:
    outcome = build_order_request(make_intent(), make_instrument())
    assert outcome.order is not None
    return outcome.order


def test_submit_without_connect_is_refused() -> None:
    adapter = DryRunBrokerAdapter(make_capabilities())
    ack = adapter.submit_order(_built_order())
    assert ack.accepted is False
    assert ack.reason == "NOT_CONNECTED"


def test_submit_after_connect_reaches_acknowledged_never_filled() -> None:
    adapter = DryRunBrokerAdapter(make_capabilities())
    adapter.connect()
    order = _built_order()
    ack = adapter.submit_order(order)
    assert ack.accepted is True
    status = adapter.query_status(order.client_order_id)
    assert status is not None
    assert status.state is OrderState.ACKNOWLEDGED
    assert status.state not in (OrderState.FILLED, OrderState.PARTIALLY_FILLED)


def test_repeated_submit_for_same_client_order_id_is_idempotent() -> None:
    adapter = DryRunBrokerAdapter(make_capabilities())
    adapter.connect()
    order = _built_order()
    first = adapter.submit_order(order)
    second = adapter.submit_order(order)
    assert first == second


def test_capabilities_returns_the_configured_profile() -> None:
    caps = make_capabilities()
    adapter = DryRunBrokerAdapter(caps)
    assert adapter.capabilities() is caps


def test_cancel_unknown_order_is_refused() -> None:
    adapter = DryRunBrokerAdapter(make_capabilities())
    adapter.connect()
    ack = adapter.cancel_order("UNKNOWN-ID")
    assert ack.accepted is False
    assert ack.reason == "UNKNOWN_ORDER"


def test_cancel_known_order_succeeds_and_removes_from_open_orders() -> None:
    adapter = DryRunBrokerAdapter(make_capabilities())
    adapter.connect()
    order = _built_order()
    adapter.submit_order(order)
    assert order.client_order_id in {s.client_order_id for s in adapter.query_open_orders()}
    ack = adapter.cancel_order(order.client_order_id)
    assert ack.accepted is True
    assert order.client_order_id not in {s.client_order_id for s in adapter.query_open_orders()}


def test_disconnect_clears_in_memory_orders() -> None:
    adapter = DryRunBrokerAdapter(make_capabilities())
    adapter.connect()
    order = _built_order()
    adapter.submit_order(order)
    adapter.disconnect()
    assert adapter.query_status(order.client_order_id) is None


def test_connect_always_succeeds_zero_network() -> None:
    adapter = DryRunBrokerAdapter(make_capabilities())
    result = adapter.connect()
    assert result.accepted is True
    assert adapter.is_connected() is True

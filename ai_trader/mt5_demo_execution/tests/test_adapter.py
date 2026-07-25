from __future__ import annotations

from types import SimpleNamespace

from ai_trader.execution_engine.types import OrderState
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.tests._fixtures import FakeMT5DemoGateway, make_order_request
from ai_trader.mt5_demo_execution.types import MT5DemoConfig


def _connected_adapter(gateway: FakeMT5DemoGateway | None = None, config: MT5DemoConfig | None = None) -> MT5DemoBrokerAdapter:
    adapter = MT5DemoBrokerAdapter(gateway=gateway if gateway is not None else FakeMT5DemoGateway(), config=config)
    adapter.connect()
    return adapter


def test_submit_without_connect_is_refused() -> None:
    adapter = MT5DemoBrokerAdapter(gateway=FakeMT5DemoGateway())
    ack = adapter.submit_order(make_order_request())
    assert ack.accepted is False
    assert "NOT_CONNECTED" in (ack.reason or "")


def test_submit_refused_when_algo_trading_disabled() -> None:
    gateway = FakeMT5DemoGateway(algo_trading_enabled=False)
    adapter = _connected_adapter(gateway)
    ack = adapter.submit_order(make_order_request())
    assert ack.accepted is False
    assert "TRADING_DISABLED_AT_TERMINAL" in (ack.reason or "")
    assert gateway.order_check_calls == []
    assert gateway.order_send_calls == []


def test_submit_refused_when_volume_exceeds_configured_maximum() -> None:
    adapter = _connected_adapter(config=MT5DemoConfig(max_order_volume=0.01))
    ack = adapter.submit_order(make_order_request(quantity=1.0))
    assert ack.accepted is False
    assert "VOLUME_EXCEEDS_CONFIGURED_MAXIMUM" in (ack.reason or "")


def test_order_check_failure_never_reaches_order_send() -> None:
    gateway = FakeMT5DemoGateway(order_check_result=SimpleNamespace(retcode=10004, comment="Requote", balance=None, margin=None, margin_free=None))
    adapter = _connected_adapter(gateway)
    ack = adapter.submit_order(make_order_request())
    assert ack.accepted is False
    assert "ORDER_CHECK_FAILED" in (ack.reason or "")
    assert len(gateway.order_check_calls) == 1
    assert gateway.order_send_calls == []


def test_order_send_failure_after_successful_check() -> None:
    gateway = FakeMT5DemoGateway(order_send_result=SimpleNamespace(retcode=10013, comment="Invalid request", order=None, deal=None, volume=None, price=None))
    adapter = _connected_adapter(gateway)
    ack = adapter.submit_order(make_order_request())
    assert ack.accepted is False
    assert "ORDER_SEND_FAILED" in (ack.reason or "")
    assert len(gateway.order_check_calls) == 1
    assert len(gateway.order_send_calls) == 1


def test_successful_submit_reaches_acknowledged() -> None:
    gateway = FakeMT5DemoGateway()
    adapter = _connected_adapter(gateway)
    order = make_order_request()
    ack = adapter.submit_order(order)
    assert ack.accepted is True
    assert ack.broker_order_id == "123456"
    status = adapter.query_status(order.client_order_id)
    assert status is not None
    assert status.state is OrderState.ACKNOWLEDGED
    assert status.filled_qty == 0.01


def test_repeated_submit_is_idempotent_never_double_sends() -> None:
    gateway = FakeMT5DemoGateway()
    adapter = _connected_adapter(gateway)
    order = make_order_request()
    first = adapter.submit_order(order)
    second = adapter.submit_order(order)
    assert first == second
    assert len(gateway.order_send_calls) == 1


def test_query_open_orders_lists_acknowledged() -> None:
    adapter = _connected_adapter()
    order = make_order_request()
    adapter.submit_order(order)
    open_orders = adapter.query_open_orders()
    assert len(open_orders) == 1
    assert open_orders[0].client_order_id == order.client_order_id


def test_capabilities_reflect_configured_max_volume() -> None:
    adapter = _connected_adapter(config=MT5DemoConfig(max_order_volume=0.05))
    caps = adapter.capabilities()
    assert caps.max_qty == 0.05


def test_adapter_never_implements_cancel_order() -> None:
    assert not hasattr(MT5DemoBrokerAdapter, "cancel_order") or "cancel_order" not in MT5DemoBrokerAdapter.__dict__

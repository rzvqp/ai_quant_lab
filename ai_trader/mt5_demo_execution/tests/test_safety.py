from __future__ import annotations

from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.safety import is_market_open_for_symbol, verify_safety_guards
from ai_trader.mt5_demo_execution.tests._fixtures import AS_OF, FakeMT5DemoGateway
from ai_trader.mt5_demo_execution.types import MT5DemoConfig


def test_market_open_true_for_fresh_tick() -> None:
    gateway = FakeMT5DemoGateway(tick_time=AS_OF)
    adapter = MT5DemoBrokerAdapter(gateway=gateway)
    adapter.connect()
    result = is_market_open_for_symbol(adapter, "XAUUSD", MT5DemoConfig(), clock=lambda: AS_OF + 10)
    assert result is True


def test_market_closed_for_stale_tick() -> None:
    gateway = FakeMT5DemoGateway(tick_time=AS_OF)
    adapter = MT5DemoBrokerAdapter(gateway=gateway)
    adapter.connect()
    config = MT5DemoConfig(market_staleness_threshold_seconds=60)
    result = is_market_open_for_symbol(adapter, "XAUUSD", config, clock=lambda: AS_OF + 3600)
    assert result is False


def test_market_open_none_when_no_tick_data() -> None:
    gateway = FakeMT5DemoGateway()
    adapter = MT5DemoBrokerAdapter(gateway=gateway)
    adapter.connect()
    result = is_market_open_for_symbol(adapter, "UNKNOWN_SYMBOL", MT5DemoConfig(), clock=lambda: AS_OF)
    assert result is None


def test_verify_safety_guards_not_connected() -> None:
    adapter = MT5DemoBrokerAdapter(gateway=FakeMT5DemoGateway())
    report = verify_safety_guards(adapter, MT5DemoConfig())
    assert report.connected is False
    assert report.all_passed is False


def test_verify_safety_guards_all_pass_with_symbol_and_fresh_tick() -> None:
    gateway = FakeMT5DemoGateway(tick_time=AS_OF)
    adapter = MT5DemoBrokerAdapter(gateway=gateway)
    adapter.connect()
    report = verify_safety_guards(adapter, MT5DemoConfig(), symbol="XAUUSD", clock=lambda: AS_OF + 5)
    assert report.all_passed is True


def test_verify_safety_guards_fails_when_algo_trading_disabled() -> None:
    gateway = FakeMT5DemoGateway(algo_trading_enabled=False, tick_time=AS_OF)
    adapter = MT5DemoBrokerAdapter(gateway=gateway)
    adapter.connect()
    report = verify_safety_guards(adapter, MT5DemoConfig(), symbol="XAUUSD", clock=lambda: AS_OF + 5)
    assert report.algo_trading_enabled is False
    assert report.all_passed is False


def test_verify_safety_guards_without_symbol_leaves_market_open_none() -> None:
    adapter = MT5DemoBrokerAdapter(gateway=FakeMT5DemoGateway())
    adapter.connect()
    report = verify_safety_guards(adapter, MT5DemoConfig())
    assert report.market_open is None
    assert report.all_passed is False  # fail-closed: undeterminable market state never passes


def test_verify_safety_guards_fails_on_unexpected_server() -> None:
    gateway = FakeMT5DemoGateway(is_demo_server="SomeOtherBroker-Demo", tick_time=AS_OF)
    adapter = MT5DemoBrokerAdapter(gateway=gateway)
    adapter.connect()
    config = MT5DemoConfig(expected_server="FusionMarkets-Demo")
    report = verify_safety_guards(adapter, config, symbol="XAUUSD", clock=lambda: AS_OF + 5)
    assert report.server_matches_expected is False
    assert report.all_passed is False

"""Controls 5-7 (CEO's own mandatory test list): DEMO account detection, non-DEMO account refusal via
mock/fake, and AlgoTrading=False detection. Every scenario here uses `FakeMT5Gateway` -- no real
terminal involved."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from ai_trader.execution_engine.adapters.connection import BrokerCredentials, ConnectionState
from ai_trader.execution_engine.adapters.exceptions import (
    AccountValidationError,
    NonDemoAccountError,
    TerminalNotConnectedError,
    UnexpectedServerError,
)
from ai_trader.execution_engine.adapters.mt5_adapter import MT5ReadOnlyBrokerAdapter
from ai_trader.execution_engine.adapters.mt5_types import AccountTradeMode, AlgoTradingStatus
from ai_trader.execution_engine.adapters.tests._fixtures import FakeMT5Gateway


def test_demo_account_is_detected_and_accepted() -> None:
    gateway = FakeMT5Gateway()  # default: trade_mode=0 (DEMO)
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    result = adapter.connect()
    assert result.accepted
    status = adapter.status()
    assert status.account_trade_mode is AccountTradeMode.DEMO
    assert status.account_is_demo is True


def test_real_account_is_refused_via_fake_gateway() -> None:
    gateway = FakeMT5Gateway()
    gateway.account_info_result = SimpleNamespace(
        trade_mode=AccountTradeMode.REAL.value, trade_allowed=True, server="SomeRealServer",
    )
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    with pytest.raises(NonDemoAccountError):
        adapter.connect()
    assert not adapter.is_connected()
    assert adapter.connection_state() is ConnectionState.REFUSED


def test_contest_account_is_also_refused_not_only_real() -> None:
    gateway = FakeMT5Gateway()
    gateway.account_info_result = SimpleNamespace(
        trade_mode=AccountTradeMode.CONTEST.value, trade_allowed=True, server="ContestServer",
    )
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    with pytest.raises(NonDemoAccountError):
        adapter.connect()


def test_unexpected_server_is_refused_when_expected_server_configured() -> None:
    gateway = FakeMT5Gateway()  # server="FusionMarkets-Demo"
    adapter = MT5ReadOnlyBrokerAdapter(
        gateway=gateway, credentials=BrokerCredentials(expected_server="SomeOtherServer-Demo"),
    )
    with pytest.raises(UnexpectedServerError):
        adapter.connect()


def test_matching_expected_server_is_accepted() -> None:
    gateway = FakeMT5Gateway()
    adapter = MT5ReadOnlyBrokerAdapter(
        gateway=gateway, credentials=BrokerCredentials(expected_server="FusionMarkets-Demo"),
    )
    assert adapter.connect().accepted


def test_no_expected_server_configured_skips_the_check() -> None:
    gateway = FakeMT5Gateway()  # expected_server unset -> the check is skipped entirely
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    assert adapter.connect().accepted


def test_terminal_not_connected_is_refused() -> None:
    gateway = FakeMT5Gateway()
    gateway.terminal_info_result = SimpleNamespace(connected=False, trade_allowed=True, build=5836)
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    with pytest.raises(TerminalNotConnectedError):
        adapter.connect()


def test_unreadable_terminal_info_is_refused() -> None:
    gateway = FakeMT5Gateway()
    gateway.terminal_info_result = None
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    with pytest.raises(AccountValidationError):
        adapter.connect()


def test_unreadable_account_info_is_refused() -> None:
    gateway = FakeMT5Gateway()
    gateway.account_info_result = None
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    with pytest.raises(AccountValidationError):
        adapter.connect()


def test_algo_trading_disabled_at_terminal_is_detected_and_reported() -> None:
    gateway = FakeMT5Gateway()
    gateway.terminal_info_result = SimpleNamespace(connected=True, trade_allowed=False, build=5836)
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    result = adapter.connect()
    assert result.accepted  # AlgoTrading being disabled does NOT block a read-only adapter's own connect
    status = adapter.status()
    assert status.terminal_algo_trading_allowed is False
    assert status.algo_trading_status is AlgoTradingStatus.TRADING_DISABLED_AT_TERMINAL


def test_algo_trading_enabled_is_reported_correctly() -> None:
    gateway = FakeMT5Gateway()  # default: trade_allowed=True
    adapter = MT5ReadOnlyBrokerAdapter(gateway=gateway)
    adapter.connect()
    status = adapter.status()
    assert status.algo_trading_status is AlgoTradingStatus.ENABLED

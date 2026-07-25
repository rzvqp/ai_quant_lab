"""`MT5AccountBridge` tests: real-shaped happy path, fail-closed on every missing-data case, and --
this package's own specific constraint -- proof that nothing is ever cached across calls."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from ai_trader.mt5_account_bridge.source import MT5AccountBridge
from ai_trader.mt5_account_bridge.tests._fixtures import FakeMT5AccountGateway, _RawAccount, _RawSymbolInfo
from ai_trader.mt5_account_bridge.types import AccountDataUnavailableError

AS_OF = 1_700_000_000


def test_read_account_state_happy_path() -> None:
    gateway = FakeMT5AccountGateway(account=_RawAccount(
        trade_mode=0, currency="USD", balance=10_000.0, equity=9_500.0, margin=200.0,
        margin_free=9_300.0, margin_level=4750.0, leverage=500.0,
    ))
    bridge = MT5AccountBridge(gateway, clock=lambda: AS_OF)
    account = bridge.read_account_state()

    assert account.as_of == AS_OF
    assert account.currency == "USD"
    assert account.balance == 10_000.0
    assert account.equity == 9_500.0
    assert account.margin_used == 200.0
    assert account.margin_free == 9_300.0
    assert account.margin_level == 4750.0
    assert account.leverage == 500.0
    assert account.is_demo is True


def test_read_account_state_is_demo_false_for_a_real_trade_mode() -> None:
    gateway = FakeMT5AccountGateway(account=_RawAccount(trade_mode=2))  # AccountTradeMode.REAL
    bridge = MT5AccountBridge(gateway, clock=lambda: AS_OF)
    assert bridge.read_account_state().is_demo is False


def test_read_account_state_raises_when_account_info_is_none() -> None:
    gateway = FakeMT5AccountGateway(account=None)
    bridge = MT5AccountBridge(gateway, clock=lambda: AS_OF)
    with pytest.raises(AccountDataUnavailableError):
        bridge.read_account_state()


def test_read_account_state_raises_when_a_required_field_is_missing() -> None:
    incomplete = SimpleNamespace(trade_mode=0, currency="USD", balance=10_000.0, equity=10_000.0)
    # missing margin/margin_free/margin_level/leverage entirely -- not just zeroed
    gateway = FakeMT5AccountGateway(account=incomplete)
    bridge = MT5AccountBridge(gateway, clock=lambda: AS_OF)
    with pytest.raises(AccountDataUnavailableError):
        bridge.read_account_state()


def test_read_account_state_never_caches() -> None:
    gateway = FakeMT5AccountGateway(account=_RawAccount(equity=10_000.0))
    bridge = MT5AccountBridge(gateway, clock=lambda: AS_OF)
    first = bridge.read_account_state()
    assert first.equity == 10_000.0

    gateway.account = _RawAccount(equity=8_000.0)
    second = bridge.read_account_state()
    assert second.equity == 8_000.0
    assert gateway.account_info_calls == 2


def test_read_instrument_specification_happy_path() -> None:
    gateway = FakeMT5AccountGateway(symbols={"XAUUSD": _RawSymbolInfo(
        trade_tick_size=0.01, volume_step=0.01, volume_min=0.01, volume_max=100.0,
        trade_contract_size=100.0, trade_tick_value=1.0, currency_margin="USD",
    )})
    bridge = MT5AccountBridge(gateway, clock=lambda: AS_OF)
    instrument = bridge.read_instrument_specification("XAUUSD")

    assert instrument.symbol == "XAUUSD"
    assert instrument.tick_size == 0.01
    assert instrument.lot_step == 0.01
    assert instrument.min_volume == 0.01
    assert instrument.max_volume == 100.0
    assert instrument.contract_size == 100.0
    assert instrument.point_value == pytest.approx(1.0 / 0.01)
    assert instrument.margin_currency == "USD"


def test_read_instrument_specification_selects_the_symbol_before_reading_it() -> None:
    """Mirrors `MT5ReadOnlyBrokerAdapter.symbol_capabilities()`'s own established precedent: a symbol
    not already on the terminal's own Market Watch list can otherwise report stale/no data."""
    gateway = FakeMT5AccountGateway(symbols={"XAUUSD": _RawSymbolInfo()})
    bridge = MT5AccountBridge(gateway, clock=lambda: AS_OF)
    bridge.read_instrument_specification("XAUUSD")
    assert gateway.symbol_select_calls == ["XAUUSD"]
    assert gateway.symbol_info_calls == ["XAUUSD"]


def test_read_instrument_specification_raises_when_symbol_info_is_none() -> None:
    gateway = FakeMT5AccountGateway(symbols={"XAUUSD": None})
    bridge = MT5AccountBridge(gateway, clock=lambda: AS_OF)
    with pytest.raises(AccountDataUnavailableError):
        bridge.read_instrument_specification("XAUUSD")


def test_read_instrument_specification_raises_when_a_required_field_is_missing() -> None:
    incomplete = SimpleNamespace(trade_tick_size=0.01, volume_step=0.01)  # missing the rest
    gateway = FakeMT5AccountGateway(symbols={"XAUUSD": incomplete})  # type: ignore[dict-item]
    bridge = MT5AccountBridge(gateway, clock=lambda: AS_OF)
    with pytest.raises(AccountDataUnavailableError):
        bridge.read_instrument_specification("XAUUSD")


def test_read_instrument_specification_raises_on_zero_tick_size_rather_than_dividing_by_zero() -> None:
    gateway = FakeMT5AccountGateway(symbols={"XAUUSD": _RawSymbolInfo(trade_tick_size=0.0)})
    bridge = MT5AccountBridge(gateway, clock=lambda: AS_OF)
    with pytest.raises(AccountDataUnavailableError):
        bridge.read_instrument_specification("XAUUSD")


def test_read_instrument_specification_never_caches() -> None:
    gateway = FakeMT5AccountGateway(symbols={"XAUUSD": _RawSymbolInfo(volume_max=100.0)})
    bridge = MT5AccountBridge(gateway, clock=lambda: AS_OF)
    first = bridge.read_instrument_specification("XAUUSD")
    assert first.max_volume == 100.0

    gateway.symbols["XAUUSD"] = _RawSymbolInfo(volume_max=50.0)
    second = bridge.read_instrument_specification("XAUUSD")
    assert second.max_volume == 50.0
    assert len(gateway.symbol_info_calls) == 2

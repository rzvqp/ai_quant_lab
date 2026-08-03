"""`LiveMT5FillReader` tests -- with a local fake `MT5HistoryGateway`, never a real terminal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai_trader.pdh_pdl_demo.live_fill_reader import LiveMT5FillReader

SYMBOL = "XAUUSD"
MAGIC = 100_001
_DEAL_ENTRY_IN = 0
_DEAL_ENTRY_OUT = 1


@dataclass
class _RawPosition:
    magic: int
    symbol: str


@dataclass
class _RawDeal:
    magic: int
    symbol: str
    entry: int
    time: int
    price: float


class _FakeHistoryGateway:
    """Stubs the FULL `MT5HistoryGateway` Protocol surface, even the methods this reader never calls --
    same established convention as `mt5_pnl_source/tests/_fixtures.py::FakeMT5HistoryGateway`."""

    def __init__(self, positions: tuple[Any, ...] | None, deals: tuple[Any, ...] | None) -> None:
        self._positions = positions
        self._deals = deals
        self.history_calls: list[tuple[int, int]] = []

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
        return None

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any:
        return None

    def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any:
        return None

    def copy_ticks_from(self, symbol: str, date_from: int, count: int, flags: int) -> Any:
        return None

    def copy_ticks_range(self, symbol: str, date_from: int, date_to: int, flags: int) -> Any:
        return None

    def orders_get(self, symbol: str | None = None) -> Any:
        return ()

    def last_error(self) -> tuple[int, str]:
        return (0, "Success")

    def positions_get(self, symbol: str | None = None) -> tuple[Any, ...] | None:
        return self._positions

    def history_deals_get(self, date_from: int, date_to: int) -> tuple[Any, ...] | None:
        self.history_calls.append((date_from, date_to))
        return self._deals


def test_is_position_open_true_when_a_position_with_the_magic_number_exists() -> None:
    gateway = _FakeHistoryGateway(positions=(_RawPosition(magic=MAGIC, symbol=SYMBOL),), deals=None)
    reader = LiveMT5FillReader(gateway, clock=lambda: 1_700_010_000)
    assert reader.is_position_open(MAGIC, SYMBOL) is True


def test_is_position_open_false_when_no_matching_magic() -> None:
    gateway = _FakeHistoryGateway(positions=(_RawPosition(magic=999, symbol=SYMBOL),), deals=None)
    reader = LiveMT5FillReader(gateway, clock=lambda: 1_700_010_000)
    assert reader.is_position_open(MAGIC, SYMBOL) is False


def test_is_position_open_none_when_gateway_read_fails() -> None:
    gateway = _FakeHistoryGateway(positions=None, deals=None)
    reader = LiveMT5FillReader(gateway, clock=lambda: 1_700_010_000)
    assert reader.is_position_open(MAGIC, SYMBOL) is None


def test_read_close_price_finds_the_matching_closing_deal() -> None:
    deals = (
        _RawDeal(magic=MAGIC, symbol=SYMBOL, entry=_DEAL_ENTRY_IN, time=1_700_000_100, price=4050.0),
        _RawDeal(magic=MAGIC, symbol=SYMBOL, entry=_DEAL_ENTRY_OUT, time=1_700_000_900, price=4055.5),
    )
    gateway = _FakeHistoryGateway(positions=None, deals=deals)
    reader = LiveMT5FillReader(gateway, clock=lambda: 1_700_010_000)
    assert reader.read_close_price(MAGIC, SYMBOL, since_ts=1_700_000_000) == 4055.5


def test_read_close_price_ignores_other_magic_numbers_and_symbols() -> None:
    deals = (
        _RawDeal(magic=999, symbol=SYMBOL, entry=_DEAL_ENTRY_OUT, time=1_700_000_900, price=1.0),
        _RawDeal(magic=MAGIC, symbol="EURUSD", entry=_DEAL_ENTRY_OUT, time=1_700_000_900, price=2.0),
    )
    gateway = _FakeHistoryGateway(positions=None, deals=deals)
    reader = LiveMT5FillReader(gateway, clock=lambda: 1_700_010_000)
    assert reader.read_close_price(MAGIC, SYMBOL, since_ts=1_700_000_000) is None


def test_read_close_price_ignores_opening_deals() -> None:
    deals = (_RawDeal(magic=MAGIC, symbol=SYMBOL, entry=_DEAL_ENTRY_IN, time=1_700_000_900, price=4050.0),)
    gateway = _FakeHistoryGateway(positions=None, deals=deals)
    reader = LiveMT5FillReader(gateway, clock=lambda: 1_700_010_000)
    assert reader.read_close_price(MAGIC, SYMBOL, since_ts=1_700_000_000) is None


def test_read_close_price_picks_the_latest_matching_deal_when_several_exist() -> None:
    deals = (
        _RawDeal(magic=MAGIC, symbol=SYMBOL, entry=_DEAL_ENTRY_OUT, time=1_700_000_500, price=4040.0),
        _RawDeal(magic=MAGIC, symbol=SYMBOL, entry=_DEAL_ENTRY_OUT, time=1_700_000_900, price=4055.5),
    )
    gateway = _FakeHistoryGateway(positions=None, deals=deals)
    reader = LiveMT5FillReader(gateway, clock=lambda: 1_700_010_000)
    assert reader.read_close_price(MAGIC, SYMBOL, since_ts=1_700_000_000) == 4055.5


def test_read_close_price_none_when_gateway_read_fails() -> None:
    gateway = _FakeHistoryGateway(positions=None, deals=None)
    reader = LiveMT5FillReader(gateway, clock=lambda: 1_700_010_000)
    assert reader.read_close_price(MAGIC, SYMBOL, since_ts=1_700_000_000) is None


def test_read_close_price_uses_padded_lookback_window() -> None:
    gateway = _FakeHistoryGateway(positions=None, deals=())
    reader = LiveMT5FillReader(gateway, clock=lambda: 1_700_010_000)
    reader.read_close_price(MAGIC, SYMBOL, since_ts=1_700_000_000)
    assert gateway.history_calls == [(1_700_000_000 - 3600, 1_700_010_000)]

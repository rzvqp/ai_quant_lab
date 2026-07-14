"""Unit tests for ai_trader.market_scanner.types value objects."""

import pytest

from ai_trader.market_scanner.types import RawBar, RawTick, SymbolMeta


def _bar(**overrides: object) -> RawBar:
    defaults: dict[str, object] = dict(
        symbol="XAUUSD", timeframe="M15", ts_open=900, ts_close=1800,
        open=2000.0, high=2005.0, low=1995.0, close=2001.0, volume=100.0, complete=True,
    )
    defaults.update(overrides)
    return RawBar(**defaults)  # type: ignore[arg-type]


class TestSymbolMeta:
    def test_valid(self) -> None:
        m = SymbolMeta(symbol="XAUUSD", tick_size=0.1, point_value=1.0, price_precision=2)
        assert m.symbol == "XAUUSD"

    def test_rejects_empty_symbol(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            SymbolMeta(symbol="", tick_size=0.1, point_value=1.0, price_precision=2)

    def test_rejects_nonpositive_tick_size(self) -> None:
        with pytest.raises(ValueError, match="tick_size"):
            SymbolMeta(symbol="X", tick_size=0.0, point_value=1.0, price_precision=2)

    def test_rejects_nonpositive_point_value(self) -> None:
        with pytest.raises(ValueError, match="point_value"):
            SymbolMeta(symbol="X", tick_size=0.1, point_value=-1.0, price_precision=2)

    def test_rejects_negative_precision(self) -> None:
        with pytest.raises(ValueError, match="price_precision"):
            SymbolMeta(symbol="X", tick_size=0.1, point_value=1.0, price_precision=-1)

    def test_frozen(self) -> None:
        m = SymbolMeta(symbol="X", tick_size=0.1, point_value=1.0, price_precision=2)
        with pytest.raises(AttributeError):
            m.symbol = "Y"  # type: ignore[misc]


class TestRawBar:
    def test_valid(self) -> None:
        b = _bar()
        assert b.available_at == b.ts_close == 1800

    def test_rejects_close_not_after_open(self) -> None:
        with pytest.raises(ValueError, match="ts_close"):
            _bar(ts_close=900)

    def test_rejects_high_below_low(self) -> None:
        with pytest.raises(ValueError, match="high"):
            _bar(high=1990.0, low=1995.0)

    def test_rejects_open_outside_range(self) -> None:
        with pytest.raises(ValueError, match="open"):
            _bar(open=2010.0)

    def test_rejects_close_outside_range(self) -> None:
        with pytest.raises(ValueError, match="close"):
            _bar(close=2010.0)

    def test_rejects_non_finite_price(self) -> None:
        with pytest.raises(ValueError, match="finite"):
            _bar(close=float("nan"))

    def test_rejects_negative_volume(self) -> None:
        with pytest.raises(ValueError, match="volume"):
            _bar(volume=-1.0)

    def test_allows_none_volume(self) -> None:
        b = _bar(volume=None)
        assert b.volume is None


class TestRawTick:
    def test_valid_bid_ask(self) -> None:
        t = RawTick(symbol="XAUUSD", ts=1000, bid=2000.0, ask=2000.2)
        assert t.mid == pytest.approx(2000.1)

    def test_valid_last_only(self) -> None:
        t = RawTick(symbol="XAUUSD", ts=1000, last=2000.5)
        assert t.mid == 2000.5

    def test_rejects_no_price_at_all(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            RawTick(symbol="XAUUSD", ts=1000)

    def test_rejects_bid_above_ask(self) -> None:
        with pytest.raises(ValueError, match="bid"):
            RawTick(symbol="XAUUSD", ts=1000, bid=2000.5, ask=2000.0)

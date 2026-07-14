"""Unit tests for ai_trader.market_scanner.bar_store."""

from ai_trader.market_scanner.bar_store import SymbolBarStore, TimeframeWindow, infer_gap_cause
from ai_trader.market_scanner.types import RawBar

_M15 = 900


def _bar(ts_open: int, complete: bool = True, **overrides: object) -> RawBar:
    defaults: dict[str, object] = dict(
        symbol="XAUUSD", timeframe="M15", ts_open=ts_open, ts_close=ts_open + _M15,
        open=100.0, high=101.0, low=99.0, close=100.5, volume=10.0, complete=complete,
    )
    defaults.update(overrides)
    return RawBar(**defaults)  # type: ignore[arg-type]


class TestTimeframeWindow:
    def test_ingest_in_order_no_gap(self) -> None:
        w = TimeframeWindow("M15", max_len=10)
        for i in range(5):
            gap = w.ingest_bar(_bar(i * _M15))
            assert gap is None
        assert len(w.bars()) == 5
        assert w.last_ingested_close == 5 * _M15

    def test_gap_detected_on_skip(self) -> None:
        w = TimeframeWindow("M15", max_len=10)
        w.ingest_bar(_bar(0))
        gap = w.ingest_bar(_bar(3 * _M15))  # skipped bars at 1*M15 and 2*M15
        assert gap is not None
        assert gap.bars_missing == 2
        assert gap.from_ts == _M15
        assert gap.to_ts == 3 * _M15

    def test_late_bar_for_already_closed_period_is_dropped(self) -> None:
        w = TimeframeWindow("M15", max_len=10)
        w.ingest_bar(_bar(2 * _M15))
        result = w.ingest_bar(_bar(0))  # arrives late, period already passed
        assert result is None
        assert w.late_dropped == 1
        assert len(w.bars()) == 1  # history was never rewritten

    def test_bounded_window_trims_oldest(self) -> None:
        w = TimeframeWindow("M15", max_len=3)
        for i in range(10):
            w.ingest_bar(_bar(i * _M15))
        assert len(w.bars()) == 3
        assert w.bars()[0].ts_open == 7 * _M15

    def test_forming_bar_never_in_complete_window(self) -> None:
        w = TimeframeWindow("M15", max_len=10)
        w.ingest_bar(_bar(0, complete=False))
        assert w.bars() == []
        assert w.forming is not None
        w.ingest_bar(_bar(0, complete=True))
        assert len(w.bars()) == 1
        assert w.forming is None  # closing bar clears the forming slot

    def test_apply_tick_creates_and_updates_forming_bar(self) -> None:
        w = TimeframeWindow("M15", max_len=10, symbol="XAUUSD")
        w.apply_tick(ts=10, price=100.0, volume=1.0)
        assert w.forming is not None
        assert w.forming.open == 100.0
        w.apply_tick(ts=20, price=105.0, volume=1.0)
        assert w.forming.high == 105.0
        assert w.forming.close == 105.0
        w.apply_tick(ts=30, price=95.0, volume=1.0)
        assert w.forming.low == 95.0

    def test_apply_tick_for_closed_period_is_dropped(self) -> None:
        w = TimeframeWindow("M15", max_len=10, symbol="XAUUSD")
        w.ingest_bar(_bar(2 * _M15))
        w.apply_tick(ts=10, price=100.0, volume=1.0)  # ts falls in an already-closed period
        assert w.late_dropped == 1


class TestInferGapCause:
    def test_weekend_gap_classified(self) -> None:
        # epoch 0 = Thursday 1970-01-01. Friday = +1 day, Monday = +4 days.
        friday_close = 1 * 86400
        monday_open = 4 * 86400
        assert infer_gap_cause(friday_close, monday_open) == "weekend"

    def test_weekday_gap_unclassified(self) -> None:
        tue = 5 * 86400
        wed = tue + 86400
        assert infer_gap_cause(tue, wed) is None


class TestSymbolBarStore:
    def test_ensure_timeframe_creates_and_reuses(self) -> None:
        store = SymbolBarStore("XAUUSD")
        w1 = store.ensure_timeframe("M15", 10)
        w2 = store.ensure_timeframe("M15", 10)
        assert w1 is w2

    def test_widen_preserves_bars(self) -> None:
        store = SymbolBarStore("XAUUSD")
        w = store.ensure_timeframe("M15", 3)
        for i in range(5):
            w.ingest_bar(_bar(i * _M15))
        assert len(w.bars()) == 3
        widened = store.ensure_timeframe("M15", 10)
        assert len(widened.bars()) == 3  # only what fit in the narrower window survives
        assert widened.last_ingested_close == 5 * _M15

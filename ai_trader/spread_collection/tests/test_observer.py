"""`SpreadCollector` tests -- same PDH/PDL touch scenario shape `pdh_pdl_demo`'s own recognition-rule
tests use (same ratified `institutional_levels` primitive), verifying the touch marker fires exactly on
the touch bar and nowhere else, alongside the spread/session/ATR fields."""

from __future__ import annotations

import pytest

from ai_trader.live_signal_source.types import Bar
from ai_trader.pdh_pdl_demo.types import LiveTick
from ai_trader.spread_collection.journal import SpreadObservationLog
from ai_trader.spread_collection.observer import SpreadCollector

SYMBOL = "XAUUSD"
BAR_SECONDS = 900
DAY0_START = 1_705_269_600
DAY1_START = 1_705_356_000


class _FakeTickReader:
    def __init__(self, tick: LiveTick | None) -> None:
        self._tick = tick

    def read(self, symbol: str) -> LiveTick | None:
        return self._tick


def _bar(ts_open: int, o: float, h: float, l: float, c: float, is_backfilled: bool = False) -> Bar:
    return Bar(
        symbol=SYMBOL, ts_open=ts_open, ts_close=ts_open + BAR_SECONDS, open=o, high=h, low=l, close=c,
        volume=100.0, is_backfilled=is_backfilled,
    )


def _day0_warmup_bars(pdh: float, pdl: float, n: int = 16) -> list[Bar]:
    bars = []
    for i in range(n):
        ts = DAY0_START + i * BAR_SECONDS
        if i == n - 2:
            bars.append(_bar(ts, 100.0, pdh, 99.5, 100.0))
        elif i == n - 1:
            bars.append(_bar(ts, 100.0, 100.5, pdl, 100.0))
        else:
            bars.append(_bar(ts, 100.0, 100.5, 99.5, 100.0))
    return bars


def test_records_bid_ask_spread_session_for_every_bar_with_a_live_tick() -> None:
    tick = LiveTick(bid=107.9, ask=108.1, as_of=DAY1_START)
    journal = SpreadObservationLog()
    collector = SpreadCollector(SYMBOL, _FakeTickReader(tick), journal)

    bar = _bar(DAY1_START, 100.0, 100.5, 99.5, 100.0)
    observation = collector.collect(bar)

    assert observation is not None
    assert observation.bid == 107.9
    assert observation.ask == 108.1
    assert observation.spread == pytest.approx(0.2)
    assert observation.session in ("asia", "london", "ny", "late")
    assert journal.entries == (observation,)


def test_no_live_tick_produces_no_observation_and_no_record() -> None:
    journal = SpreadObservationLog()
    collector = SpreadCollector(SYMBOL, _FakeTickReader(None), journal)

    bar = _bar(DAY1_START, 100.0, 100.5, 99.5, 100.0)
    observation = collector.collect(bar)

    assert observation is None
    assert journal.entries == ()


def test_atr_is_none_during_warmup_then_populated() -> None:
    tick = LiveTick(bid=99.9, ask=100.1, as_of=DAY0_START)
    journal = SpreadObservationLog()
    collector = SpreadCollector(SYMBOL, _FakeTickReader(tick), journal)

    bars = _day0_warmup_bars(110.0, 90.0, n=16)
    results = [collector.collect(b) for b in bars]

    assert results[0] is not None and results[0].atr is None  # ATR14 needs 15 bars
    assert results[-1] is not None and results[-1].atr is not None
    assert isinstance(results[-1].atr, float)


def test_fresh_level_touch_is_marked_true_with_correct_kind() -> None:
    pdh, pdl = 110.0, 90.0
    day0 = _day0_warmup_bars(pdh, pdl)
    day1_bar0 = _bar(DAY1_START, 100.0, 100.5, 99.5, 100.0)
    day1_touch = _bar(DAY1_START + BAR_SECONDS, 105.0, 111.0, 104.0, 108.0)  # PDH touch (high=111>=110)

    tick = LiveTick(bid=107.9, ask=108.1, as_of=day1_touch.ts_close)
    journal = SpreadObservationLog()
    collector = SpreadCollector(SYMBOL, _FakeTickReader(tick), journal)

    results = [collector.collect(b) for b in [*day0, day1_bar0, day1_touch]]

    assert all(r is not None and r.is_level_touch is False for r in results[:-1])
    last = results[-1]
    assert last is not None
    assert last.is_level_touch is True
    assert last.touch_level_kind == "pdh"


def test_bar_without_a_touch_is_marked_false() -> None:
    pdh, pdl = 110.0, 90.0
    day0 = _day0_warmup_bars(pdh, pdl)
    day1_bar0 = _bar(DAY1_START, 100.0, 100.5, 99.5, 100.0)  # no touch, well inside [pdl, pdh]

    tick = LiveTick(bid=99.9, ask=100.1, as_of=day1_bar0.ts_close)
    journal = SpreadObservationLog()
    collector = SpreadCollector(SYMBOL, _FakeTickReader(tick), journal)

    results = [collector.collect(b) for b in [*day0, day1_bar0]]

    last = results[-1]
    assert last is not None
    assert last.is_level_touch is False
    assert last.touch_level_kind is None


def test_a_backfilled_bar_produces_no_observation_even_with_a_live_tick() -> None:
    """CEO instruction, 2026-08-10: "Spread-ul NU se backfilleaza -- nu exista retroactiv" -- a bar
    recovered by `LiveBarFeed`'s gap-catch-up must never produce a spread observation, regardless of
    whether a live tick happens to be readable right now (it would be the WRONG tick -- read hours or
    days after the bar actually closed)."""
    tick = LiveTick(bid=107.9, ask=108.1, as_of=DAY1_START)
    journal = SpreadObservationLog()
    collector = SpreadCollector(SYMBOL, _FakeTickReader(tick), journal)

    bar = _bar(DAY1_START, 100.0, 100.5, 99.5, 100.0, is_backfilled=True)
    observation = collector.collect(bar)

    assert observation is None
    assert journal.entries == ()


def test_a_backfilled_bar_still_accumulates_into_level_touch_continuity() -> None:
    """The OHLC path itself IS real, recoverable history -- only the spread reading is irrecoverable.
    A later, non-backfilled bar's level-touch detection must still see the backfilled bar's own
    high/low, exactly as if it had been observed live."""
    pdh, pdl = 110.0, 90.0
    day0 = _day0_warmup_bars(pdh, pdl)
    backfilled_bar = _bar(DAY1_START, 100.0, 100.5, 99.5, 100.0, is_backfilled=True)
    live_touch_bar = _bar(DAY1_START + BAR_SECONDS, 105.0, 111.0, 104.0, 108.0)  # PDH touch

    tick = LiveTick(bid=107.9, ask=108.1, as_of=live_touch_bar.ts_close)
    journal = SpreadObservationLog()
    collector = SpreadCollector(SYMBOL, _FakeTickReader(tick), journal)

    for b in day0:
        collector.collect(b)
    assert collector.collect(backfilled_bar) is None
    assert collector.current_bar_count == len(day0) + 1

    result = collector.collect(live_touch_bar)

    assert result is not None
    assert result.is_level_touch is True
    assert result.touch_level_kind == "pdh"


def test_current_bar_count_tracks_bars_processed() -> None:
    tick = LiveTick(bid=99.9, ask=100.1, as_of=DAY0_START)
    journal = SpreadObservationLog()
    collector = SpreadCollector(SYMBOL, _FakeTickReader(tick), journal)
    bars = _day0_warmup_bars(110.0, 90.0, n=5)
    for b in bars:
        collector.collect(b)
    assert collector.current_bar_count == 5

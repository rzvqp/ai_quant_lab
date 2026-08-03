"""`PdhPdlRecognitionRule` tests. Anchor timestamps chosen at 2024-01-15 22:00 UTC = 17:00 NY standard
time (no DST ambiguity in the test data itself, though the anchor function is separately verified
numerically against real DST-transition data in `test_day_index.py`)."""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar, LiveCandidate
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.recognition_rule import MAGIC_NUMBER, STRATEGY_ID, PdhPdlRecognitionRule
from ai_trader.pdh_pdl_demo.types import LiveTick
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
BAR_SECONDS = 900
TICK_SIZE = 0.01
DAY0_START = 1_705_269_600  # 2024-01-14 22:00 UTC
DAY1_START = 1_705_356_000  # 2024-01-15 22:00 UTC (== 17:00 NY, no DST)
DAY2_START = 1_705_442_400  # 2024-01-16 22:00 UTC


class _FakeTickReader:
    def __init__(self, tick: LiveTick | None) -> None:
        self._tick = tick

    def read(self, symbol: str) -> LiveTick | None:
        return self._tick


def _bar(ts_open: int, o: float, h: float, l: float, c: float) -> Bar:
    return Bar(symbol=SYMBOL, ts_open=ts_open, ts_close=ts_open + BAR_SECONDS,
               open=o, high=h, low=l, close=c, volume=100.0)


def _day0_warmup_bars(pdh: float, pdl: float, n: int = 16) -> list[Bar]:
    """`n` flat bars inside day0 (ATR14 needs 15 bars for its first valid reading -- index 14), with
    the day's own high/low extremes set on the last two bars so PDH/PDL are unambiguous."""
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


def _feed(rule: PdhPdlRecognitionRule, bars: list[Bar]) -> list[LiveCandidate | None]:
    return [rule.evaluate(b) for b in bars]


def test_fresh_pdh_touch_produces_a_short_candidate_with_correct_stop_and_target() -> None:
    pdh, pdl = 110.0, 90.0
    day0 = _day0_warmup_bars(pdh, pdl)
    day1_bar0 = _bar(DAY1_START, 100.0, 100.5, 99.5, 100.0)  # available_idx, no touch
    day1_touch = _bar(DAY1_START + BAR_SECONDS, 105.0, 111.0, 104.0, 108.0)  # high=111 >= PDH=110

    tick = LiveTick(bid=107.9, ask=108.1, as_of=day1_touch.ts_close)
    journal = PdhPdlAuditJournal()
    rule = PdhPdlRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(tick), journal)

    results = _feed(rule, [*day0, day1_bar0, day1_touch])

    assert all(r is None for r in results[:-1])
    candidate = results[-1]
    assert candidate is not None
    assert candidate.strategy_id == STRATEGY_ID
    assert candidate.magic_number == MAGIC_NUMBER
    assert candidate.direction is Direction.SHORT
    assert candidate.entry == tick.bid
    assert candidate.target == pdl
    assert candidate.stop > candidate.entry  # SHORT invariant

    trigger = rule.last_trigger()
    assert trigger is not None
    assert trigger.direction == -1
    assert trigger.strategy_stop_price == 111.0  # touch bar's own high
    assert trigger.target_price == pdl
    assert trigger.effective_spread == tick.ask - tick.bid


def test_fresh_pdl_touch_produces_a_long_candidate() -> None:
    pdh, pdl = 110.0, 90.0
    day0 = _day0_warmup_bars(pdh, pdl)
    day1_bar0 = _bar(DAY1_START, 100.0, 100.5, 99.5, 100.0)
    day1_touch = _bar(DAY1_START + BAR_SECONDS, 95.0, 96.0, 89.0, 92.0)  # low=89 <= PDL=90

    tick = LiveTick(bid=91.9, ask=92.1, as_of=day1_touch.ts_close)
    journal = PdhPdlAuditJournal()
    rule = PdhPdlRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(tick), journal)

    results = _feed(rule, [*day0, day1_bar0, day1_touch])

    candidate = results[-1]
    assert candidate is not None
    assert candidate.direction is Direction.LONG
    assert candidate.entry == tick.ask
    assert candidate.target == pdh
    assert candidate.stop < candidate.entry  # LONG invariant


def test_no_second_candidate_for_the_same_consumed_touch() -> None:
    pdh, pdl = 110.0, 90.0
    day0 = _day0_warmup_bars(pdh, pdl)
    day1_bar0 = _bar(DAY1_START, 100.0, 100.5, 99.5, 100.0)
    day1_touch = _bar(DAY1_START + BAR_SECONDS, 105.0, 111.0, 104.0, 108.0)
    day1_after = _bar(DAY1_START + 2 * BAR_SECONDS, 108.0, 112.0, 107.0, 109.0)  # still >= PDH

    tick = LiveTick(bid=107.9, ask=108.1, as_of=day1_touch.ts_close)
    journal = PdhPdlAuditJournal()
    rule = PdhPdlRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(tick), journal)

    results = _feed(rule, [*day0, day1_bar0, day1_touch, day1_after])

    assert results[-2] is not None  # the actual touch bar
    assert results[-1] is None  # D7 consumption -- no re-trigger on a later bar still above PDH


def test_no_live_tick_produces_no_trade_and_is_journaled() -> None:
    pdh, pdl = 110.0, 90.0
    day0 = _day0_warmup_bars(pdh, pdl)
    day1_bar0 = _bar(DAY1_START, 100.0, 100.5, 99.5, 100.0)
    day1_touch = _bar(DAY1_START + BAR_SECONDS, 105.0, 111.0, 104.0, 108.0)

    journal = PdhPdlAuditJournal()
    rule = PdhPdlRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(None), journal)

    results = _feed(rule, [*day0, day1_bar0, day1_touch])

    assert results[-1] is None
    no_trade_entries = [e for e in journal.entries if e.detail.get("reason_code") == "LIVE_TICK_UNAVAILABLE"]
    assert len(no_trade_entries) == 1


def test_entry_beyond_target_at_live_quote_is_no_trade() -> None:
    """A live quote already past the target (PDL, the opposite level) at the moment of the touch --
    Part B's own validity guard, applied against the live reference price."""
    pdh, pdl = 110.0, 90.0
    day0 = _day0_warmup_bars(pdh, pdl)
    day1_bar0 = _bar(DAY1_START, 100.0, 100.5, 99.5, 100.0)
    day1_touch = _bar(DAY1_START + BAR_SECONDS, 105.0, 111.0, 104.0, 108.0)

    tick = LiveTick(bid=89.0, ask=89.2, as_of=day1_touch.ts_close)  # already through PDL=90
    journal = PdhPdlAuditJournal()
    rule = PdhPdlRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(tick), journal)

    results = _feed(rule, [*day0, day1_bar0, day1_touch])

    assert results[-1] is None
    reasons = [e.detail.get("reason_code") for e in journal.entries]
    assert "NO_TRADE_ENTRY_BEYOND_TARGET" in reasons


def test_atr_not_yet_available_is_no_trade() -> None:
    """Fewer than 15 bars fed -- ATR14 is NaN at the touch bar (vendored function's own documented
    warmup) -- must not silently proceed with an undefined risk floor."""
    pdh, pdl = 110.0, 90.0
    day0 = [
        _bar(DAY0_START, 100.0, pdh, 99.5, 100.0),
        _bar(DAY0_START + BAR_SECONDS, 100.0, 100.5, pdl, 100.0),
    ]
    day1_bar0 = _bar(DAY1_START, 100.0, 100.5, 99.5, 100.0)
    day1_touch = _bar(DAY1_START + BAR_SECONDS, 105.0, 111.0, 104.0, 108.0)

    tick = LiveTick(bid=107.9, ask=108.1, as_of=day1_touch.ts_close)
    journal = PdhPdlAuditJournal()
    rule = PdhPdlRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(tick), journal)

    results = _feed(rule, [*day0, day1_bar0, day1_touch])

    assert results[-1] is None
    reasons = [e.detail.get("reason_code") for e in journal.entries]
    assert "ATR_NOT_AVAILABLE_AT_TOUCH" in reasons

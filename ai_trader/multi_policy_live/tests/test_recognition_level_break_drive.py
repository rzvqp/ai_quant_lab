"""`LevelBreakDriveRecognitionRule` (CAND-0009, built but not started) tests. Bar sequence independently
verified against the real vendored `expansion`/`atr14`/`detect_level_touches` before transcribing: a PDH
touch at idx=17 coincides with a strong bullish displacement bar -> break-and-drive LONG, stop = the
broken level (PDH=110.0) itself, not the touch-bar extreme."""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar, LiveCandidate
from ai_trader.multi_policy_live.recognition_level_break_drive import (
    MAGIC_NUMBER,
    STRATEGY_ID,
    LevelBreakDriveRecognitionRule,
    opposing_expansion_or_time_stop_close,
    sentinel_target_price,
)
from ai_trader.multi_policy_live.vendor_bridge import LevelKind
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.types import LiveTick, PendingPdhPdlTrade
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
BAR_SECONDS = 900
TICK_SIZE = 0.01
DAY0_START = 1_705_269_600
DAY1_START = 1_705_356_000


class _FakeTickReader:
    def __init__(self, tick: LiveTick | None) -> None:
        self._tick = tick

    def read(self, symbol: str) -> LiveTick | None:
        return self._tick


def _bar(ts_open: int, o: float, h: float, l: float, c: float) -> Bar:
    return Bar(symbol=SYMBOL, ts_open=ts_open, ts_close=ts_open + BAR_SECONDS, open=o, high=h, low=l, close=c, volume=100.0)


def _breakout_bars() -> list[Bar]:
    bars = []
    for i in range(16):
        ts = DAY0_START + i * BAR_SECONDS
        if i == 14:
            bars.append(_bar(ts, 100.0, 110.0, 99.5, 100.0))  # PDH=110
        elif i == 15:
            bars.append(_bar(ts, 100.0, 100.5, 90.0, 100.0))  # PDL=90
        else:
            bars.append(_bar(ts, 100.0, 100.5, 99.5, 100.0))
    bars.append(_bar(DAY1_START, 100.0, 100.5, 99.5, 100.0))               # idx16: day1 anchor
    bars.append(_bar(DAY1_START + BAR_SECONDS, 108.0, 115.0, 107.5, 114.5))  # idx17: PDH break + displacement
    return bars


def test_pdh_break_with_bullish_displacement_produces_a_long_candidate() -> None:
    bars = _breakout_bars()
    tick = LiveTick(bid=114.3, ask=114.5, as_of=bars[-1].ts_close)
    journal = PdhPdlAuditJournal()
    rule = LevelBreakDriveRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(tick), journal)

    results = [rule.evaluate(b) for b in bars]

    assert all(r is None for r in results[:-1])
    candidate = results[-1]
    assert candidate is not None
    assert isinstance(candidate, LiveCandidate)
    assert candidate.strategy_id == STRATEGY_ID
    assert candidate.magic_number == MAGIC_NUMBER
    assert candidate.direction is Direction.LONG
    assert candidate.entry == tick.ask
    assert candidate.stop < candidate.entry

    trigger = rule.last_trigger()
    assert trigger is not None
    assert trigger.direction == 1
    assert trigger.strategy_stop_price == 110.0  # the broken level itself, not the touch-bar extreme
    assert rule.last_touch_level_kind() is LevelKind.PDH


def test_pdh_touch_without_displacement_is_no_trade() -> None:
    """A plain PDH touch (no expansion bar) is CAND-0001's own reversal case -- excluded here."""
    bars = []
    for i in range(16):
        ts = DAY0_START + i * BAR_SECONDS
        if i == 14:
            bars.append(_bar(ts, 100.0, 110.0, 99.5, 100.0))
        elif i == 15:
            bars.append(_bar(ts, 100.0, 100.5, 90.0, 100.0))
        else:
            bars.append(_bar(ts, 100.0, 100.5, 99.5, 100.0))
    bars.append(_bar(DAY1_START, 100.0, 100.5, 99.5, 100.0))
    bars.append(_bar(DAY1_START + BAR_SECONDS, 108.0, 111.0, 107.5, 108.5))  # touches PDH, ordinary range

    journal = PdhPdlAuditJournal()
    rule = LevelBreakDriveRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(None), journal)
    results = [rule.evaluate(b) for b in bars]

    assert results[-1] is None
    reasons = [e.detail.get("reason_code") for e in journal.entries]
    assert "NO_COINCIDENT_DISPLACEMENT" in reasons


def test_pdh_touch_with_bearish_displacement_is_rejection_not_break_no_trade() -> None:
    """PDH touched with a BEARISH displacement = CAND-0001's rejection thesis -- excluded here."""
    bars = []
    for i in range(16):
        ts = DAY0_START + i * BAR_SECONDS
        if i == 14:
            bars.append(_bar(ts, 100.0, 110.0, 99.5, 100.0))
        elif i == 15:
            bars.append(_bar(ts, 100.0, 100.5, 90.0, 100.0))
        else:
            bars.append(_bar(ts, 100.0, 100.5, 99.5, 100.0))
    bars.append(_bar(DAY1_START, 100.0, 100.5, 99.5, 100.0))
    bars.append(_bar(DAY1_START + BAR_SECONDS, 111.0, 111.5, 104.0, 104.5))  # touches PDH, bearish displacement

    journal = PdhPdlAuditJournal()
    rule = LevelBreakDriveRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(None), journal)
    results = [rule.evaluate(b) for b in bars]

    assert results[-1] is None
    reasons = [e.detail.get("reason_code") for e in journal.entries]
    assert "DISPLACEMENT_DIRECTION_NOT_THROUGH_LEVEL" in reasons


def _pending_long(entry_idx: int) -> PendingPdhPdlTrade:
    return PendingPdhPdlTrade(
        symbol=SYMBOL, direction=1, touch_idx=entry_idx - 1, entry_idx=entry_idx, strategy_stop_price=110.0,
        target_price=110.0, atr_at_touch=2.0, day_end_idx=None, day_boundary_label=DAY1_START,
        effective_spread=0.2, executable_stop_price=109.0, client_order_id="CID-1", broker_order_id=None,
        entry_as_of=DAY1_START, entry_requested_price=114.5, entry_realized_price=114.5,
    )


def test_mechanical_close_time_stop_at_atr_window_bars() -> None:
    pending = _pending_long(entry_idx=5)
    arrays = ([100.0] * 25, [101.0] * 25, [99.0] * 25, [100.0] * 25)
    assert opposing_expansion_or_time_stop_close(pending, bar_idx=18, day_boundary_label=DAY1_START, arrays=arrays) is None
    assert opposing_expansion_or_time_stop_close(pending, bar_idx=19, day_boundary_label=DAY1_START, arrays=arrays) == "TIME_STOP"


def test_mechanical_close_on_opposing_expansion_bar() -> None:
    pending = _pending_long(entry_idx=17)
    open_ = [100.0] * 25
    high = [100.5] * 25
    low = [99.5] * 25
    close = [100.0] * 25
    # bar 18: a strong BEARISH expansion bar (opposing a LONG position) -- needs real ATR14 history first
    for i in range(25):
        open_[i], high[i], low[i], close[i] = 100.0, 100.5, 99.5, 100.0
    high[18], low[18], open_[18], close[18] = 108.0, 92.0, 107.0, 93.0  # huge bearish range
    arrays = (open_, high, low, close)
    assert opposing_expansion_or_time_stop_close(pending, bar_idx=18, day_boundary_label=DAY1_START, arrays=arrays) == "OPPOSING_EXPANSION"


def test_mechanical_close_returns_none_before_entry_idx() -> None:
    pending = _pending_long(entry_idx=17)
    arrays = ([100.0] * 10, [100.5] * 10, [99.5] * 10, [100.0] * 10)
    assert opposing_expansion_or_time_stop_close(pending, bar_idx=5, day_boundary_label=DAY1_START, arrays=arrays) is None


def test_sentinel_target_price_is_unreachable_and_in_direction() -> None:
    pending = _pending_long(entry_idx=5)
    high = [100.0] * 10
    low = [95.0] * 10
    arrays = ([0.0] * 10, high, low, [0.0] * 10)
    target = sentinel_target_price(pending, arrays)
    assert target > max(high)  # LONG -> sentinel must sit ABOVE the observed range, unreachable

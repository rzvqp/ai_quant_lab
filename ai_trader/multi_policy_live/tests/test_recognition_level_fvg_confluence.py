"""`LevelFvgConfluenceRecognitionRule` (CAND-0007) tests. Bar sequence independently verified by running
the real vendored detectors directly before transcribing here (not guessed): a bullish FVG
(formed_idx=18, lower=95.5, upper=100.0, ce_50=97.75) whose first CE-50 touch lands on the EXACT same
bar (idx=20) as a fresh PDL=90.0 touch -- direction-aligned (PDL + bullish FVG -> long)."""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar, LiveCandidate
from ai_trader.multi_policy_live.recognition_level_fvg_confluence import (
    MAGIC_NUMBER,
    STRATEGY_ID,
    LevelFvgConfluenceRecognitionRule,
)
from ai_trader.multi_policy_live.vendor_bridge import LevelKind
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.types import LiveTick
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


def _confluence_bars() -> list[Bar]:
    bars = []
    for i in range(16):
        ts = DAY0_START + i * BAR_SECONDS
        if i == 14:
            bars.append(_bar(ts, 100.0, 110.0, 99.5, 100.0))  # sets PDH=110
        elif i == 15:
            bars.append(_bar(ts, 100.0, 100.5, 90.0, 100.0))  # sets PDL=90
        else:
            bars.append(_bar(ts, 100.0, 100.5, 99.5, 100.0))
    bars.append(_bar(DAY1_START, 100.0, 100.5, 99.5, 100.0))                  # idx16: day1 anchor
    bars.append(_bar(DAY1_START + BAR_SECONDS, 100.0, 95.5, 95.0, 95.2))      # idx17: FVG i-1
    bars.append(_bar(DAY1_START + 2 * BAR_SECONDS, 96.0, 97.0, 95.5, 96.5))   # idx18: FVG i (formed_idx)
    bars.append(_bar(DAY1_START + 3 * BAR_SECONDS, 100.5, 101.0, 100.0, 100.8))  # idx19: FVG i+1 (confirms)
    bars.append(_bar(DAY1_START + 4 * BAR_SECONDS, 95.0, 96.0, 89.0, 94.0))   # idx20: PDL touch + CE-50 touch
    return bars


def test_direction_aligned_confluence_produces_a_long_candidate() -> None:
    bars = _confluence_bars()
    tick = LiveTick(bid=93.9, ask=94.1, as_of=bars[-1].ts_close)
    journal = PdhPdlAuditJournal()
    rule = LevelFvgConfluenceRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(tick), journal)

    results = [rule.evaluate(b) for b in bars]

    assert all(r is None for r in results[:-1])
    candidate = results[-1]
    assert candidate is not None
    assert isinstance(candidate, LiveCandidate)
    assert candidate.strategy_id == STRATEGY_ID
    assert candidate.magic_number == MAGIC_NUMBER
    assert candidate.direction is Direction.LONG
    assert candidate.entry == tick.ask
    assert candidate.target == 110.0  # opposite level (PDH)
    assert candidate.stop < candidate.entry  # LONG invariant

    trigger = rule.last_trigger()
    assert trigger is not None
    assert trigger.direction == 1
    assert trigger.strategy_stop_price == 89.0  # min(low[touch_idx]=89.0, fvg.lower=95.5)
    assert trigger.target_price == 110.0
    assert rule.last_touch_level_kind() is LevelKind.PDL


def test_no_confluence_when_only_the_level_touches() -> None:
    """Same PDL touch bar, but WITHOUT the FVG ever forming (no idx17-19 displacement) -- must NOT fire."""
    bars = []
    for i in range(16):
        ts = DAY0_START + i * BAR_SECONDS
        if i == 14:
            bars.append(_bar(ts, 100.0, 110.0, 99.5, 100.0))
        elif i == 15:
            bars.append(_bar(ts, 100.0, 100.5, 90.0, 100.0))
        else:
            bars.append(_bar(ts, 100.0, 100.5, 99.5, 100.0))
    bars.append(_bar(DAY1_START, 100.0, 100.5, 89.0, 94.0))  # touches PDL, no FVG anywhere nearby

    journal = PdhPdlAuditJournal()
    rule = LevelFvgConfluenceRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(None), journal)
    results = [rule.evaluate(b) for b in bars]

    # No FVG exists at all -- silent return, same convention PdhPdlRecognitionRule uses for a bar with
    # no touch at all (journaling would spam an entry on every ordinary bar).
    assert results[-1] is None
    assert journal.entries == ()


def test_no_live_tick_is_no_trade_and_journaled() -> None:
    bars = _confluence_bars()
    journal = PdhPdlAuditJournal()
    rule = LevelFvgConfluenceRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(None), journal)

    results = [rule.evaluate(b) for b in bars]

    assert results[-1] is None
    reasons = [e.detail.get("reason_code") for e in journal.entries]
    assert "LIVE_TICK_UNAVAILABLE" in reasons


def test_current_bar_count_and_arrays_track_bars() -> None:
    bars = _confluence_bars()
    journal = PdhPdlAuditJournal()
    rule = LevelFvgConfluenceRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(None), journal)
    for b in bars:
        rule.evaluate(b)
    assert rule.current_bar_count == len(bars)
    open_, high, low, close = rule.current_arrays
    assert len(close) == len(bars)
    assert close[-1] == bars[-1].close

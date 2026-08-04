"""`DzLevelConfluenceRecognitionRule` (CAND-0019) tests. Bar sequence independently verified by running
the real vendored detectors directly before transcribing here: a bullish demand zone
(formation_idx=17, `[96.5, 100.2]`) whose confluence bar (idx=19) ALSO carries a fresh PDL=96.0 touch --
direction-aligned (PDL + bullish zone -> long)."""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar, LiveCandidate
from ai_trader.multi_policy_live.recognition_dz_level_confluence import (
    MAGIC_NUMBER,
    STRATEGY_ID,
    DzLevelConfluenceRecognitionRule,
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
            bars.append(_bar(ts, 100.0, 110.0, 99.5, 100.0))  # PDH=110
        elif i == 15:
            bars.append(_bar(ts, 100.0, 100.5, 96.0, 100.0))  # PDL=96.0
        else:
            bars.append(_bar(ts, 100.0, 100.5, 99.5, 100.0))
    bars.append(_bar(DAY1_START, 100.0, 100.5, 99.5, 100.0))                    # idx16: day1 anchor
    bars.append(_bar(DAY1_START + BAR_SECONDS, 100.0, 100.2, 96.5, 97.0))       # idx17: zone anchor (bearish)
    bars.append(_bar(DAY1_START + 2 * BAR_SECONDS, 96.6, 108.0, 96.2, 107.5))   # idx18: impulse (bullish, engulfs 17)
    bars.append(_bar(DAY1_START + 3 * BAR_SECONDS, 97.0, 97.5, 95.5, 96.0))     # idx19: PDL touch + zone overlap
    return bars


def test_direction_aligned_confluence_produces_a_long_candidate() -> None:
    bars = _confluence_bars()
    tick = LiveTick(bid=95.9, ask=96.1, as_of=bars[-1].ts_close)
    journal = PdhPdlAuditJournal()
    rule = DzLevelConfluenceRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(tick), journal)

    results = [rule.evaluate(b) for b in bars]

    assert all(r is None for r in results[:-1])
    candidate = results[-1]
    assert candidate is not None
    assert isinstance(candidate, LiveCandidate)
    assert candidate.strategy_id == STRATEGY_ID
    assert candidate.magic_number == MAGIC_NUMBER
    assert candidate.direction is Direction.LONG
    assert candidate.entry == tick.ask
    assert candidate.target == 110.0
    assert candidate.stop < candidate.entry

    trigger = rule.last_trigger()
    assert trigger is not None
    assert trigger.direction == 1
    assert trigger.strategy_stop_price == 95.5  # min(zone.zone_lower=96.5, low[touch_idx]=95.5)
    assert trigger.target_price == 110.0
    assert rule.last_touch_level_kind() is LevelKind.PDL


def test_no_confluence_when_only_the_level_touches() -> None:
    bars = []
    for i in range(16):
        ts = DAY0_START + i * BAR_SECONDS
        if i == 14:
            bars.append(_bar(ts, 100.0, 110.0, 99.5, 100.0))
        elif i == 15:
            bars.append(_bar(ts, 100.0, 100.5, 96.0, 100.0))
        else:
            bars.append(_bar(ts, 100.0, 100.5, 99.5, 100.0))
    bars.append(_bar(DAY1_START, 100.0, 100.5, 95.5, 96.0))  # touches PDL, no demand zone nearby

    journal = PdhPdlAuditJournal()
    rule = DzLevelConfluenceRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(None), journal)
    results = [rule.evaluate(b) for b in bars]

    assert results[-1] is None
    assert journal.entries == ()


def test_no_live_tick_is_no_trade_and_journaled() -> None:
    bars = _confluence_bars()
    journal = PdhPdlAuditJournal()
    rule = DzLevelConfluenceRecognitionRule(SYMBOL, TICK_SIZE, _FakeTickReader(None), journal)

    results = [rule.evaluate(b) for b in bars]

    assert results[-1] is None
    reasons = [e.detail.get("reason_code") for e in journal.entries]
    assert "LIVE_TICK_UNAVAILABLE" in reasons

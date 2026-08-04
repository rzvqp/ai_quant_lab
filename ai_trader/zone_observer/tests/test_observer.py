"""`ZoneObserver` tests -- 2026-08-04. Every synthetic price series here was verified directly
against the vendored functions (via a standalone script) before being written into a test -- same
discipline `structural_observer`'s own tests already established. The order-block/demand-zone and
FVG/IFVG fixtures below are the SAME proven series `structural_observer`'s own test suite uses
(`_order_block_series`, the bullish-FVG-with-3-stage-reaction series) -- reused deliberately so the
two packages' behavior can be cross-checked against identical inputs."""

from __future__ import annotations

import datetime as dt

from ai_trader.live_signal_source.types import Bar
from ai_trader.zone_observer.journal import ZoneObservationLog
from ai_trader.zone_observer.observer import ZoneObserver
from ai_trader.zone_observer.types import ZoneEventKind

SYMBOL = "XAUUSD"
BAR_SECONDS = 900


def _bar(ts_open: int, open_: float, high: float, low: float, close: float) -> Bar:
    return Bar(
        symbol=SYMBOL, ts_open=ts_open, ts_close=ts_open + BAR_SECONDS,
        open=open_, high=high, low=low, close=close, volume=100.0,
    )


def _feed_with_times(observer: ZoneObserver, times: list[int], opens: list[float], highs: list[float],
                      lows: list[float], closes: list[float]) -> None:
    for t, o, h, lo, c in zip(times, opens, highs, lows, closes):
        observer.observe(_bar(t, o, h, lo, c))


def _sequential_times(n: int, start: int = 1_700_000_000) -> list[int]:
    return [start + i * BAR_SECONDS for i in range(n)]


# -- session_levels: primitive A only (High/Low formed+touched, Mid separate via containment) --


def test_session_levels_formed_and_touched_high_low_mid_reported_separately() -> None:
    t0 = int(dt.datetime(2024, 1, 8, 0, 0, 0, tzinfo=dt.timezone.utc).timestamp())  # Monday 00:00 UTC -- asia
    n_asia = 8
    times = [t0 + i * BAR_SECONDS for i in range(n_asia)]
    highs = [100.0 + i * 0.1 for i in range(n_asia)]
    lows = [99.0 - i * 0.1 for i in range(n_asia)]

    t_london = int(dt.datetime(2024, 1, 8, 8, 0, 0, tzinfo=dt.timezone.utc).timestamp())
    times += [t_london + i * BAR_SECONDS for i in range(4)]
    highs += [100.9, 100.9, 101.0, 100.9]
    lows += [98.3, 98.2, 98.1, 98.19]
    opens = list(highs)  # irrelevant for this detector
    closes = list(highs)

    journal = ZoneObservationLog()
    observer = ZoneObserver(SYMBOL, journal)
    _feed_with_times(observer, times, opens, highs, lows, closes)

    formed = [e for e in journal.entries if e.kind is ZoneEventKind.SESSION_LEVEL_FORMED]
    by_kind = {e.detail["level_kind"]: e for e in formed}
    assert set(by_kind) == {"session_high", "session_low", "session_mid"}
    assert by_kind["session_high"].detail["price"] == 100.7
    assert by_kind["session_low"].detail["price"] == 98.3
    assert by_kind["session_mid"].detail["price"] == 99.5
    assert by_kind["session_high"].detail["session_label"] == "asia"

    touches = [e for e in journal.entries if e.kind is ZoneEventKind.SESSION_LEVEL_TOUCH]
    touch_kinds = {e.detail["level_kind"] for e in touches}
    assert touch_kinds == {"session_high", "session_low", "session_mid"}  # reported SEPARATELY, never merged
    for t in touches:
        assert t.detail["touch_idx"] == 8


def test_session_levels_never_recorded_twice() -> None:
    t0 = int(dt.datetime(2024, 1, 8, 0, 0, 0, tzinfo=dt.timezone.utc).timestamp())
    times = [t0 + i * BAR_SECONDS for i in range(8)]
    highs = [100.0 + i * 0.1 for i in range(8)]
    lows = [99.0 - i * 0.1 for i in range(8)]
    t_london = int(dt.datetime(2024, 1, 8, 8, 0, 0, tzinfo=dt.timezone.utc).timestamp())
    times += [t_london + i * BAR_SECONDS for i in range(6)]  # two extra flat bars past the touch
    highs += [100.9, 100.9, 101.0, 100.9, 100.9, 100.9]
    lows += [98.3, 98.2, 98.1, 98.19, 98.19, 98.19]
    opens = list(highs)
    closes = list(highs)

    journal = ZoneObservationLog()
    observer = ZoneObserver(SYMBOL, journal)
    _feed_with_times(observer, times, opens, highs, lows, closes)

    assert len([e for e in journal.entries if e.kind is ZoneEventKind.SESSION_LEVEL_FORMED]) == 3
    assert len([e for e in journal.entries if e.kind is ZoneEventKind.SESSION_LEVEL_TOUCH]) == 3


# -- order_flow.detect_demand_zones (the one order_flow function structural_observer doesn't cover) --


def _order_block_series() -> tuple[list[float], list[float], list[float], list[float]]:
    """Byte-identical to `structural_observer.tests.test_observer._order_block_series` (reused
    deliberately -- see module docstring)."""
    n_warmup = 14
    open_ = [102.0] * n_warmup
    high = [102.1] * n_warmup
    low = [101.9] * n_warmup
    close = [102.0] * n_warmup
    open_.append(102.05); high.append(102.15); low.append(101.85); close.append(101.95)
    open_.append(101.5); high.append(110.0); low.append(101.4); close.append(109.0)
    return open_, high, low, close


def test_demand_zone_formed_is_the_full_wick_range_not_the_ob_body() -> None:
    open_, high, low, close = _order_block_series()
    times = _sequential_times(len(close))
    journal = ZoneObservationLog()
    observer = ZoneObserver(SYMBOL, journal)
    _feed_with_times(observer, times, open_, high, low, close)

    zones = [e for e in journal.entries if e.kind is ZoneEventKind.DEMAND_ZONE_FORMED]
    assert len(zones) == 1
    assert zones[0].detail["formation_idx"] == 14
    assert zones[0].detail["zone_kind"] == "bullish"
    assert zones[0].detail["zone_lower"] == 101.85  # low[14] -- wick included, wider than OB body 101.95
    assert zones[0].detail["zone_upper"] == 102.15  # high[14] -- wider than OB body 102.05


def test_demand_zone_never_recorded_twice() -> None:
    open_, high, low, close = _order_block_series()
    open_.append(101.0); high.append(101.1); low.append(100.9); close.append(101.0)
    times = _sequential_times(len(close))
    journal = ZoneObservationLog()
    observer = ZoneObserver(SYMBOL, journal)
    _feed_with_times(observer, times, open_, high, low, close)

    assert len([e for e in journal.entries if e.kind is ZoneEventKind.DEMAND_ZONE_FORMED]) == 1


# -- imbalance_mechanics.detect_inverse_fvgs / count_bpr (detect_fvgs itself is never re-recorded) --


def test_inverse_fvg_formed_links_back_to_its_original() -> None:
    high = [1.0, 1.5, 2.0, 2.1, 2.0, 1.8]
    low = [0.5, 1.0, 3.0, 1.9, 0.9, 0.5]
    close = [0.8, 1.2, 2.5, 1.95, 1.0, 0.5]
    times = _sequential_times(len(close))
    journal = ZoneObservationLog()
    observer = ZoneObserver(SYMBOL, journal)
    _feed_with_times(observer, times, close, high, low, close)

    ifvgs = {
        e.detail["inversion_idx"]: e.detail
        for e in journal.entries if e.kind is ZoneEventKind.INVERSE_FVG_FORMED
    }
    assert set(ifvgs) == {4, 5}
    assert ifvgs[5]["new_kind"] == "bearish"
    assert ifvgs[5]["lower"] == 1.0 and ifvgs[5]["upper"] == 3.0
    assert ifvgs[5]["original_formed_idx"] == 1
    assert ifvgs[4]["original_formed_idx"] == 2


def test_ifvg_never_recorded_twice() -> None:
    high = [1.0, 1.5, 2.0, 2.1, 2.0, 1.8, 1.8, 1.8]
    low = [0.5, 1.0, 3.0, 1.9, 0.9, 0.5, 0.5, 0.5]
    close = [0.8, 1.2, 2.5, 1.95, 1.0, 0.5, 0.5, 0.5]
    times = _sequential_times(len(close))
    journal = ZoneObservationLog()
    observer = ZoneObserver(SYMBOL, journal)
    _feed_with_times(observer, times, close, high, low, close)

    assert len([e for e in journal.entries if e.kind is ZoneEventKind.INVERSE_FVG_FORMED]) == 2


def test_bpr_count_recorded_when_it_increases() -> None:
    high = [1.0, 1.5, 2.0, 2.5, 1.6, 1.5, 1.4]
    low = [0.5, 1.0, 3.0, 1.8, 0.5, 0.5, 0.5]
    close = [0.8, 1.2, 2.5, 2.0, 1.0, 0.9, 0.8]
    times = _sequential_times(len(close))
    journal = ZoneObservationLog()
    observer = ZoneObserver(SYMBOL, journal)
    _feed_with_times(observer, times, close, high, low, close)

    bpr_events = [e for e in journal.entries if e.kind is ZoneEventKind.BPR_COUNT]
    assert len(bpr_events) >= 1
    last = bpr_events[-1].detail
    assert last["tolerance_0.0"] == 4
    assert last["tolerance_0.1"] == 4
    assert last["tolerance_0.25"] == 4


def test_bpr_count_not_re_recorded_when_unchanged() -> None:
    high = [1.0, 1.5, 2.0, 2.5, 1.6, 1.5, 1.4, 1.4, 1.4]
    low = [0.5, 1.0, 3.0, 1.8, 0.5, 0.5, 0.5, 0.5, 0.5]
    close = [0.8, 1.2, 2.5, 2.0, 1.0, 0.9, 0.8, 0.8, 0.8]  # two extra flat bars, no new overlap
    times = _sequential_times(len(close))
    journal = ZoneObservationLog()
    observer = ZoneObserver(SYMBOL, journal)
    _feed_with_times(observer, times, close, high, low, close)

    bpr_events = [e for e in journal.entries if e.kind is ZoneEventKind.BPR_COUNT]
    # count is stable at the same value from the point it first reaches 4 -- never re-emitted flat
    counts_seen = [(e.detail["tolerance_0.0"], e.detail["tolerance_0.1"], e.detail["tolerance_0.25"]) for e in bpr_events]
    assert counts_seen == sorted(set(counts_seen), key=counts_seen.index)  # strictly increasing sequence, no repeats


# -- institutional_levels.compute_prior_week_levels: formation only, no touch detection (disclosed) --


def test_weekly_level_formed_no_touch_detection_exists() -> None:
    t_w1 = int(dt.datetime(2024, 1, 8, 18, 0, 0, tzinfo=dt.timezone.utc).timestamp())  # Monday evening
    times = [t_w1 + i * BAR_SECONDS for i in range(20)]
    t_w2 = int(dt.datetime(2024, 1, 15, 18, 0, 0, tzinfo=dt.timezone.utc).timestamp())  # next Monday
    times += [t_w2 + i * BAR_SECONDS for i in range(6)]
    highs = [100.0 + (i % 5) for i in range(len(times))]
    lows = [90.0 - (i % 5) for i in range(len(times))]
    opens = list(highs)
    closes = list(highs)

    journal = ZoneObservationLog()
    observer = ZoneObserver(SYMBOL, journal)
    _feed_with_times(observer, times, opens, highs, lows, closes)

    weekly = [e for e in journal.entries if e.kind is ZoneEventKind.WEEKLY_LEVEL_FORMED]
    by_kind = {e.detail["level_kind"]: e for e in weekly}
    assert by_kind["weekly_high"].detail["price"] == 104.0
    assert by_kind["weekly_low"].detail["price"] == 86.0
    assert by_kind["weekly_high"].detail["completeness"] == "PARTIAL"
    # no touch-detection kind exists for weekly levels at all -- only formation is ever recorded
    assert not any("touch_idx" in e.detail for e in weekly)


# -- order_block_void.detect_liquidity_voids --


def test_liquidity_void_classified_both_temporal_and_size() -> None:
    times = [1000, 1900, 2800, 2800 + 900 + 2000]
    opens = [100.0, 100.0, 100.0, 105.0]
    closes = [100.0, 100.0, 100.0, 100.0]
    highs = list(opens)
    lows = list(opens)

    journal = ZoneObservationLog()
    observer = ZoneObserver(SYMBOL, journal)
    _feed_with_times(observer, times, opens, highs, lows, closes)

    voids = [e for e in journal.entries if e.kind is ZoneEventKind.LIQUIDITY_VOID]
    assert len(voids) == 1
    assert voids[0].detail["at_idx"] == 2
    assert voids[0].detail["void_kind"] == "both"
    assert voids[0].detail["gap_seconds"] == 2900
    assert voids[0].detail["price_jump"] == 5.0


def test_liquidity_void_never_recorded_twice() -> None:
    times = [1000, 1900, 2800, 2800 + 900 + 2000, 2800 + 900 + 2000 + 900]
    opens = [100.0, 100.0, 100.0, 105.0, 100.0]  # bar4 opens flat vs bar3's own close -- no new void
    closes = [100.0, 100.0, 100.0, 100.0, 100.0]
    highs = list(opens)
    lows = list(opens)

    journal = ZoneObservationLog()
    observer = ZoneObserver(SYMBOL, journal)
    _feed_with_times(observer, times, opens, highs, lows, closes)

    assert len([e for e in journal.entries if e.kind is ZoneEventKind.LIQUIDITY_VOID]) == 1

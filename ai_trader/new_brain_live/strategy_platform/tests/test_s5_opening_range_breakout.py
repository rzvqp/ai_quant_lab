"""S5 Opening-Range Breakout LONG -- mandate `AI-TRADER-S5-CANONICAL-ONBOARDING-001` sections 13-18.

Historical-fixture reproduction (section 13): synthetic-but-mechanically-faithful bar sequences that
exercise the EXACT formulas recovered from `code/mstrat.py` (see `s5_opening_range_breakout.py`'s own
docstring for the full citation trail) -- never the real, escrowed 295-trade ledger (inaccessible, off-
git, hash-only; using it would violate section 13's own "do not consume new protected evidence"). This
is legitimate: the STRATEGY LOGIC (entry/SL/TP/session/window formulas) is fully, mechanically recovered
and cited; only the specific historical OUTCOMES are unavailable, and this file never claims otherwise."""

from __future__ import annotations

import dataclasses

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_live.dual_clock.upstream_context import build_context
from ai_trader.new_brain_live.market_state import MarketState
from ai_trader.new_brain_live.strategy_platform.s5_opening_range_breakout import (
    CONFIG_FINGERPRINT,
    ENTRY_WINDOW_FIRST_BIS,
    ENTRY_WINDOW_LAST_BIS,
    MAX_HOLD_BARS,
    NY_SESSION_START_UTC_SECONDS,
    RR_TARGET,
    STRATEGY_ID,
    STRATEGY_VERSION,
    TICK,
    S5OpeningRangeBreakoutLong,
    catalog_entry_for_s5,
)
from ai_trader.new_brain_live.strategy_platform.strategy_protocol import StrategyEvaluationInput
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
_BAR_SECONDS = 900
_DAY_START = 100 * 86400  # an arbitrary, deterministic calendar day
_SESSION_START = _DAY_START + NY_SESSION_START_UTC_SECONDS


def _bar(*, ts_close: int, o: float, h: float, low_: float, c: float) -> Bar:
    return Bar(symbol=SYMBOL, ts_open=ts_close - _BAR_SECONDS, ts_close=ts_close, open=o, high=h, low=low_, close=c, volume=100.0)


def _warmup_bars(*, count: int, end_before: int, start_price: float = 2000.0) -> list[Bar]:
    """Calm bars ending strictly before `end_before`, giving RawAxesBuilder enough history for a real
    ATR-14 by the time the session bars begin."""
    bars: list[Bar] = []
    price = start_price
    ts = end_before - count * _BAR_SECONDS
    for _ in range(count):
        o, c = price, price + 0.05
        bars.append(_bar(ts_close=ts, o=o, h=o + 0.3, low_=o - 0.3, c=c))
        price = c
        ts += _BAR_SECONDS
    return bars


def _or_bars() -> list[Bar]:
    """bis 0-3 (ts_close = session_start + bis*900, so bis=0's own close lands exactly at session_start),
    or_high=2050.00 (set by bis1's high), or_low=2040.00 (set by bis2's low)."""
    return [
        _bar(ts_close=_SESSION_START + 0 * _BAR_SECONDS, o=2045.0, h=2048.0, low_=2043.0, c=2046.0),  # bis0
        _bar(ts_close=_SESSION_START + 1 * _BAR_SECONDS, o=2046.0, h=2050.0, low_=2044.0, c=2047.0),  # bis1 -> or_high
        _bar(ts_close=_SESSION_START + 2 * _BAR_SECONDS, o=2047.0, h=2049.0, low_=2040.0, c=2045.0),  # bis2 -> or_low
        _bar(ts_close=_SESSION_START + 3 * _BAR_SECONDS, o=2045.0, h=2047.0, low_=2042.0, c=2044.0),  # bis3
    ]


def _session_bar(bis: int, *, close: float) -> Bar:
    ts_close = _SESSION_START + bis * _BAR_SECONDS
    return _bar(ts_close=ts_close, o=close - 1.0, h=close + 0.5, low_=close - 1.5, c=close)


def _fixture(*, extra_bars: list[Bar]) -> tuple[S5OpeningRangeBreakoutLong, MarketState]:
    """Feeds warmup + OR bars + `extra_bars` (in order) into BOTH a real `RawAxesBuilder` (for a real
    N1-computed `MarketState`) and a fresh `S5OpeningRangeBreakoutLong` (for its own OR state) --
    lockstep, mirroring how a future live-wiring step would call both on the same bar. Returns the
    strategy and the MarketState built from the LAST bar."""
    strategy = S5OpeningRangeBreakoutLong()
    builder = RawAxesBuilder(SYMBOL)
    all_bars = _warmup_bars(count=20, end_before=_SESSION_START) + _or_bars() + extra_bars
    for bar in all_bars[:-1]:
        builder.observe(bar)
        strategy.observe_bar(bar)
    last_bar = all_bars[-1]
    builder.observe(last_bar)
    strategy.observe_bar(last_bar)
    market_state = build_context(symbol=SYMBOL, timeframe="M15", bar=last_bar, axes_builder=builder, catalog=())
    return strategy, market_state


def _evaluation_input(market_state: MarketState) -> StrategyEvaluationInput:
    return StrategyEvaluationInput(market_state=market_state, tower_context=None, config={})


def test_setup_recognized_breakout_produces_correct_hypothesis() -> None:
    breakout_bar = _session_bar(ENTRY_WINDOW_FIRST_BIS + 1, close=2052.0)  # bis=5, close > or_high(2050)
    strategy, market_state = _fixture(extra_bars=[breakout_bar])
    hypothesis = strategy.evaluate(_evaluation_input(market_state))

    assert hypothesis is not None
    assert hypothesis.strategy_id == STRATEGY_ID
    assert hypothesis.strategy_version == STRATEGY_VERSION
    assert hypothesis.direction is Direction.LONG
    assert hypothesis.intended_entry == 2052.0
    assert hypothesis.invalidation == 2040.0 - 2 * TICK  # or_low - 2*TICK
    assert abs(hypothesis.invalidation - 2039.98) < 1e-9
    assert hypothesis.exit_specification == f"rr:{RR_TARGET}"
    assert hypothesis.max_hold == MAX_HOLD_BARS
    assert hypothesis.strategy_config_fingerprint == CONFIG_FINGERPRINT
    assert hypothesis.expected_edge is None  # honestly disclosed -- see module docstring
    risk = hypothesis.intended_entry - hypothesis.invalidation
    implied_target = hypothesis.intended_entry + RR_TARGET * risk
    assert abs(implied_target - (2052.0 + 3.0 * (2052.0 - 2039.98))) < 1e-9


def test_no_breakout_close_below_or_high_produces_no_signal() -> None:
    non_breakout_bar = _session_bar(ENTRY_WINDOW_FIRST_BIS, close=2045.0)  # bis=4, below or_high(2050)
    strategy, market_state = _fixture(extra_bars=[non_breakout_bar])
    assert strategy.evaluate(_evaluation_input(market_state)) is None


def test_breakout_before_entry_window_produces_no_signal() -> None:
    """bis=2 is still inside the OR-forming window (0-3) -- even a close above what will become or_high
    must not fire (the OR itself isn't finalized yet, and mstrat.py's own loop never evaluates bis<4)."""
    strategy = S5OpeningRangeBreakoutLong()
    builder = RawAxesBuilder(SYMBOL)
    warmup = _warmup_bars(count=20, end_before=_SESSION_START)
    early_high_bar = _bar(ts_close=_SESSION_START + 2 * _BAR_SECONDS, o=2045.0, h=2060.0, low_=2043.0, c=2055.0)
    or_bars = [
        _bar(ts_close=_SESSION_START + 0 * _BAR_SECONDS, o=2045.0, h=2048.0, low_=2043.0, c=2046.0),
        _bar(ts_close=_SESSION_START + 1 * _BAR_SECONDS, o=2046.0, h=2050.0, low_=2044.0, c=2047.0),
        early_high_bar,  # bis=2, closes at 2055 -- would break the eventual or_high if it counted
    ]
    all_bars = warmup + or_bars
    for bar in all_bars[:-1]:
        builder.observe(bar)
        strategy.observe_bar(bar)
    builder.observe(all_bars[-1])
    strategy.observe_bar(all_bars[-1])
    market_state = build_context(symbol=SYMBOL, timeframe="M15", bar=all_bars[-1], axes_builder=builder, catalog=())
    assert strategy.evaluate(_evaluation_input(market_state)) is None  # OR not yet finalized (only 3 of 4 bars)


def test_breakout_after_entry_window_produces_no_signal() -> None:
    late_bar = _session_bar(ENTRY_WINDOW_LAST_BIS + 1, close=2060.0)  # bis=21, well above or_high
    strategy, market_state = _fixture(extra_bars=[late_bar])
    assert strategy.evaluate(_evaluation_input(market_state)) is None


def test_breakout_at_last_valid_entry_bis_still_fires() -> None:
    boundary_bar = _session_bar(ENTRY_WINDOW_LAST_BIS, close=2051.0)  # bis=20, inclusive per mstrat.py
    strategy, market_state = _fixture(extra_bars=[boundary_bar])
    hypothesis = strategy.evaluate(_evaluation_input(market_state))
    assert hypothesis is not None


def test_wrong_session_hour_never_fires_even_with_a_qualifying_close() -> None:
    """A bar at UTC hour 8 (Asia/London, not NY) with a close that would otherwise break out must never
    produce a signal -- the strategy has no opening range for a non-NY session at all."""
    strategy = S5OpeningRangeBreakoutLong()
    builder = RawAxesBuilder(SYMBOL)
    non_ny_day_start = _DAY_START + 8 * 3600
    warmup = _warmup_bars(count=20, end_before=non_ny_day_start)
    wrong_session_bar = _bar(ts_close=non_ny_day_start + _BAR_SECONDS, o=2045.0, h=3000.0, low_=2043.0, c=2999.0)
    all_bars = warmup + [wrong_session_bar]
    for bar in all_bars[:-1]:
        builder.observe(bar)
        strategy.observe_bar(bar)
    builder.observe(all_bars[-1])
    strategy.observe_bar(all_bars[-1])
    market_state = build_context(symbol=SYMBOL, timeframe="M15", bar=all_bars[-1], axes_builder=builder, catalog=())
    assert strategy.evaluate(_evaluation_input(market_state)) is None


def test_invalid_market_state_entry_price_none_produces_no_signal() -> None:
    strategy, market_state = _fixture(extra_bars=[_session_bar(ENTRY_WINDOW_FIRST_BIS + 1, close=2052.0)])
    invalid = dataclasses.replace(market_state, entry_price=None)
    assert strategy.evaluate(_evaluation_input(invalid)) is None


def test_catalog_entry_is_validated_with_real_provenance() -> None:
    strategy = S5OpeningRangeBreakoutLong()
    entry = catalog_entry_for_s5(strategy)
    assert entry.strategy_id == STRATEGY_ID
    assert entry.strategy_version == STRATEGY_VERSION
    assert entry.allowed_directions == ("LONG",)
    assert entry.context_eligibility is None
    assert entry.validation_provenance is not None
    assert "C_2d587447" in entry.validation_provenance
    assert "633bd5da" in entry.validation_provenance
    assert "cd4e8d4a" in entry.validation_provenance


def test_determinism_same_bars_same_hypothesis() -> None:
    breakout_bar = _session_bar(ENTRY_WINDOW_FIRST_BIS + 2, close=2053.0)
    strategy_a, state_a = _fixture(extra_bars=[breakout_bar])
    strategy_b, state_b = _fixture(extra_bars=[breakout_bar])
    h_a = strategy_a.evaluate(_evaluation_input(state_a))
    h_b = strategy_b.evaluate(_evaluation_input(state_b))
    assert h_a == h_b

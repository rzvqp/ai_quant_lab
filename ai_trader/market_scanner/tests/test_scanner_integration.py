"""Integration tests for the full Market Scanner pipeline: multi-symbol, multi-timeframe replay,
determinism, lookahead-safety, gap handling, and schema validity end-to-end.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from ai_trader.market_scanner import AdapterConfig, Mode, Requirements, SymbolMeta
from ai_trader.market_scanner.config import ScannerConfig
from ai_trader.market_scanner.scanner import MarketScanner
from ai_trader.market_scanner.schema_validation import validate_context
from ai_trader.market_scanner.types import RawBar

_M15 = 900
_H1 = 3600
_H4 = 14400
_D1 = 86400
_DAY_BARS_M15 = 96  # 24h / 15min, no weekend skip (keeps the synthetic generator simple)


@dataclass
class _Tick:
    o: float
    h: float
    l: float
    c: float


def _random_walk_m15(n: int, seed: int, start_price: float = 2000.0) -> list[_Tick]:
    rng = random.Random(seed)
    ticks: list[_Tick] = []
    price = start_price
    for _ in range(n):
        o = price
        drift = rng.uniform(-1.5, 1.5)
        c = max(1.0, o + drift)
        h = max(o, c) + rng.uniform(0.05, 1.0)
        l = min(o, c) - rng.uniform(0.05, 1.0)
        ticks.append(_Tick(o, h, l, c))
        price = c
    return ticks


def _aggregate(symbol: str, timeframe: str, group_size: int, m15_ticks: list[_Tick], base_ts: int) -> list[RawBar]:
    """Aggregate consecutive M15 ticks into bars of a coarser timeframe (real OHLC rollup)."""
    secs = {"H1": _H1, "H4": _H4, "D1": _D1}[timeframe]
    bars: list[RawBar] = []
    for i in range(0, len(m15_ticks) - group_size + 1, group_size):
        group = m15_ticks[i : i + group_size]
        ts_open = base_ts + i * _M15
        bars.append(
            RawBar(
                symbol=symbol, timeframe=timeframe, ts_open=ts_open, ts_close=ts_open + secs,
                open=group[0].o, high=max(t.h for t in group), low=min(t.l for t in group),
                close=group[-1].c, volume=float(len(group) * 10), complete=True,
            )
        )
    return bars


def _m15_bars(symbol: str, ticks: list[_Tick], base_ts: int) -> list[RawBar]:
    return [
        RawBar(symbol=symbol, timeframe="M15", ts_open=base_ts + i * _M15, ts_close=base_ts + (i + 1) * _M15,
               open=t.o, high=t.h, low=t.l, close=t.c, volume=10.0, complete=True)
        for i, t in enumerate(ticks)
    ]


def _run_replay(symbols: list[str], n_m15_bars: int, seed: int, base_ts: int = 0) -> dict[str, list[dict]]:
    scanner = MarketScanner(ScannerConfig(history_buffer_bars=100))
    metas = [SymbolMeta(symbol=s, tick_size=0.1, point_value=1.0, price_precision=2) for s in symbols]
    scanner.configure(metas, AdapterConfig(mode=Mode.REPLAY, source_id="integration-test"))
    req = Requirements(
        timeframes=frozenset({"M15", "H1", "H4", "D1"}),
        fields_by_timeframe={"M15": frozenset({"m_atr", "m_rsi", "pdh", "pdl", "h1_trend_up", "rmax20"})},
        lookback_by_timeframe={"M15": 50, "H1": 30, "H4": 20, "D1": 10},
        symbols=frozenset(symbols),
    )
    scanner.register_requirements(req)

    all_events: list[tuple[int, int, RawBar]] = []  # (ts_close, tf_priority, bar) ; lower priority ingested first
    contexts_by_symbol: dict[str, list[dict]] = {s: [] for s in symbols}
    per_symbol_ticks: dict[str, list[_Tick]] = {}

    for idx, symbol in enumerate(symbols):
        ticks = _random_walk_m15(n_m15_bars, seed=seed + idx)
        per_symbol_ticks[symbol] = ticks
        for b in _m15_bars(symbol, ticks, base_ts):
            all_events.append((b.ts_close, 1, b))  # base timeframe: priority 1 (ingested AFTER same-tf HTF closes)
        for tf, group in (("H1", 4), ("H4", 16), ("D1", 96)):
            for b in _aggregate(symbol, tf, group, ticks, base_ts):
                all_events.append((b.ts_close, 0, b))  # HTF: priority 0 (ingested first at a shared close)

    all_events.sort(key=lambda e: (e[0], e[1]))

    for ts_close, _priority, bar in all_events:
        scanner.ingest_bar(bar)
        if bar.timeframe == "M15":
            scanner.advance_clock(ts_close)
            ctx = scanner.build_context(bar.symbol, ts_close)
            contexts_by_symbol[bar.symbol].append(ctx)

    return contexts_by_symbol


class TestDeterminism:
    def test_identical_replay_produces_identical_contexts(self) -> None:
        run1 = _run_replay(["XAUUSD"], n_m15_bars=200, seed=7)
        run2 = _run_replay(["XAUUSD"], n_m15_bars=200, seed=7)
        assert run1 == run2

    def test_different_seed_produces_different_contexts(self) -> None:
        run1 = _run_replay(["XAUUSD"], n_m15_bars=200, seed=7)
        run2 = _run_replay(["XAUUSD"], n_m15_bars=200, seed=8)
        # at least the price-derived features must differ somewhere in the run
        feats1 = [c["timeframes"]["M15"]["features"]["m_atr"] for c in run1["XAUUSD"]]
        feats2 = [c["timeframes"]["M15"]["features"]["m_atr"] for c in run2["XAUUSD"]]
        assert feats1 != feats2


class TestLookaheadSafety:
    def test_no_bar_in_any_context_closes_after_as_of(self) -> None:
        contexts = _run_replay(["XAUUSD"], n_m15_bars=300, seed=3)["XAUUSD"]
        violations = []
        for ctx in contexts:
            as_of = ctx["meta"]["as_of"]
            for tf, tf_ctx in ctx["timeframes"].items():
                for bar in tf_ctx["bars"]:
                    if bar["available_at"] > as_of:
                        violations.append((tf, bar["available_at"], as_of))
        assert violations == []

    def test_htf_feature_only_updates_at_its_own_close(self) -> None:
        contexts = _run_replay(["XAUUSD"], n_m15_bars=200, seed=11)["XAUUSD"]
        h1_trend_series = [c["timeframes"]["M15"]["features"]["h1_trend_up"] for c in contexts]
        # h1_trend_up can only change on M15 bars that coincide with an H1 close (every 4th M15 bar);
        # collect the indices where the value actually changes and confirm they are all multiples of 4
        # (i.e. only at H1 boundaries), once warmed up enough to be non-None.
        first_non_none = next((i for i, v in enumerate(h1_trend_series) if v is not None), None)
        assert first_non_none is not None
        for i in range(first_non_none + 1, len(h1_trend_series)):
            if h1_trend_series[i] != h1_trend_series[i - 1]:
                assert (i + 1) % 4 == 0, f"h1_trend_up changed off an H1 boundary at M15 index {i}"


class TestMultiSymbolIsolation:
    def test_two_symbols_independent_and_both_schema_valid(self) -> None:
        contexts = _run_replay(["XAUUSD", "EURUSD"], n_m15_bars=150, seed=5)
        assert set(contexts) == {"XAUUSD", "EURUSD"}
        last_a = contexts["XAUUSD"][-1]
        last_b = contexts["EURUSD"][-1]
        assert last_a["timeframes"]["M15"]["features"]["m_atr"] != last_b["timeframes"]["M15"]["features"]["m_atr"]
        for ctx in (last_a, last_b):
            assert validate_context(ctx) == []


class TestGapHandling:
    def test_feed_outage_recorded_as_gap_and_degrades_quality(self) -> None:
        scanner = MarketScanner(ScannerConfig(history_buffer_bars=50, max_gap_bars_before_degraded=1))
        scanner.configure([SymbolMeta(symbol="XAUUSD", tick_size=0.1, point_value=1.0, price_precision=2)],
                           AdapterConfig(mode=Mode.REPLAY))
        req = Requirements(timeframes=frozenset({"M15"}), fields_by_timeframe={}, lookback_by_timeframe={"M15": 10},
                            symbols=frozenset({"XAUUSD"}))
        scanner.register_requirements(req)
        ticks = _random_walk_m15(20, seed=1)
        bars = _m15_bars("XAUUSD", ticks, base_ts=0)
        for b in bars[:10]:
            scanner.ingest_bar(b)
        # skip bars[10:15] to simulate an outage, then resume
        for b in bars[15:]:
            scanner.ingest_bar(b)
            scanner.advance_clock(b.ts_close)
        ctx = scanner.build_context("XAUUSD", bars[-1].ts_close)
        gaps = ctx["data_quality"]["by_timeframe"]["M15"]["gaps"]
        assert len(gaps) == 1
        assert gaps[0]["bars_missing"] == 5
        assert gaps[0]["cause"] is None  # a weekday outage, not a weekend/holiday
        assert ctx["data_quality"]["overall"] == "DEGRADED"
        assert validate_context(ctx) == []

    def test_weekend_gap_flagged_and_exempted_from_degraded(self) -> None:
        scanner = MarketScanner(ScannerConfig(history_buffer_bars=50))
        scanner.configure([SymbolMeta(symbol="XAUUSD", tick_size=0.1, point_value=1.0, price_precision=2)],
                           AdapterConfig(mode=Mode.REPLAY))
        req = Requirements(timeframes=frozenset({"M15"}), fields_by_timeframe={}, lookback_by_timeframe={"M15": 5},
                            symbols=frozenset({"XAUUSD"}))
        scanner.register_requirements(req)
        # epoch 0 = Thursday. Friday = +1 day, Monday = +4 days. Land the pre-gap bars late on
        # Friday (so the calendar engine's last-seen dow is genuinely Friday=4), then jump to Monday.
        friday_start = 1 * _D1
        monday_start = 4 * _D1
        friday_evening_bars_start = friday_start + 80 * _M15  # hour 20 onward, still Friday
        friday_ticks = _random_walk_m15(8, seed=2)
        bars = _m15_bars("XAUUSD", friday_ticks, base_ts=friday_evening_bars_start)
        for b in bars:
            scanner.ingest_bar(b)
            scanner.advance_clock(b.ts_close)
        monday_ticks = _random_walk_m15(4, seed=3)
        monday_bars = _m15_bars("XAUUSD", monday_ticks, base_ts=monday_start)
        ctx = None
        for b in monday_bars:
            scanner.ingest_bar(b)
            scanner.advance_clock(b.ts_close)
            if ctx is None:  # capture the context for the FIRST monday bar specifically
                ctx = scanner.build_context("XAUUSD", b.ts_close)
        assert ctx["calendar"]["is_weekend_gap"] is True
        gaps = ctx["data_quality"]["by_timeframe"]["M15"]["gaps"]
        assert gaps and gaps[-1]["cause"] == "weekend"
        # a purely weekend-caused gap must not be the reason for a DEGRADED classification
        assert ctx["data_quality"]["overall"] != "DEGRADED"


class TestWarmupProgression:
    def test_sufficiency_improves_from_insufficient_to_sufficient(self) -> None:
        scanner = MarketScanner(ScannerConfig(history_buffer_bars=30))
        scanner.configure([SymbolMeta(symbol="XAUUSD", tick_size=0.1, point_value=1.0, price_precision=2)],
                           AdapterConfig(mode=Mode.REPLAY))
        req = Requirements(timeframes=frozenset({"M15"}), fields_by_timeframe={"M15": frozenset({"m_atr"})},
                            lookback_by_timeframe={"M15": 20}, symbols=frozenset({"XAUUSD"}))
        scanner.register_requirements(req)
        ticks = _random_walk_m15(40, seed=9)
        bars = _m15_bars("XAUUSD", ticks, base_ts=0)
        first_ctx = None
        last_ctx = None
        for i, b in enumerate(bars):
            scanner.ingest_bar(b)
            scanner.advance_clock(b.ts_close)
            ctx = scanner.build_context("XAUUSD", b.ts_close)
            if i == 0:
                first_ctx = ctx
            last_ctx = ctx
        assert first_ctx["sufficiency"]["overall"] == "INSUFFICIENT"
        assert last_ctx["sufficiency"]["overall"] == "SUFFICIENT"
        assert scanner.warmup_status("XAUUSD").satisfied is True

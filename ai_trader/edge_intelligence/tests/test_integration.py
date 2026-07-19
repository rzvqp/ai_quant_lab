"""Real-data integration test for Edge Intelligence -- Phase 7 Checkpoint 6. Drives a real
``MarketScanner``/``ReplayDataSource`` pair (the same construction used by
``ai_trader/market_intelligence/tests/test_integration.py``) over real XAUUSD market data, then
calls ``evaluate_edges()`` against the REAL Strategy Library (no synthetic override) to prove this
layer runs cleanly against every real, currently-registered production strategy -- not just
hand-built fixtures.
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.edge_intelligence.engine import evaluate_edges
from ai_trader.edge_intelligence.types import EdgeState
from ai_trader.market_scanner.scanner import AdapterConfig, MarketScanner
from ai_trader.market_scanner.config import ScannerConfig
from ai_trader.market_scanner.types import Mode, SymbolMeta
from ai_trader.simulation.data_source import ReplayDataSource

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOLS = ("XAUUSD",)
TIMEFRAMES = ("M15", "H1", "H4", "D1")
BASE_TIMEFRAME = "M15"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}

WINDOW_START = 1_672_617_600
WINDOW_END = 1_680_000_000
WARMUP_BARS = 200

#: The full, currently-registered production strategy set with a valid real contract (verified via
#: ``loader.load_all(DEFAULT_LIBRARY_PATH)`` directly against this repo's real Strategy Library:
#: 43 successfully parsed, matching ``_registered_strategy_ids()`` exactly).
_EXPECTED_STRATEGY_COUNT = 43


def _real_contexts(limit: int = 20) -> list[dict[str, object]]:
    data_source = ReplayDataSource(SYMBOLS, TIMEFRAMES, BASE_TIMEFRAME, DATA_DIR)
    ticks = data_source.base_ticks_in_range(WINDOW_START, WINDOW_END, WARMUP_BARS)
    assert ticks, "no market data found for the established test window"

    scanner = MarketScanner(ScannerConfig(base_timeframe=BASE_TIMEFRAME))
    scanner.configure(list(SYMBOL_META.values()), AdapterConfig(mode=Mode.REPLAY, source_id="replay"))

    contexts: list[dict[str, object]] = []
    for as_of in ticks:
        data_source.feed_up_to(scanner, as_of)
        scanner.advance_clock(as_of)
        if as_of < WINDOW_START:
            continue
        context_batch = scanner.scan(as_of, list(SYMBOLS))
        ctx = context_batch.get("XAUUSD")
        if ctx is not None:
            contexts.append(ctx)
        if len(contexts) >= limit:
            break
    return contexts


def test_evaluate_edges_runs_cleanly_over_real_market_data_and_the_real_library() -> None:
    contexts = _real_contexts(limit=20)
    assert len(contexts) > 0

    for ctx in contexts:
        snapshot = evaluate_edges(ctx)  # default library_path -- the REAL Strategy Library
        assert snapshot.symbol == "XAUUSD"
        assert len(snapshot.readings) == _EXPECTED_STRATEGY_COUNT
        for reading in snapshot.readings.values():
            assert reading.state in (EdgeState.PRESENT, EdgeState.POSSIBLE, EdgeState.ABSENT)
            assert len(reading.evidence) == 6


def test_evaluate_edges_is_deterministic_over_real_contexts() -> None:
    contexts = _real_contexts(limit=5)
    for ctx in contexts:
        assert evaluate_edges(ctx) == evaluate_edges(ctx)


def test_evaluate_edges_produces_a_real_mix_of_states_over_real_data() -> None:
    # Over 20 real bars x 43 real strategies, at least SOME reading should land in EACH of
    # PRESENT/POSSIBLE/ABSENT at some point -- a sanity check that the evidence rules genuinely
    # discriminate on real declared contract fields, not silently collapsing to one verdict always.
    contexts = _real_contexts(limit=20)
    seen_states: set[EdgeState] = set()
    for ctx in contexts:
        snapshot = evaluate_edges(ctx)
        seen_states.update(reading.state for reading in snapshot.readings.values())
    assert seen_states == {EdgeState.PRESENT, EdgeState.POSSIBLE, EdgeState.ABSENT}

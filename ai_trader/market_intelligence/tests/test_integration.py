"""Real-data integration test for Market Intelligence -- Phase 7 Checkpoint 5. Drives a real
``MarketScanner``/``ReplayDataSource`` pair directly (the SAME construction `SimulationHarness.load()`
itself uses internally) over real XAUUSD market data -- no Signal Engine/Scoring Engine/Risk Manager/
Execution Engine/Shadow Evidence involved at all, since ``build_market_intelligence`` never needs them.
Proves the engine runs cleanly, deterministically, and without ever raising across many real bars, not
just hand-built fixtures.
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.market_intelligence.engine import build_market_intelligence
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

# The same 85-day window every other integration test in this project already uses.
WINDOW_START = 1_672_617_600
WINDOW_END = 1_680_000_000
WARMUP_BARS = 200


def _real_contexts(limit: int = 300) -> list[dict[str, object]]:
    """The first ``limit`` real, fully-warmed-up ``MarketContext`` snapshots over the established
    window -- built by driving the scanner directly, never through a full harness (Signal/Scoring/
    Risk/Execution are never constructed at all, since this test needs none of them)."""
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
            continue  # still warming up -- not yet a "real" post-warmup bar
        context_batch = scanner.scan(as_of, list(SYMBOLS))
        ctx = context_batch.get("XAUUSD")
        if ctx is not None:
            contexts.append(ctx)
        if len(contexts) >= limit:
            break
    return contexts


def test_build_market_intelligence_runs_cleanly_over_real_market_data() -> None:
    contexts = _real_contexts(limit=300)
    assert len(contexts) > 0

    for ctx in contexts:
        snapshot = build_market_intelligence(ctx)  # must never raise
        assert snapshot.symbol == "XAUUSD"
        assert set(snapshot.trend) == {"M15", "H1", "H4", "D1"}
        assert set(snapshot.momentum) == {"M15", "H1", "H4", "D1"}
        assert snapshot.confidence.score is not None
        if snapshot.confidence.score is not None:
            assert 0.0 <= snapshot.confidence.score <= 1.0
        if snapshot.multi_timeframe_agreement.agreement_score is not None:
            assert 0.0 <= snapshot.multi_timeframe_agreement.agreement_score <= 1.0


def test_build_market_intelligence_is_deterministic_over_real_contexts() -> None:
    contexts = _real_contexts(limit=50)
    for ctx in contexts:
        assert build_market_intelligence(ctx) == build_market_intelligence(ctx)


def test_build_market_intelligence_produces_non_trivial_readings_over_real_data() -> None:
    # Over 300 real bars, at least SOME dimension should show real signal (not every reading UNKNOWN
    # the entire time) -- a sanity check that this is genuinely reading real features, not silently
    # failing to find them under a wrong key name.
    from ai_trader.market_intelligence.types import StructureState, TrendDirection, VolatilityRegime

    contexts = _real_contexts(limit=300)
    snapshots = [build_market_intelligence(ctx) for ctx in contexts]

    assert any(s.trend["M15"].direction is not TrendDirection.UNKNOWN for s in snapshots)
    assert any(s.volatility.regime is not VolatilityRegime.UNKNOWN for s in snapshots)
    assert any(s.structure.state is not StructureState.UNKNOWN for s in snapshots)
    assert any(s.session.session_name is not None for s in snapshots)

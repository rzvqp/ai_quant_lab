"""Real-data integration test -- Phase 7 Checkpoint 15. Drives real XAUUSD market data through both
`make_decision()` (v1) and `make_decision_v2()` (v2, with a populated synthetic Context Memory index),
runs the full falsification study over the paired result, and confirms the study reaches
`V1_REMAINS_ACTIVE` with a proven, not merely observed, zero-divergence recommendation stream -- the
same real-data proof Checkpoint 14 already established, now exercised through the comparison framework
itself.
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.decision_comparison.falsification import run_falsification_study
from ai_trader.decision_comparison.types import FalsificationVerdict
from ai_trader.decision_intelligence.engine import make_decision
from ai_trader.decision_intelligence_v2.engine import make_decision_v2
from ai_trader.decision_intelligence_v2.tests._fixtures import build_populated_index
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


def test_falsification_study_over_real_market_data_yields_v1_remains_active(tmp_path: Path) -> None:
    contexts = _real_contexts(limit=20)
    assert contexts

    index = build_populated_index(tmp_path, strategy_id="S1", n_episodes=10)

    pairs = []
    for ctx in contexts:
        v1 = make_decision(ctx)
        v2 = make_decision_v2(ctx, context_memory_index=index)
        pairs.append((v1, v2))

    report = run_falsification_study(pairs)

    assert report.recommendation_comparison.n_compared == len(contexts)
    assert report.recommendation_comparison.divergences == 0
    assert report.trade_outcome_equivalence.equivalence_holds is True
    assert report.verdict is FalsificationVerdict.V1_REMAINS_ACTIVE

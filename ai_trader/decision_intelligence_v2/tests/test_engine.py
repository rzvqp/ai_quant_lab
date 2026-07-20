"""Unit + real-data integration tests for :mod:`ai_trader.decision_intelligence_v2.engine`.

The central invariant under test throughout this file: `make_decision_v2(...).recommended_strategy_id`
must ALWAYS equal `make_decision(...).recommended_strategy_id` for the identical input -- Context Memory
must never change the recommendation, with or without a populated historical index.
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.decision_intelligence.engine import make_decision
from ai_trader.decision_intelligence_v2.engine import make_decision_v2
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


def _real_contexts(limit: int = 10) -> list[dict[str, object]]:
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


# ------------------------------------------------------------------ no index supplied


def test_make_decision_v2_without_index_matches_v1_and_has_no_context_evidence() -> None:
    for ctx in _real_contexts(limit=5):
        v1 = make_decision(ctx)
        v2 = make_decision_v2(ctx)
        assert v2.recommended_strategy_id == v1.recommended_strategy_id
        assert v2.v1_report == v1
        for c in v2.candidates:
            assert c.context_evidence is None


# ------------------------------------------------------------------ synthetic populated index


def test_make_decision_v2_with_populated_index_still_matches_v1(tmp_path: Path) -> None:
    from ai_trader.decision_intelligence_v2.tests._fixtures import build_populated_index

    contexts = _real_contexts(limit=5)
    assert contexts

    v1_reports = [make_decision(ctx) for ctx in contexts]
    present_strategy_ids = sorted({c.strategy_id for r in v1_reports for c in r.candidates})
    assert present_strategy_ids, "no PRESENT strategy found in the test window -- fixture assumption broken"

    index = build_populated_index(tmp_path, strategy_id=present_strategy_ids[0], n_episodes=10)

    for ctx, v1 in zip(contexts, v1_reports):
        v2 = make_decision_v2(ctx, context_memory_index=index)
        assert v2.recommended_strategy_id == v1.recommended_strategy_id

        for c in v2.candidates:
            assert c.context_evidence is not None
            assert len(c.context_evidence.explanation) > 0
            if c.candidate.strategy_id == present_strategy_ids[0]:
                # this strategy has synthetic history -- its own evidence report must reflect it
                assert c.context_evidence.evidence is not None


def test_make_decision_v2_is_deterministic(tmp_path: Path) -> None:
    from ai_trader.decision_intelligence_v2.tests._fixtures import build_populated_index

    contexts = _real_contexts(limit=3)
    index = build_populated_index(tmp_path, strategy_id="S1", n_episodes=5)
    for ctx in contexts:
        a = make_decision_v2(ctx, context_memory_index=index)
        b = make_decision_v2(ctx, context_memory_index=index)
        assert a == b


def test_make_decision_v2_over_real_data_recommendation_never_diverges_from_v1(tmp_path: Path) -> None:
    from ai_trader.decision_intelligence_v2.tests._fixtures import build_populated_index

    contexts = _real_contexts(limit=20)
    index = build_populated_index(tmp_path, strategy_id="S1", n_episodes=5)
    for ctx in contexts:
        v1 = make_decision(ctx)
        v2 = make_decision_v2(ctx, context_memory_index=index)
        assert v2.recommended_strategy_id == v1.recommended_strategy_id

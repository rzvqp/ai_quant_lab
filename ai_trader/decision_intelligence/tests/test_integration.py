"""Real-data integration test for Decision Intelligence -- Phase 7 Checkpoint 7. Drives a real
``MarketScanner``/``ReplayDataSource`` pair (the same construction used by
``ai_trader/edge_intelligence/tests/test_integration.py``) over real XAUUSD market data, then calls
``make_decision()`` against the REAL Strategy Library (no synthetic override, no research_stats
supplied) to prove this layer runs cleanly end-to-end -- Market Intelligence -> Edge Intelligence ->
Decision Intelligence -- over real data, not just hand-built fixtures.
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.decision_intelligence.engine import NO_TRADE, make_decision, recommended_or_no_trade
from ai_trader.decision_intelligence.types import DecisionOutcome
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


def test_make_decision_runs_cleanly_over_real_market_data_and_the_real_library() -> None:
    contexts = _real_contexts(limit=20)
    assert len(contexts) > 0

    for ctx in contexts:
        report = make_decision(ctx)  # default library_path -- the REAL Strategy Library, no research_stats
        assert report.symbol == "XAUUSD"
        for candidate in report.candidates:
            assert candidate.outcome in (DecisionOutcome.ACCEPT, DecisionOutcome.REJECT)
            assert len(candidate.evidence) > 0
        # recommended_strategy_id, if set, must be one of the ACCEPTed candidates
        if report.recommended_strategy_id is not None:
            accepted_ids = {c.strategy_id for c in report.candidates if c.outcome is DecisionOutcome.ACCEPT}
            assert report.recommended_strategy_id in accepted_ids
        assert recommended_or_no_trade(report) == (report.recommended_strategy_id or NO_TRADE)


def test_make_decision_is_deterministic_over_real_contexts() -> None:
    contexts = _real_contexts(limit=5)
    for ctx in contexts:
        assert make_decision(ctx) == make_decision(ctx)


def test_make_decision_over_real_data_genuinely_discriminates() -> None:
    # Over 20 real bars x every readable real strategy, both ACCEPT and REJECT must genuinely occur --
    # a sanity check that the eligibility gates and Edge Intelligence's own PRESENT/ABSENT split are
    # real discriminators on real data, not a silently-collapsed verdict. (Whether NO TRADE itself ever
    # occurs in this particular 20-bar window depends on the current Library's static contract metadata,
    # not a property this test should hardcode -- real strategy maturity/confidence do not change bar to
    # bar, so a strategy that is both PRESENT and the top-ranked ACCEPT candidate on most bars will
    # dominate the recommendation deterministically, which is correct behaviour, not a defect.)
    contexts = _real_contexts(limit=20)
    outcomes_seen = set()
    for ctx in contexts:
        report = make_decision(ctx)
        outcomes_seen.update(c.outcome for c in report.candidates)
    assert outcomes_seen == {DecisionOutcome.ACCEPT, DecisionOutcome.REJECT}

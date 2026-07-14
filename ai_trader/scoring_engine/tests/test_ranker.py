"""Tests for :mod:`ai_trader.scoring_engine.ranker`."""

from __future__ import annotations

from ai_trader.scoring_engine.ranker import rank_scores
from ai_trader.scoring_engine.types import (
    ComponentScores,
    OpportunityScore,
    Quality,
    Recommendation,
    Refs,
    ReasonCode,
    ScoreConfidence,
)
from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.signal_engine.types import Direction, SignalState


def _score(strategy_id: str, total: int, hist_conf: float = 0.0, sig_strength: float = 0.0) -> OpportunityScore:
    return OpportunityScore(
        scoring_schema_version="1.0.0", scoring_engine_version="1.0.0", scoring_model_version="1.0.0",
        score_id=f"{strategy_id}|XAUUSD|1", signal_id="sig", strategy_id=strategy_id, symbol="XAUUSD",
        timestamp=1, as_of=1, state=SignalState.BUY, direction=Direction.LONG, total_score=total,
        component_scores=ComponentScores(signal_strength=sig_strength, historical_confidence=hist_conf),
        confidence=ScoreConfidence.LOW, quality=Quality.MODERATE, recommendation=Recommendation.MODERATE_OPPORTUNITY,
        rank=1, reason_codes=(ReasonCode(code="SCORED_CLEAN"),),
        refs=Refs(strategy_version="1.0.0", signal_schema_version="1.0.0", interface_version="1.0.0", data_quality=DataQualityLevel.OK),
    )


class TestRankScores:
    def test_orders_by_total_score_descending(self) -> None:
        scores = [_score("S1", 40), _score("S2", 80), _score("S3", 60)]
        ranked = rank_scores(scores)
        assert [s.strategy_id for s in ranked] == ["S2", "S3", "S1"]
        assert [s.rank for s in ranked] == [1, 2, 3]

    def test_ties_broken_by_historical_confidence_desc(self) -> None:
        scores = [_score("S1", 50, hist_conf=0.2), _score("S2", 50, hist_conf=0.8)]
        ranked = rank_scores(scores)
        assert [s.strategy_id for s in ranked] == ["S2", "S1"]

    def test_ties_broken_by_signal_strength_desc(self) -> None:
        scores = [
            _score("S1", 50, hist_conf=0.5, sig_strength=0.3),
            _score("S2", 50, hist_conf=0.5, sig_strength=0.9),
        ]
        ranked = rank_scores(scores)
        assert [s.strategy_id for s in ranked] == ["S2", "S1"]

    def test_final_tiebreak_is_strategy_id_ascending(self) -> None:
        scores = [
            _score("S9", 50, hist_conf=0.5, sig_strength=0.5),
            _score("S2", 50, hist_conf=0.5, sig_strength=0.5),
        ]
        ranked = rank_scores(scores)
        assert [s.strategy_id for s in ranked] == ["S2", "S9"]

    def test_empty_list_returns_empty_tuple(self) -> None:
        assert rank_scores([]) == ()

    def test_single_score_gets_rank_one(self) -> None:
        ranked = rank_scores([_score("S1", 50)])
        assert ranked[0].rank == 1

    def test_deterministic_across_calls(self) -> None:
        scores = [_score("S1", 40), _score("S2", 80), _score("S3", 60), _score("S4", 80, hist_conf=0.9)]
        first = rank_scores(scores)
        second = rank_scores(scores)
        assert first == second

    def test_total_order_guarantees_no_ties_remain(self) -> None:
        scores = [_score(f"S{i}", 50, hist_conf=0.5, sig_strength=0.5) for i in range(1, 6)]
        ranked = rank_scores(scores)
        assert [s.rank for s in ranked] == [1, 2, 3, 4, 5]
        assert [s.strategy_id for s in ranked] == ["S1", "S2", "S3", "S4", "S5"]

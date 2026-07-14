"""Tests for :mod:`ai_trader.scoring_engine.aggregator`."""

from __future__ import annotations

import pytest

from ai_trader.scoring_engine import aggregator
from ai_trader.scoring_engine.config import ConfidenceBands, QualityBands, RecommendationBands
from ai_trader.scoring_engine.types import READY_STATES, Quality, Recommendation, ScoreConfidence
from ai_trader.signal_engine.types import SignalState

QB = QualityBands()
RB = RecommendationBands()
CB = ConfidenceBands()


class TestRoundHalfUp:
    @pytest.mark.parametrize("value,expected", [
        (0.5, 1), (1.5, 2), (2.5, 3), (35.25, 35), (35.5, 36), (0.0, 0), (99.5, 100),
    ])
    def test_half_up_not_banker_rounding(self, value: float, expected: int) -> None:
        assert aggregator.round_half_up(value) == expected

    def test_differs_from_python_builtin_round_at_the_half_boundary(self) -> None:
        """Regression guard: Python's round() uses round-half-to-even (round(2.5)==2), which would
        silently violate SCORING_MODEL.md's explicit "deterministic rounding: half-up"."""
        assert round(2.5) == 2  # documents the builtin's behavior we deliberately avoid
        assert aggregator.round_half_up(2.5) == 3


class TestAggregate:
    def test_no_penalties_total_is_100_times_base_quality(self) -> None:
        penalty_factor, total = aggregator.aggregate(base_quality=0.7, risk_penalty=0.0, conflict_penalty=0.0)
        assert penalty_factor == 1.0
        assert total == 70

    def test_full_risk_penalty_zeroes_the_score(self) -> None:
        _, total = aggregator.aggregate(base_quality=0.9, risk_penalty=1.0, conflict_penalty=0.0)
        assert total == 0

    def test_full_conflict_penalty_zeroes_the_score(self) -> None:
        _, total = aggregator.aggregate(base_quality=0.9, risk_penalty=0.0, conflict_penalty=1.0)
        assert total == 0

    def test_penalties_compound_multiplicatively(self) -> None:
        penalty_factor, _ = aggregator.aggregate(base_quality=1.0, risk_penalty=0.5, conflict_penalty=0.5)
        assert penalty_factor == pytest.approx(0.25)

    def test_total_score_always_in_bounds(self) -> None:
        for bq in (0.0, 0.3, 0.7, 1.0):
            for rp in (0.0, 0.5, 1.0):
                for cp in (0.0, 0.5, 1.0):
                    _, total = aggregator.aggregate(bq, rp, cp)
                    assert 0 <= total <= 100


class TestQualityBand:
    @pytest.mark.parametrize("score,expected", [
        (80, Quality.PREMIUM), (100, Quality.PREMIUM), (79, Quality.STRONG), (65, Quality.STRONG),
        (64, Quality.MODERATE), (45, Quality.MODERATE), (44, Quality.WEAK), (25, Quality.WEAK),
        (24, Quality.POOR), (0, Quality.POOR),
    ])
    def test_exact_bands(self, score: int, expected: Quality) -> None:
        assert aggregator.quality_band(score, QB) is expected


class TestRecommendationFor:
    @pytest.mark.parametrize("score,expected", [
        (65, Recommendation.STRONG_OPPORTUNITY), (100, Recommendation.STRONG_OPPORTUNITY),
        (64, Recommendation.MODERATE_OPPORTUNITY), (45, Recommendation.MODERATE_OPPORTUNITY),
        (44, Recommendation.WEAK_OPPORTUNITY), (25, Recommendation.WEAK_OPPORTUNITY),
        (24, Recommendation.SKIP), (0, Recommendation.SKIP),
    ])
    def test_actionable_bands(self, score: int, expected: Recommendation) -> None:
        assert aggregator.recommendation_for(SignalState.BUY, score, RB) is expected
        assert aggregator.recommendation_for(SignalState.SELL, score, RB) is expected

    def test_ready_states_are_watch_regardless_of_score(self) -> None:
        for state in READY_STATES:
            assert aggregator.recommendation_for(state, 90, RB) is Recommendation.WATCH
            assert aggregator.recommendation_for(state, 0, RB) is Recommendation.WATCH

    def test_wait_confirmation_is_watch_regardless_of_score(self) -> None:
        assert aggregator.recommendation_for(SignalState.WAIT_CONFIRMATION, 90, RB) is Recommendation.WATCH


class TestConfidenceBand:
    def test_zero_is_none(self) -> None:
        assert aggregator.confidence_band(0.0, CB) is ScoreConfidence.NONE

    def test_bands_are_monotonic_and_exhaustive(self) -> None:
        prev = None
        for value in (0.0, 0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.9, 1.0):
            band = aggregator.confidence_band(value, CB)
            assert isinstance(band, ScoreConfidence)
            if prev is not None:
                order = list(ScoreConfidence)
                assert order.index(band) >= order.index(prev)
            prev = band

    def test_high_at_or_above_threshold(self) -> None:
        assert aggregator.confidence_band(CB.high_min, CB) is ScoreConfidence.HIGH

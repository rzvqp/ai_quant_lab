"""Unit tests for the Health Score -> state classification."""

from __future__ import annotations

from ai_trader.strategy_health.classifier import classify
from ai_trader.strategy_health.types import HealthState


class TestBands:
    def test_score_at_65_is_active(self) -> None:
        state, _ = classify(65.0, None)
        assert state is HealthState.ACTIVE

    def test_score_just_below_65_is_watchlist(self) -> None:
        state, _ = classify(64.9, None)
        assert state is HealthState.WATCHLIST

    def test_score_at_45_is_watchlist(self) -> None:
        state, _ = classify(45.0, None)
        assert state is HealthState.WATCHLIST

    def test_score_just_below_45_is_probation(self) -> None:
        state, _ = classify(44.9, None)
        assert state is HealthState.PROBATION

    def test_score_at_25_is_probation(self) -> None:
        state, _ = classify(25.0, None)
        assert state is HealthState.PROBATION

    def test_score_just_below_25_is_disabled(self) -> None:
        state, _ = classify(24.9, None)
        assert state is HealthState.DISABLED

    def test_score_of_zero_is_disabled(self) -> None:
        state, _ = classify(0.0, None)
        assert state is HealthState.DISABLED

    def test_none_score_is_watchlist(self) -> None:
        state, reason = classify(None, None)
        assert state is HealthState.WATCHLIST
        assert "no trades" in reason.lower()


class TestTrendAdjustment:
    def test_strong_positive_trend_bumps_up_one_tier(self) -> None:
        # base band for 50.0 is WATCHLIST; +15 trend should bump to ACTIVE
        state, reason = classify(50.0, 15.0)
        assert state is HealthState.ACTIVE
        assert "bumped up" in reason

    def test_strong_negative_trend_bumps_down_one_tier(self) -> None:
        # base band for 50.0 is WATCHLIST; -15 trend should bump to PROBATION
        state, reason = classify(50.0, -15.0)
        assert state is HealthState.PROBATION
        assert "bumped down" in reason

    def test_moderate_trend_below_threshold_does_not_bump(self) -> None:
        state, _ = classify(50.0, 14.9)
        assert state is HealthState.WATCHLIST

    def test_bump_up_is_capped_at_active(self) -> None:
        state, _ = classify(70.0, 15.0)  # already ACTIVE
        assert state is HealthState.ACTIVE

    def test_bump_down_is_floored_at_disabled(self) -> None:
        state, _ = classify(10.0, -15.0)  # already DISABLED
        assert state is HealthState.DISABLED

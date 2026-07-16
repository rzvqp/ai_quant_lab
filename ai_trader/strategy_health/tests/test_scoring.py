"""Unit tests for the composite Health Score derivation (percentile ranking, credibility shrinkage,
PCA-derived weights, window combination)."""

from __future__ import annotations

from ai_trader.strategy_health.metrics import compute_window_metrics
from ai_trader.strategy_health.scoring import (
    combine_windows, credibility_weight, percentile_rank, score_window,
)
from ai_trader.strategy_health.types import ClosedTrade, WindowScore

AS_OF = 1_700_000_000
_DAY = 86400


def trade(sid: str, days_ago: int, net_pnl: float, pnl_r: float | None = None) -> ClosedTrade:
    return ClosedTrade(strategy_id=sid, exit_as_of=AS_OF - days_ago * _DAY, net_pnl=net_pnl, pnl_r=pnl_r, holding_bars=10)


class TestPercentileRank:
    def test_value_below_all_ranks_zero(self) -> None:
        assert percentile_rank(0.0, [1.0, 2.0, 3.0], "neutral") == 0.0

    def test_value_above_all_ranks_100(self) -> None:
        assert percentile_rank(4.0, [1.0, 2.0, 3.0], "neutral") == 100.0

    def test_value_in_the_middle(self) -> None:
        assert percentile_rank(2.0, [1.0, 2.0, 3.0], "neutral") == 50.0  # 1 below, 1 tied, 1 above

    def test_none_with_neutral_meaning_ranks_50(self) -> None:
        assert percentile_rank(None, [1.0, 2.0, 3.0], "neutral") == 50.0

    def test_none_with_best_meaning_ranks_100(self) -> None:
        assert percentile_rank(None, [1.0, 2.0, 3.0], "best") == 100.0

    def test_empty_population_ranks_50(self) -> None:
        assert percentile_rank(5.0, [], "neutral") == 50.0


class TestCredibilityWeight:
    def test_zero_trades_has_zero_credibility(self) -> None:
        assert credibility_weight(0) == 0.0

    def test_n_equals_k_gives_half_credibility(self) -> None:
        assert credibility_weight(10, k=10.0) == 0.5

    def test_large_n_approaches_full_credibility(self) -> None:
        assert credibility_weight(10_000, k=10.0) > 0.99


class TestScoreWindow:
    def _population(self, n_strategies: int, n_trades_each: int) -> list:
        pop = []
        for i in range(n_strategies):
            trades = [trade(f"S{i}", d + 1, 1.0 if d % 2 == 0 else -1.0) for d in range(n_trades_each)]
            pop.append(compute_window_metrics(trades, "3m", AS_OF))
        return pop

    def test_zero_trades_gives_no_score(self) -> None:
        empty = compute_window_metrics([], "3m", AS_OF)
        result = score_window(empty, [])
        assert result.score is None
        assert result.confidence == 0.0

    def test_strong_strategy_scores_above_weak_strategy(self) -> None:
        strong_trades = [trade("STRONG", d + 1, 10.0, pnl_r=2.0) for d in range(20)]
        weak_trades = [trade("WEAK", d + 1, -10.0, pnl_r=-2.0) for d in range(20)]
        strong_m = compute_window_metrics(strong_trades, "3m", AS_OF)
        weak_m = compute_window_metrics(weak_trades, "3m", AS_OF)
        population = [strong_m, weak_m] + self._population(5, 8)

        strong_score = score_window(strong_m, population)
        weak_score = score_window(weak_m, population)
        assert strong_score.score is not None and weak_score.score is not None
        assert strong_score.score > weak_score.score

    def test_metric_weights_sum_to_one(self) -> None:
        population = self._population(6, 12)
        result = score_window(population[0], population)
        assert abs(sum(result.metric_weights.values()) - 1.0) < 1e-9

    def test_small_population_falls_back_to_equal_weights(self) -> None:
        population = self._population(2, 8)  # below MIN_POPULATION_FOR_PCA
        result = score_window(population[0], population)
        weights = list(result.metric_weights.values())
        assert all(abs(w - weights[0]) < 1e-9 for w in weights)

    def test_low_sample_size_shrinks_toward_neutral(self) -> None:
        one_trade = compute_window_metrics([trade("S1", 1, 100.0, pnl_r=10.0)], "3m", AS_OF)
        population = [one_trade] + self._population(5, 15)
        result = score_window(one_trade, population)
        # a single extreme +10R trade would rank near 100 unshrunk; low confidence pulls it toward 50
        assert result.score is not None and result.score < 90.0


class TestCombineWindows:
    def test_weighted_average_when_all_windows_present(self) -> None:
        scores = {
            "3m": WindowScore("3m", 80.0, 1.0, {}, {}),
            "6m": WindowScore("6m", 60.0, 1.0, {}, {}),
            "12m": WindowScore("12m", 50.0, 1.0, {}, {}),
        }
        overall, trend = combine_windows(scores)
        expected = 0.60 * 50.0 + 0.25 * 60.0 + 0.15 * 80.0
        assert overall is not None and abs(overall - expected) < 1e-9
        assert trend == 80.0 - 50.0

    def test_missing_window_weight_is_redistributed(self) -> None:
        scores = {
            "3m": WindowScore("3m", None, 0.0, {}, {}),
            "6m": WindowScore("6m", 60.0, 1.0, {}, {}),
            "12m": WindowScore("12m", 40.0, 1.0, {}, {}),
        }
        overall, trend = combine_windows(scores)
        expected = (0.25 * 60.0 + 0.60 * 40.0) / (0.25 + 0.60)
        assert overall is not None and abs(overall - expected) < 1e-9
        assert trend is None  # no 3m score available

    def test_no_windows_available_returns_none(self) -> None:
        scores = {w: WindowScore(w, None, 0.0, {}, {}) for w in ("3m", "6m", "12m")}
        overall, trend = combine_windows(scores)
        assert overall is None and trend is None

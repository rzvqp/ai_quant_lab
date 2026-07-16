"""Unit tests for the top-level evaluate_strategy_health orchestrator."""

from __future__ import annotations

from ai_trader.strategy_health.evaluator import WINDOWS, evaluate_strategy_health
from ai_trader.strategy_health.types import ClosedTrade, HealthState

AS_OF = 1_700_000_000
_DAY = 86400


def trade(sid: str, days_ago: int, net_pnl: float, pnl_r: float | None = None) -> ClosedTrade:
    return ClosedTrade(strategy_id=sid, exit_as_of=AS_OF - days_ago * _DAY, net_pnl=net_pnl, pnl_r=pnl_r, holding_bars=10)


class TestEvaluateStrategyHealth:
    def test_every_strategy_id_gets_a_report(self) -> None:
        trades_by_strategy = {
            "S1": [trade("S1", 1, 10.0, pnl_r=1.0)],
            "S2": [],  # no trades at all
        }
        reports = evaluate_strategy_health(trades_by_strategy, AS_OF)
        assert set(reports) == {"S1", "S2"}

    def test_zero_trade_strategy_is_watchlist_with_no_score(self) -> None:
        reports = evaluate_strategy_health({"S1": []}, AS_OF)
        report = reports["S1"]
        assert report.overall_score is None
        assert report.state is HealthState.WATCHLIST
        for window in WINDOWS:
            assert report.window_metrics[window].n_trades == 0
            assert report.window_scores[window].score is None

    def test_report_has_all_three_windows(self) -> None:
        trades = [trade("S1", d + 1, 1.0, pnl_r=0.5) for d in range(30)]
        reports = evaluate_strategy_health({"S1": trades}, AS_OF)
        report = reports["S1"]
        assert set(report.window_metrics) == set(WINDOWS)
        assert set(report.window_scores) == set(WINDOWS)

    def test_strong_and_weak_strategies_rank_differently_with_a_larger_population(self) -> None:
        trades_by_strategy = {
            "STRONG": [trade("STRONG", d + 1, 10.0, pnl_r=2.0) for d in range(15)],
            "WEAK": [trade("WEAK", d + 1, -10.0, pnl_r=-2.0) for d in range(15)],
            **{
                f"MID{i}": [trade(f"MID{i}", d + 1, 1.0 if d % 2 == 0 else -1.0) for d in range(10)]
                for i in range(6)
            },
        }
        reports = evaluate_strategy_health(trades_by_strategy, AS_OF)
        assert reports["STRONG"].overall_score is not None
        assert reports["WEAK"].overall_score is not None
        assert reports["STRONG"].overall_score > reports["WEAK"].overall_score
        assert reports["STRONG"].state in (HealthState.ACTIVE, HealthState.WATCHLIST)
        assert reports["WEAK"].state in (HealthState.PROBATION, HealthState.DISABLED)

    def test_rationale_is_a_nonempty_explanation(self) -> None:
        reports = evaluate_strategy_health({"S1": []}, AS_OF)
        assert len(reports["S1"].rationale) > 10
        assert "S1" in reports["S1"].rationale

"""Unit tests for :mod:`ai_trader.shadow_evidence.research` -- Phase 6.10 Implementation Checkpoint 4.
Pure-function tests, no real market data or harness needed.
"""

from __future__ import annotations

from ai_trader.scoring_engine.types import Recommendation
from ai_trader.shadow_evidence import research
from ai_trader.shadow_evidence.types import ShadowOpportunityRecord, ShadowTradeLegRecord
from ai_trader.signal_engine.types import Direction, SignalState
from ai_trader.simulation.portfolio_simulator import TradeRecord

AS_OF = 1_700_000_000
DAY = 86400


def _opportunity(strategy_id: str, as_of: int = AS_OF) -> ShadowOpportunityRecord:
    return ShadowOpportunityRecord(
        opportunity_id=f"{strategy_id}:XAUUSD:{as_of}", strategy_id=strategy_id, symbol="XAUUSD",
        as_of=as_of, direction=Direction.LONG, signal_state=SignalState.BUY,
        score_recommendation=Recommendation.STRONG_OPPORTUNITY, shadow_risk_decision="ALLOW",
        shadow_denied_reason=None, resulting_position_id=f"{strategy_id}:P:{as_of}",
    )


def _trade(
    strategy_id: str, net_pnl: float, exit_as_of: int, position_id: str = "P1",
    pnl_r: float | None = 1.0, direction: Direction = Direction.LONG,
) -> ShadowTradeLegRecord:
    record = TradeRecord(
        client_order_id=f"SHADOW-CID-{strategy_id}|XAUUSD|{exit_as_of}", strategy_id=strategy_id,
        symbol="XAUUSD", direction=direction, entry_price=2000.0, exit_price=2000.0 + net_pnl,
        entry_as_of=exit_as_of - 900, exit_as_of=exit_as_of, qty=0.1, gross_pnl=net_pnl, fees=0.0,
        net_pnl=net_pnl, pnl_r=pnl_r, holding_bars=1, mfe=0.0, mae=0.0,
    )
    return ShadowTradeLegRecord(leg=record, position_id=position_id, exit_reason="TAKE_PROFIT")


def test_research_summary_for_a_strategy_with_no_trades_is_honest_not_fabricated() -> None:
    summary = research.research_summary_for("S10", "12m", AS_OF, [_opportunity("S10")], [], [])
    assert summary.strategy_id == "S10"
    assert summary.source == "shadow"
    assert summary.window_metrics.n_trades == 0
    assert summary.average_r is None
    assert summary.sharpe_ratio is None
    assert summary.best_month is None and summary.worst_month is None
    assert summary.long.n_trades == 0 and summary.short.n_trades == 0
    assert summary.max_consecutive_wins == 0


def test_average_r_matches_window_metrics_expectancy_r() -> None:
    trade_legs = [
        _trade("S10", net_pnl=10.0, exit_as_of=AS_OF, position_id="P1", pnl_r=1.0),
        _trade("S10", net_pnl=-5.0, exit_as_of=AS_OF + 900, position_id="P2", pnl_r=-0.5),
    ]
    summary = research.research_summary_for("S10", "12m", AS_OF + 900, [_opportunity("S10")], [], trade_legs)
    assert summary.average_r == summary.window_metrics.expectancy_r == 0.25


def test_long_vs_short_stats_are_correctly_split() -> None:
    trade_legs = [
        _trade("S10", net_pnl=10.0, exit_as_of=AS_OF, position_id="P1", direction=Direction.LONG),
        _trade("S10", net_pnl=-4.0, exit_as_of=AS_OF + 900, position_id="P2", direction=Direction.LONG),
        _trade("S10", net_pnl=8.0, exit_as_of=AS_OF + 1800, position_id="P3", direction=Direction.SHORT),
    ]
    summary = research.research_summary_for("S10", "12m", AS_OF + 1800, [_opportunity("S10")], [], trade_legs)
    assert summary.long.n_trades == 2
    assert summary.long.win_rate == 0.5
    assert summary.long.net_pnl == 6.0
    assert summary.short.n_trades == 1
    assert summary.short.win_rate == 1.0
    assert summary.short.net_pnl == 8.0


def test_sharpe_ratio_requires_at_least_two_r_valued_trades() -> None:
    one_trade = [_trade("S10", net_pnl=10.0, exit_as_of=AS_OF, pnl_r=1.0)]
    summary = research.research_summary_for("S10", "12m", AS_OF, [_opportunity("S10")], [], one_trade)
    assert summary.sharpe_ratio is None  # honest None, not a fabricated single-sample ratio

    two_trades = [
        _trade("S10", net_pnl=10.0, exit_as_of=AS_OF, position_id="P1", pnl_r=1.0),
        _trade("S10", net_pnl=-5.0, exit_as_of=AS_OF + 900, position_id="P2", pnl_r=0.5),
    ]
    summary2 = research.research_summary_for("S10", "12m", AS_OF + 900, [_opportunity("S10")], [], two_trades)
    assert summary2.sharpe_ratio is not None


def test_best_and_worst_month_are_identified_correctly() -> None:
    jan = 1_704_067_200  # 2024-01-01 UTC
    feb = 1_706_745_600  # 2024-02-01 UTC
    trade_legs = [
        _trade("S10", net_pnl=50.0, exit_as_of=jan, position_id="P1"),
        _trade("S10", net_pnl=-30.0, exit_as_of=feb, position_id="P2"),
    ]
    summary = research.research_summary_for("S10", "12m", feb, [_opportunity("S10")], [], trade_legs)
    assert summary.best_month == "2024-01"
    assert summary.best_month_pnl == 50.0
    assert summary.worst_month == "2024-02"
    assert summary.worst_month_pnl == -30.0


def test_max_consecutive_wins_counts_correctly() -> None:
    trade_legs = [
        _trade("S10", net_pnl=10.0, exit_as_of=AS_OF, position_id="P1"),
        _trade("S10", net_pnl=5.0, exit_as_of=AS_OF + 900, position_id="P2"),
        _trade("S10", net_pnl=-3.0, exit_as_of=AS_OF + 1800, position_id="P3"),
        _trade("S10", net_pnl=2.0, exit_as_of=AS_OF + 2700, position_id="P4"),
        _trade("S10", net_pnl=1.0, exit_as_of=AS_OF + 3600, position_id="P5"),
        _trade("S10", net_pnl=1.0, exit_as_of=AS_OF + 4500, position_id="P6"),
    ]
    summary = research.research_summary_for("S10", "12m", AS_OF + 4500, [_opportunity("S10")], [], trade_legs)
    # Sequence: win, win, loss, win, win, win -> longest winning streak is the trailing 3 wins.
    assert summary.max_consecutive_wins == 3
    assert summary.window_metrics.max_losing_streak == 1  # reused verbatim from WindowMetrics


def test_all_research_summaries_is_generic_over_43_synthetic_strategies() -> None:
    # Proves genericity directly at real production scale without paying for a 43-strategy harness
    # run -- this layer is purely a read-only, pull-based function over already-recorded data, whose
    # correctness at N=43 does not depend on how that data was produced.
    strategy_ids = [f"S{i}" for i in range(1, 44)]
    opportunities = [_opportunity(sid) for sid in strategy_ids]
    trade_legs = [_trade(sid, net_pnl=float(i), exit_as_of=AS_OF, position_id=f"P-{sid}") for i, sid in enumerate(strategy_ids, start=1)]
    summaries = research.all_research_summaries("12m", AS_OF, opportunities, [], trade_legs)
    assert len(summaries) == 43
    assert set(summaries) == set(strategy_ids)
    for sid, summary in summaries.items():
        assert summary.strategy_id == sid
        assert summary.window_metrics.n_trades == 1


def test_research_summaries_are_deterministic_across_repeated_calls() -> None:
    strategy_ids = [f"S{i}" for i in range(1, 44)]
    opportunities = [_opportunity(sid) for sid in strategy_ids]
    trade_legs = [_trade(sid, net_pnl=float(i), exit_as_of=AS_OF, position_id=f"P-{sid}") for i, sid in enumerate(strategy_ids, start=1)]
    summaries_a = research.all_research_summaries("12m", AS_OF, opportunities, [], trade_legs)
    summaries_b = research.all_research_summaries("12m", AS_OF, opportunities, [], trade_legs)
    assert summaries_a == summaries_b


def test_strategy_research_summary_rejects_non_shadow_source() -> None:
    import pytest

    from ai_trader.shadow_evidence.research import DirectionStats, StrategyResearchSummary
    from ai_trader.strategy_health.metrics import compute_window_metrics

    with pytest.raises(ValueError):
        StrategyResearchSummary(
            strategy_id="S10", source="competitive", window_metrics=compute_window_metrics([], "12m", AS_OF),
            average_r=None, sharpe_ratio=None, best_month=None, best_month_pnl=None,
            worst_month=None, worst_month_pnl=None,
            long=DirectionStats(0, None, 0.0), short=DirectionStats(0, None, 0.0), max_consecutive_wins=0,
        )


def test_strategy_research_summary_rejects_negative_max_consecutive_wins() -> None:
    import pytest

    from ai_trader.shadow_evidence.research import DirectionStats, StrategyResearchSummary
    from ai_trader.strategy_health.metrics import compute_window_metrics

    with pytest.raises(ValueError):
        StrategyResearchSummary(
            strategy_id="S10", source="shadow", window_metrics=compute_window_metrics([], "12m", AS_OF),
            average_r=None, sharpe_ratio=None, best_month=None, best_month_pnl=None,
            worst_month=None, worst_month_pnl=None,
            long=DirectionStats(0, None, 0.0), short=DirectionStats(0, None, 0.0), max_consecutive_wins=-1,
        )

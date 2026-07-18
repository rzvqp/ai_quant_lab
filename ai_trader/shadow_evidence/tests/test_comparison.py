"""Unit tests for :mod:`ai_trader.shadow_evidence.comparison` -- Phase 6.10 Implementation Checkpoint
4. Pure-function tests over hand-built ``StrategyResearchSummary`` objects.
"""

from __future__ import annotations

from ai_trader.shadow_evidence import comparison, research
from ai_trader.shadow_evidence.types import ShadowOpportunityRecord, ShadowTradeLegRecord
from ai_trader.scoring_engine.types import Recommendation
from ai_trader.signal_engine.types import Direction, SignalState
from ai_trader.simulation.portfolio_simulator import TradeRecord

AS_OF = 1_700_000_000


def _opportunity(strategy_id: str) -> ShadowOpportunityRecord:
    return ShadowOpportunityRecord(
        opportunity_id=f"{strategy_id}:XAUUSD:{AS_OF}", strategy_id=strategy_id, symbol="XAUUSD",
        as_of=AS_OF, direction=Direction.LONG, signal_state=SignalState.BUY,
        score_recommendation=Recommendation.STRONG_OPPORTUNITY, shadow_risk_decision="ALLOW",
        shadow_denied_reason=None, resulting_position_id=f"{strategy_id}:P",
    )


def _trade(strategy_id: str, net_pnl: float) -> ShadowTradeLegRecord:
    record = TradeRecord(
        client_order_id=f"SHADOW-CID-{strategy_id}|XAUUSD|{AS_OF}", strategy_id=strategy_id,
        symbol="XAUUSD", direction=Direction.LONG, entry_price=2000.0, exit_price=2000.0 + net_pnl,
        entry_as_of=AS_OF - 900, exit_as_of=AS_OF, qty=0.1, gross_pnl=net_pnl, fees=0.0,
        net_pnl=net_pnl, pnl_r=net_pnl / 10.0, holding_bars=1, mfe=0.0, mae=0.0,
    )
    return ShadowTradeLegRecord(leg=record, position_id="P1", exit_reason="TAKE_PROFIT")


def _summaries() -> dict[str, research.StrategyResearchSummary]:
    opportunities = [_opportunity("S10"), _opportunity("S21"), _opportunity("S39")]
    trade_legs = [_trade("S10", 10.0), _trade("S21", -5.0), _trade("S39", 20.0)]
    return research.all_research_summaries("12m", AS_OF, opportunities, [], trade_legs)


def test_available_metrics_is_a_fixed_deterministic_set() -> None:
    metrics = comparison.available_metrics()
    assert metrics == tuple(sorted(metrics))  # always sorted
    assert "net_pnl" in metrics and "win_rate" in metrics


def test_rank_by_orders_strategies_by_one_metric_descending() -> None:
    ranked = comparison.rank_by(_summaries(), "net_pnl", descending=True)
    assert [sid for sid, _ in ranked] == ["S39", "S10", "S21"]


def test_rank_by_ascending() -> None:
    ranked = comparison.rank_by(_summaries(), "net_pnl", descending=False)
    assert [sid for sid, _ in ranked] == ["S21", "S10", "S39"]


def test_rank_by_unknown_metric_raises() -> None:
    import pytest
    with pytest.raises(ValueError):
        comparison.rank_by(_summaries(), "not_a_real_metric")


def test_rank_by_puts_no_evidence_strategies_last_regardless_of_direction() -> None:
    summaries = _summaries()
    ranked_desc = comparison.rank_by(summaries, "sharpe_ratio", descending=True)
    ranked_asc = comparison.rank_by(summaries, "sharpe_ratio", descending=False)
    # Every strategy here has exactly 1 trade -> sharpe_ratio is always None (needs >= 2 R values) --
    # all None, so both orderings degrade to the same strategy_id tie-break, proving "None never
    # implicitly outranks anything" holds even in the degenerate all-None case.
    assert [sid for sid, _ in ranked_desc] == sorted(summaries)
    assert [sid for sid, _ in ranked_asc] == sorted(summaries)


def test_rank_by_is_deterministic_across_repeated_calls() -> None:
    summaries = _summaries()
    assert comparison.rank_by(summaries, "net_pnl") == comparison.rank_by(summaries, "net_pnl")


def test_compare_two_strategies_covers_every_metric() -> None:
    summaries = _summaries()
    result = comparison.compare(summaries["S10"], summaries["S21"])
    assert result.strategy_a == "S10" and result.strategy_b == "S21"
    assert {row.metric for row in result.rows} == set(comparison.available_metrics())
    net_pnl_row = next(row for row in result.rows if row.metric == "net_pnl")
    assert net_pnl_row.value_a == 10.0
    assert net_pnl_row.value_b == -5.0
    assert net_pnl_row.difference == 15.0


def test_compare_is_deterministic_and_row_order_is_fixed() -> None:
    summaries = _summaries()
    a = comparison.compare(summaries["S10"], summaries["S39"])
    b = comparison.compare(summaries["S10"], summaries["S39"])
    assert a == b
    assert [row.metric for row in a.rows] == list(comparison.available_metrics())


def test_export_summary_is_a_complete_plain_dict() -> None:
    summaries = _summaries()
    exported = comparison.export_summary(summaries["S10"])
    assert exported["strategy_id"] == "S10"
    assert exported["source"] == "shadow"
    assert isinstance(exported["window_metrics"], dict)
    assert isinstance(exported["long"], dict)


def test_leaderboard_ranks_by_primary_metric_and_includes_every_metric_per_row() -> None:
    board = comparison.leaderboard(_summaries(), primary_metric="net_pnl")
    assert [row["strategy_id"] for row in board] == ["S39", "S10", "S21"]
    assert [row["rank"] for row in board] == [1, 2, 3]
    assert set(comparison.available_metrics()).issubset(board[0].keys())


def test_leaderboard_is_deterministic() -> None:
    summaries = _summaries()
    assert comparison.leaderboard(summaries) == comparison.leaderboard(summaries)

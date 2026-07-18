"""Unit tests for :mod:`ai_trader.shadow_evidence.aggregation` -- Phase 6.10 Implementation
Checkpoint 2. Pure-function tests, no real market data or harness needed: hand-constructed
``ShadowOpportunityRecord``/``ShadowRejectionRecord``/``ShadowTradeLegRecord`` fixtures exercise the
generic aggregation layer directly.
"""

from __future__ import annotations

from ai_trader.scoring_engine.types import Recommendation
from ai_trader.shadow_evidence import aggregation
from ai_trader.shadow_evidence.types import (
    ShadowOpportunityRecord,
    ShadowRejectionRecord,
    ShadowTradeLegRecord,
)
from ai_trader.signal_engine.types import Direction, SignalState
from ai_trader.simulation.portfolio_simulator import TradeRecord

AS_OF = 1_700_000_000


def _opportunity(strategy_id: str, decision: str, as_of: int = AS_OF, position_id: str | None = None) -> ShadowOpportunityRecord:
    return ShadowOpportunityRecord(
        opportunity_id=f"{strategy_id}:XAUUSD:{as_of}", strategy_id=strategy_id, symbol="XAUUSD",
        as_of=as_of, direction=Direction.LONG, signal_state=SignalState.BUY,
        score_recommendation=Recommendation.STRONG_OPPORTUNITY, shadow_risk_decision=decision,
        shadow_denied_reason=None if decision == "ALLOW" else "FILTER_SPREAD",
        resulting_position_id=position_id,
    )


def _rejection(strategy_id: str, reason: str, as_of: int = AS_OF) -> ShadowRejectionRecord:
    return ShadowRejectionRecord(
        rejection_id=f"{strategy_id}:XAUUSD:{as_of}:REJ", strategy_id=strategy_id, symbol="XAUUSD",
        as_of=as_of, direction=Direction.LONG, denied_reason_code=reason, denied_detail=None,
    )


def _trade(strategy_id: str, net_pnl: float, exit_as_of: int, position_id: str = "P1", pnl_r: float | None = 1.0) -> ShadowTradeLegRecord:
    record = TradeRecord(
        client_order_id=f"SHADOW-CID-{strategy_id}|XAUUSD|{exit_as_of}", strategy_id=strategy_id,
        symbol="XAUUSD", direction=Direction.LONG, entry_price=2000.0, exit_price=2000.0 + net_pnl,
        entry_as_of=exit_as_of - 900, exit_as_of=exit_as_of, qty=0.1, gross_pnl=net_pnl, fees=0.0,
        net_pnl=net_pnl, pnl_r=pnl_r, holding_bars=1, mfe=0.0, mae=0.0,
    )
    return ShadowTradeLegRecord(leg=record, position_id=position_id, exit_reason="TAKE_PROFIT")


def test_strategy_ids_observed_is_derived_from_data_not_hardcoded() -> None:
    opportunities = [_opportunity("S10", "ALLOW"), _opportunity("S21", "DENY"), _opportunity("S10", "DENY")]
    assert aggregation.strategy_ids_observed(opportunities) == frozenset({"S10", "S21"})


def test_summary_for_a_strategy_with_no_trades_is_honest_not_fabricated() -> None:
    summary = aggregation.summary_for("S10", "12m", AS_OF, [_opportunity("S10", "DENY")], [], [])
    assert summary.strategy_id == "S10"
    assert summary.source == "shadow"
    assert summary.window_metrics.n_trades == 0
    assert summary.window_metrics.win_rate is None
    assert summary.n_opportunities == 1
    assert summary.n_shadow_denied_by_reason == {}


def test_summary_for_computes_real_statistics_from_shadow_trade_legs() -> None:
    trade_legs = [
        _trade("S10", net_pnl=10.0, exit_as_of=AS_OF, position_id="P1"),
        _trade("S10", net_pnl=-5.0, exit_as_of=AS_OF + 900, position_id="P2"),
    ]
    opportunities = [_opportunity("S10", "ALLOW", position_id="P1"), _opportunity("S10", "ALLOW", position_id="P2")]
    summary = aggregation.summary_for("S10", "12m", AS_OF + 900, opportunities, [], trade_legs)
    assert summary.window_metrics.n_trades == 2
    assert summary.window_metrics.net_pnl == 5.0
    assert summary.window_metrics.win_rate == 0.5


def test_summary_for_filters_strictly_by_strategy_id() -> None:
    # Trades/opportunities/rejections from OTHER strategies must never leak into this strategy's own
    # summary -- the generic-isolation property, checked at the aggregation layer too.
    trade_legs = [
        _trade("S10", net_pnl=10.0, exit_as_of=AS_OF, position_id="P1"),
        _trade("S21", net_pnl=-999.0, exit_as_of=AS_OF, position_id="P9"),
    ]
    opportunities = [_opportunity("S10", "ALLOW", position_id="P1"), _opportunity("S21", "ALLOW", position_id="P9")]
    rejections = [_rejection("S21", "FILTER_SPREAD")]
    summary = aggregation.summary_for("S10", "12m", AS_OF, opportunities, rejections, trade_legs)
    assert summary.window_metrics.n_trades == 1
    assert summary.window_metrics.net_pnl == 10.0
    assert summary.n_opportunities == 1
    assert summary.n_shadow_denied_by_reason == {}


def test_summary_for_counts_denied_reasons_by_strategy() -> None:
    rejections = [
        _rejection("S10", "FILTER_SPREAD"), _rejection("S10", "FILTER_SPREAD"),
        _rejection("S10", "LIMIT_MAX_PER_SYMBOL"),
    ]
    opportunities = [_opportunity("S10", "DENY") for _ in range(3)]
    summary = aggregation.summary_for("S10", "12m", AS_OF, opportunities, rejections, [])
    assert summary.n_shadow_denied_by_reason == {"FILTER_SPREAD": 2, "LIMIT_MAX_PER_SYMBOL": 1}


def test_all_summaries_is_generic_over_n_strategies() -> None:
    # Proves genericity directly: nothing in aggregation.py names S10/S21/S39 specifically.
    opportunities = [_opportunity(sid, "ALLOW", position_id=f"P-{sid}") for sid in ("S10", "S21", "S39")]
    trade_legs = [_trade(sid, net_pnl=1.0, exit_as_of=AS_OF, position_id=f"P-{sid}") for sid in ("S10", "S21", "S39")]
    summaries = aggregation.all_summaries("12m", AS_OF, opportunities, [], trade_legs)
    assert set(summaries) == {"S10", "S21", "S39"}
    for sid, summary in summaries.items():
        assert summary.strategy_id == sid
        assert summary.window_metrics.n_trades == 1


def test_all_summaries_empty_input_returns_empty_dict() -> None:
    assert aggregation.all_summaries("12m", AS_OF, [], [], []) == {}


def test_shadow_strategy_summary_rejects_non_shadow_source() -> None:
    import pytest

    from ai_trader.shadow_evidence.types import ShadowStrategySummary
    from ai_trader.strategy_health.metrics import compute_window_metrics

    with pytest.raises(ValueError):
        ShadowStrategySummary(
            strategy_id="S10", source="competitive", window_metrics=compute_window_metrics([], "12m", AS_OF),
            n_opportunities=0, n_shadow_denied_by_reason={},
        )


def test_shadow_strategy_summary_rejects_negative_n_opportunities() -> None:
    import pytest

    from ai_trader.shadow_evidence.types import ShadowStrategySummary
    from ai_trader.strategy_health.metrics import compute_window_metrics

    with pytest.raises(ValueError):
        ShadowStrategySummary(
            strategy_id="S10", source="shadow", window_metrics=compute_window_metrics([], "12m", AS_OF),
            n_opportunities=-1, n_shadow_denied_by_reason={},
        )

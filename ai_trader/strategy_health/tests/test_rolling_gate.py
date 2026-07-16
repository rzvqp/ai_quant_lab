"""Unit tests for the Phase 6.9 Rolling Health Gate -- a thin wrapper, so these tests focus on the
wrapping contract itself (matches ``evaluate_strategy_health`` exactly, extracts only ``ACTIVE`` ids)
rather than re-testing the underlying scoring methodology (already covered by
``test_evaluator.py``/``test_scoring.py``/``test_classifier.py``)."""

from __future__ import annotations

from ai_trader.strategy_health.evaluator import evaluate_strategy_health
from ai_trader.strategy_health.rolling_gate import active_strategy_ids_at, health_reports_at
from ai_trader.strategy_health.types import ClosedTrade, HealthState

AS_OF = 1_700_000_000
_DAY = 86400


def trade(sid: str, days_ago: int, net_pnl: float, pnl_r: float | None = None) -> ClosedTrade:
    return ClosedTrade(strategy_id=sid, exit_as_of=AS_OF - days_ago * _DAY, net_pnl=net_pnl, pnl_r=pnl_r, holding_bars=10)


def test_health_reports_at_matches_evaluate_strategy_health_exactly() -> None:
    trades_by_strategy = {
        "STRONG": [trade("STRONG", d + 1, 10.0, pnl_r=2.0) for d in range(15)],
        "WEAK": [trade("WEAK", d + 1, -10.0, pnl_r=-2.0) for d in range(15)],
        "EMPTY": [],
    }
    direct = evaluate_strategy_health(trades_by_strategy, AS_OF)
    via_gate = health_reports_at(trades_by_strategy, AS_OF)
    assert direct == via_gate


def test_active_ids_extracts_only_active_state() -> None:
    trades_by_strategy = {
        "STRONG": [trade("STRONG", d + 1, 10.0, pnl_r=2.0) for d in range(15)],
        "WEAK": [trade("WEAK", d + 1, -10.0, pnl_r=-2.0) for d in range(15)],
        "EMPTY": [],
    }
    reports = health_reports_at(trades_by_strategy, AS_OF)
    active_ids = active_strategy_ids_at(trades_by_strategy, AS_OF)
    assert active_ids == frozenset(sid for sid, r in reports.items() if r.state is HealthState.ACTIVE)
    assert "WEAK" not in active_ids
    assert "EMPTY" not in active_ids  # WATCHLIST for lack of evidence, never ACTIVE by default


def test_no_strategies_at_all_yields_empty_active_set() -> None:
    assert active_strategy_ids_at({}, AS_OF) == frozenset()

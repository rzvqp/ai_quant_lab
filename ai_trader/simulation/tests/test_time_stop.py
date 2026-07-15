"""Unit tests for the generic time-stop overlay (Phase 6.8 Wave B). Pure-function tests only here --
the real end-to-end proof (a genuine time-stop firing through the full composed pipeline) lives in
``ai_trader/strategy_runtime/tests/test_checkpoint2_end_to_end.py``, mirroring
``test_s1_end_to_end.py``'s own precedent of proving the mechanism against real data, not just
fixtures."""

from __future__ import annotations

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.types import Decision
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.portfolio_simulator import Position
from ai_trader.simulation.time_stop import build_time_stop_decision, positions_due_for_time_stop


def make_position(
    symbol: str = "XAUUSD", strategy_id: str = "S16", opened_bar_index: int = 10,
    direction: Direction = Direction.LONG, size: float = 1.0, avg_entry: float = 2000.0,
) -> Position:
    return Position(
        symbol=symbol, strategy_id=strategy_id, direction=direction, size=size,
        avg_entry=avg_entry, opened_as_of=0, opened_bar_index=opened_bar_index,
    )


class TestPositionsDueForTimeStop:
    def test_position_at_exact_limit_is_due(self) -> None:
        pos = make_position(opened_bar_index=10)
        due = positions_due_for_time_stop({"XAUUSD": pos}, bar_index=34, time_stop_bars_by_strategy={"S16": 24})
        assert due == (pos,)

    def test_position_under_limit_is_not_due(self) -> None:
        pos = make_position(opened_bar_index=10)
        due = positions_due_for_time_stop({"XAUUSD": pos}, bar_index=33, time_stop_bars_by_strategy={"S16": 24})
        assert due == ()

    def test_strategy_with_no_declared_limit_never_matches(self) -> None:
        """S1 (rr2-only, no time-stop) must never be force-closed regardless of age -- opting in is
        per-strategy and additive."""
        pos = make_position(strategy_id="S1", opened_bar_index=0)
        due = positions_due_for_time_stop({"XAUUSD": pos}, bar_index=10_000, time_stop_bars_by_strategy={"S16": 24})
        assert due == ()

    def test_multiple_positions_only_matured_ones_are_due(self) -> None:
        young = make_position(symbol="XAUUSD", strategy_id="S16", opened_bar_index=30)
        old = make_position(symbol="EURUSD", strategy_id="S17", opened_bar_index=0)
        due = positions_due_for_time_stop(
            {"XAUUSD": young, "EURUSD": old}, bar_index=40,
            time_stop_bars_by_strategy={"S16": 24, "S17": 24},
        )
        assert due == (old,)


class TestBuildTimeStopDecision:
    def _risk_manager(self) -> RiskManager:
        rm = RiskManager(RiskConfig())
        rm.configure(portfolio=None)  # type: ignore[arg-type]
        return rm

    def test_decision_is_reduce_only_allow_matching_position(self) -> None:
        pos = make_position(direction=Direction.LONG, size=2.5, avg_entry=2010.0, strategy_id="S16")
        decision = build_time_stop_decision(pos, as_of=1000, bar_index=40, risk_manager=self._risk_manager(), risk_config=RiskConfig())
        assert decision.decision is Decision.ALLOW
        assert decision.direction is Direction.LONG
        assert decision.strategy_id == "S16"
        assert decision.symbol == "XAUUSD"
        assert decision.constraints is not None
        assert decision.constraints.reduce_only is True
        assert decision.sizing is not None
        assert decision.sizing.size_units == 2.5

    def test_max_slippage_uses_the_same_formula_as_the_real_constraint_builder(self) -> None:
        cfg = RiskConfig()
        pos = make_position(avg_entry=2000.0)
        decision = build_time_stop_decision(pos, as_of=1000, bar_index=40, risk_manager=self._risk_manager(), risk_config=cfg)
        assert decision.constraints is not None
        assert decision.constraints.max_slippage == 2000.0 * cfg.constraints.max_slippage_pct

    def test_decision_id_is_deterministic_and_idempotent_per_bar(self) -> None:
        pos = make_position()
        d1 = build_time_stop_decision(pos, as_of=1000, bar_index=40, risk_manager=self._risk_manager(), risk_config=RiskConfig())
        d2 = build_time_stop_decision(pos, as_of=1000, bar_index=40, risk_manager=self._risk_manager(), risk_config=RiskConfig())
        assert d1.decision_id == d2.decision_id

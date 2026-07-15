"""Unit tests for the generic trailing-stop overlay (Phase 6.8 Wave B)."""

from __future__ import annotations

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.types import Decision
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.portfolio_simulator import Position
from ai_trader.simulation.trailing_stop import (
    best_favorable_price_including_bar,
    build_trailing_stop_decision,
    positions_due_for_trailing_stop,
    trailing_stop_level,
)
from ai_trader.simulation.types import Bar


def make_position(
    symbol: str = "XAUUSD", strategy_id: str = "S4", direction: Direction = Direction.LONG,
    size: float = 1.0, avg_entry: float = 2000.0, mfe: float = 0.0,
) -> Position:
    return Position(
        symbol=symbol, strategy_id=strategy_id, direction=direction, size=size,
        avg_entry=avg_entry, opened_as_of=0, opened_bar_index=0, mfe=mfe,
    )


def bar(symbol: str, high: float, low: float, close: float) -> Bar:
    return Bar(symbol=symbol, timeframe="M15", ts_open=0, ts_close=900, open=close, high=high, low=low, close=close, volume=1.0)


class TestBestFavorablePrice:
    def test_long_uses_the_higher_of_prior_mfe_and_this_bars_high(self) -> None:
        pos = make_position(direction=Direction.LONG, avg_entry=2000.0, mfe=10.0)  # prior best = 2010
        assert best_favorable_price_including_bar(pos, bar_high=2005.0, bar_low=1995.0) == 2010.0
        assert best_favorable_price_including_bar(pos, bar_high=2020.0, bar_low=1995.0) == 2020.0

    def test_short_uses_the_lower_of_prior_mfe_and_this_bars_low(self) -> None:
        pos = make_position(direction=Direction.SHORT, avg_entry=2000.0, mfe=10.0)  # prior best = 1990
        assert best_favorable_price_including_bar(pos, bar_high=2005.0, bar_low=1995.0) == 1990.0
        assert best_favorable_price_including_bar(pos, bar_high=2005.0, bar_low=1980.0) == 1980.0


class TestTrailingStopLevel:
    def test_long_level_trails_below_the_best_price(self) -> None:
        pos = make_position(direction=Direction.LONG, avg_entry=2000.0, mfe=20.0)  # best = 2020
        level = trailing_stop_level(pos, entry_atr=4.0, atr_mult=1.5, bar_high=2015.0, bar_low=2010.0)
        assert level == 2020.0 - 1.5 * 4.0

    def test_short_level_trails_above_the_best_price(self) -> None:
        pos = make_position(direction=Direction.SHORT, avg_entry=2000.0, mfe=20.0)  # best = 1980
        level = trailing_stop_level(pos, entry_atr=4.0, atr_mult=1.5, bar_high=1990.0, bar_low=1985.0)
        assert level == 1980.0 + 1.5 * 4.0


class TestPositionsDueForTrailingStop:
    def test_strategy_without_declared_mult_never_matches(self) -> None:
        pos = make_position(strategy_id="S1", direction=Direction.LONG, avg_entry=2000.0, mfe=20.0)
        due = positions_due_for_trailing_stop(
            {"XAUUSD": pos}, {"XAUUSD": bar("XAUUSD", 2005.0, 1900.0, 1950.0)},
            {"XAUUSD": 4.0}, atr_mult_by_strategy={"S4": 1.5},
        )
        assert due == ()

    def test_missing_entry_atr_never_matches(self) -> None:
        pos = make_position(strategy_id="S4", direction=Direction.LONG, avg_entry=2000.0, mfe=20.0)
        due = positions_due_for_trailing_stop(
            {"XAUUSD": pos}, {"XAUUSD": bar("XAUUSD", 2005.0, 1900.0, 1950.0)},
            entry_atr_by_symbol={}, atr_mult_by_strategy={"S4": 1.5},
        )
        assert due == ()

    def test_long_position_breached_when_bar_low_crosses_the_trail_level(self) -> None:
        pos = make_position(strategy_id="S4", direction=Direction.LONG, avg_entry=2000.0, mfe=20.0)
        # best=2020, trail=2020-1.5*4=2014; bar low of 2010 breaches it.
        due = positions_due_for_trailing_stop(
            {"XAUUSD": pos}, {"XAUUSD": bar("XAUUSD", 2022.0, 2010.0, 2015.0)},
            {"XAUUSD": 4.0}, atr_mult_by_strategy={"S4": 1.5},
        )
        assert due == (pos,)

    def test_long_position_not_breached_when_bar_low_stays_above_the_trail_level(self) -> None:
        pos = make_position(strategy_id="S4", direction=Direction.LONG, avg_entry=2000.0, mfe=20.0)
        due = positions_due_for_trailing_stop(
            {"XAUUSD": pos}, {"XAUUSD": bar("XAUUSD", 2022.0, 2018.0, 2020.0)},
            {"XAUUSD": 4.0}, atr_mult_by_strategy={"S4": 1.5},
        )
        assert due == ()


class TestBuildTrailingStopDecision:
    def test_decision_is_reduce_only_allow_matching_position(self) -> None:
        rm = RiskManager(RiskConfig())
        rm.configure(portfolio=None)  # type: ignore[arg-type]
        pos = make_position(strategy_id="S4", direction=Direction.LONG, size=2.0, avg_entry=2000.0)
        decision = build_trailing_stop_decision(pos, as_of=1000, risk_manager=rm, risk_config=RiskConfig())
        assert decision.decision is Decision.ALLOW
        assert decision.direction is Direction.LONG
        assert decision.strategy_id == "S4"
        assert decision.constraints is not None and decision.constraints.reduce_only is True
        assert decision.sizing is not None and decision.sizing.size_units == 2.0

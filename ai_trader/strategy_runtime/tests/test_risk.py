"""Tests for risk.py's stop-floor/target helpers."""

from __future__ import annotations

from ai_trader.strategy_runtime import risk


def test_executable_stop_floor_uses_tick_floors_when_atr_missing() -> None:
    floor = risk.executable_stop_floor(spread_ticks=1.0, tick=0.1, atr=None)
    assert floor == max(2 * 1.0 * 0.1, 5 * 0.1)


def test_executable_stop_floor_atr_can_dominate() -> None:
    floor = risk.executable_stop_floor(spread_ticks=1.0, tick=0.1, atr=100.0)
    assert floor == 10.0  # 0.10 * atr dominates the tick floors


def test_widen_stop_to_floor_never_tightens() -> None:
    # raw stop already wider than the floor -- returned unchanged.
    stop = risk.widen_stop_to_floor(entry=100.0, raw_stop=90.0, is_long=True, floor=1.0)
    assert stop == 90.0


def test_widen_stop_to_floor_widens_a_tight_stop() -> None:
    stop = risk.widen_stop_to_floor(entry=100.0, raw_stop=99.9, is_long=True, floor=1.0)
    assert stop == 99.0  # widened to entry - floor
    stop_short = risk.widen_stop_to_floor(entry=100.0, raw_stop=100.1, is_long=False, floor=1.0)
    assert stop_short == 101.0


def test_rr_target_long_and_short() -> None:
    assert risk.rr_target(entry=100.0, stop=98.0, is_long=True, rr=2.0) == 104.0
    assert risk.rr_target(entry=100.0, stop=102.0, is_long=False, rr=2.0) == 96.0


def test_risk_r_of() -> None:
    assert risk.risk_r_of(entry=100.0, exit_price=104.0, stop=98.0, is_long=True) == 2.0
    assert risk.risk_r_of(entry=100.0, exit_price=96.0, stop=102.0, is_long=False) == 2.0
    assert risk.risk_r_of(entry=100.0, exit_price=104.0, stop=100.0, is_long=True) is None  # degenerate stop

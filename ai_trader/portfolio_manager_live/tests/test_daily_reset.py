"""Tests for `reset_if_new_day` (Demo Readiness precondition #11 fix): `PortfolioDailyState`'s own
docstring names a Phase-9 owner that was never built -- nothing resets `trades_opened_today`/
`daily_heat_used_pct`/`session_heat_used_pct` across a UTC calendar-day boundary."""

from __future__ import annotations

from ai_trader.portfolio_manager_live.daily_reset import reset_if_new_day
from ai_trader.portfolio_manager_live.types import PortfolioDailyState

_DAY_SECONDS = 86_400
_DAY_0 = 1_700_000_000 - (1_700_000_000 % _DAY_SECONDS)  # aligned to a UTC day boundary for clean math


def test_same_day_returns_the_identical_state_unchanged() -> None:
    state = PortfolioDailyState(
        as_of=_DAY_0, trades_opened_today=3, daily_heat_used_pct=0.05,
        session_heat_used_pct={"LONDON": 0.02},
    )
    result = reset_if_new_day(state, _DAY_0 + 3600)  # one hour later, same UTC day
    assert result is state


def test_new_day_returns_a_fresh_state() -> None:
    state = PortfolioDailyState(
        as_of=_DAY_0, trades_opened_today=5, daily_heat_used_pct=0.15,
        session_heat_used_pct={"LONDON": 0.10, "NY": 0.05},
    )
    next_day = _DAY_0 + _DAY_SECONDS + 60
    result = reset_if_new_day(state, next_day)
    assert result.as_of == next_day
    assert result.trades_opened_today == 0
    assert result.daily_heat_used_pct == 0.0
    assert result.session_heat_used_pct == {}


def test_backward_or_stale_as_of_never_resets() -> None:
    """Fail-safe: an out-of-order or stale `as_of` must never wipe today's already-accumulated heat --
    only a genuine forward move into a new UTC day resets anything."""
    state = PortfolioDailyState(as_of=_DAY_0 + _DAY_SECONDS, trades_opened_today=2, daily_heat_used_pct=0.03)
    result = reset_if_new_day(state, _DAY_0)  # a full day EARLIER than the state's own as_of
    assert result is state

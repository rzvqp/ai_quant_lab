"""Tests for the state-set invariants in :mod:`ai_trader.signal_engine.types`."""

from __future__ import annotations

from ai_trader.signal_engine.types import (
    ACTIONABLE_STATES,
    NON_ACTIONABLE_STATES,
    READY_STATES,
    SignalState,
)


class TestStateSetInvariants:
    def test_every_state_is_in_exactly_one_of_the_three_sets(self) -> None:
        for state in SignalState:
            membership = [state in s for s in (ACTIONABLE_STATES, READY_STATES, NON_ACTIONABLE_STATES)]
            assert sum(membership) == 1, f"{state} must belong to exactly one state-set"

    def test_actionable_states_are_buy_and_sell(self) -> None:
        assert ACTIONABLE_STATES == {SignalState.BUY, SignalState.SELL}

    def test_ready_states_are_long_ready_and_short_ready(self) -> None:
        assert READY_STATES == {SignalState.LONG_READY, SignalState.SHORT_READY}

    def test_nine_states_total(self) -> None:
        assert len(list(SignalState)) == 9

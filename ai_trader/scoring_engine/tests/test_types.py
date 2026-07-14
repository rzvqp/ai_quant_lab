"""Tests for the state-set invariants in :mod:`ai_trader.scoring_engine.types`."""

from __future__ import annotations

from ai_trader.scoring_engine.types import ACTIONABLE_STATES, NON_ACTIONABLE_STATES, READY_STATES
from ai_trader.signal_engine.types import SignalState


class TestStateSetInvariants:
    def test_every_state_is_in_exactly_one_of_the_three_named_sets_or_wait_confirmation(self) -> None:
        # WAIT_CONFIRMATION is deliberately in none of the three (it gets its own WATCH treatment in
        # aggregator.recommendation_for, alongside READY_STATES).
        named = ACTIONABLE_STATES | READY_STATES | NON_ACTIONABLE_STATES
        for state in SignalState:
            if state is SignalState.WAIT_CONFIRMATION:
                assert state not in named
            else:
                assert state in named

    def test_non_actionable_states_match_the_schemas_own_allof_list(self) -> None:
        """SCORING_SCHEMA.json's allOf rule names exactly these four states."""
        assert NON_ACTIONABLE_STATES == {
            SignalState.NEED_CONTEXT, SignalState.BLOCKED, SignalState.INVALID, SignalState.NO_SIGNAL,
        }

    def test_actionable_states_are_buy_and_sell(self) -> None:
        assert ACTIONABLE_STATES == {SignalState.BUY, SignalState.SELL}

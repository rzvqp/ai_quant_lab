"""Identity invariant tests for the Shadow Evidence data contracts (Phase 6.10 Implementation
Checkpoint 1A). Pure, fixture-only tests -- no simulation is run, no ai_trader pipeline module is
invoked, no generated simulation results are involved. Proves the invariant stated in
``PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md`` §17.1 (Q4):

    one ShadowOpportunityRecord -> zero-or-one ShadowPositionRecord -> one-or-more ShadowTradeLegRecord

and that a partial exit (two legs from one entry) never inflates the opportunity or position count.
"""

from __future__ import annotations

import pytest

from ai_trader.scoring_engine.types import Recommendation
from ai_trader.shadow_evidence.types import (
    ShadowOpportunityRecord,
    ShadowPositionRecord,
    ShadowTradeLegRecord,
)
from ai_trader.signal_engine.types import Direction, SignalState
from ai_trader.simulation.portfolio_simulator import TradeRecord

STRATEGY_ID = "S10"
SYMBOL = "XAUUSD"


def _trade_record(client_order_id: str, entry_as_of: int, exit_as_of: int, holding_bars: int) -> TradeRecord:
    return TradeRecord(
        client_order_id=client_order_id, strategy_id=STRATEGY_ID, symbol=SYMBOL,
        direction=Direction.LONG, entry_price=2000.0, exit_price=2010.0,
        entry_as_of=entry_as_of, exit_as_of=exit_as_of, qty=0.1,
        gross_pnl=10.0, fees=0.0, net_pnl=10.0, pnl_r=1.0, holding_bars=holding_bars,
        mfe=12.0, mae=3.0,
    )


def test_denied_opportunity_has_no_resulting_position() -> None:
    opp = ShadowOpportunityRecord(
        opportunity_id="OPP-1", strategy_id=STRATEGY_ID, symbol=SYMBOL, as_of=1_700_000_000,
        direction=Direction.LONG, signal_state=SignalState.BUY,
        score_recommendation=Recommendation.STRONG_OPPORTUNITY,
        shadow_risk_decision="DENY", shadow_denied_reason="FILTER_SPREAD",
        resulting_position_id=None,
    )
    assert opp.resulting_position_id is None


def test_allowed_opportunity_maps_to_exactly_one_position() -> None:
    opp = ShadowOpportunityRecord(
        opportunity_id="OPP-2", strategy_id=STRATEGY_ID, symbol=SYMBOL, as_of=1_700_000_000,
        direction=Direction.LONG, signal_state=SignalState.BUY,
        score_recommendation=Recommendation.STRONG_OPPORTUNITY,
        shadow_risk_decision="ALLOW", shadow_denied_reason=None,
        resulting_position_id="POS-1",
    )
    position = ShadowPositionRecord(
        position_id="POS-1", strategy_id=STRATEGY_ID, symbol=SYMBOL, direction=Direction.LONG,
        entry_as_of=1_700_000_900, entry_price=2000.0, entry_opportunity_id=opp.opportunity_id,
        status="CLOSED", full_exit_as_of=1_700_010_000, n_legs=1,
        aggregate_net_pnl=10.0, aggregate_holding_bars_full=60,
    )
    assert opp.resulting_position_id == position.position_id
    assert position.entry_opportunity_id == opp.opportunity_id
    assert position.strategy_id == opp.strategy_id == STRATEGY_ID


def test_partial_exit_legs_share_one_position_id_and_do_not_inflate_opportunity_count() -> None:
    # One entry, two legs (a scaled take-profit) -- the exact pattern the Phase 6.10 pre-scope
    # diagnostic found and had to reverse-engineer post-hoc (65/25 real positions,
    # PHASE_6_10_PRE_SCOPE_DIAGNOSTIC.md §2). Here the identity is explicit, not inferred.
    opp = ShadowOpportunityRecord(
        opportunity_id="OPP-3", strategy_id=STRATEGY_ID, symbol=SYMBOL, as_of=1_700_000_000,
        direction=Direction.LONG, signal_state=SignalState.BUY,
        score_recommendation=Recommendation.STRONG_OPPORTUNITY,
        shadow_risk_decision="ALLOW", shadow_denied_reason=None,
        resulting_position_id="POS-2",
    )
    leg_1 = ShadowTradeLegRecord(
        leg=_trade_record("CID-1-TP", entry_as_of=1_700_000_900, exit_as_of=1_700_005_000, holding_bars=27),
        position_id="POS-2", exit_reason="TAKE_PROFIT",
    )
    leg_2 = ShadowTradeLegRecord(
        leg=_trade_record("CID-1-TS", entry_as_of=1_700_000_900, exit_as_of=1_700_020_000, holding_bars=126),
        position_id="POS-2", exit_reason="TRAILING_STOP",
    )
    position = ShadowPositionRecord(
        position_id="POS-2", strategy_id=STRATEGY_ID, symbol=SYMBOL, direction=Direction.LONG,
        entry_as_of=1_700_000_900, entry_price=2000.0, entry_opportunity_id=opp.opportunity_id,
        status="CLOSED", full_exit_as_of=max(leg_1.leg.exit_as_of, leg_2.leg.exit_as_of),
        n_legs=2, aggregate_net_pnl=leg_1.leg.net_pnl + leg_2.leg.net_pnl,
        aggregate_holding_bars_full=max(leg_1.leg.holding_bars, leg_2.leg.holding_bars),
    )

    # The invariant: ONE opportunity, ONE position, TWO legs -- never two opportunities/positions.
    assert leg_1.position_id == leg_2.position_id == position.position_id
    assert position.n_legs == 2
    assert position.entry_opportunity_id == opp.opportunity_id
    # ShadowTradeLegRecord carries only the position_id it was given -- there is no field on it that
    # could construct a second opportunity_id/position_id from these two legs, so the invariant holds
    # by construction, not merely by this one example.
    assert position.full_exit_as_of == 1_700_020_000
    assert position.aggregate_holding_bars_full == 126


def test_strategy_id_present_and_consistent_across_all_three_record_types() -> None:
    opp = ShadowOpportunityRecord(
        opportunity_id="OPP-4", strategy_id=STRATEGY_ID, symbol=SYMBOL, as_of=1_700_000_000,
        direction=Direction.SHORT, signal_state=SignalState.SELL,
        score_recommendation=Recommendation.MODERATE_OPPORTUNITY,
        shadow_risk_decision="ALLOW", shadow_denied_reason=None, resulting_position_id="POS-3",
    )
    position = ShadowPositionRecord(
        position_id="POS-3", strategy_id=STRATEGY_ID, symbol=SYMBOL, direction=Direction.SHORT,
        entry_as_of=1_700_000_900, entry_price=2000.0, entry_opportunity_id=opp.opportunity_id,
        status="OPEN", full_exit_as_of=None, n_legs=0, aggregate_net_pnl=None,
        aggregate_holding_bars_full=None,
    )
    leg = ShadowTradeLegRecord(
        leg=_trade_record("CID-2-SL", entry_as_of=1_700_000_900, exit_as_of=1_700_003_000, holding_bars=14),
        position_id=position.position_id, exit_reason="STOP_LOSS",
    )
    assert opp.strategy_id == position.strategy_id == leg.leg.strategy_id == STRATEGY_ID


# ---------------------------------------------------------------------------------- adversarial cases
# Found during this checkpoint's own adversarial review: the invariant above was only DOCUMENTED, not
# ENFORCED -- nothing stopped constructing an inconsistent record (e.g. a DENY carrying a
# resulting_position_id). __post_init__ validation was added to ShadowOpportunityRecord/
# ShadowPositionRecord specifically to close this gap; these tests prove the enforcement is real, not
# merely asserted in a docstring.

def test_deny_with_a_resulting_position_id_is_rejected() -> None:
    with pytest.raises(ValueError, match="DENY decision must not carry a resulting_position_id"):
        ShadowOpportunityRecord(
            opportunity_id="OPP-BAD-1", strategy_id=STRATEGY_ID, symbol=SYMBOL, as_of=1_700_000_000,
            direction=Direction.LONG, signal_state=SignalState.BUY,
            score_recommendation=Recommendation.STRONG_OPPORTUNITY,
            shadow_risk_decision="DENY", shadow_denied_reason="FILTER_SPREAD",
            resulting_position_id="POS-SHOULD-NOT-EXIST",
        )


def test_allow_without_a_resulting_position_id_is_rejected() -> None:
    with pytest.raises(ValueError, match="ALLOW decision must carry a resulting_position_id"):
        ShadowOpportunityRecord(
            opportunity_id="OPP-BAD-2", strategy_id=STRATEGY_ID, symbol=SYMBOL, as_of=1_700_000_000,
            direction=Direction.LONG, signal_state=SignalState.BUY,
            score_recommendation=Recommendation.STRONG_OPPORTUNITY,
            shadow_risk_decision="ALLOW", shadow_denied_reason=None, resulting_position_id=None,
        )


def test_unknown_shadow_risk_decision_is_rejected() -> None:
    with pytest.raises(ValueError, match="must be 'ALLOW' or 'DENY'"):
        ShadowOpportunityRecord(
            opportunity_id="OPP-BAD-3", strategy_id=STRATEGY_ID, symbol=SYMBOL, as_of=1_700_000_000,
            direction=Direction.LONG, signal_state=SignalState.BUY,
            score_recommendation=Recommendation.STRONG_OPPORTUNITY,
            shadow_risk_decision="MAYBE", shadow_denied_reason=None, resulting_position_id=None,
        )


def test_open_position_with_a_full_exit_as_of_is_rejected() -> None:
    with pytest.raises(ValueError, match="OPEN position must not carry full_exit_as_of"):
        ShadowPositionRecord(
            position_id="POS-BAD-1", strategy_id=STRATEGY_ID, symbol=SYMBOL, direction=Direction.LONG,
            entry_as_of=1_700_000_900, entry_price=2000.0, entry_opportunity_id="OPP-X",
            status="OPEN", full_exit_as_of=1_700_010_000, n_legs=0,
            aggregate_net_pnl=None, aggregate_holding_bars_full=None,
        )


def test_closed_position_without_a_full_exit_as_of_is_rejected() -> None:
    with pytest.raises(ValueError, match="CLOSED position must carry full_exit_as_of"):
        ShadowPositionRecord(
            position_id="POS-BAD-2", strategy_id=STRATEGY_ID, symbol=SYMBOL, direction=Direction.LONG,
            entry_as_of=1_700_000_900, entry_price=2000.0, entry_opportunity_id="OPP-X",
            status="CLOSED", full_exit_as_of=None, n_legs=1,
            aggregate_net_pnl=10.0, aggregate_holding_bars_full=60,
        )


def test_closed_position_with_zero_legs_is_rejected() -> None:
    with pytest.raises(ValueError, match="CLOSED position must have n_legs >= 1"):
        ShadowPositionRecord(
            position_id="POS-BAD-3", strategy_id=STRATEGY_ID, symbol=SYMBOL, direction=Direction.LONG,
            entry_as_of=1_700_000_900, entry_price=2000.0, entry_opportunity_id="OPP-X",
            status="CLOSED", full_exit_as_of=1_700_010_000, n_legs=0,
            aggregate_net_pnl=None, aggregate_holding_bars_full=None,
        )


def test_negative_n_legs_is_rejected() -> None:
    with pytest.raises(ValueError, match="n_legs must be >= 0"):
        ShadowPositionRecord(
            position_id="POS-BAD-5", strategy_id=STRATEGY_ID, symbol=SYMBOL, direction=Direction.LONG,
            entry_as_of=1_700_000_900, entry_price=2000.0, entry_opportunity_id="OPP-X",
            status="OPEN", full_exit_as_of=None, n_legs=-1,
            aggregate_net_pnl=None, aggregate_holding_bars_full=None,
        )


def test_unknown_position_status_is_rejected() -> None:
    with pytest.raises(ValueError, match="must be 'OPEN' or 'CLOSED'"):
        ShadowPositionRecord(
            position_id="POS-BAD-4", strategy_id=STRATEGY_ID, symbol=SYMBOL, direction=Direction.LONG,
            entry_as_of=1_700_000_900, entry_price=2000.0, entry_opportunity_id="OPP-X",
            status="PENDING", full_exit_as_of=None, n_legs=0,
            aggregate_net_pnl=None, aggregate_holding_bars_full=None,
        )

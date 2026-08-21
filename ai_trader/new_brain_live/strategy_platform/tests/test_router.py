"""`StrategyRouter` -- eligibility (instrument/regime), REGIME_INDEPENDENT, dispatch-only (never
decides profitability itself), and reuse of the REAL `ve_brain.applicable_regimes` classifier (never a
reinvented one, section 33)."""

from __future__ import annotations

import ve_brain  # type: ignore[import-untyped]

from ai_trader.new_brain_live.strategy_platform.mock_strategies import MockAlwaysNoTrade, MockLongOnFixedFixture
from ai_trader.new_brain_live.strategy_platform.router import (
    ELIGIBLE_REGIME_INDEPENDENT,
    ELIGIBLE_REGIME_MATCH,
    INELIGIBLE_INSTRUMENT_MISMATCH,
    INELIGIBLE_REGIME_MISMATCH,
    StrategyRouter,
)
from ai_trader.new_brain_live.strategy_platform.tests._fixtures import catalog_of, real_trend_up_market_state


def test_regime_independent_entry_is_always_eligible() -> None:
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockAlwaysNoTrade(), context_eligibility=None)
    outcome = StrategyRouter().route(catalog=catalog, market_state=market_state)
    assert len(outcome.eligible) == 1
    assert outcome.eligible[0].reason_codes == (ELIGIBLE_REGIME_INDEPENDENT,)


def test_matching_regime_is_eligible() -> None:
    market_state = real_trend_up_market_state()
    regimes = {r.value for r in ve_brain.applicable_regimes(market_state.axes)}
    assert "TREND_UP" in regimes, "fixture regression: must still resolve TREND_UP"
    catalog = catalog_of(MockAlwaysNoTrade(), context_eligibility=("TREND_UP",))
    outcome = StrategyRouter().route(catalog=catalog, market_state=market_state)
    assert len(outcome.eligible) == 1
    assert outcome.eligible[0].reason_codes == (ELIGIBLE_REGIME_MATCH,)


def test_mismatched_regime_is_ineligible() -> None:
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockAlwaysNoTrade(), context_eligibility=("RANGE",))
    outcome = StrategyRouter().route(catalog=catalog, market_state=market_state)
    assert len(outcome.eligible) == 0
    assert outcome.ineligible[0].reason_codes == (INELIGIBLE_REGIME_MISMATCH,)


def test_wrong_instrument_is_ineligible_regardless_of_regime() -> None:
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockAlwaysNoTrade(), context_eligibility=None, allowed_instruments=("EURUSD",))
    outcome = StrategyRouter().route(catalog=catalog, market_state=market_state)
    assert len(outcome.eligible) == 0
    assert outcome.ineligible[0].reason_codes == (INELIGIBLE_INSTRUMENT_MISMATCH,)


def test_disabled_entries_never_reached_by_router() -> None:
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockLongOnFixedFixture(), context_eligibility=None, enabled=False)
    outcome = StrategyRouter().route(catalog=catalog, market_state=market_state)
    assert outcome.eligible == ()
    assert outcome.ineligible == ()
    assert outcome.hypotheses == ()


def test_router_only_dispatches_never_judges_profitability() -> None:
    """A signaling, eligible strategy always produces a hypothesis in `RouterOutcome.hypotheses` -- the
    Router itself never filters on expected edge (that is EV's job, strictly downstream)."""
    market_state = real_trend_up_market_state()
    catalog = catalog_of(MockLongOnFixedFixture(), context_eligibility=None)
    outcome = StrategyRouter().route(catalog=catalog, market_state=market_state)
    assert len(outcome.hypotheses) == 1

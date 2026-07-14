"""Convenience builders for real, schema-valid ``RiskDecision`` objects, built through the REAL Risk
Manager (+ Scoring Engine + fixture Signal Engine handle) pipeline -- not hand-constructed dicts,
matching the "real upstream, fixture-driven" precedent every prior module's own test suite follows
(see ``ai_trader/risk_manager/tests/fixtures/fake_opportunity.py``, reused directly below).
"""

from __future__ import annotations

from dataclasses import replace

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import (
    make_below_floor_opportunity,
    make_opportunity,
    make_portfolio,
    make_risk_context,
)
from ai_trader.risk_manager.types import PortfolioState, RiskDecision


def _configured_manager() -> RiskManager:
    rm = RiskManager(RiskConfig())
    portfolio = make_portfolio()
    rm.configure(portfolio=portfolio)
    rm._config.filters.reference_spread["XAUUSD"] = 0.1
    rm._config.filters.liquidity_floor["XAUUSD"] = 100.0
    rm._config.filters.reference_spread["EURUSD"] = 0.1
    rm._config.filters.liquidity_floor["EURUSD"] = 100.0
    return rm


def make_allow_decision(
    strategy_id: str = "S1", symbol: str = "XAUUSD", direction: str = "LONG",
    entry: float = 100.0, stop: float = 99.0, target: float = 102.0, strength: float = 0.95,
    portfolio: PortfolioState | None = None,
) -> tuple[RiskDecision, PortfolioState]:
    """A real ``ALLOW`` decision, built end-to-end through a real, freshly-configured
    :class:`RiskManager`. Returns ``(decision, portfolio)`` -- the same portfolio the decision was
    evaluated against, for callers that need it too (e.g. the Order Validator's position-limit check)."""
    rm = _configured_manager()
    pf = portfolio if portfolio is not None else make_portfolio()
    opp = make_opportunity(
        strategy_id=strategy_id, symbol=symbol, direction=direction, entry=entry, stop=stop,
        target=target, strength=strength,
    )
    decision = rm.allow_trade(opp, make_risk_context(symbol=symbol), pf)
    assert decision.decision.value == "ALLOW", f"expected ALLOW, got {decision.decision.value}: {decision.denied_reasons}"
    return decision, pf


def make_deny_decision(
    strategy_id: str = "S1", symbol: str = "XAUUSD", portfolio: PortfolioState | None = None,
) -> tuple[RiskDecision, PortfolioState]:
    """A real ``DENY`` decision (below the recommendation floor)."""
    rm = _configured_manager()
    pf = portfolio if portfolio is not None else make_portfolio()
    opp = make_below_floor_opportunity(strategy_id=strategy_id, symbol=symbol)
    decision = rm.allow_trade(opp, make_risk_context(symbol=symbol), pf)
    assert decision.decision.value == "DENY"
    return decision, pf


def make_reduce_only_allow_decision(
    strategy_id: str = "S1", symbol: str = "XAUUSD", direction: str = "LONG",
    entry: float = 100.0, stop: float = 99.0, size_units: float = 5.0,
) -> tuple[RiskDecision, PortfolioState]:
    """A real ALLOW decision whose ``constraints.reduce_only`` is forced ``True`` -- Risk Manager v1
    never emits a genuine reduce-only ALLOW on its own (no partial-exit input exists yet, see
    ``EXECUTION_ENGINE_HANDOFF.md`` §2b's Portfolio Manager gap discussion), so this fixture forces
    the flag directly via ``dataclasses.replace``, exactly like every prior module's own
    "force the exact field under test" fixture pattern (mirrors Risk Manager's own
    ``make_below_floor_opportunity``).

    The decision itself is built against a CLEAN portfolio (so the Risk Manager's own
    ``LIMIT_MAX_PER_SYMBOL`` gate doesn't deny it) -- the returned portfolio (WITH a matching open
    position) is a separate object for the Execution Engine's own ``portfolio`` parameter, which is
    independent of whatever portfolio the Risk Manager itself evaluated against.
    """
    from ai_trader.risk_manager.types import OpenPosition
    from ai_trader.signal_engine.types import Direction

    decision, _clean_portfolio = make_allow_decision(
        strategy_id=strategy_id, symbol=symbol, direction=direction, entry=entry, stop=stop,
    )
    assert decision.constraints is not None
    reduced = replace(decision, constraints=replace(decision.constraints, reduce_only=True))

    existing = OpenPosition(
        symbol=symbol, strategy_id=strategy_id, direction=Direction[direction],
        size_units=size_units, entry_price=entry, opened_bars_ago=5, risk_pct=0.005,
    )
    portfolio_with_position = make_portfolio(open_positions=(existing,))
    return reduced, portfolio_with_position

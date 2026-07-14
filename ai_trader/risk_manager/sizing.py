"""The Position Sizer (``RISK_MANAGER_ARCHITECTURE.md`` §4/§5 stage 7, ``POSITION_SIZING.md``) --
runs ONLY after every policy gate has returned ALLOW (``POSITION_SIZING.md`` §0: "Sizing runs ONLY
after the risk policy returns ALLOW"). Fixed-fractional risk, quality-scaled within a bounded band,
clamped to the remaining portfolio exposure budget and the maximum notional allocation. v1 implements
the default `FIXED_FRACTIONAL` method only (`VOL_SCALED`/`ATR_SCALED` are documented, config-gated
future options per §5, not used in v1).
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import DeniedReason, PortfolioState, Sizing, SizingMethod
from ai_trader.scoring_engine.types import OpportunityScore


@dataclass(frozen=True, slots=True)
class SizingOutcome:
    valid: bool
    sizing: Sizing | None = None
    deny_reason: DeniedReason | None = None


def compute_sizing(
    opportunity: OpportunityScore, portfolio: PortfolioState, config: RiskConfig,
) -> SizingOutcome:
    """``POSITION_SIZING.md`` §1: ``size_units = (risk_per_trade_pct * equity) / (stop_distance *
    point_value)``, quality-scaled (§2), clamped to the remaining exposure budget (§3) and the
    maximum notional allocation (§6)."""
    tc = opportunity.trade_context
    if tc is None or tc.entry is None or tc.stop is None:
        return SizingOutcome(False, deny_reason=DeniedReason(code="INVALID_STOP", detail="missing entry/stop"))
    stop_distance = abs(tc.entry - tc.stop)
    if stop_distance <= 0:
        return SizingOutcome(False, deny_reason=DeniedReason(code="INVALID_STOP", detail="non-positive stop distance"))

    point_value = config.point_value_for(opportunity.symbol)
    if point_value <= 0 or portfolio.equity <= 0:
        return SizingOutcome(False, deny_reason=DeniedReason(code="INVALID_STOP", detail="invalid point_value/equity"))

    quality_factor = config.quality_factor_for(opportunity.quality)
    effective_risk_pct = config.sizing.risk_per_trade_pct * quality_factor

    # POSITION_SIZING.md §3, sentence 1: clamp to whatever AGGREGATE exposure budget the running
    # portfolio view has left (the coarser "is there any room at all" gate already ran in limits.py's
    # LIMIT_MAX_EXPOSURE; this is the fine-grained "how much room, exactly" clamp).
    remaining_exposure_pct = max(0.0, config.portfolio_limits.max_exposure_pct - portfolio.portfolio_risk_pct)
    effective_risk_pct = min(effective_risk_pct, remaining_exposure_pct)

    # POSITION_SIZING.md §3, sentence 2: trades sharing a correlation group share a smaller,
    # deterministic sub-budget of the aggregate exposure cap -- an EVEN split of the aggregate cap
    # across the max number of correlated positions LIMIT_MAX_CORRELATED ever allows open at once,
    # mirroring limits.py::check_max_correlated's own group-membership counting logic so both gates
    # agree on what "the same group" means.
    group = config.correlation_group_for(opportunity.symbol)
    group_risk_pct = sum(
        p.risk_pct for p in portfolio.open_positions
        if (p.correlation_group or config.correlation_group_for(p.symbol)) == group
    )
    max_correlated = max(1, config.portfolio_limits.max_correlated)
    group_budget_pct = config.portfolio_limits.max_exposure_pct / max_correlated
    remaining_group_budget_pct = max(0.0, group_budget_pct - group_risk_pct)
    effective_risk_pct = min(effective_risk_pct, remaining_group_budget_pct)

    risk_budget_currency = effective_risk_pct * portfolio.equity
    size_units = risk_budget_currency / (stop_distance * point_value)

    # §6: maximum notional allocation cap.
    max_notional = config.sizing.max_position_notional_pct * portfolio.equity
    max_size_units = max_notional / (tc.entry * point_value) if tc.entry > 0 else 0.0
    if size_units > max_size_units:
        size_units = max_size_units
        risk_budget_currency = size_units * stop_distance * point_value
        effective_risk_pct = risk_budget_currency / portfolio.equity

    notional = size_units * tc.entry * point_value
    leverage = notional / portfolio.equity

    min_budget_currency = config.sizing.min_allocation_risk_pct * portfolio.equity
    min_size_units = min_budget_currency / (stop_distance * point_value)

    if size_units < min_size_units or size_units <= 0:
        return SizingOutcome(
            False,
            deny_reason=DeniedReason(code="SIZE_BELOW_MIN", observed=size_units, limit=min_size_units),
        )

    sizing = Sizing(
        method=SizingMethod.FIXED_FRACTIONAL,
        risk_per_trade_pct=effective_risk_pct,
        quality_factor=quality_factor,
        risk_R=1.0,
        risk_budget_currency=risk_budget_currency,
        stop_distance=stop_distance,
        size_units=size_units,
        min_size=min_size_units,
        max_size=max_size_units,
        notional=notional,
        leverage=leverage,
    )
    return SizingOutcome(True, sizing=sizing)

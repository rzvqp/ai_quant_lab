"""Portfolio Limits (``RISK_MANAGER_ARCHITECTURE.md`` §4/§5 stage 4, ``RISK_POLICY.md`` §2): count/
exposure/correlation/leverage/overnight caps checked against the RUNNING :class:`~ai_trader.
risk_manager.types.PortfolioState` view (updated after every ``ALLOW`` earlier in the same batch --
``RISK_MANAGER_ARCHITECTURE.md`` §5/§9).

**Ordering note.** ``LIMIT_MAX_EXPOSURE``/``LIMIT_MAX_LEVERAGE``/``LIMIT_MAX_OVERNIGHT`` gate on
whether the portfolio is ALREADY at/over its cap -- they do NOT (cannot) know this specific trade's
own risk contribution yet, since sizing (stage 7) runs AFTER limits (stage 4) in the fixed pipeline
order. Only ``LIMIT_MAX_EXPOSURE`` has a matching fine-grained sizing-time clamp: ``POSITION_SIZING.md``
§3 defines "clamp this trade's size to whatever exposure budget remains" for exposure specifically, and
:func:`~ai_trader.risk_manager.sizing.compute_sizing` implements exactly that. ``POSITION_SIZING.md``
never describes an analogous per-trade clamp for leverage or overnight exposure, so
``LIMIT_MAX_LEVERAGE``/``LIMIT_MAX_OVERNIGHT`` remain coarse "is there any room left at all" checks
ONLY -- a trade that passes them here is never subsequently narrowed by sizing on those two axes.

**Consolidation note.** ``RISK_POLICY.md`` §2's "Maximum event exposure" (`LIMIT_MAX_EVENT`) and §5's
"News filter" (`FILTER_NEWS`) describe the SAME underlying rule -- §5's own text says "(see §2 event
exposure)". Implementing both independently would make one permanently unreachable dead code (whichever
stage runs first always fires first for the identical condition). It is implemented ONCE, as
`FILTER_NEWS` in :mod:`ai_trader.risk_manager.filters` (the earlier, stage-3 Pre-Trade Filters gate) --
no separate `LIMIT_MAX_EVENT` check exists here.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import DeniedReason, PortfolioState, SymbolRiskSnapshot


@dataclass(frozen=True, slots=True)
class LimitResult:
    passed: bool
    reason: DeniedReason | None = None


def check_max_positions(portfolio: PortfolioState, config: RiskConfig) -> LimitResult:
    count = len(portfolio.open_positions)
    limit = config.portfolio_limits.max_positions
    if count >= limit:
        return LimitResult(False, DeniedReason(code="LIMIT_MAX_POSITIONS", observed=count, limit=limit))
    return LimitResult(True)


def check_max_per_symbol(symbol: str, portfolio: PortfolioState, config: RiskConfig) -> LimitResult:
    count = sum(1 for p in portfolio.open_positions if p.symbol == symbol)
    limit = config.portfolio_limits.max_per_symbol
    if count >= limit:
        return LimitResult(False, DeniedReason(code="LIMIT_MAX_PER_SYMBOL", observed=count, limit=limit))
    return LimitResult(True)


def check_max_correlated(symbol: str, portfolio: PortfolioState, config: RiskConfig) -> LimitResult:
    group = config.correlation_group_for(symbol)
    count = sum(
        1 for p in portfolio.open_positions
        if (p.correlation_group or config.correlation_group_for(p.symbol)) == group
    )
    limit = config.portfolio_limits.max_correlated
    if count >= limit:
        return LimitResult(False, DeniedReason(code="LIMIT_MAX_CORRELATED", observed=count, limit=limit, detail=group))
    return LimitResult(True)


def check_max_exposure(portfolio: PortfolioState, config: RiskConfig) -> LimitResult:
    observed = portfolio.portfolio_risk_pct
    limit = config.portfolio_limits.max_exposure_pct
    if observed >= limit:
        return LimitResult(False, DeniedReason(code="LIMIT_MAX_EXPOSURE", observed=observed, limit=limit))
    return LimitResult(True)


def check_max_leverage(portfolio: PortfolioState, config: RiskConfig) -> LimitResult:
    observed = portfolio.leverage
    limit = config.portfolio_limits.max_leverage
    if observed >= limit:
        return LimitResult(False, DeniedReason(code="LIMIT_MAX_LEVERAGE", observed=observed, limit=limit))
    return LimitResult(True)


def check_max_overnight(symbol: str, snapshot: SymbolRiskSnapshot, portfolio: PortfolioState, config: RiskConfig) -> LimitResult:
    if not snapshot.is_near_session_close:
        return LimitResult(True)
    observed = portfolio.portfolio_risk_pct
    limit = config.portfolio_limits.max_overnight_exposure_pct
    if observed >= limit:
        return LimitResult(False, DeniedReason(code="LIMIT_MAX_OVERNIGHT", observed=observed, limit=limit))
    return LimitResult(True)


def run_portfolio_limits(
    symbol: str, snapshot: SymbolRiskSnapshot, portfolio: PortfolioState, config: RiskConfig,
) -> list[tuple[str, LimitResult]]:
    """Run every portfolio limit in the fixed order (``RISK_POLICY.md`` §2's table order), returning
    ``(rule_name, LimitResult)`` for each. Never short-circuits -- the caller stops at the first
    failure for the actual DENY decision but the full ordered list is available for audit."""
    return [
        ("LIMIT_MAX_POSITIONS", check_max_positions(portfolio, config)),
        ("LIMIT_MAX_PER_SYMBOL", check_max_per_symbol(symbol, portfolio, config)),
        ("LIMIT_MAX_CORRELATED", check_max_correlated(symbol, portfolio, config)),
        ("LIMIT_MAX_EXPOSURE", check_max_exposure(portfolio, config)),
        ("LIMIT_MAX_LEVERAGE", check_max_leverage(portfolio, config)),
        ("LIMIT_MAX_OVERNIGHT", check_max_overnight(symbol, snapshot, portfolio, config)),
    ]

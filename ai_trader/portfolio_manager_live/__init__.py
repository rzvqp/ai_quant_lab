"""Portfolio Manager (Phase 4 -- `PORTFOLIO_MANAGER_PHASE4_DESIGN.md`). Gates an already-Risk-Manager-
approved trade at the aggregate-book level: total/per-symbol/per-direction/per-strategy/per-session/
per-asset-class exposure, long/short conflicts, reserved capital, portfolio heat, and daily state. Pure
function -- no state, no I/O, no MT5 terminal API import (verified by a dedicated static test). Sits
between Risk Manager and Order Manager in the live pipeline (CEO rule 8: no module may bypass either)."""

from __future__ import annotations

from ai_trader.portfolio_manager_live.engine import evaluate_portfolio_authorization
from ai_trader.portfolio_manager_live.types import (
    ExposureSnapshot,
    PortfolioAuthorizationRequest,
    PortfolioDailyState,
    PortfolioDecision,
    PortfolioManagerConfig,
)

__all__ = [
    "evaluate_portfolio_authorization",
    "PortfolioAuthorizationRequest",
    "PortfolioDailyState",
    "PortfolioDecision",
    "ExposureSnapshot",
    "PortfolioManagerConfig",
]

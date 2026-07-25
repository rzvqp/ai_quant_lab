"""Real implementation of `risk_manager_live.types.PortfolioStateSource` (Step 2 authorization,
2026-07-25): computes `PortfolioState` P&L fields from live MT5 position/deal history, via the existing
read-only gateway, extended additively (never via a new path to MT5, never receiving the execution
adapter). Fail-closed on any missing/incomplete data -- never defaults to 0.0, never estimates (Risk
Audit #1's own finding: a silent 0.0 default reads as "no losses," the most permissive result possible
exactly when nothing is actually known). This is the ONLY implementation of `PortfolioStateSource` --
the virtual/shadow implementation for Piesa 3 is a separate, later, deliberately-not-built-yet
authorization, satisfying the identical interface, never a second parallel one.
"""

from __future__ import annotations

from ai_trader.mt5_pnl_source.source import MT5PortfolioStateSource
from ai_trader.mt5_pnl_source.types import DealRecord, PortfolioDataUnavailableError

__all__ = ["MT5PortfolioStateSource", "DealRecord", "PortfolioDataUnavailableError"]

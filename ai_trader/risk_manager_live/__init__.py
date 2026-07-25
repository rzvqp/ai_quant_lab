"""Live Risk Manager (Phase 2 -- `RISK_MANAGER_LIVE_PHASE2_DESIGN.md`). Wraps the existing, frozen
`ai_trader/risk_manager/` package's own composable guard/limit/filter/sizing functions, unmodified, for
a live `TradeProposal` context the backtest-oriented `RiskManager.evaluate()`/`allow_trade()` entry
points were never designed for. Adds the two genuinely-missing checks (volume-step rounding, free-margin
sufficiency) additively. Never imports the MT5 terminal API (verified by a dedicated static test).
"""

from __future__ import annotations

from ai_trader.risk_manager_live.circuit_breaker import evaluate_circuit_state
from ai_trader.risk_manager_live.engine import evaluate_trade_proposal
from ai_trader.risk_manager_live.types import (
    AccountState,
    CalculationTraceStep,
    InstrumentSpecification,
    LiveRiskDecision,
    PortfolioStateSource,
    READY_CIRCUIT_STATE,
    TradeProposal,
    TradingCircuitState,
)

__all__ = [
    "evaluate_trade_proposal",
    "TradeProposal",
    "AccountState",
    "InstrumentSpecification",
    "LiveRiskDecision",
    "CalculationTraceStep",
    "evaluate_circuit_state",
    "TradingCircuitState",
    "READY_CIRCUIT_STATE",
    "PortfolioStateSource",
]

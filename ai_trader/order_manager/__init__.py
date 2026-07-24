"""Order Manager (Phase 3 -- `ORDER_MANAGER_PHASE3_DESIGN.md`). Bridges an approved
`risk_manager_live.LiveRiskDecision` into a broker-ready order, reusing `ai_trader/execution_engine/`'s
already-tested build/validate/submit/track/reconcile machinery unmodified wherever it fits, adding only
the genuinely missing pieces (`ApprovedTradeIntent`, `OrderExecutionResult`, price normalization, the
audit journal, and a dry-run-only broker adapter). Never imports the MT5 terminal API, directly or via
`execution_engine.adapters.mt5_gateway`/`mt5_adapter`/`mt5_types` (verified by a dedicated static test)
-- Phase 3 never sends a real order.
"""

from __future__ import annotations

from ai_trader.order_manager.engine import process_approved_intent
from ai_trader.order_manager.types import ApprovedTradeIntent, OrderExecutionResult, OrderManagerConfig

__all__ = [
    "process_approved_intent",
    "ApprovedTradeIntent",
    "OrderExecutionResult",
    "OrderManagerConfig",
]

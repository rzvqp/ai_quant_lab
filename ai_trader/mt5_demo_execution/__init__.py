"""MT5 Demo Execution (Phase 10 -- `MT5_DEMO_EXECUTION_PHASE10_DESIGN.md`). Extends the already-approved,
frozen Phase 1 `MT5ReadOnlyBrokerAdapter`/`RealMT5Gateway` by SUBCLASSING only -- zero modification.
Every send is gated: AlgoTrading re-verified, DEMO re-verified, volume-ceiling enforced, `order_check`
before `order_send`, and no DEMO attempt is ever made until the SAME intent's own dry-run has passed
(`gating.send_after_dry_run_gate`). Structurally refuses REAL/CONTEST accounts (inherited, unmodified,
from Phase 1). Never enables AlgoTrading or changes any terminal/account setting."""

from __future__ import annotations

from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.gateway import MT5DemoGateway, RealMT5DemoGateway
from ai_trader.mt5_demo_execution.gating import GatedDemoOutcome, send_after_dry_run_gate
from ai_trader.mt5_demo_execution.safety import is_market_open_for_symbol, verify_safety_guards
from ai_trader.mt5_demo_execution.types import (
    MT5DemoConfig,
    MT5OrderCheckResult,
    MT5OrderSendResult,
    SafetyGuardReport,
)

__all__ = [
    "MT5DemoBrokerAdapter",
    "MT5DemoGateway",
    "RealMT5DemoGateway",
    "MT5DemoConfig",
    "MT5OrderCheckResult",
    "MT5OrderSendResult",
    "SafetyGuardReport",
    "verify_safety_guards",
    "is_market_open_for_symbol",
    "send_after_dry_run_gate",
    "GatedDemoOutcome",
]

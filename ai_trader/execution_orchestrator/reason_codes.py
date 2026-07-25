"""Reason codes the Execution Orchestrator's own coordination logic can produce -- additive, distinct
from every downstream engine's own vocabulary (which is reused verbatim, unmodified, when a downstream
engine denies)."""

from __future__ import annotations

EMERGENCY_STOP_ACTIVE = "EMERGENCY_STOP_ACTIVE"
LIVE_TRADING_NOT_AUTHORIZED = "LIVE_TRADING_NOT_AUTHORIZED"
NON_DEMO_ACCOUNT_REFUSED = "NON_DEMO_ACCOUNT_REFUSED"
STALE_CANDIDATE = "STALE_CANDIDATE"
CONTEXT_BUILD_FAILED = "CONTEXT_BUILD_FAILED"
CONFIDENCE_ASSESSMENT_FAILED = "CONFIDENCE_ASSESSMENT_FAILED"
NOT_ELIGIBLE_FOR_RISK_EVALUATION = "NOT_ELIGIBLE_FOR_RISK_EVALUATION"
RISK_EVALUATION_FAILED = "RISK_EVALUATION_FAILED"
RISK_DENIED = "RISK_DENIED"
PORTFOLIO_EVALUATION_FAILED = "PORTFOLIO_EVALUATION_FAILED"
PORTFOLIO_DENIED = "PORTFOLIO_DENIED"
ORDER_MANAGER_FAILED = "ORDER_MANAGER_FAILED"

#: Risk Audit #1 fix (2026-07-25): emitted when a caller-supplied, persisted `TradingCircuitState` is
#: not READY -- the account is suspended (a loss/drawdown guard escalated and has not yet recovered) or
#: in emergency stop. Distinct from `EMERGENCY_STOP_ACTIVE`, which remains the OLD, single-call,
#: non-persistent override for callers that don't supply circuit tracking at all.
TRADING_SUSPENDED = "TRADING_SUSPENDED"

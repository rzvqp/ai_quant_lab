"""Execution Orchestrator (Phase 9 -- `EXECUTION_ORCHESTRATOR_PHASE9_DESIGN.md`). Coordinates every
prior phase (Context Engine -> Recognition Engine -> Confidence Engine -> Risk Manager -> Portfolio
Manager -> Order Manager -> Broker Adapter), unmodified, in the CEO's own specified order. Never sends a
real order (`ExecutionMode.LIVE` is structurally refused; `DEMO` is functionally identical to `DRY_RUN`
this phase since Order Manager, Phase 3, is structurally dry-run-only). Never imports the MT5 terminal
API or any MT5-specific submodule (verified by dedicated static tests)."""

from __future__ import annotations

from ai_trader.execution_orchestrator.engine import correlation_id_for, orchestrate, reconcile_orchestrated_orders
from ai_trader.execution_orchestrator.types import (
    CalculationTraceStep,
    CandidateSignal,
    ExecutionMode,
    OrchestrationResult,
    OrchestratorConfig,
    OrchestratorDependencies,
)

__all__ = [
    "orchestrate",
    "reconcile_orchestrated_orders",
    "correlation_id_for",
    "CandidateSignal",
    "ExecutionMode",
    "OrchestratorConfig",
    "OrchestratorDependencies",
    "OrchestrationResult",
    "CalculationTraceStep",
]

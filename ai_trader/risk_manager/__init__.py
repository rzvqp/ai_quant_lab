"""Risk Manager v1 — public package surface.

Only the documented API (``RISK_API.md``) is exported here; internal modules
(:mod:`ai_trader.risk_manager.pipeline`, :mod:`ai_trader.risk_manager.filters`, etc.) are
implementation details, not part of the public surface.
"""

from __future__ import annotations

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import RiskManager
from ai_trader.risk_manager.exceptions import EngineNotConfiguredError, RiskManagerError, SchemaLoadError
from ai_trader.risk_manager.types import (
    Constraints,
    Decision,
    DeniedReason,
    EngineHealth,
    EngineLifecycleState,
    EngineOverallHealth,
    EngineState,
    LimitsReport,
    NotFound,
    OpenPosition,
    ClosedPosition,
    PortfolioImpact,
    PortfolioState,
    RiskContext,
    RiskDecision,
    RiskDecisionBatch,
    RiskRefs,
    Sizing,
    SizingMethod,
    SizingResult,
    Statistics,
    SymbolRiskSnapshot,
    ValidationResult,
    VersionInfo,
)

__all__ = [
    "RiskManager",
    "RiskConfig",
    "RiskManagerError",
    "EngineNotConfiguredError",
    "SchemaLoadError",
    "RiskDecision",
    "RiskDecisionBatch",
    "Decision",
    "DeniedReason",
    "Constraints",
    "Sizing",
    "SizingMethod",
    "SizingResult",
    "PortfolioImpact",
    "RiskRefs",
    "ValidationResult",
    "Statistics",
    "EngineHealth",
    "EngineOverallHealth",
    "EngineLifecycleState",
    "EngineState",
    "LimitsReport",
    "NotFound",
    "RiskContext",
    "SymbolRiskSnapshot",
    "PortfolioState",
    "OpenPosition",
    "ClosedPosition",
    "VersionInfo",
]

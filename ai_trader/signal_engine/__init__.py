"""Signal Engine v1 — the AI Trader's third module (Phase 6.3).

Public API surface (``SIGNAL_ENGINE_API.md``). Only these names are exported; internal modules
(``pipeline``, ``context_check``, ``explanation``, ``assembler``, ``validator``,
``schema_validation``) are implementation details and may change without notice. Per the separation
law (``SIGNAL_ENGINE_ARCHITECTURE.md`` §1/§10), nothing in this package reads Research Lab artifacts
— a strategy is known ONLY through the handle the Strategy Manager provides, and market data ONLY
through the ``MarketContext`` the orchestrator supplies.
"""

from ai_trader.signal_engine.config import EngineConfig, SupportedVersions
from ai_trader.signal_engine.engine import SignalEngine
from ai_trader.signal_engine.exceptions import (
    EngineNotConfiguredError,
    SchemaLoadError,
    SignalEngineError,
)
from ai_trader.signal_engine.pipeline import MalformedStrategyResponseError
from ai_trader.signal_engine.types import (
    ACTIONABLE_STATES,
    NON_ACTIONABLE_STATES,
    READY_STATES,
    ConditionRecord,
    Confirmations,
    ContextRef,
    ContextSummary,
    Direction,
    EngineHealth,
    EngineOverallHealth,
    Explanation,
    NotFound,
    QualityFlag,
    SignalBatch,
    SignalState,
    Statistics,
    StrategyRef,
    StrategySignal,
    TradeParams,
    TriggeringMechanism,
    ValidationResult,
    VersionInfo,
)

__all__ = [
    "SignalEngine",
    "EngineConfig",
    "SupportedVersions",
    "SignalState",
    "ACTIONABLE_STATES",
    "READY_STATES",
    "NON_ACTIONABLE_STATES",
    "Direction",
    "QualityFlag",
    "ContextRef",
    "TradeParams",
    "ConditionRecord",
    "TriggeringMechanism",
    "Confirmations",
    "ContextSummary",
    "StrategyRef",
    "Explanation",
    "StrategySignal",
    "SignalBatch",
    "ValidationResult",
    "Statistics",
    "EngineHealth",
    "EngineOverallHealth",
    "VersionInfo",
    "NotFound",
    "SignalEngineError",
    "EngineNotConfiguredError",
    "SchemaLoadError",
    "MalformedStrategyResponseError",
]

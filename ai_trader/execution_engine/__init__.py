"""Execution Engine v1 — public package surface.

Only the documented API (``EXECUTION_API.md``) is exported here; internal modules
(:mod:`ai_trader.execution_engine.pipeline`, :mod:`ai_trader.execution_engine.builder`, etc.) are
implementation details, not part of the public surface.
"""

from __future__ import annotations

from ai_trader.execution_engine.broker_adapter import BrokerAdapter
from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.engine import ExecutionEngine
from ai_trader.execution_engine.exceptions import EngineNotConfiguredError, ExecutionEngineError, SchemaLoadError
from ai_trader.execution_engine.types import (
    BracketLegs,
    BrokerAck,
    BrokerCapabilities,
    BrokerCapabilitiesRef,
    BrokerOrderState,
    EngineHealth,
    EngineLifecycleState,
    EngineOverallHealth,
    ExecutionReport,
    ExecutionResult,
    Fill,
    FlattenScope,
    MarketStatus,
    NotFound,
    OcoLink,
    OcoRole,
    OrderConstraints,
    OrderIntent,
    OrderRefs,
    OrderRequest,
    OrderSide,
    OrderState,
    OrderStatus,
    OrderType,
    Statistics,
    TimeInForce,
    ValidationResult,
    VersionInfo,
)

__all__ = [
    "ExecutionEngine",
    "ExecConfig",
    "ExecutionEngineError",
    "EngineNotConfiguredError",
    "SchemaLoadError",
    "BrokerAdapter",
    "BrokerAck",
    "BrokerCapabilities",
    "BrokerCapabilitiesRef",
    "BrokerOrderState",
    "OrderRequest",
    "OrderSide",
    "OrderIntent",
    "OrderType",
    "TimeInForce",
    "OrderState",
    "OcoRole",
    "OcoLink",
    "BracketLegs",
    "OrderConstraints",
    "OrderRefs",
    "OrderStatus",
    "ExecutionResult",
    "ExecutionReport",
    "Fill",
    "FlattenScope",
    "ValidationResult",
    "Statistics",
    "EngineHealth",
    "EngineOverallHealth",
    "EngineLifecycleState",
    "MarketStatus",
    "NotFound",
    "VersionInfo",
]

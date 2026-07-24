"""Broker Adapter foundation (Layer A) + MT5 read-only adapter (Layer B).
`BROKER_ADAPTER_DESIGN.md`, CEO-authorized 2026-07-24. The pre-existing `ai_trader.execution_engine.
broker_adapter.BrokerAdapter` Protocol and the pre-existing simulation-side virtual broker adapter
are both unchanged by this package."""

from __future__ import annotations

from ai_trader.execution_engine.adapters.base import RealBrokerAdapterBase, RetryPolicy
from ai_trader.execution_engine.adapters.connection import (
    BrokerConnectionLifecycle,
    BrokerCredentials,
    ConnectionResult,
    ConnectionState,
)
from ai_trader.execution_engine.adapters.exceptions import (
    AccountValidationError,
    NonDemoAccountError,
    NotConnectedError,
    RealBrokerAdapterError,
    RetryExhaustedError,
    SafetyRefusalError,
    TerminalNotConnectedError,
    UnexpectedServerError,
)
from ai_trader.execution_engine.adapters.mt5_adapter import MT5ReadOnlyBrokerAdapter
from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway, RealMT5Gateway
from ai_trader.execution_engine.adapters.mt5_types import (
    AccountTradeMode,
    AlgoTradingStatus,
    MT5AdapterStatus,
    MT5SymbolCapabilities,
    NormalizedMT5Error,
)
from ai_trader.execution_engine.adapters.null_adapter import NullBrokerAdapter

__all__ = [
    "RealBrokerAdapterBase",
    "RetryPolicy",
    "BrokerConnectionLifecycle",
    "BrokerCredentials",
    "ConnectionResult",
    "ConnectionState",
    "RealBrokerAdapterError",
    "NotConnectedError",
    "RetryExhaustedError",
    "SafetyRefusalError",
    "NonDemoAccountError",
    "UnexpectedServerError",
    "TerminalNotConnectedError",
    "AccountValidationError",
    "NullBrokerAdapter",
    "MT5Gateway",
    "RealMT5Gateway",
    "MT5ReadOnlyBrokerAdapter",
    "AccountTradeMode",
    "AlgoTradingStatus",
    "MT5AdapterStatus",
    "MT5SymbolCapabilities",
    "NormalizedMT5Error",
]

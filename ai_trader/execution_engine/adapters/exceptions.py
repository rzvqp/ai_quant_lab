"""Typed exceptions for the new Broker Adapter foundation (`BROKER_ADAPTER_DESIGN.md`, CEO-authorized
Layer A). Mirrors this project's own established exception-hierarchy pattern
(`ai_trader/execution_engine/exceptions.py`'s own docstring: "the same discipline followed by every
prior module"). All new exceptions subclass the EXISTING `ExecutionEngineError` -- one shared hierarchy,
not a competing one.

These exceptions are raised ONLY by `BrokerConnectionLifecycle.connect()` and the new
`RealBrokerAdapterBase` machinery -- never by the pre-existing `BrokerAdapter` Protocol's own 5 methods,
which remain contractually non-raising, unmodified, per the CEO's own explicit instruction.
"""

from __future__ import annotations

from ai_trader.execution_engine.exceptions import ExecutionEngineError


class RealBrokerAdapterError(ExecutionEngineError):
    """Base class for every new real-adapter-foundation error."""


class NotConnectedError(RealBrokerAdapterError):
    """Raised when an operation requiring an active connection is attempted while disconnected."""


class RetryExhaustedError(RealBrokerAdapterError):
    """Raised when a retried operation exhausts its configured `RetryPolicy` without succeeding."""


class SafetyRefusalError(RealBrokerAdapterError):
    """Base class for every safety-gate refusal at `connect()` time (CEO's own mandatory refusal
    conditions) -- the adapter never becomes operational when one of these fires."""


class NonDemoAccountError(SafetyRefusalError):
    """Raised when the connected account's own `trade_mode` is not DEMO. No automatic fallback to any
    other account is ever attempted -- this exception IS the stop, not a retry trigger."""


class UnexpectedServerError(SafetyRefusalError):
    """Raised when an explicitly-configured expected server name does not match the connected
    account's own reported server."""


class TerminalNotConnectedError(SafetyRefusalError):
    """Raised when the terminal itself reports not connected at `connect()` time."""


class AccountValidationError(SafetyRefusalError):
    """Raised when account/terminal data cannot be read/validated at all (a `None` result from the
    underlying gateway where a real value was required)."""

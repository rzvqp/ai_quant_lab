"""Exception hierarchy for the Signal Engine.

Per ``SIGNAL_ENGINE_API.md`` ("failure model: expected failures are returned as non-actionable
signals or typed results, never thrown across the boundary"), every *expected* failure — a strategy
that times out, raises, or returns malformed output, an unknown strategy id, a stale context — is a
classified, non-actionable :class:`~ai_trader.signal_engine.types.StrategySignal` (state ``INVALID``
with a ``quality_flags`` reason) or a typed result (``NotFound``), never an exception thrown across
the public API. The exceptions below exist only for genuinely exceptional conditions: programmer
errors (calling the API before :meth:`SignalEngine.configure`) and environment failures (the schema
files themselves missing/corrupt). All derive from :class:`SignalEngineError`.
"""

from __future__ import annotations


class SignalEngineError(Exception):
    """Base class for every Signal Engine exception."""


class EngineNotConfiguredError(SignalEngineError):
    """Raised when an operation requires :meth:`SignalEngine.configure` to have run first."""


class SchemaLoadError(SignalEngineError):
    """Raised when ``SIGNAL_SCHEMA.json``/``SIGNAL_EXPLANATION_SCHEMA.json`` cannot be located,
    read, or compiled."""

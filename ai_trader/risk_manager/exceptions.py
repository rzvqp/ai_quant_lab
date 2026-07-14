"""Exception hierarchy for the Risk Manager.

Per ``RISK_API.md`` ("failure model: expected failures return DENY decisions or typed results, never
thrown across the boundary"), every *expected* failure -- an invalid opportunity, unavailable
portfolio state, a breached limit -- is a classified ``DENY`` :class:`~ai_trader.risk_manager.types.
RiskDecision`, never an exception thrown across the public API. The exceptions below exist only for
genuinely exceptional conditions: programmer errors (calling the API before
:meth:`RiskManager.configure`) and environment failures (the schema file itself missing/corrupt). All
derive from :class:`RiskManagerError`.
"""

from __future__ import annotations


class RiskManagerError(Exception):
    """Base class for every Risk Manager exception."""


class EngineNotConfiguredError(RiskManagerError):
    """Raised when an operation requires :meth:`RiskManager.configure` to have run first."""


class SchemaLoadError(RiskManagerError):
    """Raised when ``RISK_SCHEMA.json`` cannot be located, read, or compiled."""

"""Exception hierarchy for the Scoring Engine.

Per ``SCORING_API.md`` ("failure model: expected failures are returned as low/zero INVALID/SKIP
scores or typed results, never thrown across the boundary"), every *expected* failure -- a signal
that fails to parse, missing contract evidence, a schema-mismatched score -- is a classified, fail-
safe :class:`~ai_trader.scoring_engine.types.OpportunityScore` (``recommendation=INVALID`` or
``SKIP``) or a typed result (``NotFound``), never an exception thrown across the public API. The
exceptions below exist only for genuinely exceptional conditions: programmer errors (calling the API
before :meth:`ScoringEngine.configure`) and environment failures (the schema file itself missing/
corrupt). All derive from :class:`ScoringEngineError`.
"""

from __future__ import annotations


class ScoringEngineError(Exception):
    """Base class for every Scoring Engine exception."""


class EngineNotConfiguredError(ScoringEngineError):
    """Raised when an operation requires :meth:`ScoringEngine.configure` to have run first."""


class SchemaLoadError(ScoringEngineError):
    """Raised when ``SCORING_SCHEMA.json`` cannot be located, read, or compiled."""

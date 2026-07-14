"""Exceptions for the Execution Engine. Mirrors the exact exception hierarchy pattern used by every
prior AI Trader module (Market Scanner, Strategy Manager, Signal Engine, Scoring Engine, Risk Manager).
"""

from __future__ import annotations


class ExecutionEngineError(Exception):
    """Base class for all Execution Engine errors."""


class EngineNotConfiguredError(ExecutionEngineError):
    """Raised when a method requiring ``configure()`` is called before it (or after ``shutdown()``)."""


class SchemaLoadError(ExecutionEngineError):
    """Raised when ``ORDER_SCHEMA.json`` cannot be read, parsed, or compiled."""

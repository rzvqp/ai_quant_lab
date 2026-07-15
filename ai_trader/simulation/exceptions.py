"""Exceptions for the Simulation Framework. Mirrors the exact exception hierarchy pattern used by
every prior AI Trader module (Market Scanner, Strategy Manager, Signal Engine, Scoring Engine, Risk
Manager, Execution Engine)."""

from __future__ import annotations


class SimulationError(Exception):
    """Base class for all Simulation Framework errors."""


class RunNotConfiguredError(SimulationError):
    """Raised when a method requiring ``configure()``/``load()`` is called before it, or after the run
    has already reached a terminal state (``COMPLETED``/``FAILED``/``STOPPED``)."""


class InvalidContextError(SimulationError):
    """Raised by ``configure()`` when the ``SimulationContext`` fails validation (bad dates/symbols/
    incompatible module versions/unsupported config value) -- fail-fast, before any bar is processed."""


class SchemaLoadError(SimulationError):
    """Raised when ``SIMULATION_SCHEMA.json`` cannot be read, parsed, or compiled."""


class DataLoadError(SimulationError):
    """Raised when the Replay Data Source cannot load the historical bars a run's ``SimulationContext``
    requires (missing file, empty range, unreadable format)."""


class UnknownRunError(SimulationError):
    """Raised internally when an operation references a ``run_id``/``batch_id`` this process has no
    record of -- public API methods convert this to a typed ``NotFound`` result instead of raising."""

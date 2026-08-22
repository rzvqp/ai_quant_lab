"""Explicit execution-mode gate (mandate section 5). `BROKER_ORDER_SUBMISSION_DISABLED`
(`mandate2_readiness.broker_gate.BrokerOrderSubmissionGate`) is NEVER replaced with a generic ENABLED --
`MT5_DEMO_ONLY` is its own, distinct, explicitly-opted-into mode, constructed only by whoever assembles
the live runtime loop. Any unrecognized configuration value fails CLOSED (raises), never silently
defaults to DISABLED *or* to enabling anything -- an unknown value is a configuration bug that must be
fixed at the call site, not guessed past."""

from __future__ import annotations

from enum import Enum


class ExecutionMode(str, Enum):
    DISABLED = "DISABLED"
    MT5_DEMO_ONLY = "MT5_DEMO_ONLY"


class UnknownExecutionModeError(ValueError):
    """Fail-closed at configuration-resolution time -- see module docstring."""


def resolve_execution_mode(raw: str | ExecutionMode | None) -> ExecutionMode:
    if raw is None:
        return ExecutionMode.DISABLED
    if isinstance(raw, ExecutionMode):
        return raw
    try:
        return ExecutionMode(raw)
    except ValueError as exc:
        raise UnknownExecutionModeError(
            f"Unknown execution mode {raw!r} -- refusing to guess; must be exactly one of "
            f"{[m.value for m in ExecutionMode]!r}, or None (defaults to DISABLED)"
        ) from exc

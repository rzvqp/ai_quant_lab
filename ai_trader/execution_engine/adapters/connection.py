"""`BrokerConnectionLifecycle` -- the new, ADDITIVE Protocol capturing connection/session lifecycle, the
one thing `ai_trader.execution_engine.broker_adapter.BrokerAdapter` never designed (`BROKER_ADAPTER_
DESIGN.md` Sec2/Sec3, CEO-accepted). The existing `BrokerAdapter` Protocol is NEVER modified -- a real
adapter implements BOTH protocols; `ExecutionSimulator` needs neither and is untouched.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, runtime_checkable


class ConnectionState(str, Enum):
    """Explicit connection states (CEO's own explicit requirement) -- never inferred implicitly from
    other flags."""

    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    REFUSED = "REFUSED"  # a safety gate fired at connect() time; never became operational


@dataclass(frozen=True, slots=True)
class ConnectionResult:
    """The outcome of one `connect()` attempt. `accepted=False` always carries a `reason` -- mirrors
    `BrokerAck`'s own "report failures via the return value" discipline, extended to connection
    lifecycle. `connect()` itself is allowed to raise a `SafetyRefusalError` subclass for the CEO's own
    mandatory refusal conditions (Sec on `RealBrokerAdapterBase` below) -- this type is what a SUCCESSFUL
    or a recoverable/transient failure looks like; a hard safety refusal is a raised exception, never a
    silently-`accepted=False` result, so it cannot be missed by a careless caller."""

    accepted: bool
    reason: str | None = None
    connected_as_of: int = field(default_factory=lambda: int(time.time()))

    def __post_init__(self) -> None:
        if not self.accepted and self.reason is None:
            raise ValueError("ConnectionResult: accepted=False must always carry a reason")


@dataclass(frozen=True, slots=True)
class BrokerCredentials:
    """Opaque credential/config holder for a real adapter's own `connect()`. ALL fields are optional --
    the primary mode this project has actually verified (`MT5_CONNECTIVITY_PROBE_REPORT.md`) is
    attaching to an ALREADY-open, already-authenticated terminal with none of these set; explicit
    login/password/server/path support a future non-interactive mode, unverified so far, per that same
    report's own disclosed open item.

    **Credential-leakage protection (CEO's own explicit mandatory requirement)**: `__repr__`/`__str__`
    NEVER include `password` -- both are overridden to redact it unconditionally, so accidental logging,
    exception-message interpolation, or `repr()` in a debugger/traceback can never leak it. `password`
    itself is stored as a plain field (no reversible-encryption theatre attempted -- out of scope, real
    secret-store integration is a future, separate decision), but is never touched by any formatting
    path in this module."""

    login: int | None = None
    password: str | None = None
    server: str | None = None
    path: str | None = None
    expected_server: str | None = None  # CEO's own "refuse if server != expected, when configured" gate

    def __repr__(self) -> str:
        redacted_password = "***REDACTED***" if self.password is not None else None
        return (
            f"BrokerCredentials(login={self.login!r}, password={redacted_password!r}, "
            f"server={self.server!r}, path={self.path!r}, expected_server={self.expected_server!r})"
        )

    __str__ = __repr__


@runtime_checkable
class BrokerConnectionLifecycle(Protocol):
    """A SEPARATE, additive Protocol -- not folded into `BrokerAdapter` (`BROKER_ADAPTER_DESIGN.md`
    Sec3's own rationale: `ExecutionSimulator` needs none of this and must never be forced to grow a
    fake implementation of it). A real adapter implements both `BrokerAdapter` and this."""

    def connect(self) -> ConnectionResult:
        """Establish (or attach to) a connection. May raise a `SafetyRefusalError` subclass (CEO's own
        mandatory refusal conditions) -- in that case the adapter never becomes CONNECTED. A recoverable
        failure (e.g. the underlying gateway call itself failed) returns `ConnectionResult(accepted=False,
        reason=...)` instead of raising."""
        ...

    def disconnect(self) -> None:
        """Tear down the connection. Idempotent -- calling it while already disconnected is a no-op,
        never an error."""
        ...

    def is_connected(self) -> bool:
        """The adapter's own current connection state -- `True` only when `ConnectionState.CONNECTED`."""
        ...

    def last_heartbeat_as_of(self) -> int | None:
        """Epoch seconds of the last successful liveness check, or `None` if never connected."""
        ...

    def heartbeat(self) -> bool:
        """Actively check liveness right now (never raises) and update `last_heartbeat_as_of()` on
        success. Returns `False` immediately, without attempting any check, if not currently connected."""
        ...

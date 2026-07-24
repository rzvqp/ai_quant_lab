"""`RealBrokerAdapterBase` -- the shared, venue-agnostic machinery every real (non-simulated) adapter
needs that `ExecutionSimulator` never had to solve, because it has no network/IPC boundary
(`BROKER_ADAPTER_DESIGN.md` Sec3, CEO-accepted): connection lifecycle, idempotent order submission,
bounded/testable retry, explicit connection states, and safe credential handling. Implements
`BrokerConnectionLifecycle` concretely; subclasses supply the venue-specific pieces (`_do_connect`,
`_do_disconnect`, `_do_heartbeat_check`) and, if they submit orders at all, call `_submit_with_idempotency`
from their own `submit_order` implementation of the pre-existing, UNMODIFIED `BrokerAdapter` Protocol.

`MT5ReadOnlyBrokerAdapter` (Layer B) never calls `_submit_with_idempotency` -- it has no `submit_order`
implementation at all, by design (Sec CEO safety rules: read-only, no trading calls of any kind).
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, TypeVar

from ai_trader.execution_engine.adapters.connection import (
    BrokerCredentials,
    ConnectionResult,
    ConnectionState,
)
from ai_trader.execution_engine.adapters.exceptions import RetryExhaustedError, SafetyRefusalError
from ai_trader.execution_engine.types import BrokerAck, OrderRequest

_T = TypeVar("_T")


class TransientOperationError(Exception):
    """Internal signal an operation failed in a way worth retrying (e.g. a momentary I/O hiccup) --
    never raised across a public `BrokerAdapter`/`BrokerConnectionLifecycle` method boundary; always
    caught by `_call_with_retry` and converted into either a successful retry or a `RetryExhaustedError`.
    """


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Explicit, versioned-by-value, never a hidden constant (this project's own standing "no hidden
    constants" discipline, `EvidencePolicy`'s/`SufficiencyPolicy`'s own precedent). Bounded by
    construction -- `max_attempts` is always finite, never infinite retry."""

    max_attempts: int = 3
    base_delay_seconds: float = 0.1
    backoff_multiplier: float = 2.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError(f"RetryPolicy.max_attempts must be >= 1, got {self.max_attempts!r}")
        if self.base_delay_seconds < 0:
            raise ValueError("RetryPolicy.base_delay_seconds must be >= 0")
        if self.backoff_multiplier < 1:
            raise ValueError("RetryPolicy.backoff_multiplier must be >= 1")


class RealBrokerAdapterBase(ABC):
    """Abstract base for every real (non-`ExecutionSimulator`) `BrokerAdapter` implementation. Owns
    connection state, idempotency bookkeeping, and retry -- delegates venue-specific I/O to subclass
    hooks. Sleeps between retries are injected via `_sleep` (defaults to `time.sleep`) so tests never
    need to wait on a real clock (`tests/test_retry_idempotency.py` overrides it with a no-op)."""

    def __init__(
        self, credentials: BrokerCredentials | None = None, retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._credentials = credentials if credentials is not None else BrokerCredentials()
        self._retry_policy = retry_policy if retry_policy is not None else RetryPolicy()
        self._state = ConnectionState.DISCONNECTED
        self._last_heartbeat: int | None = None
        self._submitted_client_order_ids: dict[str, BrokerAck] = {}
        self._sleep: Callable[[float], None] = time.sleep

    # ------------------------------------------------------------------ BrokerConnectionLifecycle

    def connect(self) -> ConnectionResult:
        self._state = ConnectionState.CONNECTING
        try:
            result = self._call_with_retry(self._do_connect, "connect")
        except SafetyRefusalError:
            # A safety-gate refusal is never retried and never becomes CONNECTED -- it propagates
            # immediately, exactly as the CEO's own mandatory refusal conditions require.
            self._state = ConnectionState.REFUSED
            self._safe_disconnect_after_refusal()
            raise
        except RetryExhaustedError:
            self._state = ConnectionState.DISCONNECTED
            raise
        if result.accepted:
            self._state = ConnectionState.CONNECTED
            self._last_heartbeat = result.connected_as_of
        else:
            self._state = ConnectionState.DISCONNECTED
        return result

    def disconnect(self) -> None:
        if self._state is ConnectionState.DISCONNECTED:
            return  # idempotent, per BrokerConnectionLifecycle's own contract
        self._do_disconnect()
        self._state = ConnectionState.DISCONNECTED

    def is_connected(self) -> bool:
        return self._state is ConnectionState.CONNECTED

    def last_heartbeat_as_of(self) -> int | None:
        return self._last_heartbeat

    def heartbeat(self) -> bool:
        if not self.is_connected():
            return False
        alive = self._do_heartbeat_check()
        if alive:
            self._last_heartbeat = int(time.time())
        return alive

    def connection_state(self) -> ConnectionState:
        return self._state

    # ------------------------------------------------------------------ idempotency + retry (shared)

    def _submit_with_idempotency(
        self, order: OrderRequest, do_submit: Callable[[], BrokerAck],
    ) -> BrokerAck:
        """Called by a subclass's own `submit_order` (only relevant to a subclass that submits orders
        at all -- `MT5ReadOnlyBrokerAdapter` never calls this). `client_order_id` (already a field on
        `OrderRequest`, unmodified) is the idempotency key: a retried/duplicate submission for the SAME
        `client_order_id` returns the ORIGINAL ack, never attempts a second real submission."""
        existing = self._submitted_client_order_ids.get(order.client_order_id)
        if existing is not None:
            return existing
        ack = self._call_with_retry(do_submit, "submit_order")
        self._submitted_client_order_ids[order.client_order_id] = ack
        return ack

    def _call_with_retry(self, operation: Callable[[], _T], operation_name: str) -> _T:
        delay = self._retry_policy.base_delay_seconds
        last_reason: str | None = None
        for attempt in range(1, self._retry_policy.max_attempts + 1):
            try:
                return operation()
            except TransientOperationError as exc:
                last_reason = str(exc)
                if attempt < self._retry_policy.max_attempts:
                    self._sleep(delay)
                    delay *= self._retry_policy.backoff_multiplier
        raise RetryExhaustedError(
            f"{operation_name} failed after {self._retry_policy.max_attempts} attempt(s): {last_reason}"
        )

    # ------------------------------------------------------------------ subclass hooks

    @abstractmethod
    def _do_connect(self) -> ConnectionResult:
        """Venue-specific connect logic. May raise `TransientOperationError` (retried) or a
        `SafetyRefusalError` subclass (never retried, propagates immediately) or return a
        `ConnectionResult` directly."""

    def _do_disconnect(self) -> None:
        """Venue-specific teardown. Default: no-op (a subclass with real resources overrides this)."""

    def _do_heartbeat_check(self) -> bool:
        """Venue-specific liveness check. Default: `True` (already known connected)."""
        return True

    def _safe_disconnect_after_refusal(self) -> None:
        """Best-effort cleanup after a safety refusal -- must never itself raise (a refusal is already
        the important signal; a secondary cleanup failure must not mask it)."""
        try:
            self._do_disconnect()
        except Exception:  # noqa: BLE001 -- deliberately broad: cleanup-after-refusal must never mask
            # the original SafetyRefusalError being propagated by the caller.
            pass

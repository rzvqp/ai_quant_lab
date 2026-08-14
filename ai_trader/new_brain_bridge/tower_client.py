"""Client for the isolated `ve_tower` worker (CEO mandate section 4, 2026-08-14: "Worker-ul produce NUMAI
N3 si N4. Nu produce decizii. Nu trimite ordine.").

**Not wired into `bridge.evaluate_bar`'s production path.** `bridge.py`'s `market_map_available=False,
levels_available=False, confirmation_available=False` hardcodes remain exactly as they are -- explicitly
forbidden to change until `TOWER_HANDOFF_PASS` (installing the real, verified N3/N4 artifact is its own,
later step). This module is infrastructure built ahead of that: tested and correct in isolation, not yet
called by anything that runs against real events.

**No fallback, structurally, not by runtime check**: this file imports nothing from `market_intelligence`,
`pdh_pdl_demo`, `multi_policy_live`, or any broker/execution module (`risk_gate`, `execution_shadow`) --
there is no legacy or broker call anywhere in this module's body for a bug to accidentally reach, the same
"absence, not a guard" discipline `fail_safe.py`'s own docstring establishes for the brain-unavailable
path. A worker failure of any kind (connection refused, timeout, malformed reply, protocol mismatch,
identity mismatch) becomes `TowerUnavailableResult` here -- callers translate that into `NO_TRADE` /
`TOWER_UNAVAILABLE` exactly the way `fail_safe.safe_evaluate_bar` already does for a brain failure."""

from __future__ import annotations

import socket
from dataclasses import dataclass, field

from ai_trader.new_brain_bridge.tower_protocol import (
    CONNECTION_FAILED,
    MALFORMED_RESPONSE,
    PROTOCOL_VERSION,
    PROTOCOL_VERSION_MISMATCH,
    RESPONSE_IDENTITY_MISMATCH,
    STALE_RESPONSE,
    TOWER_UNAVAILABLE,
    TowerProtocolError,
    TowerRequest,
    parse_response_bytes,
    pack_frame,
    unpack_length_prefix,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerN3N4Result:
    """A successful, identity-verified reply. `n3_output`/`n4_output` are opaque dicts -- this client
    does not interpret their contents, matching `mandate2_readiness.event_identity.NodeTrace`'s own
    "record the boundary, never interpret what's inside it" convention."""

    request_id: str
    market_event_id: str
    tower_version: str
    n3_output: dict[str, object] | None
    n4_output: dict[str, object] | None
    reason_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerUnavailableResult:
    """Every failure mode collapses to this one shape -- connection refused, timeout, malformed reply,
    protocol-version mismatch, identity mismatch, stale response, or the worker's own honest
    `TOWER_UNAVAILABLE` (no `ve_tower` installed yet). `reason` is always one of the protocol's own
    reason-code constants, never a free-form string, so callers can branch on it without parsing `detail`."""

    request_id: str
    market_event_id: str
    reason: str
    detail: str


TowerResult = TowerN3N4Result | TowerUnavailableResult


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerClientConfig:
    host: str = "127.0.0.1"
    port: int = 8765
    timeout_seconds: float = 5.0


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    chunks: list[bytes] = []
    remaining = n
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            raise OSError(f"connection closed after {n - remaining} of {n} bytes")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


class TowerClient:
    """One instance per caller. Holds an in-process cache keyed by `(request_id, event_fingerprint)` so a
    genuine retry of the SAME request never re-hits the network and always returns the SAME result --
    "cerere duplicata -> rezultat IDEMPOTENT" implemented as a real cache, not merely as "the worker
    happens to be a pure function" (defense in depth against a future, less-pure worker implementation)."""

    def __init__(self, config: TowerClientConfig | None = None) -> None:
        self._config = config or TowerClientConfig()
        self._cache: dict[tuple[str, str], TowerResult] = {}

    def request_n3_n4(self, request: TowerRequest) -> TowerResult:
        cache_key = (request.request_id, request.event_fingerprint)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        result = self._do_request(request)
        self._cache[cache_key] = result
        return result

    def health_check(self) -> bool:
        """Minimal TCP connect-and-close. Never raises -- a health check that itself can throw defeats
        the purpose of a fail-closed availability probe."""
        try:
            with socket.create_connection(
                (self._config.host, self._config.port), timeout=self._config.timeout_seconds
            ):
                return True
        except OSError:
            return False

    def _do_request(self, request: TowerRequest) -> TowerResult:
        try:
            payload = pack_frame(request.to_json_bytes())
        except TowerProtocolError as exc:
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=str(exc).split(":", 1)[0], detail=str(exc),
            )
        try:
            with socket.create_connection(
                (self._config.host, self._config.port), timeout=self._config.timeout_seconds
            ) as sock:
                sock.sendall(payload)
                prefix = _recv_exact(sock, 4)
                length = unpack_length_prefix(prefix)
                raw = _recv_exact(sock, length)
        except (OSError, TowerProtocolError) as exc:
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=CONNECTION_FAILED, detail=str(exc),
            )

        try:
            response = parse_response_bytes(raw)
        except TowerProtocolError as exc:
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=MALFORMED_RESPONSE, detail=str(exc),
            )

        if response.protocol_version != PROTOCOL_VERSION:
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=PROTOCOL_VERSION_MISMATCH,
                detail=f"client={PROTOCOL_VERSION} worker={response.protocol_version}",
            )

        if response.request_id == request.request_id and response.event_fingerprint != request.event_fingerprint:
            # Same request_id, different event -- a stale/reused-identity reply, not a fresh answer to
            # THIS request. Distinguished from the generic mismatch below because the specific failure
            # mode (identity reuse across events) is diagnostically different from "answered the wrong
            # request outright".
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=STALE_RESPONSE,
                detail=(
                    f"request_id matched but event_fingerprint differs: "
                    f"sent={request.event_fingerprint} received={response.event_fingerprint}"
                ),
            )
        if (
            response.request_id != request.request_id
            or response.market_event_id != request.market_event_id
            or response.event_fingerprint != request.event_fingerprint
        ):
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=RESPONSE_IDENTITY_MISMATCH,
                detail=(
                    f"sent request_id={request.request_id} market_event_id={request.market_event_id} "
                    f"event_fingerprint={request.event_fingerprint}; received request_id="
                    f"{response.request_id} market_event_id={response.market_event_id} "
                    f"event_fingerprint={response.event_fingerprint}"
                ),
            )

        if not response.ok:
            reason = response.reason_codes[0] if response.reason_codes else TOWER_UNAVAILABLE
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=reason, detail=", ".join(response.reason_codes) or TOWER_UNAVAILABLE,
            )

        return TowerN3N4Result(
            request_id=response.request_id,
            market_event_id=response.market_event_id,
            tower_version=response.tower_version,
            n3_output=response.n3_output,
            n4_output=response.n4_output,
            reason_codes=response.reason_codes,
        )

"""Client for the isolated `ve_tower` worker (CEO mandate section 4, 2026-08-14: "Worker-ul produce NUMAI
N3 si N4. Nu produce decizii. Nu trimite ordine."), extended 2026-08-14 (Red Team remediation,
`TOWER_HANDOFF_CONDITIONAL`) with session-handshake binding and a bounded cache.

**Requires an `EstablishedSession`** (from `tower_launcher.TowerWorkerLauncher.launch_and_handshake`) --
without one, every call refuses immediately with `HANDSHAKE_NOT_ESTABLISHED`, before any network I/O.
Every response is checked against the session's own `session_id`/`worker_identity_fingerprint` -- a reply
from a different session (a restarted worker, a stale connection, an impostor) is refused with
`STALE_SESSION` even if it would otherwise look like a perfectly well-formed answer.

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
identity mismatch, stale session) becomes `TowerUnavailableResult` here -- callers translate that into
`NO_TRADE` / `TOWER_UNAVAILABLE` exactly the way `fail_safe.safe_evaluate_bar` already does for a brain
failure."""

from __future__ import annotations

import socket
from dataclasses import dataclass

from ai_trader.new_brain_bridge.tower_cache import BoundedTowerCache, CacheMetrics
from ai_trader.new_brain_bridge.tower_launcher import EstablishedSession
from ai_trader.new_brain_bridge.tower_protocol import (
    CONNECTION_FAILED,
    HANDSHAKE_NOT_ESTABLISHED,
    MALFORMED_RESPONSE,
    PROTOCOL_VERSION,
    PROTOCOL_VERSION_MISMATCH,
    REQUEST_ID_REUSE_MISMATCH,
    RESPONSE_IDENTITY_MISMATCH,
    STALE_RESPONSE,
    STALE_SESSION,
    TOWER_UNAVAILABLE,
    TowerProtocolError,
    TowerRequest,
    parse_response_bytes,
    pack_frame,
    unpack_length_prefix,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerN3N4Result:
    """A successful, session-and-identity-verified reply. `n3_output`/`n4_output` are opaque dicts -- this
    client does not interpret their contents, matching `mandate2_readiness.event_identity.NodeTrace`'s own
    "record the boundary, never interpret what's inside it" convention.

    `event_fingerprint` is `ve_tower`'s OWN artifact-dependent identity for this event (see 2026-08-14
    correction below) -- recorded here for downstream provenance, never compared against anything the
    client sent.

    `session_id`/`worker_identity_fingerprint` (Red Team RT-MANDATE2-0002 remediation, 2026-08-16):
    the SAME values `_do_request` already verified match `self._session` before ever constructing this
    result -- exposed here so callers can propagate the AUTHORITATIVE, worker-verified session/identity
    downstream (telemetry, N6, Risk Manager) instead of recomputing or fabricating a substitute. Never a
    fresh claim; always the already-checked session values."""

    request_id: str
    market_event_id: str
    event_fingerprint: str
    tower_version: str
    n3_output: dict[str, object] | None
    n4_output: dict[str, object] | None
    reason_codes: tuple[str, ...]
    session_id: str
    worker_identity_fingerprint: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerUnavailableResult:
    """Every failure mode collapses to this one shape -- connection refused, timeout, malformed reply,
    protocol-version mismatch, identity mismatch, stale response/session, no established handshake, a
    reused request_id with a different payload, or the worker's own honest `TOWER_UNAVAILABLE` (no
    `ve_tower` installed yet). `reason` is always one of the protocol's own reason-code constants, never a
    free-form string, so callers can branch on it without parsing `detail`."""

    request_id: str
    market_event_id: str
    reason: str
    detail: str


TowerResult = TowerN3N4Result | TowerUnavailableResult


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerClientConfig:
    host: str = "127.0.0.1"
    port: int = 0
    timeout_seconds: float = 5.0
    cache_max_entries: int = 1000
    cache_ttl_seconds: float = 300.0


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
    """One instance per established session. `session=None` means no handshake has ever been performed
    (or the last one failed) -- every call refuses immediately, before touching the network."""

    def __init__(self, config: TowerClientConfig | None = None, *, session: EstablishedSession | None = None) -> None:
        self._config = config or TowerClientConfig()
        self._session = session
        self._cache: BoundedTowerCache[TowerResult] = BoundedTowerCache(
            max_entries=self._config.cache_max_entries, ttl_seconds=self._config.cache_ttl_seconds,
        )

    @property
    def cache_metrics(self) -> CacheMetrics:
        return self._cache.metrics

    def bind_session(self, session: EstablishedSession | None) -> None:
        """Rebinding to a new (or no) session clears the cache -- a cached result belongs to the session
        that produced it (CEO mandate: "stergere la schimbarea session_id, stergere la restart")."""
        self._session = session
        self._cache.clear()

    def request_n3_n4(self, request: TowerRequest) -> TowerResult:
        if self._session is None:
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=HANDSHAKE_NOT_ESTABLISHED, detail="no established session -- handshake was never performed or failed",
            )
        if self._cache.check_reuse(request.request_id, request.event_fingerprint):
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=REQUEST_ID_REUSE_MISMATCH,
                detail=f"request_id {request.request_id!r} was already used with a different event_fingerprint",
            )
        cached = self._cache.get(request.request_id, request.event_fingerprint)
        if cached is not None:
            return cached
        result = self._do_request(request)
        self._cache.put(request.request_id, request.event_fingerprint, result)
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
        assert self._session is not None
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

        # 2026-08-14 correction (Phase 2, first real -- non-stub -- worker response): `event_fingerprint`
        # is `ve_tower`'s OWN artifact-dependent identity (see `ve_tower.fingerprint.event_fingerprint`,
        # which folds in the installed package's version + vendored source commits) -- the client, running
        # in a venv that never has `ve_tower` installed, structurally CANNOT compute the correct value in
        # advance to compare against. Comparing it here was only ever satisfied because the STUB echoed
        # back whatever the client sent; a genuine response could never match. `request_id` (client-
        # generated, echoed) and `market_event_id` (an honest echo of a value that already uniquely
        # identifies the event -- see `bridge.py`'s own `f"{symbol}:{timeframe}:{ts_close}"` convention)
        # remain the two identifiers BOTH sides can actually agree on; `event_fingerprint` is recorded on
        # the result below for provenance, never required to match a client-side guess.
        if response.request_id != request.request_id:
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=RESPONSE_IDENTITY_MISMATCH,
                detail=(
                    f"sent request_id={request.request_id}; received request_id={response.request_id}"
                ),
            )
        if response.market_event_id != request.market_event_id:
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=STALE_RESPONSE,
                detail=(
                    f"request_id matched but market_event_id differs: "
                    f"sent={request.market_event_id} received={response.market_event_id}"
                ),
            )

        if (
            response.session_id != self._session.session_id
            or response.worker_identity_fingerprint != self._session.worker_identity_fingerprint
        ):
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=STALE_SESSION,
                detail=(
                    f"expected session_id={self._session.session_id!r} "
                    f"fingerprint={self._session.worker_identity_fingerprint!r}; received "
                    f"session_id={response.session_id!r} fingerprint={response.worker_identity_fingerprint!r}"
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
            event_fingerprint=response.event_fingerprint,
            tower_version=response.tower_version,
            n3_output=response.n3_output,
            n4_output=response.n4_output,
            reason_codes=response.reason_codes,
            session_id=response.session_id,
            worker_identity_fingerprint=response.worker_identity_fingerprint,
        )

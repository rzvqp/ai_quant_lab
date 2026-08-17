"""Client for the isolated `ve_tower` worker (CEO mandate section 4, 2026-08-14: "Worker-ul produce NUMAI
N3 si N4. Nu produce decizii. Nu trimite ordine."), extended 2026-08-14 (Red Team remediation,
`TOWER_HANDOFF_CONDITIONAL`) with session-handshake binding and a bounded cache.

**v3, 2026-08-17 (RT-TOWER-0008, `N2_HANDOFF_PASS`/`N2_CHAIN_BINDING_PASS`)**: `request_n3_n4`/
`TowerN3N4Result` renamed to `request_chain`/`TowerChainResult` -- the worker now runs N2 as well (a real,
chain-internal producer, never client-supplied), so the old name understated what a call actually does.
Dedup/cache key changes from `(request_id, event_fingerprint)` -- `event_fingerprint` no longer exists as
a client-asserted request field in v3 -- to `(request_id, correlation_id)`, the CEO's own explicit "shared
identity" field that persists across the whole N1->N6 trace.

**Requires an `EstablishedSession`** (from `tower_launcher.TowerWorkerLauncher.launch_and_handshake`) --
without one, every call refuses immediately with `HANDSHAKE_NOT_ESTABLISHED`, before any network I/O.
Every response is checked against the session's own `session_id`/`worker_identity_fingerprint` -- a reply
from a different session (a restarted worker, a stale connection, an impostor) is refused with
`STALE_SESSION` even if it would otherwise look like a perfectly well-formed answer.

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
    TowerChainRequest,
    TowerProtocolError,
    parse_chain_response_bytes,
    pack_frame,
    unpack_length_prefix,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerChainResult:
    """A successful, session-and-identity-verified reply. `n2_output`/`n3_output`/`n4_output` are opaque
    dicts -- this client does not interpret their contents, matching
    `mandate2_readiness.event_identity.NodeTrace`'s own "record the boundary, never interpret what's
    inside it" convention.

    `chain_fingerprint` is `ve_tower`'s OWN artifact-dependent identity for this whole chain call --
    recorded here for downstream provenance, never compared against anything the client sent (the client,
    running in a venv that never has `ve_tower` installed, structurally cannot compute it in advance).

    `session_id`/`worker_identity_fingerprint`: the SAME values `_do_request` already verified match
    `self._session` before ever constructing this result -- exposed here so callers can propagate the
    AUTHORITATIVE, worker-verified session/identity downstream (telemetry, N6, Risk Manager) instead of
    recomputing or fabricating a substitute. Never a fresh claim; always the already-checked session
    values."""

    request_id: str
    market_event_id: str
    correlation_id: str
    configuration_fingerprint: str
    tower_version: str
    chain_binding_version: str
    chain_response_contract_version: str
    chain_fingerprint: str
    chain_status: str
    terminal_reason_code: str
    n2_output: dict[str, object] | None
    n3_output: dict[str, object] | None
    n4_output: dict[str, object] | None
    reason_codes: tuple[str, ...]
    session_id: str
    worker_identity_fingerprint: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerUnavailableResult:
    """Every failure mode collapses to this one shape -- connection refused, timeout, malformed reply,
    protocol-version mismatch, identity mismatch, stale response/session, no established handshake, a
    reused request_id with a different payload, an unknown request field, or the worker's own honest
    `TOWER_UNAVAILABLE` (no `ve_tower` installed yet). `reason` is always one of the protocol's own
    reason-code constants, never a free-form string, so callers can branch on it without parsing `detail`."""

    request_id: str
    market_event_id: str
    reason: str
    detail: str


TowerResult = TowerChainResult | TowerUnavailableResult


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

    @property
    def session(self) -> EstablishedSession | None:
        """Read-only -- for callers that need to report the bound session's own identity (e.g. a
        heartbeat) without duplicating `bind_session`'s own bookkeeping. `None` means no handshake has
        ever succeeded, exactly matching `request_chain`'s own `HANDSHAKE_NOT_ESTABLISHED` condition."""
        return self._session

    def bind_session(self, session: EstablishedSession | None) -> None:
        """Rebinding to a new (or no) session clears the cache -- a cached result belongs to the session
        that produced it (CEO mandate: "stergere la schimbarea session_id, stergere la restart")."""
        self._session = session
        self._cache.clear()

    def request_chain(self, request: TowerChainRequest) -> TowerResult:
        if self._session is None:
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=HANDSHAKE_NOT_ESTABLISHED, detail="no established session -- handshake was never performed or failed",
            )
        if self._cache.check_reuse(request.request_id, request.correlation_id):
            return TowerUnavailableResult(
                request_id=request.request_id, market_event_id=request.market_event_id,
                reason=REQUEST_ID_REUSE_MISMATCH,
                detail=f"request_id {request.request_id!r} was already used with a different correlation_id",
            )
        cached = self._cache.get(request.request_id, request.correlation_id)
        if cached is not None:
            return cached
        result = self._do_request(request)
        self._cache.put(request.request_id, request.correlation_id, result)
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

    def _do_request(self, request: TowerChainRequest) -> TowerResult:
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
            response = parse_chain_response_bytes(raw)
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

        # `request_id` (client-generated, echoed) and `market_event_id` (an honest echo of a value that
        # already uniquely identifies the event -- see `bridge.py`'s own
        # `f"{symbol}:{timeframe}:{ts_close}"` convention) are the two identifiers BOTH sides can actually
        # agree on in advance; `chain_fingerprint` is `ve_tower`'s OWN artifact-dependent identity,
        # recorded on the result below for provenance, never required to match a client-side guess.
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

        return TowerChainResult(
            request_id=response.request_id,
            market_event_id=response.market_event_id,
            correlation_id=response.correlation_id,
            configuration_fingerprint=response.configuration_fingerprint,
            tower_version=response.tower_version,
            chain_binding_version=response.chain_binding_version,
            chain_response_contract_version=response.chain_response_contract_version,
            chain_fingerprint=response.chain_fingerprint,
            chain_status=response.chain_status,
            terminal_reason_code=response.terminal_reason_code,
            n2_output=response.n2_output,
            n3_output=response.n3_output,
            n4_output=response.n4_output,
            reason_codes=response.reason_codes,
            session_id=response.session_id,
            worker_identity_fingerprint=response.worker_identity_fingerprint,
        )

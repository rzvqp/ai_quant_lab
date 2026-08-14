"""`TowerWorkerLauncher` -- owns the FULL isolated-worker lifecycle: spawn, session-secret handoff over
stdin, readiness parsing, the challenge-response HMAC handshake, and identity-pin verification (CEO/Red
Team remediation, 2026-08-14, `TOWER_HANDOFF_CONDITIONAL`).

**Two independent sources of truth, never conflated** (the CEO's own explicit correction): the HMAC proves
SESSION POSSESSION (this really is the process I just spawned, not an old/stale/wrong server on the same
port); `tower_identity_pin.verify_pin` proves ARTIFACT IDENTITY (it's genuinely running `ve_tower` 0.3.0,
build `6daf2aa`, not merely something that knows the secret). A worker passing one check but not the other
is still refused.

Not wired into `bridge.py`'s production path -- built and tested in isolation, matching the standing
constraint from the isolation-infrastructure segment this extends.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from ai_trader.new_brain_bridge.tower_identity_pin import verify_pin
from ai_trader.new_brain_bridge.tower_protocol import (
    CONNECTION_FAILED,
    HANDSHAKE_HMAC_MISMATCH,
    HANDSHAKE_IDENTITY_MISMATCH,
    HANDSHAKE_SESSION_ID_MISMATCH,
    MALFORMED_RESPONSE,
    NON_LOOPBACK_BIND_FORBIDDEN,
    HandshakeRequest,
    HandshakeResponse,
    TowerProtocolError,
    WorkerIdentity,
    pack_frame,
    parse_handshake_response_bytes,
    unpack_length_prefix,
)

LOOPBACK_ALLOWED_HOSTS = ("127.0.0.1",)
TOWER_WORKER_STARTUP_FAILED = "TOWER_WORKER_STARTUP_FAILED"


@dataclass(frozen=True, slots=True, kw_only=True)
class EstablishedSession:
    session_id: str
    worker_identity: WorkerIdentity
    worker_identity_fingerprint: str
    host: str
    port: int
    pid: int
    process_start_identity: str


@dataclass(frozen=True, slots=True, kw_only=True)
class HandshakeFailure:
    reason: str
    detail: str


LaunchResult = EstablishedSession | HandshakeFailure


def verify_handshake_response(
    response: HandshakeResponse, *, expected_session_id: str, session_secret: bytes, challenge_hex: str,
    host: str = "127.0.0.1", port: int = 0,
) -> LaunchResult:
    """The two independent checks, in isolation from any socket I/O -- directly unit-testable against a
    hand-built `HandshakeResponse` (see `test_tower_launcher.py`), exactly the logic a real connection
    also goes through in `TowerWorkerLauncher._perform_handshake`."""
    if response.session_id != expected_session_id:
        return HandshakeFailure(
            reason=HANDSHAKE_SESSION_ID_MISMATCH,
            detail=f"handshake response session_id={response.session_id!r}, expected {expected_session_id!r}",
        )

    expected_hmac = hmac.new(
        session_secret,
        (challenge_hex + response.identity.canonical_json() + response.session_id).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected_hmac, response.hmac_hex):
        return HandshakeFailure(
            reason=HANDSHAKE_HMAC_MISMATCH,
            detail="HMAC does not match -- wrong session secret, or the claimed identity was altered "
                   "after the worker computed its own HMAC",
        )

    mismatches = verify_pin(response.identity)
    if mismatches:
        detail = ", ".join(f"{m.field}: expected={m.expected!r} actual={m.actual!r}" for m in mismatches)
        return HandshakeFailure(reason=HANDSHAKE_IDENTITY_MISMATCH, detail=detail)

    return EstablishedSession(
        session_id=response.session_id, worker_identity=response.identity,
        worker_identity_fingerprint=response.identity.fingerprint(), host=host, port=port,
        pid=response.pid, process_start_identity=response.process_start_identity,
    )


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


class TowerWorkerLauncher:
    def __init__(
        self, *, tower_python: Path, host: str = "127.0.0.1", timeout_seconds: float = 10.0,
        extra_env: dict[str, str] | None = None, run_dir: Path | None = None,
    ) -> None:
        if host not in LOOPBACK_ALLOWED_HOSTS:
            raise ValueError(f"{NON_LOOPBACK_BIND_FORBIDDEN}: {host!r} is not an allowed loopback address")
        self._tower_python = tower_python
        self._host = host
        self._timeout_seconds = timeout_seconds
        self._extra_env = dict(extra_env) if extra_env else {}
        self._run_dir = run_dir
        self.process: subprocess.Popen[str] | None = None

    def launch_and_handshake(self, requested_port: int = 0) -> LaunchResult:
        session_id = secrets.token_hex(16)
        session_secret = secrets.token_bytes(32)

        env = {"SystemRoot": "C:\\Windows"}
        env.update(self._extra_env)
        self.process = subprocess.Popen(
            [str(self._tower_python), "-I", "-m", "ve_tower_worker.cli", "--host", self._host,
             "--port", str(requested_port)],
            cwd=str(self._run_dir) if self._run_dir is not None else None, env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        assert self.process.stdin is not None
        secret_line = json.dumps({"session_id": session_id, "session_secret_hex": session_secret.hex()})
        self.process.stdin.write(secret_line + "\n")
        self.process.stdin.flush()
        self.process.stdin.close()

        readiness = self._wait_for_readiness()
        if readiness is None:
            return HandshakeFailure(reason=TOWER_WORKER_STARTUP_FAILED, detail="worker did not report ready in time")
        host, port, echoed_session_id = readiness
        if echoed_session_id != session_id:
            return HandshakeFailure(
                reason=HANDSHAKE_SESSION_ID_MISMATCH,
                detail=f"readiness line echoed session_id={echoed_session_id!r}, expected {session_id!r}",
            )

        try:
            return self._perform_handshake(host, port, session_id, session_secret)
        except OSError as exc:
            return HandshakeFailure(reason=CONNECTION_FAILED, detail=str(exc))

    def _wait_for_readiness(self, timeout: float | None = None) -> tuple[str, int, str] | None:
        assert self.process is not None and self.process.stdout is not None
        deadline = time.monotonic() + (timeout if timeout is not None else self._timeout_seconds)
        while time.monotonic() < deadline:
            line: str = self.process.stdout.readline()
            if line:
                if "TOWER_WORKER_READY" in line:
                    try:
                        payload = json.loads(line.split("TOWER_WORKER_READY", 1)[1].strip())
                        return payload["host"], int(payload["port"]), payload["session_id"]
                    except (json.JSONDecodeError, KeyError, ValueError, IndexError):
                        return None
                if "TOWER_WORKER_STARTUP_FAILED" in line:
                    return None
            elif self.process.poll() is not None:
                return None
        return None

    def _perform_handshake(
        self, host: str, port: int, session_id: str, session_secret: bytes,
    ) -> LaunchResult:
        challenge = secrets.token_bytes(32)
        request = HandshakeRequest(session_id=session_id, challenge_hex=challenge.hex())
        with socket.create_connection((host, port), timeout=self._timeout_seconds) as sock:
            sock.sendall(pack_frame(request.to_json_bytes()))
            prefix = _recv_exact(sock, 4)
            length = unpack_length_prefix(prefix)
            raw = _recv_exact(sock, length)

        try:
            response = parse_handshake_response_bytes(raw)
        except TowerProtocolError as exc:
            return HandshakeFailure(reason=MALFORMED_RESPONSE, detail=str(exc))

        return verify_handshake_response(
            response, expected_session_id=session_id, session_secret=session_secret,
            challenge_hex=challenge.hex(), host=host, port=port,
        )

    def stop(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.kill()
            self.process.wait(timeout=5.0)

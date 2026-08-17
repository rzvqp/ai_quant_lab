"""Console-script entrypoint (`ve-tower-worker`, see `pyproject.toml`'s `[project.scripts]`). This is the
ONLY supported way to start the worker -- installed into the tower venv's `Scripts/` directory by a
non-editable `pip install .`, so at runtime it is invoked as `<tower_venv>\\Scripts\\ve-tower-worker.exe`
(or, per `launch_tower_worker.ps1`/`TowerWorkerLauncher`, `-I -m ve_tower_worker.cli` for interpreter-flag
control), never as `python -m` against a path inside the AI Trader repository.

**Session secret handoff, over stdin, never argv or the network** (CEO mandate: "Il transmite prin canal
de LANSARE controlat, NU prin protocolul public dupa conectare"). The FIRST line of stdin must be a JSON
object `{"session_id": ..., "session_secret_hex": ...}`, written by the launching parent process
immediately after spawning this one. Read exactly once, at startup, before the server binds anything --
never re-read, never logged, never echoed back on the TCP socket.

Order of operations: (1) the sys.path/sys.modules contamination audit, (2) read the session secret from
stdin, (3) validate `--host` is an allowed loopback address, (4) bind and announce readiness on stdout.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import signal
import sys
from types import FrameType

from ve_tower_worker.artifact_identity import read_real_worker_identity
from ve_tower_worker.server import IdentityFn, NonLoopbackBindError, TowerWorkerServer
from ve_tower_worker.startup_audit import (
    TowerWorkerStartupFailed,
    enforce_chain_identity_complete,
    enforce_startup_audit,
)

DEFAULT_PORT = 0
"""Ephemeral by default -- the worker binds whatever the OS assigns and reports the real port back over
stdout (the controlled channel), rather than the launcher blindly trusting a fixed port (CEO mandate:
"clientul NU foloseste orbeste un port fix")."""

TEST_IDENTITY_ENV_VAR = "VE_TOWER_WORKER_TEST_IDENTITY"
"""Set to '1' ONLY by integration tests that need to exercise the handshake-ACCEPTED path against a real
subprocess without installing `ve_tower`. Never set by any real launch script. See
`artifact_identity_stub.py`'s own module docstring."""


def _install_signal_handlers(server: TowerWorkerServer) -> None:
    def _handle(signum: int, frame: FrameType | None) -> None:
        server.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, _handle)
    signal.signal(signal.SIGTERM, _handle)


def _read_session_secret_from_stdin() -> tuple[str, bytes] | None:
    """Returns `(session_id, session_secret_bytes)`, or `None` if stdin closed without a valid line."""
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    session_id = obj.get("session_id")
    session_secret_hex = obj.get("session_secret_hex")
    if not isinstance(session_id, str) or not session_id:
        return None
    if not isinstance(session_secret_hex, str) or not session_secret_hex:
        return None
    try:
        session_secret = bytes.fromhex(session_secret_hex)
    except ValueError:
        return None
    return session_id, session_secret


def _identity_fn() -> IdentityFn:
    if os.environ.get(TEST_IDENTITY_ENV_VAR) == "1":
        from ve_tower_worker.artifact_identity_stub import stub_read_worker_identity

        return stub_read_worker_identity
    return read_real_worker_identity


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ve-tower-worker")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)

    try:
        enforce_startup_audit()
    except TowerWorkerStartupFailed as exc:
        print(str(exc), file=sys.stderr)
        return 1

    session = _read_session_secret_from_stdin()
    if session is None:
        print(
            "TOWER_WORKER_STARTUP_FAILED: no valid session secret handed off via stdin -- "
            "expected a JSON line {\"session_id\": ..., \"session_secret_hex\": ...} as the first line",
            file=sys.stderr,
        )
        return 1
    session_id, session_secret = session
    process_start_identity = secrets.token_hex(16)

    identity_fn = _identity_fn()
    try:
        enforce_chain_identity_complete(identity_fn())
    except TowerWorkerStartupFailed as exc:
        print(str(exc), file=sys.stderr)
        return 1

    try:
        server = TowerWorkerServer(
            host=args.host, port=args.port, identity_fn=identity_fn,
            session_id=session_id, session_secret=session_secret,
            process_start_identity=process_start_identity,
        )
    except NonLoopbackBindError as exc:
        print(f"TOWER_WORKER_STARTUP_FAILED: {exc}", file=sys.stderr)
        return 1

    _install_signal_handlers(server)
    readiness = {
        "host": server.host, "port": server.port, "session_id": session_id, "pid": os.getpid(),
        "process_start_identity": process_start_identity,
    }
    print(f"TOWER_WORKER_READY {json.dumps(readiness, sort_keys=True)}", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

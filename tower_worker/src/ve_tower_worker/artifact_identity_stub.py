"""**FAKE. TEST-ONLY. NEVER the default.** `artifact_identity.read_real_worker_identity` (used by `cli.py`
by default) is the real production path -- it honestly reports `None` for every `ve_tower`-derived field
today, since `ve_tower` genuinely is not installed, and `None` for `worker_delivery_commit` until a real
`worker_delivery_manifest.json` exists.

This stub exists solely so integration tests can exercise the full "handshake ACCEPTED" path against a
REAL worker subprocess without installing `ve_tower` and without a real delivery manifest -- it returns a
fixed, clearly-synthetic identity that a matching TEST pin (monkeypatched in `test_tower_launcher.py`) is
written to accept. Only activated when the worker process is launched with the environment variable
`VE_TOWER_WORKER_TEST_IDENTITY=1` set (see `cli.py`) -- never set by any real launch script."""

from __future__ import annotations

from pathlib import Path

from ve_tower_worker.artifact_identity import _installed_worker_package_version
from ve_tower_worker.protocol import PROTOCOL_VERSION, WorkerIdentity

STUB_IDENTITY = WorkerIdentity(
    worker_package_version=_installed_worker_package_version(),
    worker_delivery_commit="STUB-TEST-WORKER-DELIVERY-COMMIT-NEVER-REAL",
    protocol_version=PROTOCOL_VERSION,
    ve_tower_package_version="0.3.0",
    package_build_commit="6daf2aa",
    state_delivery_commit="0207ffa",
    wheel_sha256="0c2581c068f3bd7d0c5beff1358af0aa906485d69ed74bf66c8a6d8d0c0120d2",
    vendored_source_identity="STUB-TEST-VENDORED-SOURCE-IDENTITY-NEVER-REAL",
    n3_contract_version="STUB-TEST-N3-CONTRACT-1.0",
    n4_contract_version="STUB-TEST-N4-CONTRACT-1.0",
    n2_contract_version="STUB-TEST-N2-CONTRACT-1.0",
    chain_request_contract_version="STUB-TEST-CHAIN-REQUEST-1.0",
    chain_response_contract_version="STUB-TEST-CHAIN-RESPONSE-1.0",
    tower_chain_binding_version="STUB-TEST-CHAIN-BINDING-1.0",
    production_entrypoint="STUB-TEST-run_tower_chain",
)


def stub_read_worker_identity(*, venv_root: Path | None = None) -> WorkerIdentity:
    return STUB_IDENTITY

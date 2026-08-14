"""The worker's OWN real identity -- read from local, verifiable sources only, never from anything a
client sends. Two sources, cross-checked where possible:

1. This package's own hardcoded, committed constants (`WORKER_PACKAGE_VERSION`, `WORKER_BUILD_COMMIT`) --
   known at build time, true by construction.
2. `install_manifest.py`'s `InstallManifest` -- a JSON file written by install-time tooling **only after
   `verify_tower_wheel.py`'s SHA-256 check passes** (see `tower_worker/env/verify_tower_wheel.py`), plus,
   once `ve_tower` is actually importable, `importlib.metadata.version("ve_tower")` as an independent
   cross-check against what the manifest claims.

**Today, `ve_tower` is not installed anywhere on this machine** -- every `ve_tower`-derived field below is
honestly `None`. This is the correct, fail-closed state until `STAGED_INSTALL_AUTHORIZED` and an actual
install happen -- never fabricated to make a handshake look healthier than it is."""

from __future__ import annotations

import importlib.metadata
import sys
from pathlib import Path

from ve_tower_worker.install_manifest import read_install_manifest
from ve_tower_worker.protocol import PROTOCOL_VERSION, WorkerIdentity

WORKER_PACKAGE_VERSION = "0.2.0"
WORKER_BUILD_COMMIT = "PENDING_COMMIT_PIN"
"""Set to the exact commit hash of the AI Trader commit that produced THIS remediation, per the CEO's own
instruction ("worker_build_commit = commitul NOU pe care AI Trader il va produce prin aceasta remediere").
Necessarily a two-step process (the hash of a commit is unknowable before it exists): committed once with
this placeholder, then updated to the real hash and re-committed immediately after, mirroring the exact
precedent already established in this repo for `wheel_verification.py`'s own `PINNED_WHEEL_SHA256` (built
first, hash recorded in a following commit)."""


def _installed_ve_tower_version() -> str | None:
    try:
        return importlib.metadata.version("ve_tower")
    except importlib.metadata.PackageNotFoundError:
        return None


def read_real_worker_identity(*, venv_root: Path | None = None) -> WorkerIdentity:
    """The REAL identity-reading path -- used by `cli.py` in production. `venv_root` defaults to
    `sys.prefix` (the running venv's own root), overridable only for tests."""
    root = venv_root if venv_root is not None else Path(sys.prefix)
    manifest = read_install_manifest(venv_root=root)
    return WorkerIdentity(
        worker_package_version=WORKER_PACKAGE_VERSION,
        worker_build_commit=WORKER_BUILD_COMMIT,
        protocol_version=PROTOCOL_VERSION,
        ve_tower_package_version=_installed_ve_tower_version(),
        package_build_commit=manifest.package_build_commit if manifest else None,
        state_delivery_commit=manifest.state_delivery_commit if manifest else None,
        wheel_sha256=manifest.wheel_sha256 if manifest else None,
        vendored_source_identity=manifest.vendored_source_identity if manifest else None,
        n3_contract_version=manifest.n3_contract_version if manifest else None,
        n4_contract_version=manifest.n4_contract_version if manifest else None,
    )

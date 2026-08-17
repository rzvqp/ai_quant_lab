"""The worker's OWN real identity -- read from local, verifiable sources only, never from anything a
client sends, and never from a self-referential hardcoded constant. Three sources:

1. `importlib.metadata.version("ve-tower-worker")` -- the installed package's own declared version,
   populated automatically by `pip` from `pyproject.toml` at build time. Not self-referential: this is the
   package reading its OWN metadata the standard way, the same mechanism every Python package uses to know
   its own version at runtime.
2. `worker_delivery_manifest.py`'s `WorkerDeliveryManifest` -- **NEVER a constant hardcoded into this
   package's own source.** CEO correction, 2026-08-14: "Un commit nu isi poate contine propriul hash." The
   prior remediation's `WORKER_BUILD_COMMIT` constant was exactly that mistake -- a commit hash baked into
   the very commit it claimed to identify. The manifest is written by `install_tower_env.ps1` (the
   installer, an EMITTER) running `git rev-parse HEAD` against the AI Trader repo's OWN already-existing
   commit at install time -- the identical precedent VE already established for `ve_brain`'s own
   `artifact_manifest(delivery_commit)`. If no manifest exists yet, `worker_delivery_commit` is honestly
   `None`.
3. `install_manifest.py`'s `InstallManifest` -- a JSON file written by install-time tooling **only after
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
from ve_tower_worker.worker_delivery_manifest import read_worker_delivery_manifest

_WORKER_DISTRIBUTION_NAME = "ve-tower-worker"


def _installed_worker_package_version() -> str:
    return importlib.metadata.version(_WORKER_DISTRIBUTION_NAME)


def _installed_ve_tower_version() -> str | None:
    try:
        return importlib.metadata.version("ve_tower")
    except importlib.metadata.PackageNotFoundError:
        return None


def read_real_worker_identity(*, venv_root: Path | None = None) -> WorkerIdentity:
    """The REAL identity-reading path -- used by `cli.py` in production. `venv_root` defaults to
    `sys.prefix` (the running venv's own root), overridable only for tests."""
    root = venv_root if venv_root is not None else Path(sys.prefix)
    ve_tower_manifest = read_install_manifest(venv_root=root)
    delivery_manifest = read_worker_delivery_manifest(venv_root=root)
    return WorkerIdentity(
        worker_package_version=_installed_worker_package_version(),
        worker_delivery_commit=delivery_manifest.worker_delivery_commit if delivery_manifest else None,
        protocol_version=PROTOCOL_VERSION,
        ve_tower_package_version=_installed_ve_tower_version(),
        package_build_commit=ve_tower_manifest.package_build_commit if ve_tower_manifest else None,
        state_delivery_commit=ve_tower_manifest.state_delivery_commit if ve_tower_manifest else None,
        wheel_sha256=ve_tower_manifest.wheel_sha256 if ve_tower_manifest else None,
        vendored_source_identity=ve_tower_manifest.vendored_source_identity if ve_tower_manifest else None,
        n3_contract_version=ve_tower_manifest.n3_contract_version if ve_tower_manifest else None,
        n4_contract_version=ve_tower_manifest.n4_contract_version if ve_tower_manifest else None,
        n2_contract_version=ve_tower_manifest.n2_contract_version if ve_tower_manifest else None,
        chain_request_contract_version=(
            ve_tower_manifest.chain_request_contract_version if ve_tower_manifest else None
        ),
        chain_response_contract_version=(
            ve_tower_manifest.chain_response_contract_version if ve_tower_manifest else None
        ),
        tower_chain_binding_version=(
            ve_tower_manifest.tower_chain_binding_version if ve_tower_manifest else None
        ),
        production_entrypoint=ve_tower_manifest.production_entrypoint if ve_tower_manifest else None,
        atr_source_commit=ve_tower_manifest.atr_source_commit if ve_tower_manifest else None,
    )

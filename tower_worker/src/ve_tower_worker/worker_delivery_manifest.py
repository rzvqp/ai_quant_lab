"""`WorkerDeliveryManifest` -- the record install-time tooling writes for the `ve_tower_worker` PACKAGE
ITSELF (distinct from `install_manifest.py`'s `InstallManifest`, which describes a `ve_tower` INSTALL
EVENT). CEO correction, 2026-08-14, closing the identity-handshake pin:

"Un commit nu isi poate contine propriul hash." A commit cannot contain its own hash -- so
`worker_delivery_commit` is NEVER a constant hardcoded into this package's own source (that was the
mistake in the prior remediation: `WORKER_BUILD_COMMIT` baked into `artifact_identity.py`, itself part of
the very commit it claimed to identify). The correct pattern, the exact one VE already established for
`ve_brain`'s own `artifact_manifest(delivery_commit)`: the value comes from an EMITTER that runs AFTER a
real commit already exists. `tower_worker/env/install_tower_env.ps1` is that emitter -- it runs
`git -C <repo_root> rev-parse HEAD` against the AI Trader repository's OWN current commit at install time
(a commit that, by construction, already exists and is already pushed by the time you run the installer)
and writes the result here. `artifact_identity.py` only ever READS this file; it never computes or
hardcodes the value itself.

Lives at `<venv_root>/ve_tower_worker_delivery_manifest.json` -- a plain file inside the isolated tower
venv itself, sibling to `install_manifest.py`'s own `ve_tower_install_manifest.json`."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

_MANIFEST_FILENAME = "ve_tower_worker_delivery_manifest.json"


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkerDeliveryManifest:
    worker_package_version: str
    worker_delivery_commit: str
    protocol_version: str
    delivered_at_utc: str
    delivered_by: str


def manifest_path(*, venv_root: Path) -> Path:
    return venv_root / _MANIFEST_FILENAME


def write_worker_delivery_manifest(manifest: WorkerDeliveryManifest, *, venv_root: Path) -> None:
    manifest_path(venv_root=venv_root).write_text(
        json.dumps(asdict(manifest), sort_keys=True, indent=2), encoding="utf-8",
    )


def read_worker_delivery_manifest(*, venv_root: Path) -> WorkerDeliveryManifest | None:
    """Fail-closed on any malformed manifest: returns `None` (treated by callers exactly like "no
    manifest exists yet") rather than raising or returning a partially-populated object."""
    path = manifest_path(venv_root=venv_root)
    if not path.is_file():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(obj, dict):
        return None
    required_str_fields = (
        "worker_package_version", "worker_delivery_commit", "protocol_version", "delivered_at_utc",
        "delivered_by",
    )
    if not all(isinstance(obj.get(f), str) for f in required_str_fields):
        return None
    return WorkerDeliveryManifest(
        worker_package_version=obj["worker_package_version"],
        worker_delivery_commit=obj["worker_delivery_commit"],
        protocol_version=obj["protocol_version"],
        delivered_at_utc=obj["delivered_at_utc"],
        delivered_by=obj["delivered_by"],
    )

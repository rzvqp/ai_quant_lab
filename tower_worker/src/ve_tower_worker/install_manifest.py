"""`InstallManifest` -- the record install-time tooling writes into the tower venv's own root, and ONLY
after `verify_tower_wheel.py`'s SHA-256 check passes (CEO mandate: "manifestul de instalare creat NUMAI
dupa verificarea SHA-ului"). Read back by `artifact_identity.read_real_worker_identity` at every worker
startup -- the worker never re-derives these facts, it reads what install time already verified and
recorded.

Lives at `<venv_root>/ve_tower_install_manifest.json` -- a plain file inside the isolated tower venv
itself, never inside this package's own site-packages location (a manifest describes a specific `ve_tower`
INSTALL EVENT, not a fact about the `ve_tower_worker` package, which stays the same across many possible
`ve_tower` installs/reinstalls over that venv's lifetime)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

_MANIFEST_FILENAME = "ve_tower_install_manifest.json"


@dataclass(frozen=True, slots=True, kw_only=True)
class InstallManifest:
    ve_tower_package_version: str
    package_build_commit: str
    state_delivery_commit: str
    wheel_sha256: str
    wheel_filename: str
    vendored_source_identity: str | None
    n3_contract_version: str | None
    n4_contract_version: str | None
    installed_at_utc: str
    installed_by: str
    verification_note: str
    n2_contract_version: str | None = None
    chain_request_contract_version: str | None = None
    chain_response_contract_version: str | None = None
    tower_chain_binding_version: str | None = None
    production_entrypoint: str | None = None
    atr_source_commit: str | None = None
    """Chain-binding fields (RT-TOWER-0008 remediation, 2026-08-17): `None` for every install manifest
    written before `ve_tower` 0.5.0 (0.3.0/0.4.0 pre-date `run_tower_chain`/N2 entirely) -- honest absence,
    never backfilled or guessed for an old install. A worker reading an old manifest with these `None`
    correctly refuses to claim chain-binding support in its own handshake identity.

    `atr_source_commit` (RT-TOWER-0010, 2026-08-17): `None` for every install manifest written before
    `ve_tower` 0.5.2 (0.5.0/0.5.1 either lacked ATR provenance entirely or shipped a provenance value VE
    itself later corrected)."""


def manifest_path(*, venv_root: Path) -> Path:
    return venv_root / _MANIFEST_FILENAME


def write_install_manifest(manifest: InstallManifest, *, venv_root: Path) -> None:
    manifest_path(venv_root=venv_root).write_text(
        json.dumps(asdict(manifest), sort_keys=True, indent=2), encoding="utf-8",
    )


def read_install_manifest(*, venv_root: Path) -> InstallManifest | None:
    """Fail-closed on any malformed manifest: returns `None` (treated by callers exactly like "no
    manifest exists yet") rather than raising or returning a partially-populated object -- a corrupt
    manifest must never look like a verified one."""
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
        "ve_tower_package_version", "package_build_commit", "state_delivery_commit", "wheel_sha256",
        "wheel_filename", "installed_at_utc", "installed_by", "verification_note",
    )
    if not all(isinstance(obj.get(f), str) for f in required_str_fields):
        return None
    optional_str_fields = (
        "vendored_source_identity", "n3_contract_version", "n4_contract_version", "n2_contract_version",
        "chain_request_contract_version", "chain_response_contract_version", "tower_chain_binding_version",
        "production_entrypoint", "atr_source_commit",
    )
    for f in optional_str_fields:
        if obj.get(f) is not None and not isinstance(obj.get(f), str):
            return None
    return InstallManifest(
        ve_tower_package_version=obj["ve_tower_package_version"],
        package_build_commit=obj["package_build_commit"],
        state_delivery_commit=obj["state_delivery_commit"],
        wheel_sha256=obj["wheel_sha256"],
        wheel_filename=obj["wheel_filename"],
        vendored_source_identity=obj.get("vendored_source_identity"),
        n3_contract_version=obj.get("n3_contract_version"),
        n4_contract_version=obj.get("n4_contract_version"),
        n2_contract_version=obj.get("n2_contract_version"),
        chain_request_contract_version=obj.get("chain_request_contract_version"),
        chain_response_contract_version=obj.get("chain_response_contract_version"),
        tower_chain_binding_version=obj.get("tower_chain_binding_version"),
        production_entrypoint=obj.get("production_entrypoint"),
        atr_source_commit=obj.get("atr_source_commit"),
        installed_at_utc=obj["installed_at_utc"],
        installed_by=obj["installed_by"],
        verification_note=obj["verification_note"],
    )

"""`tower_worker/env/sidecar_verification.py` tests -- CEO mandate, 2026-08-14, `TOWER_METADATA_PASS`
closure: "CITESTE SIDECAR-UL VERIFICAT... ABIA APOI generezi pinul." Proves the verification tool itself
catches a tampered/wrong sidecar BEFORE any pin constant would ever be written from it -- items #4/#5 of
the CEO's own 9-item retest list, at the sidecar level (the pin-level equivalents live in
`test_tower_identity_pin.py`)."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

_ENV_DIR = Path(__file__).resolve().parents[3] / "tower_worker" / "env"
if str(_ENV_DIR) not in sys.path:
    sys.path.insert(0, str(_ENV_DIR))

from sidecar_verification import (  # type: ignore[import-not-found] # noqa: E402
    SidecarVerificationError,
    cross_check_against_existing_pin,
    recompute_vendored_source_identity,
    verify_sidecar,
)

_REAL_SIDECAR_PATH = Path("C:/Users/MEDION GAMING/ai_quant_lab-wp5b/ve_tower/HANDOFF_MANIFEST-0.3.0.json")
"""Schema v1 (0.3.0/0.4.0 historical) -- used below for the v1-specific parsing/mutation tests, which
remain valid regression coverage regardless of which version `tower_identity_pin.py`'s pin currently
targets."""
_REAL_SIDECAR_PATH_V2 = Path("C:/Users/MEDION GAMING/ai_quant_lab-wp5b/ve_tower/HANDOFF_MANIFEST-0.5.0.json")
"""Schema v2, 0.5.0 (RT-TOWER-0008 chain-binding) -- historical as of RT-TOWER-0010 (the pin has since
moved to 0.5.2); kept for its own v2-parsing regression coverage, no longer asserted to match the
CURRENT pin (see `test_the_real_0_5_2_sidecar_cross_checks_clean_against_the_current_pin` for that)."""
_REAL_SIDECAR_PATH_V2_052 = Path("C:/Users/MEDION GAMING/ai_quant_lab-wp5b/ve_tower/HANDOFF_MANIFEST-0.5.2.json")
"""Schema v2, 0.5.2 (RT-TOWER-0010, `TOWER_CHAIN_ATR_PASS`) -- the sidecar `tower_identity_pin.py`'s
CURRENT pin is sourced from; the "matches the existing pin" cross-check must use THIS file, or it would
(correctly) report a mismatch against a pin that has since moved on."""

pytestmark = pytest.mark.skipif(
    not _REAL_SIDECAR_PATH.is_file(), reason="the real VE sidecar manifest is not present on this machine"
)


def _load_real_manifest_dict() -> dict[str, object]:
    return json.loads(_REAL_SIDECAR_PATH.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def _write_manifest(tmp_path: Path, obj: dict[str, object]) -> Path:
    path = tmp_path / "HANDOFF_MANIFEST-mutated.json"
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path


def test_the_real_sidecar_verifies_cleanly() -> None:
    sidecar = verify_sidecar(_REAL_SIDECAR_PATH)
    assert sidecar.ve_tower_package_version == "0.3.0"
    assert sidecar.package_build_commit == "6daf2aa"
    assert sidecar.state_delivery_commit == "0207ffa"
    assert sidecar.wheel_sha256 == "0c2581c068f3bd7d0c5beff1358af0aa906485d69ed74bf66c8a6d8d0c0120d2"
    assert sidecar.n3_contract_version == "tower-n3-request-v2"
    assert sidecar.n4_contract_version == "tower-n4-request-v2"
    assert sidecar.vendored_source_identity == "sha256:4c0deecbec7afc74b1fc7f61898ad10e54b63d3b7c5cad63b80ee8c647a69e1c"
    assert sidecar.artifact_fingerprint == "1b33a5a853a0167e"
    assert sidecar.vendored_module_count == 13


def test_the_0_3_0_sidecar_verifies_cleanly_as_schema_v1_historical() -> None:
    """The 0.3.0 sidecar no longer matches the CURRENT (0.5.0) pin -- expected, since the pin has moved
    on -- but it must still verify cleanly as a well-formed schema-v1 artifact in its own right."""
    sidecar = verify_sidecar(_REAL_SIDECAR_PATH)
    assert sidecar.manifest_schema_version == "ve-tower-handoff-manifest-v1"
    assert sidecar.ve_tower_package_version == "0.3.0"


@pytest.mark.skipif(
    not _REAL_SIDECAR_PATH_V2.is_file(), reason="the real 0.5.0 VE sidecar manifest is not present on this machine",
)
def test_the_0_5_0_sidecar_still_verifies_cleanly_as_schema_v2_historical() -> None:
    """The 0.5.0 sidecar no longer matches the CURRENT (0.5.2) pin -- expected, since the pin has moved on
    again (RT-TOWER-0010) -- but it must still verify cleanly as a well-formed schema-v2 artifact, and its
    own (absent) `atr_source_commit` must be honestly `None`, never backfilled."""
    sidecar = verify_sidecar(_REAL_SIDECAR_PATH_V2)
    assert sidecar.manifest_schema_version == "ve-tower-handoff-manifest-v2"
    assert sidecar.ve_tower_package_version == "0.5.0"
    assert sidecar.atr_source_commit is None


@pytest.mark.skipif(
    not _REAL_SIDECAR_PATH_V2_052.is_file(), reason="the real 0.5.2 VE sidecar manifest is not present on this machine",
)
def test_the_real_0_5_2_sidecar_cross_checks_clean_against_the_current_pin() -> None:
    """RT-TOWER-0010 (2026-08-17, `TOWER_CHAIN_ATR_PASS`): the CURRENT pin is sourced from the 0.5.2
    sidecar -- this is the live version of the CEO's own retest items today, extended with the new
    `atr_source_commit` field."""
    sidecar = verify_sidecar(_REAL_SIDECAR_PATH_V2_052)
    assert sidecar.manifest_schema_version == "ve-tower-handoff-manifest-v2"
    assert sidecar.atr_source_commit == "a80d8a085dfc26e3042beb512a10aa5c5c1ccb62"
    assert cross_check_against_existing_pin(sidecar) == ()


def test_recompute_matches_the_manifests_own_documented_algorithm_manually() -> None:
    """Independent, from-scratch re-derivation of the algorithm itself (not calling verify_sidecar) --
    proves the recompute function is correct, not merely self-consistent with its own caller."""
    manifest = _load_real_manifest_dict()
    blobs = manifest["vendored_blob_sha1"]
    assert isinstance(blobs, dict)
    pairs = sorted(blobs.items())
    import hashlib

    payload = "".join(f"{name} {sha1}\n" for name, sha1 in pairs)
    expected = "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
    assert recompute_vendored_source_identity(blobs) == expected
    assert expected == manifest["vendored_source_identity"]


def test_4_sidecar_with_a_different_wheel_sha_is_rejected(tmp_path: Path) -> None:
    manifest = copy.deepcopy(_load_real_manifest_dict())
    manifest["wheel_sha256"] = "0" * 64
    path = _write_manifest(tmp_path, manifest)
    sidecar = verify_sidecar(path)  # internally self-consistent -- verify_sidecar itself still succeeds
    mismatches = cross_check_against_existing_pin(sidecar)
    assert "wheel_sha256" in mismatches


def test_5_sidecar_with_a_different_aggregate_identity_is_rejected(tmp_path: Path) -> None:
    """A tampered blob hash changes the RECOMPUTED aggregate identity away from the manifest's own
    (untouched) declared value -- verify_sidecar itself must refuse, before any cross-check even runs."""
    manifest = copy.deepcopy(_load_real_manifest_dict())
    blobs = manifest["vendored_blob_sha1"]
    assert isinstance(blobs, dict)
    first_key = sorted(blobs)[0]
    blobs[first_key] = "0" * 40  # tamper one blob's SHA1
    path = _write_manifest(tmp_path, manifest)
    with pytest.raises(SidecarVerificationError, match="vendored_source_identity mismatch"):
        verify_sidecar(path)


def test_wrong_manifest_schema_version_is_rejected(tmp_path: Path) -> None:
    manifest = copy.deepcopy(_load_real_manifest_dict())
    manifest["manifest_schema_version"] = "some-other-schema-v0"
    path = _write_manifest(tmp_path, manifest)
    with pytest.raises(SidecarVerificationError, match="manifest_schema_version"):
        verify_sidecar(path)


def test_wrong_blob_count_is_rejected(tmp_path: Path) -> None:
    manifest = copy.deepcopy(_load_real_manifest_dict())
    blobs = manifest["vendored_blob_sha1"]
    assert isinstance(blobs, dict)
    del blobs[sorted(blobs)[0]]
    path = _write_manifest(tmp_path, manifest)
    with pytest.raises(SidecarVerificationError, match="vendored_blob_sha1 has"):
        verify_sidecar(path)


def test_mismatched_n3_request_response_contract_is_rejected(tmp_path: Path) -> None:
    manifest = copy.deepcopy(_load_real_manifest_dict())
    manifest["n3_response_contract_version"] = "tower-n3-request-v1-different"
    path = _write_manifest(tmp_path, manifest)
    with pytest.raises(SidecarVerificationError, match="n3 request/response"):
        verify_sidecar(path)


def test_missing_required_field_is_rejected(tmp_path: Path) -> None:
    manifest = copy.deepcopy(_load_real_manifest_dict())
    del manifest["artifact_fingerprint"]
    path = _write_manifest(tmp_path, manifest)
    with pytest.raises(SidecarVerificationError, match="artifact_fingerprint"):
        verify_sidecar(path)


def test_nonexistent_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SidecarVerificationError):
        verify_sidecar(tmp_path / "does_not_exist.json")

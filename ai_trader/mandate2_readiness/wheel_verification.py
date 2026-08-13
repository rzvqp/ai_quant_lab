"""`verify_wheel_hash` -- CEO Mandate 2 activation, 2026-08-14: "VERIFICI SHA-256 INAINTE DE INSTALARE.
Daca difera: INTEGRATION_BLOCKED, ARTIFACT_HASH_MISMATCH."

A tiny, standalone primitive -- computes the real file's SHA-256 and compares it byte-for-byte against
the pinned reference. No install, no import, no side effect beyond reading the file; this check must
happen and pass BEFORE anything else touches the wheel."""

from __future__ import annotations

import hashlib
from pathlib import Path

PINNED_WHEEL_SHA256 = "edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11"
PINNED_WHEEL_SIZE_BYTES = 34_250
PINNED_WHEEL_FILENAME = "ve_brain-0.1.3-py3-none-any.whl"
"""CEO, 2026-08-14, "ARTEFACTUL, predat fizic" -- corroborated independently by Red Team's own
`RT-PIN-0001_ve_brain_wheel_a1d2a6d_PASS.md` (identical hash, size, filename)."""


class ArtifactHashMismatchError(Exception):
    """reason_code = ARTIFACT_HASH_MISMATCH."""


def verify_wheel_hash(wheel_path: Path, expected_sha256: str = PINNED_WHEEL_SHA256) -> None:
    """Raises `ArtifactHashMismatchError` if the file at `wheel_path` doesn't exist, isn't exactly
    `PINNED_WHEEL_SIZE_BYTES`, or doesn't hash to `expected_sha256`. Silent on success."""
    if not wheel_path.is_file():
        raise ArtifactHashMismatchError(f"ARTIFACT_HASH_MISMATCH: {wheel_path} does not exist")
    actual_size = wheel_path.stat().st_size
    if actual_size != PINNED_WHEEL_SIZE_BYTES:
        raise ArtifactHashMismatchError(
            f"ARTIFACT_HASH_MISMATCH: size {actual_size} != expected {PINNED_WHEEL_SIZE_BYTES}"
        )
    digest = hashlib.sha256(wheel_path.read_bytes()).hexdigest()
    if digest != expected_sha256:
        raise ArtifactHashMismatchError(
            f"ARTIFACT_HASH_MISMATCH: sha256 {digest} != expected {expected_sha256}"
        )

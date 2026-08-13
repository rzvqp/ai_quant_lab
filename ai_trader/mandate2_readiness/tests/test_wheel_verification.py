"""`verify_wheel_hash` tests -- CEO instruction, Mandate 2 activation 2026-08-14: "VERIFICI SHA-256
INAINTE DE INSTALARE. Daca difera: INTEGRATION_BLOCKED, ARTIFACT_HASH_MISMATCH." Proves the primitive
refuses on every way a delivered file can fail to be the exact pinned wheel: missing, wrong size, wrong
content -- and passes silently only when all three agree."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from ai_trader.mandate2_readiness.wheel_verification import (
    PINNED_WHEEL_SHA256,
    PINNED_WHEEL_SIZE_BYTES,
    ArtifactHashMismatchError,
    verify_wheel_hash,
)


def test_missing_file_raises_hash_mismatch(tmp_path: Path) -> None:
    with pytest.raises(ArtifactHashMismatchError, match="does not exist"):
        verify_wheel_hash(tmp_path / "does_not_exist.whl")


def test_wrong_size_raises_before_hashing(tmp_path: Path) -> None:
    wrong_size = tmp_path / "wrong_size.whl"
    wrong_size.write_bytes(b"x" * (PINNED_WHEEL_SIZE_BYTES - 1))
    with pytest.raises(ArtifactHashMismatchError, match="size"):
        verify_wheel_hash(wrong_size)


def test_right_size_wrong_content_raises_on_hash(tmp_path: Path) -> None:
    """Same byte count as the real wheel but different bytes -- size alone must not be treated as
    sufficient proof of identity."""
    wrong_content = tmp_path / "wrong_content.whl"
    wrong_content.write_bytes(b"y" * PINNED_WHEEL_SIZE_BYTES)
    with pytest.raises(ArtifactHashMismatchError, match="sha256"):
        verify_wheel_hash(wrong_content)


def test_matching_size_and_hash_passes_silently(tmp_path: Path) -> None:
    """Constructs a synthetic file whose SHA-256 is independently computed and passed as the expected
    value -- proves the comparison logic itself, without depending on possessing the real wheel bytes
    in this test environment."""
    synthetic = tmp_path / "synthetic.whl"
    synthetic.write_bytes(b"z" * PINNED_WHEEL_SIZE_BYTES)
    expected = hashlib.sha256(synthetic.read_bytes()).hexdigest()
    verify_wheel_hash(synthetic, expected_sha256=expected)  # no exception -- the assertion


def test_matching_size_but_wrong_expected_hash_still_raises(tmp_path: Path) -> None:
    synthetic = tmp_path / "synthetic.whl"
    synthetic.write_bytes(b"z" * PINNED_WHEEL_SIZE_BYTES)
    with pytest.raises(ArtifactHashMismatchError, match="sha256"):
        verify_wheel_hash(synthetic, expected_sha256="0" * 64)


def test_default_expected_sha256_is_the_pinned_reference() -> None:
    assert PINNED_WHEEL_SHA256 == "edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11"


def test_the_actual_delivered_wheel_verifies_against_the_pin(tmp_path: Path) -> None:
    """End-to-end proof using the REAL wheel bytes for this mandate, copied into this session's own
    scratchpad and re-verified (not just trusted from the CEO's message or Red Team's report) -- skipped
    if that scratchpad copy isn't present in the environment running this test."""
    real_wheel = (
        Path.home()
        / "AppData"
        / "Local"
        / "Temp"
        / "claude"
        / "C--Users-MEDION-GAMING-tradingview-mcp"
        / "cf540937-d5d4-4c13-84a6-8bf2a985969f"
        / "scratchpad"
        / "mandate2_install"
        / "ve_brain-0.1.3-py3-none-any.whl"
    )
    if not real_wheel.is_file():
        pytest.skip("real delivered wheel not present in this environment's scratchpad")
    verify_wheel_hash(real_wheel)  # no exception -- the assertion

"""Fail-closed reader for `config/split_manifest.json` -- the Statistician's mechanical split/embargo
config (published on branch alpha-automation-v1, commit 6dc81a4).

This module NEVER modifies the manifest (the Statistician is the sole author). It verifies the
manifest's self-embedded SHA-256 content hash before trusting any field, and it exposes only what a
loader needs to gate access: the discovery window of a timeframe that is *exactly* status VALIDATED.
Every failure mode -- missing file, bad JSON, hash mismatch, missing/non-VALIDATED status, missing
discovery_range -- raises `ManifestError`, so an unfinished or tampered config blocks access rather
than granting it (fail_closed_default in the manifest itself).
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Final

__all__ = [
    "ManifestError", "MANIFEST_PATH", "load_manifest", "discovery_window",
    "entry_file", "verify_data_file",
]

_ROOT: Final[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH: Final[str] = os.path.join(_ROOT, "config", "split_manifest.json")


class ManifestError(ValueError):
    """Raised when the split manifest cannot be located, hash-verified, or authorizes no access."""


def load_manifest(path: str = MANIFEST_PATH) -> dict[str, Any]:
    """Read and hash-verify the split manifest. Fail-closed on every anomaly.

    The content hash is computed over the exact file bytes with `content_hash.value` set to the empty
    string, per the manifest's own `content_hash.computed_over` contract.
    """
    if not os.path.isfile(path):
        raise ManifestError(
            f"split manifest not found at {path} -- fail-closed: no data is readable without a "
            "verified manifest present."
        )
    with open(path, "rb") as fh:
        raw: bytes = fh.read()
    try:
        parsed: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ManifestError(f"split manifest is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ManifestError("split manifest root is not a JSON object -- fail-closed")

    content_hash: Any = parsed.get("content_hash")
    if not isinstance(content_hash, dict) or content_hash.get("algorithm") != "sha256":
        raise ManifestError("split manifest content_hash missing or not sha256 -- fail-closed")
    stored: Any = content_hash.get("value")
    if not isinstance(stored, str) or len(stored) != 64:
        raise ManifestError("split manifest content_hash.value missing or malformed -- fail-closed")

    blanked: bytes = raw.replace(stored.encode("utf-8"), b"")
    computed: str = hashlib.sha256(blanked).hexdigest()
    if computed != stored:
        raise ManifestError(
            f"split manifest hash mismatch (computed {computed} != stored {stored}) -- fail-closed: "
            "the manifest was altered or corrupted (e.g. CRLF conversion); refusing to trust it."
        )
    return parsed


def _validated_entry(manifest: dict[str, Any], tf: str) -> dict[str, Any]:
    """Return the timeframe entry ONLY if its status is exactly VALIDATED. Raise `ManifestError`
    otherwise -- the sealed (no-access) outcome for M15_v2 (AWAITING_DATA_FILE_HASH), M5/H1
    (AWAITING_REGIME_MAP_AND_DATA_FILE_HASH), and any timeframe absent from the manifest (H4/D1).
    Distinct keys ('M15' vs 'M15_v2') are never aliased -- the caller must pass one exact key."""
    timeframes: Any = manifest.get("timeframes")
    if not isinstance(timeframes, dict):
        raise ManifestError("split manifest has no `timeframes` table -- fail-closed")
    entry: Any = timeframes.get(tf)
    if not isinstance(entry, dict):
        raise ManifestError(
            f"timeframe {tf!r} is absent from the split manifest -- fail-closed "
            "(a missing status is never treated as open)."
        )
    status: Any = entry.get("status")
    if status != "VALIDATED":
        raise ManifestError(
            f"timeframe {tf!r} has status {status!r}, not VALIDATED -- 100% SEALED per the manifest's "
            "fail_closed_default (zero bars readable as discovery)."
        )
    return entry


def discovery_window(manifest: dict[str, Any], tf: str) -> tuple[int, int]:
    """Return `(discovery_start_epoch, discovery_end_epoch)` for a VALIDATED timeframe with a fully
    populated discovery_range. Raise `ManifestError` otherwise."""
    entry = _validated_entry(manifest, tf)
    disc: Any = entry.get("discovery_range")
    if not isinstance(disc, dict):
        raise ManifestError(f"timeframe {tf!r} is VALIDATED but has no discovery_range -- fail-closed")
    start: Any = disc.get("start_epoch")
    end: Any = disc.get("end_epoch")
    if not isinstance(start, int) or not isinstance(end, int) or start >= end:
        raise ManifestError(f"timeframe {tf!r} discovery_range is malformed -- fail-closed")
    return (start, end)


def entry_file(manifest: dict[str, Any], tf: str) -> tuple[str, str]:
    """Return `(file_path, expected_sha256)` for a VALIDATED timeframe: the exact data file that entry
    governs and the SHA-256 the file must match. Raise `ManifestError` if the entry is not VALIDATED or
    lacks a file_path / data_file_sha256.value."""
    entry = _validated_entry(manifest, tf)
    file_path: Any = entry.get("file_path")
    if not isinstance(file_path, str) or not file_path:
        raise ManifestError(f"timeframe {tf!r} is VALIDATED but has no file_path -- fail-closed")
    dfs: Any = entry.get("data_file_sha256")
    if not isinstance(dfs, dict):
        raise ManifestError(f"timeframe {tf!r} has no data_file_sha256 block -- fail-closed")
    value: Any = dfs.get("value")
    if not isinstance(value, str) or len(value) != 64:
        raise ManifestError(f"timeframe {tf!r} data_file_sha256.value missing/malformed -- fail-closed")
    return (file_path, value)


def verify_data_file(root: str, file_path: str, expected_sha256: str) -> str:
    """Verify that the physical data file's SHA-256 equals `expected_sha256`. Return the absolute path
    on success. Raise `ManifestError` if the file is missing or its hash differs by even one byte --
    this is the check that makes the manifest<->disk binding real rather than declarative."""
    abspath = file_path if os.path.isabs(file_path) else os.path.join(root, file_path)
    if not os.path.isfile(abspath):
        raise ManifestError(
            f"data file for a VALIDATED entry not found at {abspath} -- fail-closed "
            "(the manifest governs a file that is not on disk)."
        )
    digest = hashlib.sha256()
    with open(abspath, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    got = digest.hexdigest()
    if got != expected_sha256:
        raise ManifestError(
            f"data file {file_path} sha256 {got} != manifest {expected_sha256} -- fail-closed: the "
            "governed file was swapped or modified (content_hash protects the manifest text, not this)."
        )
    return abspath

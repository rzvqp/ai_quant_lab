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

__all__ = ["ManifestError", "MANIFEST_PATH", "load_manifest", "discovery_window"]

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


def discovery_window(manifest: dict[str, Any], tf: str) -> tuple[int, int]:
    """Return `(discovery_start_epoch, discovery_end_epoch)` for a timeframe whose status is exactly
    VALIDATED and whose discovery_range is fully populated. Raise `ManifestError` otherwise -- which,
    per the manifest's fail_closed_default, is the sealed (no-access) outcome for M5/H1
    (AWAITING_REGIME_MAP) and for any timeframe absent from the manifest (e.g. H4/D1).
    """
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
    disc: Any = entry.get("discovery_range")
    if not isinstance(disc, dict):
        raise ManifestError(f"timeframe {tf!r} is VALIDATED but has no discovery_range -- fail-closed")
    start: Any = disc.get("start_epoch")
    end: Any = disc.get("end_epoch")
    if not isinstance(start, int) or not isinstance(end, int) or start >= end:
        raise ManifestError(f"timeframe {tf!r} discovery_range is malformed -- fail-closed")
    return (start, end)

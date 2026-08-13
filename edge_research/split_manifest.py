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
    "ManifestError", "IdentifierError", "MANIFEST_PATH", "load_manifest", "discovery_window",
    "entry_file", "verify_data_file", "segmentation_plan", "resolve", "context_entry_file",
]

# A context-derived entry is readable only once the Statistician has ratified it.
_RATIFIED_CONTEXT_STATUSES = ("VALIDATED", "CONTEXT_DERIVED_VALIDATED")

_ROOT: Final[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH: Final[str] = os.path.join(_ROOT, "config", "split_manifest.json")


class ManifestError(ValueError):
    """Raised when the split manifest cannot be located, hash-verified, or authorizes no access.
    Covers manifest-hash failures, data-file-hash failures, and status (sealed) failures."""


class IdentifierError(ManifestError):
    """Raised specifically when a requested timeframe key does not correspond to exactly one manifest
    entry (unknown / ambiguous / no-alias). Distinct from a hash failure or a status (sealed) failure
    so the cause is diagnosable from the exception type as well as the message. 'M15' and 'M15_v2' are
    distinct keys with no default, alias, or fallback between them."""


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


def _entry(manifest: dict[str, Any], tf: str) -> dict[str, Any]:
    """Return the manifest entry for tf, or raise IdentifierError if tf names no exact entry
    (unknown/ambiguous key -- H4/D1, a typo, or a bare/generic request). No alias/default/fallback."""
    timeframes: Any = manifest.get("timeframes")
    if not isinstance(timeframes, dict):
        raise ManifestError("split manifest has no `timeframes` table -- fail-closed")
    entry: Any = timeframes.get(tf)
    if not isinstance(entry, dict):
        raise IdentifierError(
            f"timeframe {tf!r} does not correspond to exactly one manifest entry -- fail-closed with "
            "AMBIGUOUS/UNKNOWN IDENTIFIER (no alias, default, or fallback; name an exact key such as "
            "'M15' or 'M15_v2')."
        )
    return entry


def _validated_entry(manifest: dict[str, Any], tf: str) -> dict[str, Any]:
    """Return the entry ONLY if its status is exactly VALIDATED. IdentifierError if the key is unknown;
    ManifestError (status/sealed failure) if it is known but not VALIDATED."""
    entry = _entry(manifest, tf)
    status: Any = entry.get("status")
    if status != "VALIDATED":
        raise ManifestError(
            f"timeframe {tf!r} has status {status!r}, not VALIDATED -- 100% SEALED per the manifest's "
            "fail_closed_default (zero bars readable as discovery)."
        )
    return entry


def _range(obj: Any, ctx: str) -> tuple[int, int]:
    """Extract (start_epoch, end_epoch) from a manifest range object, fail-closed on any malformation.
    Coordinates are used verbatim from the manifest -- never recomputed, derived, or rounded."""
    if not isinstance(obj, dict):
        raise ManifestError(f"{ctx}: range object missing -- fail-closed")
    start: Any = obj.get("start_epoch")
    end: Any = obj.get("end_epoch")
    if not isinstance(start, int) or not isinstance(end, int) or start > end:
        raise ManifestError(f"{ctx}: malformed range (start_epoch/end_epoch) -- fail-closed")
    return (start, end)


def segmentation_plan(manifest: dict[str, Any], tf: str) -> dict[str, list[tuple[int, int]]]:
    """Return the runtime access plan for a VALIDATED timeframe, purely from manifest coordinates:
        {"discovery": [(s,e), ...], "quarantine": [(s,e), ...]}
    `discovery` is what the loader may deliver (the union of the per-segment discovery halves, or the
    single global discovery_range for M15). `quarantine` is the union of every embargo band -- per
    segment: the LEADING gap [segment_start, discovery_start), the intra_segment_embargo, and the
    TRAILING gap [sealed_end, segment_end); or the single embargo_range for M15.

    An `overlap_with_<SRC>` entry is NOT sealed by default: its rule says it INHERITS <SRC>'s
    discovery/embargo/sealed classification VERBATIM, so its portions are intersected against
    <SRC>'s own ranges and contribute to `discovery` and `quarantine` accordingly. This function
    previously sealed the whole overlap by omission, which CONTRADICTED that rule -- the manifest
    then asserted two different classifications for one interval (Statistician, v2.7.70).

    Everything the caller then finds outside both sets is SEALED by default (fully-sealed
    segments, the post-M15 tail, an unlabeled recent tail, etc.) -- never delivered."""
    entry = _validated_entry(manifest, tf)
    discovery: list[tuple[int, int]] = []
    quarantine: list[tuple[int, int]] = []
    segments: Any = entry.get("regime_segments")
    if isinstance(segments, list):
        for i, seg in enumerate(segments):
            if not isinstance(seg, dict):
                raise ManifestError(f"{tf} regime_segments[{i}] malformed -- fail-closed")
            seg_s, seg_e = _range(seg.get("segment_range"), f"{tf} seg{i} segment_range")
            if "discovery_range" in seg:  # a split segment
                ds, de = _range(seg["discovery_range"], f"{tf} seg{i} discovery_range")
                es, ee = _range(seg.get("intra_segment_embargo"), f"{tf} seg{i} intra_segment_embargo")
                _ss, sealed_end = _range(seg.get("sealed_range"), f"{tf} seg{i} sealed_range")
                discovery.append((ds, de))
                if seg_s < ds:
                    quarantine.append((seg_s, ds))       # leading boundary embargo
                quarantine.append((es, ee))              # intra-segment embargo
                if sealed_end < seg_e:
                    quarantine.append((sealed_end, seg_e))  # trailing boundary embargo
            # else: a TOO_SHORT_FULLY_SEALED segment -> sealed by default (no discovery/quarantine)
    elif "discovery_range" in entry:  # single_global_cutoff (M15 legacy)
        discovery.append(_range(entry["discovery_range"], f"{tf} discovery_range"))
        if "embargo_range" in entry:
            quarantine.append(_range(entry["embargo_range"], f"{tf} embargo_range"))
    else:
        raise ManifestError(
            f"{tf} is VALIDATED but has neither regime_segments nor a discovery_range -- fail-closed")

    # ---- overlap_with_<SRC>: honour the INHERITANCE rule instead of sealing by omission ----
    for key, ov in entry.items():
        if not (isinstance(key, str) and key.startswith("overlap_with_") and isinstance(ov, dict)):
            continue
        src = key[len("overlap_with_"):]
        ov_s, ov_e = _range(ov.get("range"), f"{tf} {key} range")
        src_entry = _validated_entry(manifest, src)
        for band, bucket in (("discovery_range", discovery), ("embargo_range", quarantine)):
            r = src_entry.get(band)
            if not isinstance(r, dict):
                continue                      # source lacks this band -> that portion stays SEALED
            b_s, b_e = _range(r, f"{src} {band}")
            lo, hi = max(ov_s, b_s), min(ov_e, b_e)
            if lo < hi:
                bucket.append((lo, hi))       # the INTERSECTION only -- never the whole overlap

    return {"discovery": discovery, "quarantine": quarantine}


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


def resolve(manifest: dict[str, Any], tf: str) -> tuple[str, dict[str, Any]]:
    """Resolve a requested key to ('timeframe', entry) or ('context', entry). A base market key lives
    under `timeframes`; a derived-context key (H4_from_M15_v2, D1_from_M15_v2) lives under
    `context_derived_htf.entries`. Raise IdentifierError if the key is in neither (unknown/ambiguous;
    no alias/default). A key present in BOTH would be ambiguous -> IdentifierError."""
    tfs = manifest.get("timeframes")
    ctx = manifest.get("context_derived_htf")
    in_tf = isinstance(tfs, dict) and isinstance(tfs.get(tf), dict)
    ctx_entries = ctx.get("entries") if isinstance(ctx, dict) else None
    in_ctx = isinstance(ctx_entries, dict) and isinstance(ctx_entries.get(tf), dict)
    if in_tf and in_ctx:
        raise IdentifierError(f"timeframe {tf!r} is ambiguous (in both timeframes and context) -- fail-closed")
    if in_tf:
        return ("timeframe", tfs[tf])  # type: ignore[index]
    if in_ctx:
        return ("context", ctx_entries[tf])  # type: ignore[index]
    raise IdentifierError(
        f"timeframe {tf!r} does not correspond to exactly one manifest entry -- fail-closed with "
        "AMBIGUOUS/UNKNOWN IDENTIFIER (no alias, default, or fallback; name an exact key)."
    )


def context_entry_file(manifest: dict[str, Any], tf: str) -> tuple[str, str]:
    """For a derived-context key whose status is a ratified state, return (file_path, expected_sha256).
    Raise ManifestError (sealed) if the entry is not yet ratified -- e.g. GENERATED_PENDING_RATIFICATION
    -- so a supplied-but-unratified context file is never delivered."""
    kind, entry = resolve(manifest, tf)
    if kind != "context":
        raise ManifestError(f"{tf!r} is not a context-derived entry -- fail-closed")
    status: Any = entry.get("status")
    if status not in _RATIFIED_CONTEXT_STATUSES:
        raise ManifestError(
            f"context-derived {tf!r} has status {status!r}, not ratified {_RATIFIED_CONTEXT_STATUSES} "
            "-- 100% SEALED until the Statistician promotes it (Data Acquisition supplies, does not ratify)."
        )
    file_path: Any = entry.get("file_path")
    dfs: Any = entry.get("data_file_sha256")
    value: Any = dfs.get("value") if isinstance(dfs, dict) else None
    if not isinstance(file_path, str) or not file_path or not isinstance(value, str) or len(value) != 64:
        raise ManifestError(f"context-derived {tf!r} missing file_path/data_file_sha256 -- fail-closed")
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

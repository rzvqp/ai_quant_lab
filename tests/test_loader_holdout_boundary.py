"""Manifest-gated loader verification (Mandate 2 + 2.5).

Confirms edge_research/_common.py::load() gates every read through the hash-verified split manifest
AND the per-file data-file hash:
  * M15 (VALIDATED) reads its governed file (the legacy/superseded file via the entry's file_path),
    with BOTH the manifest content_hash and the data-file sha256 verified, inside the manifest window.
  * M15_v2 is REJECTED on status AWAITING_DATA_FILE_HASH even though its data-file hash now matches --
    supplying the hash is Data Acquisition's job; promotion to VALIDATED is the Statistician's.
  * M5 and H1 are rejected on AWAITING_REGIME_MAP_AND_DATA_FILE_HASH; H4/D1 are absent -> sealed.
  * a data file modified by a single byte is rejected on hash mismatch (manifest<->disk binding).
  * a bad-hash manifest is rejected; an absent manifest is fail-closed; missing split config raises.

Run: python -m pytest tests/test_loader_holdout_boundary.py  or  python tests/test_loader_holdout_boundary.py
"""
import hashlib
import os
import shutil
import sys
import tempfile

import pandas as pd  # type: ignore[import-untyped]
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from edge_research import _common as C
from edge_research import split_manifest as SM

SPLIT = C.PRE_HOLDOUT_SPLIT_ID
PERMISSIVE_CUTOFF = "2025-10-23T09:15:00+00:00"  # deliberately looser than the manifest window
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MANIFEST = SM.load_manifest()
_M15_DISC = _MANIFEST["timeframes"]["M15"]["discovery_range"]
DISC_START = pd.Timestamp(_M15_DISC["start_epoch"], unit="s", tz="UTC")
DISC_END = pd.Timestamp(_M15_DISC["end_epoch"], unit="s", tz="UTC")


def test_m15_reads_with_both_hashes_verified() -> None:
    d, meta = C.load("M15", data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)
    assert len(d) > 0
    assert d["dt"].min() >= DISC_START and d["dt"].max() < DISC_END
    # both hashes recorded/verified: manifest content_hash + the governed data-file sha256
    assert meta["manifest_hash"] == _MANIFEST["content_hash"]["value"]
    assert meta["data_file_sha256"] == _MANIFEST["timeframes"]["M15"]["data_file_sha256"]["value"]
    # M15 is governed by the LEGACY superseded file, resolved from the entry's file_path (not by tf name)
    assert meta["data_file_path"] == _MANIFEST["timeframes"]["M15"]["file_path"]
    assert "SUPERSEDED" in meta["data_file_path"]
    assert meta["holdout_cutoff"] == DISC_END.isoformat()  # embargo binds vs the looser caller cutoff


def test_m15_v2_rejected_on_status_despite_matching_file_hash() -> None:
    # the file hash DOES match now (Data Acquisition supplied it)...
    fp = _MANIFEST["timeframes"]["M15_v2"]["file_path"]
    exp = _MANIFEST["timeframes"]["M15_v2"]["data_file_sha256"]["value"]
    SM.verify_data_file(_ROOT, fp, exp)  # does not raise -> hash is correct
    # ...but status AWAITING_DATA_FILE_HASH still seals it: the Statistician has not ratified.
    assert _MANIFEST["timeframes"]["M15_v2"]["status"] == "AWAITING_DATA_FILE_HASH"
    with pytest.raises(C.HoldoutConfigError):
        C.load("M15_v2", data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)


@pytest.mark.parametrize("tf", ["M5", "H1"])
def test_awaiting_regime_map_timeframes_are_sealed(tf: str) -> None:
    assert _MANIFEST["timeframes"][tf]["status"] == "AWAITING_REGIME_MAP_AND_DATA_FILE_HASH"
    with pytest.raises(C.HoldoutConfigError):
        C.load(tf, data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)


@pytest.mark.parametrize("tf", ["H4", "D1"])
def test_timeframes_absent_from_manifest_are_sealed(tf: str) -> None:
    with pytest.raises(C.HoldoutConfigError):
        C.load(tf, data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)


def test_one_byte_data_file_modification_is_rejected() -> None:
    # THE binding test: copy M15's real governed file, flip one byte, and confirm verify_data_file
    # rejects it against the manifest hash. This is what makes the manifest<->disk link real.
    fp, exp = SM.entry_file(_MANIFEST, "M15")
    src = os.path.join(_ROOT, fp)
    with tempfile.TemporaryDirectory() as td:
        dst = os.path.join(td, "copy.csv")
        shutil.copyfile(src, dst)
        SM.verify_data_file(td, "copy.csv", exp)  # unmodified copy verifies
        b = bytearray(open(dst, "rb").read())
        b[len(b) // 2] ^= 0x01  # flip a single bit of one byte
        open(dst, "wb").write(b)
        with pytest.raises(SM.ManifestError):
            SM.verify_data_file(td, "copy.csv", exp)


def test_fail_closed_without_config() -> None:
    with pytest.raises(TypeError):
        C.load("M15")  # type: ignore[call-arg]
    for kw in (dict(data_split_id="", cutoff=PERMISSIVE_CUTOFF),
               dict(data_split_id=SPLIT, cutoff="")):
        with pytest.raises(C.HoldoutConfigError):
            C.load("M15", **kw)


def test_bad_hash_manifest_is_rejected() -> None:
    real = open(SM.MANIFEST_PATH, "rb").read().decode("utf-8")
    tampered = real.replace('"margin_factor"', '"MARGIN_factor"')
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "split_manifest.json")
        open(p, "wb").write(tampered.encode("utf-8"))
        with pytest.raises(SM.ManifestError):
            SM.load_manifest(p)


def test_absent_manifest_is_fail_closed() -> None:
    with tempfile.TemporaryDirectory() as td:
        with pytest.raises(SM.ManifestError):
            SM.load_manifest(os.path.join(td, "nope.json"))


def test_manifest_v2_1_0_hash_verifies() -> None:
    raw = open(SM.MANIFEST_PATH, "rb").read()
    stored = _MANIFEST["content_hash"]["value"]
    assert hashlib.sha256(raw.replace(stored.encode(), b"")).hexdigest() == stored
    assert _MANIFEST["version"] == "2.1.0"
    assert _MANIFEST["timeframes"]["M15"]["status"] == "VALIDATED"


def _print_meta() -> None:
    _, meta = C.load("M15", data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)
    print("\n--- M15 manifest-gated load meta (v2.1.0) ---")
    for k in ("timeframe", "manifest_version", "manifest_hash", "data_file_path", "data_file_sha256",
              "manifest_discovery_start", "manifest_discovery_end", "requested_cutoff", "holdout_cutoff",
              "min_date_used", "max_date_used", "n_bars_used", "loader_version"):
        print(f"  {k}: {meta[k]}")


if __name__ == "__main__":
    rc = pytest.main([os.path.abspath(__file__), "-q"])
    _print_meta()
    sys.exit(int(rc))

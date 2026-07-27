"""Manifest-gated loader verification (Mandate 2).

Confirms edge_research/_common.py::load() gates every read through the hash-verified split manifest:
  * M15 (VALIDATED) reads ONLY inside its manifest discovery_range -- the out-of-scope extended
    2011-2022 territory is excluded, and the manifest's 1000-bar embargo binds even against a more
    permissive caller cutoff.
  * M5 and H1 (AWAITING_REGIME_MAP) raise -- 100% sealed.
  * H4/D1 (absent from the manifest) raise -- fail-closed default.
  * missing split config raises (TypeError / HoldoutConfigError).
  * a bad-hash manifest is rejected; an absent manifest is fail-closed, not permissive.

Run: python -m pytest tests/test_loader_holdout_boundary.py   or   python tests/test_loader_holdout_boundary.py
"""
import os
import sys
import tempfile

import pandas as pd  # type: ignore[import-untyped]
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from edge_research import _common as C
from edge_research import split_manifest as SM

SPLIT = C.PRE_HOLDOUT_SPLIT_ID
# A deliberately-permissive caller cutoff (the pre-manifest terminal boundary). The manifest's tighter
# discovery_end must win, proving the embargo binds.
PERMISSIVE_CUTOFF = "2025-10-23T09:15:00+00:00"
DISC_START = pd.Timestamp("2022-12-16T10:45:00+00:00")  # manifest M15 discovery_range.start
DISC_END = pd.Timestamp("2025-10-12T23:15:00+00:00")    # manifest M15 discovery_range.end (embargoed)


def test_m15_reads_only_inside_manifest_discovery_window() -> None:
    d, meta = C.load("M15", data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)
    assert len(d) > 0
    # lower bound: the out-of-scope extended 2011-2022 territory is NOT served
    assert d["dt"].min() >= DISC_START, d["dt"].min()
    # upper bound: manifest discovery_end (with embargo) binds, tighter than the permissive caller cutoff
    assert d["dt"].max() < DISC_END, d["dt"].max()
    assert meta["timeframe"] == "M15" and meta["holdout_excluded"] is True
    assert meta["holdout_cutoff"] == DISC_END.isoformat()          # effective bound == manifest end
    assert meta["requested_cutoff"] == pd.Timestamp(PERMISSIVE_CUTOFF).isoformat()
    assert meta["manifest_hash"] and len(meta["manifest_hash"]) == 64
    # a beyond-window row would fail the assertions above; also confirm active exclusion counted
    assert meta["n_bars_excluded_by_cutoff"] > 0
    assert meta["n_bars_used"] + meta["n_bars_excluded_by_cutoff"] == meta["n_bars_before_cutoff"]


def test_caller_may_tighten_but_never_widen() -> None:
    # a tighter caller cutoff is honored
    d, meta = C.load("M15", data_split_id=SPLIT, cutoff="2024-01-01T00:00:00+00:00")
    assert d["dt"].max() < pd.Timestamp("2024-01-01T00:00:00+00:00")
    assert meta["holdout_cutoff"] == "2024-01-01T00:00:00+00:00"


@pytest.mark.parametrize("tf", ["M5", "H1"])
def test_awaiting_regime_map_timeframes_are_sealed(tf: str) -> None:
    with pytest.raises(C.HoldoutConfigError):
        C.load(tf, data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)


@pytest.mark.parametrize("tf", ["H4", "D1"])
def test_timeframes_absent_from_manifest_are_sealed(tf: str) -> None:
    with pytest.raises(C.HoldoutConfigError):
        C.load(tf, data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)


def test_fail_closed_without_config() -> None:
    with pytest.raises(TypeError):
        C.load("M15")  # type: ignore[call-arg]
    for kw in (dict(data_split_id="", cutoff=PERMISSIVE_CUTOFF),
               dict(data_split_id=SPLIT, cutoff="")):
        with pytest.raises(C.HoldoutConfigError):
            C.load("M15", **kw)


def _write(tmpdir: str, text: str) -> str:
    p = os.path.join(tmpdir, "split_manifest.json")
    with open(p, "wb") as fh:
        fh.write(text.encode("utf-8"))
    return p


def test_bad_hash_manifest_is_rejected() -> None:
    real = open(SM.MANIFEST_PATH, "rb").read().decode("utf-8")
    tampered = real.replace('"margin_factor"', '"MARGIN_factor"')  # change content, keep stored hash
    with tempfile.TemporaryDirectory() as td:
        p = _write(td, tampered)
        with pytest.raises(SM.ManifestError):
            SM.load_manifest(p)


def test_absent_manifest_is_fail_closed() -> None:
    with tempfile.TemporaryDirectory() as td:
        with pytest.raises(SM.ManifestError):
            SM.load_manifest(os.path.join(td, "does_not_exist.json"))


def test_real_manifest_hash_verifies() -> None:
    m = SM.load_manifest()
    assert m["manifest_id"] == "STAT-SPLIT-MANIFEST"
    assert m["timeframes"]["M15"]["status"] == "VALIDATED"
    assert m["timeframes"]["M5"]["status"] == "AWAITING_REGIME_MAP"
    assert m["timeframes"]["H1"]["status"] == "AWAITING_REGIME_MAP"


def _print_meta() -> None:
    _, meta = C.load("M15", data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)
    print("\n--- M15 manifest-gated load meta ---")
    for k in ("timeframe", "manifest_version", "manifest_hash", "manifest_discovery_start",
              "manifest_discovery_end", "requested_cutoff", "holdout_cutoff", "min_date_used",
              "max_date_used", "n_bars_before_cutoff", "n_bars_used", "n_bars_excluded_by_cutoff",
              "loader_version"):
        print(f"  {k}: {meta[k]}")


if __name__ == "__main__":
    rc = pytest.main([os.path.abspath(__file__), "-q"])
    _print_meta()
    sys.exit(int(rc))

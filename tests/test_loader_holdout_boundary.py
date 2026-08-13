"""Manifest-gated, runtime-segmented loader verification (Mandates 2 / 2.5 / 2.6).

edge_research/_common.py::load() must, for a VALIDATED timeframe, deliver EXACTLY the union of the
manifest's per-segment discovery halves -- with every embargo band and every sealed half excluded --
and verify BOTH the manifest content_hash and the governed data file's SHA-256. The decisive tests are
the segmentation ones: a bar taken from EACH inter-segment quarantine band, and from each sealed half,
must not appear -- proving the split is real, not declarative (the same bar has since the one-byte test
proved the manifest<->disk binding is real).

Run: python -m pytest tests/test_loader_holdout_boundary.py  or  python tests/test_loader_holdout_boundary.py
"""
import csv
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
PERMISSIVE_CUTOFF = "2026-12-31T00:00:00+00:00"  # beyond all discovery -> delivers the exact union
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = SM.load_manifest()


def _raw_epochs(tf: str) -> list[int]:
    fp = MAN["timeframes"][tf]["file_path"]
    out = []
    with open(os.path.join(_ROOT, fp), newline="") as f:
        r = csv.reader(f); next(r)
        for ln in r:
            if ln and ln[0].strip():
                out.append(int(ln[0]))
    return out


def _delivered_epochs(tf: str) -> set[int]:
    d, _ = C.load(tf, data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)
    return set(int(t) for t in d["time"])


def _first_bar_in(raw: list[int], s: int, e: int) -> int:
    for t in raw:
        if s <= t < e:
            return t
    raise AssertionError(f"no bar found in [{s}, {e}) -- test setup error")


# ---------- M15 (legacy) reads with both hashes verified ----------

def test_m15_reads_with_both_hashes_verified() -> None:
    d, meta = C.load("M15", data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)
    assert len(d) > 0
    assert meta["manifest_hash"] == MAN["content_hash"]["value"]
    assert meta["data_file_sha256"] == MAN["timeframes"]["M15"]["data_file_sha256"]["value"]
    assert "SUPERSEDED" in meta["data_file_path"]  # governed by the legacy file via file_path
    assert meta["n_bars_delivered"] + meta["n_bars_quarantine"] + meta["n_bars_sealed"] == meta["n_bars_before_cutoff"]


# ---------- runtime segmentation: the decisive tests ----------

@pytest.mark.parametrize("tf", ["M15_v2", "M5"])
def test_delivered_is_exactly_the_union_of_discovery_segments(tf: str) -> None:
    raw = _raw_epochs(tf)
    delivered = _delivered_epochs(tf)
    plan = SM.segmentation_plan(MAN, tf)
    expected = set(t for t in raw for (s, e) in plan["discovery"] if s <= t < e)
    assert delivered == expected, f"{tf}: delivered != exact discovery union"
    assert len(delivered) > 0


@pytest.mark.parametrize("tf", ["M15_v2", "M5"])
def test_a_bar_from_EACH_quarantine_band_is_not_delivered(tf: str) -> None:
    raw = _raw_epochs(tf)
    delivered = _delivered_epochs(tf)
    segs = MAN["timeframes"][tf]["regime_segments"]
    checked = 0
    for seg in segs:
        if "discovery_range" not in seg:
            continue
        sr = seg["segment_range"]; dr = seg["discovery_range"]
        emb = seg["intra_segment_embargo"]; sealed = seg["sealed_range"]
        bands = []
        if sr["start_epoch"] < dr["start_epoch"]:
            bands.append((sr["start_epoch"], dr["start_epoch"]))   # leading boundary embargo
        bands.append((emb["start_epoch"], emb["end_epoch"]))       # intra-segment embargo
        if sealed["end_epoch"] < sr["end_epoch"]:
            bands.append((sealed["end_epoch"], sr["end_epoch"]))   # trailing boundary embargo
        for s, e in bands:
            try:
                bar = _first_bar_in(raw, s, e)
            except AssertionError:
                continue  # band may be empty of bars (weekend/gap) -- fine
            assert bar not in delivered, f"{tf}: quarantine bar {bar} was delivered"
            checked += 1
    assert checked >= 2, f"{tf}: expected quarantine bars from >=2 boundaries, checked {checked}"


@pytest.mark.parametrize("tf", ["M15_v2", "M5"])
def test_a_bar_from_each_sealed_half_is_not_delivered(tf: str) -> None:
    raw = _raw_epochs(tf)
    delivered = _delivered_epochs(tf)
    for seg in MAN["timeframes"][tf]["regime_segments"]:
        if "sealed_range" not in seg:
            continue
        s, e = seg["sealed_range"]["start_epoch"], seg["sealed_range"]["end_epoch"]
        bar = _first_bar_in(raw, s, e)
        assert bar not in delivered, f"{tf}: sealed-half bar {bar} was delivered"


def test_m15_v2_fully_sealed_zones_never_appear() -> None:
    # Was `..._three_fully_sealed_zones_...` and listed the WHOLE overlap_with_M15 range as fully
    # sealed. That encoded a reading the manifest contradicts: the overlap's rule INHERITS M15's
    # classification verbatim, and M15's discovery_range (2022-12-16 -> 2025-10-12) falls inside it,
    # so the overlap is NOT fully sealed -- only its portion at or beyond M15's sealed_range is.
    # Converted, not deleted: the guard (sealed bars are never delivered) is what must not regress.
    raw = _raw_epochs("M15_v2")
    delivered = _delivered_epochs("M15_v2")
    e = MAN["timeframes"]["M15_v2"]
    zones = []
    for seg in e["regime_segments"]:
        if "discovery_range" not in seg:  # the pre-overlap TOO_SHORT_FULLY_SEALED sliver
            zones.append(("pre_overlap_sliver", seg["segment_range"]))
    ov = e["overlap_with_M15"]["range"]
    src_sealed = MAN["timeframes"]["M15"]["sealed_range"]        # what the overlap INHERITS as sealed
    lo = max(ov["start_epoch"], src_sealed["start_epoch"])
    hi = min(ov["end_epoch"], src_sealed["end_epoch"])
    assert lo < hi, "overlap and M15 sealed_range must intersect -- otherwise the rule is vacuous"
    zones.append(("overlap_sealed_portion", {"start_epoch": lo, "end_epoch": hi}))
    zones.append(("post_M15_tail", e["post_M15_tail"]["range"]))
    for name, r in zones:
        bar = _first_bar_in(raw, r["start_epoch"], r["end_epoch"])
        assert bar not in delivered, f"M15_v2 fully-sealed zone {name} bar {bar} was delivered"


def test_m15_v2_overlap_discovery_portion_IS_delivered() -> None:
    # The positive counterpart, added with the fix: the overlap's DISCOVERY portion (M15's own
    # discovery_range, 2022-12-16 -> 2025-10-12) must actually be delivered. Without this the
    # regression could reappear as a silent omission and no test would notice.
    raw = _raw_epochs("M15_v2")
    delivered = _delivered_epochs("M15_v2")
    ov = MAN["timeframes"]["M15_v2"]["overlap_with_M15"]["range"]
    src_disc = MAN["timeframes"]["M15"]["discovery_range"]
    lo = max(ov["start_epoch"], src_disc["start_epoch"])
    hi = min(ov["end_epoch"], src_disc["end_epoch"])
    assert lo < hi
    bar = _first_bar_in(raw, lo, hi)
    assert bar in delivered, f"overlap discovery portion bar {bar} was WITHHELD -- the 4th block is lost"


# ---------- H1 sealed, identifiers, one-byte binding, fail-closed ----------

def test_h1_is_sealed_awaiting_regime_map() -> None:
    assert MAN["timeframes"]["H1"]["status"] == "AWAITING_REGIME_MAP"
    with pytest.raises(C.HoldoutConfigError):
        C.load("H1", data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)


@pytest.mark.parametrize("tf", ["H4", "D1", "M15x", "m15", ""])
def test_ambiguous_or_unknown_identifier_raises_distinct_exception(tf: str) -> None:
    # distinct type: IdentifierError, NOT the generic HoldoutConfigError used for hash/status failures
    with pytest.raises(SM.IdentifierError):
        C.load(tf, data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)


def test_one_byte_data_file_modification_is_rejected() -> None:
    fp, exp = SM.entry_file(MAN, "M15")
    src = os.path.join(_ROOT, fp)
    with tempfile.TemporaryDirectory() as td:
        dst = os.path.join(td, "copy.csv")
        shutil.copyfile(src, dst)
        SM.verify_data_file(td, "copy.csv", exp)  # unmodified verifies
        b = bytearray(open(dst, "rb").read())
        b[len(b) // 2] ^= 0x01
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


def test_bad_hash_manifest_and_absent_manifest_fail_closed() -> None:
    real = open(SM.MANIFEST_PATH, "rb").read().decode("utf-8")
    tampered = real.replace('"margin_factor"', '"MARGIN_factor"')
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "split_manifest.json")
        open(p, "wb").write(tampered.encode("utf-8"))
        with pytest.raises(SM.ManifestError):
            SM.load_manifest(p)
        with pytest.raises(SM.ManifestError):
            SM.load_manifest(os.path.join(td, "nope.json"))


# ---------- Mandate 2.7: derived HTF context (H4_from_M15_v2 / D1_from_M15_v2) ----------

CTX = MAN["context_derived_htf"]
CTX_BLOCKS = [(b["start_epoch"], b["end_epoch"]) for b in CTX["m15_v2_discovery_blocks"]]


def _read_htf(entry_key: str) -> list[tuple[int, float, float, float, float, float, int]]:
    fp = CTX["entries"][entry_key]["file_path"]
    rows = []
    with open(os.path.join(_ROOT, fp), newline="") as f:
        r = csv.reader(f)
        header = next(r)
        assert header == ["time", "open", "high", "low", "close", "volume", "sub"], header
        for ln in r:
            if ln and ln[0].strip():
                rows.append((int(ln[0]), float(ln[1]), float(ln[2]), float(ln[3]),
                             float(ln[4]), float(ln[5]), int(ln[6])))
    return rows


@pytest.mark.parametrize("key,bar_sec", [("H4_from_M15_v2", 14400), ("D1_from_M15_v2", 86400)])
def test_no_htf_bar_straddles_a_discovery_boundary(key: str, bar_sec: int) -> None:
    # every delivered HTF bar's window must lie fully inside ONE discovery block; i.e. no bar that
    # would straddle any block boundary exists in the file (covers every boundary, not just the first).
    rows = _read_htf(key)
    for t, *_rest in rows:
        assert any(s <= t and t + bar_sec <= e for s, e in CTX_BLOCKS), \
            f"{key}: bar {t} straddles a discovery boundary but is present"


@pytest.mark.parametrize("key", ["H4_from_M15_v2", "D1_from_M15_v2"])
def test_coverage_has_gaps_between_blocks(key: str) -> None:
    # delivered coverage is NOT continuous: each block contributes a contiguous run, with real gaps
    # (embargo + sealed + other regimes) between blocks -- at least 3 gaps for 4 blocks.
    ts = [t for t, *_ in _read_htf(key)]
    blocks_hit = sum(1 for s, e in CTX_BLOCKS if any(s <= t < e for t in ts))
    gaps = sum(1 for i in range(1, len(ts)) if ts[i] - ts[i - 1] > 7 * 86400)
    assert blocks_hit >= 3 and gaps >= blocks_hit - 1, f"{key}: expected gaps between blocks"


@pytest.mark.parametrize("key", ["H4_from_M15_v2", "D1_from_M15_v2"])
def test_bar_count_matches_generation_record(key: str) -> None:
    assert len(_read_htf(key)) == CTX["entries"][key]["generation"]["bars_with_rule"]


def test_a_pure_discovery_D1_bar_exists_and_aggregates_correctly() -> None:
    # pick a D1 bar deep inside block0 and verify OHLCV == aggregate of its constituent M15_v2 bars
    rows = _read_htf("D1_from_M15_v2")
    b0s, b0e = CTX_BLOCKS[0]
    sample = next(r for r in rows if b0s + 30 * 86400 < r[0] < b0e - 30 * 86400)  # well inside block0
    t, o, h, l, c, v, sub = sample
    m15 = pd.read_csv(os.path.join(_ROOT, MAN["timeframes"]["M15_v2"]["file_path"]))
    comp = m15[(m15["time"] >= t) & (m15["time"] < t + 86400)]
    assert len(comp) == sub and sub > 0
    assert abs(o - comp.iloc[0]["open"]) < 1e-9
    assert abs(c - comp.iloc[-1]["close"]) < 1e-9
    assert abs(h - comp["high"].max()) < 1e-9
    assert abs(l - comp["low"].min()) < 1e-9
    assert abs(v - comp["volume"].sum()) < 1e-6


@pytest.mark.parametrize("key", ["H4_from_M15_v2", "D1_from_M15_v2"])
def test_ratified_context_keys_load_and_verify(key: str) -> None:
    # manifest v2.4.1 promoted H4/D1 to CONTEXT_DERIVED_VALIDATED -> loadable (whole file, dual hash).
    assert CTX["entries"][key]["status"] == "CONTEXT_DERIVED_VALIDATED"
    d, meta = C.load(key, data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)
    assert len(d) == CTX["entries"][key]["generation"]["bars_with_rule"]
    assert meta["data_file_sha256"] == CTX["entries"][key]["data_file_sha256"]["value"]
    assert meta["manifest_hash"] == MAN["content_hash"]["value"]


def test_h1_from_m15_v2_path_reconciled() -> None:
    # Was `..._awaits_path_reconciliation`, asserting the registered path did NOT exist while the manifest
    # still pointed at the old acquisition_staging location. The reconciliation has since landed, so the
    # original assertion inverted and the test went stale (Data Acquisition, M-4). It is CONVERTED rather
    # than deleted: the guard it provided -- that the registered path is the canonical one and actually
    # loads -- is exactly what must not silently regress.
    h1 = CTX["entries"]["H1_from_M15_v2"]
    assert h1["status"] == "CONTEXT_DERIVED_VALIDATED"
    assert h1["file_path"] == "data/market/OANDA_XAUUSD_H1_from_M15_v2.csv"   # canonical, not staging
    assert "acquisition_staging" not in h1["file_path"]
    assert os.path.isfile(os.path.join(_ROOT, h1["file_path"]))
    d, _ = C.load("H1_from_M15_v2", data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)
    assert len(d) > 0


@pytest.mark.parametrize("key", ["H4_from_M15_v2", "D1_from_M15_v2"])
def test_context_file_hash_matches_manifest_and_one_byte_mod_rejected(key: str) -> None:
    fp = CTX["entries"][key]["file_path"]
    exp = CTX["entries"][key]["data_file_sha256"]["value"]
    SM.verify_data_file(_ROOT, fp, exp)  # matches
    with tempfile.TemporaryDirectory() as td:
        dst = os.path.join(td, "c.csv")
        shutil.copyfile(os.path.join(_ROOT, fp), dst)
        b = bytearray(open(dst, "rb").read()); b[len(b) // 2] ^= 0x01; open(dst, "wb").write(b)
        with pytest.raises(SM.ManifestError):
            SM.verify_data_file(td, "c.csv", exp)


def _print_breakdown() -> None:
    for tf in ("M15_v2", "M5"):
        _, m = C.load(tf, data_split_id=SPLIT, cutoff=PERMISSIVE_CUTOFF)
        print(f"  {tf}: total={m['n_bars_before_cutoff']} delivered={m['n_bars_delivered']} "
              f"quarantine={m['n_bars_quarantine']} sealed={m['n_bars_sealed']} "
              f"sum_ok={m['n_bars_delivered']+m['n_bars_quarantine']+m['n_bars_sealed']==m['n_bars_before_cutoff']}")


if __name__ == "__main__":
    rc = pytest.main([os.path.abspath(__file__), "-q"])
    print("\n--- segmentation breakdown ---")
    _print_breakdown()
    sys.exit(int(rc))

"""Loader connection + holdout-boundary verification for the newly-connected extended files.

Confirms edge_research/_common.py::load() reads the extended M15, enforces the exclusive cutoff
(a beyond-cutoff row would fail these assertions), fails closed on missing/empty split config, and
still rejects M5 (not in the tf whitelist). Run: python -m pytest tests/test_loader_holdout_boundary.py
or python tests/test_loader_holdout_boundary.py
"""
import os, sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from edge_research import _common as C

CUTOFF = C.RESEARCH_HOLDOUT_CUTOFF_UTC          # 2025-10-23T09:15:00+00:00
SPLIT = C.PRE_HOLDOUT_SPLIT_ID
CUT_TS = pd.Timestamp(CUTOFF)


def test_m15_loads_extended_history():
    d, meta = C.load("M15", data_split_id=SPLIT, cutoff=CUTOFF)
    assert len(d) > 0
    # the 11 new years are present (file starts 2011-07-26); loader did not silently drop them
    assert d["dt"].min() <= pd.Timestamp("2011-08-01T00:00:00+00:00"), d["dt"].min()
    assert meta["timeframe"] == "M15" and meta["holdout_excluded"] is True


def test_m15_cutoff_is_exclusive_upper_bound():
    # THE boundary test: if the loader ever let a holdout row through, this fails.
    d, meta = C.load("M15", data_split_id=SPLIT, cutoff=CUTOFF)
    assert d["dt"].max() < CUT_TS, f"holdout leaked: max dt {d['dt'].max()} >= cutoff {CUT_TS}"
    # and the post-cutoff holdout portion of the extended file was actively excluded (non-zero)
    assert meta["n_bars_excluded_by_cutoff"] > 0, "extended file has post-cutoff bars that must be excluded"
    assert meta["n_bars_used"] + meta["n_bars_excluded_by_cutoff"] == meta["n_bars_before_cutoff"]


def test_fail_closed_without_config():
    # Python's own fail-closed: keyword-only args with no default.
    try:
        C.load("M15")
        assert False, "expected TypeError (missing data_split_id/cutoff)"
    except TypeError:
        pass
    # explicit empty values raise HoldoutConfigError
    for kw in (dict(data_split_id="", cutoff=CUTOFF), dict(data_split_id=SPLIT, cutoff="")):
        try:
            C.load("M15", **kw)
            assert False, f"expected HoldoutConfigError for {kw}"
        except C.HoldoutConfigError:
            pass


def test_m5_is_not_loadable_by_the_official_loader():
    # M5 is physically in data/market/ but the loader whitelist is {M15,H1,H4,D1}; it must reject M5.
    try:
        C.load("M5", data_split_id=SPLIT, cutoff=CUTOFF)
        assert False, "loader unexpectedly accepted M5"
    except C.HoldoutConfigError:
        pass


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for t in tests:
        try:
            t(); print(f"PASS  {t.__name__}"); passed += 1
        except Exception:
            print(f"FAIL  {t.__name__}"); traceback.print_exc()
    # detail dump for the report
    d, meta = C.load("M15", data_split_id=SPLIT, cutoff=CUTOFF)
    print("\n--- M15 load meta ---")
    for k in ("timeframe", "data_split_id", "holdout_cutoff", "min_date_used", "max_date_used",
              "n_bars_before_cutoff", "n_bars_used", "n_bars_excluded_by_cutoff", "loader_version"):
        print(f"  {k}: {meta[k]}")
    print(f"\n{passed}/{len(tests)} tests passed")
    sys.exit(0 if passed == len(tests) else 1)

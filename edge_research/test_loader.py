"""Tests for the centralized Flow A holdout-exclusion enforcement (EDGE_RESEARCH_PROTOCOL.md SS8),
added as part of the 2026-07-21 TERMINAL HOLDOUT BREACH remediation (PROJECT_STATE_v2.md SS8.23).
"""
import glob
import os

import pandas as pd
import pytest

import _common
from _common import load, HoldoutConfigError, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID

CUTOFF_TS = pd.Timestamp(RESEARCH_HOLDOUT_CUTOFF_UTC)


def _raw(tf):
    path = os.path.join(_common.DATA_DIR, f"OANDA_XAUUSD_{tf}.csv")
    r = pd.read_csv(path).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    r["dt"] = pd.to_datetime(r["time"], unit="s", utc=True)
    return r


# ---------------------------------------------------------------- cutoff correctness


def test_cutoff_applied_exactly_all_retained_rows_strictly_before_cutoff():
    d, meta = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    assert (d["dt"] < CUTOFF_TS).all()


def test_bars_before_boundary_are_retained():
    raw = _raw("M15")
    before = raw[raw["dt"] < CUTOFF_TS]
    assert len(before) > 0, "fixture assumption: some M15 bars exist before the cutoff"
    d, meta = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    # the last retained bar should be the same as the raw series' last bar strictly before cutoff
    assert d["dt"].max() == before["dt"].max()
    assert len(d) == len(before)


def test_bar_at_the_boundary_is_excluded():
    raw = _raw("M15")
    at_boundary = raw[raw["dt"] == CUTOFF_TS]
    if len(at_boundary) == 0:
        pytest.skip("no M15 bar lands exactly on the cutoff instant in this data file")
    d, meta = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    assert not (d["dt"] == CUTOFF_TS).any()


def test_bars_after_boundary_are_excluded():
    raw = _raw("M15")
    after = raw[raw["dt"] > CUTOFF_TS]
    assert len(after) > 0, "fixture assumption: some M15 bars exist after the cutoff (i.e. the holdout is real)"
    d, meta = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    kept_times = set(d["dt"])
    assert kept_times.isdisjoint(set(after["dt"]))
    assert d["dt"].max() < CUTOFF_TS


def test_all_four_timeframes_respect_the_cutoff():
    for tf in ("M15", "H1", "H4", "D1"):
        d, meta = load(tf, data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
        assert (d["dt"] < CUTOFF_TS).all(), tf
        assert meta["max_date_used"] < str(CUTOFF_TS)


# ---------------------------------------------------------------- fail-closed behavior


def test_missing_data_split_id_and_cutoff_raises_type_error():
    with pytest.raises(TypeError):
        load("M15")  # no split configuration supplied at all


def test_empty_data_split_id_fails_closed():
    with pytest.raises(HoldoutConfigError):
        load("M15", data_split_id="", cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)


def test_none_data_split_id_fails_closed():
    with pytest.raises(HoldoutConfigError):
        load("M15", data_split_id=None, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)


def test_empty_cutoff_fails_closed():
    with pytest.raises(HoldoutConfigError):
        load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff="")


def test_none_cutoff_fails_closed():
    with pytest.raises(HoldoutConfigError):
        load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=None)


def test_unparseable_cutoff_fails_closed():
    with pytest.raises(HoldoutConfigError):
        load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff="not-a-real-timestamp")


def test_cutoff_before_all_data_fails_closed_rather_than_returning_empty():
    with pytest.raises(HoldoutConfigError):
        load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff="2000-01-01T00:00:00+00:00")


def test_invalid_timeframe_fails_closed():
    with pytest.raises(HoldoutConfigError):
        load("M5", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)


# ---------------------------------------------------------------- metadata correctness


def test_metadata_records_effective_date_range_and_counts():
    d, meta = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    assert meta["min_date_used"] == str(d["dt"].min())
    assert meta["max_date_used"] == str(d["dt"].max())
    assert meta["n_bars_used"] == len(d)
    assert meta["n_bars_before_cutoff"] >= meta["n_bars_used"]
    assert meta["n_bars_excluded_by_cutoff"] == meta["n_bars_before_cutoff"] - meta["n_bars_used"]
    assert meta["n_bars_excluded_by_cutoff"] > 0, "the cutoff should actually exclude real holdout rows"
    assert meta["data_split_id"] == PRE_HOLDOUT_SPLIT_ID
    assert meta["timeframe"] == "M15"


def test_holdout_excluded_is_true_only_on_successful_enforcement():
    d, meta = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    assert meta["holdout_excluded"] is True
    # every failure path above raises rather than returning a dict with holdout_excluded=False --
    # there is no code path in _common.load() that constructs `meta` before all checks pass, so a
    # meta with holdout_excluded=False can never be produced. Confirmed by source inspection here
    # rather than re-asserting each exception test again.
    import inspect
    src = inspect.getsource(_common.load)
    first_meta_assignment = src.index("meta = dict(")
    last_raise = max(src.rfind("raise HoldoutConfigError"), 0)
    assert last_raise < first_meta_assignment, (
        "every `raise HoldoutConfigError` must occur before `meta` is constructed, so a returned "
        "meta dict is never reachable except when enforcement fully succeeded")


# ---------------------------------------------------------------- no bypass path


def test_common_module_exposes_no_alternate_unfiltered_reader():
    import re
    src = inspect_source = open(_common.__file__, encoding="utf-8").read()
    # the only function definition reading data/market/*.csv must be `load` itself
    read_csv_lines = [ln for ln in src.splitlines() if "read_csv(" in ln]
    assert len(read_csv_lines) == 1, (
        f"expected exactly one pd.read_csv call site in _common.py (inside load()), found "
        f"{len(read_csv_lines)}: {read_csv_lines}")


def test_no_edge_script_reads_market_csvs_directly():
    here = os.path.dirname(os.path.abspath(__file__))
    edge_scripts = [f for f in glob.glob(os.path.join(here, "e0*.py"))]
    assert len(edge_scripts) > 0, "expected at least one e0NN_*.py edge script to check"
    offenders = []
    for path in edge_scripts:
        src = open(path, encoding="utf-8").read()
        if "read_csv(" in src or "OANDA_XAUUSD" in src:
            offenders.append(os.path.basename(path))
    assert offenders == [], (
        f"edge scripts must load market data exclusively via _common.load(), never directly: {offenders}")

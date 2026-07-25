"""Tests for the Set B (out-of-sample CONFIRMATION) loader, `_setb.py` (CEO Decision 2, 2026-07-25).

Verifies the five acceptance criteria the CEO set for this loader:
  1. EXACT border + count per timeframe (M15 16831, H1 4209, H4 1100, D1 183).
  2. FAIL-CLOSED config (missing/empty provenance or hypothesis_id, bad tf, negative warmup).
  3. CODE-LEVEL blacklist: the five TERMINAL-HOLDOUT-BREACHED edges (E025/E026/E028/E029/E032) and
     anything derived from them are refused with an exception.
  4. APPEND-ONLY access journal: every attempt (served or blocked) is recorded.
  5. A test that FAILS if the border moves by one bar in either direction.

These tests assert only on counts / borders / columns / provenance -- never on any price-derived edge
outcome -- so running them does not observe Set B for research purposes.
"""
import json

import pandas as pd
import pytest

import _setb
from _setb import (
    load_setb, countable_events, SETB_EXPECTED_BARS, SETB_START_EPOCH, SETB_END_EPOCH, BURNED_EDGES,
    SetBForbiddenError, SetBBoundaryError, SetBConfigError,
)

CLEAN = dict(hypothesis_id="E010-D1", provenance_edges=["E010"])


# ----------------------------------------------------------------- criterion 1: exact border + count

@pytest.mark.parametrize("tf,expected", sorted(SETB_EXPECTED_BARS.items()))
def test_exact_count_per_tf(tf, expected, tmp_path):
    df, meta = load_setb(tf, journal_path=str(tmp_path / "j.jsonl"), **CLEAN)
    assert int(df["in_setb"].sum()) == expected
    assert meta["n_setb"] == expected
    setb = df[df["in_setb"]]
    assert int(setb["time"].min()) >= SETB_START_EPOCH
    assert int(setb["time"].max()) <= SETB_END_EPOCH


def test_m15_first_and_last_bar_exact(tmp_path):
    df, meta = load_setb("M15", journal_path=str(tmp_path / "j.jsonl"), **CLEAN)
    setb = df[df["in_setb"]]
    assert int(setb["time"].min()) == SETB_START_EPOCH          # 2025-10-23T09:15:00Z
    assert int(setb["time"].max()) == SETB_END_EPOCH            # 2026-07-13T06:00:00Z
    assert str(setb["dt"].min()) == "2025-10-23 09:15:00+00:00"
    assert str(setb["dt"].max()) == "2026-07-13 06:00:00+00:00"


def test_no_bar_outside_window(tmp_path):
    df, _ = load_setb("M15", journal_path=str(tmp_path / "j.jsonl"), **CLEAN)
    setb = df[df["in_setb"]]
    assert (setb["time"] >= SETB_START_EPOCH).all()
    assert (setb["time"] <= SETB_END_EPOCH).all()


def test_methodology_columns_present(tmp_path):
    df, meta = load_setb("M15", journal_path=str(tmp_path / "j.jsonl"), **CLEAN)
    for col in ("dt", "atr14", "session", "dow", "in_setb"):
        assert col in df.columns
    assert meta["data_split_id"] == _setb.SETB_SPLIT_ID
    assert meta["setb_eligible"] is True


# ----------------------------------------------------------------- criterion 5: one-bar border shift

@pytest.mark.parametrize("delta", [-1, 1])
def test_one_bar_border_shift_fails(delta, tmp_path, monkeypatch):
    """If the frozen expectation is off by a single bar, the loader must fail closed."""
    patched = dict(SETB_EXPECTED_BARS)
    patched["M15"] = SETB_EXPECTED_BARS["M15"] + delta
    monkeypatch.setattr(_setb, "SETB_EXPECTED_BARS", patched)
    with pytest.raises(SetBBoundaryError):
        load_setb("M15", journal_path=str(tmp_path / "j.jsonl"), **CLEAN)


# ----------------------------------------------------------------- criterion 3: code-level blacklist

@pytest.mark.parametrize("edge", sorted(BURNED_EDGES))
def test_burned_edge_provenance_refused(edge, tmp_path):
    with pytest.raises(SetBForbiddenError):
        load_setb("M15", hypothesis_id=f"{edge}-INV", provenance_edges=[edge],
                  journal_path=str(tmp_path / "j.jsonl"))


def test_burned_via_hypothesis_id_backstop(tmp_path):
    """Even if provenance is mislabelled clean, a burned token in the hypothesis id is caught."""
    with pytest.raises(SetBForbiddenError):
        load_setb("M15", hypothesis_id="E028-INV", provenance_edges=["E999"],
                  journal_path=str(tmp_path / "j.jsonl"))


def test_mixed_provenance_with_burned_refused(tmp_path):
    with pytest.raises(SetBForbiddenError):
        load_setb("M15", hypothesis_id="mix", provenance_edges=["E010", "E028"],
                  journal_path=str(tmp_path / "j.jsonl"))


def test_clean_edge_allowed(tmp_path):
    df, meta = load_setb("M15", hypothesis_id="E015-V1", provenance_edges=["E015"],
                         journal_path=str(tmp_path / "j.jsonl"))
    assert meta["provenance_edges"] == ["E015"]
    assert int(df["in_setb"].sum()) == SETB_EXPECTED_BARS["M15"]


# ----------------------------------------------------------------- criterion 2: fail-closed config

def test_missing_provenance_raises(tmp_path):
    with pytest.raises(SetBConfigError):
        load_setb("M15", hypothesis_id="x", provenance_edges=None, journal_path=str(tmp_path / "j.jsonl"))


def test_empty_provenance_raises(tmp_path):
    with pytest.raises(SetBConfigError):
        load_setb("M15", hypothesis_id="x", provenance_edges=[], journal_path=str(tmp_path / "j.jsonl"))


def test_bare_string_provenance_raises(tmp_path):
    with pytest.raises(SetBConfigError):
        load_setb("M15", hypothesis_id="x", provenance_edges="E010", journal_path=str(tmp_path / "j.jsonl"))


def test_missing_hypothesis_id_raises(tmp_path):
    with pytest.raises(SetBConfigError):
        load_setb("M15", hypothesis_id="  ", provenance_edges=["E010"], journal_path=str(tmp_path / "j.jsonl"))


def test_bad_tf_raises(tmp_path):
    with pytest.raises(SetBConfigError):
        load_setb("M1", journal_path=str(tmp_path / "j.jsonl"), **CLEAN)


def test_negative_warmup_raises(tmp_path):
    with pytest.raises(SetBConfigError):
        load_setb("M15", warmup_bars=-1, journal_path=str(tmp_path / "j.jsonl"), **CLEAN)


# ----------------------------------------------------------------- warmup (lookback continuity)

def test_warmup_prefix_marked_not_in_setb(tmp_path):
    df, meta = load_setb("M15", warmup_bars=50, journal_path=str(tmp_path / "j.jsonl"), **CLEAN)
    assert meta["n_warmup"] == 50
    assert int(df["in_setb"].sum()) == SETB_EXPECTED_BARS["M15"]      # unchanged by warmup
    assert (~df["in_setb"]).sum() == 50
    warm = df[~df["in_setb"]]
    assert (warm["time"] < SETB_START_EPOCH).all()                   # warmup is strictly pre-window


# ----------------------------------------------------------------- condition 1: no event on warmup bar

def test_warmup_event_excluded():
    """A detector that would fire on a warmup bar must NOT enter the count (condition 1)."""
    m = pd.DataFrame({"in_setb": [False, False, True, True, True, True, True, True]})
    # anchor at index 1 is a warmup bar; index 3 is a genuine Set B bar.
    kept, report = countable_events(m, [1, 3], forward_needed=2)
    assert 1 not in kept                      # warmup event dropped
    assert 3 in kept
    assert report["excluded_warmup"] == 1


# ----------------------------------------------------------------- condition 3: right-edge exclusion

def test_right_edge_event_excluded():
    """An event whose full forward window runs past the end of the frame is excluded, not truncated."""
    m = pd.DataFrame({"in_setb": [True] * 10})
    # forward_needed=5: index 3 fits (3+1+5=9<=10), index 6 does not (6+1+5=12>10).
    kept, report = countable_events(m, [3, 6], forward_needed=5)
    assert kept == [3]
    assert report["excluded_right_edge"] == 1
    assert report["kept"] == 1


def test_countable_events_reports_both_exclusions():
    m = pd.DataFrame({"in_setb": [False, True, True, True]})
    kept, report = countable_events(m, [0, 1, 3], forward_needed=2)  # 0=warmup, 3=right-edge(3+1+2=6>4)
    assert kept == [1]
    assert report == dict(n_events=3, kept=1, excluded_warmup=1, excluded_right_edge=1, forward_needed=2)


# ----------------------------------------------------------------- criterion 4: append-only journal

def test_journal_records_served_and_blocked(tmp_path):
    jp = str(tmp_path / "j.jsonl")
    load_setb("M15", journal_path=jp, **CLEAN)                        # served
    with pytest.raises(SetBForbiddenError):
        load_setb("M15", hypothesis_id="E028-INV", provenance_edges=["E028"], journal_path=jp)  # blocked
    lines = [json.loads(x) for x in open(jp, encoding="utf-8") if x.strip()]
    assert len(lines) == 2                                           # append-only: two attempts, two rows
    outcomes = {rec["outcome"] for rec in lines}
    assert outcomes == {"served", "blocked_burned"}
    served = next(r for r in lines if r["outcome"] == "served")
    assert served["n_setb"] == SETB_EXPECTED_BARS["M15"]
    assert served["window_served"] == [SETB_START_EPOCH, SETB_END_EPOCH]


def test_journal_records_warmup_window(tmp_path):
    jp = str(tmp_path / "j.jsonl")
    _, meta = load_setb("M15", warmup_bars=50, journal_path=jp, **CLEAN)
    rec = json.loads(open(jp, encoding="utf-8").readline())
    assert rec["n_warmup"] == 50
    assert rec["warmup_window"] is not None
    lo, hi = rec["warmup_window"]
    assert lo < hi < SETB_START_EPOCH                       # warmup interval is strictly pre-window
    assert meta["warmup_window"] == rec["warmup_window"]


def test_journal_warmup_window_null_when_zero(tmp_path):
    jp = str(tmp_path / "j.jsonl")
    load_setb("M15", warmup_bars=0, journal_path=jp, **CLEAN)
    rec = json.loads(open(jp, encoding="utf-8").readline())
    assert rec["n_warmup"] == 0
    assert rec["warmup_window"] is None

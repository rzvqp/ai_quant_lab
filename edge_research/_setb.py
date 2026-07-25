"""Flow A Set B (out-of-sample CONFIRMATION) loader -- CEO Decision 2 (2026-07-25).

Set B is a SINGLE-USE confirmation resource (EDGE_RESEARCH_PROTOCOL.md 2B). A boundary error burns it
for all eleven clean edges, not just the caller -- so this module is fail-closed, blacklists the five
TERMINAL-HOLDOUT-BREACHED edges IN CODE (RULE 2B-1), and appends every access ATTEMPT (served or
blocked) to an append-only audit journal. Documentation-only rules are exactly what failed at the
original holdout breach; this is the loader-level guard.

Set B window (verified by direct count of data/market/OANDA_XAUUSD_*.csv on 2026-07-25):
    lower bound (inclusive): epoch 1761210900 = 2025-10-23T09:15:00Z
    upper bound (inclusive): epoch 1783922400 = 2026-07-13T06:00:00Z
    exact bar counts: M15 16831, H1 4209, H4 1100, D1 183

Indicator computation mirrors _common.load() EXACTLY (same dedup/sort, ATR-14, UTC-hour session buckets,
day-of-week) so a confirmation run uses identical methodology to Discovery. Optional `warmup_bars`
prepends lookback bars taken from BEFORE the Set B window (i.e. from Set A) purely so indicators at the
first Set B events match a continuous series; those warmup rows are marked `in_setb=False` and MUST NOT
be counted as events by any confirmation script.
"""
import os
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_ROOT, "data", "market")

SETB_LOADER_VERSION = "flowA_setb_v1_2026-07-25"
SETB_SPLIT_ID = "setB_confirmation_2025-10-23T09-15Z__2026-07-13T06-00Z_v1"

SETB_START_EPOCH = 1761210900   # 2025-10-23T09:15:00Z inclusive
SETB_END_EPOCH = 1783922400     # 2026-07-13T06:00:00Z inclusive

# Frozen per-timeframe expectation. Any one-bar border shift, or any data change, trips the fail-closed
# count check below (criteria 1 & 5).
SETB_EXPECTED_BARS = {"M15": 16831, "H1": 4209, "H4": 1100, "D1": 183}

# RULE 2B-1: Set B is permanently BURNED for these five edges and anything derived from them.
BURNED_EDGES = frozenset({"E025", "E026", "E028", "E029", "E032"})

DEFAULT_JOURNAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setb_access_journal.jsonl")


class SetBForbiddenError(RuntimeError):
    """Raised when a burned edge (or a hypothesis derived from one) tries to open Set B (RULE 2B-1)."""


class SetBBoundaryError(RuntimeError):
    """Raised fail-closed when the served window/count does not match the frozen Set B border exactly."""


class SetBConfigError(ValueError):
    """Raised fail-closed when the caller's provenance/identity arguments are missing or malformed."""


def _journal(path, record):
    """Append one JSON record to the append-only access journal (never overwrites)."""
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def _normalize_edges(provenance_edges):
    if provenance_edges is None:
        raise SetBConfigError(
            "provenance_edges is required -- fail-closed: name every edge this hypothesis derives from.")
    if isinstance(provenance_edges, str):
        raise SetBConfigError("provenance_edges must be a list/tuple of edge IDs, not a bare string.")
    edges = [str(e).strip().upper() for e in provenance_edges]
    if not edges or any(not e for e in edges):
        raise SetBConfigError(
            "provenance_edges is empty/blank -- fail-closed: name every edge this hypothesis derives from.")
    return edges


def load_setb(tf, *, hypothesis_id, provenance_edges, warmup_bars=0, journal_path=DEFAULT_JOURNAL):
    """Load the Set B confirmation window for `tf`. Returns (df, meta).

    df   -- cleaned bars (dedup/sort, dt UTC, atr14, session, dow) over [Set B, optionally + warmup
            prefix], with a boolean `in_setb` column (True only for genuine Set B bars). A confirmation
            script MUST count events only where `in_setb` is True.
    meta -- audit dict (split id, window bounds, counts, warmup, provenance, loader version).

    Fail-closed on: missing/empty provenance or hypothesis_id, burned-edge provenance (RULE 2B-1), any
    timeframe whose served Set B border/count does not match the frozen expectation exactly.
    """
    if tf not in SETB_EXPECTED_BARS:
        raise SetBConfigError(f"tf must be one of {sorted(SETB_EXPECTED_BARS)}, got {tf!r}")
    if not hypothesis_id or not str(hypothesis_id).strip():
        raise SetBConfigError("hypothesis_id is required -- fail-closed: every Set B access is attributed.")
    edges = _normalize_edges(provenance_edges)

    ts = datetime.now(timezone.utc).isoformat()

    # RULE 2B-1 blacklist -- check declared provenance AND a hypothesis_id token backstop.
    hid_upper = str(hypothesis_id).upper()
    burned_hit = sorted(set(edges) & BURNED_EDGES) or sorted(e for e in BURNED_EDGES if e in hid_upper)
    if burned_hit:
        _journal(journal_path, dict(ts=ts, outcome="blocked_burned", hypothesis_id=str(hypothesis_id),
                                    provenance_edges=edges, tf=tf, burned_hit=list(burned_hit),
                                    loader_version=SETB_LOADER_VERSION))
        raise SetBForbiddenError(
            f"Set B is BURNED for {list(burned_hit)} (RULE 2B-1, EDGE_RESEARCH_PROTOCOL.md 2B). "
            f"Hypothesis {hypothesis_id!r} derives from a TERMINAL-HOLDOUT-BREACHED edge and may never "
            f"use Set B, in any form. Freeze it in-sample-only / AWAITING UNSEEN DATA instead.")

    if warmup_bars < 0:
        raise SetBConfigError("warmup_bars must be >= 0.")

    path = os.path.join(DATA_DIR, f"OANDA_XAUUSD_{tf}.csv")
    raw = pd.read_csv(path).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    raw["dt"] = pd.to_datetime(raw["time"], unit="s", utc=True)

    positions = raw.index[(raw["time"] >= SETB_START_EPOCH) & (raw["time"] <= SETB_END_EPOCH)]
    if len(positions) == 0:
        raise SetBBoundaryError(f"No Set B bars found for {tf} -- fail-closed.")
    first_pos, last_pos = int(positions.min()), int(positions.max())
    n_setb = int(len(positions))
    expected = SETB_EXPECTED_BARS[tf]

    # Border enforcement (criteria 1 & 5): exact count, plus the bracketing bars on the correct side of
    # each bound. A one-bar shift in either direction changes the count and trips this.
    if n_setb != expected:
        raise SetBBoundaryError(
            f"{tf}: served Set B count {n_setb} != frozen expected {expected} -- fail-closed "
            f"(border moved or data changed; refusing to serve a shifted/truncated Set B).")
    if first_pos > 0 and int(raw["time"].iloc[first_pos - 1]) >= SETB_START_EPOCH:
        raise SetBBoundaryError(f"{tf}: bar before window not strictly below lower bound -- fail-closed.")
    if last_pos < len(raw) - 1 and int(raw["time"].iloc[last_pos + 1]) <= SETB_END_EPOCH:
        raise SetBBoundaryError(f"{tf}: bar after window not strictly above upper bound -- fail-closed.")
    if int(raw["time"].iloc[first_pos]) < SETB_START_EPOCH or int(raw["time"].iloc[last_pos]) > SETB_END_EPOCH:
        raise SetBBoundaryError(f"{tf}: served bars fall outside [start, end] -- fail-closed.")

    warmup_start_pos = max(0, first_pos - int(warmup_bars))
    n_warmup = first_pos - warmup_start_pos
    if warmup_bars > 0 and n_warmup < warmup_bars:
        raise SetBBoundaryError(
            f"{tf}: requested warmup {warmup_bars} but only {n_warmup} pre-window bars exist -- "
            f"fail-closed (refusing to silently serve a shorter warmup).")

    sl = raw.iloc[warmup_start_pos:last_pos + 1].copy().reset_index(drop=True)

    # Indicators computed on the continuous slice, EXACTLY as _common.load() does.
    h, l, c = sl["high"], sl["low"], sl["close"]
    tr = np.maximum(h - l, np.maximum((h - c.shift()).abs(), (l - c.shift()).abs()))
    sl["atr14"] = tr.rolling(14).mean()
    hh = sl["dt"].dt.hour
    sl["session"] = np.select([hh < 8, hh < 13, hh < 21], ["asia", "london", "ny"], default="late")
    sl["dow"] = sl["dt"].dt.day_name()
    sl["in_setb"] = (sl["time"] >= SETB_START_EPOCH) & (sl["time"] <= SETB_END_EPOCH)

    # Post-condition: in_setb count must still equal expected (defends against any slice/warmup bug).
    if int(sl["in_setb"].sum()) != expected:
        raise SetBBoundaryError(
            f"{tf}: post-slice in_setb count {int(sl['in_setb'].sum())} != {expected} -- fail-closed.")

    setb_rows = sl[sl["in_setb"]]
    warm_rows = sl[~sl["in_setb"]]
    warmup_window = ([int(warm_rows["time"].min()), int(warm_rows["time"].max())]
                     if len(warm_rows) else None)
    meta = dict(
        data_split_id=SETB_SPLIT_ID,
        setb_start=pd.Timestamp(SETB_START_EPOCH, unit="s", tz="UTC").isoformat(),
        setb_end=pd.Timestamp(SETB_END_EPOCH, unit="s", tz="UTC").isoformat(),
        min_setb_date=str(setb_rows["dt"].min()),
        max_setb_date=str(setb_rows["dt"].max()),
        n_setb=expected,
        n_warmup=int(n_warmup),
        warmup_bars_requested=int(warmup_bars),
        warmup_window=warmup_window,
        timeframe=tf,
        hypothesis_id=str(hypothesis_id),
        provenance_edges=edges,
        setb_eligible=True,
        loader_version=SETB_LOADER_VERSION,
    )
    _journal(journal_path, dict(ts=ts, outcome="served", hypothesis_id=str(hypothesis_id),
                                provenance_edges=edges, tf=tf,
                                window_requested=[SETB_START_EPOCH, SETB_END_EPOCH],
                                window_served=[int(setb_rows["time"].min()), int(setb_rows["time"].max())],
                                n_setb=expected, n_warmup=int(n_warmup), warmup_window=warmup_window,
                                loader_version=SETB_LOADER_VERSION))
    return sl, meta


def countable_events(m, anchor_indices, forward_needed):
    """Filter events to genuine Set B events that also have a FULL forward result window.

    Enforces two CEO STEP-2 conditions in one place (so both are testable):
      * Condition 1 -- an event anchored on a warmup bar (`in_setb == False`) is NEVER counted.
      * Condition 3 -- an event whose full forward window runs past the end of the loaded frame
        (`anchor_idx + 1 + forward_needed > len(m)`) is right-censored and excluded, not truncated.

    Returns (kept_indices, report). `report` breaks the exclusions down into `excluded_warmup` and
    `excluded_right_edge` so both are reported separately, never silently dropped.
    """
    anchors = [int(i) for i in anchor_indices]
    in_setb = m["in_setb"].values
    n = len(m)
    kept, exc_warm, exc_edge = [], 0, 0
    for idx in anchors:
        if not bool(in_setb[idx]):
            exc_warm += 1
            continue
        if idx + 1 + int(forward_needed) > n:
            exc_edge += 1
            continue
        kept.append(idx)
    report = dict(n_events=len(anchors), kept=len(kept), excluded_warmup=exc_warm,
                  excluded_right_edge=exc_edge, forward_needed=int(forward_needed))
    return kept, report

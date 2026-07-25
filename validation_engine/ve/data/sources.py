"""Loader STREAMING — încarcă DOAR fereastra deschisă, se oprește la granița sigilată.

Citește rândurile CSV în ordine crescătoare a timpului și se oprește la primul rând
cu `ts ≥ granița sigilată`: rândurile sigilate NU sunt parsate în memorie. Verifică
integritatea (hash), monotonia, duplicatele și validitatea OHLC — fail-closed.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from . import integrity, sealing
from .access_journal import AccessEntry, AccessJournal


class DataLoadError(RuntimeError):
    """Anomalie de date (duplicat, ne-monoton, OHLC invalid, fereastră neacoperită)."""


@dataclass
class Series:
    source_id: str
    time: list
    open: list
    high: list
    low: list
    close: list
    volume: list

    def __len__(self) -> int:
        return len(self.time)


def load_open_window(
    source_id: str,
    declared_sha256: str,
    window_start_epoch: int,
    window_end_epoch: int,
    bounds: str,
    journal: AccessJournal,
) -> Series:
    """Încarcă fereastra [start, end] ∩ fereastra deschisă. Fail-closed pe anomalii/holdout."""
    # 0. holdout: F4 refuză ferestrele care ating granița sigilată
    sealing.assert_open_window(window_end_epoch, bounds)

    # 1. integritate (hash pe fișier întreg — nu parsează rânduri sigilate)
    path, actual_hash = integrity.resolve_and_verify(source_id, declared_sha256)
    journal.record(AccessEntry(source_id=source_id, path=str(path), kind="hash_read"))

    boundary = sealing.boundary_epoch()
    lo_inc = bounds[0] == "["
    hi_inc = bounds[-1] == "]"

    times, o, h, l, c, v = [], [], [], [], [], []
    last_ts = None
    stopped = False
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            ts = int(row["time"])
            # OPRIRE la granița sigilată — rândurile sigilate nu se parsează
            if ts >= boundary:
                stopped = True
                break
            # fereastra cerută
            if ts < window_start_epoch or (not lo_inc and ts == window_start_epoch):
                continue
            if ts > window_end_epoch or (not hi_inc and ts == window_end_epoch):
                continue
            # anomalii
            if last_ts is not None and ts <= last_ts:
                raise DataLoadError(
                    f"'{source_id}': timp ne-monoton/duplicat la {ts} (după {last_ts})"
                )
            hi = float(row["high"]); lo = float(row["low"])
            op = float(row["open"]); cl = float(row["close"])
            if hi < lo or hi < max(op, cl) or lo > min(op, cl):
                raise DataLoadError(f"'{source_id}': OHLC invalid la {ts}")
            times.append(ts); o.append(op); h.append(hi); l.append(lo); c.append(cl)
            v.append(float(row["volume"]))
            last_ts = ts

    if not times:
        raise DataLoadError(
            f"'{source_id}': fereastra [{window_start_epoch}, {window_end_epoch}] "
            "nu conține nicio bară deschisă"
        )

    journal.record(AccessEntry(
        source_id=source_id, path=str(path), kind="data_read",
        rows_read=len(times), max_ts_read=times[-1], stopped_at_boundary=stopped,
    ))
    return Series(source_id, times, o, h, l, c, v)

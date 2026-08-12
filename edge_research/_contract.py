"""Canonical MEASUREMENT CONTRACT v1.0 — R8 (trading day) + R9 (data population). Data Acquisition.

Step 3 of the implementation order. Single source of truth so every engine measures on the SAME
population (R9) and the SAME trading-day delimitation (R8). Read-only w.r.t. the manifest and the
data files (never mutates M15_v2 / M5 / the manifest).

R9 — DATA POPULATION: the official manifest segmentation, EXCLUSIVELY. Reconstructing the population
by auto-splitting on temporal gaps is forbidden when it differs from the manifest (this is the M-4
divergence: _screen derived contiguity blocks from >72h gaps while the manifest defines the exact
discovery segments — different populations, incomparable numbers). `dataset_identity()` gives any
engine a verifiable id+version; `official_blocks()` gives the ONLY legitimate population blocks;
`assert_population_matches_manifest()` is the fail-closed tripwire.

R8 — TRADING DAY: 17:00 America/New_York, IANA tz, DST-aware. Every calculation that uses the
previous day, PDH, PDL, daily range, or session rollover must consume `trading_day_index()` — the
same delimiter as code/resample_ny.py (the D1 anchor) and edge_research._screen.day_index_ny17.
"""
from __future__ import annotations

from typing import Any, Optional, Sequence

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

from edge_research.split_manifest import (
    entry_file,
    load_manifest,
    resolve,
    segmentation_plan,
)

NY_TZ = "America/New_York"
TRADING_DAY_ANCHOR_HOUR = 17  # 17:00 NY (OANDA session boundary), DST-aware via IANA tz
CONTRACT_VERSION = "v1.0"


class PopulationContractError(ValueError):
    """Raised (fail-closed) when a candidate population diverges from the manifest (R9)."""


# ----------------------------------- R8: TRADING DAY -----------------------------------
def trading_day_index(time: Any) -> np.ndarray:
    """17:00-NY anchored trading-day ordinal (IANA tz, DST-aware). Input: epoch seconds (array-like).
    Output: int64 day ordinals; previous trading day = ordinal - 1. PDH/PDL/daily-range/session
    rollover MUST all consume THIS (R8). Byte-identical convention to resample_ny.py's D1 anchor and
    _screen.day_index_ny17 (floor(NY_wall_clock - 17h))."""
    dt = pd.to_datetime(np.asarray(time), unit="s", utc=True)
    ny = dt.tz_convert(NY_TZ).tz_localize(None)
    d = (ny - pd.Timedelta(hours=TRADING_DAY_ANCHOR_HOUR)).floor("D")
    return np.asarray(d.values.astype("datetime64[D]").astype("int64"), dtype=np.int64)


def trading_day_start_utc(time: Any) -> np.ndarray:
    """UTC epoch of the 17:00-NY boundary that opens each bar's trading day (the session rollover
    instant). Useful for engines that bucket intraday by trading day instead of UTC hour."""
    dt = pd.to_datetime(np.asarray(time), unit="s", utc=True)          # DatetimeIndex (tz-aware)
    ny = dt.tz_convert(NY_TZ).tz_localize(None)                        # naive NY wall clock
    day_start_ny = (ny - pd.Timedelta(hours=TRADING_DAY_ANCHOR_HOUR)).floor("D") + pd.Timedelta(hours=TRADING_DAY_ANCHOR_HOUR)
    utc = day_start_ny.tz_localize(NY_TZ, ambiguous=True, nonexistent="shift_forward").tz_convert("UTC")
    # resolution-agnostic epoch-seconds (same idiom as code/resample_ny.py), not asi8 (unit varies)
    secs = (utc - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(seconds=1)
    return np.asarray(secs, dtype=np.int64)


# ----------------------------------- R9: POPULATION -----------------------------------
def dataset_identity(tf: str, *, manifest: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Verifiable identity+version for `tf`: file_path, sha256, manifest version, discovery
    segmentation. Any engine can call this to PROVE it measured the same dataset (R9)."""
    m = manifest or load_manifest()
    kind, _ = resolve(m, tf)
    fp, sha = entry_file(m, tf)
    disc: list[tuple[int, int]] = []
    if kind == "timeframe":
        disc = segmentation_plan(m, tf)["discovery"]
    return {
        "tf": tf, "kind": kind, "file_path": fp, "sha256": sha,
        "manifest_version": m.get("version"), "contract_version": CONTRACT_VERSION,
        "discovery_segments": disc, "n_discovery_segments": len(disc),
    }


def official_blocks(
    df: pd.DataFrame, tf: Optional[str] = None, *,
    manifest: Optional[dict[str, Any]] = None,
    discovery_segments: Optional[Sequence[tuple[int, int]]] = None,
) -> list[tuple[int, int]]:
    """Index ranges (start, end) into `df` (sorted by 'time') for each MANIFEST discovery segment --
    the ONLY legitimate population blocks (R9). `df` must be the discovery population from
    _common.load. Provide `tf` (reads the manifest) or `discovery_segments` directly."""
    if discovery_segments is None:
        m = manifest or load_manifest()
        discovery_segments = segmentation_plan(m, tf)["discovery"]  # type: ignore[arg-type]
    t = df["time"].to_numpy()
    out: list[tuple[int, int]] = []
    for s_ep, e_ep in discovery_segments:
        lo = int(np.searchsorted(t, s_ep, side="left"))
        hi = int(np.searchsorted(t, e_ep, side="right"))
        if hi > lo:
            out.append((lo, hi))
    return out


def _as_pairs(blocks: Any) -> list[tuple[int, int]]:
    pairs = []
    for b in blocks:
        if hasattr(b, "start") and hasattr(b, "end"):
            pairs.append((int(b.start), int(b.end)))
        else:
            pairs.append((int(b[0]), int(b[1])))
    return pairs


def assert_population_matches_manifest(
    df: pd.DataFrame, tf: Optional[str] = None, *, candidate_blocks: Any,
    manifest: Optional[dict[str, Any]] = None,
    discovery_segments: Optional[Sequence[tuple[int, int]]] = None,
) -> list[tuple[int, int]]:
    """R9 fail-closed tripwire: raise if `candidate_blocks` (e.g. gap-derived) differ from the
    manifest's official discovery blocks. Turns a silent population divergence (M-4) into a loud
    error instead of 'incomparable numbers'. Returns the official blocks on success."""
    official = official_blocks(df, tf, manifest=manifest, discovery_segments=discovery_segments)
    cand = _as_pairs(candidate_blocks)
    if cand != official:
        raise PopulationContractError(
            f"R9 population divergence"
            f"{f' for {tf}' if tf else ''}: candidate blocks {cand} != manifest official {official}. "
            f"Gap-based reconstruction that differs from the manifest is forbidden (contract {CONTRACT_VERSION})."
        )
    return official

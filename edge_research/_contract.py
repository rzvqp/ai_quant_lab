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
def canonical_discovery_blocks(
    manifest: dict[str, Any], tf: str
) -> list[tuple[int, int]]:
    """The CANONICAL discovery-block list (epoch ranges, half-open [start,end)) -- the ONLY population
    authority. For M15_v2 this is `context_derived_htf.m15_v2_discovery_blocks` = **FOUR** blocks,
    INCLUDING the 2022-12-16 -> 2025-10-12 block sourced from `overlap_with_M15` (M15's inherited
    discovery classification). CEO decision 2026-08-13: the 4th block is MANDATORY -- it is the most
    recent and largest; windowing on only the three `regime_segments.discovery_range` entries (what
    `segmentation_plan` returns) would silently discard ~3 years (a second error, opposite to M-4).
    The 4th REGIME_SEGMENT (bull_partial, too short) is sealed and correctly has no discovery_range;
    that is a DIFFERENT entity from the 4th discovery BLOCK, which is full discovery. For any other tf
    the segmentation_plan discovery ranges are canonical (no overlap block exists there)."""
    cdh = manifest.get("context_derived_htf", {})
    blks = cdh.get("m15_v2_discovery_blocks") if isinstance(cdh, dict) else None
    if tf == "M15_v2" and blks:
        return [(int(b["start_epoch"]), int(b["end_epoch"])) for b in blks]
    return segmentation_plan(manifest, tf)["discovery"]


def dataset_identity(tf: str, *, manifest: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Verifiable identity+version for `tf` -- the COMPLETE data-side provenance block (R11 dims that
    Data Acquisition owns). file_path, sha256, manifest version, symbol/source/timeframe/bar_seconds,
    and the discovery segmentation. Any engine can call this to PROVE it measured the same dataset."""
    m = manifest or load_manifest()
    kind, entry = resolve(m, tf)
    fp, sha = entry_file(m, tf)
    disc: list[tuple[int, int]] = []
    if kind == "timeframe":
        disc = canonical_discovery_blocks(m, tf)  # FOUR for M15_v2 (incl. the overlap block)
    base = fp.rsplit("/", 1)[-1]
    source = base.split("_", 1)[0] if "_" in base else None            # e.g. OANDA
    symbol = base.split("_")[1] if base.count("_") >= 1 else None       # e.g. XAUUSD
    return {
        "tf": tf, "kind": kind, "file_path": fp, "sha256": sha,
        "source": source, "symbol": symbol, "bar_seconds": entry.get("bar_seconds"),
        "manifest_version": m.get("version"), "contract_version": CONTRACT_VERSION,
        "discovery_segments": disc, "n_discovery_segments": len(disc),
    }


# R11 PROVENANCE — the 13 measurement-provenance dimensions a result needs to be reproducible AND
# comparable. Red Team's Test 17 fails everywhere because engines label none. This schema names each
# dimension, its OWNER, and whether Data Acquisition already supplies it via dataset_identity/loader
# meta. Data Acquisition owns the DATA-SIDE block (1-4); the CONVENTION block (5-10) is the
# Statistician/VE's; the ENGINE-RUN block (11-13) is the Research-Lab engine/harness's. Any single
# result stamp must concatenate all three blocks -- today only 1-4 exist.
PROVENANCE_R11: tuple[dict[str, str], ...] = (
    {"dim": "dataset_identity", "owner": "DataAcq", "status": "SUPPLIED (dataset_identity: file_path+sha256)"},
    {"dim": "dataset_version", "owner": "DataAcq", "status": "SUPPLIED (manifest_version + contract_version)"},
    {"dim": "instrument_source_tf", "owner": "DataAcq", "status": "SUPPLIED (symbol+source+tf+bar_seconds)"},
    {"dim": "population_segmentation", "owner": "DataAcq", "status": "SUPPLIED (official_blocks + split_id + cutoff + holdout flag)"},
    {"dim": "trading_day_timezone", "owner": "Statistician/VE (delimiter provided by DataAcq)", "status": "MISSING label (R8 delimiter=trading_day_index; engines must STAMP which convention they used)"},
    {"dim": "cost_model", "owner": "Statistician/VE", "status": "MISSING (spread/slippage/commission; CFG in canonical evaluator)"},
    {"dim": "execution_convention", "owner": "Statistician/VE", "status": "MISSING (entry@next-open, intrabar stop-before-target, no-overlap, floored stop)"},
    {"dim": "evaluator_identity", "owner": "Statistician/VE", "status": "MISSING (which evaluator+version; now mstrat.simulate canonical)"},
    {"dim": "metric_definitions", "owner": "Statistician/VE", "status": "MISSING (R10: net-vs-gross, censoring, best_trade_share field)"},
    {"dim": "random_seed", "owner": "Statistician/VE", "status": "MISSING (CFG['seed'] for null pools / subsampling)"},
    {"dim": "strategy_hypothesis_id", "owner": "Engine (Research Lab)", "status": "PARTIAL (families compute a canonical hid; not emitted in a provenance stamp)"},
    {"dim": "code_commit", "owner": "Engine (Research Lab)", "status": "MISSING (git commit / RATIFIED_CODE_DIR snapshot that produced the result)"},
    {"dim": "run_env_timestamp", "owner": "Engine (Research Lab)", "status": "MISSING (run timestamp + pandas/numpy/python versions + platform)"},
)


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
        discovery_segments = canonical_discovery_blocks(m, tf)  # type: ignore[arg-type]  # FOUR for M15_v2
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
    # TILING invariant: the official blocks must partition [0, len(df)) contiguously -- no gap, no
    # overlap, every delivered bar inside exactly one manifest discovery segment. A violation means a
    # non-discovery bar leaked into the delivered population (or the loader's block map drifted).
    n = len(df)
    prev_end = 0
    covered = 0
    for s, e in official:
        if e <= s or s != prev_end:
            raise PopulationContractError(
                f"R9 tiling violation{f' for {tf}' if tf else ''}: block {(s, e)} does not abut the "
                f"previous block end {prev_end} (gap/overlap in the delivered population)."
            )
        prev_end = e
        covered += e - s
    if prev_end != n or covered != n:
        raise PopulationContractError(
            f"R9 coverage violation{f' for {tf}' if tf else ''}: official blocks cover {covered} bars "
            f"up to index {prev_end}, but the delivered frame has {n} -- a bar falls outside the "
            f"manifest discovery segmentation (leak) or the plan under-covers the frame."
        )
    return official

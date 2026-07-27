"""Flow A (Alpha Discovery Laboratory) shared utilities.

Deliberately independent of `code/` and `ai_trader/` (per the two-flow separation in
PROJECT_STATE_v2.md SS1.1 / NEXT_SESSION.md SS B) -- reads only the raw market CSVs in
`data/market/`, never imports the frozen Research Lab engine or any ai_trader package.
Any formula reused here (ATR-14, UTC-hour session buckets) is reproduced independently
and disclosed in each edge's own research log, not imported as a dependency.

HOLDOUT ENFORCEMENT (added 2026-07-21, EDGE_RESEARCH_PROTOCOL.md SS8, following the TERMINAL HOLDOUT
BREACH incident -- PROJECT_STATE_v2.md SS8.23): `load()` below is the ONLY data-reading entry point
this package exposes. It requires an explicit `data_split_id` and `cutoff` (no defaults, keyword-only)
and applies the cutoff as an EXCLUSIVE upper bound on the `dt` column BEFORE any indicator (ATR,
session, day-of-week) is computed -- no holdout-period row is ever loaded into a computed column, let
alone aggregated into a statistic. There is no alternate/raw loading path in this module; any script
that wants Flow A market data must call this function with real split configuration or the call fails
closed (raises `HoldoutConfigError`).
"""
import os
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

from .split_manifest import (
    IdentifierError,
    ManifestError,
    entry_file,
    load_manifest,
    segmentation_plan,
    verify_data_file,
)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_ROOT, "data", "market")

LOADER_VERSION = "flowA_common_v5_runtime_segmentation_2026-07-27"

# CEO-approved boundary (authorization message, 2026-07-21): the Research Lab's own consumed/invalidated
# terminal holdout, 2025-10-23 09:15 UTC -> 2026-07-13 06:00 UTC. No observation at or after the start of
# that window may be loaded, aggregated, sampled, transformed, or used by Flow A. Exclusive upper bound.
RESEARCH_HOLDOUT_CUTOFF_UTC = "2025-10-23T09:15:00+00:00"

# The split identifier every clean rerun in this remediation batch uses -- the M15/H1/H4/D1 history
# strictly before the cutoff above. This does NOT restore the old sealed holdout (PROJECT_STATE_v2.md
# SS8.23 is explicit that nothing here does that) -- it only produces a holdout-clean research rerun.
PRE_HOLDOUT_SPLIT_ID = "pre_holdout_2025-10-23T09-15-00Z_v1"


class HoldoutConfigError(ValueError):
    """Raised when `load()` cannot fail-closed-verify its holdout configuration."""


def load(tf: str, *, data_split_id: str, cutoff: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    """The sole data-reading entry point for Flow A. `tf` must name an exact key in the split manifest
    (`config/split_manifest.json`) -- 'M15', 'M15_v2', 'M5', 'H1' -- with no alias, default, or fallback;
    an unknown/ambiguous key raises `split_manifest.IdentifierError` (distinct from a hash or status
    failure). Every access is gated fail-closed by: the manifest's own content_hash; the timeframe
    status being exactly ``VALIDATED`` (H1 = AWAITING_REGIME_MAP is 100% sealed); and the governed data
    file's SHA-256 (resolved from the entry's file_path, so 'M15' -> legacy superseded file and 'M15_v2'
    -> extended canonical file) matching the manifest.

    For a VALIDATED timeframe the loader delivers, at runtime, EXACTLY the union of the manifest's
    per-segment discovery halves (or M15's single discovery_range), intersected with the caller `cutoff`
    (which may tighten but never widen). Every embargo band -- the leading/intra/trailing quarantine of
    each segment -- and every sealed half, fully-sealed segment, inherited overlap, and unlabeled tail
    are excluded. All coordinates come verbatim from the manifest; none are recomputed. The plan is
    applied on the epoch column BEFORE any indicator/session/day-of-week computation.

    `data_split_id` and `cutoff` are mandatory keyword-only (no default) -- calling without both is a
    TypeError; an empty value for either raises `HoldoutConfigError`.

    Returns `(df, meta)`. `df` is the delivered discovery bars, sorted/deduped, with UTC `dt`, ATR-14,
    session, and day-of-week. `meta` includes `manifest_version`, `manifest_hash`, `data_file_path`,
    `data_file_sha256`, `n_discovery_segments`, and the segmentation accounting that tiles the whole file
    -- `n_bars_before_cutoff` == `n_bars_delivered` + `n_bars_quarantine` + `n_bars_sealed` (with
    `n_bars_discovery_plan` the pre-cutoff discovery count) -- plus `min_date_used`, `max_date_used`,
    `n_bars_used`, `loader_version`, `timeframe`.
    """
    if not data_split_id:
        raise HoldoutConfigError(
            "data_split_id is required -- fail-closed: this loader assumes no default split.")
    if not cutoff:
        raise HoldoutConfigError(
            "cutoff is required -- fail-closed: this loader assumes no default cutoff "
            "(it will NOT silently load the full, holdout-contaminated dataset).")
    try:
        cutoff_ts = pd.Timestamp(cutoff)
    except Exception as e:
        raise HoldoutConfigError(f"cutoff {cutoff!r} could not be parsed as a timestamp: {e}") from e
    cutoff_ts = cutoff_ts.tz_localize("UTC") if cutoff_ts.tzinfo is None else cutoff_ts.tz_convert("UTC")

    # MANIFEST GATE -- every check below is fail-closed:
    #   * load_manifest() verifies the manifest's own content_hash.
    #   * segmentation_plan()/entry_file() require status EXACTLY "VALIDATED" (H1 = AWAITING_REGIME_MAP
    #     is sealed) and resolve the governed file from the entry's file_path (so 'M15' -> legacy
    #     superseded file, 'M15_v2' -> extended canonical file, with no alias/default between the keys).
    #   * verify_data_file() checks that file's SHA-256 against the manifest -- a swapped or one-byte-
    #     modified data file is rejected.
    #   * an unknown/ambiguous timeframe key raises IdentifierError, re-raised DISTINCTLY (not as the
    #     generic HoldoutConfigError) so it is diagnosable apart from a hash or a status failure.
    try:
        manifest = load_manifest()
        plan = segmentation_plan(manifest, tf)
        file_path, expected_sha = entry_file(manifest, tf)
        data_path = verify_data_file(_ROOT, file_path, expected_sha)
    except IdentifierError:
        raise
    except ManifestError as e:
        raise HoldoutConfigError(str(e)) from e

    raw = pd.read_csv(data_path).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    raw["dt"] = pd.to_datetime(raw["time"], unit="s", utc=True)
    n_before = int(len(raw))
    ep = raw["time"]

    # RUNTIME SEGMENTATION. Deliver ONLY the union of the manifest's discovery ranges, intersected with
    # the caller cutoff (which may tighten but never widen). Every embargo band (leading/intra/trailing
    # per segment, or M15's single embargo_range) is quarantine; everything outside discovery and
    # quarantine -- fully-sealed segments, the M15_v2 overlap and post-M15 tail, any unlabeled recent
    # tail -- is sealed by default. Ranges are half-open [start_epoch, end_epoch), used verbatim from the
    # manifest, and applied on the epoch column BEFORE any indicator/session/day-of-week computation.
    in_disc = pd.Series(False, index=raw.index)
    for s_ep, e_ep in plan["discovery"]:
        in_disc = in_disc | ((ep >= s_ep) & (ep < e_ep))
    in_quar = pd.Series(False, index=raw.index)
    for s_ep, e_ep in plan["quarantine"]:
        in_quar = in_quar | ((ep >= s_ep) & (ep < e_ep))
    if bool((in_disc & in_quar).any()):
        raise HoldoutConfigError(
            f"{tf}: manifest discovery and quarantine ranges overlap -- fail-closed (malformed plan).")
    n_discovery = int(in_disc.sum())
    n_quarantine = int(in_quar.sum())
    n_sealed = n_before - n_discovery - n_quarantine
    if n_sealed < 0:
        raise HoldoutConfigError(f"{tf}: segmentation plan over-covers the file -- fail-closed.")

    d = raw.loc[in_disc & (raw["dt"] < cutoff_ts)].reset_index(drop=True)
    if len(d) == 0:
        raise HoldoutConfigError(
            f"the manifest discovery union for {tf} (under cutoff {cutoff_ts.isoformat()}) excluded all "
            f"{n_before} rows -- check alignment (fail-closed: refusing an empty, unauditable result).")

    h, l, c = d["high"], d["low"], d["close"]
    tr = np.maximum(h - l, np.maximum((h - c.shift()).abs(), (l - c.shift()).abs()))
    d["atr14"] = tr.rolling(14).mean()
    hh = d["dt"].dt.hour
    d["session"] = np.select([hh < 8, hh < 13, hh < 21], ["asia", "london", "ny"], default="late")
    d["dow"] = d["dt"].dt.day_name()

    manifest_ch: Any = manifest.get("content_hash", {})
    meta: dict[str, Any] = dict(
        data_split_id=data_split_id,
        requested_cutoff=cutoff_ts.isoformat(),
        manifest_version=manifest.get("version"),
        manifest_hash=manifest_ch.get("value") if isinstance(manifest_ch, dict) else None,
        data_file_path=file_path,
        data_file_sha256=expected_sha,
        n_discovery_segments=len(plan["discovery"]),
        holdout_excluded=True,
        min_date_used=str(d["dt"].min()),
        max_date_used=str(d["dt"].max()),
        # Segmentation accounting -- these three tile the whole file: delivered + quarantine + sealed.
        n_bars_before_cutoff=n_before,
        n_bars_delivered=int(len(d)),
        n_bars_discovery_plan=n_discovery,
        n_bars_quarantine=n_quarantine,
        n_bars_sealed=n_sealed,
        n_bars_used=int(len(d)),
        loader_version=LOADER_VERSION,
        timeframe=tf,
    )
    return d, meta


def vol_regime(d: pd.DataFrame, col: str = "atr14", window: int = 200) -> pd.Series:
    """Rolling percentile rank of ATR -> low/mid/high tercile, using only trailing (lookahead-safe) data."""
    pr = d[col].rolling(window).apply(lambda x: (x[:-1] < x[-1]).mean() if len(x) > 1 else np.nan, raw=True)
    return pd.cut(pr, bins=[-0.01, 1 / 3, 2 / 3, 1.01], labels=["low", "mid", "high"])


def bootstrap_mean_ci(x: np.ndarray, n_boot: int = 5000, seed: int = 7) -> tuple[float, float, float]:
    if len(x) == 0:
        return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    boots = x[idx].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return (float(x.mean()), float(lo), float(hi))


def summarize(x: np.ndarray) -> dict[str, Any]:
    x = np.asarray(x, dtype=float)
    if len(x) == 0:
        return dict(n=0)
    mean, lo, hi = bootstrap_mean_ci(x)
    return dict(n=int(len(x)), mean=mean, ci95=[lo, hi], median=float(np.median(x)),
                std=float(np.std(x)), ci_excludes_zero=bool(lo > 0 or hi < 0))

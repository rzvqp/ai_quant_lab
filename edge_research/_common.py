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
import numpy as np
import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_ROOT, "data", "market")

LOADER_VERSION = "flowA_common_v2_holdout_enforced_2026-07-21"

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


def load(tf: str, *, data_split_id: str, cutoff: str) -> tuple:
    """The sole data-reading entry point for Flow A. tf in {'M15','H1','H4','D1'}.

    `data_split_id` and `cutoff` are mandatory keyword-only arguments with no default -- calling this
    function without both explicitly supplied is a TypeError (Python's own fail-closed behavior); an
    explicitly empty/None value for either raises `HoldoutConfigError`. `cutoff` is applied as an
    EXCLUSIVE upper bound (`dt < cutoff`) on the UTC `dt` column immediately after parsing, before ATR/
    session/day-of-week are computed -- so no holdout-period observation is ever aggregated or
    transformed, not even transiently.

    Returns `(df, meta)`. `df` is sorted by time, deduped, with a UTC `dt` column, ATR-14, session tag,
    and day-of-week, restricted to `dt < cutoff`. `meta` is the auditable split-metadata dict required by
    EDGE_RESEARCH_PROTOCOL.md SS8: `data_split_id`, `holdout_cutoff`, `holdout_excluded` (True only when
    this function returns successfully -- there is no code path that returns False; failure raises
    instead), `min_date_used`, `max_date_used`, `n_bars_used`, `n_bars_before_cutoff`,
    `n_bars_excluded_by_cutoff`, `loader_version`, `timeframe`.
    """
    if tf not in ("M15", "H1", "H4", "D1"):
        raise HoldoutConfigError(f"tf must be one of M15/H1/H4/D1, got {tf!r}")
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

    path = os.path.join(DATA_DIR, f"OANDA_XAUUSD_{tf}.csv")
    raw = pd.read_csv(path).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    raw["dt"] = pd.to_datetime(raw["time"], unit="s", utc=True)
    n_before = int(len(raw))

    # Cutoff applied HERE, before any indicator/session/day-of-week computation -- no holdout row is
    # ever fed into ATR, session tagging, or any later aggregation.
    d = raw.loc[raw["dt"] < cutoff_ts].reset_index(drop=True)
    if len(d) == 0:
        raise HoldoutConfigError(
            f"cutoff {cutoff_ts.isoformat()} excluded all {n_before} rows for {tf} -- "
            f"check cutoff/data alignment (fail-closed: refusing to return an empty, unauditable result).")

    h, l, c = d["high"], d["low"], d["close"]
    tr = np.maximum(h - l, np.maximum((h - c.shift()).abs(), (l - c.shift()).abs()))
    d["atr14"] = tr.rolling(14).mean()
    hh = d["dt"].dt.hour
    d["session"] = np.select([hh < 8, hh < 13, hh < 21], ["asia", "london", "ny"], default="late")
    d["dow"] = d["dt"].dt.day_name()

    meta = dict(
        data_split_id=data_split_id,
        holdout_cutoff=cutoff_ts.isoformat(),
        holdout_excluded=True,
        min_date_used=str(d["dt"].min()),
        max_date_used=str(d["dt"].max()),
        n_bars_used=int(len(d)),
        n_bars_before_cutoff=n_before,
        n_bars_excluded_by_cutoff=int(n_before - len(d)),
        loader_version=LOADER_VERSION,
        timeframe=tf,
    )
    return d, meta


def vol_regime(d: pd.DataFrame, col: str = "atr14", window: int = 200) -> pd.Series:
    """Rolling percentile rank of ATR -> low/mid/high tercile, using only trailing (lookahead-safe) data."""
    pr = d[col].rolling(window).apply(lambda x: (x[:-1] < x[-1]).mean() if len(x) > 1 else np.nan, raw=True)
    return pd.cut(pr, bins=[-0.01, 1 / 3, 2 / 3, 1.01], labels=["low", "mid", "high"])


def bootstrap_mean_ci(x: np.ndarray, n_boot: int = 5000, seed: int = 7) -> tuple:
    if len(x) == 0:
        return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    boots = x[idx].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return (float(x.mean()), float(lo), float(hi))


def summarize(x: np.ndarray) -> dict:
    x = np.asarray(x, dtype=float)
    if len(x) == 0:
        return dict(n=0)
    mean, lo, hi = bootstrap_mean_ci(x)
    return dict(n=int(len(x)), mean=mean, ci95=[lo, hi], median=float(np.median(x)),
                std=float(np.std(x)), ci_excludes_zero=bool(lo > 0 or hi < 0))

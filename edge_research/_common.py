"""Flow A (Alpha Discovery Laboratory) shared utilities.

Deliberately independent of `code/` and `ai_trader/` (per the two-flow separation in
PROJECT_STATE_v2.md SS1.1 / NEXT_SESSION.md SS B) -- reads only the raw market CSVs in
`data/market/`, never imports the frozen Research Lab engine or any ai_trader package.
Any formula reused here (ATR-14, UTC-hour session buckets) is reproduced independently
and disclosed in each edge's own research log, not imported as a dependency.
"""
import os
import numpy as np
import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_ROOT, "data", "market")


def load(tf: str) -> pd.DataFrame:
    """tf in {'M15','H1','H4','D1'}. Returns df sorted by time, deduped, UTC dt column, ATR-14, session tag."""
    path = os.path.join(DATA_DIR, f"OANDA_XAUUSD_{tf}.csv")
    d = pd.read_csv(path).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    d["dt"] = pd.to_datetime(d["time"], unit="s", utc=True)
    h, l, c = d["high"], d["low"], d["close"]
    tr = np.maximum(h - l, np.maximum((h - c.shift()).abs(), (l - c.shift()).abs()))
    d["atr14"] = tr.rolling(14).mean()
    hh = d["dt"].dt.hour
    d["session"] = np.select([hh < 8, hh < 13, hh < 21], ["asia", "london", "ny"], default="late")
    d["dow"] = d["dt"].dt.day_name()
    return d


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

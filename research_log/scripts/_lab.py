"""Shared analysis helpers for the autonomous research batch. Holdout-safe by construction:
all data comes through the sanctioned fail-closed loader (cutoff 2025-10-23). Descriptive only.
"""
import sys
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation")
import numpy as np
import pandas as pd
from edge_research import _common

CUTOFF = _common.RESEARCH_HOLDOUT_CUTOFF_UTC
SPLIT = _common.PRE_HOLDOUT_SPLIT_ID


def load(tf):
    df, meta = _common.load(tf, data_split_id=SPLIT, cutoff=CUTOFF)
    df = df.reset_index(drop=True)
    assert df["dt"].max() < pd.Timestamp(CUTOFF), "holdout breach"
    return df, meta


def add_prior_day(df):
    df = df.copy()
    df["day"] = df["dt"].dt.date
    daily = df.groupby("day").agg(d_high=("high", "max"), d_low=("low", "min"),
                                  d_open=("open", "first"), d_close=("close", "last")).reset_index()
    daily["pdh"] = daily["d_high"].shift(1)
    daily["pdl"] = daily["d_low"].shift(1)
    daily["pdc"] = daily["d_close"].shift(1)
    m = daily.set_index("day")
    for c in ["pdh", "pdl", "pdc"]:
        df[c] = df["day"].map(m[c])
    return df, daily


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def drift(df, K):
    c = df["close"].values
    return float(np.mean(c[K:] - c[:-K]))


def fwd(df, i, K):
    j = i + K
    n = len(df)
    return None if j >= n else float(df["close"].iat[j] - df["close"].iat[i])


def summ(a):
    a = np.asarray([x for x in a if x is not None and x == x], float)
    if len(a) == 0:
        return dict(n=0, mean=float("nan"), med=float("nan"), pgt0=float("nan"), std=float("nan"))
    return dict(n=len(a), mean=float(a.mean()), med=float(np.median(a)),
                pgt0=float((a > 0).mean()), std=float(a.std()))


def boot_ci(a, n_boot=2000, seed=7):
    a = np.asarray([x for x in a if x is not None and x == x], float)
    if len(a) < 5:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    means = [a[rng.integers(0, len(a), len(a))].mean() for _ in range(n_boot)]
    return (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))


def line(label, s, extra=""):
    return (f"{label:26s} n={s['n']:4d} mean={s['mean']:+8.3f} med={s['med']:+8.3f} "
            f"P>0={s['pgt0']:.2f} {extra}")

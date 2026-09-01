"""MULTI_SESSION_LONG_HORIZON_ALPHA_SCOUT_V1 -- engine.
Native governed M15, holdout-truncated. Fixed-UTC-hour daily anchors, non-overlapping,
month-cluster-robust inference. Budget hard-enforced at 60 scored hypotheses.
"""
from __future__ import annotations
import sys, os, math, json, hashlib
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

MK = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market\OANDA_XAUUSD_M15.csv"
CUT = pd.Timestamp("2025-10-23T09:15:00+00:00")
DEV_END_TS = pd.Timestamp("2019-01-01T00:00:00+00:00").timestamp()
PIP = 0.10
BUDGET = 60

DF = pd.read_csv(MK).drop_duplicates("time").sort_values("time").reset_index(drop=True)
DF["t"] = pd.to_datetime(DF["time"], unit="s", utc=True)
DF = DF[DF.t < CUT].reset_index(drop=True)
TS = DF["time"].to_numpy(np.int64)                 # unix seconds, straight from the file
O = DF.open.to_numpy(float); H = DF.high.to_numpy(float)
L = DF.low.to_numpy(float); C = DF.close.to_numpy(float); N = len(DF)
MON = (DF.t.dt.year * 12 + DF.t.dt.month).to_numpy()
YEAR = DF.t.dt.year.to_numpy()
hr = DF.t.dt.hour.to_numpy(); mi = DF.t.dt.minute.to_numpy()
DAY = TS // 86400                                   # UTC calendar day
DATASET_HASH = hashlib.sha256(open(MK, "rb").read()).hexdigest()

# ---------------------------------------------------------------- causal features
def rmax(a, k): return pd.Series(a).rolling(k).max().to_numpy()
def rmin(a, k): return pd.Series(a).rolling(k).min().to_numpy()
def rsum(a, k): return pd.Series(a).rolling(k).sum().to_numpy()
def rstd(a, k): return pd.Series(a).rolling(k).std().to_numpy()
def lagged(a, k): return np.concatenate([np.full(k, np.nan), a[:-k]])

K24, K48, K120, K480 = 96, 192, 480, 1920           # 24h, 48h, 5d, 20d in M15 bars
dC = np.concatenate([[np.nan], np.diff(C)])
ret24 = C - lagged(C, K24)
ret48 = C - lagged(C, K48)
gross24 = rsum(np.abs(dC), K24)
eff24 = np.abs(ret24) / np.where(gross24 > 0, gross24, np.nan)
hi48, lo48 = rmax(H, K48), rmin(L, K48); rng48 = hi48 - lo48
hi24, lo24 = rmax(H, K24), rmin(L, K24); rng24 = hi24 - lo24
clpos48 = (C - lo48) / np.where(rng48 > 0, rng48, np.nan)
prevC = np.concatenate([[np.nan], C[:-1]])
tr = np.maximum(H - L, np.maximum(np.abs(H - prevC), np.abs(L - prevC)))
atr20d = rsum(tr, K480) / 20.0
vol5, vol20 = rstd(dC, K120), rstd(dC, K480)
comp48 = rng48 / np.where(atr20d > 0, atr20d, np.nan)
volratio = vol5 / np.where(vol20 > 0, vol20, np.nan)
made_hi = rmax(H, K24) >= hi48 - 1e-9
made_lo = rmin(L, K24) <= lo48 + 1e-9
fail_up = made_hi & (clpos48 < 0.5)
fail_dn = made_lo & (clpos48 > 0.5)

# ---- daily bars on the UTC day boundary (same boundary as the 00:00 anchor) ----
g = pd.DataFrame({"d": DAY, "h": H, "l": L, "c": C, "o": O})
gg = g.groupby("d")
D = pd.DataFrame({"hi": gg.h.max(), "lo": gg.l.min(), "cl": gg.c.last(), "op": gg.o.first()})
D["rng"] = D.hi - D.lo
D["net"] = D.cl - D.op
D["clpos"] = (D.cl - D.lo) / D.rng.replace(0, np.nan)
D["persist"] = D.net.abs() / D.rng.replace(0, np.nan)
D["rng_pct"] = D.rng.rolling(20).apply(lambda x: float((x[:-1] < x[-1]).mean()), raw=True)
D["atr5"] = D.rng.rolling(5).mean(); D["atr20"] = D.rng.rolling(20).mean()
D["contract"] = D.atr5 / D.atr20
D["dirsign"] = np.sign(D.net)
D["run"] = D.groupby((D.dirsign != D.dirsign.shift()).cumsum()).cumcount() + 1
PREV = DAY - 1
def dfe(col):
    m = D[col].to_dict()
    return np.array([m.get(int(p), np.nan) for p in PREV], float)
d_rngpct, d_clpos, d_persist = dfe("rng_pct"), dfe("clpos"), dfe("persist")
d_run, d_dirsign, d_contract = dfe("run"), dfe("dirsign"), dfe("contract")

# ---- Asia phase 00:00-08:00 UTC, complete at the 08:00 anchor (BRANCH D) ----
asia = hr < 8
adf = pd.DataFrame({"d": DAY, "h": np.where(asia, H, np.nan), "l": np.where(asia, L, np.nan),
                    "c": np.where(asia, C, np.nan), "o": np.where(asia, O, np.nan)})
ag = adf.groupby("d")
A = pd.DataFrame({"hi": ag.h.max(), "lo": ag.l.min(), "cl": ag.c.last(), "op": ag.o.first()})
A["rng"] = A.hi - A.lo; A["net"] = A.cl - A.op
A["clpos"] = (A.cl - A.lo) / A.rng.replace(0, np.nan)
def afe(col):
    m = A[col].to_dict()
    return np.array([m.get(int(p), np.nan) for p in DAY], float)
a_rng, a_net, a_clpos = afe("rng"), afe("net"), afe("clpos")
a_comp = a_rng / np.where(atr20d > 0, atr20d, np.nan)

# ---------------------------------------------------------------- anchors
def anchor_index(hour):
    return np.where((hr == hour) & (mi == 0))[0]

def episodes(anchors, hbars, stride_days=1):
    keep = anchors[::stride_days]
    keep = keep[keep + hbars < N]
    keep = keep[(TS[keep + hbars] - TS[keep]) <= 1.25 * hbars * 900]
    return keep

# ---------------------------------------------------------------- targets
_fc = {}
def fwd(hbars):
    if hbars not in _fc:
        fh = np.full(N, np.nan); fl = np.full(N, np.nan); fc = np.full(N, np.nan)
        fh[:N - hbars] = pd.Series(H).rolling(hbars).max().to_numpy()[hbars:]
        fl[:N - hbars] = pd.Series(L).rolling(hbars).min().to_numpy()[hbars:]
        fc[:N - hbars] = C[hbars:]
        _fc[hbars] = (fh, fl, fc)
    return _fc[hbars]

def targets(idx, hbars):
    fh, fl, fc = fwd(hbars)
    c0 = C[idx]
    ret = (fc[idx] - c0) / PIP
    mfe = (fh[idx] - c0) / PIP
    mae = (c0 - fl[idx]) / PIP
    return dict(ret=ret, absret=np.abs(ret), mfe=mfe, mae=mae,
                exc=np.maximum(mfe, mae))

_tt = {}
def time_to_100(idx, hbars):
    if hbars not in _tt:
        hit = np.full(N, np.inf)
        U = C + 100 * PIP; Dn = C - 100 * PIP
        for j in range(1, hbars + 1):
            hj = np.concatenate([H[j:], np.full(j, np.nan)])
            lj = np.concatenate([L[j:], np.full(j, np.nan)])
            hit = np.where(((hj >= U) | (lj <= Dn)) & np.isinf(hit), j, hit)
        _tt[hbars] = np.where(np.isinf(hit), hbars, hit) * 0.25      # hours, censored -> cap
    return _tt[hbars][idx]

# ---------------------------------------------------------------- estimator
def crve(y, x, cl):
    """OLS y ~ 1 + x with CR1 month-cluster-robust SE on the slope."""
    ok = np.isfinite(y) & np.isfinite(x)
    y, x, cl = y[ok], x[ok].astype(float), cl[ok]
    n = len(y)
    if n < 60 or x.sum() < 30 or (1 - x).sum() < 30:
        return None
    X = np.column_stack([np.ones(n), x])
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ (X.T @ y)
    u = y - X @ b
    meat = np.zeros((2, 2))
    uni, inv = np.unique(cl, return_inverse=True)
    G = len(uni)
    for gI in range(G):
        m = inv == gI
        Xg = X[m]; ug = u[m]
        s = Xg.T @ ug
        meat += np.outer(s, s)
    k = 2
    adj = (G / max(G - 1, 1)) * ((n - 1) / max(n - k, 1))
    V = XtXi @ meat @ XtXi * adj
    se = math.sqrt(max(V[1, 1], 1e-18))
    cond = float(y[x == 1].mean()); base = float(y[x == 0].mean())
    return dict(n=int(n), n_cond=int(x.sum()), clusters=int(G), cond=cond, base=base,
                lift=float(b[1]), se=se, z=float(b[1] / se))

# ---------------------------------------------------------------- budget guard
SCORED = []
def score(hid, branch, desc, idx, mask, y, target_class, note=""):
    if len(SCORED) >= BUDGET:
        raise RuntimeError(f"BUDGET BREACH: hypothesis {len(SCORED)+1} exceeds declared {BUDGET}")
    dev = TS[idx] < DEV_END_TS
    r = crve(y[dev], mask[dev], MON[idx][dev])
    rec = dict(id=hid, branch=branch, desc=desc, target_class=target_class, note=note,
               dev_anchors=int(dev.sum()), dev=r)
    SCORED.append(rec)
    return rec

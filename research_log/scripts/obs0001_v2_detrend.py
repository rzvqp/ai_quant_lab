"""OBS-0001 v2 -- self-falsification: is the K=12 sweep/break separation a real effect or a
trend artifact? Split up/down interactions, work in RAW price change, and DETREND by the
unconditional K-bar drift. Also break the strongest cell down by session.

If the SMC 'sweep' claim is real and NOT just trend:
  up-REJECT excess < 0, up-HOLD excess > 0, down-REJECT excess > 0, down-HOLD excess < 0.
"""
import sys
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation")
import numpy as np, pandas as pd
from edge_research import _common

df, meta = _common.load("H1", data_split_id=_common.PRE_HOLDOUT_SPLIT_ID,
                        cutoff=_common.RESEARCH_HOLDOUT_CUTOFF_UTC)
df = df.reset_index(drop=True)
n = len(df)
df["day"] = df["dt"].dt.date
daily = df.groupby("day").agg(d_high=("high", "max"), d_low=("low", "min")).reset_index()
daily["pdh"] = daily["d_high"].shift(1); daily["pdl"] = daily["d_low"].shift(1)
pdh = dict(zip(daily["day"], daily["pdh"])); pdl = dict(zip(daily["day"], daily["pdl"]))

recs = []  # (side, cls, i, session)
for day, g in df.groupby("day"):
    ph, pl = pdh.get(day), pdl.get(day)
    if ph is None or pl is None or np.isnan(ph) or np.isnan(pl):
        continue
    idx = g.index.tolist()
    up = next((i for i in idx if df.at[i, "high"] > ph), None)
    if up is not None:
        recs.append(("up", "reject" if df.at[up, "close"] < ph else "hold", up, df.at[up, "session"]))
    dn = next((i for i in idx if df.at[i, "low"] < pl), None)
    if dn is not None:
        recs.append(("down", "reject" if df.at[dn, "close"] > pl else "hold", dn, df.at[dn, "session"]))

def raw(i, K):
    j = i + K
    return None if j >= n else df.at[j, "close"] - df.at[i, "close"]

for K in (6, 12):
    drift = np.mean([df.at[i+K, "close"] - df.at[i, "close"] for i in range(n-K)])
    print(f"\n================  K={K}  (unconditional drift = {drift:+.3f})  ================")
    print(f"{'group':16s} {'n':>4s} {'rawΔmean':>9s} {'excess':>8s} {'P(Δ>0)':>7s}")
    for side in ("up", "down"):
        for cls in ("reject", "hold"):
            vals = [raw(i, K) for (s, c, i, ss) in recs if s == side and c == cls]
            a = np.array([v for v in vals if v is not None], float)
            if len(a):
                print(f"{side+'-'+cls:16s} {len(a):4d} {a.mean():+9.3f} {a.mean()-drift:+8.3f} {(a>0).mean():7.2f}")
    # session breakdown of up-hold and up-reject (the trend-aligned cell)
    print("  -- by session (excess Δ) --")
    for side, cls in (("up", "reject"), ("up", "hold"), ("down", "reject"), ("down", "hold")):
        for ss in ("asia", "london", "ny", "late"):
            vals = [raw(i, K) for (s, c, i, s2) in recs if s == side and c == cls and s2 == ss]
            a = np.array([v for v in vals if v is not None], float)
            if len(a) >= 15:
                print(f"     {side}-{cls:6s} {ss:7s} n={len(a):3d} excess={a.mean()-drift:+7.3f} P(Δ>0)={(a>0).mean():.2f}")

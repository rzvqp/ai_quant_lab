"""cur_cr7.py — FRONTIER CR-7 (current-regime, info-first, DURATION / HAZARD / time-since-onset representation).

Distinct from every prior frontier (all conditioned on a price EVENT). Here the conditioning variable is EPISODE AGE:
how long the current-like regime has persisted since onset. Evidence motivation: a high-vol correction is internally
non-stationary — fresh legs after onset may carry reliable down-continuation, while a maturing/exhausting correction
turns choppy or reverses. If down-first ordering (P(downFirst)) is concentrated in the FIRST days after current-like
turns ON, that is a causal, real-time-observable, NON-tail temporal condition -> a time-answer to WHEN the down-payoff
is capturable.

Episode = maximal run of current-like bars, bridging gaps <= GAP_DAYS (tolerate brief signature dips). Age = days since
episode onset. INFO-FIRST (no P&L): per age bucket, P(downFirst) + dn-up, partitioned DISC/CONF/OOS. Data thru 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD
from cur_screen import like_at
from cur_cr2 import fwd
GAP_DAYS=2.0

def episode_age_days(t, cl):
    n=len(t); age=np.full(n,np.nan); onset=None; last=None
    for i in range(n):
        if not cl[i]: continue
        if onset is None or (t[i]-last)/86400.0 > GAP_DAYS:
            onset=t[i]           # new episode onset
        age[i]=(t[i]-onset)/86400.0
        last=t[i]
    return age

def main():
    m=CD.load_m15(); up,dn,af=fwd(m)
    t=m["time"].to_numpy().astype("float64"); cl=like_at(t); yr=m["dt"].dt.year.to_numpy()
    age=episode_age_days(t,cl); ok=np.isfinite(up)&np.isfinite(dn)&np.isfinite(age)
    print(f"FRONTIER CR-7: current-like EPISODE AGE (days since onset, gap<= {GAP_DAYS}d bridged) -> forward ordering.")
    def row(msk):
        n=int(msk.sum())
        if n<200: return f"n={n}(thin)", None
        afr=af[msk]; pdf=float((afr[afr!=0]==-1).mean()) if (afr!=0).sum() else float('nan')
        return f"n={n:6d} P(downFirst)={pdf:.3f} dn-up={np.median(dn[msk])-np.median(up[msk]):+.2f}", pdf
    s,_=row(cl&ok); print("  [current-like ALL ages]:", s)
    bins=[(0,1),(1,3),(3,7),(7,21),(21,60),(60,1e9)]
    for a0,a1 in bins:
        am=(age>=a0)&(age<a1)&cl&ok
        sall,pall=row(am)
        line=f"  age {a0:>2.0f}-{a1 if a1<1e8 else 'inf':>3}d: {sall}"
        parts=[]
        for plab,ym in [("D",yr<=2021),("C",(yr>=2022)&(yr<=2024)),("O",yr>=2025)]:
            ss,pp=row(am&ym); parts.append(f"{plab}={pp:.2f}" if pp is not None else f"{plab}=thin")
        print(line+"  | "+" ".join(parts))
    print("\n  Robust-ordering age windows (P(downFirst)>0.52 overall AND >0.50 in every partition) flagged above by eye.")

if __name__=="__main__":
    main()

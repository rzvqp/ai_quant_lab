"""cur_info.py — CURRENT-REGIME information-first structural-asymmetry test (§8/§9; NOT mining). On the frozen
CURRENT_LIKE_POPULATION_V1, is there a robust DIRECTIONAL asymmetry (does price reach -1.5ATR before +1.5ATR more
often = down-bias), or is the current regime genuinely SYMMETRIC/choppy? Decisive about whether any directional
specialist can exist. ATR-relative first-passage order, partitioned DISC/CONF/OOS + diagnostic non-current-like.
Data through 2026-07-27 (freshest authorized; disclosed stale ~4wk).
"""
import numpy as np, pandas as pd
import cur_data as CD
from cur_screen import like_at
H=96; K=1.5

def fp_order(m):
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    o=np.zeros(n,np.int8)
    for i in range(n-1):
        a=atr[i]
        if not np.isfinite(a) or a<=0: continue
        up=c[i]+K*a; dn=c[i]-K*a; end=min(i+1+H,n); r=0
        for j in range(i+1,end):
            if l[j]<=dn: r=-1; break
            if h[j]>=up: r=1; break
        o[i]=r
    return o

def main():
    print(f"Current-regime INFO: P(down {K}ATR before up {K}ATR) = down-bias. current-like partitioned. baseline 0.5 = symmetric.")
    m=CD.load_m15(); o=fp_order(m); t=m["time"].to_numpy()
    cl=like_at(t); yr=m["dt"].dt.year.to_numpy(); valid=(o!=0)
    def pdown(msk):
        oo=o[msk]; return (len(oo), float((oo==-1).mean()) if len(oo) else float('nan'))
    parts={"CUR-LIKE(all)":cl&valid,"  DISC<=2021":cl&valid&(yr<=2021),"  CONF 22-24":cl&valid&(yr>=2022)&(yr<=2024),
           "  OOS 25-26":cl&valid&(yr>=2025),"DIAG non-cur":(~cl)&valid}
    for k,msk in parts.items():
        n,p=pdown(msk); print(f"  {k:16s}: n={n:6d} P(down-first)={p:.3f}")

if __name__=="__main__":
    main()

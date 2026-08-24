"""frontier_v.py — FRONTIER V: is there a cross-era-stable directional bias at a TRADEABLE move-scale (+/-2 ATR)?
R32 showed cross-era-stable directional signals exist but are sub-cost (micro/drift). The tradeable question: at the
2-ATR first-passage scale (a real move, ~cost-clearing), is P(+2ATR before -2ATR) cross-era-stable materially >0.5
(a large LONG bias) - unconditional and NY-conditioned? Distinct from R29 (open-to-close drift) and R32 (1-bar).
Info-first, causal, cross-era. SUCCESS = cross-era-stable material >0.53 -> convert to a strategy + S5-independence.
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _hr_day
H=96; KATR=2.0

def fp2(fr):
    h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy(); n=len(fr)
    o=np.zeros(n,np.int8)
    for i in range(n-1):
        a=atr[i]
        if not np.isfinite(a) or a<=0: continue
        up=c[i]+KATR*a; dn=c[i]-KATR*a; end=min(i+1+H,n); r=0
        for j in range(i+1,end):
            if h[j]>=up: r=1; break
            if l[j]<=dn: r=-1; break
        o[i]=r
    return o

def main():
    print(f"Frontier V: P(+{KATR}ATR before -{KATR}ATR) over {H} bars, per era. Tradeable-scale directional bias? baseline~0.5.")
    eras=bs.build_eras(); frames={}
    for tag,fr,m in eras: frames.setdefault(id(fr),fr)
    FP={k:fp2(v) for k,v in frames.items()}
    print("\n[unconditional]")
    for tag,fr,mask in eras:
        o=FP[id(fr)]; sel=mask&(o!=0); n=int(sel.sum())
        p=float((o[sel]==1).mean()); print(f"  {tag}: P(up{KATR}ATR first)={p:.3f} (n{n})")
    print("\n[NY session 13-21 only]")
    for tag,fr,mask in eras:
        o=FP[id(fr)]; hr,_,_=_hr_day(fr); sel=mask&(o!=0)&(hr>=13)&(hr<21); n=int(sel.sum())
        if n<200: print(f"  {tag}: thin"); continue
        p=float((o[sel]==1).mean()); print(f"  {tag}: P(up{KATR}ATR first)={p:.3f} (n{n})")

if __name__=="__main__":
    main()

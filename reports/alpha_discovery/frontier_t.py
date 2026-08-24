"""frontier_t.py — FRONTIER T: DURATION-based hazard (time-since-swing-origin), distinct from S (distance). Does the
continuation P(+1ATR before -1ATR) of an active-up move depend on how LONG it has persisted (bars since the recent
20-bar low), cross-era? Duration axis vs S's distance axis. Info-first, causal, cross-era. Preregistered.
"""
import numpy as np, pandas as pd, bscreen as bs
from frontier_s import fp_order
BUCK=[(0,3),(4,7),(8,12),(13,19)]

def main():
    print("Frontier T DURATION hazard: continuation P(+1ATR before -1ATR) vs bars-since-20bar-low, active-up, cross-era. baseline~0.5.")
    eras=bs.build_eras(); frames={}
    for tag,fr,m in eras: frames.setdefault(id(fr),fr)
    ORD={k:fp_order(v) for k,v in frames.items()}
    feat={}
    for k,fr in frames.items():
        l=fr["low"]; h=fr["high"]; c=fr["close"].to_numpy()
        dur=l.rolling(20).apply(lambda x: len(x)-1-int(np.argmin(x)),raw=True).to_numpy()  # bars since 20-bar low
        olow=l.rolling(20).min().to_numpy(); ohigh=h.rolling(20).max().to_numpy()
        active=((c-olow)/np.maximum(ohigh-olow,1e-9))>=0.75
        feat[k]=(dur,active)
    print(f"  {'dur(bars)':>9} | " + "  ".join(f"{t:>13}" for t,_,_ in eras) + "  | cross-era")
    for blo,bhi in BUCK:
        cells=[]; ps=[]
        for tag,fr,mask in eras:
            dur,active=feat[id(fr)]; o=ORD[id(fr)]
            sel=mask&active&(dur>=blo)&(dur<=bhi)&(o!=0)&np.isfinite(dur)
            n=int(sel.sum())
            if n<200: cells.append(f"n{n}(thin)"); ps.append(None); continue
            p=float((o[sel]==1).mean()); cells.append(f"{p:.3f}(n{n})"); ps.append(p)
        v=[p for p in ps if p is not None]
        st="STABLE>0.5" if (len(v)>=3 and all(p>=0.53 for p in v)) else ("STABLE<0.5" if (len(v)>=3 and all(p<=0.47 for p in v)) else "-")
        print(f"  {str(blo)+'-'+str(bhi):>9} | " + "  ".join(f"{x:>13}" for x in cells) + f"  | {st}")

if __name__=="__main__":
    main()

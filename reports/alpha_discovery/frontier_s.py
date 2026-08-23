"""frontier_s.py — FRONTIER S: HAZARD/SURVIVAL structure of a directional move. Continuation probability as a
FUNCTION of travel-distance X (ATR from the recent swing origin) — a survival representation, distinct from all fixed-
event frontiers. Question: does direction become OBSERVABLE through the move itself (a cross-era-stable X-region where
continuation P >> 0.5 = trend-acceptance / point-of-no-return)? ATR-relative first-passage order (reach +1 ATR before
-1 ATR). Causal. Cross-era b0/b1/DEV/CAL. Info-first (no P&L). Preregistered fail/success in the mandate.
"""
import numpy as np, pandas as pd, bscreen as bs
H=24; W=20; KATR=1.0
BUCKETS=[(0,1),(1,2),(2,3),(3,5),(5,99)]

def fp_order(fr):
    h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy(); n=len(fr)
    order=np.zeros(n,np.int8)
    for i in range(n-1):
        a=atr[i]
        if not np.isfinite(a) or a<=0: continue
        up=c[i]+KATR*a; dn=c[i]-KATR*a; o=0; end=min(i+1+H,n)
        for j in range(i+1,end):
            if h[j]>=up: o=1; break
            if l[j]<=dn: o=-1; break
        order[i]=o
    return order

def main():
    print(f"Frontier S HAZARD/SURVIVAL: continuation P(+1ATR before -1ATR) vs travel-distance X (ATR from {W}-bar low), for ACTIVE-UP moves, cross-era. baseline~0.5.")
    eras=bs.build_eras(); frames={}
    for tag,fr,m in eras: frames.setdefault(id(fr),fr)
    ORD={k:fp_order(v) for k,v in frames.items()}
    print(f"  {'X(ATR)':>7} | " + "  ".join(f"{t:>13}" for t,_,_ in eras) + "  | cross-era")
    # precompute X_up + active per frame
    feat={}
    for k,fr in frames.items():
        c=fr["close"].to_numpy(); l=fr["low"]; h=fr["high"]; atr=fr["atr"].to_numpy()
        olow=l.rolling(W).min().to_numpy(); ohigh=h.rolling(W).max().to_numpy()
        X=(c-olow)/atr; rngpos=(c-olow)/np.maximum(ohigh-olow,1e-9); active=rngpos>=0.75
        feat[k]=(X,active)
    for blo,bhi in BUCKETS:
        cells=[]; ps=[]
        for tag,fr,mask in eras:
            X,active=feat[id(fr)]; o=ORD[id(fr)]
            sel=mask&active&(X>=blo)&(X<bhi)&(o!=0)&np.isfinite(X)
            n=int(sel.sum())
            if n<200: cells.append(f"n{n}(thin)"); ps.append(None); continue
            pcont=float((o[sel]==1).mean())  # P(+1ATR before -1ATR) = continuation up
            cells.append(f"{pcont:.3f}(n{n})"); ps.append(pcont)
        valid=[p for p in ps if p is not None]
        stable="STABLE>0.5" if (len(valid)>=3 and all(p>=0.53 for p in valid)) else ("STABLE<0.5" if (len(valid)>=3 and all(p<=0.47 for p in valid)) else "-")
        print(f"  {str(blo)+'-'+str(bhi):>7} | " + "  ".join(f"{x:>13}" for x in cells) + f"  | {stable}")

if __name__=="__main__":
    main()

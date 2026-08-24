"""cur_cr2.py — FRONTIER CR-2 (current-regime, information-first): does a confirmed LOWER-HIGH (multi-stage swing
structure = bounce exhaustion) concentrate the down-payoff WITHOUT tail-dependence? Research question (CEO): when is
the downside payoff asymmetry causally capturable? A lower-high means the bounce high is IN -> forward adverse (further
up) should be limited (path-surviving) and forward down-payoff robust. INFO-FIRST: at confirmed lower-high bars in
current-like, median forward DOWN vs UP excursion + adverse-first + P(down first), partitioned, vs current-like baseline.
No P&L/RR. Swing high = fractal max over +/-k; confirmed at i+k (causal). Data through 2026-07-27 (CEO: sufficient).
"""
import numpy as np, pandas as pd
import cur_data as CD
from cur_screen import like_at
K=6; H=96; KA=1.5

def lower_high_events(m):
    h=m["high"].to_numpy(); n=len(m)
    # confirmed swing high at i: h[i]==max(h[i-K..i+K]); known at i+K
    roll=pd.Series(h).rolling(2*K+1,center=True).max().to_numpy()
    isswing=(h==roll)&np.isfinite(roll)
    ev=np.zeros(n,bool); lastv=None
    sw=np.where(isswing)[0]
    for i in sw:
        e=i+K
        if e>=n: continue
        if lastv is not None and h[i]<lastv: ev[e]=True   # lower-high, event at confirmation bar
        lastv=h[i]
    return ev

def fwd(m):
    c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    fmax=pd.Series(m["high"].to_numpy()).rolling(H).max().shift(-H).to_numpy()
    fmin=pd.Series(m["low"].to_numpy()).rolling(H).min().shift(-H).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr
    # adverse-first for a SHORT = up 1.5ATR before down 1.5ATR
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); af=np.zeros(n,np.int8)
    for i in range(n-1):
        a=atr[i]
        if not np.isfinite(a) or a<=0: continue
        u=c[i]+KA*a; d=c[i]-KA*a; end=min(i+1+H,n); r=0
        for j in range(i+1,end):
            if h[j]>=u: r=1; break   # adverse (up) first for a short
            if l[j]<=d: r=-1; break  # favorable (down) first
        af[i]=r
    return up,dn,af

def main():
    m=CD.load_m15(); ev=lower_high_events(m); up,dn,af=fwd(m)
    t=m["time"].to_numpy(); cl=like_at(t); yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)
    print("FRONTIER CR-2: confirmed LOWER-HIGH in current-like -> forward path (info-first). down>up + low adverse-first = concentrated.")
    def row(msk):
        n=int(msk.sum())
        if n<40: return f"n={n}(thin)"
        afr=af[msk]; pdownfirst=float((afr[afr!=0]==-1).mean()) if (afr!=0).sum() else float('nan')
        return f"n={n:5d} up={np.median(up[msk]):.2f} dn={np.median(dn[msk]):.2f} dn-up={np.median(dn[msk])-np.median(up[msk]):+.2f} P(downFirst)={pdownfirst:.3f}"
    print("  [current-like BASELINE]     :", row(cl&ok))
    print("  [LOWER-HIGH x current-like] :", row(cl&ok&ev))
    for lab,ymask in [("DISC<=2021",yr<=2021),("CONF 22-24",(yr>=2022)&(yr<=2024)),("OOS 25-26",yr>=2025)]:
        print(f"    LH {lab:10s}:", row(cl&ok&ev&ymask))
    print("  [LOWER-HIGH x NON-cur DIAG] :", row((~cl)&ok&ev))

if __name__=="__main__":
    main()

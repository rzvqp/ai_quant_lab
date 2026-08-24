"""cur_cr5.py — FRONTIER CR-5 (current-regime, info-first, level-geometry / acceptance-failure representation).

DISTINCT CAUSAL IDENTITY (not short-breakdown, which enters ON the break): broken-support RETEST-FAILURE = level-flip
acceptance below. Motivated directly by accumulated evidence "large adverse bounces precede down continuation" + "failure
of tight stops" + "wide adverse-first". Every rejected short entered BEFORE the bounce -> the bounce was adverse and the
surviving edge lived in the crash tail. Here we enter AFTER the bounce fails: price breaks below a confirmed swing-low
support, RETESTS it from below (high>=L), then is REJECTED (a bar closes back below L). Hypothesis: because the adverse
bounce has already resolved, the forward down-path is more reliably concentrated with LOWER adverse-first (down 1.5ATR
before up 1.5ATR) -> a candidate answer to WHEN the down-payoff is capturable without tail-dependence.

INFO-FIRST (no P&L/RR): at rejection bars in current-like, forward down vs up excursion + adverse-first + P(down first),
partitioned DISC/CONF/OOS vs current-like baseline, + tail-spread of the down excursion (is it broad or tail-only?).
Causal: swing low confirmed at i+K; break/retest/reject all use only past+current bars. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD
from cur_screen import like_at
from cur_cr2 import fwd
K=6; WBREAK=48; WRETEST=48  # swing half-width; max bars break->retest and retest->reject

def reject_events(m):
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); n=len(m)
    roll=pd.Series(l).rolling(2*K+1,center=True).min().to_numpy()
    isswing=(l==roll)&np.isfinite(roll)
    swidx=np.where(isswing)[0]
    # confirmed level available from bar i+K onward
    lv=np.full(n,np.nan);
    for i in swidx:
        e=i+K
        if e<n: lv[e]=l[i]
    # forward-fill the most recent confirmed support level
    L=pd.Series(lv).ffill().to_numpy()
    ev=np.zeros(n,bool)
    st=0; Lb=np.nan; tb=-1; retested=False
    # states: 0=waiting for break, 1=broke waiting for retest, 2=retested waiting for reject
    for t in range(n):
        Lt=L[t]
        if not np.isfinite(Lt): continue
        if st==0:
            if c[t]<Lt:  # closed below current support -> break
                st=1; Lb=Lt; tb=t; retested=False
        elif st==1:
            if t-tb>WBREAK: st=0; continue
            if h[t]>=Lb:  # retested the broken level from below
                st=2; tr=t
        elif st==2:
            if t-tr>WRETEST: st=0; continue
            if c[t]<Lb:  # rejected: closed back below -> acceptance below = event
                ev[t]=True; st=0
    return ev

def main():
    m=CD.load_m15(); ev=reject_events(m); up,dn,af=fwd(m)
    t=m["time"].to_numpy(); cl=like_at(t); yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)
    print("FRONTIER CR-5: broken-support RETEST-FAILURE (acceptance below) in current-like -> forward path (info-first).")
    print("  down>up + LOW adverse-first (P(downFirst) high) = the bounce already resolved -> less tail-dependent.")
    def row(msk):
        n=int(msk.sum())
        if n<40: return f"n={n}(thin)"
        afr=af[msk]; pdf=float((afr[afr!=0]==-1).mean()) if (afr!=0).sum() else float('nan')
        dnv=dn[msk]; frac1=float((dnv>=1.0).mean())  # broad-capture proxy: fraction reaching 1 ATR down
        return f"n={n:5d} up={np.median(up[msk]):.2f} dn={np.median(dnv):.2f} dn-up={np.median(dnv)-np.median(up[msk]):+.2f} P(downFirst)={pdf:.3f} frac>=1ATRdn={frac1:.2f}"
    print("  [current-like BASELINE]         :", row(cl&ok))
    print("  [RETEST-FAIL x current-like]    :", row(cl&ok&ev))
    for lab,ym in [("DISC<=2021",yr<=2021),("CONF 22-24",(yr>=2022)&(yr<=2024)),("OOS 25-26",yr>=2025)]:
        print(f"    RF {lab:10s}:", row(cl&ok&ev&ym))
    print("  [RETEST-FAIL x NON-cur DIAG]    :", row((~cl)&ok&ev))

if __name__=="__main__":
    main()

"""cur_cr6.py — FRONTIER CR-6 (current-regime, info-first, SESSION-INHERITANCE / time-of-day representation).

Targets the crux isolated by CR-5: the downside payoff is broadly available (88% reach 1 ATR down) but tail-dependent
because the ADVERSE BOUNCE COMES FIRST (P(downFirst) ~ 0.51, stubbornly ~coinflip). A stop is knocked out on the bounce
before the down arrives; only stop-survivors (the tail) pay. So the down-payoff is capturable-without-tail-dependence
ONLY IF some causal condition raises P(downFirst) meaningfully above 0.5.

HYPOTHESIS (distinct representation, session inheritance): in current-like, the down-FIRST ordering is not uniform over
the trading day. Impulsive down-legs concentrate in macro sessions (London/NY) while other hours are bounce-prone chop.
If one intraday window shows P(downFirst) robustly > 0.5 across current-like partitions, conditioning entry on that window
makes down-capture less tail-dependent BY AVOIDING the adverse-bounce hours (not by surviving them).

INFO-FIRST (no P&L): bucket current-like bars by hour-of-day into 4h windows; per window report P(downFirst) and dn-up,
partitioned DISC/CONF/OOS. Discovery = does ordering have robust intraday structure? Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD
from cur_screen import like_at
from cur_cr2 import fwd

def main():
    m=CD.load_m15(); up,dn,af=fwd(m)
    t=m["time"].to_numpy(); cl=like_at(t); yr=m["dt"].dt.year.to_numpy()
    hr=m["dt"].dt.hour.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)
    base=cl&ok
    print("FRONTIER CR-6: intraday ordering in current-like. Looking for a window with P(downFirst) robustly > 0.5.")
    def stat(msk):
        n=int(msk.sum())
        if n<200: return f"n={n}(thin)", None
        afr=af[msk]; pdf=float((afr[afr!=0]==-1).mean()) if (afr!=0).sum() else float('nan')
        return f"n={n:6d} P(downFirst)={pdf:.3f} dn-up={np.median(dn[msk])-np.median(up[msk]):+.2f}", pdf
    s,_=stat(base); print("  [current-like ALL hours]:", s)
    wins=[("00-04",(hr>=0)&(hr<4)),("04-08",(hr>=4)&(hr<8)),("08-12",(hr>=8)&(hr<12)),
          ("12-16",(hr>=12)&(hr<16)),("16-20",(hr>=16)&(hr<20)),("20-24",(hr>=20)&(hr<24))]
    best=[]
    for lab,wm in wins:
        sall,pall=stat(base&wm)
        row=f"  hr {lab}: {sall}"
        pd_=[]
        for plab,ym in [("D",yr<=2021),("C",(yr>=2022)&(yr<=2024)),("O",yr>=2025)]:
            ss,pp=stat(base&wm&ym); pd_.append((plab,pp))
        row+="  | "+" ".join(f"{pl}={pp:.2f}" if pp is not None else f"{pl}=thin" for pl,pp in pd_)
        print(row)
        if pall is not None: best.append((lab,pall,pd_))
    print("\n  ROBUST-ORDERING CHECK (P(downFirst)>0.5 in ALL of D/C/O):")
    found=False
    for lab,pall,pd_ in best:
        ps=[pp for _,pp in pd_ if pp is not None]
        if len(ps)==3 and all(p>0.50 for p in ps) and pall>0.52:
            print(f"    hr {lab}: ROBUST down-first ordering (all partitions >0.50, overall {pall:.3f})"); found=True
    if not found:
        print("    none — no intraday window shows robust>0.5 down-first ordering across all partitions.")

if __name__=="__main__":
    main()

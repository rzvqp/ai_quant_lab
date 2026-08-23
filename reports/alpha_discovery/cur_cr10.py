"""cur_cr10.py — FRONTIER CR-10 (current-regime, info-first): PRIOR-DAY reference-level geometry (PDL/PDH). Last canonical
level class untested (all prior level tests used intraday fractal swings / coils). Prior-day high/low are causal calendar
references (previous COMPLETED day), economically distinct (institutional / the lab's own S1-PDH levels). Two orthogonal
events, both a SHORT thesis, measured info-first for forward ordering vs the established ~0.54 down-first ceiling:
  (1) PDL BREAK-ACCEPT : close crosses below prior-day low   (down-continuation)
  (2) PDH REJECT       : bar pierces prior-day high but closes back below  (fade from resistance)
If EITHER pushes robust P(downFirst) meaningfully above ~0.54 across current-like partitions -> tradeable test earned.
Else calendar-reference geometry is on the ceiling too. INFO-FIRST (no P&L). Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD
from cur_screen import like_at
from cur_cr2 import fwd

def prior_day_levels(m):
    day=m["dt"].dt.floor("D")                       # tz-aware, matches groupby index
    dlow=m.groupby(day)["low"].min(); dhigh=m.groupby(day)["high"].max()
    plow=dlow.shift(1); phigh=dhigh.shift(1)
    PDL=day.map(plow).to_numpy(); PDH=day.map(phigh).to_numpy()
    return PDL,PDH

def main():
    m=CD.load_m15(); up,dn,af=fwd(m); PDL,PDH=prior_day_levels(m)
    c=m["close"].to_numpy(); h=m["high"].to_numpy(); cprev=pd.Series(c).shift(1).to_numpy()
    t=m["time"].to_numpy(); cl=like_at(t); yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)
    breakPDL=(c<PDL)&(cprev>=PDL)&np.isfinite(PDL)
    rejPDH=(h>=PDH)&(c<PDH)&np.isfinite(PDH)
    def block(name, ev):
        ev=np.nan_to_num(ev.astype(float),nan=0).astype(bool)
        def row(msk):
            n=int(msk.sum())
            if n<150: return f"n={n}(thin)"
            afr=af[msk]; pdf=float((afr[afr!=0]==-1).mean()) if (afr!=0).sum() else float('nan')
            return f"n={n:6d} P(downFirst)={pdf:.3f} dn-up={np.median(dn[msk])-np.median(up[msk]):+.2f}"
        print(f"  [{name} x current-like] :", row(cl&ok&ev))
        for lab,ym in [("DISC",yr<=2021),("CONF",(yr>=2022)&(yr<=2024)),("OOS",yr>=2025)]:
            print(f"    {lab}: {row(cl&ok&ev&ym)}")
    print("FRONTIER CR-10: prior-day reference geometry in current-like -> forward ordering (ceiling ~0.54).")
    print("  [current-like baseline] : P(downFirst)=0.515")
    block("PDL break-accept", breakPDL)
    block("PDH reject",       rejPDH)

if __name__=="__main__":
    main()

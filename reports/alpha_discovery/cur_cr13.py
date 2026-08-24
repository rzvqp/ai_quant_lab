"""cur_cr13.py — FRONTIER CR-13 (current-regime, info-first): CROSS-SCALE state transition (H4 x M15). The one untested
representation class. Hypothesis: a FRESH higher-timeframe regime change — H4 EMA20 crossing below EMA50 (a slow, strong,
higher-information signal) — orders the subsequent M15 down-path better than any single-scale M15 event, potentially
breaking the ~0.54 down-first ordering ceiling. Two info checks in current-like:
  (1) STEADY STATE: M15 P(downFirst) when the known (causal) H4 trend is DOWN vs UP.
  (2) FRESH TRANSITION: M15 P(downFirst) within 4 H4 bars (~16h) AFTER a fresh H4 down-transition, partitioned.
Causal: H4 state known only at H4 close_time; merge_asof(backward) maps each M15 bar to the most recent CLOSED H4 bar.
If a fresh H4 down-transition pushes robust P(downFirst) meaningfully above ~0.54 -> tradeable test earned. INFO-FIRST.
Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD
from cur_screen import like_at
from cur_cr2 import fwd

def main():
    m=CD.load_m15(); up,dn,af=fwd(m); h4=CD.agg(m,"H4")
    td=(h4["ema20"].to_numpy()<h4["ema50"].to_numpy())            # H4 trend down
    tdp=pd.Series(td).shift(1).to_numpy()
    trans_down=td & (tdp==False)                                  # fresh down-transition bar
    # bars since last down-transition (on H4)
    since=np.full(len(h4),10**6); k=10**6
    for i in range(len(h4)):
        if trans_down[i]: k=0
        elif k<10**6: k+=1
        since[i]=k
    h4map=pd.DataFrame({"close_time":h4["close_time"].to_numpy(),"h4_down":td.astype(int),"since":since}).sort_values("close_time")
    mm=pd.DataFrame({"time":m["time"].to_numpy()}).sort_values("time")
    j=pd.merge_asof(mm,h4map,left_on="time",right_on="close_time",direction="backward")
    j=j.sort_index()
    h4_down=j["h4_down"].to_numpy(); since_m=j["since"].to_numpy()
    t=m["time"].to_numpy(); cl=like_at(t); yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)&np.isfinite(h4_down)
    def row(msk):
        n=int(msk.sum())
        if n<150: return f"n={n}(thin)"
        afr=af[msk]; pdf=float((afr[afr!=0]==-1).mean()) if (afr!=0).sum() else float('nan')
        return f"n={n:6d} P(downFirst)={pdf:.3f} dn-up={np.median(dn[msk])-np.median(up[msk]):+.2f}"
    print("FRONTIER CR-13: cross-scale H4xM15 in current-like -> M15 ordering (ceiling ~0.54).")
    print("  [current-like baseline]        : P(downFirst)=0.515")
    print("  (1) STEADY STATE:")
    print("    H4 known-trend DOWN :", row(cl&ok&(h4_down==1)))
    print("    H4 known-trend UP   :", row(cl&ok&(h4_down==0)))
    print("  (2) FRESH H4 DOWN-TRANSITION (<=4 H4 bars):")
    fresh=cl&ok&(h4_down==1)&(since_m<=4)
    print("    fresh trans (all)   :", row(fresh))
    for lab,ym in [("DISC",yr<=2021),("CONF",(yr>=2022)&(yr<=2024)),("OOS",yr>=2025)]:
        print(f"      {lab}: {row(fresh&ym)}")

if __name__=="__main__":
    main()

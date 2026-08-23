"""cur_cr3.py — FRONTIER CR-3 (current-regime, info-first): does a VOL-EXPANSION-DOWN ignition concentrate the
down-payoff with low adverse-first, robustly across current-like partitions (not recent-only)? Event = atr/atr_ma
crosses above 1 (vol expansion onset) AND the bar closes down (c<o) = a down-momentum ignition. Hypothesis: this marks
a crash-leg start -> concentrated forward down-excursion + low adverse-first, capturable without tail-dependence.
Info-first (no P&L). Reuses fwd() from cur_cr2. Data through 2026-07-27 (CEO: sufficient).
"""
import numpy as np, pandas as pd
import cur_data as CD
from cur_screen import like_at
from cur_cr2 import fwd

def main():
    m=CD.load_m15(); up,dn,af=fwd(m)
    o=m["open"].to_numpy(); c=m["close"].to_numpy(); vr=(m["atr"]/m["atr_ma"]).to_numpy()
    onset=(vr>1.0)&(pd.Series(vr).shift(1).to_numpy()<=1.0)&(c<o)   # vol-expansion onset with a down bar
    t=m["time"].to_numpy(); cl=like_at(t); yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)
    ev=np.nan_to_num(onset.astype(float),nan=0).astype(bool)
    print("FRONTIER CR-3: VOL-EXPANSION-DOWN ignition in current-like -> forward path (info-first).")
    def row(msk):
        n=int(msk.sum())
        if n<40: return f"n={n}(thin)"
        afr=af[msk]; pdf=float((afr[afr!=0]==-1).mean()) if (afr!=0).sum() else float('nan')
        return f"n={n:5d} up={np.median(up[msk]):.2f} dn={np.median(dn[msk]):.2f} dn-up={np.median(dn[msk])-np.median(up[msk]):+.2f} P(downFirst)={pdf:.3f}"
    print("  [current-like BASELINE]      :", row(cl&ok))
    print("  [VOLEXP-DN x current-like]   :", row(cl&ok&ev))
    for lab,ym in [("DISC<=2021",yr<=2021),("CONF 22-24",(yr>=2022)&(yr<=2024)),("OOS 25-26",yr>=2025)]:
        print(f"    VEDN {lab:10s}:", row(cl&ok&ev&ym))
    print("  [VOLEXP-DN x NON-cur DIAG]   :", row((~cl)&ok&ev))

if __name__=="__main__":
    main()

"""hb_info.py — HIGHVOL_BULL information test (BEFORE any tradeable strategy, per mandate §4). Does the frozen regime supply
forward directional CONTINUATION information? At regime bars, measure forward UP vs DOWN excursion (ATR units) + P(up 1.5ATR
first) + median forward return, vs a NON-regime baseline, partitioned DISC/CONF/OOS. If up-continuation is materially and
robustly present, a LONG specialist is warranted; if symmetric/absent, the regime does not supply direction (let evidence decide).
Info-first, no P&L. Causal regime (highvol_bull_regime). Reuses cur_cr2.fwd. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD
import highvol_bull_regime as HB
from cur_cr2 import fwd

def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4"); on,_=HB.build_h4(h4); onm=HB.map_to_m15(m,h4,on)
    up,dn,af=fwd(m)   # af: +1 = up 1.5ATR first (favorable for LONG), -1 = down first
    reg=(onm==1); yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)
    c=m["close"].to_numpy(); fwdret=(pd.Series(c).shift(-96).to_numpy()-c)/m["atr"].to_numpy()  # 96-bar forward return in ATR
    def row(msk):
        n=int(msk.sum())
        if n<150: return f"n={n}(thin)"
        afr=af[msk]; pu=float((afr[afr!=0]==1).mean()) if (afr!=0).sum() else float('nan')
        return f"n={n:6d} up={np.median(up[msk]):.2f} dn={np.median(dn[msk]):.2f} up-dn={np.median(up[msk])-np.median(dn[msk]):+.2f} P(upFirst)={pu:.3f} fwdRet(96)={np.nanmedian(fwdret[msk]):+.2f}ATR"
    print("HIGHVOL_BULL info test: forward continuation (LONG lens). up-dn>0 & P(upFirst)>0.5 & fwdRet>0 = up-continuation.")
    print("  [regime ON]    :", row(reg&ok))
    print("  [regime OFF]   :", row((~reg)&ok))
    for lab,ym in [("DISC<=2021",yr<=2021),("CONF 22-24",(yr>=2022)&(yr<=2024)),("OOS 25-26",yr>=2025)]:
        print(f"    ON {lab:10s}:", row(reg&ok&ym))

if __name__=="__main__":
    main()

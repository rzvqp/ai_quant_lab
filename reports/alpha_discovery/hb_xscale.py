"""hb_xscale.py — HIGHVOL_BULL new discovery (CRS-1 cross-scale LESSON, not a clone). The re-screen showed the regime's
forward direction is ERA-SPLIT: pre-2021 high-vol bull = blowoff that REVERTS (down); post-2022 = continuation (up). Question:
does a higher-TF (D1) trend confluence distinguish continuation from blowoff and make ONE direction consistent across DISC/
CONF/OOS? Test in HIGHVOL_BULL: (1) + D1-UP -> LONG continuation ; (2) + D1-DOWN control ; (3) info-first up-dn per D1 state.
If D1-UP LONG is consistent (DISC/CONF/OOS all>0) -> candidate; if still DISC-negative -> the era-split is not resolved by
D1 confluence (record, move on). Full gate. Causal regime + causal D1. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
import highvol_bull_regime as HB
from rs2_continuation import d1_trend_map
from cur_cr2 import fwd

def screen(m, idx, side, atr, name):
    n=len(m); idx=idx[idx<n-1]; dd=sb.dedup_events(idx,12); idx=idx[np.isin(idx,dd)]; sl=1.5*atr[idx]
    tr=sb.simulate(m,idx,side,sl,rr=2.0,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    if len(r)<40: print(f"  {name}: N={len(r)} thin"); return
    sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    surv=len(r)>=60 and len(d)>0 and len(cf)>0 and len(oos)>0 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  {name}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} best10%rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f}(n{len(d)}) C {cf.mean():+.3f}(n{len(cf)}) O {oos.mean():+.3f}(n{len(oos)}) -> {'SURVIVOR' if surv else 'no'}")

def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4"); on,_=HB.build_h4(h4); onm=HB.map_to_m15(m,h4,on); d1=d1_trend_map(m)
    atr=m["atr"].to_numpy(); reg=(onm==1)&np.isfinite(atr)&(atr>0)
    up,dn,af=fwd(m); yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)
    print(f"HIGHVOL_BULL x D1 cross-scale. regime={HB.FP}")
    # info-first by D1 state
    def row(msk):
        nn=int(msk.sum())
        if nn<150: return f"n={nn}(thin)"
        return f"n={nn:5d} up-dn={np.median(up[msk])-np.median(dn[msk]):+.2f}"
    for lab,ym in [("DISC",yr<=2021),("CONF",(yr>=2022)&(yr<=2024)),("OOS",yr>=2025)]:
        print(f"  info D1-UP  {lab}:", row(reg&ok&(d1==1)&ym), " | D1-DOWN:", row(reg&ok&(d1==0)&ym))
    print("  tradeable:")
    screen(m, np.where(reg&(d1==1))[0], 1, atr, "(1) HB & D1-UP  LONG      ")
    screen(m, np.where(reg&(d1==0))[0], 1, atr, "(2) HB & D1-DOWN LONG(ctl)")
    screen(m, np.where(reg&(d1==1))[0], -1, atr, "(3) HB & D1-UP  SHORT(ctl)")

if __name__=="__main__":
    main()

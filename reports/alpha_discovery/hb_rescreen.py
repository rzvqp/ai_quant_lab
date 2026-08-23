"""hb_rescreen.py — RE-SCREEN old directional-continuation LONG mechanisms GATED to frozen HIGHVOL_BULL_V1 (mandate §3, new
identity). Two old economic mechanisms tested UNCHANGED, regime-gated:
  (A) pure regime LONG      : buy on regime bars (dedup), 1.5ATR stop, rr2 (is the regime itself long-tradeable?).
  (B) pullback-continuation : buy a 3-bar dip within the regime (the 'TREND_UP x pullback3 LONG' family), 1.5ATR stop, rr2.
Info test already showed forward direction is ERA-DEPENDENT (DISC down-reverts, CONF/OOS up-continue) -> expect DISC-negative.
Full gate: per-year, DISC/CONF/OOS, best-10%-removed, STRESS. Causal regime. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
import highvol_bull_regime as HB

def screen(m, idx, side, atr, name, dedup=12):
    n=len(m); idx=idx[idx<n-1]; dd=sb.dedup_events(idx,dedup); idx=idx[np.isin(idx,dd)]; sl=1.5*atr[idx]
    tr=sb.simulate(m,idx,side,sl,rr=2.0,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    if len(r)<40: print(f"  {name}: N={len(r)} thin"); return
    sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    surv=len(r)>=60 and len(d)>0 and len(cf)>0 and len(oos)>0 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  {name}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} best10%rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f}(n{len(d)}) C {cf.mean():+.3f}(n{len(cf)}) O {oos.mean():+.3f}(n{len(oos)}) -> {'SURVIVOR' if surv else 'no'}")

def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4"); on,_=HB.build_h4(h4); onm=HB.map_to_m15(m,h4,on)
    atr=m["atr"].to_numpy(); c=m["close"].to_numpy(); reg=(onm==1)&np.isfinite(atr)&(atr>0)
    print(f"RE-SCREEN old LONG-continuation mechanisms gated to {HB.FP}")
    # (A) pure regime long
    screen(m, np.where(reg)[0], 1, atr, "(A) pure regime LONG        ")
    # (B) pullback-continuation long: close < close[3] (3-bar dip) within regime
    dip=reg & (c < pd.Series(c).shift(3).to_numpy())
    screen(m, np.where(dip)[0], 1, atr, "(B) pullback3 LONG in-regime")
    print("  (info test predicts DISC-negative: melt-up reverts pre-2021, continues post-2022)")

if __name__=="__main__":
    main()

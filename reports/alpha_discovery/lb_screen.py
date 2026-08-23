"""lb_screen.py — LOWVOL_BULL re-screen (old LONG mechanisms gated) + wide-stop discovery. Info showed era-CONSISTENT positive
forward return (DISC/CONF/OOS fwdRet +0.21/+0.23/+1.06) but coinflip path ordering (P(upFirst)~0.50) -> a tight stop gets
knocked out before the up-drift. Test whether a WIDE structural stop (hold through the low-vol noise) captures the drift.
(A) pure regime LONG 1.5ATR rr2 (tight, expect knocked out). (B) wide-stop LONG 3ATR rr1.5. (C) pullback3 LONG 2.5ATR rr2.
Full gate: per-year, DISC/CONF/OOS all>0, best-10%-removed, STRESS. Causal regime. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
import lowvol_bull_regime as LB

def screen(m, idx, side, atr, stopmult, rr, name, dedup=12):
    n=len(m); idx=idx[idx<n-1]; dd=sb.dedup_events(idx,dedup); idx=idx[np.isin(idx,dd)]; sl=stopmult*atr[idx]
    tr=sb.simulate(m,idx,side,sl,rr=rr,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    if len(r)<40: print(f"  {name}: N={len(r)} thin"); return
    sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    surv=len(r)>=60 and len(d)>0 and len(cf)>0 and len(oos)>0 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  {name}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} best10%rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f}(n{len(d)}) C {cf.mean():+.3f}(n{len(cf)}) O {oos.mean():+.3f}(n{len(oos)}) -> {'SURVIVOR' if surv else 'no'}")

def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4"); on,_=LB.build_h4(h4); onm=LB.map_to_m15(m,h4,on)
    atr=m["atr"].to_numpy(); c=m["close"].to_numpy(); reg=(onm==1)&np.isfinite(atr)&(atr>0)
    print(f"LOWVOL_BULL screen, gated to {LB.FP}")
    screen(m, np.where(reg)[0], 1, atr, 1.5, 2.0, "(A) regime LONG 1.5ATR rr2 ")
    screen(m, np.where(reg)[0], 1, atr, 3.0, 1.5, "(B) regime LONG 3.0ATR rr1.5")
    dip=reg & (c < pd.Series(c).shift(3).to_numpy())
    screen(m, np.where(dip)[0], 1, atr, 2.5, 2.0, "(C) pullback3 LONG 2.5ATR rr2")
    screen(m, np.where(reg)[0], 1, atr, 2.5, 3.0, "(D) regime LONG 2.5ATR rr3 ")

if __name__=="__main__":
    main()

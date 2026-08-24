"""bull_xscale_long.py — candidate BLS-1: cross-scale divergence LONG on the BULL side (generalization test of the CRS-1
PRINCIPLE, not a clone). CRS-1 = down-regime + H4-UP counter-bounce -> SHORT (fade WITH the down-flow). Mirror = slow BULL
context (D1-trend-UP) + FAST counter-dip (H4-trend-DOWN) -> M15 LONG (buy the dip WITH the up-flow). Distinct scales (D1 regime
vs CRS-1's current-like), opposite direction. If it survives the full gate across DISC/CONF/OOS -> a bull-side specialist
complementing CRS-1; if era-split -> the principle does not generalize to the bull side. Causal D1 + causal H4. Full gate.
Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from rs2_continuation import d1_trend_map
from cur_cr13_trade import h4_up_map   # returns h4_down: 1=H4 ema-down, 0=up

def run(m, idx, atr, sm, rr, label, verbose=True):
    n=len(m); idx=idx[idx<n-1]; dd=sb.dedup_events(idx,16); idx=idx[np.isin(idx,dd)]; sl=sm*atr[idx]
    tr=sb.simulate(m,idx,1,sl,rr=rr,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr
    if len(r)<40: print(f"  {label}: N={len(r)} thin"); return r,yr
    sr=np.sort(r); k1=max(1,len(r)//100); k10=max(1,len(r)//10)
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    negyr=sum(1 for y in set(yr) if r[yr==y].mean()<0); nyr=len(set(yr))
    o=np.sort(idx); nep=1+int((np.diff(o)>96).sum())
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} episodes~{nep}")
    print(f"    best-1%rm={sr[:-k1].mean():+.4f} best-10%rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f}(n{len(d)}) C {cf.mean():+.3f}(n{len(cf)}) O {oos.mean():+.3f}(n{len(oos)}) | neg-yrs {negyr}/{nyr} -> {'SURVIVOR' if surv else 'no'}")
    return r,yr

def main():
    m=CD.load_m15(); d1=d1_trend_map(m); h4d=h4_up_map(m); atr=m["atr"].to_numpy()
    div=(d1==1)&(h4d==1)&np.isfinite(atr)&(atr>0)   # D1 up, H4 down = dip in bull
    print(f"BLS-1 cross-scale divergence LONG (D1-UP + H4-DOWN dip). events={int(div.sum())}")
    run(m, np.where(div)[0], atr, 1.5, 2.0, "PRIMARY 1.5ATR rr2")
    print("  NEIGHBORS:")
    for sm,rr in [(1.5,1.0),(2.0,2.0),(2.5,2.0)]:
        r,yr=run(m, np.where(div)[0], atr, sm, rr, "", verbose=False)
        sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; o=r[yr>=2025]
        print(f"    stop{sm} rr{rr}: N={len(r)} avgR={r.mean():+.4f} best10rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {o.mean():+.3f}")
    print("  controls:")
    r,yr=run(m, np.where((d1==1)&(h4d==0)&np.isfinite(atr)&(atr>0))[0], atr, 1.5, 2.0, "", verbose=False)  # D1-up & H4-up (no divergence)
    print(f"    D1-UP & H4-UP (no divergence) LONG: avgR={r.mean():+.4f} (n{len(r)})")
    r,yr=run(m, np.where((d1==0)&(h4d==1)&np.isfinite(atr)&(atr>0))[0], atr, 1.5, 2.0, "", verbose=False)  # D1-down & H4-down: long-dip in bear (should fail)
    print(f"    D1-DOWN & H4-DOWN LONG (control, fight bear): avgR={r.mean():+.4f} (n{len(r)})")

if __name__=="__main__":
    main()

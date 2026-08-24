"""lvbear_gate.py — full skepticism gate for the LOWVOL_BEAR wide-stop SHORT near-miss (2.5ATR rr2, era-consistent all
partitions but best-10%-removed -0.170). Question: is it a genuine survivor or tail-dependent? Battery: best-1/5/10% removed,
leave-one-year-out, per-year, neighbor (stop,rr), effective N / episodes, regime specificity (NOT-in-regime control), and a
cross-scale D1-down conditioning to test if it removes tail-dependence. Causal regime + causal D1. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
import lowvol_bear_regime as LVB
from rs2_continuation import d1_trend_map

def run(m, idx, atr, sm, rr, label, verbose=True):
    n=len(m); idx=idx[idx<n-1]; dd=sb.dedup_events(idx,12); idx=idx[np.isin(idx,dd)]; sl=sm*atr[idx]
    tr=sb.simulate(m,idx,-1,sl,rr=rr,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); te=tr["t_entry"].to_numpy(); yr=pd.Series(pd.to_datetime(te,unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr,te
    if len(r)<40: print(f"  {label}: thin"); return r,yr,te
    sr=np.sort(r); k1=max(1,len(r)//100); k5=max(1,len(r)//20); k10=max(1,len(r)//10)
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f}")
    print(f"    best-1%rm={sr[:-k1].mean():+.4f} best-5%rm={sr[:-k5].mean():+.4f} best-10%rm={sr[:-k10].mean():+.4f} worst={sr[0]:+.2f}")
    print(f"    D {d.mean():+.3f}(n{len(d)}) C {cf.mean():+.3f}(n{len(cf)}) O {oos.mean():+.3f}(n{len(oos)})")
    ys=sorted(set(yr)); worst=min((r[yr!=y].mean(),int(y)) for y in ys)
    print(f"    per-year: {[(int(y),round(float(r[yr==y].mean()),2),int((yr==y).sum())) for y in ys]}")
    print(f"    leave-1yr-out worst avgR={worst[0]:+.4f} (drop {worst[1]})")
    return r,yr,te

def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4"); on,_=LVB.build_h4(h4); onm=LVB.map_to_m15(m,h4,on); d1=d1_trend_map(m)
    atr=m["atr"].to_numpy(); reg=(onm==1)&np.isfinite(atr)&(atr>0)
    print(f"LOWVOL_BEAR wide-short full gate, {LVB.FP}")
    run(m, np.where(reg)[0], atr, 2.5, 2.0, "PRIMARY 2.5ATR rr2")
    print("  NEIGHBORS:")
    for sm,rr in [(2.0,2.0),(3.0,2.0),(2.5,1.5),(2.5,3.0)]:
        r,yr,_=run(m, np.where(reg)[0], atr, sm, rr, "", verbose=False)
        sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; o=r[yr>=2025]
        print(f"    stop{sm} rr{rr}: N={len(r)} avgR={r.mean():+.4f} best10rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {o.mean():+.3f}")
    print("  CROSS-SCALE (D1-down confluence) — does it remove tail-dependence?")
    run(m, np.where(reg&(d1==0))[0], atr, 2.5, 2.0, "D1-DOWN 2.5ATR rr2")
    print("  REGIME SPECIFICITY (same short NOT-in-regime):")
    r,yr,_=run(m, np.where((onm!=1)&np.isfinite(atr)&(atr>0))[0], atr, 2.5, 2.0, "", verbose=False)
    print(f"    NOT-in-regime: N={len(r)} avgR={r.mean():+.4f} (should be <= in-regime if regime matters)")

if __name__=="__main__":
    main()

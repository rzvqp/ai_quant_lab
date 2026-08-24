"""lvbear_accept.py — LOWVOL_BEAR specialist candidate via a DIFFERENT cross-scale event (mandate §5 'acceptance/retest, not
raw breakout'; NOT the CRS-1 bounce-fade). Higher-TF LOWVOL_BEAR_V1 supplies the down-context; lower-TF M15 broken-support
RETEST-FAILURE (acceptance below, reused unchanged from cur_cr5.reject_events) times the entry. Question: does event-timing
remove the LOWVOL_BEAR wide-short's tail-dependence (best-5%rm was negative)? SHORT, 2.5ATR stop, rr2, STRESS. Full gate.
Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
import lowvol_bear_regime as LVB
from cur_cr5 import reject_events

def run(m, idx, atr, sm, rr, label, verbose=True):
    n=len(m); idx=idx[idx<n-1]; dd=sb.dedup_events(idx,12); idx=idx[np.isin(idx,dd)]; sl=sm*atr[idx]
    tr=sb.simulate(m,idx,-1,sl,rr=rr,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr
    if len(r)<40: print(f"  {label}: N={len(r)} thin"); return r,yr
    sr=np.sort(r); k1=max(1,len(r)//100); k5=max(1,len(r)//20); k10=max(1,len(r)//10)
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    nyr=len(set(yr)); negyr=sum(1 for y in set(yr) if r[yr==y].mean()<0)
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and (len(oos)==0 or oos.mean()>0) and sr[:-k5].mean()>0
    print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f}")
    print(f"    best-1%rm={sr[:-k1].mean():+.4f} best-5%rm={sr[:-k5].mean():+.4f} best-10%rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f}(n{len(d)}) C {cf.mean():+.3f}(n{len(cf)}) O {oos.mean():+.3f}(n{len(oos)}) neg-yrs {negyr}/{nyr} -> {'SURVIVOR(best5rm+)' if surv else 'no'}")
    return r,yr

def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4"); on,_=LVB.build_h4(h4); onm=LVB.map_to_m15(m,h4,on)
    ev=reject_events(m); atr=m["atr"].to_numpy()
    reg=(onm==1)&np.isfinite(atr)&(atr>0)
    both=reg&ev
    print(f"LOWVOL_BEAR x M15 acceptance/retest-failure SHORT, {LVB.FP}")
    print(f"  acceptance events total={int(ev.sum())}, in-LOWVOL_BEAR={int(both.sum())}")
    run(m, np.where(both)[0], atr, 2.5, 2.0, "PRIMARY accept-short 2.5ATR rr2")
    print("  NEIGHBORS:")
    for sm,rr in [(2.0,2.0),(3.0,2.0),(2.5,3.0)]:
        r,yr=run(m, np.where(both)[0], atr, sm, rr, "", verbose=False)
        if len(r)<40: print(f"    stop{sm} rr{rr}: thin"); continue
        sr=np.sort(r); k5=max(1,len(r)//20); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; o=r[yr>=2025]
        print(f"    stop{sm} rr{rr}: N={len(r)} avgR={r.mean():+.4f} best5rm={sr[:-k5].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {o.mean():+.3f}")
    print("  regime specificity (acceptance short NOT in LOWVOL_BEAR):")
    r,yr=run(m, np.where((onm!=1)&ev&np.isfinite(atr)&(atr>0))[0], atr, 2.5, 2.0, "", verbose=False)
    if len(r)>=40: print(f"    NOT-in-regime: N={len(r)} avgR={r.mean():+.4f}")

if __name__=="__main__":
    main()

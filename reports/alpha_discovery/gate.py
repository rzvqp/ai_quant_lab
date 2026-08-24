"""gate.py — shared causal skepticism-gate screen for post-repair discovery frontiers. STRESS, structural full gate."""
import numpy as np, pandas as pd
import swing_base as sb
def screen(m, idx, side, atr, label, sm=1.5, rr=2.0, dedup=8, H=96, verbose=True):
    n=len(m); idx=np.asarray(idx); idx=idx[idx<n-1]
    if len(idx)<40:
        if verbose: print(f"  {label}: N={len(idx)} thin")
        return None
    dd=sb.dedup_events(idx,dedup); idx=idx[np.isin(idx,dd)]; sl=sm*atr[idx]
    tr=sb.simulate(m,idx,side,sl,rr=rr,horizon=H,scenario="STRESS")
    r=tr["R"].to_numpy(); te=tr["t_entry"].to_numpy(); yr=pd.Series(pd.to_datetime(te,unit="s",utc=True)).dt.year.to_numpy()
    if len(r)<40:
        if verbose: print(f"  {label}: N={len(r)} thin")
        return None
    sr=np.sort(r); k1=max(1,len(r)//100); k10=max(1,len(r)//10)
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]; ny=sum(1 for y in set(yr) if r[yr==y].mean()<0)
    o=np.sort(idx); nep=1+int((np.diff(o)>H).sum())
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    if verbose:
        print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} best1rm={sr[:-k1].mean():+.4f} best10rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {oos.mean():+.3f} negyr{ny}/{len(set(yr))} ep~{nep} -> {'SURVIVOR' if surv else 'no'}")
    return dict(r=r,yr=yr,surv=surv,avg=float(r.mean()))

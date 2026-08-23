"""accept_above_long.py — candidate ALS-1: LONG acceptance-continuation via resistance-break RETEST-HOLD (the untested MIRROR
of the validated acceptance-short). Portfolio gap = long-side structural events (only S5). Event: price breaks ABOVE a confirmed
swing-high (resistance), RETESTS it from above (low<=level), then HOLDS (a bar closes back ABOVE the level = acceptance above =
level flips to support) -> LONG. Direction-supplying structural event (like S5/CRS-1), distinct from S5 (level-flip-timed not
NY-session-timed). Causal: swing high confirmed at i+K; break/retest/hold use only past+current. Test unconditional + gated to
D1-up + gated to high-vol context; full gate (DISC/CONF/OOS, tail, per-year, neighbor, S5/CRS-1 redundancy). Data thru 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from rs2_continuation import d1_trend_map
K=6; WBREAK=48; WRETEST=48

def accept_above_events(m):
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); n=len(m)
    roll=pd.Series(h).rolling(2*K+1,center=True).max().to_numpy()
    isswing=(h==roll)&np.isfinite(roll); sw=np.where(isswing)[0]
    lv=np.full(n,np.nan)
    for i in sw:
        e=i+K
        if e<n: lv[e]=h[i]
    L=pd.Series(lv).ffill().to_numpy()   # most recent confirmed resistance (causal)
    ev=np.zeros(n,bool); st=0; Lb=np.nan; tb=-1; tr=-1
    for t in range(n):
        Lt=L[t]
        if not np.isfinite(Lt): continue
        if st==0:
            if c[t]>Lt: st=1; Lb=Lt; tb=t          # broke above resistance
        elif st==1:
            if t-tb>WBREAK: st=0; continue
            if l[t]<=Lb: st=2; tr=t                  # retested from above
        elif st==2:
            if t-tr>WRETEST: st=0; continue
            if c[t]>Lb: ev[t]=True; st=0             # held (closed back above) = acceptance above
    return ev

def run(m, idx, atr, sm, rr, label, verbose=True):
    n=len(m); idx=idx[idx<n-1]; dd=sb.dedup_events(idx,12); idx=idx[np.isin(idx,dd)]; sl=sm*atr[idx]
    tr=sb.simulate(m,idx,1,sl,rr=rr,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); te=tr["t_entry"].to_numpy(); yr=pd.Series(pd.to_datetime(te,unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr,te
    if len(r)<40: print(f"  {label}: N={len(r)} thin"); return r,yr,te
    sr=np.sort(r); k1=max(1,len(r)//100); k10=max(1,len(r)//10)
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    negyr=sum(1 for y in set(yr) if r[yr==y].mean()<0); nyr=len(set(yr))
    o=np.sort(idx); nep=1+int((np.diff(o)>96).sum())
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} episodes~{nep}")
    print(f"    best-1%rm={sr[:-k1].mean():+.4f} best-10%rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f}(n{len(d)}) C {cf.mean():+.3f}(n{len(cf)}) O {oos.mean():+.3f}(n{len(oos)}) | neg-yrs {negyr}/{nyr} -> {'SURVIVOR' if surv else 'no'}")
    return r,yr,te

def main():
    m=CD.load_m15(); ev=accept_above_events(m); atr=m["atr"].to_numpy(); d1=d1_trend_map(m)
    h4=CD.agg(m,"H4"); base=pd.Series(h4["atr"].to_numpy()).rolling(360).median().shift(1).to_numpy()
    vr4=h4["atr"].to_numpy()/base
    hm=pd.DataFrame({"close_time":h4["close_time"].to_numpy(),"hv":(vr4>=1.2).astype(float)}).sort_values("close_time")
    mm=pd.DataFrame({"time":m["time"].to_numpy()}).sort_values("time")
    hv=pd.merge_asof(mm,hm,left_on="time",right_on="close_time",direction="backward").sort_index()["hv"].to_numpy()
    okm=np.isfinite(atr)&(atr>0); evb=np.nan_to_num(ev.astype(float),nan=0).astype(bool)
    print(f"ALS-1 acceptance-above LONG. events={int(evb.sum())}")
    run(m, np.where(evb&okm)[0], atr, 1.5, 2.0, "PRIMARY all-context 1.5ATR rr2")
    run(m, np.where(evb&okm&(d1==1))[0], atr, 1.5, 2.0, "gated D1-UP 1.5ATR rr2")
    run(m, np.where(evb&okm&(hv==1))[0], atr, 1.5, 2.0, "gated HIGH-VOL 1.5ATR rr2")
    print("  neighbors (all-context):")
    for sm,rr in [(1.5,1.0),(2.0,2.0),(2.5,3.0)]:
        r,yr,_=run(m, np.where(evb&okm)[0], atr, sm, rr, "", verbose=False)
        sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; o=r[yr>=2025]
        print(f"    stop{sm} rr{rr}: avgR={r.mean():+.4f} best10rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {o.mean():+.3f}")

if __name__=="__main__":
    main()

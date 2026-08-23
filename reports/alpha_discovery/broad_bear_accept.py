"""broad_bear_accept.py — BEAR-context acceptance SHORT (portfolio candidate BRS-1). Motivated by the LOWVOL_BEAR x acceptance
near-miss (tail-dependence removed but OOS too thin). Broaden the down-context to ANY causal H4 downtrend (ema20<ema50 &
effic<0, any vol) to get adequate OOS, keep the SAME lower-TF acceptance/retest-failure trigger (cur_cr5.reject_events). This
is INHERENTLY DISJOINT from CRS-1 (which requires H4 ema-UP), so no redundancy. FROZEN causal context (bounded effic + EMA,
no global pct). SHORT, 2.5ATR stop, rr2, STRESS. Full gate: best-1/5/10% removed, DISC/CONF/OOS, per-year, leave-1yr, neighbor,
effective N/episodes, regime specificity (acceptance short in H4-UP context must be worse). Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from cur_cr5 import reject_events

def bear_map(m):
    h4=CD.agg(m,"H4"); dn=((h4["ema20"].to_numpy()<h4["ema50"].to_numpy())&(h4["effic"].to_numpy()<0)).astype(float)
    up=((h4["ema20"].to_numpy()>h4["ema50"].to_numpy())&(h4["effic"].to_numpy()>0)).astype(float)
    hm=pd.DataFrame({"close_time":h4["close_time"].to_numpy(),"dn":dn,"up":up}).sort_values("close_time")
    mm=pd.DataFrame({"time":m["time"].to_numpy()}).sort_values("time")
    j=pd.merge_asof(mm,hm,left_on="time",right_on="close_time",direction="backward").sort_index()
    return j["dn"].to_numpy(), j["up"].to_numpy()

def run(m, idx, atr, sm, rr, label, verbose=True):
    n=len(m); idx=idx[idx<n-1]; dd=sb.dedup_events(idx,12); idx=idx[np.isin(idx,dd)]; sl=sm*atr[idx]
    tr=sb.simulate(m,idx,-1,sl,rr=rr,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); te=tr["t_entry"].to_numpy(); yr=pd.Series(pd.to_datetime(te,unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr
    if len(r)<40: print(f"  {label}: N={len(r)} thin"); return r,yr
    sr=np.sort(r); k1=max(1,len(r)//100); k5=max(1,len(r)//20); k10=max(1,len(r)//10)
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    negyr=sum(1 for y in set(yr) if r[yr==y].mean()<0); nyr=len(set(yr))
    worst=min((r[yr!=y].mean(),int(y)) for y in set(yr))
    # episode clustering
    o=np.sort(idx); nep=1+int((np.diff(o)>96).sum())
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k5].mean()>0 and sr[:-k10].mean()>0
    print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} episodes~{nep}")
    print(f"    best-1%rm={sr[:-k1].mean():+.4f} best-5%rm={sr[:-k5].mean():+.4f} best-10%rm={sr[:-k10].mean():+.4f} worst={sr[0]:+.2f}")
    print(f"    D {d.mean():+.3f}(n{len(d)}) C {cf.mean():+.3f}(n{len(cf)}) O {oos.mean():+.3f}(n{len(oos)}) | neg-yrs {negyr}/{nyr} | leave1yr-worst {worst[0]:+.3f}(drop{worst[1]}) -> {'SURVIVOR' if surv else 'no'}")
    return r,yr

def main():
    m=CD.load_m15(); dn,up=bear_map(m); ev=reject_events(m); atr=m["atr"].to_numpy()
    bear=(dn==1)&np.isfinite(atr)&(atr>0); both=bear&ev
    print(f"BEAR-context (H4 ema-down & effic<0) x M15 acceptance SHORT. events in-bear={int(both.sum())}")
    run(m, np.where(both)[0], atr, 2.5, 2.0, "PRIMARY 2.5ATR rr2")
    print("  NEIGHBORS:")
    for sm,rr in [(2.0,2.0),(3.0,2.0),(2.5,1.5),(2.5,3.0)]:
        r,yr=run(m, np.where(both)[0], atr, sm, rr, "", verbose=False)
        sr=np.sort(r); k5=max(1,len(r)//20); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; o=r[yr>=2025]
        print(f"    stop{sm} rr{rr}: N={len(r)} avgR={r.mean():+.4f} best5rm={sr[:-k5].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {o.mean():+.3f}")
    print("  regime specificity (acceptance short in H4-UP context, should be worse):")
    r,yr=run(m, np.where((up==1)&ev&np.isfinite(atr)&(atr>0))[0], atr, 2.5, 2.0, "", verbose=False)
    if len(r)>=40: print(f"    H4-UP context: N={len(r)} avgR={r.mean():+.4f}")

if __name__=="__main__":
    main()

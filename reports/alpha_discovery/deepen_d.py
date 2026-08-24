"""deepen_d.py — §15 deepening + §30 PORTFOLIO INDEPENDENCE of the Batch D session-range-inheritance survivors
(all NY-long) vs the frozen S5 (ORB_NY_L). Decisive question: are they a NEW edge or the same NY-long-momentum
as S5 fired by a different trigger? Measures per-year/DISC-CONF/best-block-removal + same-DAY overlap vs S5 +
incremental (S5-day-excluded) trade count & avgR. Same ratified sb engine, STRESS.
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import orb
from batch_d import session_range_break

def trades_of(sigfn, side, rr):
    rows=[]
    for tag,fr,mask in bs.build_eras():
        idx,sl=sigfn(fr); idx=np.asarray(idx); sl=np.asarray(sl,float)
        keep=mask[idx]; idx=idx[keep]; sl=sl[keep]
        if len(idx)==0: continue
        o=np.argsort(idx); idx=idx[o]; sl=sl[o]; dd=bs.sb.dedup_events(idx,8); p=np.isin(idx,dd); idx=idx[p]; sl=sl[p]
        ok=np.isfinite(sl)&(sl>0); idx=idx[ok]; sl=sl[ok]
        tr=bs.sb.simulate(fr,idx,side,sl,rr=rr,horizon=48,scenario="STRESS")
        if len(tr): tr=tr.copy(); tr["era"]=tag; rows.append(tr)
    return pd.concat(rows,ignore_index=True) if rows else pd.DataFrame()

def daykey(tr):
    d=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.floor("D").astype("int64").to_numpy()
    return set(zip(tr["era"].to_numpy(), d)), d

def analyze(name, sigfn, side, s5days):
    tr=trades_of(sigfn, side, 2.0); R=tr["R"].to_numpy()
    yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    order=np.argsort(tr["t_entry"].to_numpy()); Rs=R[order]; cut=int(len(Rs)*0.6)
    py={int(y):(round(float(R[yr==y].mean()),3),int((yr==y).sum())) for y in np.unique(yr)}
    blk=np.where(yr<=2014,"b0",np.where(yr<=2018,"b1",np.where(yr<=2023,"DEV","CAL")))
    bavg={b:float(R[blk==b].mean()) for b in np.unique(blk)}; bb=max(bavg,key=bavg.get)
    rem=R[blk!=bb]; remavg=float(rem.mean()) if len(rem) else np.nan
    dk,_=daykey(tr); d=np.array([x[1] for x in dk]) if dk else np.array([])
    on_s5=sum(1 for k in dk if k in s5days); frac=on_s5/max(len(dk),1)
    # incremental: trades whose (era,day) NOT an S5 day
    keyarr=list(zip(tr["era"].to_numpy(), pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.floor("D").astype("int64").to_numpy()))
    indep_mask=np.array([k not in s5days for k in keyarr]); indepR=R[indep_mask]
    months=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.to_period("M").nunique()
    print(f"\n### {name} N={len(R)} avgR={R.mean():+.3f} DISC={Rs[:cut].mean():+.3f} CONF={Rs[cut:].mean():+.3f}")
    print(f"  per-year: {py}")
    print(f"  blocks={{ {', '.join(f'{k}:{round(v,3)}' for k,v in bavg.items())} }} best={bb} -> w/o-best={remavg:+.3f}")
    print(f"  §30 vs S5: {frac:.0%} of trade-days overlap an S5 NY-long day | INDEPENDENT (non-S5-day) trades: n={int(indep_mask.sum())} avgR={indepR.mean():+.3f} (~{indep_mask.sum()/max(months,1):.1f}/mo)")

if __name__=="__main__":
    print("BATCH D DEEPENING + §30 INDEPENDENCE vs frozen S5 (ORB_NY_L).")
    s5=trades_of(lambda f:orb(f,13,21,1),1,3.0); s5days,_=daykey(s5)
    print(f"S5 anchor: N={len(s5)} avgR={s5['R'].mean():+.3f} unique NY-long days={len(s5days)}")
    analyze("ASIArange_NYbreak_L", lambda f:session_range_break(f,(0,7),(13,21),1), 1, s5days)
    analyze("LONrange_NYbreak_L",  lambda f:session_range_break(f,(7,13),(13,21),1), 1, s5days)
    analyze("LONrange_NYbreak_L_acc", lambda f:session_range_break(f,(7,13),(13,21),1,hold=True), 1, s5days)

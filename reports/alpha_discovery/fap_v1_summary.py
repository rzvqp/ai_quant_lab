"""fap_v1_summary.py — full §5-20 battery for FAILED_ACCEPTANCE_PRIOR_LEVEL_V1 (behavior-only): destination race, §7 info gate (lift + folds),
§9 path MFE/MAE vs control, §10 time-to-L0, §11 move sizes, §13 level types, §14 direction, §15 chronology, §16 overshoot, §17 failure-close
distances, §18 behavior gate, §19 execution-research gate. No PnL, no optimization."""
import numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
EV=pd.read_parquet(OUT+r"\FAILED_ACCEPTANCE_PRIOR_LEVEL_V1_EVENTS.parquet")
EV1=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet"); yrs=(EV1.dtime.max()-EV1.dtime.min())/(365.25*86400)
P=lambda a,q: float(np.percentile(a,q))
fail=EV[~EV.accepted]; acc=EV[EV.accepted]; failv=fail[fail.has_L0].copy(); accv=acc[acc.has_L0].copy()
FL0=failv.l0_reached.mean()*100; AL0=accv.l0_reached.mean()*100; LIFT=FL0-AL0
dest=failv.dest.value_counts(normalize=True).mul(100).round(2)
L0f=dest.get("L0_FIRST",0); L2f=dest.get("L2_FIRST",0); NE=dest.get("NEITHER",0)
ratio=L0f/(L2f+1e-9)
# §7 chronological folds of failed-vs-accepted L0-reach lift
def fold_lift():
    fv=failv.sort_values("dtime"); av=accv.sort_values("dtime"); out=[]
    fthir=np.array_split(fv.index.to_numpy(),3); athir=np.array_split(av.index.to_numpy(),3)
    for ft,at in zip(fthir,athir):
        out.append(round(100*(failv.loc[ft].l0_reached.mean()-accv.loc[at].l0_reached.mean()),1))
    return out
folds=fold_lift(); folds_ok=sum(1 for x in folds if x>0)
INFO=(LIFT>=15) and (folds_ok>=2)
# §9 MFE/MAE
mm_f=failv.mfe_rev.median()/(failv.mae_rev.median()+1e-9); mm_a=accv.mfe_rev.median()/(accv.mae_rev.median()+1e-9)
mfe_better = mm_f > mm_a*1.05
# §10 time to L0 (events reaching L0 first)
l0first=failv[failv.dest=="L0_FIRST"]; b2=l0first.bars_to_L0.to_numpy()
ttl={w:100*(failv.bars_to_L0[(failv.bars_to_L0>=0)]<=w).sum()/len(failv) for w in (4,8,16,32)}
# §11 move sizes (reversal favorable USD before defeat); 1 pip=$0.10
mv={}
for lbl,thr in (("50p",5),("100p",10),("150p",15),("200p",20)):
    cnt=int((failv.rev_usd>=thr).sum()); mv[lbl]=(round(100*cnt/len(failv),1),round(cnt/yrs,0))
# §16/17
overshoot=failv.overshoot_atr.median(); f2l0=failv.fail_to_L0_atr.median(); f2l1=failv.fail_to_L1_atr.median(); f2l2=failv.fail_to_L2_atr.median(); l1l0=failv.L1_L0_atr.median()
# §13 level types (by L1 and L0)
ltL1=failv.groupby("L1_type").agg(n=("dest","size"),L0_first=("dest",lambda x:(x=="L0_FIRST").mean()))
ltL0=failv.groupby("L0_type").agg(n=("dest","size"),L0_first=("dest",lambda x:(x=="L0_FIRST").mean()))
best_lt=int(ltL1.L0_first.idxmax())
# §14 direction
up=failv[failv.dir>0]; dn=failv[failv.dir<0]
# §18 behavior gate
BEHAV = (len(failv)>=500) and INFO and (L0f>L2f*1.2) and (folds_ok>=2) and mfe_better
# §19 execution gate
EXEC = BEHAV and (len(failv)/yrs>=100) and (f2l0>=0.5)
# writes
failv.groupby("year").agg(n=("dest","size"),L0_first=("dest",lambda x:(x=="L0_FIRST").mean()),l0_reach=("l0_reached","mean")).to_csv(OUT+r"\FAILED_ACCEPTANCE_PRIOR_LEVEL_V1_YEARLY.csv")
pd.concat([ltL1.assign(by="L1"),ltL0.assign(by="L0")]).to_csv(OUT+r"\FAILED_ACCEPTANCE_PRIOR_LEVEL_V1_LEVEL_TYPES.csv")
pd.DataFrame([dict(w=w,l0_within_pct=round(ttl[w],1)) for w in (4,8,16,32)]).to_csv(OUT+r"\FAILED_ACCEPTANCE_PRIOR_LEVEL_V1_PATH.csv",index=False)
pd.DataFrame([dict(threshold=k,pct=v[0],per_year=v[1]) for k,v in mv.items()]).to_csv(OUT+r"\FAILED_ACCEPTANCE_PRIOR_LEVEL_V1_MOVE_DISTRIBUTION.csv",index=False)
pd.DataFrame([dict(metric="failed_events",v=len(fail)),dict(metric="failed_per_yr",v=round(len(fail)/yrs,0)),dict(metric="valid_L0",v=len(failv)),
    dict(metric="failed_L0_rate",v=round(FL0,1)),dict(metric="accepted_L0_rate",v=round(AL0,1)),dict(metric="L0_reach_lift_pp",v=round(LIFT,1)),
    dict(metric="L0_first_pct",v=round(L0f,1)),dict(metric="L2_first_pct",v=round(L2f,1)),dict(metric="neither_pct",v=round(NE,1)),dict(metric="L0_L2_ratio",v=round(ratio,2)),
    dict(metric="median_bars_to_L0",v=float(np.median(b2)) if len(b2) else np.nan),dict(metric="rev_MFE_MAE",v=round(mm_f,2)),dict(metric="acc_MFE_MAE",v=round(mm_a,2)),
    dict(metric="overshoot_atr",v=round(overshoot,2)),dict(metric="fail_to_L0_atr",v=round(f2l0,2)),dict(metric="L1_L0_atr",v=round(l1l0,2)),
    dict(metric="up_L0_first",v=round(100*(up.dest=="L0_FIRST").mean(),1)),dict(metric="dn_L0_first",v=round(100*(dn.dest=="L0_FIRST").mean(),1))]).to_csv(OUT+r"\FAILED_ACCEPTANCE_PRIOR_LEVEL_V1_RESULTS.csv",index=False)
print(f"FAILED={len(fail)} ({len(fail)/yrs:.0f}/yr) VALID_L0={len(failv)} ({len(failv)/yrs:.0f}/yr)")
print(f"DEST: L0_first={L0f:.1f}% L2_first={L2f:.1f}% neither={NE:.1f}% | L0/L2 ratio={ratio:.2f}")
print(f"§7 FAILED_L0={FL0:.1f}% ACCEPTED_L0={AL0:.1f}% LIFT={LIFT:+.1f}pp folds={folds} ok={folds_ok}/3 -> INFO={'YES' if INFO else 'NO'}")
print(f"§9 reversal MFE/MAE failed={mm_f:.2f} accepted={mm_a:.2f} -> materially_better={mfe_better}")
print(f"§10 median bars_to_L0={np.median(b2):.1f} P25={P(b2,25):.0f} P75={P(b2,75):.0f} | L0_within 4/8/16/32={[round(ttl[w],1) for w in (4,8,16,32)]}")
print(f"§11 reversal moves/yr={({k:v[1] for k,v in mv.items()})} pct={({k:v[0] for k,v in mv.items()})}")
print(f"§16 overshoot={overshoot:.2f}ATR §17 fail->L1={f2l1:.2f} fail->L0={f2l0:.2f} fail->L2={f2l2:.2f} ATR | L1->L0={l1l0:.2f}ATR")
print(f"§14 UP L0_first={100*(up.dest=='L0_FIRST').mean():.1f}%(n{len(up)}) DOWN L0_first={100*(dn.dest=='L0_FIRST').mean():.1f}%(n{len(dn)})")
print(f"§13 L1-type L0_first:\n{ltL1.round(3).to_string()}\n best_L1_type={best_lt}")
print(f"§18 BEHAVIOR_CONFIRMED={'YES' if BEHAV else 'NO'} (events{len(failv)>=500} info{INFO} L0>>L2{L0f>L2f*1.2} folds{folds_ok>=2} mfe_better{mfe_better})")
print(f"§19 EXECUTION_RESEARCH_JUSTIFIED={'YES' if EXEC else 'NO'}")

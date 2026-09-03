"""lvl_v1_summary.py — level-to-level V1 metrics: behavior confirmation (accepted vs rejected reach, chronological folds), full strategy
metrics, tail, level-type, move audit, L2-vs-2R counterfactual, candidate gate. Diagnostic; no optimization."""
import os, numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
EV=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet"); TR=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_TRADES.parquet")
SEC_YR=365.25*86400; yrs=(EV.dtime.max()-EV.dtime.min())/SEC_YR
# behavior: accepted vs rejected reach, overall + chronological thirds (by event)
def foldwise(EVv):
    E=EVv[EVv.has_L2].sort_values("dtime"); th=np.array_split(E.index.to_numpy(),3); out=[]
    for t in th:
        g=E.loc[t]; a=g[g.accepted].reached_L2.mean()*100; r=g[~g.accepted].reached_L2.mean()*100; out.append((a,r,a-r))
    return out
acc=EV[EV.accepted&EV.has_L2]; rej=EV[(~EV.accepted)&EV.has_L2]
AR=acc.reached_L2.mean()*100; RR=rej.reached_L2.mean()*100
folds=foldwise(EV); lift_signs=sum(1 for a,r,dlt in folds if dlt>=15)
behav_conf = (AR-RR)>=15 and lift_signs>=2
print(f"ACCEPTED_REACH={AR:.1f}% REJECTED_REACH={RR:.1f}% LIFT={AR-RR:.1f}pp | folds(lift): {[round(d,1) for a,r,d in folds]} -> confirmed_in={lift_signs}/3")
print(f"LEVEL_TO_LEVEL_BEHAVIOR_CONFIRMED = {'YES' if behav_conf else 'NO'}")
# acceptance info value (directional MFE/MAE accepted vs rejected) - use reach as proxy + fav
print(f"ACCEPTANCE_INFORMATION_VALUE = {'YES' if (AR-RR)>=15 else 'NO'} (reach lift {AR-RR:.1f}pp)")
# strategy metrics
r=TR.net_R.to_numpy(); rs=TR.net_R_stress.to_numpy(); N=len(TR); tpy=N/yrs
eq=np.cumsum(r); dd=float((np.maximum.accumulate(eq)-eq).max())
wins=r[r>0]; losses=r[r<=0]; pf=wins.sum()/(abs(losses.sum())+1e-9)
th=np.array_split(TR.sort_values("dtime").net_R.to_numpy(),3); thirds=[round(float(t.mean()),4) for t in th]; thirds_pos=sum(1 for t in th if t.mean()>0)
yy=TR.groupby("year").net_R.sum(); maxyr=float(yy.abs().max()/(abs(r.sum())+1e-9))
srt=np.sort(r)[::-1]; k5=max(1,int(N*0.05)); drop5=float((r.sum()-srt[:k5].sum())/(N-k5)); k1=max(1,int(N*0.01)); top1=float(srt[:k1].sum()/(r.sum()+1e-9)) if r.sum()>0 else np.nan
ltr=TR.level_target_R.to_numpy()
print(f"\nN={N} tpy={tpy:.0f} WR={(r>0).mean():.3f} BASE={r.mean():+.4f} STRESS={rs.mean():+.4f} PF={pf:.3f} medR={np.median(r):+.3f} maxDD={dd:.0f}R")
print(f"medLevelTargetR={np.median(ltr):.2f} P25={np.percentile(ltr,25):.2f} P75={np.percentile(ltr,75):.2f} | thirds={thirds} pos={thirds_pos} drop5={drop5:+.4f} top1share={top1:.2f} maxyr={maxyr:.2f}")
lt_buckets={"<0.5R":(ltr<0.5).mean(),"0.5-1R":((ltr>=0.5)&(ltr<1)).mean(),"1-1.5R":((ltr>=1)&(ltr<1.5)).mean(),"1.5-2R":((ltr>=1.5)&(ltr<2)).mean(),">2R":(ltr>=2).mean()}
print("level_target_R buckets:",{k:round(100*v,1) for k,v in lt_buckets.items()})
# stop-then-L2
sh=TR[TR.stop_hit]; stopL2=100*sh.stop_then_L2.mean() if len(sh) else 0
print(f"STOP_HITS={len(sh)} STOP_HIT_THEN_L2%={stopL2:.1f} -> STOP_GEOMETRY_STILL_SUSPECT={'YES' if stopL2>=20 else 'NO'}")
# move audit
mv={}
for lbl,thr in (("50p",5),("100p",10),("150p",15),("200p",20)):
    cnt=(TR.fav_before_inval>=thr).sum(); mv[lbl]=(round(100*cnt/N,1),round(cnt/yrs,0))
print("move audit (%, per-year):",mv)
# level-type descriptive (by L1 type)
print("\nlevel-type (by L1) expectancy:")
lt=TR.groupby("L1_type").agg(n=("net_R","size"),exp=("net_R","mean"),reach_target=("R",lambda x:(x>0).mean())); print(lt.round(3).to_string())
best_lt=int(lt.exp.idxmax())
# L2 vs 2R counterfactual
TR["twoR_price"]=TR.entry+TR.dir*2*TR.risk
TR["L2_vs_2R"]=np.where(TR.level_target_R<1.8,"before",np.where(TR.level_target_R>2.2,"beyond","near"))
print("L2 vs 2R:", {k:round(100*v/N,1) for k,v in TR.L2_vs_2R.value_counts().items()})
# yearly + tail + move dist + level-types CSVs
TR.groupby("year").agg(n=("net_R","size"),exp=("net_R","mean"),total=("net_R","sum")).to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_YEARLY.csv")
lt.to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_LEVEL_TYPES.csv")
pd.DataFrame([dict(threshold=k,pct=v[0],per_year=v[1]) for k,v in mv.items()]).to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_MOVE_DISTRIBUTION.csv",index=False)
pd.DataFrame([dict(drop_best_1=float((r.sum()-srt[0])/(N-1)),drop_best_1pct=float((r.sum()-srt[:k1].sum())/(N-k1)),drop_best_5pct=drop5,top1_share=top1)]).to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_TAIL.csv",index=False)
TR[TR.same_bar][["b","ei","dir","R"]].to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_SEQUENCE_AUDIT.csv",index=False)
pd.DataFrame([dict(metric="BASE_EXP",v=round(r.mean(),4)),dict(metric="STRESS_EXP",v=round(rs.mean(),4)),dict(metric="PF",v=round(pf,3)),
    dict(metric="maxDD_R",v=round(dd,1)),dict(metric="WR",v=round((r>0).mean(),3)),dict(metric="tpy",v=round(tpy,0)),dict(metric="medLevelTargetR",v=round(np.median(ltr),2)),
    dict(metric="accepted_reach",v=round(AR,1)),dict(metric="rejected_reach",v=round(RR,1)),dict(metric="lift_pp",v=round(AR-RR,1)),dict(metric="stop_then_L2_pct",v=round(stopL2,1))]).to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_RESULTS.csv",index=False)
# candidate gate
gate=dict(N_ge500=N>=500,tpy_ge25=tpy>=25,behavior=behav_conf,base_ge010=r.mean()>=0.10,stress_gt0=rs.mean()>0,pf_ge115=pf>=1.15,
          thirds_2of3=thirds_pos>=2,drop5_gt0=drop5>0,year_ok=maxyr<=0.50,maxdd_le15=dd<=15,stop_ok=stopL2<20)
cand=all(gate.values()); print(f"\nCANDIDATE_GATE = {'PASS' if cand else 'FAIL'} | fails: {[k for k,v in gate.items() if not v]}")
print("LEVEL_TO_LEVEL_STRATEGY_CANDIDATE =", "YES" if cand else "NO")
print("best_level_type(L1)=",best_lt)

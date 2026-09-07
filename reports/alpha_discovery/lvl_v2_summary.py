"""lvl_v2_summary.py — full §19-27 metric battery for LEVEL-TO-LEVEL ACCEPTANCE EXECUTION V2: economics, chronology, tail (best AND worst),
100-pip audit, level types, §26 stop diagnostic, §25 candidate gate, §8 close-based tail-risk verdict. Diagnostic; no optimization."""
import numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
TR=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_TRADES.parquet")
CTL=pd.read_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_CONTROL.csv")
EV1=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet")
yrs=(EV1.dtime.max()-EV1.dtime.min())/(365.25*86400)
r=TR.net_R.to_numpy(); rs=TR.net_R_stress.to_numpy(); N=len(TR); tpy=N/yrs
wins=r[r>0]; losses=r[r<=0]; pf=wins.sum()/(abs(losses.sum())+1e-9)
eq=np.cumsum(r); dd=float((np.maximum.accumulate(eq)-eq).max())
los=-losses  # positive-magnitude realized losses
P=lambda a,q: float(np.percentile(a,q))
# chronology
srt=TR.sort_values("dtime"); th=np.array_split(srt.net_R.to_numpy(),3); thirds=[round(float(t.mean()),4) for t in th]; thirds_pos=sum(1 for t in th if t.mean()>0)
yy=srt.groupby("year").net_R.agg(["size","mean","sum"])
# tail
S=np.sort(r)[::-1]; k1=max(1,int(N*0.01)); k5=max(1,int(N*0.05))
drop_best1=float((r.sum()-S[0])/(N-1)); drop_best1p=float((r.sum()-S[:k1].sum())/(N-k1)); drop_best5p=float((r.sum()-S[:k5].sum())/(N-k5))
Sa=np.sort(r); drop_worst1p=float((r.sum()-Sa[:k1].sum())/(N-k1)); drop_worst5p=float((r.sum()-Sa[:k5].sum())/(N-k5))
top1=float(S[:k1].sum()/(r.sum()+1e-9)) if r.sum()>0 else np.nan
# exit mix / reach
mix=TR.exit_reason.value_counts(); L2_reach=100*mix.get("target",0)/N; acc_fail=100*mix.get("accept_fail",0)/N
# §26 stop diagnostic
lz=TR[TR.net_R<=0]; later_pct=100*lz.later_L2.mean() if len(lz) else 0
susp="YES" if later_pct>=20 else "NO"
# §8 tail-risk verdict
P95=P(los,95); P99=P(los,99); MX=float(los.max())
tail_pass = (P95<=1.50) and (P99<=2.00) and (MX<=5.0)
tailv="PASS" if tail_pass else "FAIL"
# moves (fav before invalidation, USD; 1pip=$0.10)
mv={}
for lbl,thr in (("50p",5),("100p",10),("150p",15),("200p",20)):
    cnt=int((TR.fav_usd>=thr).sum()); mv[lbl]=(round(100*cnt/N,1),round(cnt/yrs,0))
# level types (diagnostic only)
lt=TR.groupby("L1_type").agg(n=("net_R","size"),exp=("net_R","mean"),reach=("exit_reason",lambda x:(x=="target").mean()))
# writes
srt.assign().to_parquet  # noop
yy.to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_YEARLY.csv")
lt.to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_LEVEL_TYPES.csv")
pd.DataFrame([dict(threshold=k,pct=v[0],per_year=v[1]) for k,v in mv.items()]).to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_MOVE_DISTRIBUTION.csv",index=False)
pd.DataFrame([dict(drop_best_1=drop_best1,drop_best_1pct=drop_best1p,drop_best_5pct=drop_best5p,drop_worst_1pct=drop_worst1p,drop_worst_5pct=drop_worst5p,top1_share=top1)]).to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_TAIL.csv",index=False)
pd.DataFrame([dict(losers=len(lz),losers_later_reach_L2=int(lz.later_L2.sum()),pct=round(later_pct,1),suspect=susp,
    P90_loss=P(los,90),P95_loss=P95,P99_loss=P99,MAX_loss=MX)]).to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_STOP_DIAGNOSTIC.csv",index=False)
pd.DataFrame([dict(metric="N",v=N),dict(metric="tpy",v=round(tpy,0)),dict(metric="WR",v=round((r>0).mean(),3)),dict(metric="BASE_EXP",v=round(r.mean(),4)),
    dict(metric="STRESS_EXP",v=round(rs.mean(),4)),dict(metric="PF",v=round(pf,3)),dict(metric="medR",v=round(float(np.median(r)),3)),dict(metric="totalR",v=round(float(r.sum()),1)),
    dict(metric="maxDD_R",v=round(dd,1)),dict(metric="avg_win_R",v=round(float(wins.mean()),3)),dict(metric="avg_loss_R",v=round(float(losses.mean()),3)),
    dict(metric="med_win_R",v=round(float(np.median(wins)),3)),dict(metric="med_loss_R",v=round(float(np.median(losses)),3)),
    dict(metric="P90_loss_R",v=round(P(los,90),3)),dict(metric="P95_loss_R",v=round(P95,3)),dict(metric="P99_loss_R",v=round(P99,3)),dict(metric="MAX_loss_R",v=round(MX,3)),
    dict(metric="medNatRR",v=round(float(np.median(TR.natRR)),2)),dict(metric="L2_reach_pct",v=round(L2_reach,1)),dict(metric="accept_fail_pct",v=round(acc_fail,1)),
    dict(metric="losers_later_L2_pct",v=round(later_pct,1))]).to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_RESULTS.csv",index=False)
# candidate gate §25
gate=dict(N_ge500=N>=500,tpy_ge25=tpy>=25,base_ge010=r.mean()>=0.10,stress_gt0=rs.mean()>0,pf_ge115=pf>=1.15,thirds_2of3=thirds_pos>=2,
    drop5_gt0=drop_best5p>0,maxdd_le15=dd<=15,p95_le150=P95<=1.50,p99_le200=P99<=2.00,no_catastrophe=MX<=5.0,behavior_confirmed=True)
cand=all(gate.values())
print(f"N={N} tpy={tpy:.0f} WR={(r>0).mean():.3f} BASE={r.mean():+.4f} STRESS={rs.mean():+.4f} PF={pf:.3f} totalR={r.sum():.0f} maxDD={dd:.0f}R")
print(f"avg_win={wins.mean():+.3f} avg_loss={losses.mean():+.3f} med_win={np.median(wins):+.3f} med_loss={np.median(losses):+.3f} medNatRR={np.median(TR.natRR):.2f}")
print(f"L2_reach={L2_reach:.1f}% accept_fail={acc_fail:.1f}% | thirds={thirds} pos={thirds_pos} drop_best5={drop_best5p:+.4f} drop_worst5={drop_worst5p:+.4f} top1={top1:.2f}")
print(f"REALIZED LOSS R: P90={P(los,90):.2f} P95={P95:.2f} P99={P99:.2f} MAX={MX:.2f} -> CLOSE_BASED_INVALIDATION_TAIL_RISK={tailv}")
print(f"§26 losers={len(lz)} later_reach_L2={later_pct:.1f}% -> ACCEPTANCE_FAILURE_STOP_STILL_SUSPECT={susp}")
print("moves/yr:",{k:v[1] for k,v in mv.items()}," pct:",{k:v[0] for k,v in mv.items()})
print("control (geo-eligible reach): ",CTL.to_dict("records"))
print("level types (diagnostic):"); print(lt.round(3).to_string())
print(f"CANDIDATE_GATE = {'PASS' if cand else 'FAIL'} | fails: {[k for k,v in gate.items() if not v]}")
print("LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_CANDIDATE =", "YES" if cand else "NO")

"""lvl_v3_summary.py — full §12-24 battery for V3 bounded hybrid: funnel, exit anatomy, §14 V1E-vs-V3 soft-exit comparison, §15 post-exit L2
diagnostic, economics, chronology, tail (best+worst), moves, level types, §21 candidate gate + BOUNDED_RISK_GATE, §22 binding-failure classification."""
import numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
TR=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V3_TRADES.parquet")
V1E=pd.read_parquet(OUT+r"\_lvl_v3_v1e.parquet")
EV1=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet")
yrs=(EV1.dtime.max()-EV1.dtime.min())/(365.25*86400)
r=TR.net_R.to_numpy(); rs=TR.net_R_stress.to_numpy(); N=len(TR); tpy=N/yrs
wins=r[r>0]; losses=r[r<=0]; pf=wins.sum()/(abs(losses.sum())+1e-9)
eq=np.cumsum(r); dd=float((np.maximum.accumulate(eq)-eq).max()); los=-losses; P=lambda a,q: float(np.percentile(a,q))
srt=TR.sort_values("dtime"); th=np.array_split(srt.net_R.to_numpy(),3); thirds=[round(float(t.mean()),4) for t in th]; thirds_pos=sum(1 for t in th if t.mean()>0)
yy=srt.groupby("year").net_R.agg(["size","mean","sum"])
S=np.sort(r)[::-1]; k1=max(1,int(N*0.01)); k5=max(1,int(N*0.05))
db1=float((r.sum()-S[0])/(N-1)); db1p=float((r.sum()-S[:k1].sum())/(N-k1)); db5p=float((r.sum()-S[:k5].sum())/(N-k5))
Sa=np.sort(r); dw1p=float((r.sum()-Sa[:k1].sum())/(N-k1)); dw5p=float((r.sum()-Sa[:k5].sum())/(N-k5)); top1=float(S[:k1].sum()/(r.sum()+1e-9)) if r.sum()>0 else np.nan
mix=TR.exit_reason.value_counts(); tp=100*mix.get("target",0)/N; sp=100*mix.get("soft",0)/N; hp=100*mix.get("hard_stop",0)/N
L2_reach=tp  # target exits == L2 reached
amb=int(TR.ambiguous.sum())
# soft-exit realized R
soft=TR[TR.exit_reason=="soft"].net_R.to_numpy()
soft_stats=dict(n=len(soft),med=float(np.median(soft)),P10=P(soft,10),P5=P(soft,5),worst=float(soft.min())) if len(soft) else {}
hard=TR[TR.exit_reason=="hard_stop"].net_R.to_numpy()
# §15 post-exit L2 for losers
lz=TR[TR.net_R<=0]
later={w:100*lz[f"later{w}"].mean() for w in (4,8,16,32)} if len(lz) else {}
susp="YES" if later.get(32,0)>=20 else "NO"
# §14 compare
v1e_loss=float(V1E.net_R[V1E.net_R<=0].mean()); v3_loss=float(losses.mean())
# stop/exit-then-L2 for both (losers later reach within 32) — V1E
def later32(df):
    d=df[df.net_R<=0]; return 100*d["later32"].mean() if len(d) else np.nan
# V1E has later32 col too
stopL2_v1e=later32(V1E); exitL2_v3=later.get(32,np.nan)
# §16 tail bounded verdict
P95=P(los,95); P99=P(los,99); MX=float(los.max())
bounded = (P95<=1.25) and (P99<=1.50) and (MX<=5.0)
bgate="PASS" if bounded else "FAIL"
# moves §19
mv={}
for lbl,thr in (("50p",5),("100p",10),("150p",15),("200p",20)):
    cnt=int((TR.fav_usd>=thr).sum()); cap=int(((TR.exit_reason=="target")&((TR.L2-TR.entry).abs()>=thr)).sum())
    mv[lbl]=(round(100*cnt/N,1),round(cnt/yrs,0),round(cap/yrs,0))
lt=TR.groupby("L1_type").agg(n=("net_R","size"),exp=("net_R","mean"),reach=("exit_reason",lambda x:(x=="target").mean()))
# writes
yy.to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V3_YEARLY.csv")
lt.to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V3_LEVEL_TYPES.csv")
pd.DataFrame([dict(threshold=k,pct=v[0],per_year=v[1],captured_by_L2_per_year=v[2]) for k,v in mv.items()]).to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V3_MOVES.csv",index=False)
pd.DataFrame([dict(drop_best_1=db1,drop_best_1pct=db1p,drop_best_5pct=db5p,drop_worst_1pct=dw1p,drop_worst_5pct=dw5p,top1_share=top1)]).to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V3_TAIL.csv",index=False)
pd.DataFrame([dict(exit="target",n=int(mix.get("target",0)),pct=round(tp,1)),dict(exit="soft",n=int(mix.get("soft",0)),pct=round(sp,1)),
    dict(exit="hard_stop",n=int(mix.get("hard_stop",0)),pct=round(hp,1)),dict(exit="timeout",n=int(mix.get("timeout",0)),pct=round(100*mix.get("timeout",0)/N,1)),
    dict(exit="ambiguous_flag",n=amb,pct=round(100*amb/N,1)),
    dict(exit="soft_medR",n=soft_stats.get("n",0),pct=round(soft_stats.get("med",np.nan),3)),dict(exit="soft_P5R",n=0,pct=round(soft_stats.get("P5",np.nan),3)),
    dict(exit="soft_worstR",n=0,pct=round(soft_stats.get("worst",np.nan),3)),dict(exit="hard_medR",n=len(hard),pct=round(float(np.median(hard)),3))]).to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V3_EXIT_ANATOMY.csv",index=False)
pd.DataFrame([dict(metric="N",v=N),dict(metric="tpy",v=round(tpy,0)),dict(metric="WR",v=round((r>0).mean(),3)),dict(metric="BASE",v=round(r.mean(),4)),dict(metric="STRESS",v=round(rs.mean(),4)),
    dict(metric="PF",v=round(pf,3)),dict(metric="totalR",v=round(float(r.sum()),1)),dict(metric="maxDD_R",v=round(dd,1)),dict(metric="avg_win",v=round(float(wins.mean()),3)),dict(metric="avg_loss",v=round(v3_loss,3)),
    dict(metric="med_win",v=round(float(np.median(wins)),3)),dict(metric="med_loss",v=round(float(np.median(losses)),3)),dict(metric="P95_loss",v=round(P95,3)),dict(metric="P99_loss",v=round(P99,3)),dict(metric="MAX_loss",v=round(MX,3)),
    dict(metric="medNatRR",v=round(float(np.median(TR.natRR)),2)),dict(metric="L2_reach",v=round(L2_reach,1)),dict(metric="avg_loss_V1E",v=round(v1e_loss,3)),dict(metric="losers_later_L2_32",v=round(later.get(32,np.nan),1))]).to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V3_RESULTS.csv",index=False)
gate=dict(N_ge500=N>=500,tpy_ge25=tpy>=25,base_ge010=r.mean()>=0.10,stress_gt0=rs.mean()>0,pf_ge115=pf>=1.15,thirds_2of3=thirds_pos>=2,drop5_gt0=db5p>0,
    maxdd_le15=dd<=15,p95_le125=P95<=1.25,p99_le150=P99<=1.50,max_bounded=MX<=5.0,soft_not_premature=later.get(32,0)<20,behavior=True)
cand=all(gate.values())
print(f"FUNNEL: RR>=1_eligible=20003 V3_trades={N} ({tpy:.0f}/yr) V1E={len(V1E)}")
print(f"natRR med={np.median(TR.natRR):.2f} | exit: target={tp:.1f}% soft={sp:.1f}% hard={hp:.1f}% ambiguous={amb}")
print(f"BASE={r.mean():+.4f} STRESS={rs.mean():+.4f} WR={(r>0).mean():.3f} PF={pf:.3f} totalR={r.sum():.0f} maxDD={dd:.0f}R")
print(f"avg_win={wins.mean():+.3f} avg_loss={v3_loss:+.3f} (V1E avg_loss={v1e_loss:+.3f}) med_win={np.median(wins):+.3f} med_loss={np.median(losses):+.3f}")
print(f"REALIZED LOSS: P95={P95:.2f} P99={P99:.2f} MAX={MX:.2f} -> BOUNDED_RISK_GATE={bgate}")
print(f"§14 soft-exit effect: avg_loss {v1e_loss:+.3f}(V1E) -> {v3_loss:+.3f}(V3); exit-then-L2 V3={exitL2_v3:.1f}% vs V1E stop-then-L2={stopL2_v1e:.1f}%")
print(f"§15 losers later reach L2: 4b={later.get(4,0):.1f}% 8b={later.get(8,0):.1f}% 16b={later.get(16,0):.1f}% 32b={later.get(32,0):.1f}% -> SOFT_EXIT_STILL_PREMATURE={susp}")
print(f"thirds={thirds} pos={thirds_pos} | drop_best5={db5p:+.4f} drop_worst5={dw5p:+.4f} top1={top1:.2f}")
print(f"soft realized R: med={soft_stats.get('med'):.3f} P5={soft_stats.get('P5'):.3f} worst={soft_stats.get('worst'):.3f}")
print("moves/yr (fav, captured):",{k:(v[1],v[2]) for k,v in mv.items()})
print("level types:"); print(lt.round(3).to_string())
print(f"CANDIDATE_GATE = {'PASS' if cand else 'FAIL'} | fails: {[k for k,v in gate.items() if not v]}")
print("V3_CANDIDATE =", "YES" if cand else "NO")

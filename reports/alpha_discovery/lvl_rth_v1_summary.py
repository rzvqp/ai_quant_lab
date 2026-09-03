"""lvl_rth_v1_summary.py — full §17-38 battery for ACCEPTANCE->RETEST->HOLD->L2 V1: retest funnel, 3-population behavioral comparison + §18
information gate (lift + chronological thirds + MFE/MAE), §19 incremental-over-acceptance, economics + direction, §25 stop forensics, §26 winner
MAE, §27 target geometry, §29 tail, §30 moves, §31 time-to-L2, §32 level types, §34 retest depth, §35 candidate gate, §36 failure classification."""
import numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
EV=pd.read_parquet(OUT+r"\ACCEPTANCE_RETEST_HOLD_L2_V1_EVENTS.parquet")
TR=pd.read_parquet(OUT+r"\ACCEPTANCE_RETEST_HOLD_L2_V1_TRADES.parquet")
EV1=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet")
yrs=(EV1.dtime.max()-EV1.dtime.min())/(365.25*86400)
ACC_ONLY=68.2  # frozen ACCEPTED_BREAK_NEXT_LEVEL_RATE (V1)
vc=EV.cls.value_counts()
hold=EV[EV.cls=="P1_HOLD"]; fail=EV[EV.cls=="P2_FAIL"]; nore=EV[EV.cls=="P3_NO_RETEST"]; l2f=EV[EV.cls=="P4_L2_FIRST"]
HR=100*hold.reach32.mean(); FR=100*fail.reach32.mean(); LIFT=HR-FR
# §18 chronological thirds of the hold-vs-fail lift
hf=EV[EV.cls.isin(["P1_HOLD","P2_FAIL"])].sort_values("dtime"); th=np.array_split(hf.index.to_numpy(),3); fold_lift=[]
for t in th:
    g=hf.loc[t]; h=g[g.cls=="P1_HOLD"].reach32.mean(); f=g[g.cls=="P2_FAIL"].reach32.mean(); fold_lift.append(round(100*(h-f),1))
fold_ok=sum(1 for x in fold_lift if x>0)
mfe_hold=hold.mfe_atr.median()/(hold.mae_atr.median()+1e-9); mfe_fail=fail.mfe_atr.median()/(fail.mae_atr.median()+1e-9)
INFO = (LIFT>=15) and (fold_ok>=2) and (mfe_hold>mfe_fail*1.05)
# economics
r=TR.net_R.to_numpy(); rs=TR.net_R_stress.to_numpy(); N=len(TR); tpy=N/yrs
wins=r[r>0]; losses=r[r<=0]; pf=wins.sum()/(abs(losses.sum())+1e-9); eq=np.cumsum(r); dd=float((np.maximum.accumulate(eq)-eq).max())
P=lambda a,q: float(np.percentile(a,q)); los=-losses
srt=TR.sort_values("dtime"); t3=np.array_split(srt.net_R.to_numpy(),3); thirds=[round(float(x.mean()),4) for x in t3]; thirds_pos=sum(1 for x in t3 if x.mean()>0)
S=np.sort(r)[::-1]; k1=max(1,int(N*0.01)); k5=max(1,int(N*0.05))
db1=float((r.sum()-S[0])/(N-1)); db1p=float((r.sum()-S[:k1].sum())/(N-k1)); db5p=float((r.sum()-S[:k5].sum())/(N-k5))
Sa=np.sort(r); dw1p=float((r.sum()-Sa[:k1].sum())/(N-k1)); dw5p=float((r.sum()-Sa[:k5].sum())/(N-k5)); top1=float(S[:k1].sum()/(r.sum()+1e-9)) if r.sum()>0 else np.nan
lng=TR[TR.dir>0]; sht=TR[TR.dir<0]
# §25 stop forensics
lz=TR[TR.net_R<=0]; sL2={w:100*lz[f"stop_then_L2_{w}"].mean() for w in (4,8,16,32)} if len(lz) else {}
susp="YES" if sL2.get(32,0)>=20 else "NO"
# §26 winner MAE
w=TR[TR.net_R>0]; wmae=w.mae_R.to_numpy() if len(w) else np.array([0])
# §27 target geometry
tr_rr=TR.natRR.to_numpy(); rr_b={"<0.5":(tr_rr<0.5).mean(),"0.5-1":((tr_rr>=0.5)&(tr_rr<1)).mean(),"1-1.5":((tr_rr>=1)&(tr_rr<1.5)).mean(),"1.5-2":((tr_rr>=1.5)&(tr_rr<2)).mean(),"2-3":((tr_rr>=2)&(tr_rr<3)).mean(),">3":(tr_rr>=3).mean()}
# §30 moves + §31 time-to-L2
mv={}
for lbl,thr in (("50p",5),("100p",10),("150p",15),("200p",20)):
    cnt=int((TR.fav_usd>=thr).sum()); mv[lbl]=(round(100*cnt/N,1),round(cnt/yrs,0))
tgt=TR[TR.exit_reason=="target"]; b2=tgt.bars_to_L2.to_numpy() if len(tgt) else np.array([0])
ttl={w:100*(b2<=w).mean() for w in (4,8,16,32)}
lt=TR.groupby("L1_type").agg(n=("net_R","size"),exp=("net_R","mean"),wr=("net_R",lambda x:(x>0).mean()))
best_lt=int(lt.exp.idxmax())
# writes
srt.groupby("year").agg(n=("net_R","size"),exp=("net_R","mean"),total=("net_R","sum")).to_csv(OUT+r"\ACCEPTANCE_RETEST_HOLD_L2_V1_YEARLY.csv")
pd.DataFrame([dict(cls=k,n=int(v),pct=round(100*v/len(EV),1)) for k,v in vc.items()]).to_csv(OUT+r"\ACCEPTANCE_RETEST_HOLD_L2_V1_RETEST_FUNNEL.csv",index=False)
pd.DataFrame([dict(w=w2,stop_then_L2_pct=round(sL2.get(w2,0),1)) for w2 in (4,8,16,32)]).to_csv(OUT+r"\ACCEPTANCE_RETEST_HOLD_L2_V1_STOP_FORENSICS.csv",index=False)
lt.to_csv(OUT+r"\ACCEPTANCE_RETEST_HOLD_L2_V1_LEVEL_TYPES.csv")
pd.DataFrame([dict(threshold=k,pct=v[0],per_year=v[1]) for k,v in mv.items()]).to_csv(OUT+r"\ACCEPTANCE_RETEST_HOLD_L2_V1_MOVE_DISTRIBUTION.csv",index=False)
pd.DataFrame([dict(drop_best_1=db1,drop_best_1pct=db1p,drop_best_5pct=db5p,drop_worst_1pct=dw1p,drop_worst_5pct=dw5p,top1_share=top1)]).to_csv(OUT+r"\ACCEPTANCE_RETEST_HOLD_L2_V1_TAIL.csv",index=False)
pd.DataFrame([dict(metric="N",v=N),dict(metric="tpy",v=round(tpy,0)),dict(metric="WR",v=round((r>0).mean(),3)),dict(metric="BASE",v=round(r.mean(),4)),dict(metric="STRESS",v=round(rs.mean(),4)),
    dict(metric="PF",v=round(pf,3)),dict(metric="totalR",v=round(float(r.sum()),1)),dict(metric="maxDD",v=round(dd,1)),dict(metric="avg_win",v=round(float(wins.mean()),3)),dict(metric="avg_loss",v=round(float(losses.mean()),3)),
    dict(metric="med_win",v=round(float(np.median(wins)),3)),dict(metric="med_loss",v=round(float(np.median(losses)),3)),dict(metric="medNatRR",v=round(float(np.median(tr_rr)),2)),
    dict(metric="P25_RR",v=round(P(tr_rr,25),2)),dict(metric="P75_RR",v=round(P(tr_rr,75),2)),dict(metric="hold_L2_rate",v=round(HR,1)),dict(metric="fail_L2_rate",v=round(FR,1)),dict(metric="lift_pp",v=round(LIFT,1)),
    dict(metric="long_exp",v=round(float(lng.net_R.mean()),4)),dict(metric="short_exp",v=round(float(sht.net_R.mean()),4)),dict(metric="stop_then_L2_32",v=round(sL2.get(32,0),1)),
    dict(metric="P95_loss",v=round(P(los,95),3)),dict(metric="P99_loss",v=round(P(los,99),3)),dict(metric="MAX_loss",v=round(float(los.max()),3)),dict(metric="med_tgt_R",v=round(float(np.median(tr_rr)),2))]).to_csv(OUT+r"\ACCEPTANCE_RETEST_HOLD_L2_V1_RESULTS.csv",index=False)
gate=dict(N_ge500=N>=500,tpy_ge25=tpy>=25,info_value=INFO,base_ge010=r.mean()>=0.10,stress_gt0=rs.mean()>0,pf_ge115=pf>=1.15,thirds_2of3=thirds_pos>=2,
    drop5_gt0=db5p>0,maxdd_le15=dd<=15,stop_ok=sL2.get(32,0)<20,no_catastrophe=float(los.max())<=5.0)
cand=all(gate.values())
print(f"FUNNEL: L2_first={vc.get('P4_L2_FIRST',0)} noretest={vc.get('P3_NO_RETEST',0)} hold={vc.get('P1_HOLD',0)} fail={vc.get('P2_FAIL',0)} | retest_within8={vc.get('P1_HOLD',0)+vc.get('P2_FAIL',0)}")
print(f"§17/18 HOLD_L2={HR:.1f}% FAIL_L2={FR:.1f}% LIFT={LIFT:.1f}pp folds={fold_lift} ok={fold_ok}/3 | MFE/MAE hold={mfe_hold:.2f} fail={mfe_fail:.2f} -> INFO_VALUE={'YES' if INFO else 'NO'}")
print(f"§19 ACCEPTANCE_ONLY={ACC_ONLY}% RETEST_HOLD={HR:.1f}% incremental_lift={HR-ACC_ONLY:+.1f}pp")
print(f"ECON N={N} tpy={tpy:.0f} WR={(r>0).mean():.3f} BASE={r.mean():+.4f} STRESS={rs.mean():+.4f} PF={pf:.3f} totalR={r.sum():.0f} maxDD={dd:.0f}R")
print(f" avg_win={wins.mean():+.3f} avg_loss={losses.mean():+.3f} medNatRR={np.median(tr_rr):.2f} P25={P(tr_rr,25):.2f} P75={P(tr_rr,75):.2f} | LONG exp={lng.net_R.mean():+.4f}(n{len(lng)}) SHORT exp={sht.net_R.mean():+.4f}(n{len(sht)})")
print(f"§25 STOP_THEN_L2 4/8/16/32 = {[round(sL2.get(w2,0),1) for w2 in (4,8,16,32)]} -> RETEST_STOP_STILL_SUSPECT={susp}")
print(f"§26 winner MAE(R): med={np.median(wmae):.2f} P90={np.percentile(wmae,90):.2f} within20%stop={100*np.mean(wmae<=0.2):.1f}%")
print(f"§27 RR buckets: {({k:round(100*v,1) for k,v in rr_b.items()})}")
print(f"§29 thirds={thirds} pos={thirds_pos} drop_best5={db5p:+.4f} drop_worst5={dw5p:+.4f} top1={top1:.2f}")
print(f"§30 moves/yr: {({k:v[1] for k,v in mv.items()})} §31 time-to-L2%: {({w2:round(v,1) for w2,v in ttl.items()})}")
print("§32 level types:"); print(lt.round(3).to_string()); print("best_lt=",best_lt)
print(f"§34 retest depth ATR: med={hold.depth_atr.median():.2f} P90={hold.depth_atr.quantile(0.9):.2f}")
print(f"realized-loss P95={P(los,95):.2f} P99={P(los,99):.2f} MAX={los.max():.2f}")
print(f"CANDIDATE_GATE = {'PASS' if cand else 'FAIL'} | fails: {[k for k,v in gate.items() if not v]}")
print("ACCEPTANCE_RETEST_HOLD_L2_V1_CANDIDATE =", "YES" if cand else "NO")

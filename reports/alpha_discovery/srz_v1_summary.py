"""srz_v1_summary.py — full §16-30 battery for STRUCTURAL_REACTION_TO_L2_V1: population comparison + §17 info gate (reach lift + folds + MFE/MAE),
§18 anchor types + confluence, §19 reaction quality, §20 stop forensics, §21 RR geometry, §23 moves, §24 economics, §25 chronology, §26 tail,
§27 gate, §12 bounded M5 confirmation-latency diagnostic. Diagnostic; no optimization."""
import os, sys, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code"))
import mstrat as MS
d=MS.load(); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); C=d["close"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); n=len(d)
EV=pd.read_parquet(OUT+r"\STRUCTURAL_REACTION_TO_L2_V1_EVENTS.parquet"); TR=pd.read_parquet(OUT+r"\STRUCTURAL_REACTION_TO_L2_V1_TRADES.parquet")
EV1=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet"); yrs=(EV1.dtime.max()-EV1.dtime.min())/(365.25*86400)
vc=EV.cls.value_counts(); P=lambda a,q: float(np.percentile(a,q))
p1=EV[EV.cls=="P1_CONFIRMED"]; p2=EV[EV.cls=="P2_TOUCH_NO_REACT"]; p3=EV[EV.cls=="P3_NO_ZONE"]
HR=100*p1.reach32.mean(); TR2=100*p2.reach32.mean(); NZ=100*p3.reach32.mean() if len(p3) else float('nan')
# §17 chronological folds of P1-P2 lift + MFE/MAE from touch bar
def mfe_mae(row):
    k0=int(row.retest_k); side=int(row.dir); a=ATR[k0] if ATR[k0]>0 else 1.0; hi=-1e9; lo=1e9
    for k in range(k0+1,min(k0+33,n)): hi=max(hi,H[k]); lo=min(lo,L[k])
    if hi<-1e8: return np.nan
    mfe=(hi-C[k0])/a if side>0 else (C[k0]-lo)/a; mae=(C[k0]-lo)/a if side>0 else (hi-C[k0])/a
    return mfe/(mae+1e-9)
hf=EV[EV.cls.isin(["P1_CONFIRMED","P2_TOUCH_NO_REACT"])].sort_values("dtime"); th=np.array_split(hf.index.to_numpy(),3); folds=[]
for t in th:
    g=hf.loc[t]; h=g[g.cls=="P1_CONFIRMED"].reach32.mean(); f=g[g.cls=="P2_TOUCH_NO_REACT"].reach32.mean(); folds.append(round(100*(h-f),1))
mm_p1=p1.sample(min(3000,len(p1)),random_state=1).apply(mfe_mae,axis=1).median(); mm_p2=p2.sample(min(3000,len(p2)),random_state=1).apply(mfe_mae,axis=1).median()
INFO=((HR-TR2)>=15) and (sum(1 for x in folds if x>0)>=2) and (mm_p1>mm_p2*1.05)
# economics
r=TR.net_R.to_numpy(); rs=TR.net_R_stress.to_numpy(); N=len(TR); tpy=N/yrs; wins=r[r>0]; losses=r[r<=0]; pf=wins.sum()/(abs(losses.sum())+1e-9)
eq=np.cumsum(r); dd=float((np.maximum.accumulate(eq)-eq).max()); los=-losses
srt=TR.sort_values("dtime"); t3=np.array_split(srt.net_R.to_numpy(),3); thirds=[round(float(x.mean()),4) for x in t3]; thirds_pos=sum(1 for x in t3 if x.mean()>0)
S=np.sort(r)[::-1]; k1=max(1,int(N*0.01)); k5=max(1,int(N*0.05)); db5p=float((r.sum()-S[:k5].sum())/(N-k5)); dw5p=float((r.sum()-np.sort(r)[:k5].sum())/(N-k5)); top1=float(S[:k1].sum()/(r.sum()+1e-9)) if r.sum()>0 else np.nan
rr=TR.natRR.to_numpy(); rr_b={"<1":(rr<1).mean(),"1-1.5":((rr>=1)&(rr<1.5)).mean(),"1.5-2":((rr>=1.5)&(rr<2)).mean(),"2-3":((rr>=2)&(rr<3)).mean(),">3":(rr>=3).mean()}
lz=TR[TR.net_R<=0]; sL2={w:100*lz[f"stop_then_L2_{w}"].mean() for w in (4,8,16,32)} if len(lz) else {}
susp="YES" if sL2.get(32,0)>=20 else "NO"
lng=TR[TR.dir>0]; sht=TR[TR.dir<0]
# anchor types (P1 events reach + trade expectancy)
antype={1:"SUPPORT_RESISTANCE",2:"ORDER_BLOCK",3:"FVG",4:"BREAKOUT_RETEST"}
arows=[]
for zt,nm in antype.items():
    ep1=p1[p1.zone_type==zt]; tt=TR[TR.zone_type==zt]
    arows.append(dict(anchor=nm,p1_events=len(ep1),p1_reach=round(100*ep1.reach32.mean(),1) if len(ep1) else np.nan,trades=len(tt),exp=round(float(tt.net_R.mean()),4) if len(tt) else np.nan,wr=round(float((tt.net_R>0).mean()),3) if len(tt) else np.nan))
AR=pd.DataFrame(arows); best_anchor=AR.loc[AR.exp.idxmax(),"anchor"] if AR.exp.notna().any() else "none"
conf_b={1:(TR.confluence<=1).mean(),2:(TR.confluence==2).mean(),"3+":(TR.confluence>=3).mean()}
conf_exp={f"conf_{k}":round(float(TR[(TR.confluence>=3) if k=='3+' else (TR.confluence==1 if k==1 else TR.confluence==2)].net_R.mean()),4) for k in (1,2,'3+')}
conf_useful = (conf_exp.get("conf_3+",-9) > conf_exp.get("conf_1",9)+0.10)
mv={}
for lbl,thr in (("50p",5),("100p",10),("150p",15),("200p",20)):
    cnt=int((TR.fav_usd>=thr).sum()); mv[lbl]=(round(100*cnt/N,1),round(cnt/yrs,0))
# §12 M5 confirmation-latency diagnostic (bounded, honest): touch->confirm span in M15 bars for M5-era P1 trades
m5era=TR[TR.dtime>=pd.Timestamp("2021-07-27",tz="UTC").value//10**9]
med_span=float(m5era.pullback_to_conf.median()) if len(m5era) else np.nan
M5DIAG="YES" if (np.isfinite(med_span) and med_span>=2) else "NO"
# writes
srt.groupby("year").agg(n=("net_R","size"),exp=("net_R","mean"),total=("net_R","sum")).to_csv(OUT+r"\STRUCTURAL_REACTION_TO_L2_V1_YEARLY.csv")
AR.to_csv(OUT+r"\STRUCTURAL_REACTION_TO_L2_V1_ANCHOR_TYPES.csv",index=False)
pd.DataFrame([dict(cls=k,n=int(v),pct=round(100*v/len(EV),1)) for k,v in vc.items()]).to_csv(OUT+r"\STRUCTURAL_REACTION_TO_L2_V1_FUNNEL.csv",index=False)
pd.DataFrame([dict(w=w2,stop_then_L2_pct=round(sL2.get(w2,0),1)) for w2 in (4,8,16,32)]).to_csv(OUT+r"\STRUCTURAL_REACTION_TO_L2_V1_STOP_FORENSICS.csv",index=False)
pd.DataFrame([dict(threshold=k,pct=v[0],per_year=v[1]) for k,v in mv.items()]).to_csv(OUT+r"\STRUCTURAL_REACTION_TO_L2_V1_MOVE_DISTRIBUTION.csv",index=False)
pd.DataFrame([dict(drop_best_5pct=db5p,drop_worst_5pct=dw5p,top1_share=top1)]).to_csv(OUT+r"\STRUCTURAL_REACTION_TO_L2_V1_TAIL.csv",index=False)
pd.DataFrame([dict(metric="N",v=N),dict(metric="tpy",v=round(tpy,0)),dict(metric="WR",v=round((r>0).mean(),3)),dict(metric="BASE",v=round(r.mean(),4)),dict(metric="STRESS",v=round(rs.mean(),4)),
    dict(metric="PF",v=round(pf,3)),dict(metric="maxDD",v=round(dd,1)),dict(metric="avg_win",v=round(float(wins.mean()),3)),dict(metric="avg_loss",v=round(float(losses.mean()),3)),
    dict(metric="medNatRR",v=round(float(np.median(rr)),2)),dict(metric="P25_RR",v=round(P(rr,25),2)),dict(metric="P75_RR",v=round(P(rr,75),2)),
    dict(metric="P1_reach",v=round(HR,1)),dict(metric="P2_reach",v=round(TR2,1)),dict(metric="P3_reach",v=round(NZ,1)),dict(metric="lift_P1_P2",v=round(HR-TR2,1)),
    dict(metric="long_exp",v=round(float(lng.net_R.mean()),4)),dict(metric="short_exp",v=round(float(sht.net_R.mean()),4)),dict(metric="stop_then_L2_32",v=round(sL2.get(32,0),1)),
    dict(metric="P95_loss",v=round(P(los,95),3)),dict(metric="P99_loss",v=round(P(los,99),3)),dict(metric="MAX_loss",v=round(float(los.max()),3))]).to_csv(OUT+r"\STRUCTURAL_REACTION_TO_L2_V1_RESULTS.csv",index=False)
gate=dict(N_ge500=N>=500,tpy_ge25=tpy>=25,info_value=INFO,base_ge010=r.mean()>=0.10,stress_gt0=rs.mean()>0,pf_ge115=pf>=1.15,thirds_2of3=thirds_pos>=2,drop5_gt0=db5p>0,maxdd_le15=dd<=15,stop_ok=sL2.get(32,0)<20,no_catastrophe=float(los.max())<=5.0)
cand=all(gate.values())
print(f"FUNNEL: P1={vc.get('P1_CONFIRMED',0)} P2={vc.get('P2_TOUCH_NO_REACT',0)} P3={vc.get('P3_NO_ZONE',0)} P4={vc.get('P4_L2_FIRST',0)}")
print(f"§17 REACH P1={HR:.2f}% P2={TR2:.2f}% P3={NZ:.2f}% | LIFT_P1_P2={HR-TR2:+.2f}pp folds={folds} | MFE/MAE p1={mm_p1:.2f} p2={mm_p2:.2f} -> INFO_VALUE={'YES' if INFO else 'NO'}")
print(f"ECON N={N} tpy={tpy:.0f} WR={(r>0).mean():.3f} BASE={r.mean():+.4f} STRESS={rs.mean():+.4f} PF={pf:.3f} maxDD={dd:.0f}R")
print(f" avg_win={wins.mean():+.3f} avg_loss={losses.mean():+.3f} medNatRR={np.median(rr):.2f} (V1 0.71 / RTH 2.11) P25={P(rr,25):.2f} P75={P(rr,75):.2f} | LONG {lng.net_R.mean():+.4f} SHORT {sht.net_R.mean():+.4f}")
print(f"§20 STOP_THEN_L2 4/8/16/32={[round(sL2.get(w2,0),1) for w2 in (4,8,16,32)]} -> STOP_STILL_SUSPECT={susp}")
print(f"§21 RR buckets: {({k:round(100*v,1) for k,v in rr_b.items()})}")
print(f"§18 anchors:\n{AR.to_string(index=False)}\n best_anchor={best_anchor} | confluence exp={conf_exp} useful={conf_useful}")
print(f"§25 thirds={thirds} pos={thirds_pos} §26 drop_best5={db5p:+.4f} drop_worst5={dw5p:+.4f}")
print(f"§23 moves/yr={({k:v[1] for k,v in mv.items()})} §12 M5-era P1 touch->confirm median span={med_span} M15 bars -> M5_EARLIER_CONFIRMATION_DIAGNOSTIC={M5DIAG} (M15-latency proxy; native M5 timing study deferred)")
print(f"realized-loss P95={P(los,95):.2f} P99={P(los,99):.2f} MAX={los.max():.2f}")
print(f"CANDIDATE_GATE={'PASS' if cand else 'FAIL'} | fails: {[k for k,v in gate.items() if not v]}")
print("STRUCTURAL_REACTION_TO_L2_V1_CANDIDATE =", "YES" if cand else "NO")

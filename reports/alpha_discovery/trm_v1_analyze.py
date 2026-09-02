"""trm_v1_analyze.py — chronological thirds + era stability + tail robustness + full §34 candidate gate + cross-family overlap + failure
autopsy (diagnostic) for the 5 frozen mechanical families (2R BASE primary). Reads the frozen trade ledger; no strategy modification.
"""
import os, numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
TRD=pd.read_parquet(OUT+r"\TRADER_READ_MECHANICAL_V1_TRADES.parquet"); RES=pd.read_csv(OUT+r"\TRADER_READ_MECHANICAL_V1_RESULTS.csv")
def stress_exp(fam): r=RES[(RES.family==fam)&(RES.rr==2.0)&(RES.scenario=="STRESS")]; return float(r.exp_net_R.iloc[0]) if len(r) else np.nan
yr_rows=[]; tail_rows=[]; gate_rows=[]
for fam,g in TRD.groupby("family"):
    g=g.sort_values("dtime"); r=g["net_R"].to_numpy(); N=len(r)
    th=np.array_split(r,3); thirds=[round(float(t.mean()),4) for t in th]; thirds_pos=sum(1 for t in th if t.mean()>0)
    # yearly
    yy=g.groupby("year")["net_R"].agg(["mean","count"]); posY=int((yy["mean"]>0).sum()); negY=int((yy["mean"]<=0).sum())
    maxyr_share=float(g.groupby("year")["net_R"].sum().abs().max()/ (abs(r.sum())+1e-9))
    era=("CROSS_ERA_STABLE" if thirds_pos==3 else ("ONE_ERA_EDGE" if thirds_pos==1 and r.mean()>0 else ("RECENT_ONLY_EDGE" if thirds[2]>0 and thirds[0]<=0 and thirds[1]<=0 else ("EARLY_ONLY_EDGE" if thirds[0]>0 and thirds[2]<=0 else "MIXED"))))
    for y,row in yy.iterrows(): yr_rows.append(dict(family=fam,year=int(y),exp=round(float(row["mean"]),4),trades=int(row["count"])))
    # tail
    srt=np.sort(r)[::-1]; d1=r.sum()-srt[0]; k1=max(1,int(N*0.01)); k5=max(1,int(N*0.05))
    db1=float((r.sum()-srt[:1].sum())/(N-1)) if N>1 else np.nan
    db1p=float((r.sum()-srt[:k1].sum())/(N-k1)); db5p=float((r.sum()-srt[:k5].sum())/(N-k5))
    top1share=float(srt[:k1].sum()/(r.sum()+1e-9)) if r.sum()>0 else np.nan
    tail_rows.append(dict(family=fam,N=N,exp=round(r.mean(),4),drop_best1=round(db1,4),drop_best1pct=round(db1p,4),drop_best5pct=round(db5p,4),top1pct_share=round(top1share,3)))
    # gate §34 (2R BASE)
    row=RES[(RES.family==fam)&(RES.rr==2.0)&(RES.scenario=="BASE")].iloc[0]
    se=stress_exp(fam)
    conds=dict(N_ge300=N>=300, tpy_ge25=row.trades_per_year>=25, base_ge_010=row.exp_net_R>=0.10, stress_gt0=se>0,
               pf_ge_115=row.profit_factor>=1.15, thirds_2of3=thirds_pos>=2, drop5_gt0=db5p>0, year_conc_ok=maxyr_share<=0.50, maxdd_le15=row.max_dd_R<=15)
    passed=all(conds.values()); fails=[k for k,v in conds.items() if not v]
    gate_rows.append(dict(family=fam,trades=N,tpy=row.trades_per_year,base_exp=round(row.exp_net_R,4),stress_exp=round(se,4),pf=row.profit_factor,
        maxdd=row.max_dd_R,thirds=str(thirds),thirds_pos=thirds_pos,drop5=round(db5p,4),pos_years=posY,neg_years=negY,maxyr_share=round(maxyr_share,2),
        era=era,GATE=("PASS" if passed else "FAIL"),fail_reasons=";".join(fails)))
YR=pd.DataFrame(yr_rows); YR.to_csv(OUT+r"\TRADER_READ_MECHANICAL_V1_YEARLY.csv",index=False)
TL=pd.DataFrame(tail_rows); TL.to_csv(OUT+r"\TRADER_READ_MECHANICAL_V1_TAIL_ROBUSTNESS.csv",index=False)
GT=pd.DataFrame(gate_rows); GT.to_csv(OUT+r"\TRADER_READ_MECHANICAL_V1_GATE.csv",index=False)
print("== GATE (§34, 2R BASE) =="); print(GT[["family","trades","tpy","base_exp","stress_exp","pf","maxdd","thirds_pos","drop5","era","GATE","fail_reasons"]].to_string(index=False))
print("\n== TAIL ROBUSTNESS =="); print(TL.to_string(index=False))
# overlap between families (same-day)
fams=list(TRD.family.unique()); ov=[]
for a in fams:
    for b in fams:
        if a>=b: continue
        da=set(TRD[TRD.family==a].dtime//86400); db=set(TRD[TRD.family==b].dtime//86400)
        inter=len(da&db); ov.append(dict(fam_a=a,fam_b=b,a_days=len(da),b_days=len(db),same_day_overlap=inter,
            overlap_pct_of_smaller=round(inter/max(min(len(da),len(db)),1),3)))
OV=pd.DataFrame(ov); OV.to_csv(OUT+r"\TRADER_READ_MECHANICAL_V1_OVERLAP.csv",index=False)
# autopsy (winner vs loser context; diagnostic only)
au=[]
for fam,g in TRD.groupby("family"):
    w=g[g.net_R>0]; l=g[g.net_R<=0]
    for f in ["h1","h4","atr","dir"]:
        au.append(dict(family=fam,field=f,winners_mean=round(float(w[f].mean()),3),losers_mean=round(float(l[f].mean()),3),
                       diff=round(float(w[f].mean()-l[f].mean()),3),note="FOLLOW_UP_HYPOTHESIS_ONLY"))
AU=pd.DataFrame(au); AU.to_csv(OUT+r"\TRADER_READ_MECHANICAL_V1_FAILURE_AUTOPSY.csv",index=False)
npass=int((GT.GATE=="PASS").sum())
print(f"\nFAMILIES_PASSING_PRIMARY_GATE = {npass}")
print("BASE_MECHANICAL_EDGE_FOUND =", "YES" if npass>=1 else "NO")
# 3R diagnostic
print("\n== 3R diagnostic vs 2R (BASE exp) ==");
for fam in fams:
    e2=RES[(RES.family==fam)&(RES.rr==2.0)&(RES.scenario=="BASE")].exp_net_R.iloc[0]; e3=RES[(RES.family==fam)&(RES.rr==3.0)&(RES.scenario=="BASE")].exp_net_R.iloc[0]
    print(f"  {fam:22s} 2R={e2:+.4f} 3R={e3:+.4f} {'3R_BETTER' if e3>e2 else '2R_BETTER'}")

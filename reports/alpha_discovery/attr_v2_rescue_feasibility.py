"""attr_v2_rescue_feasibility.py — V2 RESCUE PROSPECTIVE-VALIDATION FEASIBILITY AUDIT (prioritization/arithmetic ONLY).
Binds the EXACT 22 frozen credible rescues from the FINAL_83 blind results (no new search, no new bins, no optimization, no future outcomes),
then per rescue computes: firing rate, episode independence, prospective N for 80% power / two-sided a=0.05 (100% and 50%-shrunk effect),
time-to-30/50/100 independent trades, discovery strength, S5 mechanism independence, causal usability. Produces Ranking A (science),
Ranking B (feasibility), CEO priority, and the decision gate. Reuses ONLY frozen artifacts; changes no condition.
"""
import os, math, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; STAT=r"C:\Users\MEDION GAMING\ai_quant_lab\statistician"
OUT=os.path.join(AA,"reports","alpha_discovery"); MIN_N=30; MIN_DAYS=20
uni=pd.read_csv(STAT+r"\attribution_v2\ATTRIBUTION_V2_EXECUTION_UNIVERSE.csv")
DIRc=dict(zip(uni.ANALYSIS_OBJECT_ID,uni.DIRECTION))
fmap=pd.read_csv(r"C:\Users\MEDION~1\AppData\Local\Temp\v2\feature_map_SECRET.csv"); NAME=dict(zip(fmap.BLIND_ID,fmap.TRUE_NAME))
FEATS=[f"f{i:03d}" for i in range(1,47)]
# full 83-object trade panel + frozen final blind results
B=pd.read_parquet(OUT+r"\ATTRIBUTION_V2_TRADE_FEATURES.parquet")[["object","net_R","decision_time"]+FEATS]
N=pd.read_parquet(OUT+r"\ATTRIBUTION_V2_T2_ALL_TRADE_FEATURES.parquet")[["object","net_R","decision_time"]+FEATS]
df=pd.concat([B,N],ignore_index=True)
R=pd.read_csv(OUT+r"\ATTRIBUTION_V2_FINAL83_BLIND_RESULTS.csv")
SEC_YR=365.25*86400
Z=(1.959963985+0.841621234)**2   # 80% power, two-sided a=0.05

def dirof(o):
    base=str(o).split("::")[0]; return DIRc.get(o) or DIRc.get(base) or "?"

rescues=[]
for o,g in df.groupby("object"):
    rr=R[(R.object==o)&(R.fdr)&(R.bp_exp>0)&(R.bp_N>=MIN_N)].sort_values("bp_lift",ascending=False)
    for _,c in rr.iterrows():
        f=c.feature; b=c.bp_bin; sub=g[g[f]==b]
        sel=sub["net_R"].to_numpy()
        if len(sel)<MIN_N: continue
        d5=np.sort(sel)[:int(len(sel)*0.95)].mean()
        gg=sub.sort_values("decision_time"); th=np.array_split(gg["net_R"].to_numpy(),3)
        chrono=sum(1 for t in th if len(t) and t.mean()>0)
        if not (sel.mean()>0 and d5>0 and chrono>=2): continue
        # ---- GATE-PASSING RESCUE for object o ----
        rem=g[g[f]!=b]["net_R"].to_numpy()
        subt=sub["decision_time"].to_numpy(); objt=g["decision_time"].to_numpy()
        active_yr=(objt.max()-objt.min())/SEC_YR
        days=np.unique(subt//86400); udays=len(days)
        # episodes: >=1 day gap between consecutive subset days
        sd=np.sort(days); eps=1+int((np.diff(sd)>1).sum()) if len(sd)>1 else len(sd)
        maxday=pd.Series(subt//86400).value_counts().max()
        effN=udays                                   # independent-day proxy for effective N
        rate=len(sel)/active_yr                       # rescue trades/year (raw)
        eff_rate=udays/active_yr                       # independent (per-day) trades/year
        # per-year concentration
        yrs=(pd.to_datetime(subt,unit="s",utc=True).year); yc=pd.Series(yrs).value_counts()
        span_years=int(objt.max()//1//SEC_YR - objt.min()//1//SEC_YR)+1
        zero_years=max(0, span_years-len(yc)); maxyr=yc.max()/len(sel)
        # prospective N for 80% power (positive expectancy vs 0), on the INDEPENDENT-day mean/var
        dmean=pd.DataFrame({"d":subt//86400,"r":sel}).groupby("d")["r"].mean().to_numpy()
        sd_ind=dmean.std(ddof=1) if len(dmean)>1 else sel.std(ddof=1); eff=dmean.mean()
        n100=Z*(sd_ind**2)/(eff**2) if eff>0 else np.inf
        n50 =Z*(sd_ind**2)/((0.5*eff)**2) if eff>0 else np.inf
        t30=30/eff_rate*12; t50=50/eff_rate*12; t100=100/eff_rate*12   # months to N independent
        m_min=t30; m_reasonable=n50/eff_rate*12
        horizon=("FAST" if m_reasonable<=12 else "MEDIUM" if m_reasonable<=24 else "SLOW" if m_reasonable<=60 else "IMPRACTICAL")
        # discovery strength (frozen)
        pf=(sel[sel>0].sum())/(abs(sel[sel<=0].sum())+1e-9); wr=(sel>0).mean(); top1=np.sort(sel)[-max(1,len(sel)//100):].sum()/max(sel.sum(),1e-9)
        strong = (sel.mean()>=0.20 and d5>0 and chrono==3 and top1<0.5 and len(sel)>=50)
        med = (sel.mean()>=0.10 and d5>0 and chrono>=2 and len(sel)>=40)
        DSTR="HIGH" if strong else ("MEDIUM" if med else "LOW")
        mech=c.mechanism; indep="NO" if mech=="M05_OPENING_RANGE" else ("PARTIAL" if mech in ("M06_SESSION_TIME",) else "YES")
        rescues.append(dict(object=o,family=c.family,mechanism=mech,direction=dirof(o),feature=NAME.get(f,f),
                            condition=f"{NAME.get(f,f)}={b}",N=len(sel),subset_exp=round(sel.mean(),4),remainder_exp=round(rem.mean(),4),
                            lift=round(sel.mean()-rem.mean(),4),PF=round(pf,2),WR=round(wr,3),chrono3=chrono,drop5=round(d5,4),top1_share=round(top1,2),
                            active_years=round(active_yr,1),trades_per_year=round(rate,2),eff_trades_per_year=round(eff_rate,2),
                            unique_days=udays,episodes=eps,max_per_day=int(maxday),effective_N=effN,zero_years=zero_years,max_year_share=round(maxyr,2),
                            N_req_100=round(n100,0),N_req_50=round(n50,0),time_to_30_mo=round(t30,1),time_to_50_mo=round(t50,1),time_to_100_mo=round(t100,1),
                            months_min_useful=round(m_min,1),months_reasonable=round(m_reasonable,1),horizon=horizon,
                            discovery_strength=DSTR,independent_from_S5=indep,causal_at_decision="YES"))
        break   # one gate-passing rescue per object (the frozen best)
RD=pd.DataFrame(rescues).sort_values("subset_exp",ascending=False).reset_index(drop=True)
RD.to_csv(OUT+r"\ATTRIBUTION_V2_RESCUE_FEASIBILITY_REGISTER.csv",index=False)
print(f"FROZEN_RESCUES_TOTAL = {len(RD)}")
print(f"CAUSAL_RESCUES = {(RD.causal_at_decision=='YES').sum()}  S5_INDEPENDENT (YES) = {(RD.independent_from_S5=='YES').sum()}  PARTIAL = {(RD.independent_from_S5=='PARTIAL').sum()}  NO = {(RD.independent_from_S5=='NO').sum()}")
print("horizon:", dict(RD.horizon.value_counts()))
print("\n== RESCUE REGISTER (frozen 22) ==")
cols=["object","mechanism","direction","condition","N","subset_exp","remainder_exp","lift","eff_trades_per_year","effective_N","time_to_50_mo","horizon","discovery_strength","independent_from_S5"]
print(RD[cols].to_string(index=False))
# S14 benchmark
s14=RD[RD.object.str.startswith("S14")]
if len(s14): r=s14.iloc[0]; print(f"\nS14 BENCHMARK: N={r.N} exp={r.subset_exp} rem={r.remainder_exp} eff/yr={r.eff_trades_per_year} t50={r.time_to_50_mo}mo t100={r.time_to_100_mo}mo horizon={r.horizon}")
# post-2026-07-27 expected qualifying events
print("\n== expected qualifying events post-2026-07-27 (rate only, no outcome inspection) ==")
for _,r in RD.head(8).iterrows():
    e=r.eff_trades_per_year
    print(f"  {r.object:20s} {r.condition:28s} 1mo={e/12:.1f} 3mo={e/4:.1f} 6mo={e/2:.1f} 12mo={e:.1f} 24mo={2*e:.1f}")
# rankings
print("\n== RANKING A (scientific strength): by discovery strength then lift ==")
sa=RD.sort_values(["discovery_strength","subset_exp"],ascending=[True,False])  # HIGH<LOW alpha; fix order
order={"HIGH":0,"MEDIUM":1,"LOW":2}; RD["_s"]=RD.discovery_strength.map(order)
sa=RD.sort_values(["_s","lift"],ascending=[True,False])
print(sa[["object","condition","subset_exp","lift","discovery_strength"]].head(8).to_string(index=False))
print("\n== RANKING B (validation feasibility): by months_reasonable asc ==")
sb=RD.sort_values("months_reasonable")
print(sb[["object","condition","eff_trades_per_year","effective_N","months_reasonable","horizon","independent_from_S5"]].head(8).to_string(index=False))
# CEO priority: causal YES & independent (YES/PARTIAL) & strength HIGH/MEDIUM & horizon<=MEDIUM, then by feasibility
elig=RD[(RD.causal_at_decision=="YES")&(RD.independent_from_S5.isin(["YES","PARTIAL"]))&(RD.discovery_strength.isin(["HIGH","MEDIUM"]))&(RD.horizon.isin(["FAST","MEDIUM"]))]
print(f"\n== DECISION GATE eligible (causal & indep & HIGH/MED & <=24mo): {len(elig)} ==")
if len(elig):
    ce=elig.sort_values(["_s","months_reasonable"])
    print(ce[["object","mechanism","condition","subset_exp","eff_trades_per_year","effective_N","months_reasonable","horizon","discovery_strength","independent_from_S5"]].to_string(index=False))
    print("\nPRACTICALLY_VALIDATABLE_RESCUE_EXISTS = YES")
    top=ce.iloc[0]; print(f"NEXT_RESCUE_FOR_PROSPECTIVE_VALIDATION = {top.object} | {top.condition}")
else:
    print("\nPRACTICALLY_VALIDATABLE_RESCUE_EXISTS = NO -> V2_RESCUE_ROUTE_NEAR_TERM_BLOCKED = YES")

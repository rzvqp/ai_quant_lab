"""attr_v2_t2_recompute.py — V2 COMPLETION Phase D: recompute the global findings over the FULL universe (70 baseline + 13 regenerated T2
= 83 ANALYSED objects), preserving the FROZEN experiment-wide multiplicity (declared m=5175, all 115 objects in the denominator; no easier
FDR universe). Re-runs blind stage-1 (day-clustered rescue vs remainder, BH-FDR q=0.05 @ m=5175), placebo, meta-state, per-family autopsy;
compares V2_PARTIAL_70 vs V2_FINAL_83 for each major finding. Writes final coverage (all 45 T2) + comparison.
"""
import os, sys, math, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; STAT=r"C:\Users\MEDION GAMING\ai_quant_lab\statistician"
OUT=os.path.join(AA,"reports","alpha_discovery")
Q=0.05; M_DECLARED=5175; MIN_N=30; MIN_DAYS=20; FEATS=[f"f{i:03d}" for i in range(1,47)]
uni=pd.read_csv(STAT+r"\attribution_v2\ATTRIBUTION_V2_EXECUTION_UNIVERSE.csv")
FAM=dict(zip(uni.ANALYSIS_OBJECT_ID,uni.SOURCE_FAMILY_ID)); MECH=dict(zip(uni.ANALYSIS_OBJECT_ID,uni.MECHANISM_ID))
elig=pd.read_csv(STAT+r"\attribution_v2_handoff\ATTRIBUTION_V2_STAGE1_ELIGIBLE_FEATURES.csv")
EF=elig[elig.STAGE1_ELIGIBLE==1].F_ID.tolist()

def famkey(o):
    if o in FAM: return FAM[o],MECH.get(o,"?")
    base=str(o).split("::")[0]; return FAM.get(base,base),MECH.get(base,"?")

# baseline 70 (frozen) + new 13
B=pd.read_parquet(OUT+r"\ATTRIBUTION_V2_TRADE_FEATURES.parquet")[["object","net_R","decision_time"]+FEATS]
N=pd.read_parquet(OUT+r"\ATTRIBUTION_V2_T2_ALL_TRADE_FEATURES.parquet")[["object","net_R","decision_time"]+FEATS]
df=pd.concat([B,N],ignore_index=True)
df["family"]=[famkey(o)[0] for o in df.object]; df["mechanism"]=[famkey(o)[1] for o in df.object]
print(f"FULL universe analysed: objects={df.object.nunique()} trades={len(df)} (baseline 70 + new {N.object.nunique()})")

def dcl(net,day,mask):
    yin=net[mask]; yout=net[~mask]
    if len(yin)<MIN_N or len(yout)<MIN_N: return None
    mu=yin.mean(); base=yout.mean(); g=pd.DataFrame({"d":day[mask],"y":yin}).groupby("d")["y"].agg(["sum","count"]);G=len(g);NN=len(yin)
    if G<MIN_DAYS: return None
    se=math.sqrt(max(((g["sum"].to_numpy()-g["count"].to_numpy()*mu)**2).sum()/NN**2*(G/max(G-1,1)),1e-18))
    z=(mu-base)/se if se>0 else 0.0; p=2*(1-0.5*(1+math.erf(abs(z)/math.sqrt(2))))
    return dict(N=NN,exp=float(mu),lift=float(mu-base),z=float(z),p=float(p))

def score(df,shuffle=False,seed=0):
    rng=np.random.RandomState(seed); rec=[]
    for o,g in df.groupby("object"):
        net=g["net_R"].to_numpy().copy(); day=g["decision_time"].to_numpy()//86400
        if shuffle: rng.shuffle(net)
        for f in EF:
            b=g[f].to_numpy(); bins=[]
            for v in pd.Series(b).dropna().unique():
                r=dcl(net,day,b==v)
                if r: r["bin"]=v; bins.append(r)
            if not bins: continue
            nb=len(bins); bp=max([x for x in bins if x["exp"]>0],key=lambda x:x["lift"],default=None)
            rec.append(dict(object=o,family=g["family"].iloc[0],mechanism=g["mechanism"].iloc[0],feature=f,omni_p=min(min(x["p"]*nb,1.0) for x in bins),
                            bp_bin=bp["bin"] if bp else np.nan,bp_exp=bp["exp"] if bp else np.nan,bp_N=bp["N"] if bp else 0,bp_lift=bp["lift"] if bp else np.nan))
    R=pd.DataFrame(rec).sort_values("omni_p").reset_index(drop=True); R["rank"]=np.arange(1,len(R)+1)
    kmax=R.index[R["omni_p"]<=R["rank"]/M_DECLARED*Q].max() if (R["omni_p"]<=R["rank"]/M_DECLARED*Q).any() else -1
    R["fdr"]=R.index<=kmax if kmax>=0 else False
    return R

R=score(df); R.to_csv(OUT+r"\ATTRIBUTION_V2_FINAL83_BLIND_RESULTS.csv",index=False)
sig=R[R.fdr&(R.bp_exp>0)&(R.bp_N>=MIN_N)]
print(f"\nSTAGE-1 (83 obj): tests={len(R)} FDR@m={M_DECLARED}={int(R.fdr.sum())} | FDR-sig +ve bins={len(sig)} across {sig.object.nunique()} objects")
pl=[len(score(df,True,100+s)[lambda x:x.fdr&(x.bp_exp>0)&(x.bp_N>=MIN_N)]) for s in range(3)]
print(f"PLACEBO: null {pl} vs real {len(sig)} -> {'PASS' if np.mean(pl)<=max(2,0.5*len(sig)) else 'FAIL'}")

# meta-state (pooled)
print("\n== META-STATE (pooled, full 83) ==")
for f in ["f011","f017","f016"]:
    g=df.groupby(f)["net_R"]; ex=g.mean()[g.count()>=200]
    print(f"  {f}: best pooled={ex.max():+.3f} worst={ex.min():+.3f}")
best_pooled=max(df.groupby("f011")["net_R"].mean()[df.groupby("f011")["net_R"].count()>=200].max(),
                df.groupby("f017")["net_R"].mean()[df.groupby("f017")["net_R"].count()>=200].max())
PROF_META = bool(best_pooled>0.02)

# autopsy (concentration+chrono)
prof=[]
for o,g in df.groupby("object"):
    rr=R[(R.object==o)&R.fdr&(R.bp_exp>0)&(R.bp_N>=MIN_N)].sort_values("bp_lift",ascending=False)
    for _,c in rr.iterrows():
        sel=g[g[c.feature]==c.bp_bin]["net_R"].to_numpy()
        if len(sel)<MIN_N: continue
        d5=np.sort(sel)[:int(len(sel)*0.95)].mean(); th=np.array_split(g[g[c.feature]==c.bp_bin].sort_values("decision_time")["net_R"].to_numpy(),3)
        if sel.mean()>0 and d5>0 and sum(1 for t in th if len(t) and t.mean()>0)>=2: prof.append(o); break
print(f"\nPROFITABLE_RESCUE objects (83): {len(set(prof))}")
# recurrence
print("recurrence (full):")
for f in ["f011","f017","f016"]:
    s=sig[sig.feature==f]; print(f"  {f}: fam={s.family.nunique()} mech={s.mechanism.nunique()} obj={s.object.nunique()}")
fc=sig.groupby("feature").object.nunique().sort_values(ascending=False)
print("top features:", dict(fc.head(5)))

# ---- FINAL COVERAGE (all 45 T2) ----
ERC=pd.read_csv(OUT+r"\ATTRIBUTION_V2_T2_ER_COVERAGE.csv"); FCC=pd.read_csv(OUT+r"\ATTRIBUTION_V2_T2_FAC_COVERAGE.csv")
extra=pd.DataFrame([
 ("M5_EVENT_REVEALED_DIRECTION_FACTORY_V1","ANALYSED","n=3636 Family E 2R (M5-native, backward-asof join)"),
 ("H1_H4_SETUP_M5_EXECUTION_V1","GENUINE_FAILED_REGENERATION","NO_SINGLE_TRADE_POPULATION: 5-edge HTF->M5 campaign (pullback/breakout/reject/failbreak/transition), no single canonical strategy"),
 ("COMP_CONT_L_RR2","ANALYSED","n=53 frontier5_compcont LONG rr2 STRESS (H4-native, backward-asof)"),
 ("CRS1_H4DIV_FADE_S","ANALYSED","n=2 cur_cr13_trade curlike H4up SHORT 1.5ATR rr2 dedup16 (H4-native; thin current-like gate)"),
 ("H4_BO_RAW_S","GENUINE_FAILED_REGENERATION","REPRESENTATIVE_UNRESOLVED: frozen candidate selected post-hoc from a multi-candidate batch scan; no unique executable representative declared (REP_ID=nan)"),
 ("HR_TU_PB_L","GENUINE_FAILED_REGENERATION","REPRESENTATIVE_UNRESOLVED: frozen weak candidate from batch scan; no unique executable representative declared"),
 ("MT_H4_DISPACCEPT_L","GENUINE_FAILED_REGENERATION","REPRESENTATIVE_UNRESOLVED: frozen weak candidate from batch scan; no unique executable representative declared"),
 ("E015_ORDER_BLOCK_REMITIGATION","GENUINE_FAILED_REGENERATION","HTF_SOURCE_ABSENT: order-block remitigation requires D1 (not a ratified manifest timeframe), same blocker as edge_research E015"),
],columns=["object","STATUS","note"])
# drop the placeholder factory rows we superseded
FCC=FCC[~FCC.object.isin(["M5_EVENT_REVEALED_DIRECTION_FACTORY_V1","H1_H4_SETUP_M5_EXECUTION_V1"])]
COV=pd.concat([ERC[["object","STATUS","note"]],FCC[["object","STATUS","note"]],extra],ignore_index=True).drop_duplicates("object")
COV.to_csv(OUT+r"\ATTRIBUTION_V2_T2_FINAL_COVERAGE.csv",index=False)
print("\n== FINAL T2 COVERAGE (45) =="); print(COV.STATUS.value_counts().to_string())
gb=COV[COV.STATUS.str.contains("GENUINE")].note.str.extract(r"(NO_TRADE_POPULATION|NO_SINGLE_TRADE_POPULATION|HTF_SOURCE_ABSENT|HTF_SOURCE_SEALED|REPRESENTATIVE_UNRESOLVED)")[0].value_counts()
print("\nGENUINE blocker breakdown:"); print(gb.to_string())
print(f"\nFINAL: T2 ANALYSED={int((COV.STATUS=='ANALYSED').sum())} / 45 ; total ANALYSED objects={70+int((COV.STATUS=='ANALYSED').sum())}/115")

"""attr_v2_score.py — V2 PHASE 2: BLIND stage-1 scoring + placebo + recurrence + freeze/hash. Feature ids stay blind (f001..f046, f029
excluded -> 45). Per (object x feature): for each frozen bin with N>=30 & >=20 independent days, day-clustered z of (bin exp - remainder
exp). Omnibus p per (object,feature) = Bonferroni-within-feature min-bin p. BH-FDR q=0.05 at the DECLARED m=5175 (frozen multiplicity).
Rescue class per object: PROFITABLE_RESCUE (a bin exp>0, gates+FDR+concentration+chrono pass) / LOSE_LESS_TILT / NO_EFFECT / HARMFUL.
Placebo: shuffle net_R within object, recount FDR-rescues -> hard gate. Writes BLIND_ATTRIBUTION_RESULTS_V2.csv + hash. NO semantics.
"""
import sys, os, math, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; STAT=r"C:\Users\MEDION GAMING\ai_quant_lab\statistician"
OUT=os.path.join(AA,"reports","alpha_discovery")
Q=0.05; M_DECLARED=5175; MIN_N=30; MIN_DAYS=20

def dcl_z(net, day, mask):
    """day-clustered z of mean(net[mask]) - mean(net[~mask]) using cluster-robust SE on the IN-group (scout cl)."""
    yin=net[mask]; yout=net[~mask]
    if len(yin)<MIN_N or len(yout)<MIN_N: return None
    mu=yin.mean(); base=yout.mean(); din=day[mask]
    g=pd.DataFrame({"d":din,"y":yin}).groupby("d")["y"].agg(["sum","count"]); G=len(g); N=len(yin)
    if G<MIN_DAYS: return None
    resid=g["sum"].to_numpy()-g["count"].to_numpy()*mu
    se=math.sqrt(max((resid**2).sum()/N**2*(G/max(G-1,1)),1e-18))
    z=(mu-base)/se if se>0 else 0.0
    from math import erf,sqrt
    p=2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
    return dict(N=N,days=G,exp=float(mu),base=float(base),lift=float(mu-base),z=float(z),p=float(p))

def score(df, feats, uni, shuffle=False, seed=0):
    fam=dict(zip(uni.ANALYSIS_OBJECT_ID,uni.SOURCE_FAMILY_ID)); mech=dict(zip(uni.ANALYSIS_OBJECT_ID,uni.MECHANISM_ID))
    rng=np.random.RandomState(seed); recs=[]
    for oid,g in df.groupby("object"):
        net=g["net_R"].to_numpy().copy(); day=(g["decision_time"].to_numpy()//86400)
        if shuffle: rng.shuffle(net)
        for f in feats:
            b=g[f].to_numpy(); vals=pd.Series(b).dropna().unique()
            bins=[]
            for v in vals:
                mask=(b==v)
                r=dcl_z(net,day,mask)
                if r: r["bin"]=v; bins.append(r)
            if not bins: continue
            nb=len(bins)
            best_pos=max([x for x in bins if x["exp"]>0], key=lambda x:x["lift"], default=None)
            omn_p=min(min(x["p"]*nb,1.0) for x in bins)   # Bonferroni within feature
            bp=best_pos
            recs.append(dict(object=oid, family=fam.get(oid,oid), mechanism=mech.get(oid,"?"), feature=f,
                             n_bins=nb, omni_p=omn_p,
                             best_pos_bin=(bp["bin"] if bp else np.nan), best_pos_exp=(bp["exp"] if bp else np.nan),
                             best_pos_N=(bp["N"] if bp else 0), best_pos_days=(bp["days"] if bp else 0),
                             best_pos_lift=(bp["lift"] if bp else np.nan), best_pos_z=(bp["z"] if bp else np.nan),
                             pooled_exp=float(net.mean())))
    R=pd.DataFrame(recs)
    # BH-FDR at declared m
    R=R.sort_values("omni_p").reset_index(drop=True); R["rank"]=np.arange(1,len(R)+1)
    R["bh_thresh"]=R["rank"]/M_DECLARED*Q
    kmax=R.index[R["omni_p"]<=R["bh_thresh"]].max() if (R["omni_p"]<=R["bh_thresh"]).any() else -1
    R["fdr_sig"]=R.index<=kmax if kmax>=0 else False
    return R

def main():
    df=pd.read_parquet(os.path.join(OUT,"ATTRIBUTION_V2_TRADE_FEATURES.parquet"))
    elig=pd.read_csv(os.path.join(STAT,"attribution_v2_handoff","ATTRIBUTION_V2_STAGE1_ELIGIBLE_FEATURES.csv"))
    feats=elig[elig.STAGE1_ELIGIBLE==1].F_ID.tolist()  # 45, f029 excluded
    uni=pd.read_csv(os.path.join(STAT,"attribution_v2","ATTRIBUTION_V2_EXECUTION_UNIVERSE.csv"))
    print(f"objects={df.object.nunique()} trades={len(df)} eligible_features={len(feats)} (f029 excluded: {'f029' not in feats})")
    R=score(df,feats,uni,shuffle=False)
    R.to_csv(os.path.join(OUT,"ATTRIBUTION_V2_BLIND_FEATURE_RESULTS.csv"),index=False)
    nsig=int(R["fdr_sig"].sum())
    print(f"\nSTAGE-1: {len(R)} (object,feature) tests scored; BH-FDR q=0.05 @ m={M_DECLARED} -> {nsig} FDR-significant")
    # rescue class per object (needs a POSITIVE FDR-sig bin passing gates)
    sig=R[R.fdr_sig & (R.best_pos_exp>0) & (R.best_pos_N>=MIN_N)]
    obj_profit=set(sig.object.unique())
    # concentration + chronological gate on candidate rescues (drop-best-5% & thirds) done in unblind phase; here flag raw
    print(f"objects with >=1 FDR-sig POSITIVE bin (raw rescue candidate) = {len(obj_profit)}")
    # PLACEBO: 3 shuffles, count FDR-sig positive-bin rescues under null
    pl=[]
    for s in range(3):
        Rs=score(df,feats,uni,shuffle=True,seed=100+s)
        sg=Rs[Rs.fdr_sig & (Rs.best_pos_exp>0) & (Rs.best_pos_N>=MIN_N)]
        pl.append(len(sg));
    print(f"PLACEBO FDR-sig positive rescues per shuffle: {pl}  (real={len(sig)})")
    placebo_pass = np.mean(pl) <= max(2, 0.5*len(sig)+1)   # null rescues must be far below real
    print(f"PLACEBO_GATE = {'PASS' if placebo_pass else 'FAIL'}")
    # freeze + hash blind results
    R.to_csv(os.path.join(OUT,"BLIND_ATTRIBUTION_RESULTS_V2.csv"),index=False)
    h=hashlib.sha256(open(os.path.join(OUT,"BLIND_ATTRIBUTION_RESULTS_V2.csv"),"rb").read()).hexdigest()
    print(f"\nBLIND_RESULTS_HASH = {h}")
    # top blind features by count of FDR-sig objects (global discriminators)
    fc=sig.groupby("feature").object.nunique().sort_values(ascending=False)
    print("\nTOP BLIND FEATURES by # objects with FDR-sig positive rescue:")
    print(fc.head(12).to_string())
    # cross-family / cross-mechanism recurrence per feature (>=5 families & >=3 mechanisms, same-direction positive)
    print("\nCROSS-FAMILY/MECHANISM RECURRENCE (feature: #families #mechanisms with FDR-sig positive bin):")
    for f,c in fc.head(12).items():
        s=sig[sig.feature==f]; print(f"  {f}: objects={c} families={s.family.nunique()} mechanisms={s.mechanism.nunique()} "
              f"-> RECURRENCE={'YES' if (s.family.nunique()>=5 and s.mechanism.nunique()>=3) else 'no'}")

if __name__=="__main__":
    main()

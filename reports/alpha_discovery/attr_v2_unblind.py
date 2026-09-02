"""attr_v2_unblind.py — V2 PHASE 3 (post-freeze): unblind for interpretation, apply concentration+chrono gates, decide
PROFITABLE_META_STATE vs LOSE_LESS, per-family autopsy, rescue ranking, post-entry. Ranking NOT changed (blind results frozen+hashed).
"""
import sys, os, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; STAT=r"C:\Users\MEDION GAMING\ai_quant_lab\statistician"
OUT=os.path.join(AA,"reports","alpha_discovery")
MIN_N=30; MIN_DAYS=20

def main():
    df=pd.read_parquet(os.path.join(OUT,"ATTRIBUTION_V2_TRADE_FEATURES.parquet"))
    R=pd.read_csv(os.path.join(OUT,"BLIND_ATTRIBUTION_RESULTS_V2.csv"))
    fmap=pd.read_csv(r"C:\Users\MEDION~1\AppData\Local\Temp\v2\feature_map_SECRET.csv")
    NAME=dict(zip(fmap.BLIND_ID,fmap.TRUE_NAME))
    df["day"]=df["decision_time"]//86400
    # ===== §30 PROFITABLE META-STATE test: pooled net_R by the top clock features =====
    print("== §30 POOLED meta-state (all 70 objects, 505k trades): best bin per top feature ==")
    for f,nm in (("f011",NAME["f011"]),("f017",NAME["f017"]),("f016",NAME["f016"]),("f039",NAME["f039"]),("f005",NAME["f005"])):
        g=df.groupby(f)["net_R"]; ex=g.mean(); N=g.count(); ex=ex[N>=200]
        if len(ex)==0: continue
        bb=ex.idxmax()
        # concentration on best bin
        sub=df[df[f]==bb]["net_R"].to_numpy(); drop5=np.sort(sub)[:int(len(sub)*0.95)].mean()
        # cross-family: fraction of objects positive in best bin
        per=[df[(df[f]==bb)&(df.object==o)]["net_R"].mean() for o in df.object.unique() if ((df[f]==bb)&(df.object==o)).sum()>=30]
        per=[x for x in per if np.isfinite(x)]
        print(f"  {f}={nm:22s} best_bin={bb} pooled_exp={ex.max():+.3f} N={int(N[bb])} drop5%={drop5:+.3f} "
              f"objs+={sum(x>0 for x in per)}/{len(per)}  (worst_bin_exp={ex.min():+.3f})")
    # ===== rescue class per object (concentration + chrono gates on FDR-sig positive bins) =====
    print("\n== §24 PER-FAMILY AUTOPSY (rescue class; concentration + chrono gates applied) ==")
    autopsy=[]; profit_objs=[]
    for o,g in df.groupby("object"):
        rr=R[(R.object==o)&(R.fdr_sig) & (R.best_pos_exp>0) & (R.best_pos_N>=MIN_N)]
        cls="NONE"; cond=""; sub_exp=np.nan; rem_exp=np.nan
        if len(rr):
            rr=rr.sort_values("best_pos_lift",ascending=False)
            for _,c in rr.iterrows():
                f=c.feature; b=c.best_pos_bin; sel=g[g[f]==b]["net_R"].to_numpy()
                if len(sel)<MIN_N: continue
                drop5=np.sort(sel)[:int(len(sel)*0.95)].mean()
                # chrono thirds
                gg=g[g[f]==b].sort_values("decision_time"); th=np.array_split(gg["net_R"].to_numpy(),3)
                chrono=sum(1 for t in th if len(t)>0 and t.mean()>0)
                if sel.mean()>0 and drop5>0 and chrono>=2:
                    cls="PROFITABLE_RESCUE"; cond=f"{NAME.get(f,f)}={b}"; sub_exp=float(sel.mean())
                    rem_exp=float(g[g[f]!=b]["net_R"].mean()); profit_objs.append(o); break
            if cls=="NONE": cls="LOSE_LESS_OR_FRAGILE";
        po=float(g["net_R"].mean())
        autopsy.append(dict(object=o,family=g["family"].iloc[0],mechanism=g["mechanism"].iloc[0] if "mechanism" in g else "",
                            n=len(g),pooled_exp=po,rescue_class=cls,condition=cond,subset_exp=sub_exp,remainder_exp=rem_exp))
    A=pd.DataFrame(autopsy)
    # attach mechanism from universe
    uni=pd.read_csv(os.path.join(STAT,"attribution_v2","ATTRIBUTION_V2_EXECUTION_UNIVERSE.csv"))
    A=A.drop(columns=["mechanism"]).merge(uni[["ANALYSIS_OBJECT_ID","MECHANISM_ID","SOURCE_FAMILY_ID"]],left_on="object",right_on="ANALYSIS_OBJECT_ID",how="left")
    A.to_csv(os.path.join(OUT,"ATTRIBUTION_V2_PER_FAMILY_AUTOPSY.csv"),index=False)
    print(A["rescue_class"].value_counts().to_string())
    pr=A[A.rescue_class=="PROFITABLE_RESCUE"]
    print(f"\nPROFITABLE_RESCUE objects = {len(pr)} / {len(A)} analysed")
    if len(pr):
        print(pr.sort_values("subset_exp",ascending=False)[["object","MECHANISM_ID","pooled_exp","subset_exp","remainder_exp","condition"]].head(20).to_string(index=False))
    # ===== global rescue ranking (top 20) with unblinded condition =====
    rk=R[(R.fdr_sig)&(R.best_pos_exp>0)&(R.best_pos_N>=MIN_N)].copy()
    rk["condition"]=rk.apply(lambda r: f"{NAME.get(r.feature,r.feature)}={r.best_pos_bin}",axis=1)
    rk=rk.sort_values("best_pos_lift",ascending=False)
    rk[["object","family","mechanism","feature","condition","best_pos_N","best_pos_exp","best_pos_lift","pooled_exp","omni_p"]].head(20).to_csv(os.path.join(OUT,"ATTRIBUTION_V2_RESCUE_REGISTER.csv"),index=False)
    print("\n== TOP 10 RESCUE HYPOTHESES (unblinded) ==")
    print(rk[["object","mechanism","condition","best_pos_N","pooled_exp","best_pos_exp","best_pos_lift"]].head(10).to_string(index=False))
    # cross-mechanism recurrence unblinded (top feature)
    sig=R[R.fdr_sig&(R.best_pos_exp>0)&(R.best_pos_N>=MIN_N)]
    print("\n== recurrence (unblinded) ==")
    for f in ["f011","f017","f016"]:
        s=sig[sig.feature==f]; print(f"  {NAME[f]:22s}: families={s.family.nunique()} mechanisms={s.mechanism.nunique()} objects={s.object.nunique()}")

if __name__=="__main__":
    main()

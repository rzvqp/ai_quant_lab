"""attr_v2_regen.py — V2 PHASE 1: regenerate causal trade ledgers + join BLINDED features at the DECISION bar (frozen rule).
S-library (56 reps) via mstrat.simulate (si = decision bar); T1 (14) from the V1 master table. 45 T2 objects -> FAILED_REGENERATION
(bespoke per-object generators across edge_research/factory/frozen subsystems, not regenerable in this cycle) -- kept in denominators.
Join: blinded feature panel (frozen bin indices, per bar) at the decision bar by exact BAR_OPEN_TIME (panels index-aligned; verified),
NEVER the entry bar. Writes ATTRIBUTION_V2_TRADE_FEATURES.parquet (object, family, mechanism, dir, net_R, decision_time, f001..f046 bins).
"""
import sys, os, json, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
STAT=r"C:\Users\MEDION GAMING\ai_quant_lab\statistician"
sys.path.insert(0, os.path.join(AA,"code")); sys.path.insert(0, os.path.join(AA,"reports","alpha_discovery"))
OUT=os.path.join(AA,"reports","alpha_discovery")

def main():
    U=pd.read_csv(os.path.join(STAT,"attribution_v2","ATTRIBUTION_V2_EXECUTION_UNIVERSE.csv"))
    REP=pd.read_csv(os.path.join(STAT,"attribution_v2","REPRESENTATIVE_VARIANT_MAP.csv"))
    BV=pd.read_parquet(os.path.join(STAT,"attribution_v2_handoff","ATTRIBUTION_V2_BLINDED_FEATURE_VALUES.parquet"))
    FEATS=[f"f{ i:03d}" for i in range(1,47)]
    bt=BV["BAR_OPEN_TIME"].to_numpy(); bi=BV["BAR_INDEX"].to_numpy()
    t2idx={int(t):int(ix) for t,ix in zip(bt,bi)}                      # exact open-time -> row
    import mstrat as MS, mstrat_ext as MX
    d=MS.load(); dtime=d["time"].to_numpy(); REG={**MS.REGISTRY,**MX.EXT_REGISTRY}
    # verify panel alignment blinded<->mstrat
    align=np.array_equal(bt[:len(dtime)], dtime) if len(bt)==len(dtime) else False
    print(f"blinded rows={len(BV)} mstrat rows={len(dtime)} index-aligned={align}")
    rows=[]; cov=[]
    # ---- S-library (56 reps) ----
    for _,r in REP[REP.STATUS=="ELIGIBLE"].iterrows():
        fam=r.FAMILY_ID; oid=f"{fam}::{r.REP_ID}"
        try:
            gram,setf=REG[fam]; hs=gram(); h=next((x for x in hs if x.get("id")==r.REP_ID),None)
            if h is None: cov.append((oid,fam,"FAILED_REGENERATION","rep id not in grammar")); continue
            led=MS.simulate(d,setf(d,h)); side=1 if str(h.get("side","")).lower() in ("high","long","up","buy") else (0 if str(h.get("side","")).lower() in ("low","short","down","sell") else -1)
            sd=str(h.get("side",""))
            for R,si in zip(led["R"].to_numpy(), led["si"].to_numpy()):
                rows.append((oid,fam,"SLIB",sd,float(R),int(dtime[int(si)])))
            cov.append((oid,fam,"ANALYSED",f"n={len(led)}"))
        except Exception as e:
            cov.append((oid,fam,"FAILED_REGENERATION",str(e)[:60]))
    # ---- T1 (14) from V1 master table; decision bar = entry_bar-1 (signal), join by its open time ----
    try:
        import cur_data as CD; m=CD.load_m15(); ct=m["time"].to_numpy()
        MT=pd.read_csv(os.path.join(OUT,"STRATEGY_ATTRIBUTION_MASTER_TABLE.csv"))
        for sid,g in MT.groupby("sid"):
            for _,t in g.iterrows():
                e=int(t["ent"]); sig=max(e-1,0); rows.append((sid,sid,"T1",("L" if t["side"]>0 else "S"),float(t["net"]),int(ct[sig])))
            cov.append((sid,sid,"ANALYSED",f"n={len(g)} (V1 log)"))
    except Exception as e:
        print("T1 err",e)
    # ---- 45 T2 objects: FAILED_REGENERATION (kept in denominators) ----
    t2=U[U.TIER.str.startswith("T2")]
    for _,r in t2.iterrows():
        cov.append((r.ANALYSIS_OBJECT_ID, r.SOURCE_FAMILY_ID, "FAILED_REGENERATION",
                    f"bespoke {r.TIER} generator not regenerable this cycle"))
    T=pd.DataFrame(rows, columns=["object","family","tier","side_raw","net_R","decision_time"])
    # join blinded features by exact decision open-time
    ix=T["decision_time"].map(t2idx)
    ok=ix.notna(); print(f"trades={len(T)} joined={int(ok.sum())} unmatched={int((~ok).sum())}")
    T=T[ok].copy(); ix=ix[ok].astype(int).to_numpy()
    for f in FEATS: T[f]=BV[f].to_numpy()[ix]
    T.to_parquet(os.path.join(OUT,"ATTRIBUTION_V2_TRADE_FEATURES.parquet"))
    C=pd.DataFrame(cov, columns=["object","family","STATUS","note"])
    C.to_csv(os.path.join(OUT,"ATTRIBUTION_V2_COVERAGE_STATUS.csv"),index=False)
    print("\n== COVERAGE ==")
    print(C.STATUS.value_counts().to_string())
    print(f"objects ANALYSED={int((C.STATUS=='ANALYSED').sum())}  FAILED_REGEN={int((C.STATUS=='FAILED_REGENERATION').sum())}  total={len(C)}")
    print(f"total valid trades joined = {len(T)}  across {T.object.nunique()} objects")

if __name__=="__main__":
    main()

"""ctx_setups.py — CONTEXTUAL TRADE SELECTION V1, PHASE 1: freeze the 10 base setups and regenerate their ORIGINAL frozen trades
(entry/stop/target/cost UNCHANGED) via the canonical mstrat engine, capturing per-trade R + si (DECISION/signal bar) + ei (entry bar) +
decision_time. The base OUTCOME is the target to be explained; nothing about the strategy is modified. Writes BASE_SETUP_10_REGISTER.csv +
CTX_SETUP_TRADES.parquet (object, mechanism, R, si, ei, decision_time).
"""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; STAT=r"C:\Users\MEDION GAMING\ai_quant_lab\statistician"
sys.path.insert(0, os.path.join(AA,"code")); sys.path.insert(0, os.path.join(AA,"reports","alpha_discovery"))
OUT=os.path.join(AA,"reports","alpha_discovery")
import mstrat as MS, mstrat_ext as MX
REG={**MS.REGISTRY, **MX.EXT_REGISTRY}
uni=pd.read_csv(STAT+r"\attribution_v2\ATTRIBUTION_V2_EXECUTION_UNIVERSE.csv")
REP=pd.read_csv(STAT+r"\attribution_v2\REPRESENTATIVE_VARIANT_MAP.csv")
o2m=dict(zip(uni.ANALYSIS_OBJECT_ID,uni.MECHANISM_ID))

# FROZEN SELECTION — 10 mechanism-diverse setups, big winner+loser populations, causal executable, NOT S5
SEL=[("S21","6ddb75c3f9b1","M01_LIQUIDITY_SWEEP"),("S2","691f36c634e3","M02_FAILED_BREAKOUT_FADE"),
     ("S3","7aafa506c507","M03_BREAKOUT_RETEST"),("S4","cf232107e3b5","M04_VOLATILITY_COMPRESSION_EXPANSION"),
     ("S8","b7adfd7f9d4f","M08_EXTENSION_MEAN_REVERSION"),("S10","7df75fdb8ecb","M10_DISPLACEMENT_CONTINUATION"),
     ("S11","576394ea476f","M11_STRUCTURE_BREAK_REVERSAL"),("S12","884efeda36f3","M12_RANGE_ROTATION"),
     ("S13","7d288aa44d52","M13_IMBALANCE_FVG"),("S27","8492323d86e4","M16_AUCTION_VALUE")]

d=MS.load(); dtime=d["time"].to_numpy()
print("d columns:", list(d.columns))
rows=[]; reg=[]
for i,(fam,rep,mech) in enumerate(SEL,1):
    oid=f"{fam}::{rep}"
    gram,setf=REG[fam]; hs=gram(); h=next((x for x in hs if x.get("id")==rep),None)
    if h is None:
        # rep hash may be a content hash; match by REP map
        rr=REP[(REP.FAMILY_ID==fam)]; h=None
        if len(rr):
            rid=rr.iloc[0].REP_ID; h=next((x for x in hs if x.get("id")==rid),None)
    if h is None: print(f"  {oid} REP NOT FOUND (grammar ids: {[x.get('id') for x in hs][:4]}...)"); continue
    led=MS.simulate(d, setf(d,h))
    R=led["R"].to_numpy(); si=led["si"].to_numpy().astype(int); ei=led["ei"].to_numpy().astype(int)
    for r_,s_,e_ in zip(R,si,ei): rows.append((oid,mech,f"BASE_SETUP_{i:02d}",float(r_),int(s_),int(e_),int(dtime[int(s_)])))
    spec_hash=hashlib.sha256(json.dumps(h,sort_keys=True,default=str).encode()).hexdigest()[:16]
    reg.append(dict(setup_id=f"BASE_SETUP_{i:02d}",object=oid,family=fam,mechanism=mech,rep_id=rep,
                    N=len(R),wins=int((R>0).sum()),losses=int((R<=0).sum()),WR=round((R>0).mean(),3),
                    base_expR=round(R.mean(),4),sdR=round(R.std(),3),spec_hash=spec_hash,
                    date_start=pd.to_datetime(dtime[si].min(),unit="s",utc=True).date().isoformat(),
                    date_end=pd.to_datetime(dtime[si].max(),unit="s",utc=True).date().isoformat()))
    print(f"  {f'BASE_SETUP_{i:02d}':13s} {oid:20s} {mech:36s} N={len(R):6d} WR={(R>0).mean():.3f} expR={R.mean():+.4f}")

T=pd.DataFrame(rows,columns=["object","mechanism","setup_id","R","si","ei","decision_time"])
T.to_parquet(OUT+r"\CTX_SETUP_TRADES.parquet")
RG=pd.DataFrame(reg); RG.to_csv(OUT+r"\BASE_SETUP_10_REGISTER.csv",index=False)
print(f"\nFROZEN 10 setups; total trades={len(T)}; distinct mechanisms={RG.mechanism.nunique()}")
print("register hash:", hashlib.sha256(open(OUT+r'\BASE_SETUP_10_REGISTER.csv','rb').read()).hexdigest()[:16])

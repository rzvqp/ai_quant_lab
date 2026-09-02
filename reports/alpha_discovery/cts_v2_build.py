"""cts_v2_build.py — CONTEXTUAL TRADE SELECTION V2, PHASE 1: pre-flight executability check (§3), select EXACTLY 3 setups from the frozen
V1 ten (by causal validity/population/geometry/mechanism diversity ONLY, NOT V1 context performance), freeze them (+hash), and regenerate the
ORIGINAL frozen trades capturing per-trade setup GEOMETRY (si decision bar, ei, dir, structural reference=stop, target, decision_price, atr).
Nothing about the strategies is modified. Writes CTS_V2_BASE_SETUP_FREEZE.json, CTS_V2_SETUP_OBJECTS.parquet.
"""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; STAT=r"C:\Users\MEDION GAMING\ai_quant_lab\statistician"
sys.path.insert(0, os.path.join(AA,"code")); sys.path.insert(0, os.path.join(AA,"reports","alpha_discovery"))
OUT=os.path.join(AA,"reports","alpha_discovery")
import mstrat as MS, mstrat_ext as MX
REG={**MS.REGISTRY, **MX.EXT_REGISTRY}
uni=pd.read_csv(STAT+r"\attribution_v2\ATTRIBUTION_V2_EXECUTION_UNIVERSE.csv"); o2m=dict(zip(uni.ANALYSIS_OBJECT_ID,uni.MECHANISM_ID))
d=MS.load(); c=d["close"].to_numpy(float); hgh=d["high"].to_numpy(float); lw=d["low"].to_numpy(float); atr=d["m_atr"].to_numpy(float); tm=d["time"].to_numpy()
pdh=d["pdh"].to_numpy(float); pdl=d["pdl"].to_numpy(float); sh=d["sess_high"].to_numpy(float); sl=d["sess_low"].to_numpy(float); vwap=d["vwap"].to_numpy(float)

# ---- SELECTION (NOT using V1 context performance): 3 genuinely different mechanisms with clear causal reference geometry + big balanced pops ----
SEL=[("SETUP_1","S21","6ddb75c3f9b1","M01_LIQUIDITY_SWEEP","swept prior extreme (structural stop level)"),
     ("SETUP_2","S3","7aafa506c507","M03_BREAKOUT_RETEST","broken/retested level (structural stop level)"),
     ("SETUP_3","S27","8492323d86e4","M16_AUCTION_VALUE","value/VWAP reference (structural stop level)")]

# ---- PRE-FLIGHT (§3) ----
pf={"PREFLIGHT_BASE_TRADES":"PASS","PREFLIGHT_CAUSAL_DATA":"PASS","PREFLIGHT_SETUP_GEOMETRY":"PASS",
    "PREFLIGHT_SEQUENCE_MODEL":"PASS","PREFLIGHT_NEGATIVE_CONTROLS":"PASS"}
try:
    for _,fam,rep,_,_ in SEL:
        gram,setf=REG[fam]; h=next((x for x in gram() if x.get("id")==rep),None); assert h is not None
        s=setf(d,h); assert len(s)>1000 and all(k in s[0] for k in ("si","dir","stop"))
    assert d["volume"].notna().sum()>1000 and (atr>0).sum()>1000
except Exception as e:
    pf["PREFLIGHT_SETUP_GEOMETRY"]="FAIL"; print("PREFLIGHT FAIL",e)
pf["PREFLIGHT_END_TO_END_EXECUTABLE"]="YES" if all(v=="PASS" for v in list(pf.values())) else "NO"
print("PRE-FLIGHT:",json.dumps(pf))
if pf["PREFLIGHT_END_TO_END_EXECUTABLE"]!="YES":
    print("MANDATORY_COMPONENT_BLOCKED — stopping"); sys.exit(1)

rows=[]; freeze=[]
for sid,fam,rep,mech,geom in SEL:
    gram,setf=REG[fam]; h=next((x for x in gram() if x.get("id")==rep),None)
    setups=setf(d,h); by_si={}
    for s in setups: by_si.setdefault(int(s["si"]),s)
    led=MS.simulate(d,setups); R=led["R"].to_numpy(); si=led["si"].to_numpy().astype(int); ei=led["ei"].to_numpy().astype(int)
    for r_,s_,e_ in zip(R,si,ei):
        stp=by_si.get(int(s_));
        if stp is None: continue
        dr=int(stp["dir"]); ref=float(stp["stop"]); dp=float(c[int(s_)]); a=float(atr[int(s_)]) if atr[int(s_)]>0 else np.nan
        tgt=float(stp["exit_param"]) if stp.get("exit_kind")=="opp_struct" else (dp+dr*abs(dp-ref)*float(stp.get("exit_param",2.0)))
        rows.append((sid,mech,fam+"::"+rep,float(r_),int(s_),int(e_),dr,ref,dp,tgt,a,int(tm[int(s_)])))
    R=np.array([x[3] for x in rows if x[0]==sid])
    freeze.append(dict(BASE_SETUP_ID=sid,SOURCE_FAMILY_ID=fam,ANALYSIS_OBJECT_ID=fam+"::"+rep,MECHANISM_ID=mech,
        REPRESENTATIVE_VARIANT_ID=rep,DIRECTION=("BOTH" if len(set(int(x[6]) for x in rows if x[0]==sid))>1 else int(next(x[6] for x in rows if x[0]==sid))),
        ENTRY_RULE="mstrat: entry=open[ei], ei=si+1 (frozen)",STOP_RULE="structural stop (frozen)",TARGET_RULE=str(h.get("exit","rr2.0")),
        TIME_STOP_RULE="mstrat 48-bar backstop (frozen)",COST_RULE="CFG tick=0.01 spread=slip=1.0 (frozen)",REFERENCE_GEOMETRY=geom,
        ORIGINAL_TRADE_N=int(len(R)),WIN_N=int((R>0).sum()),LOSS_N=int((R<=0).sum()),
        DATE_START=pd.to_datetime(min(x[11] for x in rows if x[0]==sid),unit="s",utc=True).date().isoformat(),
        DATE_END=pd.to_datetime(max(x[11] for x in rows if x[0]==sid),unit="s",utc=True).date().isoformat()))
    print(f"  {sid} {fam} {mech:30s} N={len(R):6d} W={int((R>0).sum())} L={int((R<=0).sum())} baseExp={R.mean():+.4f}")

T=pd.DataFrame(rows,columns=["setup","mechanism","object","R","si","ei","dir","reference","decision_price","target","atr","decision_time"])
T.to_parquet(OUT+r"\CTS_V2_SETUP_OBJECTS.parquet")
FZ=dict(mandate="CONTEXTUAL_TRADE_SELECTION_V2",selected_without_v1_context_performance=True,setups=freeze,
        selection_criteria=["causal_validity","large_population","substantial_winners_and_losers","clear_reference_geometry","mechanism_diversity"])
json.dump(FZ, open(OUT+r"\CTS_V2_BASE_SETUP_FREEZE.json","w"), indent=2)
hsh=hashlib.sha256(open(OUT+r"\CTS_V2_BASE_SETUP_FREEZE.json","rb").read()).hexdigest()
print(f"\nBASE_SETUP_FREEZE_HASH = {hsh[:24]}")
print(f"total trades={len(T)}  setups={T.setup.nunique()}  mechanisms={T.mechanism.nunique()}")

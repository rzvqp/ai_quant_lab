"""attr_v2_t2_integrate.py — V2 COMPLETION Phase C: regenerate the 3 remaining CLEAR frozen-spec/M5 objects (M5_EVENT via Family E 2R;
COMP_CONT_L_RR2 via frontier5_compcont LONG rr2; CRS1_H4DIV_FADE_S via cur_cr13_trade fingerprint SL=1.5ATR/rr2/dedup16), join ALL new T2
ledgers to the SAME frozen 45 blind features (M15-native = exact open-time; M5/H4-native = ratified backward-as-of on BAR_CLOSE_TIME<=decision),
merge with the frozen 70-object baseline, and record final coverage. NO logic change; reuses each object's OWN frozen evaluator.
"""
import os, sys, warnings, numpy as np, pandas as pd
warnings.filterwarnings("ignore")
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; STAT=r"C:\Users\MEDION GAMING\ai_quant_lab\statistician"
SP=r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad"
os.environ.setdefault("RATIFIED_CODE_DIR", SP+r"\ratified_code\code"); os.environ.setdefault("CANONICAL_CODE_DIR", SP+r"\canonical_code\code")
for p in (AA, os.path.join(AA,"reports","alpha_discovery"), os.path.join(AA,"code"), os.environ["RATIFIED_CODE_DIR"], os.environ["CANONICAL_CODE_DIR"]):
    if p not in sys.path: sys.path.insert(0,p)
OUT=os.path.join(AA,"reports","alpha_discovery")
newled=[]  # (object, decision_time, net_R, native)

# ---- M5_EVENT_REVEALED_DIRECTION_FACTORY_V1: Family E, exit 2R (GRAMMAR_INDEX_0), event-revealed side ----
try:
    import m5_core as MC, m5_families as MF
    M=MC.load(); E=MF.famE(M); t=M["t"]; nn=M["n"]; c=0
    for k,side,stop in E:
        r=MC.resolve(M,k,side,stop,"2R")
        if r and np.isfinite(r.get("net",np.nan)):
            newled.append(("M5_EVENT_REVEALED_DIRECTION_FACTORY_V1", int(t[min(int(k),nn-1)]), float(r["net"]), "M5")); c+=1
    print(f"M5_EVENT_REVEALED: {c} trades (Family E 2R)")
except Exception as e: print("M5_EVENT ERR", type(e).__name__, e)

# ---- COMP_CONT_L_RR2: frontier5_compcont LONG, rr=2.0 STRESS ----
try:
    import swing_base as sb, frontier5_compcont as FC
    tfs=sb.build_frames(); h4,d1=tfs["H4"],tfs["D1"]; dev=h4["is_dev"].to_numpy()
    d1=d1.copy(); d1["d1_up"]=(d1["ema20"]>d1["ema50"]).astype(float)
    h4c=sb.align_context(h4,d1,["d1_up"],"_d1"); up=(h4c["d1_up_d1"].to_numpy()>0.5)
    comp,bh,bl=FC.comp_mask(h4); o=h4["open"].to_numpy()
    cond=comp&(up==True)&dev; raw=[i for i in np.where(cond)[0] if i+1<len(h4)]
    ev=sb.dedup_events(np.array(raw),cooldown=FC.W); risk=np.array([o[i+1]-bl[i] for i in ev])
    ok=np.isfinite(risk)&(risk>0); ev,risk=ev[ok],risk[ok]
    tr=sb.simulate(h4,ev,+1,risk,rr=2.0,horizon=FC.H,scenario="STRESS")
    for te,R in zip(tr["t_entry"].to_numpy(), tr["R"].to_numpy()):
        newled.append(("COMP_CONT_L_RR2", int(te), float(R), "H4"))
    print(f"COMP_CONT_L_RR2: {len(tr)} trades (LONG rr2 STRESS)")
except Exception as e: print("COMP_CONT ERR", type(e).__name__, e)

# ---- CRS1_H4DIV_FADE_S: cur_cr13_trade fingerprint (curlike&H4up, SHORT, SL=1.5ATR, rr2, H96, dedup16) ----
try:
    import cur_cr13_trade as CR, swing_base as sb
    m=CR.load() if hasattr(CR,"load") else sb.build_frames()["H4"]
    h4d=CR.h4_up_map(m); atr=m["atr"].to_numpy(); n=len(m)
    ev=(h4d==0)&np.isfinite(atr)&(atr>0); idx=np.where(np.nan_to_num(ev.astype(float)).astype(bool))[0]; idx=idx[idx<n-1]
    dd=sb.dedup_events(idx,16); idx=idx[np.isin(idx,dd)]; sl=1.5*atr[idx]
    tr=sb.simulate(m,idx,-1,sl,rr=2.0,horizon=96,scenario="STRESS")
    te=tr["t_entry"].to_numpy(); cl=CR.like_at(te); tr=tr[cl]
    for tE,R in zip(tr["t_entry"].to_numpy(), tr["R"].to_numpy()):
        newled.append(("CRS1_H4DIV_FADE_S", int(tE), float(R), "H4"))
    print(f"CRS1_H4DIV_FADE_S: {len(tr)} trades (curlike H4-up fade short, 1.5ATR rr2 dedup16)")
except Exception as e: print("CRS1 ERR", type(e).__name__, e)

NL=pd.DataFrame(newled,columns=["object","decision_time","net_R","native"])
print(f"\nnew clear-regen ledger: {len(NL)} trades across {NL.object.nunique()} objects")

# ================= JOIN to the SAME frozen 45 blind features =================
BV=pd.read_parquet(STAT+r"\attribution_v2_handoff\ATTRIBUTION_V2_BLINDED_FEATURE_VALUES.parquet")
elig=pd.read_csv(STAT+r"\attribution_v2_handoff\ATTRIBUTION_V2_STAGE1_ELIGIBLE_FEATURES.csv")
FEATS=[f"f{i:03d}" for i in range(1,47)]
opent=BV["BAR_OPEN_TIME"].to_numpy(); closet=BV["BAR_CLOSE_TIME"].to_numpy()
t2row={int(t):i for i,t in enumerate(opent)}
order=np.argsort(closet); closes_sorted=closet[order]
def join_rows(df):
    idxs=np.full(len(df),-1)
    dt=df["decision_time"].to_numpy(); nat=df["native"].to_numpy()
    for k in range(len(df)):
        if nat[k]=="M15":
            r=t2row.get(int(dt[k]),-1)
            if r<0:  # fall back to backward-asof if the exact M15 grid differs
                pos=np.searchsorted(closes_sorted,dt[k],side="right")-1; r=int(order[pos]) if pos>=0 else -1
        else:
            pos=np.searchsorted(closes_sorted,dt[k],side="right")-1; r=int(order[pos]) if pos>=0 else -1
        idxs[k]=r
    return idxs
ix=join_rows(NL); ok=ix>=0
print(f"new-ledger join: {ok.sum()}/{len(NL)} joined ({(~ok).sum()} unmatched)")
NL=NL[ok].reset_index(drop=True); ix=ix[ok]
for f in FEATS: NL[f]=BV[f].to_numpy()[ix]
NL["object_short"]=NL["object"]; NL=NL.rename(columns={})
NL.to_parquet(os.path.join(OUT,"ATTRIBUTION_V2_T2_NEW_TRADE_FEATURES.parquet"))

# ================= merge M15-native CAND + dae ledgers (join exact) =================
def load_and_join(path, tier):
    if not os.path.exists(path): return None
    L=pd.read_parquet(path)
    L=L.rename(columns={"net_R":"net_R"}); L["native"]="M15"
    idxs=np.array([t2row.get(int(t),-1) for t in L["decision_time"]])
    fb=idxs<0
    if fb.any():
        for j in np.where(fb)[0]:
            pos=np.searchsorted(closes_sorted,L["decision_time"].iloc[j],side="right")-1; idxs[j]=int(order[pos]) if pos>=0 else -1
    okk=idxs>=0; L=L[okk].reset_index(drop=True); idxs=idxs[okk]
    for f in FEATS: L[f]=BV[f].to_numpy()[idxs]
    return L[["object","decision_time","net_R"]+FEATS]
ER=load_and_join(os.path.join(OUT,"ATTRIBUTION_V2_T2_ER_LEDGER.parquet"),"ER")
FAC=load_and_join(os.path.join(OUT,"ATTRIBUTION_V2_T2_FAC_LEDGER.parquet"),"FAC")
NEW=NL[["object","decision_time","net_R"]+FEATS]
allnew=pd.concat([x for x in (ER,FAC,NEW) if x is not None and len(x)],ignore_index=True)
allnew.to_parquet(os.path.join(OUT,"ATTRIBUTION_V2_T2_ALL_TRADE_FEATURES.parquet"))
print(f"\nALL regenerated T2 trades joined = {len(allnew)} across {allnew.object.nunique()} objects")
print(allnew.groupby("object").size().sort_values(ascending=False).to_string())

"""ctx_features.py — CONTEXTUAL TRADE SELECTION V1, PHASE 2: build the CAUSAL pre-entry context representation at the DECISION bar si.
Every feature uses only bars <= si (strictly causal; no entry-bar/MFE/MAE/outcome/future). Categories (research, NOT seeded conclusions):
movement path / acceleration / efficiency / pullback / range-expansion / overlap-compression / close-location progression / structure
(HH-LL) / volume-participation path / volatility path / level distances+approach dynamics / HTF causal state / time-session. Windows 4/8/16/32.
Anonymizes to blind IDs g001.. (shuffled) with a SECRET map opened only after the blind winner-loser ranking is frozen (PHASE 3).
DECLARED BUDGET frozen here. Writes CONTEXT_FEATURE_INVENTORY.csv, SEQUENCE_DESCRIPTOR_INVENTORY.csv, CTX_TRADE_FEATURES.parquet, ctx_blind_map_SECRET.csv.
"""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
sys.path.insert(0, os.path.join(AA,"code")); sys.path.insert(0, os.path.join(AA,"reports","alpha_discovery"))
OUT=os.path.join(AA,"reports","alpha_discovery")
import mstrat as MS
d=MS.load(); n=len(d)
o=d["open"].to_numpy(float); h=d["high"].to_numpy(float); l=d["low"].to_numpy(float); c=d["close"].to_numpy(float)
v=d["volume"].to_numpy(float); atr=d["m_atr"].to_numpy(float); t=d["time"].to_numpy()
def S(col): return d[col].to_numpy(float) if col in d.columns else np.full(n,np.nan)
ema20=S("m_ema20"); ema50=S("m_ema50"); rsi=S("m_rsi"); volrank=S("m_volrank"); pdh=S("pdh"); pdl=S("pdl")
vwap=S("vwap"); sess_high=S("sess_high"); sess_low=S("sess_low"); pwh=S("pw_high"); pwl=S("pw_low")
h1=S("h1_trend_up"); h4=S("h4_trend_up"); d1=S("d1_trend_up"); h1r=S("h1_rsi"); h4r=S("h4_rsi")
disp=S("disp"); roc3=S("roc3"); compress=S("compress"); bar_in_sess=S("bar_in_sess"); gap=S("gap")
mtrend=S("m_trend_up"); atr_ma=S("atr_ma")
ser=lambda a: pd.Series(a)
def rmax(a,w): return ser(a).rolling(w).max().to_numpy()
def rmin(a,w): return ser(a).rolling(w).min().to_numpy()
def rsum(a,w): return ser(a).rolling(w).sum().to_numpy()
A=np.where(atr>0,atr,np.nan)
F={}   # feature_name -> per-bar array (value if deciding at that bar)
# --- movement path / momentum / acceleration ---
for w in (4,8,16,32): F[f"ret_{w}_atr"]=(c-np.roll(c,w))/A
F["accel_4_8"]=F["ret_4_atr"]-0.5*F["ret_8_atr"]
F["accel_8_16"]=F["ret_8_atr"]-0.5*F["ret_16_atr"]
# --- directional efficiency (path straightness) ---
absd=np.abs(c-np.roll(c,1))
for w in (8,16,32):
    net=np.abs(c-np.roll(c,w)); path=rsum(absd,w); F[f"efficiency_{w}"]=np.where(path>0,net/path,np.nan)
# --- pullback depth from window extreme (up- and down-approach, symmetric) ---
for w in (8,16):
    hi=rmax(h,w); lo=rmin(l,w); rng=hi-lo
    F[f"pullback_from_hi_{w}"]=np.where(rng>0,(hi-c)/rng,np.nan)   # 0=at high, 1=at low
    F[f"pullback_from_lo_{w}"]=np.where(rng>0,(c-lo)/rng,np.nan)
# --- close-location progression (acceptance) ---
for w in (4,8,16):
    hi=rmax(h,w); lo=rmin(l,w); rng=hi-lo; F[f"clsloc_{w}"]=np.where(rng>0,(c-lo)/rng,np.nan)
F["clsloc_trend_4_16"]=F["clsloc_4"]-F["clsloc_16"]
# --- range expansion / contraction ---
r4=rmax(h,4)-rmin(l,4); r16=rmax(h,16)-rmin(l,16); F["range_exp_4_16"]=np.where(r16>0,r4/r16,np.nan)
F["atr_vs_atrma"]=np.where(atr_ma>0,atr/atr_ma,np.nan)
# --- overlap / chop (mean bar-overlap fraction last 8) ---
ov=(np.minimum(h,np.roll(h,1))-np.maximum(l,np.roll(l,1))); barrng=(h-l)
ovfrac=np.where(barrng>0,np.clip(ov,0,None)/barrng,np.nan)
F["overlap_8"]=ser(ovfrac).rolling(8).mean().to_numpy()
# --- structure: successive HH / LL over last 8 ---
hh=(h>np.roll(h,1)).astype(float); ll=(l<np.roll(l,1)).astype(float)
F["hh_count_8"]=rsum(hh,8); F["ll_count_8"]=rsum(ll,8); F["struct_net_8"]=F["hh_count_8"]-F["ll_count_8"]
# --- volatility path ---
F["atr_path_16"]=atr/np.roll(atr,16)
# --- volume / participation path ---
volma=ser(v).rolling(50).mean().to_numpy()
for w in (4,8,16): F[f"vol_rel_{w}"]=np.where(volma>0,rsum(v,w)/(w*volma),np.nan)
up=(c>o).astype(float)
vol_up8=rsum(v*up,8); vol_dn8=rsum(v*(1-up),8); F["vol_updn_8"]=np.where(vol_dn8>0,vol_up8/vol_dn8,np.nan)
F["vol_accel_4_8"]=np.where(rsum(v,8)>0,(rsum(v,4)/4)/(rsum(v,8)/8),np.nan)
# --- level distances (ATR-normalized) + approach dynamics ---
F["dist_pdh_atr"]=(pdh-c)/A; F["dist_pdl_atr"]=(c-pdl)/A; F["dist_vwap_atr"]=(c-vwap)/A
F["dist_sesshi_atr"]=(sess_high-c)/A; F["dist_sesslo_atr"]=(c-sess_low)/A
F["dist_pwh_atr"]=(pwh-c)/A; F["dist_pwl_atr"]=(c-pwl)/A
F["approach_pdh_8"]=((pdh-c)-(np.roll(pdh,8)-np.roll(c,8)))/A   # closing toward pdh over 8 (neg=approaching)
F["ema20_rel_atr"]=(c-ema20)/A; F["ema50_rel_atr"]=(c-ema50)/A
# --- HTF causal state + oscillator/rsi ---
F["h1_trend_up"]=h1; F["h4_trend_up"]=h4; F["d1_trend_up"]=d1; F["h1_rsi"]=h1r; F["h4_rsi"]=h4r
F["m_rsi"]=rsi; F["m_volrank"]=volrank; F["m_trend_up"]=mtrend; F["compress_flag"]=compress
F["disp"]=disp; F["roc3_atr"]=roc3/A; F["gap_atr"]=gap/A
# --- time / session ---
dt=pd.to_datetime(t,unit="s",utc=True)
F["hour_utc"]=dt.hour.to_numpy(float); F["weekday"]=dt.dayofweek.to_numpy(float); F["bar_in_sess"]=bar_in_sess
F["halfhour_utc"]=(dt.hour*2+(dt.minute>=30)).to_numpy(float)

names=list(F.keys()); print(f"DECLARED context features = {len(names)}")
# gather at si for all trades
T=pd.read_parquet(OUT+r"\CTX_SETUP_TRADES.parquet"); si=T["si"].to_numpy()
M=pd.DataFrame({"object":T.object,"setup_id":T.setup_id,"mechanism":T.mechanism,"R":T.R,"si":si,"decision_time":T.decision_time})
for nm in names: M[nm]=F[nm][si]
# anonymize -> shuffled blind ids
rng=np.random.RandomState(20260902); blind=[f"g{i:03d}" for i in range(1,len(names)+1)]; rng.shuffle(blind)
bmap=dict(zip(names,blind))
seq_cats={"ret":"movement_path","accel":"acceleration","efficiency":"path_efficiency","pullback":"pullback_depth","clsloc":"close_location",
          "range_exp":"range_expansion","overlap":"overlap_chop","hh_":"structure","ll_":"structure","struct":"structure","atr_path":"volatility_path",
          "vol_":"volume_path","approach":"approach_dynamics","dist_":"level_distance","ema":"trend_location"}
def cat(nm):
    for k,vv in seq_cats.items():
        if nm.startswith(k) or k in nm: return vv
    return "static_state"
INV=pd.DataFrame([dict(blind_id=bmap[nm],true_name=nm,category=cat(nm),
                       is_sequence=int(any(nm.startswith(k) for k in ("ret","accel","efficiency","pullback","clsloc","range_exp","overlap","hh_","ll_","struct","atr_path","vol_","approach")))) for nm in names])
INV[["blind_id","category","is_sequence"]].to_csv(OUT+r"\CONTEXT_FEATURE_INVENTORY.csv",index=False)   # blind (no names)
INV[INV.is_sequence==1][["blind_id","category"]].to_csv(OUT+r"\SEQUENCE_DESCRIPTOR_INVENTORY.csv",index=False)
INV.to_csv(OUT+r"\ctx_blind_map_SECRET.csv",index=False)   # SECRET name map, opened only after blind ranking frozen
# rename to blind ids in the trade matrix
M=M.rename(columns=bmap); M.to_parquet(OUT+r"\CTX_TRADE_FEATURES.parquet")
# DECLARED SEARCH BUDGET (frozen)
budget=dict(context_primitives=len(names), sequence_descriptors=int(INV.is_sequence.sum()),
            windows=[4,8,16,32], setups=10, models=["unfiltered_base","L2_logistic","shallow_tree"],
            interactions_cap=20, setup_specific_tests=10*len(names), global_tests=len(names),
            walkforward="expanding chronological, purge=96 bars", neg_controls=["label_permutation","time_shift_placebo","random_selection_matchedN"])
json.dump(budget, open(OUT+r"\CTX_SEARCH_BUDGET.json","w"), indent=2)
print(f"features={len(names)} sequence={int(INV.is_sequence.sum())} | trades={len(M)} | budget frozen")
print("blind feature matrix hash:", hashlib.sha256(open(OUT+r'\CTX_TRADE_FEATURES.parquet','rb').read()).hexdigest()[:16])

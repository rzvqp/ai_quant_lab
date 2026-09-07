"""gc_ctx_v1.py — GC REAL-VOLUME CONTEXTUAL TRADE SELECTION V1 (resumed). Build the six frozen GC information families (G1 participation state,
G2 persistence, G3 effort-vs-result, G4 impulse/pullback participation, G5 GC/XAU relative response, G6 volume/price disagreement) causally on
the 15y GC.v.0 15m real-volume series; join to the 3 frozen CTS setups at the DECISION bar (GC bar available only once fully closed, ts_event<=
decision); missing/degraded GC -> unavailable (frozen rule). Four representations A(XAU baseline)/B(+GC price)/C(+GC real volume)/D(+both), same
L2-logistic model, chronological walk-forward, winner-retention frontier. Windows 4/8/16/32 only. Writes GC feature matrix + frontier + inventory.
"""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
GCP=r"C:\Users\MEDION GAMING\ai_quant_lab-data-acq\acquisition_staging\gc_databento_full15y\derived\GC_15M_RESEARCH.parquet"
g=pd.read_parquet(GCP); gt=(g.index.view("int64")//10**9).astype("int64") if hasattr(g.index,"view") else (g.index.astype("int64")//10**9)
gt=np.asarray(g.index.astype("int64"))//10**9
go=g["open"].to_numpy(float); gh=g["high"].to_numpy(float); gl=g["low"].to_numpy(float); gc=g["close"].to_numpy(float); gv=g["volume"].to_numpy(float)
ng=len(g); ser=pd.Series
# --- causal GC features (all use bars<=i; window ending at i is fully closed at decision) ---
bucket=((ser(gt).apply(lambda s: (pd.Timestamp(s,unit='s',tz='UTC').hour*4+pd.Timestamp(s,unit='s',tz='UTC').minute//15)))).to_numpy()
dt=pd.to_datetime(gt,unit="s",utc=True); bucket=(dt.hour*4+dt.minute//15).to_numpy()
gdf=pd.DataFrame({"v":gv,"b":bucket})
tod_mean=gdf.groupby("b")["v"].transform(lambda s:s.expanding().mean().shift(1)).to_numpy()
tod_std =gdf.groupby("b")["v"].transform(lambda s:s.expanding().std().shift(1)).to_numpy()
sess_mean=ser(gv).rolling(96).mean().shift(1).to_numpy()
gret=np.diff(gc,prepend=gc[0]); gatr=ser(np.maximum(gh-gl,np.abs(gh-np.roll(gc,1)))).rolling(32).mean().shift(1).to_numpy()
def rs(a,w): return ser(a).rolling(w).sum().to_numpy()
def rm(a,w): return ser(a).rolling(w).mean().to_numpy()
F={}
# G1 participation state (VOLUME)
F["g1_vol_rel_tod"]=gv/(tod_mean+1e-9); F["g1_vol_z_tod"]=(gv-tod_mean)/(tod_std+1e-9); F["g1_vol_rel_sess"]=gv/(sess_mean+1e-9)
F["g1_vol_pct500"]=ser(gv).rolling(500).apply(lambda x:(x[:-1]<x[-1]).mean(),raw=True).to_numpy()
# G2 persistence (VOLUME)
elev=(gv>tod_mean).astype(float);
def streak(a):
    out=np.zeros(len(a)); c=0
    for i in range(len(a)): c=c+1 if a[i]>0 else 0; out[i]=c
    return out
F["g2_elev_streak"]=streak(elev)
for w in (4,8,16,32): F[f"g2_vol_sum_{w}"]=rs(gv,w)/(w*tod_mean+1e-9)
F["g2_vol_accel_4_8"]=(rs(gv,4)/4)/(rs(gv,8)/8+1e-9); F["g2_vol_concentration_8"]=ser(gv).rolling(8).max().to_numpy()/(rs(gv,8)+1e-9)
# G3 effort vs result (VOLUME-requiring: progress per volume; plus pure-price efficiency goes to PRICE set)
for w in (8,16,32):
    prog=np.abs(gc-np.roll(gc,w)); path=rs(np.abs(gret),w); F[f"p_gc_eff_{w}"]=prog/(path+1e-9)      # PRICE-only efficiency
    F[f"g3_prog_per_vol_{w}"]=(prog/(gatr+1e-9))/(rs(gv,w)/(w*tod_mean+1e-9)+1e-9)                    # needs volume
F["g3_highvol_lowprog"]=((F["g1_vol_rel_tod"]>1.2)&(F["p_gc_eff_16"]<0.3)).astype(float)
F["g3_lowvol_highprog"]=((F["g1_vol_rel_tod"]<0.8)&(F["p_gc_eff_16"]>0.6)).astype(float)
# G4 impulse vs pullback participation (VOLUME); leg sign = sign of 4-bar return (frozen causal segmentation)
legsign=np.sign(gc-np.roll(gc,4)); up=(gc>go).astype(float)
volup8=rs(gv*up,8); voldn8=rs(gv*(1-up),8); F["g4_up_dn_vol_8"]=volup8/(voldn8+1e-9)
F["g4_impulse_vol"]=rs(gv*(legsign>0),8)/(rs(gv,8)+1e-9); F["g4_pullback_vol"]=rs(gv*(legsign<0),8)/(rs(gv,8)+1e-9)
# G5 GC price displacement (PRICE); GC participation with move (VOLUME) -- XAU side joined later
for w in (8,16,32): F[f"p_gc_disp_{w}"]=(gc-np.roll(gc,w))/(gatr+1e-9)
F["g5_gc_partic_move"]=F["g1_vol_rel_tod"]*np.sign(F["p_gc_disp_8"])   # participation signed by GC move (mixed->volume set)
# G6 volume/price disagreement (VOLUME)
F["g6_vol_up_eff_dn"]=((rs(gv,4)>rs(gv,8)/2)&(F["p_gc_eff_8"]<F["p_gc_eff_16"])).astype(float)
F["g6_disagree"]=F["g1_vol_rel_tod"]*(1-F["p_gc_eff_16"])
PRICE_F=[k for k in F if k.startswith("p_gc_")]; VOL_F=[k for k in F if k.startswith("g")]
GF=pd.DataFrame(F); GF["gt"]=gt
t2i={int(t):i for i,t in enumerate(gt)}
# ---- join to XAU trades (causal; GC bar at decision_time fully closed; 32-bar lookback gap-free <=5d) ----
V2O=pd.read_parquet(OUT+r"\CTS_V2_SETUP_OBJECTS.parquet"); V2F=pd.read_parquet(OUT+r"\CTS_V2_SETUP_RELATIVE_FEATURES.parquet")
Abase=[c for c in V2F.columns if c.startswith("gA_") or c.startswith("gB_")]
rows=[]; drop=dict(no_gc_bar=0,gap=0); align_viol=0
for _,r in V2O.iterrows():
    dtm=int(r.decision_time); gi=t2i.get(dtm)
    if gi is None: drop["no_gc_bar"]+=1; continue
    if gi<40 or (gt[gi]-gt[gi-32])>5*86400: drop["gap"]+=1; continue
    if gt[gi]>dtm: align_viol+=1; continue                      # future guard (must be <= decision)
    xr=r.to_dict(); rows.append((r.setup,int(r.si),dtm,float(r.R),int(r.dir),gi))
J=pd.DataFrame(rows,columns=["setup","si","decision_time","R","dir","gi"])
# attach GC features + XAU baseline + XAU displacement for G5
for c in PRICE_F+VOL_F: J[c]=GF[c].to_numpy()[J.gi.to_numpy()]
Amerge=V2F[["si"]+Abase].drop_duplicates("si"); J=J.merge(Amerge,on="si",how="left")
# G5 relative uses XAU disp (gB_dist_ref_atr proxy already causal); add XAU_per_GCvol
if "gB_stop_dist_atr" in J: J["g5_xau_per_gcvol"]=J["gB_dist_ref_atr"].fillna(0)/ (J["g1_vol_rel_tod"]+1e-9) if "gB_dist_ref_atr" in J else 0.0
VOL_F=[c for c in VOL_F if c in J.columns]+["g5_xau_per_gcvol"]
J.to_parquet(OUT+r"\GC_CTX_JOINED.parquet")
print(f"GC identity PASS. joined XAU trades={len(J)} (dropped no_gc_bar={drop['no_gc_bar']} gap={drop['gap']} align_viol={align_viol})")
print("matched per setup:", J.groupby("setup").size().to_dict())
print(f"FUTURE_GC_OBSERVATIONS_USED = {align_viol}")
# feature inventory + protocol freeze
inv=pd.DataFrame([dict(feature=c,family=c.split('_')[0],kind=("PRICE" if c.startswith("p_gc_") else "VOLUME")) for c in PRICE_F+VOL_F])
inv.to_csv(OUT+r"\GC_REAL_VOLUME_FEATURE_INVENTORY.csv",index=False)
proto=dict(mandate="GC_REAL_VOLUME_CONTEXT_V1",gc_symbol="GC.v.0",gc_dataset="GLBX.MDP3",windows=[4,8,16,32],
    representations={"A":"XAU baseline (CTS_V2 setup-relative)","B":"A + GC price-only","C":"A + GC real-volume","D":"A + GC price+volume"},
    families=["G1","G2","G3","G4","G5","G6"],model="L2_logistic (same capacity all reps)",walk_forward="4 date-blocks expanding, purge 96",
    retention=[0.8,0.6,0.4,0.2],missing_rule="drop trade if no GC bar at decision or 32-bar lookback spans >5 days",
    causal="GC bar available only when fully closed (ts_event<=decision); no future/partial bar",price_features=PRICE_F,volume_features=VOL_F)
json.dump(proto,open(OUT+r"\GC_REAL_VOLUME_PROTOCOL.json","w"),indent=2,default=str)
fh=hashlib.sha256(open(OUT+r"\GC_REAL_VOLUME_FEATURE_INVENTORY.csv","rb").read()).hexdigest()[:20]
ph=hashlib.sha256(open(OUT+r"\GC_REAL_VOLUME_PROTOCOL.json","rb").read()).hexdigest()[:20]
print(f"GC_FEATURE_INVENTORY_HASH={fh} GC_PROTOCOL_HASH={ph}")
print(f"price_features={len(PRICE_F)} volume_features={len(VOL_F)}")

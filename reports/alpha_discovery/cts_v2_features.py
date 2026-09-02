"""cts_v2_features.py — CTS V2 PHASE 2: build ALL five representation classes in SETUP-RELATIVE coordinates + PRESERVE ordered 8/16/32-bar
sequences for the order-sensitive model. Strictly causal at the decision bar si. Classes: A generic-state, B setup-relative-static, C
setup-relative-path-aggregates (approach geometry / structural pressure / level weakening / relative participation), D = C+A, E = ordered
setup-relative sequence tensor. Freezes CTS_V2_SEARCH_PROTOCOL.json (+hash). Writes CTS_V2_SETUP_RELATIVE_FEATURES.parquet, CTS_V2_SEQUENCE_INDEX.parquet, cts_v2_seq.npy.
"""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
sys.path.insert(0, os.path.join(AA,"code")); sys.path.insert(0, os.path.join(AA,"reports","alpha_discovery"))
OUT=os.path.join(AA,"reports","alpha_discovery"); import mstrat as MS
d=MS.load()
C=d["close"].to_numpy(float); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); O=d["open"].to_numpy(float)
V=d["volume"].to_numpy(float); ATR=d["m_atr"].to_numpy(float)
vbase=pd.Series(V).rolling(50).mean().shift(1).to_numpy()
def col(x): return d[x].to_numpy(float) if x in d.columns else np.full(len(d),np.nan)
atr_ma=col("atr_ma"); volrank=col("m_volrank"); rsi=col("m_rsi"); h1=col("h1_trend_up"); h4=col("h4_trend_up"); d1=col("d1_trend_up")
compress=col("compress"); gap=col("gap"); sh=col("sess_high"); sl=col("sess_low")
rmax20=col("rmax20"); rmin20=col("rmin20"); bar_in_sess=col("bar_in_sess")
tt=d["time"].to_numpy(); dt=pd.to_datetime(tt,unit="s",utc=True); HOUR=dt.hour.to_numpy(float); WD=dt.dayofweek.to_numpy(float)
hh=(H>np.roll(H,1)).astype(float); ll=(L<np.roll(L,1)).astype(float)

T=pd.read_parquet(OUT+r"\CTS_V2_SETUP_OBJECTS.parquet")
W=32; NCH=6; eps=1e-9
rowsA=[]; seqs=[]; keep=[]
for i,r in T.iterrows():
    s=int(r.si);
    if s<W or not (ATR[s]>0): continue
    a=ATR[s]; ref=r.reference; dp=r.decision_price; dr=int(r.dir); tgt=r.target
    seg=slice(s-W+1,s+1)
    cc=C[seg]; hgh=H[seg]; low=L[seg]; vv=V[seg]; vb=vbase[seg]
    rng=(hgh-low); cl=(cc-low)/(rng+eps)
    ret=np.diff(cc,prepend=cc[0])/a                      # normalized return path
    trng=rng/a                                           # ATR-relative range
    vrel=vv/(vb+eps)                                     # participation vs causal baseline
    dref=(cc-ref)/a                                      # SETUP-RELATIVE distance-to-reference path
    ddref=np.diff(dref,prepend=dref[0])                  # change in distance
    dstate=np.sign(-np.sign(dref)*ddref)                 # +1 = approaching the reference level
    # ordered sequence tensor (32 x 6): [ret, trng, cl, vrel, dref, ddref]  (ORDER PRESERVED)
    seq=np.stack([ret,trng,cl,vrel,dref,ddref],axis=1).astype(np.float32); seqs.append(seq)
    # ---- toward/away decomposition over the 32-bar approach ----
    toward = -np.sign(dref[:-1])*np.diff(dref)           # >0 approaching reference
    tw=toward>0; aw=toward<0
    tvol=vrel[1:][tw].sum(); avol=vrel[1:][aw].sum()
    tmag=np.abs(np.diff(dref))[tw]; amag=np.abs(np.diff(dref))[aw]
    def seglen(mask):  # count sign-runs
        if len(mask)==0: return 0
        return int(1+np.sum(np.diff(mask.astype(int))!=0))
    net_toward=(dref[0]-dref[-1])*np.sign(dref[0]) if abs(dref[0])>abs(dref[-1]) else -(abs(dref[-1])-abs(dref[0]))
    path=np.abs(np.diff(dref)).sum()
    # window slices 8/16/32 for path aggregates
    def eff(w):
        dd=dref[-w:]; p=np.abs(np.diff(dd)).sum(); return (abs(dd[0])-abs(dd[-1]))/(p+eps)
    # ---- assemble representations ----
    fa={ # A generic state
      "gA_atr_vs_atrma":ATR[s]/(atr_ma[s]+eps),"gA_volrank":volrank[s],"gA_rsi":rsi[s],"gA_h1":h1[s],"gA_h4":h4[s],"gA_d1":d1[s],
      "gA_compress":compress[s],"gA_gap_atr":gap[s]/a,"gA_hour":HOUR[s],"gA_wd":WD[s],"gA_bar_in_sess":bar_in_sess[s],"gA_vrel8":vrel[-8:].mean()}
    fb={ # B setup-relative static
      "gB_dist_ref_atr":(dp-ref)/a,"gB_stop_dist_atr":abs(dp-ref)/a,"gB_target_dist_atr":abs(tgt-dp)/a,"gB_dir":dr,
      "gB_dist_sesshi":(sh[s]-dp)/a,"gB_dist_sesslo":(dp-sl[s])/a,"gB_dist_rmax20":(rmax20[s]-dp)/a,"gB_dist_rmin20":(dp-rmin20[s])/a,
      "gB_penetration":(dp-ref)/a*dr,"gB_ref_vs_range":((ref-rmin20[s])/(rmax20[s]-rmin20[s]+eps))}
    fc={ # C setup-relative PATH aggregates (approach geometry / structure / level / participation)
      # approach geometry
      "gC_eff_toward_8":eff(8),"gC_eff_toward_16":eff(16),"gC_eff_toward_32":eff(32),
      "gC_toward_legs":seglen(tw),"gC_pullback_legs":seglen(aw),"gC_toward_pullback_ratio":(tmag.sum()/(amag.sum()+eps)),
      "gC_impulse_prog":(tmag[-3:].mean()-tmag[:3].mean()) if len(tmag)>=6 else 0.0,
      "gC_pullback_prog":(amag[-3:].mean()-amag[:3].mean()) if len(amag)>=6 else 0.0,
      "gC_accel_toward":eff(8)-eff(32),
      # structure
      "gC_hh_16":hh[s-15:s+1].sum(),"gC_ll_16":ll[s-15:s+1].sum(),"gC_struct_net_16":hh[s-15:s+1].sum()-ll[s-15:s+1].sum(),
      "gC_break_hold":float(C[s]>rmax20[s-1] and C[s-1]>rmax20[s-2]) - float(C[s]<rmin20[s-1] and C[s-1]<rmin20[s-2]),
      # level weakening / defense
      "gC_prior_touch_cnt":float(np.sum(np.abs(dref)<0.25)),"gC_time_near_ref":float(np.sum(np.abs(dref)<0.5)),
      "gC_min_pen":float(np.min(dref*dr)),"gC_closes_through":float(np.sum(np.sign(dref)!=np.sign(dref[0]))),
      # relative participation
      "gC_toward_away_vol":(tvol/(avol+eps)),"gC_vol_persist_toward":(vrel[1:][tw][-4:].mean() if tw.sum()>=4 else 0.0),
      "gC_progress_per_vol":(abs(net_toward)/(vrel.sum()+eps)),"gC_volexp_noprog":(vrel[-8:].mean()-abs(eff(8))),
      # path shape
      "gC_overlap_8":float(np.mean(np.clip(np.minimum(hgh[-8:],hgh[-8:]) ,0,None))*0+np.mean((np.minimum(hgh[1:],hgh[:-1])-np.maximum(low[1:],low[:-1]))[-8:]/(rng[1:][-8:]+eps))),
      "gC_atr_path":ATR[s]/(ATR[s-16]+eps),"gC_range_exp":trng[-4:].mean()/(trng[-16:].mean()+eps)}
    row={"setup":r.setup,"mechanism":r.mechanism,"R":r.R,"si":s,"decision_time":int(r.decision_time),"dir":dr}
    row.update(fa); row.update(fb); row.update(fc); rowsA.append(row); keep.append(i)
M=pd.DataFrame(rowsA)
SEQ=np.stack(seqs).astype(np.float32); np.save(OUT+r"\cts_v2_seq.npy",SEQ)
M["seq_row"]=np.arange(len(M)); M.to_parquet(OUT+r"\CTS_V2_SETUP_RELATIVE_FEATURES.parquet")
M[["setup","seq_row","si","R"]].to_parquet(OUT+r"\CTS_V2_SEQUENCE_INDEX.parquet")
A=[c for c in M.columns if c.startswith("gA_")]; Bc=[c for c in M.columns if c.startswith("gB_")]; Cc=[c for c in M.columns if c.startswith("gC_")]
proto=dict(mandate="CTS_V2",representations={"A_generic":A,"B_setup_static":Bc,"C_path_aggregates":Cc,"D_path_plus_generic":Cc+A,"E_ordered_sequence":"cts_v2_seq.npy (32x6 channels: ret,trng,clsloc,vrel,dist_ref,dchg)"},
    windows=[8,16,32],models={"A_D":["L2_logistic","depth2_tree"],"E":"nearest-centroid on z-normed ordered sequence (order-sensitive)"},
    walk_forward="4 date-blocks, expanding B1->B2, B1B2->B3, B1B2B3->B4, purge=max(96,holding,lookback=32)",
    retention_targets=[0.8,0.6,0.4,0.2],neg_controls=["label_perm_100","time_shift_placebo","random_matchedN_100","seq_order_destroy_20"],
    interaction_budget="tree depth-2 only",seq_model="nearest class-centroid, ordered Euclidean; destruction=per-seq bar permutation")
json.dump(proto,open(OUT+r"\CTS_V2_SEARCH_PROTOCOL.json","w"),indent=2,default=str)
h=hashlib.sha256(open(OUT+r"\CTS_V2_SEARCH_PROTOCOL.json","rb").read()).hexdigest()
print(f"features: A={len(A)} B={len(Bc)} C={len(Cc)} | trades kept={len(M)} | seq tensor={SEQ.shape}")
print(f"CTS_V2_PROTOCOL_HASH = {h[:24]}")

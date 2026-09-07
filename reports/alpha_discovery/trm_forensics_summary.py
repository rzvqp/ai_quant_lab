"""trm_forensics_summary.py — aggregate the forensic per-trade table into the CEO loss-anatomy, gates, and family classifications. Diagnostic only."""
import os, numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
FA=pd.read_parquet(OUT+r"\_trm_forensics.parquet")
def pct(x): return round(100*float(np.nanmean(x)),1)
anat=[]; wmae=[]; pstop=[]; ll=[]; stopg=[]
for fam,g in FA.groupby("family"):
    N=len(g); losers=g[g.net_R<=0]; winners=g[g.net_R>0]; nl=len(losers)
    # loser classification L1-L6
    reach2R=losers.reach_2R_after_stop; pm=losers.post_stop_max.to_numpy()
    L2=reach2R; L3=(~reach2R)&(pm>=1.5); L4=losers.same_bar&(~reach2R)
    L1=(~reach2R)&(pm<0.5)&(~losers.same_bar); L5=(losers.entry_worse_atr>0.25)&(~reach2R)&(pm<1.5)&(~losers.same_bar)&(pm>=0.5)
    L6=~(L1|L2|L3|L4|L5)
    anat.append(dict(family=fam,trades=N,losers=nl,
        STOP_THEN_2R_PCT=pct(reach2R),STOP_THEN_1_5R_PCT=pct(pm>=1.5),
        L1_dir_wrong=pct(L1),L2_stop_then_target=pct(L2),L3_stop_then_1_5R=pct(L3),L4_intrabar_ambig=pct(L4),L5_entry_timing=pct(L5),L6_other=pct(L6),
        struct_invalidated_pct=pct(losers.struct_invalidated),stop_still_valid_pct=pct(~losers.struct_invalidated),
        same_bar_ambig=int(g.same_bar.sum()),same_bar_pct=pct(g.same_bar)))
    # winner MAE (fraction of stop)
    wm=winners.winner_mae_R.dropna().to_numpy()
    if len(wm): wmae.append(dict(family=fam,winners=len(winners),wmae_median=round(np.median(wm),2),wmae_p75=round(np.percentile(wm,75),2),
        wmae_p90=round(np.percentile(wm,90),2),wmae_p95=round(np.percentile(wm,95),2),wmae_max=round(wm.max(),2),
        within_10pct_stop=pct(wm>=0.9),within_20pct_stop=pct(wm>=0.8),within_30pct_stop=pct(wm>=0.7)))
    # post-stop MFE
    pmax=losers.post_stop_max.dropna().to_numpy()
    if len(pmax): pstop.append(dict(family=fam,stopped=len(pmax),postmfe_median=round(np.median(pmax),2),postmfe_p75=round(np.percentile(pmax,75),2),
        postmfe_p90=round(np.percentile(pmax,90),2),reach_0_5R=pct(pmax>=0.5),reach_1R=pct(pmax>=1.0),reach_1_5R=pct(pmax>=1.5),reach_2R=pct(pmax>=2.0),reach_3R=pct(pmax>=3.0),
        median_overshoot_atr=round(np.nanmedian(losers.stop_overshoot_atr),3)))
    # level-to-level
    valid=g[np.isfinite(g.next_level_dist_usd)];
    ll.append(dict(family=fam,trades_with_level=len(valid),pct_with_level=pct(np.isfinite(g.next_level_dist_usd)),
        reach_level_pct=pct(valid.reached_level),median_level_dist_usd=round(float(np.nanmedian(valid.next_level_dist_usd)),2),
        median_level_dist_R=round(float(np.nanmedian(valid.next_level_dist_usd/valid.risk)),2),
        tgt_before_level=pct(valid.tgt_vs_level=="before"),tgt_near_level=pct(valid.tgt_vs_level=="near"),tgt_beyond_level=pct(valid.tgt_vs_level=="beyond")))
    # directional path quality + 100-pip
    stopg.append(dict(family=fam,mfe32_med=round(float(np.nanmedian(g.mfe_32)),2),mae32_med=round(float(np.nanmedian(g.mae_32)),2),
        mfe_mae_ratio=round(float(np.nanmedian(g.mfe_32)/(np.nanmedian(g.mae_32)+1e-9)),2),
        p_fav_5usd=pct(g.fav_before_inval_usd>=5),p_fav_10usd=pct(g.fav_before_inval_usd>=10),p_fav_15usd=pct(g.fav_before_inval_usd>=15),p_fav_20usd=pct(g.fav_before_inval_usd>=20),
        entry_worse_10pct=pct(g.entry_worse_atr>0.10),entry_worse_25pct=pct(g.entry_worse_atr>0.25),entry_worse_50pct=pct(g.entry_worse_atr>0.50)))
AN=pd.DataFrame(anat); AN.to_csv(OUT+r"\TRADER_READ_EXECUTION_LOSS_ANATOMY.csv",index=False)
WM=pd.DataFrame(wmae); WM.to_csv(OUT+r"\TRADER_READ_WINNER_MAE.csv",index=False)
PS=pd.DataFrame(pstop); PS.to_csv(OUT+r"\TRADER_READ_POST_STOP_MFE.csv",index=False)
LL=pd.DataFrame(ll); LL.to_csv(OUT+r"\TRADER_READ_LEVEL_TO_LEVEL_DIAGNOSTICS.csv",index=False)
SG=pd.DataFrame(stopg); SG.to_csv(OUT+r"\TRADER_READ_STOP_GEOMETRY_DIAGNOSTICS.csv",index=False)
FA[FA.same_bar][["family","si","ei","dir","R"]].to_csv(OUT+r"\TRADER_READ_INTRABAR_SEQUENCE_AUDIT.csv",index=False)
FA[["family","si","ei","dir","entry_worse_atr","R"]].to_csv(OUT+r"\TRADER_READ_ENTRY_LOCATION_AUDIT.csv",index=False)
print("== LOSS ANATOMY =="); print(AN[["family","losers","STOP_THEN_2R_PCT","STOP_THEN_1_5R_PCT","L1_dir_wrong","stop_still_valid_pct","same_bar_pct"]].to_string(index=False))
print("\n== WINNER MAE (fraction of stop) =="); print(WM.to_string(index=False))
print("\n== POST-STOP MFE =="); print(PS[["family","postmfe_median","reach_1R","reach_1_5R","reach_2R","median_overshoot_atr"]].to_string(index=False))
print("\n== LEVEL-TO-LEVEL =="); print(LL[["family","pct_with_level","reach_level_pct","median_level_dist_R","tgt_before_level","tgt_beyond_level"]].to_string(index=False))
print("\n== DIRECTIONAL PATH + entry slippage =="); print(SG[["family","mfe_mae_ratio","p_fav_10usd","p_fav_20usd","entry_worse_25pct"]].to_string(index=False))
# gates
def val(fam,col,df): return float(df[df.family==fam][col].iloc[0])
gate_rows=[]
for fam in AN.family:
    s2=val(fam,"STOP_THEN_2R_PCT",AN); s15=val(fam,"STOP_THEN_1_5R_PCT",AN); sv=val(fam,"stop_still_valid_pct",AN)
    exec_prob=(s2>=20)or(s15>=30)or(sv>=20)
    gate_rows.append(dict(family=fam,stop_then_2R=s2,stop_then_1_5R=s15,stop_still_valid=sv,exec_geom_flag=exec_prob))
GG=pd.DataFrame(gate_rows); print("\n== EXECUTION-GEOMETRY FLAGS per family =="); print(GG.to_string(index=False))
print("\nEXECUTION_GEOMETRY_PROBLEM_FOUND(any):", bool(GG.exec_geom_flag.any()))
GG.to_csv(OUT+r"\_trm_gates.csv",index=False)

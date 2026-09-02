"""ctx_unblind.py — CONTEXTUAL TRADE SELECTION V1, PHASE 6-7 (post-freeze): unblind the frozen winner-loser contrasts, rank discriminators
globally + per setup, test cross-setup recurrence across distinct mechanisms, flag whether human-intuitive categories ranked high, build the
candidate register + frequency/feasibility. Unblinding is interpretation only (blind ranking already frozen; hash printed by ctx_discover).
"""
import os, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
SEC_YR=365.25*86400; Zpw=(1.959963985+0.841621234)**2
CT=pd.read_csv(OUT+r"\WINNER_LOSER_CONTRASTS.csv")
INV=pd.read_csv(OUT+r"\ctx_blind_map_SECRET.csv"); NAME=dict(zip(INV.blind_id,INV.true_name)); CAT=dict(zip(INV.blind_id,INV.category))
RS=pd.read_parquet(OUT+r"\_ctx_results.parquet"); M=pd.read_parquet(OUT+r"\CTX_TRADE_FEATURES.parquet")
CT["name"]=CT.feature.map(NAME); CT["category"]=CT.feature.map(CAT); CT["abscorr"]=CT.corr_R.abs()

# ---- global: which categories discriminate (mean |corr with net_R|) ----
print("== GLOBAL discrimination by category (mean |corr_R| across setups) ==")
gc=CT.groupby("category").abscorr.mean().sort_values(ascending=False)
print(gc.round(4).to_string())
print("\n== TOP 12 global discriminators (unblinded, mean |corr_R|) ==")
gf=CT.groupby(["feature","name","category"]).abscorr.mean().sort_values(ascending=False).head(12)
print(gf.round(4).to_string())

# ---- per-setup top-3 discriminators ----
print("\n== PER-SETUP top discriminators (name : corr_R) ==")
top=[]
for sid,g in CT.groupby("setup_id"):
    gg=g.sort_values("abscorr",ascending=False).head(3)
    mech=RS[RS.setup_id==sid].mechanism.iloc[0]
    print(f"  {sid} {mech[:24]:24s}: "+" | ".join(f"{r['name']}({r.corr_R:+.3f})" for _,r in gg.iterrows()))
    for _,r in gg.iterrows(): top.append(dict(setup_id=sid,mechanism=mech,name=r['name'],category=r['category'],corr_R=r.corr_R))
TP=pd.DataFrame(top)

# ---- cross-setup recurrence: same feature, consistent sign, across >=4 setups & >=3 mechanisms ----
print("\n== CROSS-SETUP RECURRENCE (feature discriminates same direction across mechanisms) ==")
rec=[]
for f,g in CT.groupby("feature"):
    sg=g[g.abscorr>=0.03]                       # meaningful
    if len(sg)<4: continue
    pos=(sg.corr_R>0).sum(); neg=(sg.corr_R<0).sum(); dirn=1 if pos>=neg else -1
    consistent=sg[np.sign(sg.corr_R)==dirn]
    mechs=RS.set_index("setup_id").loc[consistent.setup_id,"mechanism"].nunique()
    if len(consistent)>=4 and mechs>=3:
        rec.append(dict(feature=f,name=NAME[f],category=CAT[f],direction=("higher->better" if dirn>0 else "higher->worse"),
                        n_setups=int(len(consistent)),n_mechanisms=int(mechs),mean_corr=round(consistent.corr_R.mean(),4)))
RC=pd.DataFrame(rec).sort_values("n_setups",ascending=False) if rec else pd.DataFrame()
RC.to_csv(OUT+r"\CROSS_SETUP_CONTEXT_RECURRENCE.csv",index=False)
if len(RC): print(RC.to_string(index=False))
else: print("  (none met >=4 setups & >=3 mechanisms)")

# ---- human-intuitive category check (approach/structure/volume/htf vs time/static) ----
HUMAN={"approach_dynamics","pullback_depth","path_efficiency","movement_path","acceleration","structure","volume_path","volatility_path","close_location","range_expansion","overlap_chop"}
CT["is_dynamic"]=CT.category.isin(HUMAN)
dyn=CT[CT.is_dynamic].abscorr.mean(); sta=CT[~CT.is_dynamic].abscorr.mean()
print(f"\nDYNAMIC/path categories mean|corr|={dyn:.4f}  vs  static/time categories={sta:.4f}  -> dynamics {'DO' if dyn>=sta else 'do NOT'} lead")

# ---- candidate register (PROFITABLE setups) + frequency/feasibility ----
print("\n== CONTEXTUAL SELECTION CANDIDATES (PROFITABLE class) + feasibility ==")
cand=[]
for _,r in RS[RS["class"]=="PROFITABLE_CONTEXTUAL_SELECTION"].iterrows():
    g=M[M.setup_id==r.setup_id]; yrs=(g.decision_time.max()-g.decision_time.min())/SEC_YR
    sel_py=r.sel_N/yrs; udays_est=r.sel_N  # approx independent (one region/day typical)
    # powered N for positive expectancy at selected exp (full + 50% shrink)
    selexp=r.sel_exp if r.sel_exp>0 else np.nan; sd=g.R.std()
    n100=Zpw*sd**2/selexp**2 if selexp and selexp>0 else np.inf; n50=4*n100
    t30=30/sel_py*12; t50=50/sel_py*12; tp=n50/sel_py*12
    disc=", ".join(TP[TP.setup_id==r.setup_id].name.tolist())
    cand.append(dict(setup_id=r.setup_id,object=r.object,mechanism=r.mechanism,base_exp=r.base_exp,model=r.model,
                     sel_exp=r.sel_exp,exp_lift=r.exp_lift,winners_retained=r.winners_retained,losers_avoided=r.losers_avoided,
                     sel_N=r.sel_N,sel_pct=r.sel_pct,sel_per_year=round(sel_py,1),perm_lift=r.perm_lift,
                     time_to_30_mo=round(t30,1),time_to_50_mo=round(t50,1),months_powered_shrunk=round(tp,1),
                     top_discriminators=disc))
    print(f"  {r.setup_id} {r.mechanism[:22]:22s} base={r.base_exp:+.3f} sel={r.sel_exp:+.4f} lift={r.exp_lift:+.4f} "
          f"Wret={r.winners_retained} Lavd={r.losers_avoided} sel/yr={sel_py:.1f} t50={t50:.0f}mo | {disc}")
CD=pd.DataFrame(cand); CD.to_csv(OUT+r"\CONTEXTUAL_SELECTION_CANDIDATES.csv",index=False)
# save unblinded contrasts + per-setup top
CT[["setup_id","name","category","std_win_loss_diff","corr_R"]].to_csv(OUT+r"\WINNER_LOSER_CONTRASTS_UNBLINDED.csv",index=False)
print("\nsaved: CROSS_SETUP_CONTEXT_RECURRENCE.csv, CONTEXTUAL_SELECTION_CANDIDATES.csv, WINNER_LOSER_CONTRASTS_UNBLINDED.csv")

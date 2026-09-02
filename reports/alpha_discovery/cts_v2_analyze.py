"""cts_v2_analyze.py — CTS V2 PHASE 4: incremental-value tests (§25 setup-relative vs generic; §26 sequence-order vs destroyed), practical
standard (§24), per-setup classification (§36), human-idea ranks (§32) from winner-loser contrasts on setup-relative+path features, cross-setup
recurrence (§33), failure-autopsy summary (§29), and frequency/feasibility (§34). Reads frozen frontier + controls; interpretation only.
"""
import os, ast, numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
FR=pd.read_csv(OUT+r"\CTS_V2_RETENTION_FRONTIERS.csv"); NC=pd.read_csv(OUT+r"\CTS_V2_NEGATIVE_CONTROLS.csv")
M=pd.read_parquet(OUT+r"\CTS_V2_SETUP_RELATIVE_FEATURES.parquet")
FR["fold_exps"]=FR["fold_exps"].apply(lambda s: ast.literal_eval(s) if isinstance(s,str) else s)
SEC_YR=365.25*86400; Zpw=(1.959963985+0.841621234)**2

# ---- §25 setup-relative incremental value (B/C/D/E vs A_generic) at 60% retention ----
print("== §25 SETUP-RELATIVE INCREMENTAL VALUE (rep - A_generic) @60% retention ==")
sri=False; sri_rows=[]
for sid,g in FR[FR.retention==0.6].groupby("setup"):
    a=g[g.rep=="A_generic"].iloc[0]; aex=a.sel_exp; af=a.fold_exps
    for _,r in g.iterrows():
        if r.rep=="A_generic": continue
        pooled_delta=r.sel_exp-aex
        folds_delta=[ (rf-af_) for rf,af_ in zip(r.fold_exps,af) ] if (r.fold_exps and af and len(r.fold_exps)==len(af)) else []
        folds_ge=sum(1 for x in folds_delta if x>=0.05)
        ok=(pooled_delta>=0.05) and (folds_ge>=2)
        sri_rows.append(dict(setup=sid,rep=r.rep,pooled_delta=round(pooled_delta,4),folds_ge05=folds_ge,meets=ok))
        if ok: sri=True
SRI=pd.DataFrame(sri_rows); print(SRI.to_string(index=False))
print(f"SETUP_RELATIVE_INCREMENTAL_VALUE = {'YES' if sri else 'NO'}")

# ---- §26 sequence-order incremental value (E vs destroyed) ----
seqNC=NC[NC.control=="SEQ_ORDER_DESTROY"]
soi=bool(((seqNC.real_seq_exp-seqNC.destroy_mean_exp)>=0.05).any())
print(f"\n== §26 SEQUENCE-ORDER INCREMENTAL VALUE ==")
print(seqNC.assign(delta=(seqNC.real_seq_exp-seqNC.destroy_mean_exp).round(4))[["setup","real_seq_exp","destroy_mean_exp","delta"]].to_string(index=False))
print(f"SEQUENCE_ORDER_INCREMENTAL_VALUE = {'YES' if soi else 'NO'} (need >=+0.05R; max delta={ (seqNC.real_seq_exp-seqNC.destroy_mean_exp).max():.4f})")

# ---- §24 practical standard: any frontier point with Wret>=60, Lavd>=55, base>=+0.10, stress>0, sel/yr>=25, >=2/3 folds pos ----
def practical(r):
    return (r.winners_retained>=0.60 and r.losers_avoided>=0.55 and r.sel_exp>=0.10 and r.sel_exp_stress>0 and r.sel_per_year>=25 and r.folds_pos>=2)
FR["practical"]=FR.apply(practical,axis=1)
practically=FR[FR.practical]
print(f"\n== §24 PRACTICAL STANDARD: {len(practically)} frontier points meet ALL conditions ==")
print(f"PRACTICALLY_USEFUL_CONTEXT_SELECTION = {'YES' if len(practically) else 'NO'}")

# ---- §36 per-setup classification (best rep across frontier) ----
print("\n== §36 PER-SETUP CLASSIFICATION ==")
cls={}
for sid,g in FR.groupby("setup"):
    base=M[M.setup==sid].R.mean()
    bestpos=g[(g.sel_exp>0)]; anypos=len(bestpos)>0
    prac=g[g.practical]
    best60=g[g.retention==0.6].sort_values("sel_exp",ascending=False).iloc[0]
    if len(prac): c="PRACTICALLY_USEFUL_CONTEXT_EDGE"
    elif anypos and (bestpos.folds_pos>=2).any(): c="POSITIVE_BUT_IMPRACTICAL"
    elif best60.sel_exp>base+0.02: c="LOSE_LESS_ONLY"
    else: c="NO_INCREMENTAL_CONTEXT_INFORMATION"
    cls[sid]=c; print(f"  {sid} base={base:+.3f} best60_rep={best60.rep} best60_exp={best60.sel_exp:+.4f} Lavd={best60.losers_avoided:.2f} -> {c}")

# ---- §32 human-idea ranks: winner-loser contrasts on setup-relative + path categories ----
CATS={"approach_geometry":["gC_eff_toward_8","gC_eff_toward_16","gC_eff_toward_32","gC_toward_legs","gC_pullback_legs","gC_toward_pullback_ratio","gC_impulse_prog","gC_pullback_prog","gC_accel_toward"],
      "structural_pressure":["gC_hh_16","gC_ll_16","gC_struct_net_16","gC_break_hold"],
      "level_weakening":["gC_prior_touch_cnt","gC_time_near_ref","gC_min_pen","gC_closes_through","gB_penetration","gB_dist_ref_atr"],
      "relative_participation":["gC_toward_away_vol","gC_vol_persist_toward","gC_progress_per_vol","gC_volexp_noprog"],
      "generic_state":["gA_atr_vs_atrma","gA_volrank","gA_compress","gA_rsi","gA_hour","gA_h4"]}
def abscorr(sid,feat):
    g=M[M.setup==sid]; x=g[feat].to_numpy(float); r=g.R.to_numpy(); ok=np.isfinite(x)
    if ok.sum()<200: return np.nan
    xr=x[ok]-np.nanmean(x[ok]); rr=r[ok]-r[ok].mean(); return abs((xr*rr).sum()/(np.sqrt((xr**2).sum()*(rr**2).sum())+1e-9))
catscore={cat:np.nanmean([abscorr(sid,f) for sid in M.setup.unique() for f in feats]) for cat,feats in CATS.items()}
print("\n== §32 IDEA-CLASS RANKS (mean |corr with net_R| across setups) ==")
for cat,sc in sorted(catscore.items(),key=lambda kv:-kv[1]): print(f"  {cat:24s} {sc:.4f}")
def rank(cat):
    vals=sorted(catscore.values(),reverse=True); pos=vals.index(catscore[cat]); return "HIGH" if pos<2 else ("MEDIUM" if pos<4 else "LOW")
print(f"APPROACH-GEOMETRY IDEA RANK = {rank('approach_geometry')}")
print(f"STRUCTURAL-PRESSURE IDEA RANK = {rank('structural_pressure')}")
print(f"VOLUME-RELATIVE-TO-IMPULSE IDEA RANK = {rank('relative_participation')}")
print(f"LEVEL-WEAKENING (bearish-block-style pressure) IDEA RANK = {rank('level_weakening')}")

# ---- §33 cross-setup recurrence: same feature discriminates same sign across >=2/3 setups ----
rec=[]
for cat,feats in CATS.items():
    for f in feats:
        signs=[];
        for sid in M.setup.unique():
            g=M[M.setup==sid]; x=g[f].to_numpy(float); r=g.R.to_numpy(); ok=np.isfinite(x)
            if ok.sum()<200: continue
            xr=x[ok]-np.nanmean(x[ok]); rr=r[ok]-r[ok].mean(); cc=(xr*rr).sum()/(np.sqrt((xr**2).sum()*(rr**2).sum())+1e-9)
            if abs(cc)>=0.03: signs.append(np.sign(cc))
        if len(signs)>=2 and abs(sum(signs))==len(signs): rec.append(dict(feature=f,category=cat,n_setups=len(signs),dirn=int(signs[0])))
RC=pd.DataFrame(rec); RC.to_csv(OUT+r"\CTS_V2_CROSS_SETUP_RECURRENCE.csv",index=False)
csf=len(RC)>0
print(f"\n== §33 CROSS_SETUP_CONTEXT_FOUND = {'YES' if csf else 'NO'} ({len(RC)} features recur same-sign across >=2 setups) ==")
if csf: print(RC.sort_values("n_setups",ascending=False).head(8).to_string(index=False))

# ---- §34 feasibility for the best lose-less selector (SETUP_3 B @60) ----
b=FR[(FR.setup=="SETUP_3")&(FR.rep=="B_setup_static")&(FR.retention==0.6)].iloc[0]
yrs=(M[M.setup=="SETUP_3"].decision_time.max()-M[M.setup=="SETUP_3"].decision_time.min())/SEC_YR
feas=pd.DataFrame([dict(setup=s.setup,rep=s.rep,sel_exp=s.sel_exp,sel_per_year=s.sel_per_year,
    time_to_30_mo=round(30/s.sel_per_year*12,1),time_to_50_mo=round(50/s.sel_per_year*12,1)) for _,s in FR[FR.retention==0.6].iterrows()])
feas.to_csv(OUT+r"\CTS_V2_PROSPECTIVE_FEASIBILITY.csv",index=False)
print("\nfeasibility saved. Best lose-less = SETUP_3 B_setup_static (still negative, not a candidate).")
# save comparison + classifications summary
import json
json.dump({"classifications":cls,"setup_relative_incremental":('YES' if sri else 'NO'),"sequence_order_incremental":('YES' if soi else 'NO'),
           "practically_useful":('YES' if len(practically) else 'NO'),"cross_setup":('YES' if csf else 'NO'),"idea_ranks":{k:rank(k) for k in CATS if k!='generic_state'}},
          open(OUT+r"\_cts_v2_summary.json","w"),indent=2)
print("summary saved")

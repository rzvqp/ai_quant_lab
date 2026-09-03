"""atlas_v1_summary.py — §21-35 battery for XAU_100_300_PIP_MOVE_ATLAS_V1. Univariate precursor info: (A) OCCURRENCE = episode vs matched
control (AUC, medians, chronological thirds); (B) DIRECTION = up vs down among episodes. §23/§24 gates, §25 one predeclared 2-precursor
intersection (only if >=2 families pass), path-quality, yearly, final block. No PnL, no threshold optimization."""
import numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
EP=pd.read_parquet(OUT+r"\XAU_100_300_PIP_MOVE_EPISODES.parquet"); CO=pd.read_parquet(OUT+r"\XAU_100_300_PIP_MOVE_CONTROLS.parquet")
yrs=15.0
def auc(ev, co):  # P(ev>co), Mann-Whitney
    ev=ev[np.isfinite(ev)]; co=co[np.isfinite(co)]
    if len(ev)<50 or len(co)<50: return np.nan
    allv=np.concatenate([ev,co]); r=pd.Series(allv).rank().to_numpy(); re=r[:len(ev)]
    return (re.sum()-len(ev)*(len(ev)+1)/2)/(len(ev)*len(co))
def era3(df):
    q=np.quantile(df.dtime,[1/3,2/3]); return [df[df.dtime<=q[0]],df[(df.dtime>q[0])&(df.dtime<=q[1])],df[df.dtime>q[1]]]
# OCCURRENCE: magnitude features (abs for signed)
EP2=EP.copy(); CO2=CO.copy()
for df in (EP2,CO2):
    df["m_ret1"]=df.p2_ret1.abs(); df["m_ret4"]=df.p2_ret4.abs(); df["m_press"]=df.p4_press.abs()
occ_feats=["p1_range4","p1_tr1","p1_body","m_ret1","m_ret4","p2_bodydom","p5_volratio","p5_volpct","p7_pdloc","p7_ssloc","p9_retr","m_press"]
rows=[]
for f in occ_feats:
    A=auc(EP2[f].to_numpy(),CO2[f].to_numpy())
    ep3=era3(EP2); co3=era3(CO2); folds=[auc(ep3[i][f].to_numpy(),co3[i][f].to_numpy()) for i in range(3)]
    signs=[np.sign(x-0.5) for x in folds if np.isfinite(x)]; consistent=len(set(signs))==1 and len(signs)==3
    rows.append(dict(precursor=f,AUC=round(A,3),effect=round(abs(A-0.5),3),ev_med=round(float(np.nanmedian(EP2[f])),3),co_med=round(float(np.nanmedian(CO2[f])),3),
        folds=[round(x,3) for x in folds],consistent=bool(consistent),passes=bool(abs(A-0.5)>=0.05 and consistent)))
OCC=pd.DataFrame(rows).sort_values("effect",ascending=False)
# categorical occurrence: sweep, level-state (event rate vs control rate)
def catlift(col):
    out=[]
    for v in sorted(set(EP2[col].dropna())|set(CO2[col].dropna())):
        er=(EP2[col]==v).mean(); cr=(CO2[col]==v).mean(); out.append(dict(feature=col,val=v,ev_rate=round(100*er,1),co_rate=round(100*cr,1),lift_pp=round(100*(er-cr),1)))
    return out
CAT=pd.DataFrame(catlift("p3_sweep")+catlift("p8_lvl"))
# DIRECTION: up vs down among episodes (signed features)
up=EP[EP.dir>0]; dn=EP[EP.dir<0]
dir_feats=["p2_ret1","p2_ret4","p2_bodydom","p2_closeloc","p4_press","p5_volratio","p7_pdloc","p7_ssloc","p9_retr","p1_range4"]
drows=[]
for f in dir_feats:
    A=auc(up[f].to_numpy(),dn[f].to_numpy())
    u3=era3(up); d3=era3(dn); folds=[auc(u3[i][f].to_numpy(),d3[i][f].to_numpy()) for i in range(3)]
    signs=[np.sign(x-0.5) for x in folds if np.isfinite(x)]; consistent=len(set(signs))==1 and len(signs)==3
    drows.append(dict(precursor=f,AUC=round(A,3),effect=round(abs(A-0.5),3),folds=[round(x,3) for x in folds],consistent=bool(consistent),passes=bool(abs(A-0.5)>=0.05 and consistent)))
DIR=pd.DataFrame(drows).sort_values("effect",ascending=False)
occ_pass=OCC[OCC.passes]; dir_pass=DIR[DIR.passes]
MAG = len(occ_pass)>0; DIRINFO=len(dir_pass)>0
best_occ=OCC.iloc[0]; best_dir=DIR.iloc[0]
# §25 intersection: only if >=2 occurrence families pass
inter_tested="NO"; inter_incr="NO"
if len(occ_pass)>=2:
    fa,fb=occ_pass.iloc[0].precursor, occ_pass.iloc[1].precursor
    comb=pd.concat([EP2.assign(ev=1),CO2.assign(ev=0)],ignore_index=True)
    for f in (fa,fb):
        hi=comb[f].quantile(2/3); comb[f+"_hi"]=(comb[f]>=hi).astype(int) if best_occ.AUC>0.5 else (comb[f]<=comb[f].quantile(1/3)).astype(int)
    base=comb.ev.mean(); single=comb[comb[fa+"_hi"]==1].ev.mean(); both=comb[(comb[fa+"_hi"]==1)&(comb[fb+"_hi"]==1)].ev.mean()
    inter_tested="YES"; inter_incr="YES" if both>single+0.03 else "NO"
    print(f"§25 intersection {fa}+{fb}: base={base:.3f} single={single:.3f} both={both:.3f} -> incremental={inter_incr}")
# path quality + yearly
pq=pd.DataFrame([dict(metric="median_bars_to_100",v=float(EP.bars_to_100.median())),dict(metric="median_MAE_usd",v=float(EP.mae_usd.median())),
    dict(metric="P75_MAE_usd",v=float(EP.mae_usd.quantile(.75))),dict(metric="P90_MAE_usd",v=float(EP.mae_usd.quantile(.90))),
    dict(metric="MFE_MAE_gt1",v=round(100*(EP.mfe_mae>1).mean(),1)),dict(metric="MFE_MAE_gt2",v=round(100*(EP.mfe_mae>2).mean(),1)),dict(metric="MFE_MAE_gt3",v=round(100*(EP.mfe_mae>3).mean(),1))])
pq.to_csv(OUT+r"\XAU_100_300_PIP_PATH_QUALITY.csv",index=False)
EP.groupby("year").agg(episodes=("t","size"),ext150=("ext150","sum"),ext200=("ext200","sum"),ext300=("ext300","sum")).to_csv(OUT+r"\XAU_100_300_PIP_YEARLY.csv")
OCC.to_csv(OUT+r"\XAU_100_300_PIP_PRECURSOR_RESULTS.csv",index=False); DIR.to_csv(OUT+r"\XAU_100_300_PIP_DIRECTION_RESULTS.csv",index=False); CAT.to_csv(OUT+r"\XAU_100_300_PIP_CATEGORICAL.csv",index=False)
print("== OCCURRENCE (episode vs matched control) =="); print(OCC.to_string(index=False))
print("\n== CATEGORICAL =="); print(CAT.to_string(index=False))
print("\n== DIRECTION (up vs down) =="); print(DIR.to_string(index=False))
print(f"\nMAGNITUDE_INFORMATION_FOUND={'YES' if MAG else 'NO'} (passing occ: {list(occ_pass.precursor)})")
print(f"DIRECTIONAL_INFORMATION_FOUND={'YES' if DIRINFO else 'NO'} (passing dir: {list(dir_pass.precursor)})")
print(f"BEST_OCC={best_occ.precursor} AUC={best_occ.AUC} | BEST_DIR={best_dir.precursor} AUC={best_dir.AUC}")
print(f"FOLLOW_UP_STRATEGY_RESEARCH_JUSTIFIED={'YES' if (MAG and DIRINFO) else 'NO'}")

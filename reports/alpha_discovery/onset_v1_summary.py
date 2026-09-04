"""onset_v1_summary.py — §19-33 battery for onset atlas. Occurrence (episode vs control) + DIRECTION (up vs down) AUC per family, per block;
§22/§23 direction gates; §24 M1-vs-M5 overlap; §25 onset timing; path quality. Direction is the success criterion. No PnL."""
import numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
def auc(a,b):
    a=a[np.isfinite(a)]; b=b[np.isfinite(b)]
    if len(a)<40 or len(b)<40: return np.nan
    allv=np.concatenate([a,b]); r=pd.Series(allv).rank().to_numpy(); ra=r[:len(a)]
    return (ra.sum()-len(a)*(len(a)+1)/2)/(len(a)*len(b))
def thirds(df):
    q=np.quantile(df.dtime,[1/3,2/3]) if "dtime" in df else (0,0)
    return [df[df.dtime<=q[0]],df[(df.dtime>q[0])&(df.dtime<=q[1])],df[df.dtime>q[1]]] if "dtime" in df else None
SIGN=["s1_net","s1_bull","s1_bodysum","s2_loc","s2_slope","s3_wick","s4_d30","s4_d15","s5_imp","s6","s7_expside","s8","s9","s10"]
MAG=["s7_rng","s5_pull"]
def dir_table(ep):
    up=ep[ep.dir>0]; dn=ep[ep.dir<0]; rows=[]
    for f in SIGN:
        A=auc(up[f].to_numpy(),dn[f].to_numpy())
        u3=thirds(up); d3=thirds(dn); fold=[auc(u3[i][f].to_numpy(),d3[i][f].to_numpy()) for i in range(3)]
        signs={np.sign(x-0.5) for x in fold if np.isfinite(x)}; cons=(len(signs)==1 and len([x for x in fold if np.isfinite(x)])==3)
        latest=fold[2] if np.isfinite(fold[2]) else np.nan
        rows.append(dict(f=f,AUC=round(A,3) if np.isfinite(A) else np.nan,eff=round(abs(A-0.5),3) if np.isfinite(A) else np.nan,
            folds=[round(x,3) if np.isfinite(x) else np.nan for x in fold],latest_eff=round(abs(latest-0.5),3) if np.isfinite(latest) else np.nan,consistent=bool(cons)))
    return pd.DataFrame(rows).sort_values("eff",ascending=False)
def occ_table(ep,co):
    rows=[]
    for f in SIGN+MAG:
        ev=np.abs(ep[f].to_numpy()) if f in SIGN else ep[f].to_numpy(); cv=np.abs(co[f].to_numpy()) if f in SIGN else co[f].to_numpy()
        A=auc(ev,cv); rows.append(dict(f=f,AUC=round(A,3) if np.isfinite(A) else np.nan,eff=round(abs(A-0.5),3) if np.isfinite(A) else np.nan))
    return pd.DataFrame(rows).sort_values("eff",ascending=False)
# load
A=pd.read_parquet(OUT+r"\_onset_blockA.parquet"); Aep=A[A.dir!=0]; Aco=A[A.dir==0]
Bm1=pd.read_parquet(OUT+r"\_onset_blockB_m1.parquet"); Bep1=Bm1[Bm1.dir!=0]; Bco1=Bm1[Bm1.dir==0]
Bm5=pd.read_parquet(OUT+r"\M5_M1_OVERLAP_EPISODES.parquet"); Bep5=Bm5[Bm5.dir!=0]; Bco5=Bm5[Bm5.dir==0]
dA=dir_table(Aep); dB1=dir_table(Bep1); dB5=dir_table(Bep5)
oA=occ_table(Aep,Aco); oB1=occ_table(Bep1,Bco1); oB5=occ_table(Bep5,Bco5)
def gate(row): return bool(np.isfinite(row.eff) and row.eff>=0.08 and row.consistent and np.isfinite(row.latest_eff) and row.latest_eff>=0.05)
dA["passes"]=dA.apply(gate,axis=1); dB1["passes"]=dB1.apply(gate,axis=1); dB5["passes"]=dB5.apply(gate,axis=1)
bestA=dA.iloc[0]; bestB1=dB1.iloc[0]; bestB5=dB5.iloc[0]
# §24 overlap: M1 best vs same-feature M5 effect on same episodes
m1_by_f=dict(zip(dB1.f,dB1.eff)); m5_by_f=dict(zip(dB5.f,dB5.eff))
overlap=pd.DataFrame([dict(f=f,M1_eff=m1_by_f.get(f,np.nan),M5_eff=m5_by_f.get(f,np.nan),M1_minus_M5=round(m1_by_f.get(f,np.nan)-m5_by_f.get(f,np.nan),3)) for f in SIGN]).sort_values("M1_eff",ascending=False)
m1_incr = bool(gate(bestB1) and (bestB1.eff - m5_by_f.get(bestB1.f,0) >= 0.05))
# onset timing (M1): direction AUC of net-return at 30/15/10/5 min
ONS=pd.read_parquet(OUT+r"\_onset_timing.parquet"); up=ONS[ONS.dir>0]; dn=ONS[ONS.dir<0]
onset_rows=[]
for W in (30,15,10,5):
    c=f"net{W}"
    if c in ONS: onset_rows.append(dict(window_min=W,dir_AUC=round(auc(up[c].to_numpy(),dn[c].to_numpy()),3)))
ONR=pd.DataFrame(onset_rows)
earliest=next((r.window_min for _,r in ONR.sort_values("window_min",ascending=False).iterrows() if abs(r.dir_AUC-0.5)>=0.05),"none")
# path quality block B from atlas episodes
try:
    ATL=pd.read_parquet(OUT+r"\XAU_100_300_PIP_MOVE_EPISODES.parquet")
    pb=ATL[(ATL.dtime>=int(pd.Timestamp('2025-08-04',tz='UTC').value//10**9))]
    pathB=dict(median_mae=round(float(pb.mae_usd.median()),1),mfe_mae_gt2=round(100*(pb.mfe_mae>2).mean(),1),n=len(pb))
except Exception as e: pathB={"err":str(e)}
# writes
dA.to_csv(OUT+r"\M5_2021_2024_SEQUENCE_RESULTS.csv",index=False); dB1.to_csv(OUT+r"\M1_2025_CURRENT_SEQUENCE_RESULTS.csv",index=False)
overlap.to_csv(OUT+r"\M5_M1_OVERLAP_COMPARISON.csv",index=False); ONR.to_csv(OUT+r"\M1_ONSET_TIMING.csv",index=False)
Aep.groupby("year").size().to_frame("episodes").to_csv(OUT+r"\M15_M5_M1_YEARLY.csv")
pd.DataFrame([pathB]).to_csv(OUT+r"\M15_M5_M1_PATH_QUALITY.csv",index=False)
print("== BLOCK A M5 2021-2024 DIRECTION (top5) =="); print(dA.head(5).to_string(index=False))
print("== BLOCK B M1 2025+ DIRECTION (top6) =="); print(dB1.head(6).to_string(index=False))
print("== BLOCK B M5 2025+ DIRECTION (same episodes, top5) =="); print(dB5.head(5).to_string(index=False))
print("== §24 OVERLAP M1-vs-M5 (top6 by M1) =="); print(overlap.head(6).to_string(index=False))
print("== OCCURRENCE best: A_M5", oA.iloc[0].to_dict(), " B_M1", oB1.iloc[0].to_dict())
print("== §25 ONSET TIMING (M1 net-return direction AUC) =="); print(ONR.to_string(index=False))
print(f"\nBEST_M5_2021_2024_DIR={bestA.f} eff={bestA.eff} pass={bool(bestA.passes)}")
print(f"BEST_M5_CURRENT_DIR={bestB5.f} eff={bestB5.eff}")
print(f"BEST_M1_CURRENT_DIR={bestB1.f} eff={bestB1.eff} latest_eff={bestB1.latest_eff} pass={bool(bestB1.passes)}")
print(f"M1_MINUS_M5_SAME_PERIOD_EFF={round(bestB1.eff-m5_by_f.get(bestB1.f,0),3)}")
print(f"CURRENT_M1_DIRECTIONAL_INFORMATION_FOUND={'YES' if dB1.passes.any() else 'NO'}")
print(f"M1_INCREMENTAL_DIRECTION_INFORMATION={'YES' if m1_incr else 'NO'}")
print(f"EARLIEST_M1_DIR_WINDOW={earliest} | path_B={pathB}")
print(f"M15_TO_M1_EXECUTION_RESEARCH_JUSTIFIED={'YES' if (dB1.passes.any() and m1_incr) else 'NO'}")

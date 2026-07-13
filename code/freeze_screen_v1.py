import numpy as np, pandas as pd, time
import mstrat as MS, run_lot
from alpha_lab import bh_fdr
d=MS.load(); n=len(d); a=int(n*0.6); b=int(n*0.8)
res=d.iloc[:a].copy(); val=d.iloc[a:b].copy()
MINTR=MS.CFG['MINTR']; PF_S=1.02; DD_S=25.0; Q=MS.CFG['FDR_Q']
fams=['S1','S2','S3','S4','S5','S6','S7','S8','S9','S10']
rows=[]; t0=time.time()
for fam in fams:
    for h in MS.REGISTRY[fam][0]():
        tr=MS.backtest(res,h); m=run_lot.metrics(tr)
        valid = m['n']>=MINTR
        rc = valid and (m['exp']>0) and (m['pf']>=PF_S) and (m['dd']<=DD_S)   # Screen V1: research-only, NO OOS
        reason='RC' if rc else ('invalid_min_trades' if not valid else ('exp<=0' if m['exp']<=0 else ('pf<1.02' if m['pf']<PF_S else 'dd>25')))
        p=MS.analytic_p(res,MS.setups(res,h),m['exp'],m['n']) if valid else 1.0
        rows.append(dict(fam=fam,id=h['id'],n=m['n'],exp=m['exp'],pf=m['pf'],dd=m['dd'],valid=valid,rc=rc,reason=reason,p=p))
df=pd.DataFrame(rows)
print(f"compute {time.time()-t0:.0f}s | total={len(df)} valid={int(df['valid'].sum())} Research_Candidates={int(df['rc'].sum())}")
print("\n=== EXACT per-family under FROZEN Discovery Screen V1 (exp>0 & PF>=1.02 & maxDD<=25R & n>=25; NO OOS) ===")
tot_rc=0
for fam in fams:
    sub=df[df['fam']==fam]; g=len(sub); v=int(sub['valid'].sum()); rc=int(sub['rc'].sum()); tot_rc+=rc
    rr=sub[~sub['rc']]['reason'].value_counts().to_dict()
    print(f"  {fam}: generated={g} valid={v} RC={rc} ({100*rc/v if v else 0:.1f}% of valid) | elim: {rr}")
print(f"  SUM RC = {tot_rc}")
print("\nRC hypothesis_ids per family (first 6):")
for fam in fams:
    ids=df[(df['fam']==fam)&df['rc']]['id'].tolist()
    if ids: print(f"  {fam}: {ids[:6]}{'...' if len(ids)>6 else ''} (total {len(ids)})")
# FDR breakdown
valid_p=df[df['valid']]['p'].values; rc_p=df[df['rc']]['p'].values; all_p=df['p'].values
def fdr_stats(p,m,label):
    p=np.sort(p); k=np.where(p<=(np.arange(1,len(p)+1)/m*Q))[0]; npass=(k.max()+1) if len(k) else 0
    q=(p*m/np.arange(1,len(p)+1)); return f"{label}: m={m} minp={p[0]:.2e} minq={np.min(q):.3f} pass={npass}"
print("\n=== FDR (report all 3, strict verdict = official method C) ===")
print(" A. "+fdr_stats(valid_p,len(valid_p),"over ALL VALID (p computed for every valid hyp)"))
print(" B. "+fdr_stats(rc_p,len(rc_p),"over RC SUBSET [SELECTIVE/DIAGNOSTIC - needs selection correction, NOT a strict verdict]"))
print(" C. "+fdr_stats(all_p,len(all_p),"OFFICIAL frozen pipeline: BH over full canonical universe (invalid->p=1)"))
print("    -> p-values are computed for ALL valid hyps (not only after screen); strict verdict uses C.")
df.to_parquet("FAMILY_RESULTS.parquet")
print("\nwrote FAMILY_RESULTS.parquet (exact, reproducible)")

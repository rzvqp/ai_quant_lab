import numpy as np, pandas as pd, time
import mstrat as MS, run_lot
d=MS.load(); n=len(d); a=int(n*0.6); b=int(n*0.8)
res=d.iloc[:a].copy(); val=d.iloc[a:b].copy()
fams=['S1','S2','S3','S4','S5','S6','S7','S8','S9','S10']
rows=[]; t0=time.time()
for fam in fams:
    for h in MS.REGISTRY[fam][0]():
        m=run_lot.metrics(MS.backtest(res,h))
        if m['n']<MS.CFG['MINTR']: rows.append((fam,h,m['n'],np.nan,np.nan,np.nan,np.nan,False)); continue
        mv=run_lot.metrics(MS.backtest(val,h))
        rows.append((fam,h,m['n'],m['exp'],m['pf'],m['dd'],mv['exp'] if mv['n']>=5 else np.nan,True))
df=pd.DataFrame(rows,columns=['fam','h','n','exp','pf','dd','exp_val','valid'])
V=int(df['valid'].sum())
print(f"total hyps={len(df)} | VALID(n>=MINTR)={V} | compute {time.time()-t0:.0f}s")
print("\ncalibrating DISCOVERY SCREEN to hit 5-15% of valid as Research Candidate:")
for exp_min,pf_min,dd_max,oos in [(0.0,1.15,12,True),(0.0,1.05,20,True),(0.0,1.02,25,True),(0.0,1.0,30,False),(0.02,1.05,25,True)]:
    cond=df['valid'] & (df['exp']>exp_min) & (df['pf']>=pf_min) & (df['dd']<=dd_max)
    if oos: cond=cond & (df['exp_val']>0)
    rc=int(cond.sum()); print(f"  exp>{exp_min} pf>={pf_min} dd<={dd_max} oos={oos}: research_candidates={rc} ({100*rc/V:.1f}% of valid)")
# choose the setting landing in 5-15%
CH=(0.0,1.05,20,True); cond=df['valid'] & (df['exp']>CH[0]) & (df['pf']>=CH[1]) & (df['dd']<=CH[2]) & (df['exp_val']>0)
rc=int(cond.sum()); print(f"\nCHOSEN screen exp>0 & PF>=1.05 & maxDD<=20R & OOS>0 -> {rc} Research Candidates ({100*rc/V:.1f}% of valid)")
print("per-family Research Candidates:")
for fam in fams:
    c=int((cond & (df['fam']==fam)).sum()); v=int((df['valid']&(df['fam']==fam)).sum())
    print(f"  {fam}: valid={v} research_candidates={c}")
df['rc']=cond; df[['fam','n','exp','pf','dd','exp_val','valid','rc']].to_parquet("FAMILY_RESULTS.parquet") if hasattr(pd.DataFrame,'to_parquet') else None
print("\nStrict validation (UNCHANGED) still applies global-FDR+walk-forward+Red Team over these; decides survival separately.")

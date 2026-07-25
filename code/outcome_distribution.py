"""DESCRIPTIVE DISTRIBUTION over ALL 1972 hypotheses. Measurement only, no selection, no matched-null,
no holdout, no parquet change, no new screen proposed. Reconstructs research trades (deterministic
MS.simulate) to get net1=best/sumR (defined only where sumR>0); win/wo1/research_worthy from FAMILY_RESULTS;
stop-class and exit-rule from the grammar. Reports joint win x net1, splits by stop type and exit rule,
and an alternative-screen COUNT (not a proposal). Draws no conclusion."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import mstrat as MS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fr = pd.read_parquet(os.path.join(ROOT, "results", "FAMILY_RESULTS.parquet"))
ATR={'atr'}; EMA={'ema'}
STRUCT={'beyond_sweep','structural','beyond_ext','beyond_level','bar','or_opp','prev_ext','ext','struct','level'}
idmap={}
for fam in MS.REGISTRY:
    for h in MS.REGISTRY[fam][0](): idmap[h['id']]=h
def stopclass(s): return 'atr' if s in ATR else ('ema' if s in EMA else ('struct' if s in STRUCT else '?'))

d=MS.load(); a=int(len(d)*0.6); res=d.iloc[:a].copy()   # research; holdout never loaded
best=[]; sumR=[]
for hid in fr['id']:
    t=MS.simulate(res, MS.setups(res, idmap[hid]))
    R=t['R'].values
    best.append(float(R.max()) if len(R) else np.nan); sumR.append(float(R.sum()) if len(R) else np.nan)
m=fr[['id','fam','n','exp','pf','dd','win','wo1','val_exp','hist_prof','research_worthy']].copy()
m['best']=best; m['sumR']=sumR
m['stopc']=m['id'].map(lambda i: stopclass(idmap[i].get('stop')))
m['exit']=m['id'].map(lambda i: idmap[i].get('exit'))
m['net1']=np.where(m['sumR']>0, m['best']/m['sumR'], np.nan)
prof=m[m['sumR']>0].copy()
print(f"ALL={len(m)}  sumR>0 (net1 defined)={len(prof)}  research_worthy={int(m['research_worthy'].sum())}")

def qd(s):
    s=s.dropna()
    return {k: round(float(np.quantile(s,k)),3) for k in (.1,.25,.5,.75,.9)} if len(s) else {}

print("\n=== 1. JOINT win x net1 (on sumR>0) ===")
print("Pearson(win,net1)=%.3f  Spearman=%.3f  (n=%d)" % (
    np.corrcoef(prof['win'],prof['net1'])[0,1],
    np.corrcoef(prof['win'].rank(),prof['net1'].rank())[0,1], len(prof)))
winbin=pd.cut(prof['win'],[0,0.30,0.45,0.60,1.01],labels=['<.30','.30-.45','.45-.60','>=.60'])
netbin=pd.cut(prof['net1'],[-1e9,0.30,0.50,1.0,1e9],labels=['net1<.30','.30-.50','.50-1.0','>1.0'])
ct=pd.crosstab(winbin,netbin)
print("cross-tab counts (rows=win, cols=net1):"); print(ct.to_string())
print("median net1 by win bin:", {str(k): round(float(prof.loc[winbin==k,'net1'].median()),3) for k in ['<.30','.30-.45','.45-.60','>=.60']})

print("\n=== 2. by STOP TYPE (win, net1) ===")
for sc in ['atr','struct','ema']:
    sub=m[m['stopc']==sc]; subp=prof[prof['stopc']==sc]
    print(f"  {sc}: n_hyp={len(sub)}  win q[10/25/50/75/90]={qd(sub['win'])}  net1(sumR>0,n={len(subp)}) q={qd(subp['net1'])}")

print("\n=== 3. by EXIT RULE (win, net1) ===")
for ex in sorted(m['exit'].dropna().unique()):
    sub=m[m['exit']==ex]; subp=prof[prof['exit']==ex]
    print(f"  {ex:10s}: n={len(sub):4d}  median win={sub['win'].median():.3f}  median net1(sumR>0,n={len(subp)})={subp['net1'].median() if len(subp) else float('nan'):.3f}  median dd={sub['dd'].median():.1f}")

print("\n=== 4. alternative-screen COUNT (win>=0.50 & net1<0.30 & wo1>0) + overlap with research_worthy ===")
alt = m[(m['win']>=0.50)&(m['net1']<0.30)&(m['wo1']>0)&m['net1'].notna()]
rw = m[m['research_worthy']]
altset=set(alt['id']); rwset=set(rw['id'])
print(f"alt-screen passes: {len(altset)}  | research_worthy: {len(rwset)}")
print(f"  overlap (alt AND rw): {len(altset & rwset)}")
print(f"  alt-only (pass alt, NOT rw): {len(altset - rwset)}")
print(f"  rw-only (rw, NOT alt): {len(rwset - altset)}")
print("  alt-screen passers by family:", dict(alt['fam'].value_counts()))
print("  alt-screen passers by stop type:", dict(alt['stopc'].value_counts()))
# current 130 research_worthy: their net1 / win profile
print(f"  research_worthy median win={rw['win'].median():.3f} median net1={rw['net1'].median():.3f} median dd={rw['dd'].median():.1f}")
m.to_parquet(os.path.join(ROOT,"results","matched_null_validation","outcome_distribution.parquet"))
print("\nwrote results/matched_null_validation/outcome_distribution.parquet")

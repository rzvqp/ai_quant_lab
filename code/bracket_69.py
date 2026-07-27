"""BRACKET verification for the 69 hypotheses whose profitable-status appeared only under the
exclusion convention. For each: hist_prof status under worst-case (stop-first, keep all = baseline),
best-case (target-first, keep all), and exclusion (new). Measurement only; target_first is a toggle,
NOT the default. No holdout, no promotion, no re-run of the campaign."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import mstrat as MS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = pd.read_parquet(os.path.join(ROOT, "results", "FAMILY_RESULTS.parquet")).set_index('id')
new  = pd.read_parquet(os.path.join(ROOT, "results", "reproduction_d2", "FAMILY_RESULTS.parquet")).set_index('id')
idmap = {}
for fam in MS.REGISTRY:
    for h in MS.REGISTRY[fam][0](): idmap[h['id']] = h
d = MS.load(); a = int(len(d)*0.6); res = d.iloc[:a].copy()

WORST = {'mark_invalid': False, 'target_first': False}   # baseline (stop-first, keep all)
BEST  = {'mark_invalid': False, 'target_first': True}    # target-first, keep all
EXCL  = {'mark_invalid': True,  'target_first': False}   # new convention

def cfg(over):
    c = dict(MS.CFG); c.update(over); return c
def histprof(hid, over):
    R = MS.simulate(res, MS.setups(res, idmap[hid]), cfg(over))['R'].values
    if len(R)==0: return False, dict(n=0)
    sumR=float(R.sum()); exp=float(R.mean()); gp=R[R>0].sum(); gl=-R[R<0].sum()
    pf=float(gp/gl) if gl>0 else np.inf
    hp = bool(len(R)>0 and sumR>0 and exp>0 and pf>1.00)
    return hp, dict(n=len(R), sumR=round(sumR,2), exp=round(exp,4), pf=round(pf,3) if np.isfinite(pf) else 99.0)

# --- the 69: baseline hist_prof False AND reproduction_d2 hist_prof True ---
flipped = sorted([i for i in base.index if (not bool(base.loc[i,'hist_prof'])) and bool(new.loc[i,'hist_prof'])])
print(f"flipped unprofitable->profitable under exclusion: {len(flipped)}")

# --- sanity: default refactor preserves baseline + reproduction_d2 ---
smp = flipped[:8]
okW = all(histprof(i, WORST)[0]==bool(base.loc[i,'hist_prof']) for i in smp)
okE = all(histprof(i, EXCL)[0]==bool(new.loc[i,'hist_prof']) for i in smp)
# ATR unchanged under refactor (target_first=False default): survivor identical
svR0 = MS.simulate(res, MS.setups(res, idmap['ce76669a3b2a']), cfg(WORST))['R'].values
svRb = float(base.loc['ce76669a3b2a','sumR'])
print(f"SANITY: worst==baseline(sample)={okW}  excl==reproduction_d2(sample)={okE}  ATR survivor sumR {svR0.sum():.2f} vs base {svRb:.2f} match={abs(svR0.sum()-svRb)<1e-9}")

rows=[]
for hid in flipped:
    hpW,mW = histprof(hid, WORST); hpB,mB = histprof(hid, BEST); hpE,mE = histprof(hid, EXCL)
    rows.append(dict(id=hid, fam=idmap[hid]['family'], worst=hpW, best=hpB, excl=hpE,
                     worst_exp=mW.get('exp'), best_exp=mB.get('exp'), excl_exp=mE.get('exp'),
                     worst_n=mW.get('n'), best_n=mB.get('n'), excl_n=mE.get('n')))
m=pd.DataFrame(rows)
# classification
m['bracket_same'] = (m['worst']==m['best'])          # status robust across the worst<->best bracket
m['excl_creates'] = (~m['worst']) & (~m['best']) & (m['excl'])   # profitable ONLY under exclusion (not even best-case)
m['conv_dependent'] = (m['worst']!=m['best'])         # status flips across bracket -> belongs to convention

print("\n=== BRACKET status of the 69 (hist_prof under each convention) ===")
print(f"  best-case (target-first) profitable: {int(m['best'].sum())} / {len(m)}")
print(f"  CONVENTION-DEPENDENT (worst False, best True -> status spans bracket): {int(m['conv_dependent'].sum())}")
print(f"  EXCLUSION-CREATED (False under BOTH worst and best, True only under exclusion): {int(m['excl_creates'].sum())}")
print(f"  (all 69 are worst=False by construction; excl=True by construction)")
print("\nby family (convention-dependent):", dict(m[m.conv_dependent]['fam'].value_counts()))
print("by family (exclusion-created):", dict(m[m.excl_creates]['fam'].value_counts()))
print("\nsample rows:")
print(m[['id','fam','worst','best','excl','worst_exp','best_exp','excl_exp']].head(12).to_string(index=False))
m.to_parquet(os.path.join(ROOT,"results","reproduction_d2","bracket_69.parquet"))
json.dump(dict(n_flipped=len(m), best_profitable=int(m['best'].sum()),
               convention_dependent=int(m['conv_dependent'].sum()),
               exclusion_created=int(m['excl_creates'].sum()),
               sanity_worst_eq_baseline=bool(okW), sanity_excl_eq_repro=bool(okE)),
          open(os.path.join(ROOT,"results","reproduction_d2","bracket_69_summary.json"),"w"), indent=1)
print("\nwrote bracket_69.parquet + bracket_69_summary.json")

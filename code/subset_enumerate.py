"""PRE-REGISTRATION ENUMERATION (no p-values computed). Classifies the full 1972-hypothesis
grammar by the 'stop' FIELD only, defines the ATR-stop subset (validated regime = 1.5xATR),
and reports subset size + BH threshold + validity breakdown. Grammar-derived, not results-derived."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, mstrat as MS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAM_PARQUET = os.path.join(ROOT, "results", "FAMILY_RESULTS.parquet")

# stop-field classification (from the code audit of every family's setup provider)
ATR_STOP = {'atr'}                         # every family maps h['stop']=='atr' -> o[ei]-dir*1.5*atr  (validated regime)
STRUCTURAL = {'beyond_sweep','structural','beyond_ext','beyond_level','bar','or_opp',
              'prev_ext','ext','struct','level'}   # local-range / level stops -> D2 regime, OUT of domain
AMBIGUOUS_EXCLUDE = {'ema'}                # S7: stop at an EMA level = indicator-distance regime, neither 1.5xATR nor local-range -> exclude

rows = []
for fam in MS.REGISTRY:
    for h in MS.REGISTRY[fam][0]():
        rows.append(dict(id=h['id'], fam=fam, stop=h.get('stop')))
g = pd.DataFrame(rows)
assert g['id'].is_unique, "duplicate hypothesis ids in grammar"
total = len(g)

# classify by stop field
def cls(s):
    if s in ATR_STOP: return 'atr_indomain'
    if s in STRUCTURAL: return 'structural_excluded'
    if s in AMBIGUOUS_EXCLUDE: return 'ambiguous_excluded'
    return 'UNKNOWN_'+str(s)
g['regime'] = g['stop'].map(cls)

print("=== TOTAL grammar hypotheses:", total, "(expect 1972) ===")
print("\n=== distinct stop-field values x count ===")
print(g['stop'].value_counts().to_string())
print("\n=== regime classification ===")
print(g['regime'].value_counts().to_string())
unknown = g[g['regime'].str.startswith('UNKNOWN')]
print("\n=== UNKNOWN stop values (must be zero):", len(unknown), "===")
if len(unknown): print(unknown['stop'].value_counts().to_string())

print("\n=== per-family: atr vs excluded ===")
piv = g.pivot_table(index='fam', columns='regime', values='id', aggfunc='count', fill_value=0)
print(piv.to_string())

# validity from FAMILY_RESULTS (frozen eligibility, NOT a performance filter)
fr = pd.read_parquet(FAM_PARQUET)
print("\n=== FAMILY_RESULTS columns:", list(fr.columns), "===")
print("FAMILY_RESULTS rows:", len(fr))
# discover validity fields
for c in fr.columns:
    if fr[c].dtype == bool:
        print(f"  bool col {c}: True={int(fr[c].sum())}")
if 'n' in fr.columns:
    print("  n>=25:", int((fr['n']>=25).sum()), " n>=100:", int((fr['n']>=100).sum()))

atr_ids = set(g[g['regime']=='atr_indomain']['id'])
print("\n=== ATR-stop subset size (grammar):", len(atr_ids), "===")

merged = fr[fr['id'].isin(atr_ids)].copy()
print("ATR-subset rows found in FAMILY_RESULTS:", len(merged), "of", len(atr_ids))
if 'n' in merged.columns:
    for thr in (25,):
        m_valid = int((merged['n']>=thr).sum())
        print(f"ATR-subset valid (n>={thr}): {m_valid}")
        if m_valid>0:
            bh = 0.05/m_valid
            print(f"  BH first threshold alpha/m = 0.05/{m_valid} = {bh:.3e}")

# write prereg subset id-list (sorted, deterministic)
out = dict(total=total,
           stop_value_counts={str(k): int(v) for k,v in g['stop'].value_counts().items()},
           regime_counts={str(k): int(v) for k,v in g['regime'].value_counts().items()},
           atr_subset_ids=sorted(atr_ids))
if 'n' in merged.columns:
    valid_ids = sorted(set(merged[merged['n']>=25]['id']))
    out['atr_subset_valid_ids'] = valid_ids
    out['m_valid'] = len(valid_ids)
    out['bh_threshold'] = 0.05/len(valid_ids) if valid_ids else None
json.dump(out, open(os.path.join(ROOT, "results", "matched_null_validation", "subset_prereg_enumeration.json"), "w"), indent=1)
print("\nwrote results/matched_null_validation/subset_prereg_enumeration.json")

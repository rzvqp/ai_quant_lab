"""WP-3 proof + WP-4 audit. Compares baseline FAMILY_RESULTS (pre-D2) vs the D2-closed re-run.
PROVES the ATR regime is unchanged (max diff must be EXACTLY 0), then audits what changed elsewhere.
No engine calls here — pure comparison of the two committed result tables."""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = pd.read_parquet(os.path.join(ROOT, "results", "FAMILY_RESULTS.parquet"))
new  = pd.read_parquet(os.path.join(ROOT, "results", "reproduction_d2", "FAMILY_RESULTS.parquet"))
enum = json.load(open(os.path.join(ROOT, "results", "matched_null_validation", "subset_prereg_enumeration.json")))
atr_ids = set(enum["atr_subset_ids"]); atr_valid = set(enum["atr_subset_valid_ids"])

assert set(base['id'])==set(new['id']), "id set changed!"
b = base.set_index('id'); n = new.set_index('id')
numcols = [c for c in b.columns if b[c].dtype.kind in 'fi' and c in n.columns]
boolcols = [c for c in ('hist_prof','research_worthy','fragile') if c in b.columns]

def maxdiff(ids, cols):
    ids=sorted(ids); md=0.0; worst=None
    for c in cols:
        d=(b.loc[ids,c].astype(float)-n.loc[ids,c].astype(float)).abs()
        if d.max()>md: md=float(d.max()); worst=(c, d.idxmax())
    return md, worst

# ---------- WP-3 PROOF: ATR regime unchanged ----------
print("=== WP-3 PROOF — ATR regime unchanged (must be EXACTLY 0) ===")
md_all, w_all = maxdiff(atr_ids, numcols)
md_val, w_val = maxdiff(atr_valid, numcols)
bad_bool = sum(int((b.loc[sorted(atr_ids),c]!=n.loc[sorted(atr_ids),c]).sum()) for c in boolcols)
print(f"ATR all ({len(atr_ids)}): max|diff| numeric = {md_all:.3e}  worst={w_all}")
print(f"ATR valid FDR-412 ({len(atr_valid)}): max|diff| numeric = {md_val:.3e}  worst={w_val}")
print(f"ATR bool-flag changes (hist_prof/research_worthy/fragile): {bad_bool}")
ATR_UNCHANGED = (md_all==0.0 and bad_bool==0)
print(f"ATR_UNCHANGED = {ATR_UNCHANGED}  {'-> PASS' if ATR_UNCHANGED else '-> STOP: ATR CHANGED'}")

# ---------- WP-4 AUDIT: what changed elsewhere ----------
print("\n=== WP-4 AUDIT — changes over the full 1972 ===")
changed_rows=[]
for hid in b.index:
    dif=max((abs(float(b.loc[hid,c])-float(n.loc[hid,c])) for c in numcols), default=0.0)
    if dif>0: changed_rows.append(hid)
print(f"hypotheses with ANY numeric change: {len(changed_rows)} / {len(b)}")
# confine to struct/ema?
def stopc(hid):
    s=None
    import mstrat as MS
    return None
# use enumeration regime map
regime={}
for hid in atr_ids: regime[hid]='atr'
# everything else struct or ema
chg=pd.Index(changed_rows)
n_atr_changed=len(chg.intersection(atr_ids))
print(f"  of which ATR: {n_atr_changed}  (must be 0)")
# flag flips
for c in boolcols:
    flips=int((b[c]!=n.loc[b.index,c]).sum())
    b_true=int(b[c].sum()); n_true=int(n[c].sum())
    print(f"  {c}: baseline True={b_true} -> new True={n_true}  (flips={flips})")
# magnitude of n / sumR change on changed hyps
if changed_rows:
    dn=(b.loc[changed_rows,'n']-n.loc[changed_rows,'n'])
    print(f"  trades dropped per changed hyp: total={int(dn.sum())} median={int(dn.median())} max={int(dn.max())}")
    print(f"  changed hyps by family:", dict(new.set_index('id').loc[changed_rows,'fam'].value_counts()))
# net-profit-status of changed hyps (were they profitable?)
prof_changed=int(b.loc[changed_rows,'hist_prof'].sum()) if changed_rows else 0
print(f"  changed hyps that were hist_prof in baseline: {prof_changed} / {len(changed_rows)}")
json.dump({'atr_unchanged':bool(ATR_UNCHANGED),'atr_maxdiff':md_all,'atr412_maxdiff':md_val,
           'changed_hyps':len(changed_rows),'atr_changed':int(n_atr_changed),
           'hist_prof_base':int(b['hist_prof'].sum()),'hist_prof_new':int(n['hist_prof'].sum()),
           'research_worthy_base':int(b['research_worthy'].sum()),'research_worthy_new':int(n['research_worthy'].sum()),
           'fragile_base':int(b['fragile'].sum()),'fragile_new':int(n['fragile'].sum())},
          open(os.path.join(ROOT,"results","reproduction_d2","d2_verify_summary.json"),"w"), indent=1)
print("\nwrote results/reproduction_d2/d2_verify_summary.json")

"""DUPLICATE AUDIT over the full 1972 grammar. Two IDs are duplicates if they produce IDENTICAL
trade series on the same window. Uses the existing FAMILY_RESULTS (research window) as a cheap
metric-fingerprint to cluster, then CONFIRMS each cluster by hashing the reconstructed R series
(canonical engine) -- only for clustered IDs, not a campaign re-run. Reports counts (428 + full
body), which params are inert and under which gating values, and whether inertia is systematic.
Measurement only; no holdout."""
import os, sys, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import mstrat as MS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fr = pd.read_parquet(os.path.join(ROOT, "results", "FAMILY_RESULTS.parquet"))
enum = json.load(open(os.path.join(ROOT, "results", "matched_null_validation", "subset_prereg_enumeration.json")))
ATR = set(enum["atr_subset_ids"])
idmap = {}
for fam in MS.REGISTRY:
    for h in MS.REGISTRY[fam][0](): idmap[h["id"]] = h

# ---- fingerprint from FAMILY_RESULTS metric columns ----
mcols = [c for c in ["n","exp","pf","dd","win","sumR","median","trim5","t1","t3","t5","wo1","val_exp"] if c in fr.columns]
def fp(r):
    return tuple(("nan" if (isinstance(r[c], float) and np.isnan(r[c])) else round(float(r[c]), 8)) for c in mcols)
fr = fr.copy(); fr["fp"] = fr.apply(fp, axis=1)

# ---- confirm clusters by hashing reconstructed R series (canonical engine, research window) ----
d = MS.load()
def rhash(hid):
    R = MS.simulate(d, MS.setups(d, idmap[hid]))["R"].values
    return hashlib.sha256(np.ascontiguousarray(np.round(R, 10)).tobytes()).hexdigest()[:16], len(R)

groups = {}
for fpk, sub in fr.groupby("fp"):
    ids = sorted(sub["id"])
    if len(ids) > 1:
        groups[fpk] = ids

# confirm by R-hash within each metric-cluster (split if hashes differ)
confirmed = []   # list of sets of truly-identical ids
n0_ids = set(fr[fr["n"] == 0]["id"])
for fpk, ids in groups.items():
    hmap = {}
    for i in ids:
        h, nn = rhash(i)
        hmap.setdefault((h, nn), []).append(i)
    for key, members in hmap.items():
        if len(members) > 1:
            confirmed.append(sorted(members))

dup_ids = set(i for grp in confirmed for i in grp)
dup_ids_nonzero = set(i for grp in confirmed for i in grp if idmap and i not in n0_ids)

def stats(scope_ids, label):
    grps = [g for g in confirmed if any(i in scope_ids for i in g)]
    # restrict clusters to the scope
    grps = [[i for i in g if i in scope_ids] for g in grps]
    grps = [g for g in grps if len(g) > 1]
    ndup = sum(len(g) for g in grps)
    # distinct strategies in scope = (ids not in any dup cluster) + (one representative per cluster)
    in_cluster = set(i for g in grps for i in g)
    singletons = len(scope_ids) - len(in_cluster)
    distinct = singletons + len(grps)
    print(f"\n=== {label}: {len(scope_ids)} IDs ===")
    print(f"  duplicate IDs (in a >1 cluster): {ndup}  | clusters: {len(grps)}  | distinct strategies: {distinct}")
    print(f"  redundancy: {len(scope_ids)-distinct} IDs are redundant ({100*(len(scope_ids)-distinct)/len(scope_ids):.1f}%)")
    return grps

grps_all = stats(set(fr["id"]), "FULL BODY 1972")
grps_atr = stats(ATR, "428 ATR")

# ---- which params are inert, under which gating values ----
print("\n=== INERT-PARAMETER ANALYSIS (within confirmed duplicate clusters) ===")
from collections import defaultdict
inert = defaultdict(lambda: defaultdict(int))   # inert_param -> frozenset(fixed gating items) -> count of clusters
byfam = defaultdict(int)
for g in [gg for gg in confirmed if len(gg) > 1]:
    params = [idmap[i] for i in g]
    keys = [k for k in params[0] if k not in ("id",)]
    varying = [k for k in keys if len({p.get(k) for p in params}) > 1]
    fixed = {k: params[0].get(k) for k in keys if k not in varying}
    fam = params[0].get("family")
    byfam[fam] += 1
    for vk in varying:
        # gating context = the fixed params that "explain" the inertness (esp. the family + a plausible gate)
        inert[vk][(fam, )] += 1
print("  clusters by family:", dict(byfam))
print("  inert params -> (family): #clusters where that param varies with no effect")
for vk, ctx in sorted(inert.items(), key=lambda x: -sum(x[1].values())):
    tot = sum(ctx.values())
    fams = ", ".join(f"{f[0]}:{c}" for f, c in sorted(ctx.items(), key=lambda x: -x[1]))
    print(f"    {vk}: {tot} clusters  [{fams}]")

# example clusters (decoded) + the S2 sanity pair
print("\n=== sample clusters (decoded) ===")
for g in [gg for gg in confirmed if len(gg) > 1][:6]:
    params = [idmap[i] for i in g]; keys=[k for k in params[0] if k!='id']
    varying = {k: sorted({str(p.get(k)) for p in params}) for k in keys if len({p.get(k) for p in params})>1}
    fixed = {k: params[0].get(k) for k in keys if k not in varying and k!='family'}
    print(f"  {params[0].get('family')} x{len(g)}: inert={varying}  fixed={fixed}")
print("\nS2 sanity (92481423c6b8, a53441048c3c) same cluster:",
      any({'92481423c6b8','a53441048c3c'}.issubset(set(g)) for g in confirmed))
json.dump({"n_clusters_body": len([g for g in confirmed if len(g)>1]),
           "dup_ids_body": len(dup_ids),
           "inert_params": {k: sum(v.values()) for k,v in inert.items()},
           "clusters_by_family": dict(byfam)},
          open(os.path.join(ROOT,"results","reproduction_d2","duplicate_audit_summary.json"),"w"), indent=1)
print("\nwrote duplicate_audit_summary.json")

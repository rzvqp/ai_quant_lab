import sys, os, json, hashlib
import pandas as pd, numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = r"C:\Users\MEDION~1\AppData\Local\Temp\v2"
OUT = r"C:\Users\MEDION GAMING\ai_quant_lab\statistician\attribution_v2"
os.makedirs(OUT, exist_ok=True)
M = pd.read_csv(r"C:\Users\MEDION GAMING\ai_quant_lab\statistician\COMPLETE_STRATEGY_GRAVEYARD_MANIFEST_V1.csv")
R = pd.read_csv(os.path.join(T, "rep_map.csv"))
B = pd.read_csv(os.path.join(T, "BLINDED_FEATURE_SCHEMA.csv"))

# ---------- 1. attribution objects ----------
classA = M[(M.ATTRIBUTION_CLASS.str.startswith("A_")) & (M.BLOCK == "C")].OBJECT_ID.tolist()   # 14 analysable units
slib = R[R.STATUS == "ELIGIBLE"].copy()
er = M[(M.BLOCK == "E")].OBJECT_ID.tolist()
fac = M[(M.BLOCK == "B") & (M.ATTRIBUTION_CLASS.str.startswith("B_"))].OBJECT_ID.tolist()
frz = M[(M.BLOCK == "D") & (M.ATTRIBUTION_CLASS.str.startswith("B_"))].OBJECT_ID.tolist()
objs = []
for o in classA: objs.append(dict(OBJECT_ID=o, TIER="T1_LOG_EXISTS", SOURCE="Alpha V1 generators"))
for _, r in slib.iterrows():
    objs.append(dict(OBJECT_ID=f"{r.FAMILY_ID}::{r.REP_ID}", TIER="T1_REGENERATE_SLIB", SOURCE=r.RULE))
for o in er: objs.append(dict(OBJECT_ID=o, TIER="T2_REGENERATE_EDGERESEARCH", SOURCE="edge_research module"))
for o in fac: objs.append(dict(OBJECT_ID=o, TIER="T2_REGENERATE_FACTORY", SOURCE="alpha_discovery module"))
for o in frz: objs.append(dict(OBJECT_ID=o, TIER="T2_REGENERATE_FROZEN_SPEC", SOURCE="frozen spec"))
O = pd.DataFrame(objs)
print("=" * 108); print("  ATTRIBUTION_UNIVERSE_V2"); print("=" * 108)
print(f"  {O.TIER.value_counts().sort_index().to_string()}")
print(f"  TOTAL ATTRIBUTION OBJECTS = {len(O)}")

# ---------- 2. binning ----------
BINS = {"numeric": 5, "bool": 2}
CATLEV = _load_held_back_catlev()   # REDACTED: maps true feature names -> declared bin counts;
                                    # held by the Statistician, released at unblinding.
SEC = pd.read_csv(os.path.join(T, "feature_map_SECRET.csv"))
nb = []
for _, r in SEC.iterrows():
    nb.append(CATLEV.get(r.TRUE_NAME, BINS.get(r.KIND, 5)))
SEC["N_BINS"] = nb
print(f"\n  binning: numeric -> 5 causal quintiles (trailing-2000-bar rank; NO threshold scanning)")
print(f"           bool    -> 2 levels;  categorical -> declared natural levels")
print(f"  total declared bins across the 46 features = {int(SEC.N_BINS.sum())}")

# ---------- 3. declared tests ----------
NF = len(B); NO = len(O)
S1 = NF * NO                      # stage 1: one omnibus test per (object, feature)
S2 = NF                           # stage 2: one recurrence test per feature
S3 = 20                           # stage 3: bounded interactions, declared count
TOT = S1 + S2 + S3
print("\n" + "=" * 108); print("  SEARCH BUDGET (frozen before any outcome is read)"); print("=" * 108)
print(f"  STAGE 1  per-object x per-feature omnibus         : {NF} x {NO} = {S1}")
print(f"  STAGE 2  cross-family recurrence, one per feature : {S2}")
print(f"  STAGE 3  bounded interactions (declared cap)      : {S3}")
print(f"  TOTAL_DECLARED_TESTS = {TOT}")
print(f"  BH-FDR q=0.05 on stage 1 · Bonferroni m={S2} on stage 2 · Bonferroni m={S3} on stage 3")
print(f"  (Bonferroni at the full {TOT} would require |z| > {abs(round(float(__import__('statistics').NormalDist().inv_cdf(0.025/TOT)),2))} -- reported as a reference bound, not the primary policy)")

# ---------- 4. post-entry eligibility ----------
mt = pd.read_csv(r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\STRATEGY_ATTRIBUTION_MASTER_TABLE.csv")
pe = mt.groupby("sid")["mfe"].apply(lambda s: int(s.notna().sum()) > 0)
POST = sorted(pe[pe].index.tolist())
print("\n" + "=" * 108); print("  POST-ENTRY ELIGIBILITY"); print("=" * 108)
print(f"  families with valid path (MFE/MAE) TODAY = {len(POST)} : {POST}")
print(f"  families WITHOUT path = {sorted(pe[~pe].index.tolist())}")
print(f"  S-library representatives: simulate() emits (R, si, ei) but NOT MFE/MAE ->")
print(f"    CONDITIONALLY eligible once path is recomputed causally from (si, ei) + bars; until then EXCLUDED.")

# ---------- 5. package ----------
O.to_csv(os.path.join(OUT, "ATTRIBUTION_UNIVERSE_V2.csv"), index=False)
slib.to_csv(os.path.join(OUT, "REPRESENTATIVE_VARIANT_MAP.csv"), index=False)
B.to_csv(os.path.join(OUT, "BLINDED_FEATURE_SCHEMA.csv"), index=False)
SEC[["BLIND_ID", "KIND", "N_BINS"]].to_csv(os.path.join(OUT, "FEATURE_BINNING.csv"), index=False)
pd.DataFrame(dict(OBJECT_ID=POST)).to_csv(os.path.join(OUT, "POST_ENTRY_ELIGIBILITY.csv"), index=False)
budget = dict(stage1_per_object_per_feature=S1, stage2_recurrence=S2, stage3_interactions=S3,
              total_declared_tests=TOT, multiplicity="BH-FDR q=0.05 (stage1); Bonferroni (stage2 m=46, stage3 m=20)",
              min_trades_per_bin=30, min_independent_days_per_bin=20,
              binning="numeric=5 causal quintiles on a trailing 2000-bar rank; bool=2; categorical=declared levels",
              interactions=_BLIND_INTERACTION_RULE)   # see SEARCH_BUDGET.json (fully blind, no feature name required)
json.dump(budget, open(os.path.join(OUT, "SEARCH_BUDGET.json"), "w"), indent=1)

files = sorted(os.listdir(OUT))
h = hashlib.sha256()
for f in files:
    h.update(f.encode()); h.update(open(os.path.join(OUT, f), "rb").read())
PKG = h.hexdigest()
print("\n" + "=" * 108); print("  FROZEN PACKAGE"); print("=" * 108)
for f in files: print(f"    {f}")
print(f"\n  PROTOCOL_PACKAGE_HASH = {PKG}")
print(f"  FEATURE_MAP_HASH      = {json.load(open(os.path.join(T,'feat_meta.json')))['feature_map_hash']}")
print(f"  (feature_map_SECRET.csv is deliberately NOT in the package -- Alpha must not receive it)")
json.dump(dict(pkg=PKG, objects=len(O), tests=TOT), open(os.path.join(T, "pkg.json"), "w"))

import sys, os, pandas as pd, numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
M=pd.read_csv(r"C:\Users\MEDION GAMING\ai_quant_lab\statistician\COMPLETE_STRATEGY_GRAVEYARD_MANIFEST_V1.csv")
A14=set(M[M.BLOCK=="C"].OBJECT_ID)
elig=M[M.ATTRIBUTION_CLASS.str.startswith(("A_","B_"))]
print("="*110); print("  ALPHA V1 COVERAGE AUDIT"); print("="*110)
print(f"  TOTAL_OBJECTS_DISCOVERED        = {len(M)}")
print(f"  attribution-eligible (class A/B) = {len(elig)}")
print(f"  ALPHA_V1_FAMILIES_ANALYSED       = {len(A14)}")
print(f"  COVERAGE_BY_FAMILY               = {100*len(A14)/len(elig):.1f}%   ({len(A14)}/{len(elig)})")
me=set(elig.MECHANISM_ID); ma=set(M[M.OBJECT_ID.isin(A14)].MECHANISM_ID)
print(f"\n  distinct mechanisms among eligible objects = {len(me)}")
print(f"  distinct mechanisms covered by Alpha V1    = {len(ma)}  -> {sorted(ma)}")
print(f"  COVERAGE_BY_DISTINCT_MECHANISM = {100*len(ma)/len(me):.1f}%")
print(f"\n  MECHANISMS MISSED ENTIRELY ({len(me-ma)}):")
for m in sorted(me-ma): print(f"    {m}")
core=pd.read_parquet(os.path.join(AA,"results","FAMILY_RESULTS.parquet"),engine="fastparquet")
ext=pd.read_parquet(os.path.join(AA,"results","ext_families","EXT_FAMILY_RESULTS.parquet"),engine="fastparquet")
al=pd.concat([core,ext]); al=al[~al.fam.isin(["S47","S49"])]
rep=al.groupby("fam")["n"].max().sum()
print(f"\n  TRADE VOLUME AVAILABLE (S-library, ONE representative variant per family, 42 valid families):")
print(f"    representative trades = {int(rep):,}      (all {len(al)} variants pooled = {int(al.n.sum()):,} variant-trades)")
print(f"    Alpha V1 analysed     = 30,703 trades from 14 objects")
print(f"    COVERAGE_BY_VALID_TRADES (vs S-library representative alone) = {100*30703/(30703+rep):.1f}%")
print(f"\n  VALID_FAMILIES_MISSED_BY_ALPHA_V1 (attribution-eligible, not analysed) = {len(elig)-len(A14)}")
miss=elig[~elig.OBJECT_ID.isin(A14)]
print(f"    by block: {miss.BLOCK.value_counts().sort_index().to_dict()}")
print(f"\n  WHY MISSED (mandate S12 classification):")
r={}
for _,x in miss.iterrows():
    if x.BLOCK=="A": r.setdefault("GENERATOR_NOT_CALLABLE_FROM_ALPHA_CWD (S-library engine not imported by attr_run.py)",[]).append(x.OBJECT_ID)
    elif x.BLOCK=="E": r.setdefault("NOT_DISCOVERED_BY_ALPHA (edge_research series never enumerated)",[]).append(x.OBJECT_ID)
    elif x.BLOCK=="B": r.setdefault("FORMAT_INCOMPATIBLE (different panel/timeframe; Alpha noted these explicitly)",[]).append(x.OBJECT_ID)
    else: r.setdefault("NO_TRADE_LOG / frozen-spec only",[]).append(x.OBJECT_ID)
for k,v in r.items(): print(f"    {k}: {len(v)}")
print(f"\n  ATTRIBUTION_UNIVERSE_V2 (class A) = {sorted(M[M.ATTRIBUTION_CLASS.str.startswith('A_')].OBJECT_ID)}")
print(f"\n  REGENERATION_REQUIRED (class B) = {len(M[M.ATTRIBUTION_CLASS.str.startswith('B_')])} objects")
print(f"  UNUSABLE (class C/D) = {len(M[M.ATTRIBUTION_CLASS.str.startswith(('C_','D_'))])} objects")

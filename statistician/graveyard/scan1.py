import sys, glob, os, re
import pandas as pd, numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
print("="*110); print("  A. CORE S-FAMILY CAMPAIGN (ENGINE v2)"); print("="*110)
core = pd.read_parquet(os.path.join(AA,"results","FAMILY_RESULTS.parquet"), engine="fastparquet")
print(f"  results/FAMILY_RESULTS.parquet : rows {len(core)}  cols {list(core.columns)}")
fc = 'fam' if 'fam' in core.columns else core.columns[0]
print(f"  families {core[fc].nunique()} -> {sorted(core[fc].unique(), key=lambda s:int(re.sub(r'\D','',str(s)) or 0))}")
print(f"  variants (rows) per family: total {len(core)}")
ext = pd.read_parquet(os.path.join(AA,"results","ext_families","EXT_FAMILY_RESULTS.parquet"), engine="fastparquet")
print(f"\n  results/ext_families/EXT_FAMILY_RESULTS.parquet : rows {len(ext)}  families {ext['fam'].nunique()}")
print(f"  -> {sorted(ext['fam'].unique(), key=lambda s:int(re.sub(r'\D','',str(s)) or 0))}")
per = {}
for f in sorted(glob.glob(os.path.join(AA,"results","ext_families","S*_results.parquet"))):
    fam = os.path.basename(f).split("_")[0]
    d = pd.read_parquet(f, engine="fastparquet"); per[fam] = len(d)
print(f"\n  per-family variant counts (S21+): {per}")
print(f"  sum of ext variants = {sum(per.values())}")
allv = len(core) + sum(per.values())
print(f"\n  TOTAL VARIANT ROWS (core {len(core)} + ext {sum(per.values())}) = {allv}")
core.to_csv("core.csv", index=False); ext.to_csv("ext.csv", index=False)

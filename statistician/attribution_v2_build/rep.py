"""REPRESENTATIVE_VARIANT_MAP -- outcome-blind. Regenerates each family's FROZEN grammar and takes the
canonical declaration-order representative. No PnL/WR/PF/expectancy/DD/OOS field is read anywhere here."""
import sys, os, json, hashlib
import pandas as pd, numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
sys.path.insert(0, os.path.join(AA, "code"))
os.chdir(os.path.join(AA, "code"))
import mstrat as MS, mstrat_ext as MX

GRAMMARS = {}
for fam, (gram, _setups) in MS.REGISTRY.items():
    GRAMMARS[fam] = gram
for fam, (gram, _setups) in MX.EXT_REGISTRY.items():
    GRAMMARS[fam] = gram
print(f"  frozen grammar functions available: {len(GRAMMARS)} families")

# side/direction dimension names actually used by the library
SIDE_KEYS = ("side", "dir", "direction")
rows = []
for fam in sorted(GRAMMARS, key=lambda s: int(s[1:])):
    hs = GRAMMARS[fam]()
    if not hs:
        rows.append(dict(FAMILY_ID=fam, REP_ID="", RULE="EMPTY_GRAMMAR", SPEC="", N_VARIANTS=0)); continue
    keys = [k for k in hs[0] if k not in ("family", "id")]
    sk = next((k for k in SIDE_KEYS if k in keys), None)
    picks = []
    if sk:
        seen = []
        for h in hs:                       # declaration order preserved by itertools.product
            if h[sk] not in seen:
                seen.append(h[sk]); picks.append((h, f"GRAMMAR_FIRST_PER_{sk.upper()}={h[sk]}"))
    else:
        picks = [(hs[0], "GRAMMAR_INDEX_0")]
    for h, rule in picks:
        spec = {k: h[k] for k in keys}
        rows.append(dict(FAMILY_ID=fam, REP_ID=h["id"], RULE=rule,
                         SPEC=json.dumps(spec, sort_keys=True), N_VARIANTS=len(hs),
                         SIDE_DIM=sk or ""))
R = pd.DataFrame(rows)

# verify every representative was actually RUN (existence check only -- no metric is read)
core = pd.read_parquet(os.path.join(AA, "results", "FAMILY_RESULTS.parquet"), engine="fastparquet")
ext = pd.read_parquet(os.path.join(AA, "results", "ext_families", "EXT_FAMILY_RESULTS.parquet"), engine="fastparquet")
have = set(pd.concat([core, ext])["id"])
R["RAN"] = R.REP_ID.isin(have)
INVALID = {"S47": "n<25", "S49": "non-selective"}
R["STATUS"] = R.FAMILY_ID.map(lambda f: "INVALID_EXCLUDED" if f in INVALID else "ELIGIBLE")

print(f"\n  representatives produced : {len(R)}")
print(f"  families covered         : {R.FAMILY_ID.nunique()}")
print(f"  families with a side dim : {R[R.SIDE_DIM!=''].FAMILY_ID.nunique()}  -> 1 representative per declared side")
print(f"  representatives verified present in the frozen result set : {int(R.RAN.sum())}/{len(R)}")
miss = R[~R.RAN]
if len(miss):
    print(f"  NOT FOUND (must be reported as FAILED_REGENERATION if they cannot be rerun):")
    print(miss[["FAMILY_ID","REP_ID","RULE"]].to_string(index=False))
elig = R[R.STATUS == "ELIGIBLE"]
print(f"\n  ELIGIBLE representatives (S-library) = {len(elig)} across {elig.FAMILY_ID.nunique()} families")
print(f"\n  sample:")
print(R.head(8)[["FAMILY_ID","REP_ID","RULE","SPEC"]].to_string(index=False, max_colwidth=70))
R.to_csv(r"C:\Users\MEDION~1\AppData\Local\Temp\v2\rep_map.csv", index=False)
print(f"\n  wrote rep_map.csv")

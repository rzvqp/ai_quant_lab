import sys, os, hashlib
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
MK = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market"
print("="*104); print("  MULTI_SESSION_LONG_HORIZON_ALPHA_SCOUT_V1 -- SECTION 2 DATA AUDIT"); print("="*104)

def load(name):
    p = os.path.join(MK, name)
    d = pd.read_csv(p)
    d = d.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    d["t"] = pd.to_datetime(d["time"], unit="s", utc=True)
    h = hashlib.sha256(open(p,"rb").read()).hexdigest()
    return d, h

for nm in ("OANDA_XAUUSD_M15.csv","OANDA_XAUUSD_M5.csv","OANDA_XAUUSD_H1_from_M15_v2.csv","OANDA_XAUUSD_H1.csv"):
    d,h = load(nm)
    raw = len(pd.read_csv(os.path.join(MK,nm)))
    print(f"\n  {nm}")
    print(f"    bars {len(d)} (raw {raw}, dupes dropped {raw-len(d)})   {d.t.min()} -> {d.t.max()}")
    print(f"    sha256 {h[:32]}...")

print("\n" + "="*104); print("  M15 GAP STRUCTURE  (the 2013-2016 concern is checked explicitly)"); print("="*104)
m,_ = load("OANDA_XAUUSD_M15.csv")
dt = m.t.diff().dt.total_seconds()/60.0
print(f"  expected step 15 min. steps == 15 : {(dt==15).sum()} / {len(dt)-1}  ({(dt==15).mean():.1%})")
big = m.loc[dt > 60*24*3, ["t"]].copy(); big["gap_days"] = (dt[dt>60*24*3]/1440).values
print(f"\n  gaps LONGER THAN 3 DAYS (weekend = ~2.1d, so these are real holes):")
if len(big)==0: print("    none")
for _,r in big.iterrows():
    print(f"    ends {r.t}   length {r.gap_days:.1f} days   (starts {r.t - pd.Timedelta(days=r.gap_days)})")
yr = m.t.dt.year.value_counts().sort_index()
exp = 365*24*4*(5/7)
print(f"\n  bars per calendar year (a full year of 24x5 M15 ~= {exp:.0f}):")
for y,c in yr.items(): print(f"    {y}: {c:6d}   {'*** SPARSE ***' if c < exp*0.75 and y not in (2011,2026) else ''}")

print("\n" + "="*104); print("  HOLDOUT FIREWALL"); print("="*104)
CUT = pd.Timestamp("2025-10-23T09:15:00+00:00")
print(f"  program constant RESEARCH_HOLDOUT_CUTOFF_UTC = {CUT}  (edge_research/_common.py:43)")
print(f"  bars at or after cutoff (PROTECTED, will NOT be consumed): {(m.t>=CUT).sum()}")
u = m[m.t < CUT]
print(f"  usable research window: {u.t.min()} -> {u.t.max()}   bars {len(u)}   ({(u.t.max()-u.t.min()).days/365.25:.1f} years)")
m5,_ = load("OANDA_XAUUSD_M5.csv")
print(f"  native M5 for comparison : {m5.t.min()} -> {m5.t.max()}   ({(m5.t.max()-m5.t.min()).days/365.25:.1f} years)")
print(f"  -> extra history gained by moving to M15: {((u.t.max()-u.t.min()) - (m5.t.max()-m5.t.min())).days/365.25:.1f} years")

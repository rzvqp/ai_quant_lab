#!/usr/bin/env python3
"""Diagnostic (read-only) for the 196 M15 overlap mismatches.
TEST C: volume-delta distribution. Plus: documented-artifact presence in existing vs new.
Modifies nothing; chooses no version."""
import csv
from datetime import datetime, timezone

def iso(ep): return datetime.fromtimestamp(ep, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

def load(path):
    rows = {}
    with open(path, newline="") as f:
        r = csv.reader(f); next(r)
        for ln in r:
            if not ln or not ln[0].strip(): continue
            rows[int(ln[0])] = (int(ln[0]), float(ln[1]), float(ln[2]), float(ln[3]), float(ln[4]), float(ln[5]))
    return rows

NEW = load("acquisition_staging/OANDA_XAUUSD_M15.csv")
EX  = load("data/market/OANDA_XAUUSD_M15.csv")
common = sorted(set(NEW) & set(EX))
mism = [t for t in common if any(NEW[t][i] != EX[t][i] for i in range(1, 6))]

print("="*72)
print(f"overlap={len(common)}  mismatches={len(mism)}")
print("="*72)

# ---- TEST C: volume delta distribution ----
print("\n[TEST C] volume |delta| distribution over the mismatches")
vd = sorted(abs(NEW[t][5] - EX[t][5]) for t in mism)
buckets = [(0,0,"exactly 0"),(1,10,"1-10"),(11,100,"11-100"),(101,1000,"101-1000"),
           (1001,10000,"1001-10000")]
for lo, hi, lab in buckets:
    n = sum(1 for d in vd if lo <= d <= hi)
    print(f"   |dV| {lab:12s}: {n}")
nz = [d for d in vd if d > 0]
if nz:
    print(f"   nonzero dV: n={len(nz)} min={min(nz):.0f} median={nz[len(nz)//2]:.0f} "
          f"p90={nz[int(0.9*len(nz))]:.0f} max={max(nz):.0f} mean={sum(nz)/len(nz):.1f}")
print("   largest 10 volume deltas:")
for t in sorted(mism, key=lambda t: -abs(NEW[t][5]-EX[t][5]))[:10]:
    print(f"     {iso(t)}  new_vol={NEW[t][5]:.0f}  ex_vol={EX[t][5]:.0f}  dV={NEW[t][5]-EX[t][5]:+.0f}  "
          f"dClose={NEW[t][4]-EX[t][4]:+.3f}")

# ---- close/price delta distribution (context for C) ----
print("\n[context] close |delta| distribution over the mismatches")
cd = sorted(abs(NEW[t][4] - EX[t][4]) for t in mism)
for lo, hi, lab in [(0,0,"exactly 0"),(0.0001,0.05,"<=0.05"),(0.05,0.2,"0.05-0.2"),
                    (0.2,1.0,"0.2-1.0"),(1.0,10,">1.0")]:
    n = sum(1 for d in cd if lo < d <= hi) if lo>0 else sum(1 for d in cd if d==0)
    print(f"   |dC| {lab:12s}: {n}")

# ---- Artifact presence: documented signature range 120-136 @ vol 748-3980 ----
print("\n[ARTIFACT] documented signature (range 120-136pt AND vol 748-3980)")
def sig(b): return 120 <= (b[2]-b[3]) <= 136 and 748 <= b[5] <= 3980
ex_sig = [t for t in EX if sig(EX[t])]
new_sig = [t for t in NEW if sig(NEW[t])]
print(f"   in EXISTING file : {len(ex_sig)}")
print(f"   in NEW file      : {len(new_sig)}")
for t in sorted(ex_sig):
    innew = NEW.get(t)
    tag = "(NOT in new)" if innew is None else ("(identical in new)" if innew==EX[t] else "(DIFFERS in new)")
    print(f"     EX {iso(t)} range={EX[t][2]-EX[t][3]:.2f} vol={EX[t][5]:.0f} {tag}")
    if innew is not None and innew != EX[t]:
        print(f"        new: range={innew[2]-innew[3]:.2f} vol={innew[5]:.0f} close={innew[4]} | ex close={EX[t][4]}")

# ---- Around 2026-01-29 (Alpha Observation Registry entry 17) ----
print("\n[2026-01-29 window] bars flagged by Alpha (high vol / artifact) — existing vs new")
lo = int(datetime(2026,1,29,tzinfo=timezone.utc).timestamp())
hi = int(datetime(2026,1,30,tzinfo=timezone.utc).timestamp())
# highest-volume existing bars that day
day = sorted([t for t in EX if lo<=t<hi], key=lambda t:-EX[t][5])[:6]
for t in day:
    innew = NEW.get(t)
    d = "MATCH" if innew==EX[t] else ("MISSING" if innew is None else "DIFF")
    extra = "" if innew is None or innew==EX[t] else f"  new_vol={innew[5]:.0f} new_close={innew[4]}"
    print(f"     {iso(t)} ex_vol={EX[t][5]:.0f} ex_range={EX[t][2]-EX[t][3]:.2f} ex_close={EX[t][4]} -> {d}{extra}")

#!/usr/bin/env python3
"""TEST A: do the 196 overlap mismatches concentrate on window-boundary bars?
Joins the staged-vs-existing mismatch set with per-bar edge-from-right position from the
instrumented re-pull. Read-only; modifies nothing."""
import csv, sys
from datetime import datetime, timezone

def iso(ep): return datetime.fromtimestamp(ep, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

def load(path):
    d = {}
    with open(path, newline="") as f:
        r = csv.reader(f); next(r)
        for ln in r:
            if not ln or not ln[0].strip(): continue
            d[int(ln[0])] = tuple(float(x) for x in ln[1:6])
    return d

SC = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/MEDION~1/AppData/Local/Temp/claude/C--Users-MEDION-GAMING-tradingview-mcp/8790cba3-f745-45e3-ad32-17c6c2676463/scratchpad"
NEW = load("acquisition_staging/OANDA_XAUUSD_M15.csv")
EX  = load("data/market/OANDA_XAUUSD_M15.csv")
RE  = load(f"{SC}/edgepull_m15.csv")

edges = {}
with open(f"{SC}/edgepull_edges.csv", newline="") as f:
    r = csv.reader(f); next(r)
    for ln in r:
        if not ln or not ln[0].strip(): continue
        edges[int(ln[0])] = (int(ln[1]), int(ln[2]))  # (edgeFromRight, winSize)

overlap = sorted(set(NEW) & set(EX))
mism = set(t for t in overlap if NEW[t] != EX[t])
print("="*72)
print(f"overlap bars={len(overlap)}  mismatches(staged vs existing)={len(mism)}")

# sanity: re-pull vs staged on overlap (both 'now' captures -> should match)
re_ov = [t for t in overlap if t in RE]
re_vs_staged = sum(1 for t in re_ov if RE[t] != NEW[t])
print(f"re-pull covers {len(re_ov)}/{len(overlap)} overlap bars; re-pull!=staged on {re_vs_staged}")
print("="*72)

# edge distribution over overlap bars we have edge info for
have = [t for t in overlap if t in edges]
def bucket(e): return "0 (right edge)" if e == 0 else "1" if e == 1 else "2" if e == 2 else "3+ (interior)"
from collections import defaultdict
tot = defaultdict(int); mis = defaultdict(int)
for t in have:
    b = bucket(edges[t][0]); tot[b] += 1
    if t in mism: mis[b] += 1
print(f"edge info available for {len(have)}/{len(overlap)} overlap bars")
print(f"\n{'edgeFromRight':16s} {'#bars':>8s} {'#mismatch':>10s} {'rate%':>8s}")
for b in ["0 (right edge)", "1", "2", "3+ (interior)"]:
    rate = 100*mis[b]/tot[b] if tot[b] else 0
    print(f"{b:16s} {tot[b]:8d} {mis[b]:10d} {rate:8.3f}")

mism_with_edge = [t for t in mism if t in edges]
n0 = sum(1 for t in mism_with_edge if edges[t][0] == 0)
print(f"\nof {len(mism_with_edge)} mismatches with edge info: {n0} are edge==0 "
      f"({100*n0/len(mism_with_edge):.1f}%)")
print("window sizes seen:", sorted(set(w for _, w in edges.values())))
# verdict hint
if have:
    r0 = 100*mis['0 (right edge)']/tot['0 (right edge)'] if tot['0 (right edge)'] else 0
    ri = 100*mis['3+ (interior)']/tot['3+ (interior)'] if tot['3+ (interior)'] else 0
    print(f"\nright-edge mismatch rate={r0:.3f}%  vs interior={ri:.3f}%  ratio={r0/ri if ri else float('inf'):.1f}x")

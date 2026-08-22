from __future__ import annotations
import json, sys, os, collections
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
B=os.path.dirname(os.path.abspath(__file__))
V=json.load(open(os.path.join(B,"S_v44.json"))); N=json.load(open(os.path.join(B,"S_vnext.json")))
BIG=10**9
def f(x):
    try: return None if x in (None,"None","") else float(x)
    except Exception: return None
for r in V+N:
    for k in ("start","conf","end","bu","bl"): r[k]=f(r[k])
Vc=[r for r in V if r["confirmed"]]
children=collections.defaultdict(list)
for r in N:
    for key in ("cont","pred"):
        v=r.get(key)
        if v not in (None,"None"):
            try: children[int(float(v))].append(r)
            except Exception: pass
def chain_conf(r,seen=None,d=0):
    seen=seen if seen is not None else set()
    if r["sid"] in seen or d>60: return False
    seen.add(r["sid"])
    return r["confirmed"] or any(chain_conf(c,seen,d+1) for c in children.get(r["sid"],[]))
def iou(a,b):
    if None in (a[0],a[1],b[0],b[1]): return 0.0
    lo=max(a[0],b[0]); hi=min(a[1],b[1])
    return 0.0 if hi<=lo else (hi-lo)/max(1e-12,(max(a[1],b[1])-min(a[0],b[0])))
def run(tol, thr):
    lost=[]
    for v in Vc:
        vs=(v["start"] or 0)-tol; ve_=(v["end"] if v["end"] is not None else BIG)+tol
        ov=[n for n in N
            if not ((n["end"] if n["end"] is not None else BIG) < vs or (n["start"] or 0) > ve_)
            and iou((v["bl"],v["bu"]),(n["bl"],n["bu"]))>thr]
        if not ov: lost.append((v,"UNMATCHABLE",[])); continue
        if any(n["confirmed"] for n in ov): continue
        if any(chain_conf(n) for n in ov): continue
        lost.append((v,"LOST",sorted({str(n["reason"]) for n in ov})))
    return lost
print("="*84); print("NEGATIVE-CONTROL SENSITIVITY -- how methodology-dependent is the premature-kill rate?")
print("="*84)
print(f"  {'time tol (bars)':>16} | " + " | ".join(f"IoU>{t:<4}" for t in (0.0,0.1,0.3)))
grid={}
for tol in (0, 29, 100, 500, 2000):
    row=[]
    for thr in (0.0,0.1,0.3):
        L=run(tol,thr); grid[(tol,thr)]=L
        row.append(f"{len(L):3d}/{len(Vc)} {len(L)/len(Vc):6.2%}")
    print(f"  {tol:>16} | " + " | ".join(row))
print(f"\n  VE's published figure: 5/187 = 2.67%   (or 4/187 = 2.14%)")
base=grid[(0,0.0)]
print(f"  My primary setting (tol=0, any zone overlap): {len(base)}/{len(Vc)} = {len(base)/len(Vc):.2%}")
wide=grid[(500,0.0)]
print(f"  Most generous to vNext (tol=500 bars, any overlap): {len(wide)}/{len(Vc)} = {len(wide)/len(Vc):.2%}")
lo=min(len(v) for v in grid.values()); hi=max(len(v) for v in grid.values())
print(f"  RANGE ACROSS ALL SETTINGS: {lo}-{hi} of {len(Vc)} = {lo/len(Vc):.2%} - {hi/len(Vc):.2%}")
print(f"\n  Mechanism attribution at the most generous setting (tol=500, any overlap):")
ab=sum(1 for _,k,r in wide if any("ABANDONED" in x for x in r))
mg=sum(1 for _,k,r in wide if any("SUPERSEDED_BY_MERGE" in x for x in r))
cp=sum(1 for _,k,r in wide if any("CAPACITY" in x for x in r))
print(f"    abandonment {ab} | merge {mg} | capacity {cp} | of {len(wide)} lost")
json.dump({f"tol{t}_iou{th}":len(v) for (t,th),v in grid.items()}, open(os.path.join(B,"SENS.json"),"w"), indent=1)

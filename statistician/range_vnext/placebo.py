from __future__ import annotations
import json, sys, os, collections, random
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
Vc=[r for r in V if r["confirmed"] and r["bl"] is not None and r["bu"] is not None]
Nc=[n for n in N if n["confirmed"]]
def iou(a,b):
    lo=max(a[0],b[0]); hi=min(a[1],b[1])
    return 0.0 if hi<=lo else (hi-lo)/max(1e-12,(max(a[1],b[1])-min(a[0],b[0])))
def matched(v, tol, thr, tshift=0, zone=None):
    vs=(v["start"] or 0)+tshift-tol; ve_=((v["end"] if v["end"] is not None else BIG))+tshift+tol
    z=zone if zone is not None else (v["bl"],v["bu"])
    for n in Nc:
        if n["bl"] is None or n["bu"] is None: continue
        if (n["end"] if n["end"] is not None else BIG) < vs or (n["start"] or 0) > ve_: continue
        if iou(z,(n["bl"],n["bu"]))>thr: return True
    return False
print("="*88)
print("PLACEBO CONTROL -- does the matcher discriminate, or is it reading a base rate?")
print("="*88)
print("  vNext produces 4092 confirmed structures vs v4.4's 187 (21.9x). A loose matcher will find")
print("  'a confirmed structure nearby' for almost any window by chance. Test: REAL episodes vs")
print("  TIME-SHIFTED placebos (same zone, wrong era) and ZONE-SHUFFLED placebos (right era, wrong zone).")
rng=random.Random(11)
zones=[(v["bl"],v["bu"]) for v in Vc]
print(f"\n  {'tol':>5} {'IoU>':>5} | {'REAL match':>11} | {'TIME-SHIFTED +80k':>18} | {'ZONE-SHUFFLED':>14} | discrimination")
for tol in (0,29,100,500,2000):
    for thr in (0.0,0.3):
        real=np.mean([matched(v,tol,thr) for v in Vc])
        shift=np.mean([matched(v,tol,thr,tshift=80000) for v in Vc])
        zsh=[]
        for v in Vc:
            z=zones[rng.randrange(len(zones))]
            zsh.append(matched(v,tol,thr,zone=z))
        zsh=np.mean(zsh)
        disc=real-max(shift,zsh)
        print(f"  {tol:5d} {thr:5.1f} | {real:10.1%} | {shift:17.1%} | {zsh:13.1%} | {disc:+.1%}")
print("\n  A matcher whose PLACEBO match rate approaches its REAL match rate is measuring the base rate,")
print("  not correspondence -- and its complement ('lost') is then not a premature-kill rate at all.")

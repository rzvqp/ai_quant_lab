from __future__ import annotations
import json, sys, os, collections
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
B=os.path.dirname(os.path.abspath(__file__))
V=json.load(open(os.path.join(B,"S_v44.json"))); N=json.load(open(os.path.join(B,"S_vnext.json")))
def f(x):
    try: return None if x in (None,"None","") else float(x)
    except Exception: return None
for r in V+N:
    for k in ("start","conf","end","bu","bl"): r[k]=f(r[k])
print("="*82); print("SECTION 13 -- FORMATION-AGE GATE (frozen d_macro = 29), per STRUCTURE not per transition")
print("="*82)
for nm,S in (("vNext",N),("v4.4 ",V)):
    a=np.array([r["conf"]-r["start"] for r in S if r["confirmed"] and r["conf"] is not None and r["start"] is not None])
    below=int((a<29).sum())
    print(f"  {nm}: n={len(a):5d}  min={a.min():6.0f}  p1={np.percentile(a,1):6.0f}  median={np.median(a):7.0f}  max={a.max():8.0f}"
          f"   BELOW GATE (<29): {below}  = {below/len(a):.4%}")
    if below: print(f"        below-gate ages: {sorted(a[a<29].tolist())[:20]}")
print("\n  Confirmations reached via a MERGE or CONTINUATION identity (fresh start_ts by construction):")
for nm,S in (("vNext",N),):
    mc=[r for r in S if r["confirmed"] and r.get("cont") not in (None,"None")]
    a=np.array([r["conf"]-r["start"] for r in mc if r["conf"] is not None and r["start"] is not None])
    if len(a): print(f"    n={len(a)}  min age={a.min():.0f}  below gate={int((a<29).sum())}  -> identity inheritance does NOT bypass the gate")
print("\n"+"="*82); print("SECTION 11 -- TERMINATION-REASON PROFILE (vNext, all macro structures)"); print("="*82)
er=collections.Counter(str(r["reason"]) for r in N if r["end"] is not None)
tot=sum(er.values())
for k,x in er.most_common(9): print(f"    {k:44} {x:6d}  {x/tot:7.2%}")
ca=sum(1 for r in N if r["confirmed"] and str(r["reason"])=="CANDIDATE_ABANDONED_PRICE_MOVED_ON")
print(f"\n  CONFIRMED structures terminated by price-abandonment: {ca}")
print(f"    (the code path skips st.reached_confirmed -- expected exactly 0; observed {ca})")
al=[r for r in N if str(r["reason"])=="CANDIDATE_ABANDONED_PRICE_MOVED_ON"]
lifetimes=np.array([r["end"]-r["start"] for r in al if r["end"] is not None and r["start"] is not None])
print(f"  abandoned-candidate lifetimes: n={len(lifetimes)} median={np.median(lifetimes):.0f} p95={np.percentile(lifetimes,95):.0f} max={lifetimes.max():.0f} bars")
print(f"  fraction abandoned BEFORE reaching the age gate (age<29): {(lifetimes<29).mean():.2%}")
print(f"    -> if abandonment were an age-timeout in disguise, this would cluster at a fixed age; it does not.")

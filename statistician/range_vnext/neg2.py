"""Independent negative control -- does NOT reuse VE's matching implementation.
Every v4.4 confirmed episode is matched against vNext's own full structure history by
time-window overlap AND zone overlap, with forward merge/continuation chain following."""
from __future__ import annotations
import json, sys, collections
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import os as _o
_B=_o.path.dirname(_o.path.abspath(__file__))
V=json.load(open(_o.path.join(_B,"S_v44.json"))); N=json.load(open(_o.path.join(_B,"S_vnext.json")))
BIG=10**9
def f(x):
    try: return None if x in (None,"None","") else float(x)
    except Exception: return None
for r in V+N:
    for k in ("start","conf","end","bu","bl"): r[k]=f(r[k])
Vc=[r for r in V if r["confirmed"]]
byid={r["sid"]:r for r in N}
children=collections.defaultdict(list)
for r in N:
    for key in ("cont","pred"):
        v=r.get(key)
        if v not in (None,"None"):
            try: children[int(float(v))].append(r)
            except Exception: pass
def chain_confirmed(r, seen=None, depth=0):
    seen = seen if seen is not None else set()
    if r["sid"] in seen or depth>50: return False
    seen.add(r["sid"])
    if r["confirmed"]: return True
    return any(chain_confirmed(c, seen, depth+1) for c in children.get(r["sid"], []))
def zov(a,b):
    if None in (a[0],a[1],b[0],b[1]): return 0.0
    lo=max(a[0],b[0]); hi=min(a[1],b[1])
    return 0.0 if hi<=lo else (hi-lo)/max(1e-12,(max(a[1],b[1])-min(a[0],b[0])))
cls=collections.Counter(); detail=[]
for v in Vc:
    vs=v["start"] or 0; ve_=v["end"] if v["end"] is not None else BIG
    ov=[n for n in N
        if not ((n["end"] if n["end"] is not None else BIG) < vs or (n["start"] or 0) > ve_)
        and zov((v["bl"],v["bu"]),(n["bl"],n["bu"]))>0.0]
    if not ov:
        cls["UNMATCHABLE_no_overlapping_structure"]+=1
        detail.append(dict(v44_id=v["sid"], kind="UNMATCHABLE", n_overlap=0, end_reasons=[])); continue
    if any(n["sid"]==v["sid"] and n["confirmed"] for n in ov): cls["PRESERVED_same_structure_id"]+=1
    elif any(n["confirmed"] for n in ov):                      cls["CONFIRMED_under_different_identity"]+=1
    elif any(chain_confirmed(n) for n in ov):                  cls["CONFIRMED_via_merge_or_continuation_chain"]+=1
    else:
        cls["GENUINELY_LOST_overlapped_never_confirmed"]+=1
        detail.append(dict(v44_id=v["sid"], kind="LOST", v44_start=v["start"], v44_conf=v["conf"], v44_end=v["end"],
                           n_overlap=len(ov), end_reasons=sorted({str(n["reason"]) for n in ov})))
tot=len(Vc)
print("="*80); print(f"SECTION 8/9 -- NEGATIVE CONTROL against ALL {tot} real v4.4 confirmations"); print("="*80)
for k,x in cls.most_common(): print(f"  {k:48} {x:4d}   {x/tot:8.3%}")
lost=cls["GENUINELY_LOST_overlapped_never_confirmed"]; unm=cls["UNMATCHABLE_no_overlapping_structure"]
print(f"\n  TRUE premature-kill (lost + unmatchable) = {lost+unm}/{tot} = {(lost+unm)/tot:.3%}")
print(f"  VE reports: 5/187 = 2.7%  (or 4/187 = 2.14% excluding one non-vNext-specific case)")
L=[d for d in detail if d["kind"]=="LOST"]
ab=sum(1 for d in L if any("ABANDONED" in r for r in d["end_reasons"]))
mg=sum(1 for d in L if any("SUPERSEDED_BY_MERGE" in r for r in d["end_reasons"]))
cp=sum(1 for d in L if any("CAPACITY" in r for r in d["end_reasons"]))
zd=sum(1 for d in L if any("ZONES_DEGENERATE" in r for r in d["end_reasons"]))
print(f"\n  MECHANISM ATTRIBUTION among the {len(L)} genuinely-lost:")
print(f"    price-abandonment present : {ab}   (VE: 4/187 = 2.14%, 'contributing not isolated')")
print(f"    merge-supersession present: {mg}   (VE: 0/187 = 0.0%)")
print(f"    capacity-refusal present  : {cp}   (VE: 0/187 = 0.0%)")
print(f"    legacy ZONES_DEGENERATE   : {zd}   (pre-existing v4.3/v4.4 semantics, not vNext)")
for d in L: print("      ", d)
json.dump(dict(v44_confirmed=tot, classification=dict(cls), true_lost=lost+unm, rate=(lost+unm)/tot,
               mechanism_attribution=dict(abandonment=ab,merge=mg,capacity=cp,legacy_zones_degenerate=zd),
               detail=detail), open(r"C:SERSMEDION~1APPDATAocaltempnextnegctl.json","w"), indent=1, default=str)
print("\n"+"="*80); print("SECTION 13 -- FORMATION-AGE GATE (frozen d_macro = 29)"); print("="*80)
for nm,S in (("vNext",N),("v4.4",V)):
    a=np.array([r["conf"]-r["start"] for r in S if r["confirmed"] and r["conf"] is not None and r["start"] is not None])
    print(f"  {nm}: n={len(a)}  min={a.min():.0f}  p1={np.percentile(a,1):.0f}  median={np.median(a):.0f}  max={a.max():.0f}"
          f"   BELOW GATE (<29): {int((a<29).sum())} = {(a<29).mean():.4%}")
print("\n"+"="*80); print("SECTION 11 -- SUPERSESSION / ABANDONMENT CONTRIBUTION"); print("="*80)
er=collections.Counter(str(r["reason"]) for r in N if r["end"] is not None)
tote=sum(er.values())
for k,x in er.most_common(8): print(f"    {k:42} {x:6d}  {x/tote:7.2%}")
conf_ab=sum(1 for r in N if r["confirmed"] and str(r["reason"])=="CANDIDATE_ABANDONED_PRICE_MOVED_ON")
print(f"  CONFIRMED structures ended by abandonment: {conf_ab}  (code skips reached_confirmed -- expected 0)")

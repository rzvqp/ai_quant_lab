"""range_atlas.py — RANGE vNext lifecycle EVENT ATLAS engine (mandate: RANGE-LIFECYCLE frontier, information-first).
Contract-INDEPENDENT: takes, per underlying frame, a dict {event_name -> per-bar boolean mask} produced by running the
RATIFIED RANGE vNext (read-only, unmodified) on that frame, plus optional per-bar descriptor arrays (age, width,
atrnorm_width, n_candidates, dist_to_boundary, ...). Produces:
  Phase 1 (describe): count, unique days, session distribution, descriptor medians per event, cross-era.
  Phase 2 (forward path): P(+X/-Y) LONG & SHORT at the 5 predeclared labels, MFE/MAE, cross-era, via passage first-passage.
NO P&L. NO strategy. Direction supplied per event only where the event is inherently directional. S5-independence is a
separate step (deepen) for any material+stable directional event.
"""
import numpy as np, pandas as pd
from state_path_m15 import passage_m15, Pm
from batch_a import _hr_day
LABELS=[(50,50),(70,50),(100,70),(100,100),(150,75)]
SESS=[("Asia",0,7),("Lon",7,13),("NY",13,21),("Off",21,24)]

def _sess(fr, idx):
    hr,_,_=_hr_day(fr); h=hr[idx]; tot=max(len(h),1)
    return {nm:f"{((h>=lo)&(h<hi)).sum()/tot:.0%}" for nm,lo,hi in SESS}

def describe(fr, idx, descriptors=None):
    hr,day,_=_hr_day(fr)
    d=dict(n=len(idx), uniq_days=len(set(day[idx])), sess=_sess(fr,idx))
    if descriptors:
        for k,arr in descriptors.items():
            v=arr[idx]; v=v[np.isfinite(v)]
            if len(v): d[k]=f"med{np.median(v):.2f}(p25 {np.percentile(v,25):.2f}/p75 {np.percentile(v,75):.2f})"
    return d

def forward_line(fr, ou, od, mfe, mae, idx, side, Hbars):
    """Directional (side='L'/'S') forward path at event idx; returns the 5-label P string + MFE/MAE."""
    m=np.zeros(len(fr),bool); m[idx]=True
    parts=[f"+{X}/-{Y}:{Pm(ou,od,X,Y,side,Hbars,m)[0]:.2f}" for (X,Y) in LABELS]
    return "  ".join(parts)+f" | MFE {np.median(mfe[idx]):.0f}p MAE {np.median(mae[idx]):.0f}p"

def bilat_line(fr, ou, od, mfe, mae, idx, Hbars):
    """Neutral event: both L & S asymmetry. Returns per-label L/S and asym=L-S."""
    m=np.zeros(len(fr),bool); m[idx]=True
    out=[]
    for (X,Y) in LABELS:
        L=Pm(ou,od,X,Y,'L',Hbars,m)[0]; S=Pm(ou,od,X,Y,'S',Hbars,m)[0]
        out.append(f"+{X}/-{Y}:L{L:.2f}/S{S:.2f}(a{L-S:+.2f})")
    return "  ".join(out)+f" | MFE {np.median(mfe[idx]):.0f}p MAE {np.median(mae[idx]):.0f}p"

def run_atlas(frames, eras, events, directions=None, descriptors=None, Hbars=32, title=""):
    """frames: {key: frame}. eras: [(tag, framekey, maskcol)]. events: {framekey: {event_name: per-bar mask}}.
    directions: {event_name: 'L'/'S'/None}. descriptors: {framekey: {name: per-bar array}}."""
    directions=directions or {}; descriptors=descriptors or {}
    PSG={k:passage_m15(v,Hmax=Hbars) for k,v in frames.items()}
    ev_names=sorted({e for d in events.values() for e in d})
    print(f"\n===== RANGE vNext EVENT ATLAS{': '+title if title else ''} (Hbars={Hbars}, labels {LABELS}) =====")
    for ev in ev_names:
        print(f"\n--- EVENT: {ev}  (direction={directions.get(ev,'neutral')}) ---")
        for tag,fk,mk in eras:
            fr=frames[fk]; em=events.get(fk,{}).get(ev)
            if em is None: continue
            ou,od,mfe,mae=PSG[fk]; base=fr[mk].to_numpy(); idx=np.where(base&em)[0]; idx=idx[idx<len(fr)-1]
            if len(idx)<25: print(f"  [{tag}] n={len(idx)} (thin)"); continue
            desc=describe(fr,idx,descriptors.get(fk))
            sd=descriptors.get(fk); dstr=" ".join(f"{k}={desc[k]}" for k in desc if k not in("n","uniq_days","sess"))
            print(f"  [{tag}] n={desc['n']} days={desc['uniq_days']} sess={desc['sess']} {dstr}")
            dr=directions.get(ev)
            if dr in ('L','S'): print(f"        path[{dr}]: "+forward_line(fr,ou,od,mfe,mae,idx,dr,Hbars))
            else:               print(f"        path[L/S]: "+bilat_line(fr,ou,od,mfe,mae,idx,Hbars))

if __name__=="__main__":
    print("range_atlas engine ready. Import and call run_atlas(frames,eras,events,...) once RANGE vNext event masks are extracted.")

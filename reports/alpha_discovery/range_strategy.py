"""range_strategy.py — Phase-5 tradeability of the ONLY sign-stable RANGE vNext event: BREAKOUT_ACCEPTED-upper->LONG
(and the mirror BO_dn->SHORT for completeness). Structural invalidation = the range boundary (2 mechanistic variants:
stop=broken boundary `bup` (retest-fail) vs stop=far boundary `blo` (full-range)). Ratified sb engine, STRESS 0.24,
cross-era. If positive + cross-era-stable + material -> deepen + S5-independence; else RANGE fully bounded.
"""
import numpy as np, pandas as pd
import swing_base as sb
from range_atlas2 import load, ERAS

def test(D, evcol, side, stopcol, rr=2.0, H=48):
    per=[]; allR=[]
    for tag,_,_ in ERAS:
        d=D[tag]; sub=d["sub"]; ev=d["ev"]; o=sub["open"].to_numpy(); n=len(sub)
        idx=np.where(ev[evcol].to_numpy().astype(bool))[0]; idx=idx[idx<n-1]
        if len(idx)==0: per.append((tag,0,np.nan)); continue
        idx=np.sort(idx); dd=sb.dedup_events(idx,8); idx=idx[np.isin(idx,dd)]
        entry=o[idx+1]; stoplvl=ev[stopcol].to_numpy()[idx]; sl=np.abs(entry-stoplvl)
        ok=np.isfinite(sl)&(sl>0); idx=idx[ok]; sl=sl[ok]
        if len(idx)<25: per.append((tag,len(idx),np.nan)); continue
        tr=sb.simulate(sub,idx,side,sl,rr=rr,horizon=H,scenario="STRESS")
        r=tr["R"].to_numpy(); per.append((tag,len(tr),float(r.mean()))); allR.append(r)
    R=np.concatenate(allR) if allR else np.array([])
    used=[p for p in per if p[1]>=25]; pos=sum(1 for p in used if p[2]>0)
    pooled=float(R.mean()) if len(R) else np.nan
    cells="  ".join(f"{t}:{a:+.3f}(n{n})" if n>=25 else f"{t}:n{n}" for t,n,a in per)
    sl_med=None
    verd="SURVIVOR" if (len(used)>=3 and pos==len(used) and pooled>0) else "ELIM"
    print(f"[{verd:8s}] {evcol}->{'L' if side>0 else 'S'} stop={stopcol} rr{rr} | poolN={len(R)} poolR={pooled:+.3f} pos={pos}/{len(used)} | {cells}")
    return verd,pooled

if __name__=="__main__":
    print("RANGE Phase-5 tradeability (ratified sb, STRESS, structural range-boundary stop, cross-era).")
    D=load()
    test(D,"E_BO_up",1,"bup")   # accepted upside escape, stop = broken (upper) boundary
    test(D,"E_BO_up",1,"blo")   # accepted upside escape, stop = far (lower) boundary
    test(D,"E_BO_dn",-1,"blo")  # accepted downside escape, stop = broken (lower) boundary
    test(D,"E_BO_dn",-1,"bup")  # accepted downside escape, stop = far (upper) boundary

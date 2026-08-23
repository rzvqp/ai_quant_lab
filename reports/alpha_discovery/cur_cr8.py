"""cur_cr8.py — FRONTIER CR-8 (current-regime, info-first): the ONE preregistered CONJUNCTION of the two independent
evidence-motivated ordering conditions found so far:
  (A) macro session  = hour in [12,16) UTC          (CR-6: robust P(downFirst)=0.541)
  (B) fresh episode  = current-like age < 1 day      (CR-7: robust P(downFirst)=0.522, monotone in freshness)
Both independently shift down-first ordering the same way but each is too weak alone (cost-fragile). Distinct conjunctive
identity: 'down-continuation is most ordered in the FRESH phase of a correction DURING the macro session'. This is NOT a
grid search — exactly one preregistered conjunction, tested once, with a bar SET BEFORE SCORING:
    proceed to a tradeable test ONLY IF conjunction P(downFirst) >= 0.56 overall AND > 0.53 in every partition.
Else: definitive bound, no further fishing. INFO-FIRST (no P&L). Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD
from cur_screen import like_at
from cur_cr2 import fwd
from cur_cr7 import episode_age_days

def main():
    m=CD.load_m15(); up,dn,af=fwd(m)
    t=m["time"].to_numpy().astype("float64"); cl=like_at(t); yr=m["dt"].dt.year.to_numpy()
    hr=m["dt"].dt.hour.to_numpy(); age=episode_age_days(t,cl)
    ok=np.isfinite(up)&np.isfinite(dn)
    A=(hr>=12)&(hr<16); B=np.isfinite(age)&(age<1.0)
    conj=cl&ok&A&B
    def row(msk):
        n=int(msk.sum())
        if n<150: return f"n={n}(thin)", None
        afr=af[msk]; pdf=float((afr[afr!=0]==-1).mean()) if (afr!=0).sum() else float('nan')
        return f"n={n:6d} P(downFirst)={pdf:.3f} dn-up={np.median(dn[msk])-np.median(up[msk]):+.2f}", pdf
    print("FRONTIER CR-8: CONJUNCTION macro-session[12-16) x fresh-episode(age<1d) in current-like -> ordering.")
    s0,_=row(cl&ok);           print("  [current-like baseline]:", s0)
    sa,_=row(cl&ok&A);         print("  [session A only]       :", sa)
    sb_,_=row(cl&ok&B);        print("  [fresh B only]         :", sb_)
    sc,pc=row(conj);           print("  [CONJUNCTION A&B]      :", sc)
    parts=[]
    for plab,ym in [("DISC",yr<=2021),("CONF",(yr>=2022)&(yr<=2024)),("OOS",yr>=2025)]:
        ss,pp=row(conj&ym); parts.append((plab,pp)); print(f"    {plab}: {ss}")
    ps=[pp for _,pp in parts if pp is not None]
    passgate = pc is not None and pc>=0.56 and len(ps)==3 and all(p>0.53 for p in ps)
    print(f"\n  PREREGISTERED BAR (>=0.56 overall AND >0.53 every partition): {'PASS -> proceed to tradeable test' if passgate else 'FAIL -> definitive bound, ordering too weak, NO tradeable test'}")

if __name__=="__main__":
    main()

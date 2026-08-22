"""RANGE §6/§9/§10 diagnostics + niche search on the least-fragile coarse candidates.
Range-width economics; entry-location concentration; width/quality filters; CALIB; temporal.
Question: does ANY filtered niche yield a robust (non-tail-fragile, CALIB-positive) RANGE edge?"""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import range_m5 as R
PIP=R.PIP

# ---- §9 range-width economics (whole DEV H1 range population) ----
wid_dev = R.width[R.in_range & R.h1dev]/PIP
wid_dev = wid_dev[np.isfinite(wid_dev)]
print("=== §9 RANGE-WIDTH ECONOMICS (DEV H1 ranges) ===")
print(f"  n_range_bars={len(wid_dev)} median={np.median(wid_dev):.0f}p P25={np.percentile(wid_dev,25):.0f} P75={np.percentile(wid_dev,75):.0f}")
print(f"  %>=80={np.mean(wid_dev>=80):.2f} %>=100={np.mean(wid_dev>=100):.2f} %>=150={np.mean(wid_dev>=150):.2f} %>=200={np.mean(wid_dev>=200):.2f}")

def arm(fn,long,m5,tp,coarse=True,split="dev"):
    res=R.run(fn,long,m5,tp,split); return res["A"] if coarse else res["B"]
def stats(tr, dev=True):
    r=[x for x in tr if (x["is_dev"] if dev else x["is_cal"])]
    if not r: return dict(n=0)
    Rv=np.array([x["R"] for x in r]); n=len(Rv); Rs=np.sort(Rv)[::-1]
    return dict(n=n, WR=round(float(np.mean([x["win"] for x in r])),3), avg=round(float(Rv.mean()),4),
                best5=round(float(Rs[max(1,int(n*.05)):].mean()),4), best10=round(float(Rs[max(1,int(n*.1)):].mean()),4))
def filt(tr, wmin=None, locmax=None, ntmin=None):
    out=[]
    for x in tr:
        if wmin is not None and x["width"]/PIP < wmin: continue
        if locmax is not None and x["loc"] > locmax: continue
        if ntmin is not None and x["ntest"] < ntmin: continue
        out.append(x)
    return out

CANDS=[("exhaust-S-mid",R.sig_exhaustion,False,"mom","mid"),
       ("exhaust-L-mid",R.sig_exhaustion,True,"mom","mid"),
       ("exhaust-L-opp",R.sig_exhaustion,True,"mom","opp"),
       ("failbreak-L-opp",R.sig_failbreak,True,"mom","opp")]
for name,fn,long,m5,tp in CANDS:
    A=arm(fn,long,m5,tp,coarse=True,split="dev"); Ac=arm(fn,long,m5,tp,coarse=True,split="cal")
    base=stats(A); baseC=stats(Ac,dev=False)
    print(f"\n=== {name} (coarse) ===  base: {base} | CALIB {baseC}")
    # entry-location concentration (§6)
    dev=[x for x in A if x["is_dev"]]; loc=np.array([x["loc"] for x in dev]); Rv=np.array([x["R"] for x in dev])
    for t in (0.10,0.20,0.25):
        m=loc<=t; print(f"   entry within {int(t*100)}% of boundary: n={int(m.sum())} avgR={Rv[m].mean():.3f} | beyond: n={int((~m).sum())} avgR={Rv[~m].mean():.3f}")
    # width filter (§9/§10)
    for wmin in (100,150):
        f=stats(filt(A,wmin=wmin)); fC=stats(filt(Ac,wmin=wmin),dev=False)
        print(f"   width>={wmin}p: DEV {f} | CALIB {fC}")
    # temporal
    yr={}
    for x in dev: yr.setdefault(pd.to_datetime(x['t'],unit='s',utc=True).year,[]).append(x['R'])
    print(f"   temporal={ {int(y):round(float(np.mean(v)),3) for y,v in sorted(yr.items())} }")

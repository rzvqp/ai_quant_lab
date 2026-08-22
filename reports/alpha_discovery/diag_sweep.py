"""S5/S23/S24 DIAGNOSTICS (DEV-only, outcome used for DIAGNOSIS not signal): what distinguishes sweeps
that precede a bearish departure from those that continue bullish? Large-bearish-move catalog. H1 vs H4."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import liquidity_sweep_short as Q
PIP=Q.PIP
def diag(tf, HOR=12):
    o,h,l,c,atr,e20,e50,eff,dev,yr=Q.arrs(tf); n=len(o)
    rows=[]
    for ev in Q.sweeps(tf):
        i=ev['i']; lvl=ev['lvl']; ei=i+1
        if ei>=n-HOR-1: continue
        # forward excursions from next open (causal outcome for DIAGNOSIS only)
        entry=o[ei]; fh=h[ei:ei+HOR]; fl=l[ei:ei+HOR]
        bear=(entry-fl.min())/PIP; bull=(fh.max()-entry)/PIP
        # pre-entry causal features (known at sweep bar i)
        close_below = c[i]<lvl
        disp = any((o[j]-c[j])>1.0*atr[j] and c[j]<o[j] for j in range(i,min(i+4,n)))
        prelow=min(l[max(0,ev['k']):i]) if i>ev['k'] else l[i]
        sbreak = any(c[j]<prelow for j in range(i,min(i+5,n)))
        sweep_mag=(h[i]-lvl)/PIP  # excursion above level on breach bar
        bars_above=0
        for j in range(i,min(i+HOR,n)):
            if c[j]>lvl: bars_above+=1
            else: break
        # regime at sweep
        reg = "TREND_UP" if (e20[i]>e50[i] and eff[i]==eff[i] and eff[i]>0.30) else ("TREND_DOWN" if (e20[i]<e50[i] and eff[i]<-0.30) else "OTHER")
        rows.append(dict(bear=bear,bull=bull,close_below=close_below,disp=disp,sbreak=sbreak,sweep_mag=sweep_mag,bars_above=bars_above,reg=reg,is_bear=(bear>=100 and bear>bull)))
    R=rows; nb=sum(r['is_bear'] for r in R)
    print(f"\n=== {tf} SWEEP OUTCOME DIAGNOSTIC (n={len(R)}, forward {HOR} bars) ===")
    print(f"  bearish-departure (>=100p down & down>up): {nb} ({nb/len(R)*100:.0f}%) | bullish-continue: {len(R)-nb} ({(len(R)-nb)/len(R)*100:.0f}%)")
    print(f"  median forward bear excursion={np.median([r['bear'] for r in R]):.0f}p | median bull excursion={np.median([r['bull'] for r in R]):.0f}p")
    print(f"  large-move catalog: %sweeps with bear>= 100/150/200/300 p = "
          + "/".join(f"{np.mean([r['bear']>=x for r in R])*100:.0f}" for x in (100,150,200,300)))
    # feature discrimination: bearish vs bullish group
    bearG=[r for r in R if r['is_bear']]; bullG=[r for r in R if not r['is_bear']]
    def rate(g,key): return np.mean([g_[key] for g_ in g]) if g else 0
    print(f"  FEATURE DISCRIMINATION (bearish grp vs bullish grp):")
    for k in ("close_below","disp","sbreak"):
        print(f"    {k}: bearish={rate(bearG,k)*100:.0f}%  bullish={rate(bullG,k)*100:.0f}%  lift={rate(bearG,k)*100-rate(bullG,k)*100:+.0f}pp")
    print(f"    sweep_mag(pips): bearish med={np.median([r['sweep_mag'] for r in bearG]):.0f}  bullish med={np.median([r['sweep_mag'] for r in bullG]):.0f}")
    print(f"    bars_above_level: bearish med={np.median([r['bars_above'] for r in bearG]):.1f}  bullish med={np.median([r['bars_above'] for r in bullG]):.1f}")
    # regime of bearish sweeps (S10/S11: do they happen in TREND_UP?)
    from collections import Counter
    print(f"    regime@sweep of BEARISH sweeps: {dict(Counter(r['reg'] for r in bearG))}")
    return R
for tf in ("H4","H1"): diag(tf)

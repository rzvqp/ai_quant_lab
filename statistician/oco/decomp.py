import sys, math; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from rep import S,PDH,PDL,Hi,Lo,Cl,O,TS,YR,N,H,COST,episode,run,stats,d,HOLDOUT
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def cl_mean(y, cl):
    mu=y.mean(); n=len(y)
    g=pd.DataFrame({'c':cl,'y':y}).groupby('c')['y'].agg(['sum','count'])
    G=len(g); resid=g['sum'].to_numpy()-g['count'].to_numpy()*mu
    return mu, math.sqrt((resid**2).sum()/n**2*(G/(G-1))), G

print("="*122); print("  §9 DECISIVE -- IS THE 'MARKET SELECTS DIRECTION' CLAIM DOING THE WORK?"); print("="*122)
for m in (1.0,1.5,2.0):
    ST=stats(run(m),"",quiet=True); tr=ST["tr"]; net=ST["net"]; ii=ST["ii"]
    side=np.array([r["side"] for r in tr]); ts=TS[S[ii]]
    wk=(pd.to_datetime(ts,unit='s',utc=True).isocalendar().year*100+
        pd.to_datetime(ts,unit='s',utc=True).isocalendar().week).to_numpy()
    L=side>0; Sh=side<0
    muL,seL,_=cl_mean(net[L],wk[L]); muS,seS,_=cl_mean(net[Sh],wk[Sh]); mu,se,_=cl_mean(net,wk)
    print(f"\n  target {m}R   overall {mu:+.4f} (t {mu/se:+.2f})")
    print(f"    market selected LONG  : n={L.sum():5d} ({L.mean():.1%})  net {muL:+.4f}  t {muL/seL:+.2f}  WR {(net[L]>0).mean():.3f}")
    print(f"    market selected SHORT : n={Sh.sum():5d} ({Sh.mean():.1%})  net {muS:+.4f}  t {muS/seS:+.2f}  WR {(net[Sh]>0).mean():.3f}")
    print(f"    LONG minus SHORT      : {muL-muS:+.4f} R")

print("\n" + "="*122)
print("  SAME-EPISODE matched control: on EVERY episode the candidate traded, what would ALWAYS-LONG have paid?")
print("  (long entry at the prior-day HIGH whenever it was touched inside the same 24h window)")
print("="*122)
ST=stats(run(2.0),"",quiet=True); tr=ST["tr"]; net=ST["net"]; ii=ST["ii"]
side=np.array([r["side"] for r in tr])
paired_c=[]; paired_l=[]
for pos,r in enumerate(tr):
    i=r["i"]; s=S[i]; ua,da=PDH[i],PDL[i]; risk=ua-da; end=min(s+H,N-1)
    j=None
    for k in range(s+1,end+1):
        if Hi[k]>=ua: j=k; break
    if j is None: continue
    entry=ua; stop=da; tgt=entry+2.0*risk; res=None
    for k in range(j,end+1):
        ht=Hi[k]>=tgt; hs=Lo[k]<=stop
        if ht and hs: res=-1.0; break
        if hs: res=-1.0; break
        if ht: res=2.0; break
    if res is None: res=(Cl[end]-entry)/risk
    paired_l.append(res-COST/risk); paired_c.append(net[pos])
paired_l=np.array(paired_l); paired_c=np.array(paired_c)
print(f"  paired episodes (candidate traded AND the prior-day high was touched): {len(paired_c)}")
print(f"    candidate (market-selected side) : {paired_c.mean():+.4f} R")
print(f"    ALWAYS-LONG on the same episodes : {paired_l.mean():+.4f} R")
print(f"    incremental value of MARKET SELECTION over ALWAYS-LONG : {paired_c.mean()-paired_l.mean():+.4f} R")

print("\n" + "="*122); print("  §7  WHERE DOES THE GROSS EDGE ACTUALLY COME FROM?  (exit-type attribution)"); print("="*122)
print(f"  {'target':<9}{'hit target':>12}{'hit stop':>11}{'24h expiry':>12}   {'contribution to GROSS expectancy (R)':>40}")
for m in (1.0,1.5,2.0):
    ST=stats(run(m),"",quiet=True); tr=ST["tr"]; gr=ST["gross"]
    won=np.isclose(gr,m); lost=np.isclose(gr,-1.0); mtm=~(won|lost)
    cw=won.mean()*m; cl_=lost.mean()*(-1.0); cm=gr[mtm].sum()/len(gr)
    print(f"  {m}R{'':<6}{won.mean():>11.1%}{lost.mean():>11.1%}{mtm.mean():>12.1%}   "
          f"target {cw:+.4f}  stop {cl_:+.4f}  expiry {cm:+.4f}   = {cw+cl_+cm:+.4f}")
print("\n  -> target and stop nearly CANCEL at every payoff. The whole gross edge sits in the")
print("     episodes that are still open at the 24h horizon and get marked to market.")

print("\n" + "="*122); print("  HOLDOUT-CLEAN RESTATEMENT (all headline numbers, protected data removed)"); print("="*122)
print(f"  {'target':<9}{'N':>7}{'net (as Alpha ran it)':>24}{'net EXCLUDING holdout':>24}{'delta':>10}")
for m in (1.0,1.5,2.0):
    ST=stats(run(m),"",quiet=True); net_=ST["net"]; ii_=ST["ii"]; ts=TS[S[ii_]]
    keep=ts < HOLDOUT.timestamp()
    print(f"  {m}R{'':<6}{len(net_):>7}{net_.mean():>+24.4f}{net_[keep].mean():>+24.4f}{net_[keep].mean()-net_.mean():>+10.4f}")
ts=TS[S[ii]]; keep=ts<HOLDOUT.timestamp()
wk=(pd.to_datetime(ts,unit='s',utc=True).isocalendar().year*100+
    pd.to_datetime(ts,unit='s',utc=True).isocalendar().week).to_numpy()
mu,se,G=cl_mean(net[keep],wk[keep])
print(f"\n  2R holdout-clean: mean {mu:+.4f}  week-clustered se {se:.4f}  t {mu/se:+.2f}  "
      f"CI95 [{mu-1.96*se:+.4f}, {mu+1.96*se:+.4f}]  (n={int(keep.sum())})")
stress=stats(run(2.0,cost=0.838),"",quiet=True)
ii2=stress["ii"]; ts2=TS[S[ii2]]; k2=ts2<HOLDOUT.timestamp()
print(f"  2R holdout-clean at STRESS cost (2x): {stress['net'][k2].mean():+.4f} R")

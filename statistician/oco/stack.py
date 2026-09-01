import sys, math; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from rep import S,PDH,PDL,Hi,Lo,Cl,O,TS,YR,N,H,COST,run,stats,HOLDOUT
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
def cl_mean(y,cl):
    mu=y.mean(); n=len(y); g=pd.DataFrame({'c':cl,'y':y}).groupby('c')['y'].agg(['sum','count'])
    G=len(g); r=g['sum'].to_numpy()-g['count'].to_numpy()*mu
    return mu, math.sqrt((r**2).sum()/n**2*(G/(G-1)))
def variant(mult=2.0, cost=COST, fill_open=False, holdout_clean=False):
    out=[];idx=[]
    for i in range(len(S)):
        s,ua,da=S[i],PDH[i],PDL[i]; risk=ua-da; end=min(s+H,N-1); trig=None
        if holdout_clean and TS[s]>=HOLDOUT.timestamp(): continue
        for j in range(s+1,end+1):
            up=Hi[j]>=ua; dn=Lo[j]<=da
            if up and dn: trig="skip"; break
            if up: trig=(j,+1,max(ua,O[j]) if fill_open else ua); break
            if dn: trig=(j,-1,min(da,O[j]) if fill_open else da); break
        if trig is None or trig=="skip": continue
        j,dr,entry=trig; stop=da if dr>0 else ua; tgt=entry+dr*mult*risk; res=None
        for k in range(j,end+1):
            ht=(Hi[k]>=tgt) if dr>0 else (Lo[k]<=tgt); hs=(Lo[k]<=stop) if dr>0 else (Hi[k]>=stop)
            if ht and hs: res=-abs(entry-stop)/risk; break
            if hs: res=-abs(entry-stop)/risk; break
            if ht: res=float(mult); break
        if res is None: res=dr*(Cl[end]-entry)/risk
        out.append(res-cost/risk); idx.append(i)
    y=np.array(out); ts=TS[S[np.array(idx)]]
    wk=(pd.to_datetime(ts,unit='s',utc=True).isocalendar().year*100+
        pd.to_datetime(ts,unit='s',utc=True).isocalendar().week).to_numpy()
    mu,se=cl_mean(y,wk); return y,mu,se
print("="*118); print("  STACKED REALISM -- 2R target, each governed correction applied cumulatively"); print("="*118)
print(f"  {'variant':<62}{'N':>7}{'net R':>10}{'week-t':>9}{'CI95':>24}")
rows=[("as Alpha ran it (BASE cost, fill at level, holdout consumed)", dict()),
      ("+ research holdout removed", dict(holdout_clean=True)),
      ("+ gap-through fills at the bar OPEN (realistic stop fill)", dict(holdout_clean=True, fill_open=True)),
      ("+ STRESS cost (2x governed)", dict(holdout_clean=True, fill_open=True, cost=0.838))]
for lbl,kw in rows:
    y,mu,se=variant(**kw)
    print(f"  {lbl:<62}{len(y):>7}{mu:>+10.4f}{mu/se:>+9.2f}   [{mu-1.96*se:+.4f}, {mu+1.96*se:+.4f}]")
print()
y,mu,se=variant(holdout_clean=True, fill_open=True)
rk=np.array([PDH[i]-PDL[i] for i in range(len(S))])
g,_,_=variant(holdout_clean=True, fill_open=True, cost=0.0)
gross=g[0].mean() if isinstance(g,tuple) else g.mean()
yg,mg,_=variant(holdout_clean=True, fill_open=True, cost=0.0)
inv=[]
for i in range(len(S)):
    if TS[S[i]]>=HOLDOUT.timestamp(): continue
    inv.append(1.0/(PDH[i]-PDL[i]))
print(f"  holdout-clean + realistic fill: GROSS {mg:+.4f} R")
print(f"  BREAK_EVEN_COST = {mg/np.mean(inv):.3f} price units ({mg/np.mean(inv)/0.419:.2f}x BASE, {mg/np.mean(inv)/0.838:.2f}x STRESS)")
print(f"  extra adverse execution that erases it: {mg/np.mean(inv)-0.419:.3f} USD = {(mg/np.mean(inv)-0.419)/0.10:.1f} pips/trade")

import numpy as np, pandas as pd
import alpha_lab as A, families as F, campaign as C
A.add_features=F.add_features; A.signal_series=F.signal_series; A.backtest=F.backtest; A.neighbors=F.neighbors; A.mc_pvalue=F.mc_pvalue
def ou(n,k,seed,sig=6.0,base=4000.):
    rng=np.random.default_rng(seed); x=np.zeros(n); x[0]=base
    for t in range(1,n): x[t]=x[t-1]+k*(base-x[t-1])+rng.normal(0,sig)
    op=np.concatenate([[base],x[:-1]]); r2=np.random.default_rng(seed+9); w=np.abs(r2.normal(0,sig,n))
    return pd.DataFrame(dict(time=np.arange(n)*86400,open=op,high=np.maximum(op,x)+w,low=np.minimum(op,x)-w,close=x,volume=100.,ntrades=100))
def rw(n,seed,base=4000.):
    rng=np.random.default_rng(seed); x=base*np.exp(np.cumsum(rng.normal(0,0.01,n)))
    op=np.concatenate([[base],x[:-1]]); w=np.abs(rng.normal(0,0.01,n))*x
    return pd.DataFrame(dict(time=np.arange(n)*86400,open=op,high=np.maximum(op,x)+w,low=np.minimum(op,x)-w,close=x,volume=100.,ntrades=100))
# grammar subset (mean-reversion-type) to bound compute
mr=[h for h in F.generate(None) if h['entry'] in ('meanrev','distance') and h['trail']=='none' and h['dow']=='any'][:400]
A.generate=lambda: mr
F._POOL.clear()
datasets={'STRONG_OU':ou(2000,0.10,1),'NOISE_1':rw(2000,2),'NOISE_2':rw(2000,3)}
cands,kpi,prep,vault=C.run_campaign(datasets,"CONTROL")
print("KPI:",kpi)
print(f"CANDIDATES (passed Statistician+globalFDR+walkforward+RedTeam): {len(cands)}")
byinst={}
for c in cands: byinst[c['inst']]=byinst.get(c['inst'],0)+1
print("candidates by instrument:",byinst)
print("holdout opened during run (must be 0):",len(vault.opened))
# show a couple candidate stats
for c in cands[:3]:
    d,r,v,hd=prep[c['inst']]; st=C.full_stats(F.backtest(r,c['h'],C.CFG))
    print(f"  {c['inst']} {c['h']['entry']}/{c['h']['direction']} p={c['p']:.2e} exp={st['expectancy_R']:.3f} pf={st['profit_factor']:.2f} n={st['n']} wf={c.get('walk_forward')} rt={c.get('redteam_pass')}")
print("\nVALIDATION:",
      "PASS" if (byinst.get('STRONG_OU',0)>=1 and byinst.get('NOISE_1',0)==0 and byinst.get('NOISE_2',0)==0 and len(vault.opened)==0) else "CHECK")

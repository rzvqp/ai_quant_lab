import numpy as np, pandas as pd
import alpha_lab as A, families as F
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
A.generate=lambda: [h for h in F.generate(None) if h['entry'] in ('meanrev','distance','range_pos')]
F._POOL.clear(); pos=A.run_pipeline(ou(1600,0.02,1),"POWER-OU",touch_holdout=True,verbose=True)
print("POS ALPHA:", sum(c['holdout_ok'] for c in pos['candidates']))
F._POOL.clear(); neg=A.run_pipeline(rw(1600,2),"NEG-RW",touch_holdout=True,verbose=False)
print("NEG ALPHA:", sum(c['holdout_ok'] for c in neg['candidates']),"(expect 0)")

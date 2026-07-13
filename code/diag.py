import numpy as np, pandas as pd
import alpha_lab as A, families as F
A.add_features=F.add_features; A.signal_series=F.signal_series; A.backtest=F.backtest; A.neighbors=F.neighbors; A.mc_pvalue=F.mc_pvalue
def ou(n,k,seed,sig=6.0,base=4000.):
    rng=np.random.default_rng(seed); x=np.zeros(n); x[0]=base
    for t in range(1,n): x[t]=x[t-1]+k*(base-x[t-1])+rng.normal(0,sig)
    op=np.concatenate([[base],x[:-1]]); r2=np.random.default_rng(seed+9); w=np.abs(r2.normal(0,sig,n))
    return pd.DataFrame(dict(time=np.arange(n)*86400,open=op,high=np.maximum(op,x)+w,low=np.minimum(op,x)-w,close=x,volume=100.,ntrades=100))
for kappa in (0.04,0.06,0.10):
    A.generate=lambda: [h for h in F.generate(None) if h['entry']=='meanrev']
    F._POOL.clear(); r=A.run_pipeline(ou(1600,kappa,1),f"OU k={kappa}",touch_holdout=True,verbose=False)
    # min p among stat survivors
    print(f"kappa={kappa}: hyp={r['n_hyp']} stat={r.get('n_stat')} FDR={r.get('n_fdr')} RT={r.get('n_rt')} ALPHA={sum(c['holdout_ok'] for c in r['candidates'])}")

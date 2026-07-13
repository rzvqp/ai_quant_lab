import numpy as np, pandas as pd
import alpha_lab as A, families as F
A.add_features=F.add_features; A.signal_series=F.signal_series; A.backtest=F.backtest; A.neighbors=F.neighbors
A.mc_pvalue=lambda d,h,e,cfg: F.mc_pvalue(d,h,e,cfg,B=2000)
def ou(n,k,seed,sig=6.0,base=4000.):
    rng=np.random.default_rng(seed); x=np.zeros(n); x[0]=base
    for t in range(1,n): x[t]=x[t-1]+k*(base-x[t-1])+rng.normal(0,sig)
    op=np.concatenate([[base],x[:-1]]); r2=np.random.default_rng(seed+9); w=np.abs(r2.normal(0,sig,n))
    return pd.DataFrame(dict(time=np.arange(n)*86400,open=op,high=np.maximum(op,x)+w,low=np.minimum(op,x)-w,close=x,volume=100.,ntrades=100))
d=F.add_features(ou(1600,0.08,1)); dr,dv,dh=A.splits(d)
mh=[h for h in F.generate(None) if h['entry']=='meanrev' and h['timeout']==10 and h['trail']=='none' and h['dow']=='any'][:300]
F._POOL.clear()
res=[]
for h in mh:
    v=A.statistician(dr,dv,h)
    if v['passed']: res.append((h,v['p'],v['m']['exp'],v['mv']['exp']))
res.sort(key=lambda r:r[1])
print(f"meanrev hyps tested={len(mh)}  stat-passed={len(res)}")
print("top survivors by p:")
for h,p,e,ev in res[:8]:
    print(f"  p={p:.5f} res_exp={e:.3f} val_exp={ev:.3f} vol={h['vol_regime']} trend={h['trend']} z={h['z_thresh']} sl={h['sl_atr']} tp={h['tp_r']}")
ps=[r[1] for r in res]; import numpy as np
if ps:
    keep=A.bh_fdr(np.array(ps),0.10); print(f"min p={min(ps):.5f}  FDR-pass={int(keep.sum())}  (m={len(ps)}, BH top-threshold={0.1/len(ps):.5f})")

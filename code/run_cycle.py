import numpy as np, pandas as pd, sys, time
import alpha_lab as A

def synth_bars(n, phi, seed, vol=0.0015, base=4000.0):
    """AR(1) returns (phi>0 = momentum edge). Build OHLC with intrabar range."""
    rng=np.random.default_rng(seed)
    r=np.zeros(n); e=rng.normal(0,vol,n)
    for t in range(1,n): r[t]=phi*r[t-1]+e[t]
    close=base*np.exp(np.cumsum(r))
    openp=np.concatenate([[base],close[:-1]])
    rng2=np.random.default_rng(seed+99)
    wick=np.abs(rng2.normal(0,vol,n))*close
    high=np.maximum(openp,close)+wick
    low =np.minimum(openp,close)-wick
    vol_=rng2.integers(50,500,n).astype(float)
    return pd.DataFrame(dict(open=openp,high=high,low=low,close=close,volume=vol_,ntrades=vol_))

def ou_bars(n, kappa, seed, sigma=6.0, base=4000.0):
    """Ornstein-Uhlenbeck mean-reverting price -> genuine TIMING edge for mean-reversion
    that random entries cannot capture (no drift)."""
    rng=np.random.default_rng(seed)
    x=np.zeros(n); x[0]=base
    for t in range(1,n): x[t]=x[t-1]+kappa*(base-x[t-1])+rng.normal(0,sigma)
    close=x; openp=np.concatenate([[base],close[:-1]])
    rng2=np.random.default_rng(seed+99); wick=np.abs(rng2.normal(0,sigma,n))
    high=np.maximum(openp,close)+wick; low=np.minimum(openp,close)-wick
    v=rng2.integers(50,500,n).astype(float)
    return pd.DataFrame(dict(open=openp,high=high,low=low,close=close,volume=v,ntrades=v))

def summarize(res):
    nc=sum(c['holdout_ok'] for c in res['candidates'])
    print(f"  >>> {res['label']}: hyps={res['n_hyp']} statPass={res.get('n_stat',0)} "
          f"FDR={res.get('n_fdr',0)} RedTeam={res.get('n_rt',0)} ALPHA={nc}")
    return nc

if __name__=="__main__":
    t0=time.time()
    print("############ SELF-TEST: POSITIVE CONTROL (OU mean-reversion timing edge) ############")
    pos=A.run_pipeline(ou_bars(1600,0.02,seed=1), "POS-CONTROL", touch_holdout=True)
    print("\n############ SELF-TEST: NEGATIVE CONTROL (random walk, phi=0.0) ############")
    neg=A.run_pipeline(synth_bars(1600,0.0,seed=2), "NEG-CONTROL", touch_holdout=True)
    print("\n############ FIRST REAL ALPHA-DISCOVERY CYCLE: GC 15m ############")
    gc=pd.read_csv(r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\344b31d3-785f-43a4-b73b-d80a24bc18df\scratchpad\phaseb\alpha\gc_15m.csv")
    real=A.run_pipeline(gc[['open','high','low','close','volume','ntrades']], "GC-15m", touch_holdout=True)

    print("\n############ SUMMARY ############")
    npos=summarize(pos); nneg=summarize(neg); nreal=summarize(real)
    print("\nCONTROL CHECK:")
    print(f"  positive control found alpha: {'PASS' if npos>=1 else 'FAIL'} (expect >=1)")
    print(f"  negative control clean:       {'PASS' if nneg==0 else 'FAIL'} (expect 0)")
    print(f"  pipeline valid: {'YES' if (npos>=1 and nneg==0) else 'NO'}")
    print(f"elapsed {time.time()-t0:.1f}s")

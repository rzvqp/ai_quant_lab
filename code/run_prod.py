import numpy as np, pandas as pd, glob, os, time, sys
import alpha_lab as A
import families as F

# ---- monkeypatch grammar extension onto FROZEN pipeline (gates unchanged) ----
A.add_features=F.add_features; A.signal_series=F.signal_series
A.backtest=F.backtest; A.neighbors=F.neighbors; A.mc_pvalue=F.mc_pvalue
BUDGET=int(sys.argv[1]) if len(sys.argv)>1 else 1700; SEED=7
RUN_CONTROLS=(len(sys.argv)<=2)
A.generate=lambda: F.generate(BUDGET, SEED)

DATADIR=r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\344b31d3-785f-43a4-b73b-d80a24bc18df\scratchpad\phaseb\alpha\data"

def ou(n,k,seed,sig=6.0,base=4000.):
    rng=np.random.default_rng(seed); x=np.zeros(n); x[0]=base
    for t in range(1,n): x[t]=x[t-1]+k*(base-x[t-1])+rng.normal(0,sig)
    op=np.concatenate([[base],x[:-1]]); r2=np.random.default_rng(seed+9); w=np.abs(r2.normal(0,sig,n))
    return pd.DataFrame(dict(time=np.arange(n)*86400,open=op,high=np.maximum(op,x)+w,low=np.minimum(op,x)-w,close=x,volume=r2.integers(50,500,n).astype(float),ntrades=100))
def rw(n,seed,base=4000.):
    rng=np.random.default_rng(seed); x=base*np.exp(np.cumsum(rng.normal(0,0.01,n)))
    op=np.concatenate([[base],x[:-1]]); w=np.abs(rng.normal(0,0.01,n))*x
    return pd.DataFrame(dict(time=np.arange(n)*86400,open=op,high=np.maximum(op,x)+w,low=np.minimum(op,x)-w,close=x,volume=100.,ntrades=100))

if __name__=="__main__":
    t0=time.time()
    full=F.generate(None); print(f"Full grammar size (unique canonical, per symbol): {len(full)}")
    print(f"Sampled budget/symbol: {BUDGET}  (balanced across {len(F.FAMILIES)} families)")

    if RUN_CONTROLS:
        print("\n===== CONTROL RE-VALIDATION (extended grammar, strong planted edge) =====")
        mr=[h for h in F.generate(None) if h['entry'] in ('meanrev','distance') and h['trail']=='none'][:600]
        A.generate=lambda: mr
        F._POOL.clear(); pos=A.run_pipeline(ou(1600,0.08,1),"POS",touch_holdout=True,verbose=False)
        F._POOL.clear(); neg=A.run_pipeline(rw(1600,2),"NEG",touch_holdout=True,verbose=False)
        npos=sum(c['holdout_ok'] for c in pos['candidates']); nneg=sum(c['holdout_ok'] for c in neg['candidates'])
        print(f"POS alpha={npos} (expect>=1) | NEG alpha={nneg} (expect 0) | VALID={'YES' if npos>=1 and nneg==0 else 'NO'}")
    A.generate=lambda: F.generate(BUDGET,SEED)

    print("\n===== PRODUCTION BATCH #1 : 6 daily symbols x %d =====" % BUDGET)
    files=sorted(glob.glob(DATADIR+r"\*.csv"))
    agg=dict(hyp=0,stat=0,fdr=0,rt=0,alpha=0,deaths={}); per_fam_pass={f:0 for f in F.FAMILIES}; per_fam_tot={f:0 for f in F.FAMILIES}
    alpha_list=[]
    for fp in files:
        sym=os.path.basename(fp).replace('.csv','')
        df=pd.read_csv(fp)
        if len(df)<300: print(f"[{sym}] SKIP (bars={len(df)})"); continue
        F._POOL.clear()
        res=A.run_pipeline(df[['time','open','high','low','close','volume']].assign(ntrades=100),sym,touch_holdout=True,verbose=False)
        na=sum(c['holdout_ok'] for c in res['candidates'])
        agg['hyp']+=res['n_hyp']; agg['stat']+=res.get('n_stat',0); agg['fdr']+=res.get('n_fdr',0)
        agg['rt']+=res.get('n_rt',0); agg['alpha']+=na
        for k,v in res['stage_deaths'].items(): agg['deaths'][k]=agg['deaths'].get(k,0)+v
        # family survival tallies (which families reach stat pass)
        for h in F.generate(BUDGET,SEED): per_fam_tot[h['entry']]+=1
        for c in res['candidates']:
            if c['holdout_ok']: alpha_list.append((sym,c))
        print(f"[{sym}] bars={len(df)} hyp={res['n_hyp']} statPass={res.get('n_stat',0)} "
              f"FDR={res.get('n_fdr',0)} RedTeam={res.get('n_rt',0)} ALPHA={na}")

    dt=time.time()-t0
    print("\n===== KPI REPORT (BATCH #1) =====")
    print(f"Hypotheses backtested (sum over symbols): {agg['hyp']}")
    print(f"Deaths by gate: {dict(sorted(agg['deaths'].items(),key=lambda x:-x[1]))}")
    print(f"Passed Statistician: {agg['stat']}  Passed FDR: {agg['fdr']}  Passed RedTeam: {agg['rt']}  ALPHA CANDIDATES: {agg['alpha']}")
    print(f"Throughput: {agg['hyp']/dt*3600:,.0f} hyp/hour  (elapsed {dt:.1f}s)")
    if alpha_list:
        print("ALPHA CANDIDATES (survived full battery incl. holdout):")
        for sym,c in alpha_list:
            print(f"  {sym} {c['h']['entry']}/{c['h']['direction']} vol={c['h']['vol_regime']} trend={c['h']['trend']} "
                  f"sl={c['h']['sl_atr']} tp={c['h']['tp_r']} trail={c['h'].get('trail')} | "
                  f"res exp={c['research']['exp']:.3f} pf={c['research']['pf']:.2f} n={c['research']['n']} | "
                  f"val exp={c['val']['exp']:.3f} | p={c['p']:.3f} | holdout exp={c['holdout']['exp']:.3f} n={c['holdout']['n']}")
    else:
        print("ALPHA CANDIDATES: 0  (all hypotheses eliminated — expected falsification-first outcome)")

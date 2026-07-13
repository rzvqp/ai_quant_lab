"""MTF Alpha Discovery campaign (XAUUSD). FROZEN stats: Statistician->global FDR->walk-forward
->Red Team. Holdout SEALED (not opened). Reports KPIs + S1,S2... . Batches via CLI budget."""
import numpy as np, pandas as pd, sys, time, math
import alpha_lab as A, mtf as M
from alpha_lab import bh_fdr
from campaign import full_stats

CFG=A.CFG; Q=CFG['FDR_Q']
MINTR=CFG['MINTR']; PF_MIN=CFG['PF_MIN']; DD_MAX=CFG['DD_MAX_R']

def metrics(tr):
    if len(tr)==0: return dict(n=0,exp=np.nan,pf=np.nan,dd=np.nan)
    R=tr['R'].values; eq=np.cumsum(R); dd=float(np.max(np.maximum.accumulate(eq)-eq))
    gp=R[R>0].sum(); gl=-R[R<0].sum()
    return dict(n=len(R),exp=float(R.mean()),pf=float(gp/gl) if gl>0 else np.inf,dd=dd)

def statistician(res,val,h):
    tr=M.backtest(res,h); m=metrics(tr)
    if m['n']<1 or np.isnan(m['exp']): return dict(p=1.0,stage='sanity',passed=False,m=m)
    if m['n']<MINTR: return dict(p=1.0,stage='min_trades',passed=False,m=m)
    if m['exp']<=0: return dict(p=1.0,stage='expectancy',passed=False,m=m)
    if m['pf']<PF_MIN: return dict(p=1.0,stage='profit_factor',passed=False,m=m)
    if m['dd']>DD_MAX: return dict(p=1.0,stage='max_dd',passed=False,m=m)
    nb=[metrics(M.backtest(res,hn))['exp'] for hn in M.neighbors(h)]; nb=[x for x in nb if not np.isnan(x)]
    if not nb or np.mean([x>0 for x in nb])<0.5: return dict(p=1.0,stage='param_stability',passed=False,m=m)
    mv=metrics(M.backtest(val,h))
    if mv['n']<5 or mv['exp']<=0: return dict(p=1.0,stage='oos',passed=False,m=m,mv=mv)
    p=M.analytic_p(res,h,m['exp'],m['n'])
    return dict(p=p,stage='stat_ok',passed=True,m=m,mv=mv)

def walk_forward(nonhold,h,K=4,need=3):
    n=len(nonhold); pos=used=0
    for i in range(K):
        seg=nonhold.iloc[int(n*i/K):int(n*(i+1)/K)]
        if len(seg)<200: continue
        mm=metrics(M.backtest(seg,h))
        if mm['n']>=5: used+=1; pos+=1 if mm['exp']>0 else 0
    return used>=2 and pos>=math.ceil(need*used/K)

def red_team(res,h):
    att={}
    c2=dict(CFG); c2['spread_ticks']*=3; c2['slip_ticks']*=3
    att['cost_stress_3x']= metrics(M.backtest(res,h,c2))['exp']>0
    tr=M.backtest(res,h); R=tr['R'].values
    if len(R)>=5:
        k=max(1,len(R)//5); best=max(np.sum(R[i:i+k]) for i in range(len(R)-k+1))
        att['no_cherry_block']= (R.sum()-best)/max(len(R)-k,1)>0
        mon=pd.to_datetime(res['time'].values[tr['ei'].astype(int).values],unit='s',utc=True).to_period('M')
        dfm=pd.DataFrame({'R':R,'m':mon}); g=dfm.groupby('m')['R'].agg(['mean','count']); g=g[g['count']>=3]
        att['monthly_consistency']= (g['mean']>0).mean()>=0.5 if len(g)>=3 else False
    else: att['no_cherry_block']=False; att['monthly_consistency']=False
    return all(att.values()),att

def sessions_perf(res,h):
    tr=M.backtest(res,h)
    if len(tr)==0: return {}
    sess=res['session'].values[tr['ei'].astype(int).values]
    return {s:round(float(tr['R'].values[sess==s].mean()),3) for s in set(sess) if (sess==s).sum()>=3}

def run_batch(m15,budget,seed,bn):
    n=len(m15); a=int(n*0.60); b=int(n*0.80)
    res=m15.iloc[:a].copy(); val=m15.iloc[a:b].copy(); hold=m15.iloc[b:].copy()  # HOLDOUT sealed (unused)
    nonhold=m15.iloc[:b].copy()
    hyps=M.generate(budget,seed); t0=time.time()
    reg=[]
    for h in hyps:
        v=statistician(res,val,h); v['h']=h; reg.append(v)
    N=len(reg); deaths={}
    for v in reg:
        if not v['passed']: deaths[v['stage']]=deaths.get(v['stage'],0)+1
    pvec=np.array([v['p'] for v in reg]); keep=bh_fdr(pvec,Q)
    fdr=[reg[i] for i in range(N) if keep[i] and reg[i]['passed']]
    wf=[v for v in fdr if walk_forward(nonhold,v['h'])]
    cands=[]
    for v in wf:
        ok,att=red_team(res,v['h'])
        if ok: v['att']=att; cands.append(v)
    dt=time.time()-t0
    print(f"\n===== BATCH #{bn} KPI (MTF XAUUSD, holdout SEALED) =====")
    print(f"hypotheses generated/tested: {N}")
    print(f"eliminated by gate: {dict(sorted(deaths.items(),key=lambda x:-x[1]))}")
    print(f"passed Statistician: {sum(v['passed'] for v in reg)} | global-FDR: {len(fdr)} | walk-forward: {len(wf)} | Red Team -> CANDIDATES: {len(cands)}")
    print(f"throughput: {N/dt*3600:,.0f} hyp/hour ({dt:.0f}s)")
    if not cands:
        print("S-list: (none) — 0 discovery candidates this batch (expected; campaign continues)")
    for i,v in enumerate(cands,1):
        h=v['h']; st=full_stats(M.backtest(res,h)); yrs={}
        r=res.copy(); tr=M.backtest(r,h)
        yy=pd.to_datetime(r['time'].values[tr['ei'].astype(int).values],unit='s',utc=True).year
        for Y in sorted(set(yy)): yrs[int(Y)]=round(float(tr['R'].values[yy==Y].mean()),3)
        print(f"\n  S{i}  [{h['id']}]  status=DISCOVERY CANDIDATE")
        print(f"    4H context: trend={h['c4h_trend']} vol={h['c4h_vol']}")
        print(f"    1H confirm: {h['conf_1h']}")
        print(f"    15M trigger: {h['trig']} lookback={h.get('lookback')} dir={h['direction']} session={h['session']}")
        print(f"    exits: SL={h['sl_atr']}xATR  TP={h['tp_r']}R  timeout={h['timeout']}bars  trail={h['trail']}")
        print(f"    n_trades={st['n']} win_rate={st['win_rate']:.3f} avgWin={st['avg_win_R']:.2f}R avgLoss={st['avg_loss_R']:.2f}R")
        print(f"    expectancy={st['expectancy_R']:.3f}R  PF={st['profit_factor']:.2f}  maxDD={st['max_dd_R']:.1f}R  longestLoss={st['longest_losing_streak']}")
        print(f"    per-year exp(R): {yrs}")
        print(f"    per-session exp(R): {sessions_perf(res,h)}")
        print(f"    walk-forward: PASS  Red Team: {v['att']}")
    return cands

if __name__=="__main__":
    budget=int(sys.argv[1]) if len(sys.argv)>1 else 10000
    seed=int(sys.argv[2]) if len(sys.argv)>2 else 101
    bn=sys.argv[3] if len(sys.argv)>3 else "1"
    print("loading MTF data (M15 + attached last-closed H4/H1/D1, lookahead-safe)...")
    m15=M.load_mtf()
    print(f"M15 bars={len(m15)}  full grammar size={len(M.generate(None))}  batch budget={budget}")
    run_batch(m15,budget,seed,bn)

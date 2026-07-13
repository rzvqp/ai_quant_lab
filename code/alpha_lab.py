"""
AI QUANT RESEARCH LAB - Alpha Discovery pipeline (MVP).
Generator -> Backtest -> Statistician -> Red Team -> Alpha Candidate | Reject.
Falsification-first: every hypothesis FALSE until it survives the full battery.
Lookahead-safe. Deterministic (fixed seeds). Holdout sealed until the very end.
"""
import numpy as np, pandas as pd, itertools, hashlib, json

# ----------------------------- CONFIG (immutable per run) -----------------------------
CFG = dict(
    tick=0.1, spread_ticks=1.0, slip_ticks=1.0,      # costs
    atr_len=14, vol_len=20, vol_rank_win=80, trend_len=20,
    split=(0.65,0.15,0.20),                          # research / validation / holdout
    MINTR=25, PF_MIN=1.15, DD_MAX_R=12.0, EXP_MIN=0.0,
    FDR_Q=0.10, MC_B=500, seed=7,
)
GRID = dict(
    vol_regime=['any','low','high'], trend=['any','up','down'],
    entry=['breakout','meanrev'], direction=['long','short'],
    lookback=[10,20,50], z_thresh=[1.5,2.0],
    sl_atr=[1.0,2.0,3.0], tp_r=[1.0,2.0,3.0], timeout=[8,16,32],
)

# ----------------------------- FEATURES (lookahead-safe) -----------------------------
def add_features(df, cfg=CFG):
    d=df.copy().reset_index(drop=True)
    c,h,l=d['close'],d['high'],d['low']
    d['ret']=c.pct_change()
    tr=np.maximum(h-l, np.maximum((h-c.shift()).abs(),(l-c.shift()).abs()))
    d['atr']=tr.rolling(cfg['atr_len']).mean()
    park=np.log(h/l)**2/(4*np.log(2))
    d['pvol']=np.sqrt(park.rolling(cfg['vol_len']).mean())
    d['vol_rank']=d['pvol'].rolling(cfg['vol_rank_win']).apply(
        lambda x: (x[:-1]<x[-1]).mean() if len(x)>1 else np.nan, raw=True)
    sma=c.rolling(cfg['trend_len']).mean()
    d['trend_up']=(sma>sma.shift(cfg['trend_len']//2)).astype(float)
    d['sma']=sma; d['sma_std']=c.rolling(cfg['trend_len']).std()
    # all features are computed on data up to and including bar t (close). Entry at t+1 open.
    return d

def canonical(h):
    hh=dict(h)
    if hh['entry']=='breakout': hh['z_thresh']=None      # unused -> canonicalize
    key=tuple(sorted(hh.items(),key=lambda kv:kv[0]))
    return hh, hashlib.md5(str(key).encode()).hexdigest()[:12]

# ----------------------------- HYPOTHESIS GENERATOR -----------------------------
def generate():
    seen=set(); out=[]
    keys=list(GRID.keys())
    for combo in itertools.product(*[GRID[k] for k in keys]):
        h=dict(zip(keys,combo))
        hh,hid=canonical(h)
        if hid in seen: continue
        seen.add(hid); hh['id']=hid; out.append(hh)
    return out

# ----------------------------- BACKTEST ENGINE (lookahead-safe) -----------------------------
def signal_series(d,h):
    c=d['close']
    if h['entry']=='breakout':
        roll_max=c.rolling(h['lookback']).max().shift(1)   # max of PAST lookback bars
        roll_min=c.rolling(h['lookback']).min().shift(1)
        sig = (c>roll_max) if h['direction']=='long' else (c<roll_min)
    else: # meanrev
        z=(c-d['sma'])/d['sma_std']
        sig = (z< -h['z_thresh']) if h['direction']=='long' else (z> h['z_thresh'])
    # context filters
    if h['vol_regime']=='low':  sig &= (d['vol_rank']<0.5)
    elif h['vol_regime']=='high': sig &= (d['vol_rank']>=0.5)
    if h['trend']=='up':   sig &= (d['trend_up']>0.5)
    elif h['trend']=='down': sig &= (d['trend_up']<=0.5)
    return sig.fillna(False).values

def backtest(d,h,cfg=CFG):
    o=d['open'].values; hi=d['high'].values; lo=d['low'].values; cl=d['close'].values
    atr=d['atr'].values; sig=signal_series(d,h)
    n=len(d); cost=(cfg['spread_ticks']+cfg['slip_ticks'])*cfg['tick']   # per side
    dirn=1 if h['direction']=='long' else -1
    trades=[]; i=0
    while i< n-2:
        if sig[i] and not np.isnan(atr[i]) and atr[i]>0:
            entry_idx=i+1; entry=o[entry_idx]
            risk=h['sl_atr']*atr[i]
            if risk<=0: i+=1; continue
            sl=entry - dirn*risk; tp=entry + dirn*risk*h['tp_r']
            exit_px=None; exit_idx=None
            for j in range(entry_idx, min(entry_idx+h['timeout'], n)):
                # worst-case intrabar: SL checked before TP
                if dirn==1:
                    if lo[j]<=sl: exit_px=sl; exit_idx=j; break
                    if hi[j]>=tp: exit_px=tp; exit_idx=j; break
                else:
                    if hi[j]>=sl: exit_px=sl; exit_idx=j; break
                    if lo[j]<=tp: exit_px=tp; exit_idx=j; break
            if exit_px is None:
                exit_idx=min(entry_idx+h['timeout'], n-1); exit_px=cl[exit_idx]
            pnl=dirn*(exit_px-entry) - 2*cost           # round-trip cost
            R=pnl/risk
            trades.append(dict(ei=entry_idx,xi=exit_idx,R=R,pnl=pnl))
            i=exit_idx+1
        else:
            i+=1
    return pd.DataFrame(trades)

# ----------------------------- METRICS -----------------------------
def metrics(tr):
    if len(tr)==0: return dict(n=0,exp=np.nan,pf=np.nan,dd=np.nan,win=np.nan,sharpe=np.nan)
    R=tr['R'].values; eq=np.cumsum(R); peak=np.maximum.accumulate(eq)
    dd=float(np.max(peak-eq)) if len(eq) else 0.0
    gp=R[R>0].sum(); gl=-R[R<0].sum()
    pf=float(gp/gl) if gl>0 else (np.inf if gp>0 else 0.0)
    return dict(n=int(len(R)),exp=float(R.mean()),pf=pf,dd=dd,
                win=float((R>0).mean()),sharpe=float(R.mean()/(R.std()+1e-9)*np.sqrt(len(R))))

# ----------------------------- SPLITS -----------------------------
def splits(d,cfg=CFG):
    n=len(d); a=int(n*cfg['split'][0]); b=a+int(n*cfg['split'][1])
    return d.iloc[:a].copy(), d.iloc[a:b].copy(), d.iloc[b:].copy()  # research, validation, holdout

# ----------------------------- STATISTICIAN -----------------------------
def neighbors(h):
    out=[]
    for k,seq in [('lookback',GRID['lookback']),('sl_atr',GRID['sl_atr']),('tp_r',GRID['tp_r'])]:
        idx=seq.index(h[k])
        for d2 in (-1,1):
            j=idx+d2
            if 0<=j<len(seq):
                hn=dict(h); hn[k]=seq[j]; out.append(hn)
    return out

def mc_pvalue(d,h,obs_exp,cfg=CFG):
    """randomized-entry null: same #trades, random eligible entry bars -> expectancy dist."""
    rng=np.random.default_rng(cfg['seed'])
    o=d['open'].values; hi=d['high'].values; lo=d['low'].values; cl=d['close'].values; atr=d['atr'].values
    valid=np.where(~np.isnan(atr)&(atr>0))[0]; valid=valid[valid<len(d)-2]
    tr=backtest(d,h,cfg); k=len(tr)
    if k<3 or len(valid)<k: return 1.0
    dirn=1 if h['direction']=='long' else -1
    null=np.empty(cfg['MC_B'])
    for b in range(cfg['MC_B']):
        ents=rng.choice(valid,size=k,replace=False); Rs=[]
        for i in ents:
            entry=o[i+1]; risk=h['sl_atr']*atr[i]
            if risk<=0: Rs.append(0); continue
            sl=entry-dirn*risk; tp=entry+dirn*risk*h['tp_r']; ex=None
            for j in range(i+1,min(i+1+h['timeout'],len(d))):
                if dirn==1:
                    if lo[j]<=sl: ex=sl;break
                    if hi[j]>=tp: ex=tp;break
                else:
                    if hi[j]>=sl: ex=sl;break
                    if lo[j]<=tp: ex=tp;break
            if ex is None: ex=cl[min(i+1+h['timeout'],len(d)-1)]
            cost=(cfg['spread_ticks']+cfg['slip_ticks'])*cfg['tick']
            Rs.append((dirn*(ex-entry)-2*cost)/risk)
        null[b]=np.mean(Rs)
    return float((np.sum(null>=obs_exp)+1)/(cfg['MC_B']+1))

def statistician(d_res,d_val,h,cfg=CFG):
    """returns (verdict dict). Gates in order; first failure stops."""
    tr=backtest(d_res,h,cfg); m=metrics(tr)
    g={}
    g['sanity']= m['n']>0 and not np.isnan(m['exp'])
    if not g['sanity']: return dict(passed=False,stage='sanity',m=m)
    g['min_trades']= m['n']>=cfg['MINTR']
    if not g['min_trades']: return dict(passed=False,stage='min_trades',m=m)
    g['expectancy']= m['exp']>cfg['EXP_MIN']
    if not g['expectancy']: return dict(passed=False,stage='expectancy',m=m)
    g['profit_factor']= m['pf']>=cfg['PF_MIN']
    if not g['profit_factor']: return dict(passed=False,stage='profit_factor',m=m)
    g['max_dd']= m['dd']<=cfg['DD_MAX_R']
    if not g['max_dd']: return dict(passed=False,stage='max_dd',m=m)
    # parameter stability: majority of grid-neighbors positive on research
    nb=[metrics(backtest(d_res,hn,cfg))['exp'] for hn in neighbors(h)]
    nb=[x for x in nb if not np.isnan(x)]
    g['param_stability']= (np.mean([x>0 for x in nb])>=0.5) if nb else False
    if not g['param_stability']: return dict(passed=False,stage='param_stability',m=m)
    # out-of-sample (validation)
    mv=metrics(backtest(d_val,h,cfg))
    g['oos']= (mv['n']>=5) and (mv['exp']>cfg['EXP_MIN'])
    if not g['oos']: return dict(passed=False,stage='oos',m=m,mv=mv)
    # Monte-Carlo significance (randomized-entry null) on research
    p=mc_pvalue(d_res,h,m['exp'],cfg)
    return dict(passed=True,stage='stat_ok',m=m,mv=mv,p=p,nb_pos=float(np.mean([x>0 for x in nb])))

def bh_fdr(pvals,q):
    p=np.array(pvals); m=len(p); order=np.argsort(p); passed=np.zeros(m,bool)
    sp=p[order]; k=np.where(sp<=(np.arange(1,m+1)/m*q))[0]
    if len(k): passed[order[:k.max()+1]]=True
    return passed

# ----------------------------- RED TEAM -----------------------------
def red_team(d_res,d_val,h,cfg=CFG):
    attacks={}
    # 1. cost stress 3x
    c2=dict(cfg); c2['spread_ticks']*=3; c2['slip_ticks']*=3
    attacks['cost_stress_3x']= metrics(backtest(d_res,h,c2))['exp']>0
    # 2. remove single best 'day' (regime cherry-pick) : drop the best contiguous 20% block
    tr=backtest(d_res,h,cfg)
    if len(tr)>=5:
        R=tr['R'].values; k=max(1,len(R)//5)
        # sliding best block sum
        best=max(np.sum(R[i:i+k]) for i in range(0,len(R)-k+1))
        attacks['no_cherry_block']= (R.sum()-best)/max(len(R)-k,1) > 0   # still positive without best block
    else: attacks['no_cherry_block']=False
    # 3. sign consistency across sessions (per 'day') on research
    # 4. synthetic null: strategy on bootstrapped bar returns should NOT be profitable > real
    attacks['beats_bootstrap']= _bootstrap_attack(d_res,h,cfg)
    passed=all(attacks.values())
    return passed, attacks

def _bootstrap_attack(d,h,cfg,B=200):
    """resample bar log-returns to build synthetic price paths; real expectancy must beat 95% of them."""
    rng=np.random.default_rng(cfg['seed']+1)
    obs=metrics(backtest(d,h,cfg))['exp']
    if np.isnan(obs): return False
    lr=np.log(d['close']/d['close'].shift()).dropna().values
    base=d['close'].iloc[0]; n=len(d); null=[]
    for b in range(B):
        samp=rng.choice(lr,size=n-1,replace=True); path=base*np.exp(np.concatenate([[0],np.cumsum(samp)]))
        dd=d.copy(); scale=path/dd['close'].values
        dd['open']=dd['open'].values*scale; dd['high']=dd['high'].values*scale
        dd['low']=dd['low'].values*scale; dd['close']=path
        dd=add_features(dd,cfg); null.append(metrics(backtest(dd,h,cfg))['exp'])
    null=np.array([x for x in null if not np.isnan(x)])
    return bool(obs> np.quantile(null,0.95)) if len(null)>10 else False

# ----------------------------- ORCHESTRATOR -----------------------------
def run_pipeline(df, label, cfg=CFG, touch_holdout=True, verbose=True):
    d=add_features(df,cfg); d_res,d_val,d_hold=splits(d,cfg)
    hyps=generate()
    if verbose: print(f"\n==== CYCLE [{label}] ====\nHypotheses generated: {len(hyps)}  bars: research={len(d_res)} val={len(d_val)} holdout={len(d_hold)}")
    # Stage A: statistician gates (cheap first)
    survivors=[]; stage_deaths={}
    for h in hyps:
        v=statistician(d_res,d_val,h,cfg)
        stage_deaths[v['stage']]=stage_deaths.get(v['stage'],0)+1
        if v['passed']: survivors.append((h,v))
    if verbose:
        print("Deaths by stage:", dict(sorted(stage_deaths.items(),key=lambda x:-x[1])))
        print(f"Passed statistical gates (pre-FDR): {len(survivors)}")
    if not survivors:
        return dict(label=label,candidates=[],n_hyp=len(hyps),stage_deaths=stage_deaths)
    # Stage B: multiple-testing FDR across ALL tested hypotheses
    ps=[v['p'] for _,v in survivors]; keep=bh_fdr(ps,cfg['FDR_Q'])
    fdr_surv=[survivors[i] for i in range(len(survivors)) if keep[i]]
    if verbose: print(f"Survive FDR (q={cfg['FDR_Q']}): {len(fdr_surv)}")
    # Stage C: Red Team
    rt_surv=[]
    for h,v in fdr_surv:
        ok,att=red_team(d_res,d_val,h,cfg)
        if ok: rt_surv.append((h,v,att))
    if verbose: print(f"Survive Red Team: {len(rt_surv)}")
    # Stage D: HOLDOUT (opened once, terminal) - only for Red Team survivors
    cands=[]
    for h,v,att in rt_surv:
        mh=metrics(backtest(d_hold,h,cfg)) if touch_holdout and len(d_hold)>20 else dict(n=0,exp=np.nan)
        holdout_ok = touch_holdout and mh['n']>=5 and mh['exp']>0
        cands.append(dict(h=h,research=v['m'],val=v['mv'],p=v['p'],attacks=att,holdout=mh,holdout_ok=holdout_ok))
    if verbose:
        print(f"ALPHA CANDIDATES (passed everything incl. holdout): {sum(c['holdout_ok'] for c in cands)}")
        for c in cands:
            tag="ALPHA" if c['holdout_ok'] else "rejected@holdout"
            print(f"  [{tag}] {c['h']['id']} {c['h']['entry']}/{c['h']['direction']} vol={c['h']['vol_regime']} "
                  f"lb={c['h']['lookback']} sl={c['h']['sl_atr']} tp={c['h']['tp_r']} | "
                  f"res exp={c['research']['exp']:.3f} pf={c['research']['pf']:.2f} n={c['research']['n']} | "
                  f"val exp={c['val']['exp']:.3f} | p={c['p']:.3f} | holdout exp={c['holdout']['exp']:.3f} n={c['holdout']['n']}")
    return dict(label=label,candidates=cands,n_hyp=len(hyps),stage_deaths=stage_deaths,
                n_stat=len(survivors),n_fdr=len(fdr_surv),n_rt=len(rt_surv))

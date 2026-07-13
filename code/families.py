"""
GRAMMAR EXTENSION (production). Adds families to the FROZEN pipeline via monkeypatch:
breakout, mean-reversion, momentum, rsi, ema_cross, vol_expansion, range_pos, distance.
Adds trailing-stop exit. Gate/stat/redteam logic in alpha_lab.py stays UNCHANGED.
Lookahead-safe; entries executed at next-bar open by the frozen backtest loop.
"""
import numpy as np, pandas as pd, itertools, hashlib
from alpha_lab import CFG

FAMILIES=['breakout','meanrev','momentum','rsi','ema_cross','vol_expansion','range_pos','distance']

COMMON=dict(direction=['long','short'], vol_regime=['any','low','high'], trend=['any','up','down'],
            dow=['any','midweek'], sl_atr=[1.0,2.0,3.0], tp_r=[1.0,2.0,3.0],
            timeout=[5,10,20], trail=['none','atr2'])
FAMPARAMS=dict(
    breakout=dict(lookback=[10,20,50]),
    meanrev=dict(z_thresh=[1.5,2.0,2.5]),
    momentum=dict(lookback=[10,20,50], mom_thresh=[0.02,0.05]),
    rsi=dict(rsi_level=[30,20]),
    ema_cross=dict(),
    vol_expansion=dict(k_exp=[1.5,2.0]),
    range_pos=dict(lookback=[10,20,50], range_frac=[0.15,0.10]),
    distance=dict(dist=[1.5,2.5]),
)
ALLPARAMS=['lookback','z_thresh','mom_thresh','rsi_level','k_exp','range_frac','dist']

# ---------------- features ----------------
def add_features(df, cfg=CFG):
    d=df.copy().reset_index(drop=True)
    c,h,l=d['close'],d['high'],d['low']
    tr=np.maximum(h-l, np.maximum((h-c.shift()).abs(),(l-c.shift()).abs()))
    d['atr']=tr.rolling(cfg['atr_len']).mean()
    park=np.log(h/l)**2/(4*np.log(2)); d['pvol']=np.sqrt(park.rolling(cfg['vol_len']).mean())
    d['vol_rank']=d['pvol'].rolling(cfg['vol_rank_win']).apply(
        lambda x:(x[:-1]<x[-1]).mean() if len(x)>1 else np.nan, raw=True)
    sma=c.rolling(cfg['trend_len']).mean(); d['sma']=sma; d['sma_std']=c.rolling(cfg['trend_len']).std()
    d['trend_up']=(sma>sma.shift(cfg['trend_len']//2)).astype(float)
    d['ema20']=c.ewm(span=20).mean(); d['ema50']=c.ewm(span=50).mean()
    delta=c.diff(); gain=delta.clip(lower=0); loss=-delta.clip(upper=0)
    ag=gain.ewm(alpha=1/14,adjust=False).mean(); al=loss.ewm(alpha=1/14,adjust=False).mean()
    d['rsi']=100-100/(1+ag/(al+1e-12))
    d['atr_ma']=d['atr'].rolling(20).mean()
    if 'time' in d: d['dow']=pd.to_datetime(d['time'],unit='s',utc=True).dt.dayofweek
    else: d['dow']=-1
    return d

# ---------------- signal ----------------
def signal_series(d,h):
    c=d['close']; sig=pd.Series(False,index=d.index)
    lb=h.get('lookback'); dirn=h['direction']
    if h['entry']=='breakout':
        rmax=c.rolling(lb).max().shift(1); rmin=c.rolling(lb).min().shift(1)
        sig=(c>rmax) if dirn=='long' else (c<rmin)
    elif h['entry']=='meanrev':
        z=(c-d['sma'])/d['sma_std']; sig=(z<-h['z_thresh']) if dirn=='long' else (z>h['z_thresh'])
    elif h['entry']=='momentum':
        roc=c/c.shift(lb)-1; sig=(roc>h['mom_thresh']) if dirn=='long' else (roc<-h['mom_thresh'])
    elif h['entry']=='rsi':
        lv=h['rsi_level']; sig=(d['rsi']<lv) if dirn=='long' else (d['rsi']>100-lv)
    elif h['entry']=='ema_cross':
        f,s=d['ema20'],d['ema50']; up=(f>s)&(f.shift(1)<=s.shift(1)); dn=(f<s)&(f.shift(1)>=s.shift(1))
        sig=up if dirn=='long' else dn
    elif h['entry']=='vol_expansion':
        rng=d['high']-d['low']; exp=rng>h['k_exp']*d['atr'].shift(1)
        sig=(exp&(c>d['open'])) if dirn=='long' else (exp&(c<d['open']))
    elif h['entry']=='range_pos':
        rmax=c.rolling(lb).max(); rmin=c.rolling(lb).min(); rp=(c-rmin)/(rmax-rmin+1e-12)
        sig=(rp<h['range_frac']) if dirn=='long' else (rp>1-h['range_frac'])
    elif h['entry']=='distance':
        dd=(c-d['sma'])/d['atr']; sig=(dd<-h['dist']) if dirn=='long' else (dd>h['dist'])
    # context filters
    if h['vol_regime']=='low': sig=sig&(d['vol_rank']<0.5)
    elif h['vol_regime']=='high': sig=sig&(d['vol_rank']>=0.5)
    if h['trend']=='up': sig=sig&(d['trend_up']>0.5)
    elif h['trend']=='down': sig=sig&(d['trend_up']<=0.5)
    if h['dow']=='midweek': sig=sig&(d['dow'].isin([1,2,3]))
    return sig.fillna(False).values

# ---------------- backtest (adds trailing) ----------------
def backtest(d,h,cfg=CFG):
    o=d['open'].values; hi=d['high'].values; lo=d['low'].values; cl=d['close'].values
    atr=d['atr'].values; sig=signal_series(d,h); n=len(d)
    cost=(cfg['spread_ticks']+cfg['slip_ticks'])*cfg['tick']; dirn=1 if h['direction']=='long' else -1
    trail = h.get('trail','none'); tmult=2.0
    trades=[]; i=0
    while i<n-2:
        if sig[i] and not np.isnan(atr[i]) and atr[i]>0:
            ei=i+1; entry=o[ei]; risk=h['sl_atr']*atr[i]
            if risk<=0: i+=1; continue
            sl=entry-dirn*risk; tp=entry+dirn*risk*h['tp_r']; best=entry; expx=None; xi=None
            for j in range(ei, min(ei+h['timeout'], n)):
                if trail=='atr2':
                    best = max(best,hi[j]) if dirn==1 else min(best,lo[j])
                    ts = best-dirn*tmult*atr[i]; sl = max(sl,ts) if dirn==1 else min(sl,ts)
                if dirn==1:
                    if lo[j]<=sl: expx=sl;xi=j;break
                    if hi[j]>=tp: expx=tp;xi=j;break
                else:
                    if hi[j]>=sl: expx=sl;xi=j;break
                    if lo[j]<=tp: expx=tp;xi=j;break
            if expx is None: xi=min(ei+h['timeout'],n-1); expx=cl[xi]
            pnl=dirn*(expx-entry)-2*cost
            trades.append(dict(ei=ei,xi=xi,R=pnl/risk,pnl=pnl)); i=xi+1
        else: i+=1
    return pd.DataFrame(trades)

# ---------------- generator (canonical, dedup, balanced sampling) ----------------
def canonical(h):
    hh=dict(h)
    for p in ALLPARAMS:
        if p not in FAMPARAMS.get(hh['entry'],{}): hh[p]=None
    key=tuple(sorted((k,v) for k,v in hh.items() if k!='id'))
    return hh, hashlib.md5(str(key).encode()).hexdigest()[:12]

def family_grid(fam):
    params={'entry':[fam], **COMMON, **FAMPARAMS[fam]}
    keys=list(params.keys()); out=[]; seen=set()
    for combo in itertools.product(*[params[k] for k in keys]):
        h=dict(zip(keys,combo)); hh,hid=canonical(h)
        if hid in seen: continue
        seen.add(hid); hh['id']=hid; out.append(hh)
    return out

# ---------------- CRITICAL-DEFECT FIX: higher-resolution randomized-entry null ----------------
# Same statistic (mean-R under random entry) + BH-FDR unchanged, but B=5000 resolution and a
# per-exit-config cached entry-R pool so genuine edges are not killed by coarse p-floor at scale.
_POOL={}
def _entry_pool(d,ecfg,cfg,npool=4000):
    key=(len(d),round(float(d['close'].iloc[0]),3),round(float(d['close'].iloc[-1]),3))+ecfg
    if key in _POOL: return _POOL[key]
    dirn,sl_atr,tp_r,timeout,trail=ecfg
    o=d['open'].values;hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;atr=d['atr'].values
    valid=np.where(~np.isnan(atr)&(atr>0))[0]; valid=valid[valid<len(d)-2]
    if len(valid)<10: _POOL[key]=np.array([]); return _POOL[key]
    rng=np.random.default_rng(cfg['seed'])
    ents=rng.choice(valid,size=min(npool,len(valid)),replace=(len(valid)<npool))
    d_=1 if dirn=='long' else -1; cost=(cfg['spread_ticks']+cfg['slip_ticks'])*cfg['tick']; Rs=[]
    for i in ents:
        entry=o[i+1]; risk=sl_atr*atr[i]
        if risk<=0: continue
        sl=entry-d_*risk; tp=entry+d_*risk*tp_r; best=entry; ex=None
        for j in range(i+1,min(i+1+timeout,len(d))):
            if trail=='atr2':
                best=max(best,hi[j]) if d_==1 else min(best,lo[j])
                ts=best-d_*2.0*atr[i]; sl=max(sl,ts) if d_==1 else min(sl,ts)
            if d_==1:
                if lo[j]<=sl: ex=sl;break
                if hi[j]>=tp: ex=tp;break
            else:
                if hi[j]>=sl: ex=sl;break
                if lo[j]<=tp: ex=tp;break
        if ex is None: ex=cl[min(i+1+timeout,len(d)-1)]
        Rs.append((d_*(ex-entry)-2*cost)/risk)
    _POOL[key]=np.array(Rs); return _POOL[key]

def mc_pvalue(d,h,obs_exp,cfg,B=5000):
    ecfg=(h['direction'],h['sl_atr'],h['tp_r'],h['timeout'],h.get('trail','none'))
    pool=_entry_pool(d,ecfg,cfg); tr=backtest(d,h,cfg); k=len(tr)
    if k<3 or len(pool)<10: return 1.0
    rng=np.random.default_rng(cfg['seed']+1)
    samp=rng.choice(pool,size=(B,k),replace=True).mean(axis=1)
    return float((np.sum(samp>=obs_exp)+1)/(B+1))

NEIGHBOR_GRIDS={'sl_atr':[1.0,2.0,3.0],'tp_r':[1.0,2.0,3.0],'timeout':[5,10,20],
                'lookback':[10,20,50],'z_thresh':[1.5,2.0,2.5],'mom_thresh':[0.02,0.05],
                'dist':[1.5,2.5],'range_frac':[0.15,0.10]}
def neighbors(h):
    """param_stability neighbors: perturb each present numeric param +/-1 grid step."""
    out=[]
    for k,seq in NEIGHBOR_GRIDS.items():
        v=h.get(k)
        if v is None or v not in seq: continue
        idx=seq.index(v)
        for dd in (-1,1):
            j=idx+dd
            if 0<=j<len(seq):
                hn=dict(h); hn[k]=seq[j]; out.append(hn)
    return out

def generate(budget=None, seed=7):
    grids={f:family_grid(f) for f in FAMILIES}
    if budget is None:
        allh=[h for g in grids.values() for h in g]
        return allh
    rng=np.random.default_rng(seed); per=budget//len(FAMILIES); out=[]; seen=set()
    for f in FAMILIES:
        g=grids[f]; idx=rng.permutation(len(g))[:per]
        for k in idx:
            if g[k]['id'] not in seen: seen.add(g[k]['id']); out.append(g[k])
    return out

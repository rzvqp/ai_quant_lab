"""Multi-timeframe alpha engine (XAUUSD). Daily/4H context -> 1H confirm -> 15M trigger/exec.
Lookahead-safe: each M15 bar sees only higher-TF bars already CLOSED (merge_asof on availability
= next-bar-start). Signal at M15 close; entry at next M15 open. Optimized backtest (signal-indexed)."""
import numpy as np, pandas as pd, itertools, hashlib, math
from alpha_lab import CFG
D=r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\344b31d3-785f-43a4-b73b-d80a24bc18df\scratchpad\phaseb\alpha\data_market"
TICK=0.1

def _ind(df):
    c,h,l=df['close'],df['high'],df['low']
    tr=np.maximum(h-l,np.maximum((h-c.shift()).abs(),(l-c.shift()).abs())); atr=tr.rolling(14).mean()
    park=np.log(h/l)**2/(4*np.log(2)); pv=np.sqrt(park.rolling(14).mean())
    volrank=pv.rolling(60).apply(lambda x:(x[:-1]<x[-1]).mean() if len(x)>1 else np.nan,raw=True)
    ema20=c.ewm(span=20).mean(); ema50=c.ewm(span=50).mean()
    dlt=c.diff(); ag=dlt.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); al=(-dlt.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean()
    rsi=100-100/(1+ag/(al+1e-12)); sma=c.rolling(20).mean(); std=c.rolling(20).std()
    return dict(atr=atr,volrank=volrank,ema20=ema20,ema50=ema50,rsi=rsi,sma=sma,std=std,
                trend_up=(ema20>ema50).astype(float))

def _htf_feat(path,period):
    df=pd.read_csv(path); ind=_ind(df)
    df['trend_up']=ind['trend_up']; df['volrank']=ind['volrank']; df['rsi']=ind['rsi']
    df['avail']=df['time'].shift(-1); df.loc[df.index[-1],'avail']=df['time'].iloc[-1]+period
    df['avail']=df['avail'].astype('int64')
    return df[['avail','trend_up','volrank','rsi']]

def load_mtf():
    m=pd.read_csv(D+r"\OANDA_XAUUSD_M15.csv").drop_duplicates('time').sort_values('time').reset_index(drop=True)
    ind=_ind(m)
    for k in ['atr','ema20','ema50','rsi','sma','std','volrank','trend_up']: m['m_'+k]=ind[k]
    hh=pd.to_datetime(m['time'],unit='s',utc=True).dt.hour
    m['session']=np.select([hh<8,hh<13,hh<21],['asia','london','ny'],default='late')
    for pre,path,per in [('h4_',D+r"\OANDA_XAUUSD_H4.csv",4*3600),('h1_',D+r"\OANDA_XAUUSD_H1.csv",3600),('d1_',D+r"\OANDA_XAUUSD_D1.csv",86400)]:
        htf=_htf_feat(path,per).rename(columns={'trend_up':pre+'trend_up','volrank':pre+'volrank','rsi':pre+'rsi'})
        m=pd.merge_asof(m.sort_values('time'),htf.sort_values('avail'),left_on='time',right_on='avail',direction='backward').drop(columns='avail')
    return m.reset_index(drop=True)

# ---------------- grammar ----------------
TRIGS=['breakout','meanrev','momentum','rsi','ema_cross','range_pos']
GD=dict(direction=['long','short'],c4h_trend=['any','up','down'],c4h_vol=['any','low','high'],
        conf_1h=['any','align','rsi'],session=['any','asia','london','ny'],
        sl_atr=[1.0,2.0,3.0],tp_r=[1.0,2.0,3.0],timeout=[8,16,32],trail=['none','atr2'])
USES_LB={'breakout','momentum','range_pos'}
def canonical(h):
    hh=dict(h)
    if hh['trig'] not in USES_LB: hh['lookback']=None
    key=tuple(sorted((k,v) for k,v in hh.items() if k!='id'))
    return hh,hashlib.md5(str(key).encode()).hexdigest()[:12]
def _fam_grid(trig):
    p={'trig':[trig],**GD}; p['lookback']=[10,20,50] if trig in USES_LB else [None]
    keys=list(p.keys()); out=[]; seen=set()
    for combo in itertools.product(*[p[k] for k in keys]):
        h=dict(zip(keys,combo)); hh,hid=canonical(h)
        if hid in seen: continue
        seen.add(hid); hh['id']=hid; out.append(hh)
    return out
def generate(budget=None,seed=7):
    grids={t:_fam_grid(t) for t in TRIGS}
    if budget is None: return [h for g in grids.values() for h in g]
    rng=np.random.default_rng(seed); per=budget//len(TRIGS); out=[]; seen=set()
    for t in TRIGS:
        g=grids[t]; idx=rng.permutation(len(g))[:per]
        for k in idx:
            if g[k]['id'] not in seen: seen.add(g[k]['id']); out.append(g[k])
    return out
def neighbors(h):
    grids={'sl_atr':[1.0,2.0,3.0],'tp_r':[1.0,2.0,3.0],'timeout':[8,16,32],'lookback':[10,20,50]}
    out=[]
    for k,seq in grids.items():
        v=h.get(k)
        if v is None or v not in seq: continue
        i=seq.index(v)
        for dd in (-1,1):
            if 0<=i+dd<len(seq): hn=dict(h); hn[k]=seq[i+dd]; out.append(hn)
    return out

# ---------------- signal ----------------
def signal_series(d,h):
    c=d['close']; dirn=h['direction']; lb=int(h['lookback']) if h.get('lookback') else 20; t=h['trig']
    if t=='breakout':
        rmax=c.rolling(lb).max().shift(1); rmin=c.rolling(lb).min().shift(1); s=(c>rmax) if dirn=='long' else (c<rmin)
    elif t=='meanrev':
        z=(c-d['m_sma'])/d['m_std']; s=(z<-1.5) if dirn=='long' else (z>1.5)
    elif t=='momentum':
        roc=c/c.shift(lb)-1; s=(roc>0.003) if dirn=='long' else (roc<-0.003)
    elif t=='rsi':
        s=(d['m_rsi']<30) if dirn=='long' else (d['m_rsi']>70)
    elif t=='ema_cross':
        f,sl=d['m_ema20'],d['m_ema50']; up=(f>sl)&(f.shift(1)<=sl.shift(1)); dn=(f<sl)&(f.shift(1)>=sl.shift(1)); s=up if dirn=='long' else dn
    elif t=='range_pos':
        rmax=c.rolling(lb).max(); rmin=c.rolling(lb).min(); rp=(c-rmin)/(rmax-rmin+1e-9); s=(rp<0.15) if dirn=='long' else (rp>0.85)
    if h['c4h_trend']=='up': s=s&(d['h4_trend_up']>0.5)
    elif h['c4h_trend']=='down': s=s&(d['h4_trend_up']<=0.5)
    if h['c4h_vol']=='low': s=s&(d['h4_volrank']<0.5)
    elif h['c4h_vol']=='high': s=s&(d['h4_volrank']>=0.5)
    if h['conf_1h']=='align': s=s&((d['h1_trend_up']>0.5) if dirn=='long' else (d['h1_trend_up']<=0.5))
    elif h['conf_1h']=='rsi': s=s&((d['h1_rsi']<45) if dirn=='long' else (d['h1_rsi']>55))
    if h['session']!='any': s=s&(d['session']==h['session'])
    return np.asarray(s.fillna(False).values)

# ---------------- optimized backtest (signal-indexed) ----------------
def backtest(d,h,cfg=CFG):
    Rs,eis=_exact_R(d,h,cfg); return pd.DataFrame({'R':Rs,'ei':eis})

def _exact_R(d,h,cfg):
    o=d['open'].values;hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;atr=d['m_atr'].values
    sig=signal_series(d,h); n=len(d); cost=(cfg['spread_ticks']+cfg['slip_ticks'])*TICK
    dirn=1 if h['direction']=='long' else -1; trail=h.get('trail','none'); to=int(h['timeout']); Rs=[]; eis=[]; last=-1
    for i in np.flatnonzero(sig):
        if i<=last or i>=n-2 or np.isnan(atr[i]) or atr[i]<=0: continue
        ei=i+1; entry=o[ei]; risk=h['sl_atr']*atr[i]
        if risk<=0: continue
        sl=entry-dirn*risk; tp=entry+dirn*risk*h['tp_r']; best=entry; ex=None; xi=None
        for j in range(ei,min(ei+to,n)):
            if trail=='atr2':
                best=max(best,hi[j]) if dirn==1 else min(best,lo[j])
                ts=best-dirn*2.0*atr[i]; sl=max(sl,ts) if dirn==1 else min(sl,ts)
            if dirn==1:
                if lo[j]<=sl: ex=sl;xi=j;break
                if hi[j]>=tp: ex=tp;xi=j;break
            else:
                if hi[j]>=sl: ex=sl;xi=j;break
                if lo[j]<=tp: ex=tp;xi=j;break
        if ex is None: xi=min(ei+to,n-1); ex=cl[xi]
        Rs.append((dirn*(ex-entry)-2*cost)/risk); eis.append(ei); last=xi
    return Rs,eis

# random-entry pool for analytic null (exit-config keyed)
_POOL={}
def entry_pool(d,ecfg,cfg,npool=3000):
    key=(len(d),round(float(d['close'].iloc[0]),2))+ecfg
    if key in _POOL: return _POOL[key]
    dirn,sl_atr,tp_r,to,trail=ecfg
    o=d['open'].values;hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;atr=d['m_atr'].values
    valid=np.where(np.isfinite(atr)&(atr>0))[0]; valid=valid[valid<len(d)-2]
    if len(valid)<50: _POOL[key]=np.array([]); return _POOL[key]
    rng=np.random.default_rng(cfg['seed']); ents=rng.choice(valid,size=min(npool,len(valid)),replace=False)
    d_=1 if dirn=='long' else -1; cost=(cfg['spread_ticks']+cfg['slip_ticks'])*TICK; Rs=[]
    for i in ents:
        entry=o[i+1]; risk=sl_atr*atr[i]
        if risk<=0: continue
        sl=entry-d_*risk; tp=entry+d_*risk*tp_r; best=entry; ex=None
        for j in range(i+1,min(i+1+to,len(d))):
            if trail=='atr2':
                best=max(best,hi[j]) if d_==1 else min(best,lo[j]); ts=best-d_*2.0*atr[i]; sl=max(sl,ts) if d_==1 else min(sl,ts)
            if d_==1:
                if lo[j]<=sl: ex=sl;break
                if hi[j]>=tp: ex=tp;break
            else:
                if hi[j]>=sl: ex=sl;break
                if lo[j]<=tp: ex=tp;break
        if ex is None: ex=cl[min(i+1+to,len(d)-1)]
        Rs.append((d_*(ex-entry)-2*cost)/risk)
    _POOL[key]=np.array(Rs); return _POOL[key]

def analytic_p(d,h,obs_exp,k):
    ec=(h['direction'],h['sl_atr'],h['tp_r'],int(h['timeout']),h.get('trail','none'))
    pool=entry_pool(d,ec,CFG)
    if k<CFG['MINTR'] or len(pool)<30: return 1.0
    mu=float(np.mean(pool)); sd=float(np.std(pool,ddof=1))
    if sd<=0: return 1.0
    z=(obs_exp-mu)/(sd/math.sqrt(k)); return max(0.5*math.erfc(z/math.sqrt(2)),1e-300)

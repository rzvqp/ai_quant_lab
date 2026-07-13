"""S1 experimental family: liquidity sweep -> change of behavior (confirmation) -> imbalance(FVG/IFVG)
-> entry. NOT assuming ICT is correct: each stage is an independent PRIMITIVE with variants; all valid
combinations tested. Event-driven, lookahead-safe (entry at bar-open AFTER confirmation close).
Runs through the FROZEN pipeline (statistician->global FDR->walk-forward->Red Team; holdout sealed)."""
import numpy as np, pandas as pd, itertools, hashlib, math
from alpha_lab import CFG
import mtf as M
TICK=0.1

def load_s1():
    d=M.load_mtf()
    # attach last-closed Daily high/low (PDH/PDL)
    d1=pd.read_csv(M.D+r"\OANDA_XAUUSD_D1.csv"); d1['avail']=d1['time'].shift(-1); d1.loc[d1.index[-1],'avail']=d1['time'].iloc[-1]+86400
    d1['avail']=d1['avail'].astype('int64')
    d=pd.merge_asof(d.sort_values('time'),d1[['avail','high','low']].rename(columns={'high':'pdh','low':'pdl'}).sort_values('avail'),
                    left_on='time',right_on='avail',direction='backward').drop(columns='avail')
    h=d['high']; l=d['low']; c=d['close']; o=d['open']
    for L in (20,50):
        d[f'rmax{L}']=h.rolling(L).max().shift(1); d[f'rmin{L}']=l.rolling(L).min().shift(1)
    # session running high/low (reset per session block), shifted (lookahead-safe)
    sess=d['session'].values; blk=np.concatenate([[0],np.cumsum(sess[1:]!=sess[:-1])])
    d['blk']=blk
    d['sess_high']=h.groupby(d['blk']).cummax().shift(1); d['sess_low']=l.groupby(d['blk']).cummin().shift(1)
    # imbalance (3-bar FVG)
    d['fvg_bull']=(l>h.shift(2)).astype(float); d['fvg_bear']=(h<l.shift(2)).astype(float)
    d['disp']=((h-l)>1.5*d['m_atr']).astype(float)
    d['roc3']=c/c.shift(3)-1
    d['bear_close']=(c<o).astype(float); d['bull_close']=(c>o).astype(float)
    return d.reset_index(drop=True)

# ---------------- primitives (grammar) ----------------
GRID=dict(
    side=['high','low'],                                   # high=short setup, low=long setup
    liq_ref=['swing','session','pdh_pdl'],                 # A. liquidity event source
    liq_lb=[20,50],
    confirm=['none','displacement','close_beyond','consecutive2','momentum','break_retest'],  # B
    imb=['none','fvg','ifvg'],                             # C
    entry=['market','retest','limit'],                    # D
    stop=['beyond_sweep','atr','structural'],             # E
    exit=['rr2','rr3','trailing','opposite_liq','time'],  # F
    window=[4,8],
)
USES_LB={'swing'}
PRIMS=list(GRID.keys())
def canonical(h):
    hh=dict(h)
    if hh['liq_ref'] not in USES_LB: hh['liq_lb']=None
    key=tuple(sorted((k,v) for k,v in hh.items() if k!='id'))
    return hh,hashlib.md5(str(key).encode()).hexdigest()[:12]
def generate(budget=None,seed=7):
    keys=list(GRID.keys()); seen=set(); out=[]
    for combo in itertools.product(*[GRID[k] for k in keys]):
        h=dict(zip(keys,combo)); hh,hid=canonical(h)
        if hid in seen: continue
        seen.add(hid); hh['id']=hid; out.append(hh)
    if budget and budget<len(out):
        rng=np.random.default_rng(seed); out=[out[i] for i in rng.permutation(len(out))[:budget]]
    return out
def neighbors(h):
    out=[]
    for k,seq in [('window',[4,8]),('liq_lb',[20,50])]:
        v=h.get(k)
        if v in seq:
            for w in seq:
                if w!=v: hn=dict(h); hn[k]=w; out.append(hn)
    return out

def _refs(d,h):
    if h['liq_ref']=='swing': lb=int(h['liq_lb']); return d[f'rmax{lb}'].values, d[f'rmin{lb}'].values
    if h['liq_ref']=='session': return d['sess_high'].values, d['sess_low'].values
    return d['pdh'].values, d['pdl'].values

def _trades(d,h,cfg):
    o=d['open'].values;hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;atr=d['m_atr'].values
    rmax=d['rmax20'].values; rmin=d['rmin20'].values
    fb=d['fvg_bull'].values; fr=d['fvg_bear'].values; disp=d['disp'].values
    bearc=d['bear_close'].values; bullc=d['bull_close'].values; roc=d['roc3'].values
    refH,refL=_refs(d,h); n=len(d); W=int(h['window']); side=h['side']; dirn=-1 if side=='high' else 1
    cost=(cfg['spread_ticks']+cfg['slip_ticks'])*TICK
    # sweep events
    if side=='high': sweep=(hi>refH)&(cl<refH)&np.isfinite(refH)
    else: sweep=(lo<refL)&(cl>refL)&np.isfinite(refL)
    Rs=[]; eis=[]; last=-1
    for t0 in np.flatnonzero(sweep):
        if t0<=last or np.isnan(atr[t0]) or atr[t0]<=0: continue
        # confirmation
        conf=None
        if h['confirm']=='none': conf=t0
        else:
            for t1 in range(t0+1,min(t0+W+1,n)):
                ok=False; k=h['confirm']
                if k=='displacement': ok= disp[t1]>0 and ((bearc[t1]>0) if dirn<0 else (bullc[t1]>0))
                elif k=='close_beyond': ok= (cl[t1]<refL[t1]) if dirn<0 else (cl[t1]>refH[t1])
                elif k=='consecutive2': ok= (bearc[t1]>0 and bearc[t1-1]>0) if dirn<0 else (bullc[t1]>0 and bullc[t1-1]>0)
                elif k=='momentum': ok= (roc[t1]*dirn)>0.002
                elif k=='break_retest': ok= (cl[t1]<refL[t1]) if dirn<0 else (cl[t1]>refH[t1])
                if ok: conf=t1; break
        if conf is None: continue
        # imbalance requirement
        if h['imb']=='fvg':
            win=slice(t0,conf+1); has=(fr[win].any()) if dirn<0 else (fb[win].any())
            if not has: continue
        elif h['imb']=='ifvg':
            win=slice(t0,conf+1); has=(fb[win].any()) if dirn<0 else (fr[win].any())  # inverse-side FVG (flip)
            if not has: continue
        # entry
        if h['entry']=='market': ei=conf+1
        elif h['entry']=='limit': ei=conf+1
        else:  # retest: next bar that pulls back toward ref (touch)
            ei=None
            for t2 in range(conf+1,min(conf+W+1,n)):
                if (dirn<0 and hi[t2]>=refH[t0]) or (dirn>0 and lo[t2]<=refL[t0]): ei=t2; break
            if ei is None: continue
        if ei>=n-1: continue
        entry=o[ei]
        # stop
        if h['stop']=='beyond_sweep': stop= hi[t0]+2*TICK if dirn<0 else lo[t0]-2*TICK
        elif h['stop']=='atr': stop= entry-dirn*1.5*atr[t0]
        else: stop= (rmax[ei]+2*TICK) if dirn<0 else (rmin[ei]-2*TICK)
        risk=abs(entry-stop)
        if risk<=0 or not np.isfinite(risk): continue
        # exit / target
        to = 24 if h['exit']=='time' else 48
        if h['exit']=='rr2': tgt=entry+dirn*2*risk
        elif h['exit']=='rr3': tgt=entry+dirn*3*risk
        elif h['exit']=='opposite_liq': tgt= refL[ei] if dirn<0 else refH[ei]
        else: tgt=None   # trailing / time
        best=entry; ex=None; xi=None; trail=(h['exit']=='trailing')
        for j in range(ei,min(ei+to,n)):
            if trail:
                best=max(best,hi[j]) if dirn>0 else min(best,lo[j])
                ts=best-dirn*1.5*atr[t0]; stop=max(stop,ts) if dirn>0 else min(stop,ts)
            if dirn>0:
                if lo[j]<=stop: ex=stop;xi=j;break
                if tgt is not None and hi[j]>=tgt: ex=tgt;xi=j;break
            else:
                if hi[j]>=stop: ex=stop;xi=j;break
                if tgt is not None and lo[j]<=tgt: ex=tgt;xi=j;break
        if ex is None: xi=min(ei+to,n-1); ex=cl[xi]
        Rs.append((dirn*(ex-entry)-2*cost)/risk); eis.append(ei); last=xi
    return Rs,eis

def backtest(d,h,cfg=CFG):
    R,ei=_trades(d,h,cfg); return pd.DataFrame({'R':R,'ei':ei})

# analytic null: random entries with matched risk/RR (side, stop, exit)
_POOL={}
def _pool(d,h,cfg,npool=3000):
    ec=(h['side'],h['stop'],h['exit'],int(h['window'])); key=(len(d),round(float(d['close'].iloc[0]),1))+ec
    if key in _POOL: return _POOL[key]
    o=d['open'].values;hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;atr=d['m_atr'].values
    rmax=d['rmax20'].values; rmin=d['rmin20'].values
    valid=np.where(np.isfinite(atr)&(atr>0))[0]; valid=valid[(valid>2)&(valid<len(d)-2)]
    if len(valid)<50: _POOL[key]=np.array([]); return _POOL[key]
    rng=np.random.default_rng(cfg['seed']); ents=rng.choice(valid,size=min(npool,len(valid)),replace=False)
    dirn=-1 if h['side']=='high' else 1; cost=(cfg['spread_ticks']+cfg['slip_ticks'])*TICK; Rs=[]
    for i in ents:
        ei=i+1; entry=o[ei]
        if h['stop']=='beyond_sweep': stop=hi[i]+2*TICK if dirn<0 else lo[i]-2*TICK
        elif h['stop']=='atr': stop=entry-dirn*1.5*atr[i]
        else: stop=(rmax[ei]+2*TICK) if dirn<0 else (rmin[ei]-2*TICK)
        risk=abs(entry-stop)
        if risk<=0 or not np.isfinite(risk): continue
        rr=2 if h['exit']=='rr2' else 3 if h['exit']=='rr3' else 2
        tgt=entry+dirn*rr*risk; to=24 if h['exit']=='time' else 48; ex=None
        for j in range(ei,min(ei+to,len(d))):
            if dirn>0:
                if lo[j]<=stop: ex=stop;break
                if hi[j]>=tgt: ex=tgt;break
            else:
                if hi[j]>=stop: ex=stop;break
                if lo[j]<=tgt: ex=tgt;break
        if ex is None: ex=cl[min(ei+to,len(d)-1)]
        Rs.append((dirn*(ex-entry)-2*cost)/risk)
    _POOL[key]=np.array(Rs); return _POOL[key]

def analytic_p(d,h,obs_exp,k):
    pool=_pool(d,h,CFG)
    if k<CFG['MINTR'] or len(pool)<30: return 1.0
    mu=float(np.mean(pool)); sd=float(np.std(pool,ddof=1))
    if sd<=0: return 1.0
    z=(obs_exp-mu)/(sd/math.sqrt(k)); return max(0.5*math.erfc(z/math.sqrt(2)),1e-300)

"""MULTI-STRATEGY ALPHA DISCOVERY — common architecture.
ONE shared production backtester (simulate) + ONE feature set + ONE pipeline for ALL families.
Each family only provides: grammar() and setups(d,h)->list of setup dicts. The shared engine does
execution (entry@next-open, stop/target/timeout/trailing) identically for every family. Lookahead-safe.
Interface per trade in ledger: family, hypothesis_id, si(signal_ts idx), ei(entry_ts idx), entry_price,
stop, exit_price, R, dir. Global-FDR over the WHOLE campaign universe."""
import numpy as np, pandas as pd, itertools, hashlib, math
from alpha_lab import CFG
import s1 as _s1
TICK=0.1

# ---------------- shared features ----------------
def load():
    d=_s1.load_s1()  # M15 + H4/H1/D1 ctx + session + PDH/PDL + rmax/rmin20/50 + sess_high/low + FVG + disp + roc + bull/bear close + m_atr
    c=d['close']; h=d['high']; l=d['low']
    d['atr_ma']=d['m_atr'].rolling(50).mean()
    d['compress']=(d['m_atr']<0.8*d['atr_ma']).astype(float)
    # opening range: first 4 M15 bars high/low of each session block (shifted -> available after OR forms)
    g=d.groupby('blk')
    d['or_high']=g['high'].transform(lambda x: x.iloc[:4].max()); d['or_low']=g['low'].transform(lambda x: x.iloc[:4].min())
    d['bar_in_sess']=g.cumcount()
    # previous-session high/low (completed block), available from current session start
    bh=g['high'].max(); bl=g['low'].min()
    d['prev_sess_high']=d['blk'].map(bh.shift(1)); d['prev_sess_low']=d['blk'].map(bl.shift(1))
    # session VWAP (cumulative typical*vol / cumvol within block), lookahead-safe (running)
    tp=(h+l+c)/3; pv=tp*d['volume']
    d['vwap']=pv.groupby(d['blk']).cumsum()/d['volume'].groupby(d['blk']).cumsum().replace(0,np.nan)
    # prev-day open/close/mid (last-closed D1)
    d1=pd.read_csv(_s1.M.D+r"\OANDA_XAUUSD_D1.csv"); d1['avail']=d1['time'].shift(-1); d1.loc[d1.index[-1],'avail']=d1['time'].iloc[-1]+86400; d1['avail']=d1['avail'].astype('int64')
    d=pd.merge_asof(d.sort_values('time'),d1[['avail','open','close']].rename(columns={'open':'pd_open','close':'pd_close'}).sort_values('avail'),left_on='time',right_on='avail',direction='backward').drop(columns='avail')
    d['pd_mid']=(d['pdh']+d['pdl'])/2
    # prev-week high/low (weekly resample of D1, last-closed)
    w=pd.read_csv(_s1.M.D+r"\OANDA_XAUUSD_D1.csv"); w['dt']=pd.to_datetime(w['time'],unit='s',utc=True)
    wk=w.set_index('dt').resample('W').agg(high=('high','max'),low=('low','min')).dropna().reset_index()
    wk['avail']=((wk['dt']-pd.Timestamp('1970-01-01',tz='UTC'))//pd.Timedelta(seconds=1)).astype('int64')  # week-end ~ availability
    d=pd.merge_asof(d.sort_values('time'),wk[['avail','high','low']].rename(columns={'high':'pw_high','low':'pw_low'}).sort_values('avail'),left_on='time',right_on='avail',direction='backward').drop(columns='avail')
    # prev-session close + gap (at session start)
    d['prev_sess_close']=d['blk'].map(g['close'].last().shift(1))
    d['gap']=np.where(d['bar_in_sess']==0, d['open']-d['prev_sess_close'], np.nan)
    return d.reset_index(drop=True)

# ---------------- shared backtester (production engine) ----------------
def simulate(d,setups,cfg=CFG):
    o=d['open'].values;hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;atr=d['m_atr'].values
    n=len(d); cost=(cfg['spread_ticks']+cfg['slip_ticks'])*TICK
    Rs=[];sis=[];eis=[];last=-1
    for s in sorted(setups,key=lambda x:x['ei']):
        ei=s['ei']; si=s['si']
        if ei<=last or ei>=n-1 or ei<1: continue
        dirn=s['dir']; entry=o[ei]; stop=s['stop']; risk=abs(entry-stop)
        if not np.isfinite(risk) or np.isnan(atr[si]) or atr[si]<=0: continue
        # ENGINE v2 pre-registered stop-floor: executable_stop = max(strategy_stop, min_executable_risk)
        min_exec=max(2*cfg['spread_ticks']*TICK, 5*TICK, 0.10*atr[si])
        widened=False
        if risk<min_exec: risk=min_exec; stop=entry-dirn*risk; widened=True    # widen tiny stop to executable floor
        if risk<=0: continue
        ek=s['exit_kind']; ep=s.get('exit_param'); trail=(ek=='trailing')
        to=int(ep) if ek=='time' else 48
        if ek=='rr': tgt=entry+dirn*ep*risk
        elif ek in ('opp_liq','opp_struct'): tgt=ep
        else: tgt=None
        best=entry; ex=None; xi=None; tfirst=cfg.get('target_first', False)   # target_first = MEASUREMENT toggle (best-case bracket); default False = pre-registered stop-first worst-case
        for j in range(ei,min(ei+to,n)):
            if trail:
                best=max(best,hi[j]) if dirn>0 else min(best,lo[j]); ts=best-dirn*1.5*atr[si]
                stop=max(stop,ts) if dirn>0 else min(stop,ts)
            hitS = (lo[j]<=stop) if dirn>0 else (hi[j]>=stop)
            hitT = (tgt is not None and np.isfinite(tgt)) and ((hi[j]>=tgt) if dirn>0 else (lo[j]<=tgt))
            if tfirst:
                if hitT: ex=tgt;xi=j;break
                if hitS: ex=stop;xi=j;break
            else:
                if hitS: ex=stop;xi=j;break
                if hitT: ex=tgt;xi=j;break
        if ex is None: xi=min(ei+to,n-1); ex=cl[xi]
        # WP-1 INVALID-EXECUTION (D2, docs/MIN_STOP_FLOOR_PREREG): a FLOORED (widened) trade that resolves on
        # its own entry bar = gap-through-floored-stop-at-entry / same-bar ambiguous fill -> excluded, not
        # counted (still advances overlap cursor). Scoped to widened trades so the ATR regime (0 widened) is
        # provably unchanged. Toggle cfg['mark_invalid'] (default True) reproduces the pre-D2 baseline when False.
        if cfg.get('mark_invalid', True) and widened and xi==ei:
            last=xi; continue
        Rs.append((dirn*(ex-entry)-2*cost)/risk); sis.append(si); eis.append(ei); last=xi
    return pd.DataFrame({'R':Rs,'si':sis,'ei':eis})

def simulate_ref(d,setups,cfg=CFG):
    """independent reference re-implementation for PARITY audit (no trailing/opp for simplicity of the
    subset it audits — used only on rr/time setups)."""
    o=d['open'].values;hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;atr=d['m_atr'].values; n=len(d)
    cost=(cfg['spread_ticks']+cfg['slip_ticks'])*TICK; out=[]; last=-1
    for s in sorted(setups,key=lambda x:x['ei']):
        ei=s['ei']
        if ei<=last or ei>=n-1 or ei<1: continue
        dirn=s['dir']; entry=o[ei]; stop=s['stop']; risk=abs(entry-stop)
        if not np.isfinite(risk): continue
        min_exec=max(2*cfg['spread_ticks']*TICK, 5*TICK, 0.10*atr[s['si']]) if not np.isnan(atr[s['si']]) else 5*TICK
        widened=False
        if risk<min_exec: risk=min_exec; stop=entry-dirn*risk; widened=True
        if risk<=0: continue
        ek=s['exit_kind']; ep=s.get('exit_param'); to=int(ep) if ek=='time' else 48
        tgt=entry+dirn*ep*risk if ek=='rr' else (ep if ek in('opp_liq','opp_struct') else None)
        ex=None; xi=None
        for j in range(ei,min(ei+to,n)):
            hitS = (lo[j]<=stop) if dirn>0 else (hi[j]>=stop)
            hitT = (tgt is not None and np.isfinite(tgt)) and ((hi[j]>=tgt) if dirn>0 else (lo[j]<=tgt))
            if hitS: ex=stop;xi=j;break
            if hitT: ex=tgt;xi=j;break
        if ex is None: xi=min(ei+to,n-1); ex=cl[xi]
        # WP-1 INVALID-EXECUTION (identical rule to simulate, for parity)
        if cfg.get('mark_invalid', True) and widened and xi==ei:
            last=xi; continue
        out.append((dirn*(ex-entry)-2*cost)/risk); last=xi
    return np.array(out)

# ---------------- analytic null (shared): random entries matched to (dir, exit) ----------------
_POOL={}
def _pool(d,dirn,ek,ep,cfg,npool=2500):
    key=(len(d),round(float(d['close'].iloc[0]),1),dirn,ek,ep)
    if key in _POOL: return _POOL[key]
    o=d['open'].values;hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;atr=d['m_atr'].values
    valid=np.where(np.isfinite(atr)&(atr>0))[0]; valid=valid[(valid>2)&(valid<len(d)-2)]
    if len(valid)<50: _POOL[key]=np.array([]); return _POOL[key]
    rng=np.random.default_rng(cfg['seed']); ents=rng.choice(valid,size=min(npool,len(valid)),replace=False)
    cost=(cfg['spread_ticks']+cfg['slip_ticks'])*TICK; rr=ep if ek=='rr' else 2; to=int(ep) if ek=='time' else 48; Rs=[]
    for i in ents:
        ei=i+1; entry=o[ei]; stop=entry-dirn*1.5*atr[i]; risk=abs(entry-stop)
        if risk<=0: continue
        tgt=entry+dirn*rr*risk; ex=None
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

def analytic_p(d,setups,obs_exp,k):
    if k<CFG['MINTR'] or not setups: return 1.0
    s0=setups[0]; pool=_pool(d,s0['dir'],s0['exit_kind'],s0.get('exit_param'),CFG)
    if len(pool)<30: return 1.0
    mu=float(np.mean(pool)); sd=float(np.std(pool,ddof=1))
    if sd<=0: return 1.0
    z=(obs_exp-mu)/(sd/math.sqrt(k)); return max(0.5*math.erfc(z/math.sqrt(2)),1e-300)

# ==================== FAMILIES (setups providers) ====================
def _exitmap(exit_kind,dirn,refL,refH,ei,rmax,rmin):
    if exit_kind=='rr2': return ('rr',2.0)
    if exit_kind=='rr3': return ('rr',3.0)
    if exit_kind=='time': return ('time',24)
    if exit_kind=='trailing': return ('trailing',None)
    if exit_kind=='opp_liq': return ('opp_liq', refL[ei] if dirn<0 else refH[ei])
    if exit_kind=='opp_struct': return ('opp_struct', rmin[ei] if dirn<0 else rmax[ei])
    return ('rr',2.0)

def _grid(family,dims):
    keys=list(dims); seen=set(); out=[]
    for combo in itertools.product(*[dims[k] for k in keys]):
        h=dict(zip(keys,combo)); h['family']=family
        key=tuple(sorted(h.items())); hid=hashlib.md5((family+str(key)).encode()).hexdigest()[:12]
        if hid in seen: continue
        seen.add(hid); h['id']=hid; out.append(h)
    return out

# ---- S1 Liquidity Sweep Reversal ----
S1_DIMS=dict(side=['high','low'],liq_ref=['swing','session','pdh_pdl'],liq_lb=[20,50],
             confirm=['consecutive2','close_beyond','displacement'],imb=['none','fvg'],
             stop=['beyond_sweep','structural'],exit=['rr2','rr3','opp_liq','time'],window=[4,8])
def s1_grammar(): return _grid('S1',S1_DIMS)
def s1_setups(d,h):
    hi=d['high'].values;lo=d['low'].values;cl=d['close'].values
    rmax=d['rmax20'].values;rmin=d['rmin20'].values;fb=d['fvg_bull'].values;fr=d['fvg_bear'].values
    disp=d['disp'].values;bc=d['bear_close'].values;uc=d['bull_close'].values
    lb=int(h['liq_lb']) if h['liq_ref']=='swing' else 20
    if h['liq_ref']=='swing': refH=d[f'rmax{lb}'].values; refL=d[f'rmin{lb}'].values
    elif h['liq_ref']=='session': refH=d['sess_high'].values; refL=d['sess_low'].values
    else: refH=d['pdh'].values; refL=d['pdl'].values
    side=h['side']; dirn=-1 if side=='high' else 1; W=int(h['window']); n=len(d)
    sweep=((hi>refH)&(cl<refH)&np.isfinite(refH)) if side=='high' else ((lo<refL)&(cl>refL)&np.isfinite(refL))
    out=[]
    for t0 in np.flatnonzero(sweep):
        conf=None
        for t1 in range(t0+1,min(t0+W+1,n)):
            k=h['confirm']
            ok=(disp[t1]>0 and ((bc[t1]>0) if dirn<0 else (uc[t1]>0))) if k=='displacement' else \
               ((cl[t1]<refL[t1]) if dirn<0 else (cl[t1]>refH[t1])) if k=='close_beyond' else \
               ((bc[t1]>0 and bc[t1-1]>0) if dirn<0 else (uc[t1]>0 and uc[t1-1]>0))
            if ok: conf=t1;break
        if conf is None: continue
        if h['imb']=='fvg':
            has=(fr[t0:conf+1].any()) if dirn<0 else (fb[t0:conf+1].any())
            if not has: continue
        ei=conf+1
        stop=(hi[t0]+2*TICK) if dirn<0 else (lo[t0]-2*TICK)
        if h['stop']=='structural': stop=(rmax[ei]+2*TICK) if dirn<0 else (rmin[ei]-2*TICK)
        ek,ep=_exitmap(h['exit'],dirn,refL,refH,ei,rmax,rmin)
        out.append(dict(si=t0,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out

# ---- S2 Failed Breakout / Failed Sweep (contrarian back into range) ----
S2_DIMS=dict(ref=['swing','session','pdh_pdl'],lb=[20,50],fail_within=[2,4],
             stop=['beyond_ext','atr'],exit=['rr2','opp_liq','time'],side=['high','low'])
def s2_grammar(): return _grid('S2',S2_DIMS)
def s2_setups(d,h):
    hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;o=d['open'].values;atr=d['m_atr'].values
    rmax=d['rmax20'].values;rmin=d['rmin20'].values; lb=int(h['lb']) if h['ref']=='swing' else 20
    if h['ref']=='swing': refH=d[f'rmax{lb}'].values; refL=d[f'rmin{lb}'].values
    elif h['ref']=='session': refH=d['sess_high'].values; refL=d['sess_low'].values
    else: refH=d['pdh'].values; refL=d['pdl'].values
    side=h['side']; dirn=-1 if side=='high' else 1; W=int(h['fail_within']); n=len(d)
    # break = CLOSE beyond level; then FAIL (close back inside within W) -> contrarian (selective)
    brk=((cl>refH)&np.isfinite(refH)) if side=='high' else ((cl<refL)&np.isfinite(refL))
    out=[]
    for t0 in np.flatnonzero(brk):
        fail=None
        for t1 in range(t0+1,min(t0+W+1,n)):
            if (side=='high' and cl[t1]<refH[t0]) or (side=='low' and cl[t1]>refL[t0]): fail=t1;break
        if fail is None: continue
        ei=fail+1
        if ei>=n-1 or np.isnan(atr[t0]): continue
        ext=hi[t0] if side=='high' else lo[t0]
        stop=(ext+2*TICK) if dirn<0 else (ext-2*TICK)
        if h['stop']=='atr': stop=o[ei]-dirn*1.5*atr[t0]
        ek,ep=_exitmap(h['exit'],dirn,refL,refH,ei,rmax,rmin)
        out.append(dict(si=t0,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out

# ---- S3 Breakout Retest Continuation ----
S3_DIMS=dict(ref=['swing','session'],lb=[20,50],retest_within=[4,8],
             stop=['beyond_level','atr'],exit=['rr2','rr3','trailing'],side=['up','down'])
def s3_grammar(): return _grid('S3',S3_DIMS)
def s3_setups(d,h):
    hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;o=d['open'].values;atr=d['m_atr'].values
    rmax=d['rmax20'].values;rmin=d['rmin20'].values; lb=int(h['lb'])
    if h['ref']=='swing': refH=d[f'rmax{lb}'].values; refL=d[f'rmin{lb}'].values
    else: refH=d['sess_high'].values; refL=d['sess_low'].values
    up=(h['side']=='up'); dirn=1 if up else -1; W=int(h['retest_within']); n=len(d)
    brk=((cl>refH)&np.isfinite(refH)) if up else ((cl<refL)&np.isfinite(refL))
    out=[]
    for t0 in np.flatnonzero(brk):
        lvl=refH[t0] if up else refL[t0]; rt=None
        for t1 in range(t0+1,min(t0+W+1,n)):
            if (up and lo[t1]<=lvl) or ((not up) and hi[t1]>=lvl): rt=t1;break
        if rt is None: continue
        ei=rt+1
        if ei>=n-1 or np.isnan(atr[t0]): continue
        stop=(lvl-2*TICK) if up else (lvl+2*TICK)
        if h['stop']=='atr': stop=o[ei]-dirn*1.5*atr[t0]
        ek,ep=_exitmap(h['exit'],dirn,refL,refH,ei,rmax,rmin)
        out.append(dict(si=t0,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out

# ---- S4 Volatility Compression Expansion ----
S4_DIMS=dict(exp_k=[1.5,2.0],stop=['bar','atr'],exit=['rr2','rr3','trailing','time'],min_compress=[1,3])
def s4_grammar(): return _grid('S4',S4_DIMS)
def s4_setups(d,h):
    hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;o=d['open'].values;atr=d['m_atr'].values
    comp=d['compress'].values; rmax=d['rmax20'].values;rmin=d['rmin20'].values; n=len(d); k=h['exp_k']; mc=int(h['min_compress'])
    rng=hi-lo
    out=[]
    for t in range(mc+1,n-1):
        if not np.isfinite(atr[t]) or atr[t]<=0: continue
        if comp[t-1-mc:t].sum()<mc: continue          # prior compression
        if rng[t]>k*atr[t]:                             # expansion bar
            dirn=1 if cl[t]>o[t] else -1; ei=t+1
            stop=(lo[t]-2*TICK) if dirn>0 else (hi[t]+2*TICK)
            if h['stop']=='atr': stop=o[ei]-dirn*1.5*atr[t]
            ek,ep=_exitmap(h['exit'],dirn,rmin,rmax,ei,rmax,rmin)
            out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out

# ---- S5 Opening Range Breakout ----
S5_DIMS=dict(session=['asia','london','ny'],mode=['breakout','retest'],stop=['or_opp','atr'],
             exit=['rr2','rr3','opp_liq','time'],side=['up','down'])
def s5_grammar(): return _grid('S5',S5_DIMS)
def s5_setups(d,h):
    hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;o=d['open'].values;atr=d['m_atr'].values
    orh=d['or_high'].values;orl=d['or_low'].values;bis=d['bar_in_sess'].values;sess=d['session'].values
    rmax=d['rmax20'].values;rmin=d['rmin20'].values; up=(h['side']=='up'); dirn=1 if up else -1; n=len(d)
    inS=(sess==h['session']); out=[]
    for t in range(1,n-1):
        if not inS[t] or bis[t]<4 or bis[t]>20: continue  # after OR formed, within session
        brk=(cl[t]>orh[t]) if up else (cl[t]<orl[t])
        if not brk or np.isnan(atr[t]): continue
        ei=t+1
        stop=(orl[t]-2*TICK) if up else (orh[t]+2*TICK)
        if h['stop']=='atr': stop=o[ei]-dirn*1.5*atr[t]
        ek,ep=_exitmap(h['exit'],dirn,rmin,rmax,ei,rmax,rmin)
        out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out

# ---- S6 Session Transition ----
S6_DIMS=dict(session=['london','ny'],mode=['breakout','fade'],side=['up','down'],stop=['prev_ext','atr'],exit=['rr2','time'])
def s6_grammar(): return _grid('S6',S6_DIMS)
def s6_setups(d,h):
    hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;o=d['open'].values;atr=d['m_atr'].values
    ph=d['prev_sess_high'].values;pl=d['prev_sess_low'].values;bis=d['bar_in_sess'].values;sess=d['session'].values
    rmax=d['rmax20'].values;rmin=d['rmin20'].values; up=(h['side']=='up'); dirn=1 if up else -1; n=len(d)
    inS=(sess==h['session']); out=[]
    for t in range(1,n-1):
        if not inS[t] or bis[t]>10 or not np.isfinite(ph[t]) or np.isnan(atr[t]): continue
        lvl=ph[t] if up else pl[t]
        cross=(cl[t]>lvl) if up else (cl[t]<lvl)
        take = cross if h['mode']=='breakout' else (not cross and ((hi[t]>=lvl) if up else (lo[t]<=lvl)))
        if h['mode']=='fade': dirn2=-dirn
        else: dirn2=dirn
        if not take: continue
        ei=t+1; stop=(lvl-2*TICK) if dirn2>0 else (lvl+2*TICK)
        if h['stop']=='atr': stop=o[ei]-dirn2*1.5*atr[t]
        ek,ep=_exitmap(h['exit'],dirn2,rmin,rmax,ei,rmax,rmin)
        out.append(dict(si=t,ei=ei,dir=dirn2,stop=stop,exit_kind=ek,exit_param=ep))
    return out

# ---- S7 Trend Pullback (HTF trend -> LTF pullback to EMA -> continuation) ----
S7_DIMS=dict(htf=['h4','h1'],stop=['ema','atr'],exit=['rr2','rr3','trailing'],pb_within=[4,8])
def s7_grammar(): return _grid('S7',S7_DIMS)
def s7_setups(d,h):
    cl=d['close'].values;o=d['open'].values;atr=d['m_atr'].values;ema=d['m_ema20'].values
    tr=d[h['htf']+'_trend_up'].values; n=len(d); W=int(h['pb_within']); rmax=d['rmax20'].values;rmin=d['rmin20'].values
    out=[]; t=1
    while t<n-1:
        up=tr[t]>0.5; dirn=1 if up else -1
        pulled=(cl[t]<ema[t]) if up else (cl[t]>ema[t])
        if pulled and np.isfinite(atr[t]) and atr[t]>0:
            conf=None
            for t1 in range(t+1,min(t+W+1,n)):
                if (up and cl[t1]>ema[t1]) or ((not up) and cl[t1]<ema[t1]): conf=t1;break
            if conf is not None:
                ei=conf+1; stop=(ema[ei]-2*TICK) if up else (ema[ei]+2*TICK)
                if h['stop']=='atr': stop=o[ei]-dirn*1.5*atr[conf]
                ek,ep=_exitmap(h['exit'],dirn,rmin,rmax,ei,rmax,rmin)
                out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep)); t=conf+1; continue
        t+=1
    return out

# ---- S8 Mean Reversion (extreme extension vs ref -> revert) ----
S8_DIMS=dict(ref=['sma','vwap'],k=[2.0,3.0],side=['up','down'],stop=['atr','ext'],exit=['rr2','opp_liq','time'])
def s8_grammar(): return _grid('S8',S8_DIMS)
def s8_setups(d,h):
    cl=d['close'].values;o=d['open'].values;hi=d['high'].values;lo=d['low'].values;atr=d['m_atr'].values
    ref=d['m_sma'].values if h['ref']=='sma' else d['vwap'].values
    rmax=d['rmax20'].values;rmin=d['rmin20'].values; up=(h['side']=='up'); dirn=1 if up else -1; n=len(d); k=h['k']
    ext = ((cl - ref) < -k*atr) if up else ((cl - ref) > k*atr)   # far below(long) / above(short)
    extp=np.concatenate([[False],ext[:-1]]); onset=ext & ~extp     # only the ONSET of extension (selective)
    out=[]
    for t in np.flatnonzero(onset & np.isfinite(ref) & np.isfinite(atr) & (atr>0)):
        if t>=n-1: continue
        ei=t+1; stop=o[ei]-dirn*1.5*atr[t]
        if h['stop']=='ext': stop=(lo[t]-2*TICK) if up else (hi[t]+2*TICK)
        ek,ep=_exitmap(h['exit'],dirn,rmin,rmax,ei,rmax,rmin)
        if ek=='opp_liq': ep=ref[ei]   # revert to the reference (equilibrium) as target
        out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=('opp_liq' if h['exit']=='opp_liq' else ek),exit_param=ep))
    return out

# ---- S9 Multi-Timeframe Alignment (4H trend + 1H confirm + 15M breakout trigger) ----
S9_DIMS=dict(c4h=['up','down'],conf1h=['align','any'],lb=[10,20],stop=['atr','structural'],exit=['rr2','rr3'])
def s9_grammar(): return _grid('S9',S9_DIMS)
def s9_setups(d,h):
    c=d['close']; cl=c.values;o=d['open'].values;atr=d['m_atr'].values
    h4=d['h4_trend_up'].values; h1=d['h1_trend_up'].values; rmax=d['rmax20'].values;rmin=d['rmin20'].values
    up=(h['c4h']=='up'); dirn=1 if up else -1; lb=int(h['lb']); n=len(d)
    roll=(c.rolling(lb).max().shift(1).values) if up else (c.rolling(lb).min().shift(1).values)
    ctx=(h4>0.5) if up else (h4<=0.5)
    if h['conf1h']=='align': ctx=ctx & ((h1>0.5) if up else (h1<=0.5))
    trig=(cl>roll) if up else (cl<roll)
    trigp=np.concatenate([[False],trig[:-1]]); trig=trig & ~trigp   # ONSET of breakout only (selective)
    sig=trig & ctx & np.isfinite(roll) & np.isfinite(atr) & (atr>0)
    out=[]
    for t in np.flatnonzero(sig):
        if t>=n-1: continue
        ei=t+1; stop=o[ei]-dirn*1.5*atr[t]
        if h['stop']=='structural': stop=(rmin[ei]-2*TICK) if up else (rmax[ei]+2*TICK)
        ek,ep=_exitmap(h['exit'],dirn,rmin,rmax,ei,rmax,rmin)
        out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out

# ---- S10 Displacement Continuation ----
S10_DIMS=dict(disp_k=[1.5,2.0],pb=[2,4],side=['up','down'],stop=['bar','atr'],exit=['rr2','rr3','trailing'])
def s10_grammar(): return _grid('S10',S10_DIMS)
def s10_setups(d,h):
    hi=d['high'].values;lo=d['low'].values;cl=d['close'].values;o=d['open'].values;atr=d['m_atr'].values
    rng=hi-lo; rmax=d['rmax20'].values;rmin=d['rmin20'].values; up=(h['side']=='up'); dirn=1 if up else -1; n=len(d); k=h['disp_k']; W=int(h['pb'])
    disp=(rng>k*atr) & (((cl>o)) if up else ((cl<o)))
    out=[]
    for t0 in np.flatnonzero(disp & np.isfinite(atr) & (atr>0)):
        # controlled pullback then continuation entry
        ei=None
        for t1 in range(t0+1,min(t0+W+1,n)):
            if (up and lo[t1]<=cl[t0]) or ((not up) and hi[t1]>=cl[t0]): ei=t1+1; break
        if ei is None or ei>=n-1: continue
        stop=(lo[t0]-2*TICK) if up else (hi[t0]+2*TICK)
        if h['stop']=='atr': stop=o[ei]-dirn*1.5*atr[t0]
        ek,ep=_exitmap(h['exit'],dirn,rmin,rmax,ei,rmax,rmin)
        out.append(dict(si=t0,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out

def _onset(mask): p=np.concatenate([[False],mask[:-1]]); return mask & ~p
# S11 Structure Break Reversal (CHoCH: HTF trend + break of opposite swing -> reversal)
S11_DIMS=dict(htf=['h4','h1'],lb=[20,50],stop=['struct','atr'],exit=['rr2','rr3','time'])
def s11_grammar(): return _grid('S11',S11_DIMS)
def s11_setups(d,h):
    cl=d['close'].values;o=d['open'].values;atr=d['m_atr'].values; tr=d[h['htf']+'_trend_up'].values; lb=int(h['lb'])
    rmax=d[f'rmax{lb}'].values;rmin=d[f'rmin{lb}'].values;r20x=d['rmax20'].values;r20n=d['rmin20'].values;n=len(d)
    up=tr>0.5; brk=_onset(np.where(up,cl<rmin,cl>rmax)&np.isfinite(rmin)); out=[]
    for t in np.flatnonzero(brk):
        if t>=n-1 or np.isnan(atr[t]) or atr[t]<=0: continue
        dirn=-1 if up[t] else 1; ei=t+1; stop=(r20x[ei]+2*TICK) if dirn<0 else (r20n[ei]-2*TICK)
        if h['stop']=='atr': stop=o[ei]-dirn*1.5*atr[t]
        ek,ep=_exitmap(h['exit'],dirn,r20n,r20x,ei,r20x,r20n); out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out
# S12 Range Rotation (extreme -> rejection -> rotate)
S12_DIMS=dict(lb=[20,50],target=['center','opp'],side=['up','down'],stop=['ext','atr'],exit=['rr2','opp_liq','time'])
def s12_grammar(): return _grid('S12',S12_DIMS)
def s12_setups(d,h):
    cl=d['close'].values;o=d['open'].values;hi=d['high'].values;lo=d['low'].values;atr=d['m_atr'].values;lb=int(h['lb'])
    rmax=d[f'rmax{lb}'].values;rmin=d[f'rmin{lb}'].values;r20x=d['rmax20'].values;r20n=d['rmin20'].values;n=len(d)
    up=(h['side']=='up'); dirn=1 if up else -1
    at_ext=_onset((lo<=rmin*1.001) if up else (hi>=rmax*0.999)); out=[]
    for t in np.flatnonzero(at_ext & np.isfinite(rmin) & np.isfinite(atr) & (atr>0)):
        if t>=n-1: continue
        ei=t+1; stop=(rmin[t]-2*TICK) if up else (rmax[t]+2*TICK)
        if h['stop']=='atr': stop=o[ei]-dirn*1.5*atr[t]
        ek,ep=_exitmap('opp_liq' if h['exit']=='opp_liq' else h['exit'],dirn,r20n,r20x,ei,r20x,r20n)
        if h['target']=='center': ek,ep=('rr',1.5) if h['exit']!='time' else ('time',24)
        out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out
# S13 Imbalance Fill (FVG -> fill -> reaction/continuation)
S13_DIMS=dict(fvg=['bull','bear'],mode=['revert','continue'],stop=['atr','struct'],exit=['rr2','rr3','time'])
def s13_grammar(): return _grid('S13',S13_DIMS)
def s13_setups(d,h):
    cl=d['close'].values;o=d['open'].values;atr=d['m_atr'].values;r20x=d['rmax20'].values;r20n=d['rmin20'].values
    fvg=d['fvg_bull'].values if h['fvg']=='bull' else d['fvg_bear'].values; n=len(d); ev=_onset(fvg>0.5); out=[]
    for t in np.flatnonzero(ev):
        if t>=n-1 or np.isnan(atr[t]) or atr[t]<=0: continue
        base=1 if h['fvg']=='bull' else -1; dirn= base if h['mode']=='continue' else -base
        ei=t+1; stop=o[ei]-dirn*1.5*atr[t]
        if h['stop']=='struct': stop=(r20n[ei]-2*TICK) if dirn>0 else (r20x[ei]+2*TICK)
        ek,ep=_exitmap(h['exit'],dirn,r20n,r20x,ei,r20x,r20n); out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out
# S14 Momentum Exhaustion (accel then stall -> reversal)
S14_DIMS=dict(roc_k=[0.004,0.008],side=['up','down'],stop=['atr','bar'],exit=['rr2','time'])
def s14_grammar(): return _grid('S14',S14_DIMS)
def s14_setups(d,h):
    c=d['close'];cl=c.values;o=d['open'].values;hi=d['high'].values;lo=d['low'].values;atr=d['m_atr'].values
    roc=(c/c.shift(3)-1).values; r20x=d['rmax20'].values;r20n=d['rmin20'].values;n=len(d); up=(h['side']=='up'); dirn=1 if up else -1;k=h['roc_k']
    # exhaustion of a down-move => long (up); accel down then stall (roc recovers)
    accel=(roc< -k) if up else (roc> k); stall=np.concatenate([[False],(np.abs(roc[1:])<np.abs(roc[:-1]))])
    ev=_onset(accel & stall); out=[]
    for t in np.flatnonzero(ev & np.isfinite(atr) & (atr>0)):
        if t>=n-1: continue
        ei=t+1; stop=o[ei]-dirn*1.5*atr[t]
        if h['stop']=='bar': stop=(lo[t]-2*TICK) if up else (hi[t]+2*TICK)
        ek,ep=_exitmap(h['exit'],dirn,r20n,r20x,ei,r20x,r20n); out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out
# S15 Trend Acceleration (trend + vol/mom expansion -> continuation)
S15_DIMS=dict(htf=['h4','h1'],exp_k=[1.5,2.0],stop=['atr','struct'],exit=['rr2','rr3','trailing'])
def s15_grammar(): return _grid('S15',S15_DIMS)
def s15_setups(d,h):
    cl=d['close'].values;o=d['open'].values;hi=d['high'].values;lo=d['low'].values;atr=d['m_atr'].values
    tr=d[h['htf']+'_trend_up'].values; rng=hi-lo; r20x=d['rmax20'].values;r20n=d['rmin20'].values;n=len(d);k=h['exp_k']
    up=tr>0.5; exp=_onset((rng>k*atr)&(np.where(up,cl>o,cl<o))); out=[]
    for t in np.flatnonzero(exp & np.isfinite(atr) & (atr>0)):
        if t>=n-1: continue
        dirn=1 if up[t] else -1; ei=t+1; stop=o[ei]-dirn*1.5*atr[t]
        if h['stop']=='struct': stop=(r20n[ei]-2*TICK) if dirn>0 else (r20x[ei]+2*TICK)
        ek,ep=_exitmap(h['exit'],dirn,r20n,r20x,ei,r20x,r20n); out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out
# S16 Previous Day Levels
S16_DIMS=dict(level=['pdh','pdl','pd_open','pd_close','pd_mid'],mode=['breakout','reject'],stop=['atr','level'],exit=['rr2','time'])
def s16_grammar(): return _grid('S16',S16_DIMS)
def s16_setups(d,h):
    cl=d['close'].values;o=d['open'].values;hi=d['high'].values;lo=d['low'].values;atr=d['m_atr'].values
    lv=d[h['level']].values; r20x=d['rmax20'].values;r20n=d['rmin20'].values;n=len(d)
    cross_up=_onset((cl>lv)&np.isfinite(lv)); out=[]
    ev = cross_up if h['mode']=='breakout' else _onset((hi>=lv)&(cl<lv)&np.isfinite(lv))  # reject from above
    for t in np.flatnonzero(ev):
        if t>=n-1 or np.isnan(atr[t]) or atr[t]<=0: continue
        dirn=1 if h['mode']=='breakout' else -1; ei=t+1
        stop=o[ei]-dirn*1.5*atr[t]
        if h['stop']=='level': stop=(lv[t]-2*TICK) if dirn>0 else (lv[t]+2*TICK)
        ek,ep=_exitmap(h['exit'],dirn,r20n,r20x,ei,r20x,r20n); out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out
# S17 Weekly Levels
S17_DIMS=dict(level=['pw_high','pw_low'],mode=['breakout','reject'],stop=['atr','level'],exit=['rr2','rr3','time'])
def s17_grammar(): return _grid('S17',S17_DIMS)
def s17_setups(d,h):
    cl=d['close'].values;o=d['open'].values;hi=d['high'].values;lo=d['low'].values;atr=d['m_atr'].values
    lv=d[h['level']].values; r20x=d['rmax20'].values;r20n=d['rmin20'].values;n=len(d)
    ev=_onset((cl>lv)&np.isfinite(lv)) if h['mode']=='breakout' else _onset((hi>=lv)&(cl<lv)&np.isfinite(lv)); out=[]
    for t in np.flatnonzero(ev):
        if t>=n-1 or np.isnan(atr[t]) or atr[t]<=0: continue
        dirn=1 if h['mode']=='breakout' else -1; ei=t+1; stop=o[ei]-dirn*1.5*atr[t]
        if h['stop']=='level': stop=(lv[t]-2*TICK) if dirn>0 else (lv[t]+2*TICK)
        ek,ep=_exitmap(h['exit'],dirn,r20n,r20x,ei,r20x,r20n); out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out
# S18 Time-of-Day Edge (enter at a fixed hour, directional)
S18_DIMS=dict(hour=[0,7,8,13,14,20],side=['up','down'],stop=['atr'],exit=['rr2','time'])
def s18_grammar(): return _grid('S18',S18_DIMS)
def s18_setups(d,h):
    o=d['open'].values;atr=d['m_atr'].values; hh=pd.to_datetime(d['time'],unit='s',utc=True).dt.hour.values; mm=pd.to_datetime(d['time'],unit='s',utc=True).dt.minute.values
    r20x=d['rmax20'].values;r20n=d['rmin20'].values; up=(h['side']=='up'); dirn=1 if up else -1; n=len(d)
    ev=(hh==h['hour'])&(mm==0); out=[]
    for t in np.flatnonzero(ev):
        if t>=n-1 or np.isnan(atr[t]) or atr[t]<=0: continue
        ei=t+1; stop=o[ei]-dirn*1.5*atr[t]
        ek,ep=_exitmap(h['exit'],dirn,r20n,r20x,ei,r20x,r20n); out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out
# S19 Session Gap (gap -> fill or continuation)
S19_DIMS=dict(gap_dir=['up','down'],mode=['fill','continue'],stop=['atr'],exit=['rr2','opp_liq','time'])
def s19_grammar(): return _grid('S19',S19_DIMS)
def s19_setups(d,h):
    o=d['open'].values;atr=d['m_atr'].values; gap=d['gap'].values; pc=d['prev_sess_close'].values
    r20x=d['rmax20'].values;r20n=d['rmin20'].values; n=len(d); gu=(h['gap_dir']=='up')
    ev=(np.isfinite(gap))&((gap>0.5*atr) if gu else (gap< -0.5*atr)); out=[]
    for t in np.flatnonzero(ev):
        if t>=n-1 or np.isnan(atr[t]) or atr[t]<=0: continue
        # gap up: fill=short(back to prev close), continue=long
        dirn=(-1 if gu else 1) if h['mode']=='fill' else (1 if gu else -1); ei=t+1; stop=o[ei]-dirn*1.5*atr[t]
        ek,ep=_exitmap('opp_liq' if h['exit']=='opp_liq' else h['exit'],dirn,r20n,r20x,ei,r20x,r20n)
        if h['exit']=='opp_liq' and h['mode']=='fill': ek,ep='opp_struct',pc[t]  # target prev close (gap fill)
        out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out
# S20 Hybrid (signal families combined, non-arbitrary): S9 MTF-trend context + S1-style sweep trigger
S20_DIMS=dict(ctx=['h4up','h4down'],trig=['sweep','breakout'],lb=[20,50],stop=['atr','struct'],exit=['rr2','rr3'])
def s20_grammar(): return _grid('S20',S20_DIMS)
def s20_setups(d,h):
    c=d['close'];cl=c.values;o=d['open'].values;hi=d['high'].values;lo=d['low'].values;atr=d['m_atr'].values
    h4=d['h4_trend_up'].values; lb=int(h['lb']); rmax=d[f'rmax{lb}'].values;rmin=d[f'rmin{lb}'].values;r20x=d['rmax20'].values;r20n=d['rmin20'].values;n=len(d)
    up=(h['ctx']=='h4up'); dirn=1 if up else -1; ctx=(h4>0.5) if up else (h4<=0.5)
    if h['trig']=='sweep': trig=((lo<rmin)&(cl>rmin)) if up else ((hi>rmax)&(cl<rmax))
    else: trig=_onset((cl>rmax) if up else (cl<rmin))
    sig=_onset(np.asarray(trig)) & ctx & np.isfinite(rmax) & np.isfinite(atr) & (atr>0); out=[]
    for t in np.flatnonzero(sig):
        if t>=n-1: continue
        ei=t+1; stop=o[ei]-dirn*1.5*atr[t]
        if h['stop']=='struct': stop=(r20n[ei]-2*TICK) if dirn>0 else (r20x[ei]+2*TICK)
        ek,ep=_exitmap(h['exit'],dirn,r20n,r20x,ei,r20x,r20n); out.append(dict(si=t,ei=ei,dir=dirn,stop=stop,exit_kind=ek,exit_param=ep))
    return out

REGISTRY={'S1':(s1_grammar,s1_setups),'S2':(s2_grammar,s2_setups),'S3':(s3_grammar,s3_setups),
          'S4':(s4_grammar,s4_setups),'S5':(s5_grammar,s5_setups),
          'S6':(s6_grammar,s6_setups),'S7':(s7_grammar,s7_setups),'S8':(s8_grammar,s8_setups),
          'S9':(s9_grammar,s9_setups),'S10':(s10_grammar,s10_setups),
          'S11':(s11_grammar,s11_setups),'S12':(s12_grammar,s12_setups),'S13':(s13_grammar,s13_setups),
          'S14':(s14_grammar,s14_setups),'S15':(s15_grammar,s15_setups),'S16':(s16_grammar,s16_setups),
          'S17':(s17_grammar,s17_setups),'S18':(s18_grammar,s18_setups),'S19':(s19_grammar,s19_setups),
          'S20':(s20_grammar,s20_setups)}
def backtest(d,h):
    return simulate(d, REGISTRY[h['family']][1](d,h), CFG)

_NB={'S1':('window',[4,8]),'S2':('fail_within',[2,4]),'S3':('retest_within',[4,8]),
     'S4':('exp_k',[1.5,2.0]),'S5':None,'S6':None,'S7':('pb_within',[4,8]),
     'S8':('k',[2.0,3.0]),'S9':('lb',[10,20]),'S10':('pb',[2,4]),
     'S11':('lb',[20,50]),'S12':('lb',[20,50]),'S13':None,'S14':('roc_k',[0.004,0.008]),
     'S15':('exp_k',[1.5,2.0]),'S16':None,'S17':None,'S18':None,'S19':None,'S20':('lb',[20,50])}
# economic-factor tags per family (for ALPHA_REGISTRY / portfolio lens)
ECON={'S1':'liquidity-sweep mean-reversion','S2':'failed-breakout fade','S3':'breakout-retest momentum',
      'S4':'volatility-regime expansion','S5':'opening-range momentum','S6':'session-transition momentum',
      'S7':'trend-pullback continuation','S8':'extension mean-reversion','S9':'MTF-trend momentum',
      'S10':'displacement continuation','S11':'structure-break reversal','S12':'range rotation',
      'S13':'imbalance fill','S14':'momentum exhaustion','S15':'trend acceleration',
      'S16':'previous-day levels','S17':'weekly levels','S18':'time-of-day','S19':'session gap','S20':'hybrid sweep+MTF'}
def neighbors(h):
    nb=_NB.get(h['family'])
    if not nb: return []
    k,seq=nb; v=h.get(k); out=[]
    if v in seq:
        for w in seq:
            if w!=v: hn=dict(h); hn[k]=w; out.append(hn)
    return out
def setups(d,h): return REGISTRY[h['family']][1](d,h)

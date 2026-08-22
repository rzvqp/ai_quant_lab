"""ALPHA-XAUUSD-LIQUIDITY-SWEEP-SHORT-001. SHORT after price sweeps liquidity above a PRIOR CONFIRMED
swing high and fails to accept. Raw-signal-FIRST + COMMON PARENT decomposition (L0..L4). Causal swing
highs (fractal, confirmed with lag). Baselines: sweep-only (L0), PROJECT TREND_DOWN, same-geometry.
Gated M5 -> causal H1/H4. NO N4/2025+/read_csv/V1. Cost tick 0.01 / STRESS 0.24. DEV-only. <=40 IDs."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
PIP=0.10; TICK=0.01; RT={"GROSS":0.0,"BASE":0.05,"STRESS":0.24}
def log(m): print(f"[{int(time.time())}] {m}",flush=True); open(os.path.join(SP,"liq.log"),"a").write(f"{int(time.time())} {m}\n")
tfs,META=D.build()
for tf in ("H1","H4"): tfs[tf]["m_atr"]=tfs[tf]["atr"]
log(f"loader sha={META['data_file_sha256'][:16]} H1 DEV={int(tfs['H1']['is_dev'].sum())} H4 DEV={int(tfs['H4']['is_dev'].sum())}")
RRTF={"H1":2.5,"H4":1.5}; L=2; LOOKBACK=60

def arrs(tf):
    x=tfs[tf]; return (x["open"].to_numpy(),x["high"].to_numpy(),x["low"].to_numpy(),x["close"].to_numpy(),
        x["atr"].to_numpy(),x["ema20"].to_numpy(),x["ema50"].to_numpy(),x["effic"].to_numpy(),
        x["is_dev"].to_numpy(),pd.to_datetime(x["time"],unit="s",utc=True).dt.year.to_numpy())

def sweeps(tf):
    """Return list of sweep events: dict(i=sweep bar, lvl=swept level, k=pivot bar). CAUSAL:
    bar i first breaches a prior confirmed swing high (fractal max over +-L, confirmed by i-1) that was
    unbroken since it formed."""
    o,h,l,c,atr,e20,e50,eff,dev,yr=arrs(tf); n=len(h)
    is_sh=np.zeros(n,bool)
    for k in range(L,n-L):
        if h[k]==max(h[k-L:k+L+1]): is_sh[k]=True
    ev=[]
    for i in range(L+5,n-1):
        if atr[i]!=atr[i] or not dev[i]: continue
        for k in range(i-L-1, max(L,i-LOOKBACK), -1):
            if not is_sh[k]: continue
            lvl=h[k]
            if h[i]>lvl and h[i-1]<=lvl and (i-1<k+1 or max(h[k+1:i])<=lvl):  # first unbroken breach
                ev.append(dict(i=i,lvl=lvl,k=k)); break
    return ev

def sim_short(tf,entry_i,stop_px,rr,scen):
    o,h,l,c,atr,*_=arrs(tf); n=len(o); ei=entry_i
    if ei<=0 or ei>=n-1: return None
    entry=o[ei]; risk=stop_px-entry
    if not np.isfinite(risk): return None
    me=max(5*TICK,0.10*atr[ei-1] if atr[ei-1]==atr[ei-1] else 5*TICK)
    if risk<me: risk=me; stop_px=entry+risk
    if risk<=0: return None
    tgt=entry-rr*risk; cost=RT[scen]; ex=None
    for j in range(ei,min(ei+48,n)):
        if h[j]>=stop_px: ex=stop_px;break
        if l[j]<=tgt: ex=tgt;break
    if ex is None: ex=c[min(ei+48,n-1)]
    return dict(R=((entry-ex)-cost)/risk, risk=risk, sl_pips=risk/PIP, tp_pips=rr*risk/PIP, i=entry_i)

# ---- L0..L4 mechanisms on COMMON PARENT sweeps ----
def build(tf, mech):
    o,h,l,c,atr,e20,e50,eff,dev,yr=arrs(tf); n=len(o); rr=RRTF[tf]; out=[]
    for ev in sweeps(tf):
        i=ev['i']; lvl=ev['lvl']
        entry_i=None; sweep_hi=h[i]
        if mech=="L0_sweep":                      # short next bar after breach
            entry_i=i+1
        elif mech=="L1_failaccept":               # sweep bar closes back below level
            if c[i]<lvl: entry_i=i+1
        elif mech=="L2_displacement":             # bearish displacement within i..i+3
            for j in range(i,min(i+4,n-1)):
                sweep_hi=max(sweep_hi,h[j])
                if (o[j]-c[j])>1.0*atr[j] and c[j]<o[j]: entry_i=j+1; break
        elif mech=="L3_disp_follow":              # displacement + next bearish close
            for j in range(i,min(i+4,n-2)):
                sweep_hi=max(sweep_hi,h[j])
                if (o[j]-c[j])>1.0*atr[j] and c[j]<o[j] and c[j+1]<c[j]: entry_i=j+2; break
        elif mech=="L4_structbreak":              # break below pre-sweep swing low within i..i+4
            prelow=min(l[max(0,ev['k']):i])       # structure between pivot and sweep
            for j in range(i,min(i+5,n-1)):
                sweep_hi=max(sweep_hi,h[j])
                if c[j]<prelow and c[j]<o[j]: entry_i=j+1; break
        elif mech=="S7_failreclaim":              # falls below, retests lvl, fails, closes below
            below=False
            for j in range(i,min(i+6,n-1)):
                sweep_hi=max(sweep_hi,h[j])
                if c[j]<lvl: below=True
                if below and h[j]>=lvl and c[j]<lvl: entry_i=j+1; break
        if entry_i is None or entry_i>=n-1: continue
        stop_px=sweep_hi+0.15*atr[i]              # stop above the sweep extreme (structural invalidation)
        s=sim_short(tf,entry_i,stop_px,rr,"STRESS"); b=sim_short(tf,entry_i,stop_px,rr,"BASE")
        if s and b: out.append(dict(**s,BASE=b['R'],yr=int(yr[entry_i]),sweep_i=i))
    return out

def project_td(tf):  # baseline: generic short in PROJECT TREND_DOWN, same short geometry (stop=recent high)
    o,h,l,c,atr,e20,e50,eff,dev,yr=arrs(tf); R=[]
    for i in range(55,len(o)-1):
        if atr[i]==atr[i] and dev[i] and e20[i]<e50[i] and eff[i]==eff[i] and eff[i]<-0.30:
            s=sim_short(tf,i+1,max(h[i-4:i+1])+0.15*atr[i],RRTF[tf],"STRESS")
            if s: R.append(s['R'])
    return np.array(R)

def M(trades,rr,base=None):
    if len(trades)<15: return dict(n=len(trades))
    R=np.array([t['R'] for t in trades]); Rb=np.array([t['BASE'] for t in trades]); nn=len(R); Rs=np.sort(R)[::-1]; net=R.sum(); w=R[R>0]
    byy=defaultdict(list)
    for t in trades: byy[t['yr']].append(t['R'])
    return dict(n=nn,WR=round(float((R>=rr-0.05).mean()),3),BASE=round(float(Rb.mean()),4),avgR=round(float(R.mean()),4),medR=round(float(np.median(R)),3),
        pf=round(float(w.sum()/-R[R<=0].sum()),3) if R[R<=0].sum()<0 else None,
        b5rem=round(float(Rs[max(1,int(nn*.05)):].mean()),4),b10rem=round(float(Rs[max(1,int(nn*.1)):].mean()),4),
        top10=round(float(Rs[:max(1,int(nn*.1))].sum()/net*100),1) if net>0 else 999,
        incr=round(float(R.mean()-(base.mean() if base is not None else 0)),4) if base is not None else None,
        medTP=round(float(np.median([t['tp_pips'] for t in trades])),1),medSL=round(float(np.median([t['sl_pips'] for t in trades])),1),
        temporal={y:(len(v),round(float(np.mean(v)),3)) for y,v in sorted(byy.items())})

PTD={tf:project_td(tf) for tf in ("H4","H1")}
for tf in PTD: log(f"PROJECT_TREND_DOWN {tf}: n={len(PTD[tf])} avgR={PTD[tf].mean():.4f}")
for tf in ("H4","H1"):
    sw=sweeps(tf); log(f"{tf} RAW SWEEP EVENTS (first breach of prior confirmed swing high): n={len(sw)}")

log("=== S4 COMMON-PARENT L0..L4 DECOMPOSITION (raw per-signal, STRESS) ===")
records=[]
for tf in ("H4","H1"):
    base=PTD[tf]
    for mech in ("L0_sweep","L1_failaccept","L2_displacement","L3_disp_follow","L4_structbreak","S7_failreclaim"):
        tr=build(tf,mech); m=M(tr,RRTF[tf],base)
        if m.get("n",0)<15: log(f"SW-{tf}-{mech}: n={m.get('n')} SPARSE"); records.append(dict(id=f"SW-{tf}-{mech}",tf=tf,mech=mech,m=m,status="SPARSE")); continue
        gate = m["avgR"]>0 and (m["incr"] or -9)>0 and m["b5rem"]>0 and m["top10"]<=60
        st="RAW_SURVIVE" if gate else "RAW_FAIL"
        records.append(dict(id=f"SW-{tf}-{mech}",tf=tf,mech=mech,m=m,status=st))
        log(f"SW-{tf}-{mech}: n={m['n']} WR={m['WR']} STRESS={m['avgR']} incr_vs_TD={m['incr']} medR={m['medR']} b5rem={m['b5rem']} top10%={m['top10']} medTP={m['medTP']}p -> {st}")
surv=[r for r in records if r['status']=='RAW_SURVIVE']
json.dump(dict(records=records,survivors=[r['id'] for r in surv],ptd={tf:float(PTD[tf].mean()) for tf in PTD}),open(os.path.join(SP,"liq_records.json"),"w"),indent=1,default=float)
log(f"L0..L4 DECOMPOSITION COMPLETE: {len(surv)} raw-survivors: {[r['id'] for r in surv]}")

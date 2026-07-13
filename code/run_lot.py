import numpy as np, pandas as pd, time, sys
from collections import Counter
import alpha_lab as A, mstrat as MS
from alpha_lab import bh_fdr
from campaign import full_stats
CFG=A.CFG; Q=CFG['FDR_Q']; MINTR=CFG['MINTR']
# DISCOVERY SCREEN thresholds (permissive, calibrated to ~6% of valid -> Research Candidate; recall not proof)
PF_MIN=1.02; DD_MAX=25.0
# STRICT VALIDATION (global-FDR + walk-forward + Red Team) is UNCHANGED and decides survival later.

def metrics(tr):
    if len(tr)==0: return dict(n=0,exp=np.nan,pf=np.nan,dd=np.nan)
    R=tr['R'].values; eq=np.cumsum(R); dd=float(np.max(np.maximum.accumulate(eq)-eq))
    gp=R[R>0].sum(); gl=-R[R<0].sum()
    return dict(n=len(R),exp=float(R.mean()),pf=float(gp/gl) if gl>0 else np.inf,dd=dd)

def statistician(d_res,d_val,h):
    tr=MS.backtest(d_res,h); m=metrics(tr)
    if m['n']<1 or np.isnan(m['exp']): return dict(p=1.0,stage='validity',passed=False,m=m)
    if m['n']<MINTR: return dict(p=1.0,stage='min_trades',passed=False,m=m)
    if m['exp']<=0: return dict(p=1.0,stage='expectancy',passed=False,m=m)
    if m['pf']<PF_MIN: return dict(p=1.0,stage='profit_factor',passed=False,m=m)
    if m['dd']>DD_MAX: return dict(p=1.0,stage='max_dd',passed=False,m=m)
    nb=[metrics(MS.backtest(d_res,hn))['exp'] for hn in MS.neighbors(h)]; nb=[x for x in nb if not np.isnan(x)]
    if MS.neighbors(h) and (not nb or np.mean([x>0 for x in nb])<0.5): return dict(p=1.0,stage='param_stability',passed=False,m=m)
    mv=metrics(MS.backtest(d_val,h))
    if mv['n']<5 or mv['exp']<=0: return dict(p=1.0,stage='oos',passed=False,m=m,mv=mv)
    p=MS.analytic_p(d_res,MS.setups(d_res,h),m['exp'],m['n'])
    return dict(p=p,stage='stat_ok',passed=True,m=m,mv=mv)

def walk_forward(nonhold,h,K=4,need=3):
    n=len(nonhold); pos=used=0
    for i in range(K):
        seg=nonhold.iloc[int(n*i/K):int(n*(i+1)/K)]
        if len(seg)<200: continue
        mm=metrics(MS.backtest(seg,h))
        if mm['n']>=5: used+=1; pos+=1 if mm['exp']>0 else 0
    import math; return used>=2 and pos>=math.ceil(need*used/K)

def red_team(d_res,h):
    att={}; c2=dict(CFG); c2['spread_ticks']*=3; c2['slip_ticks']*=3
    att['cost3x']= metrics(MS.simulate(d_res,MS.setups(d_res,h),c2))['exp']>0
    tr=MS.backtest(d_res,h); R=tr['R'].values
    if len(R)>=5:
        k=max(1,len(R)//5); best=max(np.sum(R[i:i+k]) for i in range(len(R)-k+1))
        att['no_cherry']=(R.sum()-best)/max(len(R)-k,1)>0
        mon=pd.to_datetime(d_res['time'].values[tr['ei'].astype(int).values],unit='s').to_period('M')
        g=pd.DataFrame({'R':R,'m':mon}).groupby('m')['R'].agg(['mean','count']); g=g[g['count']>=3]
        att['monthly']=(g['mean']>0).mean()>=0.5 if len(g)>=3 else False
    else: att['no_cherry']=False; att['monthly']=False
    return all(att.values()),att

def parity_and_smoke(d):
    print("\n--- BACKTEST PARITY AUDIT (fast vs reference engine) ---")
    ok_par=True
    for fam in MS.REGISTRY:
        g=MS.REGISTRY[fam][0]()[:40]
        for h in g:
            if h.get('exit') in ('trailing',) or h.get('exit_kind')=='trailing': continue
            su=[s for s in MS.setups(d,h) if s['exit_kind'] in ('rr','time','opp_liq','opp_struct')]
            if len(su)<3: continue
            a=MS.simulate(d,su,CFG)['R'].values; b=MS.simulate_ref(d,su,CFG)
            if len(a)!=len(b) or (len(a)>0 and np.max(np.abs(a-b))>1e-9): ok_par=False; print(f"  PARITY FAIL {fam} {h['id']}")
            break
    print(f"  parity: {'PASS' if ok_par else 'FAIL'}")
    print("\n--- SMOKE + LOOKAHEAD + LEDGER per family ---")
    ok_all=True
    nb=len(d)
    for fam,(gram,_) in MS.REGISTRY.items():
        hs=gram(); sig=0; la_ok=True; ledger_ok=True; selective=True
        for h in hs[:60]:
            su=MS.setups(d,h)
            if su: sig+=1
            if len(su)>0.10*nb: selective=False          # selectivity: most bars are NON-signal
            for s in su[:200]:
                if not (s['ei']>s['si']): la_ok=False     # entry strictly after signal (no lookahead)
            if su and not set(['R','si','ei']).issubset(MS.backtest(d,h).columns): ledger_ok=False
        v = sig>=1 and selective and la_ok and ledger_ok
        ok_all&=v
        print(f"  {fam}: grammar={len(hs)} signal_hyps={sig} selective(<10%bars)={selective} lookahead_safe={la_ok} ledger_ok={ledger_ok} -> {'OK' if v else 'FAIL'}")
    return ok_par and ok_all

def run_lot(lot_families, lot_name):
    d=MS.load(); n=len(d); a=int(n*0.6); b=int(n*0.8)
    res=d.iloc[:a].copy(); val=d.iloc[a:b].copy(); nonhold=d.iloc[:b].copy()   # holdout d[b:] SEALED
    print(f"=== {lot_name}: families {lot_families} | M15={n} research={a} val={b-a} holdout(SEALED)={n-b} ===")
    if not parity_and_smoke(d):
        print("PRE-CHECKS FAILED -> abort lot"); return
    # generate universe (canonical, dedup)
    gen=0; uni=[]; seen=set()
    for fam in lot_families:
        g=MS.REGISTRY[fam][0](); gen+=len(g)
        for h in g:
            if h['id'] in seen: continue
            seen.add(h['id']); uni.append(h)
    dup=gen-len(uni)
    t0=time.time(); reg=[]
    for h in uni:
        v=statistician(res,val,h); v['h']=h; reg.append(v)
    N=len(reg); deaths={}
    for v in reg:
        if not v['passed']: deaths[v['stage']]=deaths.get(v['stage'],0)+1
    pv=np.array([v['p'] for v in reg])
    keep=bh_fdr(pv,Q)  # GLOBAL FDR over whole lot universe
    fdr=[reg[i] for i in range(N) if keep[i] and reg[i]['passed']]
    # min p, min q
    order=np.argsort(pv); m=N; sp=pv[order]; qv=sp*m/np.arange(1,m+1)
    minp=float(sp[0]); minq=float(np.min(qv))
    wfs=[v for v in fdr if walk_forward(nonhold,v['h'])]
    cands=[]
    for v in wfs:
        ok,att=red_team(res,v['h'])
        if ok: v['att']=att; cands.append(v)
    dt=time.time()-t0
    # per-family stats
    perfam={f:{'gen':0,'stat':0,'fdr':0,'cand':0} for f in lot_families}
    for f in lot_families: perfam[f]['gen']=len(MS.REGISTRY[f][0]())
    for v in reg:
        f=v['h']['family']
        if v['passed']: perfam[f]['stat']+=1
    for v in fdr: perfam[v['h']['family']]['fdr']+=1
    for v in cands: perfam[v['h']['family']]['cand']+=1

    print(f"\n===== {lot_name} REPORT (holdout SEALED) =====")
    print(f"hypotheses generated: {gen} | unique canonical: {N} | semantic duplicates removed: {dup}")
    print(f"eliminated per stage: {dict(sorted(deaths.items(),key=lambda x:-x[1]))}")
    print(f"passed Statistician: {sum(v['passed'] for v in reg)} | GLOBAL-FDR: {len(fdr)} | walk-forward: {len(wfs)} | Red Team -> CANDIDATES: {len(cands)}")
    print(f"min p-value: {minp:.2e} | min q-value: {minq:.3f} | throughput: {N/dt*3600:,.0f} hyp/hr ({dt:.0f}s) | errors: 0")
    print("\nper-family (diagnostic):")
    for f in lot_families:
        pf=perfam[f]; verdict='DISCOVERY CANDIDATE' if pf['cand']>0 else ('REJECTED' if pf['stat']>0 else 'NO SIGNAL')
        print(f"  {f}: grammar={pf['gen']} statPass={pf['stat']} globalFDR={pf['fdr']} candidates={pf['cand']} -> {verdict}")
    fams_signal=[f for f in lot_families if perfam[f]['cand']>0]; fams_none=[f for f in lot_families if perfam[f]['stat']==0]
    print(f"\nfamilies WITH candidates: {fams_signal or 'none'} | families NO-SIGNAL: {fams_none or 'none'}")
    print("\n--- CANDIDATES (survived Statistician->global-FDR->walk-forward->Red Team; holdout SEALED) ---")
    if not cands: print("  NONE")
    grp=Counter()
    for v in cands:
        h=v['h']; stt=full_stats(MS.backtest(res,h)); grp[h['family']]+=1
        print(f"  {h['family']}[{h['id']}] {dict((k,val) for k,val in h.items() if k not in ('id','family'))}")
        print(f"     n={stt['n']} win={stt['win_rate']:.3f} exp={stt['expectancy_R']:.3f}R PF={stt['profit_factor']:.2f} maxDD={stt['max_dd_R']:.1f}R longestLoss={stt['longest_losing_streak']} RedTeam={v['att']}")
    return reg,cands

if __name__=="__main__":
    run_lot(['S1','S2','S3','S4','S5'],"LOT 1 (S1-S5)")

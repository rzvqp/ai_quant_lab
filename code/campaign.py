"""
Campaign orchestrator implementing the TWO CEO-mandated critical-defect fixes + walk-forward.
FIX 1 GLOBAL MULTIPLE TESTING: registry holds EVERY hypothesis tested (incl early deaths);
       BH-FDR computed once over the WHOLE campaign (m = N total), not per-symbol/late-survivors.
FIX 2 REAL TERMINAL HOLDOUT: a sealed holdout slice per instrument, never passed to any
       elimination step; opened ONCE only for full-pass strategies, and only on CEO approval.
Pass order (per CEO): Statistician -> GLOBAL FDR -> walk-forward -> Red Team -> [CEO gate] -> holdout.
Analytic p-value (normal approx of the frozen randomized-entry null) gives the resolution global
FDR needs at N in the tens of thousands. Frozen backtest/gates reused unchanged.
"""
import numpy as np, pandas as pd, math, json, os
import alpha_lab as A, families as F

CFG=A.CFG; Q=CFG['FDR_Q']
HOLD_FRAC=0.20; VAL_FRAC=0.20   # research 60 / validation 20 / holdout 20 (time-ordered)

# ---------------- sealed holdout vault ----------------
class HoldoutVault:
    def __init__(self): self._d={}; self.opened=set()
    def seal(self, inst, df_holdout): self._d[inst]=df_holdout.reset_index(drop=True)
    def open(self, inst, approval):     # requires explicit CEO approval token
        if approval!="CEO_APPROVED": raise PermissionError("terminal holdout requires CEO approval")
        self.opened.add(inst); return self._d[inst]

def split_campaign(df):
    n=len(df); h=int(n*(1-HOLD_FRAC)); v=int(n*(1-HOLD_FRAC-VAL_FRAC))
    return df.iloc[:v].copy(), df.iloc[v:h].copy(), df.iloc[h:].copy()   # research, validation, HOLDOUT(sealed)

# ---------------- analytic p (normal approx of frozen randomized-entry null) ----------------
def analytic_p(d,h,obs_exp):
    ecfg=(h['direction'],h['sl_atr'],h['tp_r'],h['timeout'],h.get('trail','none'))
    pool=F._entry_pool(d,ecfg,CFG)
    tr=F.backtest(d,h,CFG); k=len(tr)
    if k<CFG['MINTR'] or len(pool)<30: return 1.0, k
    mu=float(np.mean(pool)); sd=float(np.std(pool,ddof=1))
    if sd<=0: return 1.0, k
    z=(obs_exp-mu)/(sd/math.sqrt(k))
    p=0.5*math.erfc(z/math.sqrt(2))     # upper tail
    return max(p,1e-300), k

# ---------------- walk-forward (time-robustness on non-holdout) ----------------
def walk_forward(d_nonhold,h,K=4,need=3):
    n=len(d_nonhold); pos=0; used=0
    for i in range(K):
        seg=d_nonhold.iloc[int(n*i/K):int(n*(i+1)/K)]
        if len(seg)<40: continue
        m=A.metrics(F.backtest(seg,h,CFG))
        if m['n']>=5: used+=1; pos+= (1 if m['exp']>0 else 0)
    return (used>=2) and (pos>=need*used/K)

# ---------------- full per-strategy stats ----------------
def full_stats(tr):
    if len(tr)==0: return {}
    R=tr['R'].values; wins=R[R>0]; losses=R[R<0]
    eq=np.cumsum(R); dd=float(np.max(np.maximum.accumulate(eq)-eq))
    # longest losing streak
    ls=mx=0
    for r in R:
        if r<0: ls+=1; mx=max(mx,ls)
        else: ls=0
    gp=wins.sum(); gl=-losses.sum()
    return dict(n=int(len(R)), win_rate=float((R>0).mean()),
                avg_win_R=float(wins.mean()) if len(wins) else 0.0,
                avg_loss_R=float(losses.mean()) if len(losses) else 0.0,
                expectancy_R=float(R.mean()), profit_factor=float(gp/gl) if gl>0 else np.inf,
                max_dd_R=dd, longest_losing_streak=int(mx))

def per_year(df,h):
    d=F.add_features(df)
    yrs={}
    if 'time' in d:
        y=pd.to_datetime(d['time'],unit='s',utc=True).dt.year
        for yr in sorted(set(y.dropna())):
            sub=d[y==yr]
            if len(sub)>50:
                m=A.metrics(F.backtest(sub,h,CFG)); yrs[int(yr)]=round(m['exp'],3) if not np.isnan(m['exp']) else None
    return yrs

# ---------------- campaign runner ----------------
def run_campaign(datasets, label, vault=None):
    """datasets: dict inst -> df (with features to be added). Returns candidates + KPIs. Holdout NOT opened."""
    vault=vault or HoldoutVault()
    registry=[]   # every hypothesis tested (FIX 1)
    hyps=A.generate()
    prepared={}
    for inst,df in datasets.items():
        d=F.add_features(df); r,v,hd=split_campaign(d); vault.seal(inst,hd)
        prepared[inst]=(d,r,v,hd)
    # Stage A: per (inst,hyp) statistician gates on research+validation (NO holdout)
    for inst,(d,r,v,hd) in prepared.items():
        for h in hyps:
            res=A.statistician(r,v,h,CFG)     # frozen gates: sanity..oos (uses MC internally; we override p below)
            rec=dict(inst=inst,id=h['id'],h=h,stage=res['stage'],passed_stat=res['passed'])
            if res['passed']:
                p,k=analytic_p(r,h,res['m']['exp'])
                rec.update(p=p,m=res['m'],mv=res['mv'],k=k)
            else:
                rec.update(p=1.0,m=res.get('m'))
            registry.append(rec)
    N=len(registry)
    # Stage B: GLOBAL BH-FDR over ALL N (FIX 1)
    pvec=np.array([rec['p'] for rec in registry])
    keep=A.bh_fdr(pvec,Q)
    for i,rec in enumerate(registry): rec['fdr_global']=bool(keep[i])
    fdr_surv=[rec for rec in registry if rec['fdr_global'] and rec['passed_stat']]
    # Stage C: walk-forward
    wf_surv=[]
    for rec in fdr_surv:
        d,r,v,hd=prepared[rec['inst']]; nonhold=pd.concat([r,v]).reset_index(drop=True)
        if walk_forward(nonhold,rec['h']): rec['walk_forward']=True; wf_surv.append(rec)
        else: rec['walk_forward']=False
    # Stage D: Red Team
    rt_surv=[]
    for rec in wf_surv:
        d,r,v,hd=prepared[rec['inst']]
        ok,att=A.red_team(r,v,rec['h'],CFG); rec['redteam']=att; rec['redteam_pass']=ok
        if ok: rt_surv.append(rec)
    # CANDIDATES = passed Statistician + global FDR + walk-forward + Red Team (holdout still SEALED)
    kpi=dict(label=label, N=N, stat_pass=sum(r['passed_stat'] for r in registry),
             fdr_pass=len(fdr_surv), wf_pass=len(wf_surv), redteam_pass=len(rt_surv),
             deaths={}, holdout_opened=len(vault.opened))
    for rec in registry:
        if not rec['passed_stat']: kpi['deaths'][rec['stage']]=kpi['deaths'].get(rec['stage'],0)+1
    return rt_surv, kpi, prepared, vault

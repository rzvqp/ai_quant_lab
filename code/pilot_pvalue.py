import numpy as np, pandas as pd, math, mstrat as MS
CFG=MS.CFG; rng0=np.random.default_rng(12345); B=50000
d=MS.load(); res=d.iloc[:int(len(d)*0.6)].copy()
o=res['open'].values;hi=res['high'].values;lo=res['low'].values;cl=res['close'].values;atr=res['m_atr'].values; N=len(res)
cost=(CFG['spread_ticks']+CFG['slip_ticks'])*MS.TICK
def trades_risk(h):
    setups=MS.setups(res,h); sd={s['ei']:s for s in setups}; tr=MS.backtest(res,h)
    ei=tr['ei'].astype(int).values; R=tr['R'].values
    risks=np.array([abs(o[e]-sd[e]['stop']) for e in ei]); s0=setups[0]
    return R,risks,s0['dir'],s0['exit_kind'],s0.get('exit_param')
def p_analytic(h,R):
    s=MS.setups(res,h); return MS.analytic_p(res,s,R.mean(),len(R))
def p_iid(R):  # one-sided H0 mean<=0 : center at 0
    bm=rng0.choice(R,size=(B,len(R)),replace=True).mean(axis=1); k=int(np.sum(bm-R.mean()>=R.mean())); return (k+1)/(B+1)
def p_block(R,bl=5):
    n=len(R); nb=int(np.ceil(n/bl)); idx=np.arange(n); means=np.empty(B)
    for b in range(B):
        starts=rng0.integers(0,n,nb); s=np.concatenate([idx[st:st+bl] for st in starts])[:n]; means[b]=R[s%n].mean()
    k=int(np.sum(means-R.mean()>=R.mean())); return (k+1)/(B+1)
def p_matched(R,risks,dirn,ek,ep):  # random timing + SAME realized risk profile + same exit
    valid=np.where(np.isfinite(atr)&(atr>0))[0]; valid=valid[(valid>2)&(valid<N-2)]; k=len(R); obs=R.mean()
    rr=ep if ek=='rr' else 2; to=int(ep) if ek=='time' else 48; means=np.empty(B)
    for b in range(B):
        ents=rng0.choice(valid,size=k,replace=True); rk=rng0.choice(risks,size=k,replace=True); Rs=np.empty(k)
        for j,(i,risk) in enumerate(zip(ents,rk)):
            entry=o[i+1]; stop=entry-dirn*risk; tgt=entry+dirn*rr*risk; ex=None
            for t in range(i+1,min(i+1+to,N)):
                if dirn>0:
                    if lo[t]<=stop: ex=stop;break
                    if hi[t]>=tgt: ex=tgt;break
                else:
                    if hi[t]>=stop: ex=stop;break
                    if lo[t]<=tgt: ex=tgt;break
            if ex is None: ex=cl[min(i+1+to,N-1)]
            Rs[j]=(dirn*(ex-entry)-2*cost)/risk
        means[b]=Rs.mean()
    kk=int(np.sum(means>=obs)); return (kk+1)/(B+1)

def report(name,R,risks,dirn,ek,ep,h=None):
    pa=p_analytic(h,R) if h else float('nan')
    print(f"\n[{name}] n={len(R)} mean={R.mean():.3f} sd={R.std():.2f} skew={((R-R.mean())**3).mean()/R.std()**3:.1f}")
    print(f"   p_analytic(generic ATR null,normal)={pa:.2e} | p_iid_boot={p_iid(R):.4f} | p_block_boot={p_block(R):.4f} | p_MATCHED_null={p_matched(R,risks,dirn,ek,ep):.4f}")

# S6 extreme
h6=[hh for hh in MS.REGISTRY['S6'][0]() if hh['id']=='7a86a38610f8'][0]; R,rk,dn,ek,ep=trades_risk(h6); report("S6 extreme",R,rk,dn,ek,ep,h6)
# S1 representative RC
df=pd.read_parquet('FAMILY_RESULTS.parquet'); s1id=df[(df.fam=='S1')&df.rc].sort_values('exp',ascending=False).iloc[0]['id']
h1=[hh for hh in MS.REGISTRY['S1'][0]() if hh['id']==s1id][0]; R,rk,dn,ek,ep=trades_risk(h1); report("S1 rep RC",R,rk,dn,ek,ep,h1)
# synthetic controls
def synth(mean,n,tail=1.0,seed=1):
    r=np.random.default_rng(seed); base=r.normal(mean,1.0,n); out=base+ (r.standard_t(3,n)*tail if tail else 0); return out
Rn=synth(0.0,150,0.0,seed=2); report("SYNTH null (mean0)",Rn,np.full(len(Rn),1.0),1,'rr',2.0)
Re=synth(0.25,150,0.0,seed=3); report("SYNTH edge (mean0.25)",Re,np.full(len(Re),1.0),1,'rr',2.0)
print("\nNOTE: matched-null uses random timing + SAME realized risk profile + same exit => reproduces tiny-stop outliers; the correct benchmark.")

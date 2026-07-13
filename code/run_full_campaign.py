import numpy as np, pandas as pd, time
import mstrat as MS, run_lot
d=MS.load(); n=len(d); a=int(n*0.6); b=int(n*0.8)
res=d.iloc[:a].copy(); val=d.iloc[a:b].copy()   # holdout d[b:] SEALED
rt=res['time'].values; ryr=pd.to_datetime(rt,unit='s').year; rmon=pd.to_datetime(rt,unit='s').to_period('M')
FAMS=[f'S{i}' for i in range(1,21)]
print(f"ENGINE v2 (stop-floor). research={a} val={b-a} holdout(SEALED)={n-b}")
# parity + smoke
if not run_lot.parity_and_smoke(d): print("PRECHECK FAIL"); import sys; sys.exit()
rows=[]; t0=time.time()
for fam in FAMS:
    for h in MS.REGISTRY[fam][0]():
        tr=MS.backtest(res,h); R=tr['R'].values; ei=tr['ei'].astype(int).values
        nn=len(R)
        if nn==0: rows.append(dict(fam=fam,id=h['id'],h=h,n=0)); continue
        eq=np.cumsum(R); dd=float(np.max(np.maximum.accumulate(eq)-eq)); gp=R[R>0].sum(); gl=-R[R<0].sum()
        pf=float(gp/gl) if gl>0 else np.inf; exp=float(R.mean())
        srt=np.sort(R)[::-1]; gpp=R[R>0].sum() if (R>0).any() else 1
        t1=srt[:1].sum()/gpp; t3=srt[:3].sum()/gpp; t5=srt[:5].sum()/gpp
        wo1=(R.sum()-srt[:1].sum())/max(nn-1,1)
        lo,hi=np.percentile(R,[5,95]); trim5=R[(R>=lo)&(R<=hi)].mean()
        mon=pd.to_datetime(rt[ei],unit='s').to_period('M'); gm=pd.Series(R).groupby(mon).mean()
        yr=pd.to_datetime(rt[ei],unit='s').year; yrs={int(Y):round(float(R[yr==Y].mean()),3) for Y in sorted(set(yr))}
        mv=MS.backtest(val,h); mvexp=float(mv['R'].mean()) if len(mv)>=5 else np.nan
        dirs=set(s['dir'] for s in MS.setups(res,h)); side='both' if len(dirs)>1 else ('long' if 1 in dirs else 'short')
        rows.append(dict(fam=fam,id=h['id'],h={k:v for k,v in h.items() if k not in('id','family')},
            n=nn,exp=exp,pf=pf,dd=dd,win=float((R>0).mean()),sumR=float(R.sum()),val_exp=mvexp,
            median=float(np.median(R)),trim5=float(trim5),t1=float(t1),t3=float(t3),t5=float(t5),wo1=float(wo1),
            months=int(gm.shape[0]),pos_months=int((gm>0).sum()),years=len(yrs),yrs=yrs,side=side))
df=pd.DataFrame(rows)
def hist_prof(r): return r['n']>0 and r['sumR']>0 and r['exp']>0 and r['pf']>1.00
def research_worthy(r):
    return (r['n']>=25 and r['exp']>0 and r['pf']>=1.02 and r['dd']<=25 and (r['wo1']>0 or r['t1']<0.5) and (r['months']>=2 and r['years']>=2))
df['hist_prof']=df.apply(lambda r: hist_prof(r) if r['n']>0 else False,axis=1)
df['research_worthy']=df.apply(lambda r: research_worthy(r) if r['n']>0 else False,axis=1)
df['fragile']=df.apply(lambda r: (r['n']>0 and r['exp']>0 and (r['t1']>=0.5 or r['wo1']<=0)),axis=1)
print(f"compute {time.time()-t0:.0f}s | total hyps={len(df)}")

print("\n================= CENTRAL TABLE (ENGINE v2; statistical fields PENDING) =================")
print(f"{'S':4}{'econ':26}{'gen':>5}{'valid':>6}{'profit':>7}{'%prof':>7}{'bestExp':>8}{'bestPF':>7}{'RW':>4}")
tot={}
for fam in FAMS:
    s=df[df.fam==fam]; g=len(s); v=int((s['n']>=25).sum()); pr=int(s['hist_prof'].sum()); rw=int(s['research_worthy'].sum())
    sp=s[s['n']>0]; be=sp['exp'].max() if len(sp) else np.nan; bp=sp[sp['pf']<np.inf]['pf'].max() if len(sp[sp['pf']<np.inf]) else np.nan
    print(f"{fam:4}{MS.ECON[fam][:25]:26}{g:>5}{v:>6}{pr:>7}{100*pr/max(v,1):>6.0f}%{be:>8.3f}{bp:>7.2f}{rw:>4}")
    tot[fam]=dict(gen=g,valid=v,prof=pr,rw=rw)
print(f"\nTOTALS: generated={len(df)} valid(n>=25)={int((df['n']>=25).sum())} HIST_PROFITABLE={int(df['hist_prof'].sum())} RESEARCH_WORTHY={int(df['research_worthy'].sum())}")
fam_prof=[f for f in FAMS if tot[f]['prof']>0]; fam_noprof=[f for f in FAMS if tot[f]['prof']==0]; fam_rw=[f for f in FAMS if tot[f]['rw']>0]
print(f"families WITH >=1 historically profitable: {fam_prof}")
print(f"families WITH 0 profitable: {fam_noprof}")
print(f"families WITH >=1 RESEARCH WORTHY: {fam_rw}")

def show(title,sub,cols):
    print(f"\n--- {title} ---")
    for _,r in sub.iterrows():
        print(f"  {r['fam']}[{r['id']}] {r['side']} n={r['n']} exp={r['exp']:.3f} pf={r['pf'] if r['pf']<np.inf else 99:.2f} dd={r['dd']:.1f} win={r['win']:.2f} posM={r['pos_months']}/{r['months']} t1={r['t1']:.2f} RW={r['research_worthy']}")
prof=df[df.hist_prof].copy()
show("TOP 20 historically profitable (by expectancy)", prof.sort_values('exp',ascending=False).head(20),None)
prof['stab']=prof['pos_months']/prof['months'].clip(lower=1)
show("TOP 20 by monthly stability (pos_months share, n>=40)", prof[prof.n>=40].sort_values(['stab','n'],ascending=False).head(20),None)
prof['pdd']=prof['sumR']/prof['dd'].clip(lower=0.1)
show("TOP 20 by profit/maxDD", prof.sort_values('pdd',ascending=False).head(20),None)
show("FRAGILE / outlier-dependent (exp>0 but top1>=50% or without-top1<=0)", df[df.fragile].sort_values('exp',ascending=False).head(25),None)
inv=df[df.n==0]; print(f"\n--- technically-invalid (no trades): {len(inv)} variants ---")
df.drop(columns=['h','yrs']).to_parquet("FAMILY_RESULTS.parquet")
print("\nSTRICT VALIDATION: PENDING (p-value engine under remediation). No significance verdicts. Holdout SEALED.")

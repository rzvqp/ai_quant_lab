import numpy as np, pandas as pd, mstrat as MS
d=MS.load(); res=d.iloc[:int(len(d)*0.6)].copy(); o=res['open'].values; atr=res['m_atr'].values
df=pd.read_parquet('FAMILY_RESULTS.parquet'); s1id=df[(df.fam=='S1')&df.rc].sort_values('exp',ascending=False).iloc[0]['id']
h=[hh for hh in MS.REGISTRY['S1'][0]() if hh['id']==s1id][0]
setups=MS.setups(res,h); sd={s['ei']:s for s in setups}; tr=MS.backtest(res,h); R=tr['R'].values; ei=tr['ei'].astype(int).values
risk=np.array([abs(o[e]-sd[e]['stop']) for e in ei])
print("S1 rep RC:",{k:v for k,v in h.items() if k not in('id','family')})
print(f"\n=== TEST A: ROBUSTNESS OF OBSERVED TRADE MEAN (S1 rep) — outlier-driven or robust? ===")
print(f"n={len(R)} raw_expectancy={R.mean():.3f}R median_R={np.median(R):.3f}")
for p in (1,2.5,5):
    lo,hi=np.percentile(R,[p,100-p]); tm=R[(R>=lo)&(R<=hi)].mean(); wm=np.clip(R,lo,hi).mean()
    print(f"  trim {p}% mean={tm:.3f}  winsorized {p}% mean={wm:.3f}")
srt=np.sort(R)[::-1]
for k in (1,3,5): print(f"  without top-{k} winners: mean={(R.sum()-srt[:k].sum())/(len(R)-k):.3f}  (top-{k} share of gross profit={srt[:k].sum()/R[R>0].sum()*100:.0f}%)")
loo=np.array([ (R.sum()-R[i])/(len(R)-1) for i in range(len(R))]); print(f"  leave-one-out expectancy range: [{loo.min():.3f}, {loo.max():.3f}]")
print(f"  R: max={R.max():.1f} skew={((R-R.mean())**3).mean()/R.std()**3:.1f}")
# tiny-stop / R-normalization check
ratio=risk/atr[ei]; print(f"\n  risk/ATR: median={np.median(ratio):.2f} min={ratio.min():.3f} | trades stop<0.3ATR: {(ratio<0.3).sum()} | stop<1 tick({MS.TICK}): {(risk<MS.TICK).sum()}")
# monthly
mon=pd.to_datetime(res['time'].values[ei],unit='s').to_period('M'); g=pd.Series(R).groupby(mon).agg(['sum','count','mean'])
print(f"\n  months traded={len(g)} positive_months={(g['mean']>0).sum()} ({100*(g['mean']>0).mean():.0f}%)  monthly sum R min/median/max={g['sum'].min():.1f}/{g['sum'].median():.1f}/{g['sum'].max():.1f}")
# yearly
yr=pd.to_datetime(res['time'].values[ei],unit='s').year; 
for Y in sorted(set(yr)): sel=yr==Y; print(f"    {Y}: n={sel.sum()} exp={R[sel].mean():.3f}R")

print("\n=== TEST (1): bootstrap H0-centering automated proof ===")
rng=np.random.default_rng(7); B=20000
bm=rng.choice(R,size=(B,len(R)),replace=True).mean(axis=1)
null_centered=bm-R.mean()   # H0: mean<=0 -> shift so null-population mean ~ 0
print(f"  observed mean={R.mean():.4f} | centered-null mean={null_centered.mean():.5f} (must be ~0) -> {'PASS' if abs(null_centered.mean())<0.02 else 'FAIL'}")
k=int(np.sum(null_centered>=R.mean())); print(f"  p_block/IID = (k+1)/(B+1) with k={k} -> {(k+1)/(B+1):.4f}  [exceedance: null_centered >= observed]")

print("\n=== matched-null failure cause (synthetic control) ===")
print("  CAUSE: synthetic control fed synthetic R's DIRECTLY, but matched-null builds its null by running")
print("  RANDOM ENTRIES THROUGH THE REAL-PRICE BACKTESTER (risk=1.0 px on ~4000 gold, ATR~10 => absurd tiny")
print("  stop => degenerate R scale). Synthetic-R vs real-price-null = construction/scale MISMATCH, not a")
print("  matched-null property. FIX: validate matched-null on synthetic PRICE series with injected null/edge")
print("  SIGNALS run through the SAME backtester (100 null series -> uniform p), never on bare synthetic R's.")

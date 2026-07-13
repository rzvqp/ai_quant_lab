import numpy as np, pandas as pd, mstrat as MS
d=MS.load(); res=d.iloc[:int(len(d)*0.6)].copy()
h=[hh for hh in MS.REGISTRY['S6'][0]() if hh['id']=='7a86a38610f8'][0]
print("S6 hyp:",{k:v for k,v in h.items() if k not in('id','family')})
setups=MS.setups(res,h); tr=MS.backtest(res,h); R=tr['R'].values; ei=tr['ei'].astype(int).values
o=res['open'].values;atr=res['m_atr'].values
# per-trade risk (entry-stop distance) from setups aligned to trades
risk=[]
sd={s['ei']:s for s in setups}
for e in ei:
    s=sd.get(e); risk.append(abs(o[e]-s['stop']) if s else np.nan)
risk=np.array(risk)
def moments(x):
    m=x.mean(); s=x.std(); sk=((x-m)**3).mean()/s**3; ku=((x-m)**4).mean()/s**4
    return m,s,sk,ku
m,s,sk,ku=moments(R)
print(f"\nR distribution: n={len(R)} mean={m:.3f} sd={s:.3f} skew={sk:.2f} kurtosis={ku:.2f}")
print(f"R min={R.min():.2f} max={R.max():.2f} | trades |R|>10: {(np.abs(R)>10).sum()} | R>20: {(R>20).sum()}")
srt=np.sort(R)[::-1]; print(f"top-5 R: {np.round(srt[:5],1)}  -> share of total profit: {srt[:5].sum()/R[R>0].sum()*100:.0f}%")
print(f"total sum R={R.sum():.1f} ; without top-5 winners: {(R.sum()-srt[:5].sum()):.1f} ; mean without top-5: {(R.sum()-srt[:5].sum())/(len(R)-5):.3f}")
# tiny-stop diagnosis: risk in price units vs ATR
print(f"\nrisk(entry-stop) price units: min={np.nanmin(risk):.3f} median={np.nanmedian(risk):.3f} max={np.nanmax(risk):.3f}")
print(f"risk/ATR ratio: min={np.nanmin(risk/atr[ei]):.3f} median={np.nanmedian(risk/atr[ei]):.3f} (tiny stops -> huge R)")
tiny=(risk<0.3*atr[ei]); print(f"trades with stop < 0.3*ATR (tiny): {tiny.sum()} ; their mean R: {R[tiny].mean() if tiny.any() else 0:.2f}")
# overlap check
print(f"\noverlap: entries={len(ei)} unique={len(set(ei))} monotonic={bool((np.diff(ei)>0).all())}")
# maxDD location
eq=np.cumsum(R); dd=np.maximum.accumulate(eq)-eq; print(f"maxDD={dd.max():.1f}R at trade {dd.argmax()}/{len(R)}")
print("\nCAUSE: extreme analytic-p is driven by", "TINY-STOP OUTLIERS + PROFIT CONCENTRATION (few trades dominate), not clean heavy-tail alpha" if srt[:5].sum()/R[R>0].sum()>0.2 or tiny.sum()>0 else "genuine heavy tails")

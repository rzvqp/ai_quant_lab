"""Bearish mechanism mining — stage 2: multi-feature discriminator + SEQUENCE hypotheses with a
DISCOVERY/CONFIRMATION chronological split (S7/S8/S13/S23.E). Answer: is bearish direction predictable
from causal features/sequences at all, or is it noise? Outcome labels DIAGNOSTIC only."""
import sys, os, numpy as np, pandas as pd
from collections import Counter
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
PIP=0.10
tfs,META=D.build()
tf="H4"; H=12
x=tfs[tf]; o=x["open"].to_numpy();h=x["high"].to_numpy();l=x["low"].to_numpy();c=x["close"].to_numpy()
atr=x["atr"].to_numpy();e20=x["ema20"].to_numpy();e50=x["ema50"].to_numpy();hh20=x["hh20"].to_numpy();ll20=x["ll20"].to_numpy()
hh50=x["hh50"].to_numpy();ll50=x["ll50"].to_numpy();eff=x["effic"].to_numpy();ama=x["atr_ma"].to_numpy()
dev=x["is_dev"].to_numpy();dt=pd.to_datetime(x["time"],unit="s",utc=True);n=len(o)
ema100=pd.Series(c).ewm(span=100,adjust=True).mean().to_numpy()
hh100=pd.Series(h).rolling(100).max().shift(1).to_numpy()
rows=[]
for i in range(105,n-H-1):
    if atr[i]!=atr[i] or not dev[i]: continue
    entry=o[i+1]; fh=h[i+1:i+1+H]; fl=l[i+1:i+1+H]
    bear=(entry-fl.min())/PIP; bull=(fh.max()-entry)/PIP
    w=hh50[i]-ll50[i]
    feats=dict(
        rangepos=(c[i]-ll50[i])/w if w>0 else 0.5,
        dist_hh20_atr=(hh20[i]-c[i])/atr[i] if np.isfinite(hh20[i]) else 3.0,
        above_hh20=float(np.isfinite(hh20[i]) and c[i]>hh20[i]),
        eff=eff[i] if eff[i]==eff[i] else 0.0,
        ext_ema20_atr=(c[i]-e20[i])/atr[i],
        ext_ema100_atr=(c[i]-ema100[i])/atr[i],           # overextension vs longer reference
        dist_hh100_atr=(hh100[i]-c[i])/atr[i] if np.isfinite(hh100[i]) else 5.0,  # proximity to major high
        upper_wick_atr=(h[i]-max(o[i],c[i]))/atr[i],
        consec_up=sum(1 for q in range(i,max(i-6,0),-1) if c[q]>c[q-1]),
        hour=dt[i].hour,
        atr_ratio=atr[i]/ama[i] if np.isfinite(ama[i]) and ama[i]>0 else 1.0,
    )
    rows.append(dict(i=i,t=dt[i],bear=bear,bull=bull,is_bear=int(bear>=150 and bear>bull),**feats))
FEATS=[k for k in rows[0] if k not in ("i","t","bear","bull","is_bear")]
# chronological discovery/confirmation split (not by outcome)
cut=rows[int(len(rows)*0.6)]['t']
disc=[r for r in rows if r['t']<cut]; conf=[r for r in rows if r['t']>=cut]
print(f"DISCOVERY n={len(disc)} ({sum(r['is_bear'] for r in disc)} bear) | CONFIRMATION n={len(conf)} ({sum(r['is_bear'] for r in conf)} bear)")
def auc(data, score_fn):
    s=np.array([score_fn(r) for r in data]); y=np.array([r['is_bear'] for r in data])
    p=s[y==1]; q=s[y==0]
    if len(p)==0 or len(q)==0: return np.nan
    r=np.argsort(np.argsort(np.concatenate([p,q])))  # ranks
    return (r[:len(p)].sum()-len(p)*(len(p)-1)/2)/(len(p)*len(q))
# FROZEN linear discriminant: weights = discovery std-diff; standardize with discovery stats
mu={f:np.nanmean([r[f] for r in disc]) for f in FEATS}; sd={f:np.nanstd([r[f] for r in disc])+1e-9 for f in FEATS}
bg=[r for r in disc if r['is_bear']]; cg=[r for r in disc if not r['is_bear']]
W={f:((np.nanmean([r[f] for r in bg])-np.nanmean([r[f] for r in cg]))/sd[f]) for f in FEATS}
def score(r): return sum(W[f]*((r[f]-mu[f])/sd[f]) for f in FEATS)
print(f"\n=== FROZEN LINEAR DISCRIMINANT (weights learned on DISCOVERY) ===")
print(f"  DISCOVERY AUC (in-sample) = {auc(disc,score):.3f}")
print(f"  CONFIRMATION AUC (out-of-sample, FROZEN) = {auc(conf,score):.3f}   [0.50=no signal]")
print("  top weights:", {f:round(W[f],2) for f in sorted(FEATS,key=lambda z:-abs(W[z]))[:5]})
# best single feature AUC on confirmation
print("  best single-feature CONFIRMATION AUC:")
for f in sorted(FEATS,key=lambda z:-abs(auc(conf,lambda r:r[z])-0.5))[:4]:
    print(f"    {f}: {auc(conf,lambda r,ff=f:r[ff]):.3f}")

# ---- SEQUENCE HYPOTHESES (S7): forward bearish rate vs base, on DISCOVERY then CONFIRMATION ----
base_d=np.mean([r['is_bear'] for r in disc]); base_c=np.mean([r['is_bear'] for r in conf])
def seq_rate(data, cond):
    g=[r for r in data if cond(r)]; return (len(g), np.mean([r['is_bear'] for r in g]) if g else np.nan)
SEQS={
 "range_high_rejection": lambda r: r['rangepos']>0.80 and r['upper_wick_atr']>0.5,
 "overext_ema100": lambda r: r['ext_ema100_atr']>2.0,
 "near_major_high": lambda r: r['dist_hh100_atr']<0.5,
 "overext+rejection": lambda r: r['ext_ema100_atr']>1.5 and r['upper_wick_atr']>0.5,
 "rangehigh+overext": lambda r: r['rangepos']>0.75 and r['ext_ema20_atr']>1.0,
 "exhaustion_run": lambda r: r['consec_up']>=4 and r['ext_ema20_atr']>1.0,
}
print(f"\n=== SEQUENCE HYPOTHESES: forward-bearish rate (base DISC {base_d:.2f} / CONF {base_c:.2f}) ===")
for name,cond in SEQS.items():
    nd,rd=seq_rate(disc,cond); nc,rc=seq_rate(conf,cond)
    print(f"  {name:22s}: DISC n={nd} rate={rd:.2f} (lift {rd-base_d:+.2f}) | CONF n={nc} rate={rc:.2f} (lift {rc-base_c:+.2f})")

"""S9 / Gate N trajectory invariance: is the serialized M1 +0.38 a canonical-trajectory artifact?
Compute avgR over MANY alternate valid non-overlapping trajectories of the SAME M1 signal set.
If +0.38 is an outlier far above the raw per-signal mean (+0.08) and the trajectory distribution,
the serialized edge is a serialization artifact, not efficiency-signal value."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import gate_m_audit as G   # reuses populations + sim; re-runs audit prints (ok)
n=G.n; o=G.o;h=G.h;l=G.l;c=G.c;atr=G.atr;TICK=G.TICK;RT=G.RT;RR=G.RR
def sim_xi(si,scen="STRESS"):
    ei=si+1
    if ei>=n-1: return None
    entry=o[ei];stop=min(l[si-4:si+1])-0.15*atr[si];risk=abs(entry-stop)
    if not np.isfinite(risk) or atr[si]!=atr[si] or atr[si]<=0: return None
    me=max(5*TICK,0.10*atr[si])
    if risk<me: risk=me;stop=entry-risk
    if risk<=0: return None
    tgt=entry+RR*risk;cost=RT[scen];to=48;ex=None;xi=None
    for j in range(ei,min(ei+to,n)):
        if l[j]<=stop: ex=stop;xi=j;break
        if h[j]>=tgt: ex=tgt;xi=j;break
    if ex is None: xi=min(ei+to,n-1);ex=c[xi]
    return ((ex-entry)-cost)/risk, ei, xi
def greedy(sigs, order):
    trades=[];last=-1
    for si in order:
        r=sim_xi(si)
        if r is None: continue
        R,ei,xi=r
        if ei>last: trades.append(R);last=xi
    return np.array(trades)
M1=sorted(G.M1)
# canonical (ei ascending)
canon=greedy(M1, sorted(M1))
print(f"CANONICAL (ei-ascending, = frozen policy): n={len(canon)} avgR={canon.mean():.4f}")
# alternate valid trajectories: random shuffles of processing order
rng=np.random.default_rng(0); avgs=[]
for k in range(200):
    order=list(M1); rng.shuffle(order)
    t=greedy(M1, order)
    if len(t): avgs.append(t.mean())
avgs=np.array(avgs)
print(f"200 RANDOM valid trajectories: avgR mean={avgs.mean():.4f} median={np.median(avgs):.4f} p05={np.percentile(avgs,5):.4f} p95={np.percentile(avgs,95):.4f} min={avgs.min():.4f} max={avgs.max():.4f}")
print(f"RAW per-signal mean (all 339): {np.mean([sim_xi(si)[0] for si in M1 if sim_xi(si)]):.4f}")
print(f"=> canonical percentile among random trajectories: {round(float((avgs<canon.mean()).mean())*100,1)}%")
# same for M2 (TREND_UP) for reference
M2=sorted(G.M2); canon2=greedy(M2,sorted(M2))
avgs2=[]
for k in range(100):
    order=list(M2); rng.shuffle(order); t=greedy(M2,order)
    if len(t): avgs2.append(t.mean())
avgs2=np.array(avgs2)
print(f"\nM2 canonical avgR={canon2.mean():.4f} | 100 random trajectories mean={avgs2.mean():.4f} p05={np.percentile(avgs2,5):.4f} p95={np.percentile(avgs2,95):.4f}")

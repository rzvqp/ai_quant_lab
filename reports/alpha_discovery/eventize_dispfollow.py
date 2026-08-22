"""ALPHA-H4-DISP-FOLLOWTHROUGH-EVENTIZATION-001. FROZEN signal: H4 displacement (body>1.0*ATR up at d)
+ follow-through (close[d+1]>close[d]) -> earliest CAUSAL entry OPEN[d+2]. SL/TP/RR/hold/cost frozen.
Only research variable: how overlapping raw signals -> causal trade EVENTS. DEV-only. No d+1 (lookahead).
No CALIB. PROJECT TREND_UP baseline = ema20>ema50 AND effic>0.30 (+0.0144). <=5 new policy IDs."""
import sys, os, numpy as np, pandas as pd
from collections import defaultdict
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import gate_m_audit as G
o=G.o;h=G.h;l=G.l;c=G.c;atr=G.atr;e20=G.e20;e50=G.e50;eff=G.eff;dev=G.dev;yr=G.yr;n=G.n;TICK=G.TICK;RT=G.RT;PIP=G.PIP;RR=G.RR

# ---- frozen signals: i=follow-through bar (d+1), d=i-1 disp bar, entry ei=i+1 (=d+2) ----
SIG=[]
for i in range(51,n-1):
    if atr[i]!=atr[i] or not dev[i]: continue
    if (c[i-1]-o[i-1])>1.0*atr[i-1] and c[i]>c[i-1] and i+1<n-1: SIG.append(i)
def sim(i, scen="STRESS"):
    ei=i+1; entry=o[ei]; stop=min(l[i-4:i+1])-0.15*atr[i]; risk=abs(entry-stop)
    if not np.isfinite(risk) or atr[i]!=atr[i] or atr[i]<=0: return None
    me=max(5*TICK,0.10*atr[i])
    if risk<me: risk=me; stop=entry-risk
    if risk<=0: return None
    tgt=entry+RR*risk; cost=RT[scen]; ex=None; xi=None
    for j in range(ei,min(ei+48,n)):
        if l[j]<=stop: ex=stop;xi=j;break
        if h[j]>=tgt: ex=tgt;xi=j;break
    if ex is None: xi=min(ei+48,n-1); ex=c[xi]
    mfe=max(h[ei:xi+1])-entry if xi>=ei else 0; mae=entry-min(l[ei:xi+1]) if xi>=ei else 0
    return dict(i=i,ei=ei,xi=xi,R=((ex-entry)-cost)/risk,risk=risk,yr=int(yr[i]),mfe=mfe,mae=mae,tp_pips=RR*risk/PIP,sl_pips=risk/PIP)
RAW=[sim(i) for i in SIG]; RAW=[r for r in RAW if r]
print(f"=== FROZEN RAW SIGNAL POPULATION: N={len(RAW)} ===")
Rr=np.array([r['R'] for r in RAW]); Rs=np.sort(Rr)[::-1]
print(f"  medR={np.median(Rr):.3f} avgR={Rr.mean():.4f} top-4 profit share={Rs[:4].sum()/Rs[Rs>0].sum()*100:.1f}% top-10%share={Rs[:max(1,int(len(Rr)*.1))].sum()/Rr[Rr>0].sum()*100:.1f}%")

# ---- clustering (causal, no outcome): inter-signal gaps + displacement runs ----
idx=np.array([r['i'] for r in RAW]); gaps=np.diff(idx)
print(f"\n=== S7 CLUSTERING ===")
print(f"  inter-signal gap (H4 bars): P25={np.percentile(gaps,25):.0f} P50={np.median(gaps):.0f} P75={np.percentile(gaps,75):.0f} min={gaps.min()} %gap<=2={np.mean(gaps<=2)*100:.0f}% %gap<=6={np.mean(gaps<=6)*100:.0f}%")
def clusters(G_):  # new cluster when gap>G_
    cl=[[RAW[0]]]
    for k in range(1,len(RAW)):
        if idx[k]-idx[k-1]>G_: cl.append([])
        cl[-1].append(RAW[k])
    return cl
for Gv in (2,6):
    cl=clusters(Gv); sizes=[len(x) for x in cl]
    print(f"  gap>{Gv} -> {len(cl)} clusters; size P25/P50/P75={np.percentile(sizes,25):.0f}/{np.median(sizes):.0f}/{np.percentile(sizes,75):.0f} max={max(sizes)} %clusters_size1={np.mean(np.array(sizes)==1)*100:.0f}%")

# ---- PROJECT TREND_UP baseline (ema20>ema50 AND effic>0.30), same geometry ----
def baseline_project():
    R=[]
    for i in range(51,n-1):
        if atr[i]!=atr[i] or not dev[i]: continue
        if e20[i]>e50[i] and eff[i]==eff[i] and eff[i]>0.30:
            r=sim(i)
            if r: R.append(r['R'])
    return np.array(R)
PB=baseline_project(); print(f"\nPROJECT TREND_UP baseline (ema20>ema50 & effic>0.30): n={len(PB)} avgR={PB.mean():.4f} (stat ref +0.0144)")

# ---- one-at-a-time causal executor over an eligible signal set (deterministic, path-free) ----
def execute(eligible, cooldown=0):
    trades=[]; last=-1
    for r in eligible:   # eligible pre-sorted by i
        if r['ei']<=last: continue
        trades.append(r); last=r['xi']+cooldown
    return trades
def metrics(trades, scen="STRESS", base=None):
    if len(trades)<5: return dict(n=len(trades))
    R=np.array([sim(t['i'],scen)['R'] for t in trades]); nn=len(R); Rs=np.sort(R)[::-1]; w=R[R>0]; ll=R[R<=0]
    net=R.sum()  # Gate I convention: top-X% of trades' R / TOTAL NET profit (matches Statistician)
    top10=Rs[:max(1,int(nn*.1))].sum()/net*100 if net>0 else 999
    top4=Rs[:4].sum()/net*100 if net>0 else 999
    top1=Rs[:max(1,int(nn*.01))].sum()/net*100 if net>0 else 999
    top5=Rs[:max(1,int(nn*.05))].sum()/net*100 if net>0 else 999
    byy=defaultdict(list)
    for t in trades: byy[t['yr']].append(sim(t['i'],scen)['R'])
    sl=np.array([t['sl_pips'] for t in trades]); tp=np.array([t['tp_pips'] for t in trades])
    return dict(n=nn,WR=round(float((R>=RR-0.05).mean()),3),avgR=round(float(R.mean()),4),medR=round(float(np.median(R)),3),
                pf=round(float(w.sum()/-ll.sum()),3) if ll.sum()<0 else None,maxDD=round(float((np.maximum.accumulate(np.cumsum(R))-np.cumsum(R)).max()),2),
                b5rem=round(float(Rs[max(1,int(nn*.05)):].mean()),4),b10rem=round(float(Rs[max(1,int(nn*.1)):].mean()),4),
                top10share=round(float(top10),1),top4share=round(float(top4),1),top1share=round(float(top1),1),top5share=round(float(top5),1),
                incr=round(float(R.mean()-(base.mean() if base is not None else 0)),4),
                medSL=round(float(np.median(sl)),1),medTP=round(float(np.median(tp)),1),
                temporal={y:(len(v),round(float(np.mean(v)),3)) for y,v in sorted(byy.items())})

# ---- POLICIES (<=5 new, causal, deterministic) ----
# P_FIRST = frozen serialization (reference, existing candidate policy)
def elig_all(): return RAW
# NEWDISP: displacement bar d=i-1 must be a NEW displacement (prior bar i-2 was NOT itself a >1ATR up body)
def elig_newdisp(): return [r for r in RAW if not ((c[r['i']-2]-o[r['i']-2])>1.0*atr[r['i']-2])]
# EPISODE: first signal of each gap<=2 episode (same displacement run)
def elig_episode():
    out=[RAW[0]]
    for k in range(1,len(RAW)):
        if idx[k]-idx[k-1]>2: out.append(RAW[k])
    return out
# FIRSTCLUSTER G=6: first signal of each gap>6 cluster
def elig_cluster6():
    out=[RAW[0]]
    for k in range(1,len(RAW)):
        if idx[k]-idx[k-1]>6: out.append(RAW[k])
    return out
POLICIES=[("REF_FIRST(frozen serialization)",elig_all,0),
          ("H4-DISP-FOLLOW-L-NEWDISP",elig_newdisp,0),
          ("H4-DISP-FOLLOW-L-EPISODE",elig_episode,0),
          ("H4-DISP-FOLLOW-L-CLUSTER6",elig_cluster6,0),
          ("H4-DISP-FOLLOW-L-COOLDOWN6",elig_all,6)]
GATES=lambda m,PB: dict(stress_pos=(m.get('avgR') or -9)>0, b5=(m.get('b5rem') or -9)>0, b10=(m.get('b10rem') or -9)>0,
                        topI=(m.get('top10share') or 999)<=60, incr=(m.get('incr') or -9)>0)
print("\n=== S8/S13 EVENT POLICIES (one-at-a-time causal execution) ===")
res={}
for name,elig,cd in POLICIES:
    tr=execute(elig(),cooldown=cd); m=metrics(tr,base=PB)
    if m.get('n',0)<5: print(f"  {name}: n={m.get('n')} (sparse)"); continue
    g=GATES(m,PB); allpass=all([g['stress_pos'],g['b5'],g['b10'],g['topI'],g['incr']])
    res[name]=(m,g,allpass)
    print(f"  {name}: n={m['n']} WR={m['WR']} avgR={m['avgR']} medR={m['medR']} PF={m['pf']} b5rem={m['b5rem']} b10rem={m['b10rem']} top10%={m['top10share']} incr={m['incr']} medTP={m['medTP']}p")
    print(f"      GATES stress+={g['stress_pos']} b5+={g['b5']} b10+={g['b10']} topI<=60={g['topI']} incr+={g['incr']} => {'ALL_PASS' if allpass else 'FAIL'} | temporal={m['temporal']}")
print("\nSURVIVORS:", [k for k,(m,g,ap) in res.items() if ap and not k.startswith('REF')])

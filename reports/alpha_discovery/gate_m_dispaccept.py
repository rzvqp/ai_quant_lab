"""GATE M audit of MT-H4-dispaccept-L: do displacement+acceptance add alpha beyond H4 LONG trend beta?
Frozen mechanism: disp at bar d (body>1.0*ATR up), acceptance at d+1 (close>close[d]), entry d+2, RR 1.5,
H4 structural SL. Reuses gate_m_audit machinery (identical geometry). Adds displacement/acceptance
attribution (D0/D1/D2) and acceptance-cost (S7). DEV-only. No retuning."""
import sys, os, numpy as np, pandas as pd
from collections import defaultdict
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import gate_m_audit as G   # reuses H4 arrays + sim_one + raw_metrics + ser_metrics (same geometry)
o=G.o;h=G.h;l=G.l;c=G.c;atr=G.atr;e20=G.e20;e50=G.e50;dev=G.dev;yr=G.yr;n=G.n;RR=G.RR
raw=G.raw_metrics; ser=G.ser_metrics; sim1=G.sim_one

# ---- frozen MT-H4-dispaccept-L signal set (acceptance bar i = d+1; disp at i-1=d) ----
def pop_dispaccept():
    S=set()
    for i in range(51,n-1):
        if atr[i]!=atr[i] or not dev[i]: continue
        b=c[i-1]-o[i-1]
        if b>1.0*atr[i-1] and c[i]>c[i-1]: S.add(i)
    return S
M1=pop_dispaccept(); M0=G.M0; M2=G.M2
print("=== S3 POPULATIONS (H4 DEV, LONG) ===")
print(f"  M0(all H4)={len(M0)}  M1(dispaccept, frozen)={len(M1)}  M2(TREND_UP)={len(M2)}")
print(f"  M1 in M2={len(M1&M2)} ({len(M1&M2)/max(1,len(M1))*100:.1f}% of M1 in TREND_UP)  M0 int M1={len(M0&M1)}  M0 int M2={len(M0&M2)}")

print("\n=== S8 SERIALIZED (frozen policy) -- M1 must reproduce published dispaccept (n~41, +0.197) ===")
for nm,S in (("M0",M0),("M1_dispaccept",M1),("M2_TREND_UP",M2)):
    m=ser(S); print(f"  {nm}: n={m['n']} WR={m['WR']} avgR={m['avg']} b5rem={m['b5']} b10rem={m['b10']}")

print("\n=== S4 RAW PER-SIGNAL (trajectory-free = SIGNAL VALUE), STRESS ===")
for nm,S in (("M0",M0),("M1_dispaccept",M1),("M2_TREND_UP",M2)):
    m=raw(S); print(f"  {nm}: n={m['n']} WR={m['WR']} avgR={m['avg']} PF={m['pf']} medR={m['med']} b1rem={m['b1']} b5rem={m['b5']} b10rem={m['b10']} top1={m['top1']} top5={m['top5']} top10={m['top10']}")
print("  BASE avgR:", {nm:raw(S,'BASE')['avg'] for nm,S in (("M0",M0),("M1",M1),("M2",M2))})

print("\n=== S5 CONDITIONAL (within TREND_UP): dispaccept subset vs all TREND_UP ===")
a=raw(M1&M2); b=raw(M2); d=raw(M2-M1)
print(f"  dispaccept-in-uptrend (M1&M2): n={a['n']} avgR={a['avg']} WR={a['WR']} PF={a['pf']} b10rem={a['b10']}")
print(f"  all TREND_UP (M2):            n={b['n']} avgR={b['avg']} WR={b['WR']} PF={b['pf']} b10rem={b['b10']}")
print(f"  TREND_UP NOT dispaccept:      n={d['n']} avgR={d['avg']} WR={d['WR']}")
print(f"  => incremental avgR of dispaccept within TREND_UP: {round((a['avg'] or 0)-(b['avg'] or 0),4)}")

# ---- S6 displacement/acceptance attribution (parent = displacement events d) ----
D=[d for d in range(51,n-2) if atr[d]==atr[d] and dev[d] and dev[d+1] and (c[d]-o[d])>1.0*atr[d]]
D1=set(d for d in D)                    # displacement only: signal d, enter d+1
D2=set(d+1 for d in D if c[d+1]>c[d])   # disp+accept (frozen): signal d+1, enter d+2
Dacc=[d for d in D if c[d+1]>c[d]]      # accepted displacements
print("\n=== S6 DISPLACEMENT / ACCEPTANCE ATTRIBUTION (parent = displacement events) ===")
print(f"  displacement events D={len(D)}; accepted (close[d+1]>close[d])={len(Dacc)} ({len(Dacc)/max(1,len(D))*100:.1f}%)")
mD0=raw(M2); mD1=raw(D1); mD2=raw(D2)
print(f"  D0 TREND_UP ref: n={mD0['n']} avgR={mD0['avg']} WR={mD0['WR']} b10rem={mD0['b10']}")
print(f"  D1 displacement-only (enter d+1): n={mD1['n']} avgR={mD1['avg']} WR={mD1['WR']} b10rem={mD1['b10']}")
print(f"  D2 disp+accept (enter d+2, frozen): n={mD2['n']} avgR={mD2['avg']} WR={mD2['WR']} b10rem={mD2['b10']}")
print(f"  => displacement value (D1 - D0): {round((mD1['avg'] or 0)-(mD0['avg'] or 0),4)} | acceptance incremental (D2 - D1_accepted_only): see S7")

# S7 acceptance cost: on ACCEPTED disp events, compare enter-d+1 (no wait) vs enter-d+2 (accept, frozen)
r_nowait=[];r_wait=[];entrydiff=[];missed_win=0
for d in Dacc:
    a1=sim1(d,"STRESS"); a2=sim1(d+1,"STRESS")
    if a1 and a2:
        r_nowait.append(a1[0]); r_wait.append(a2[0]); entrydiff.append(o[d+2]-o[d+1])  # d+2 entry vs d+1 entry (long: higher=worse)
# missed winners: displacement events NOT accepted whose immediate (d+1) trade would have won
for d in D:
    if c[d+1]>c[d]: continue
    a1=sim1(d,"STRESS")
    if a1 and a1[0]>=RR-0.05: missed_win+=1
r_nowait=np.array(r_nowait);r_wait=np.array(r_wait);entrydiff=np.array(entrydiff)
print("\n=== S7 ACCEPTANCE COST (on accepted displacements) ===")
print(f"  enter d+1 (no wait): avgR={r_nowait.mean():.4f} WR={np.mean(r_nowait>=RR-0.05):.3f}")
print(f"  enter d+2 (accept, frozen): avgR={r_wait.mean():.4f} WR={np.mean(r_wait>=RR-0.05):.3f}")
print(f"  => acceptance-wait dAvgR={r_wait.mean()-r_nowait.mean():.4f} | median entry-price delta (higher=worse for long)={np.median(entrydiff):.2f} USD")
print(f"  missed winners (unaccepted displacements whose d+1 trade would have hit target): {missed_win}")

# ---- S8 trajectory invariance on M1 ----
def sim_xi(si):
    ei=si+1
    if ei>=n-1: return None
    entry=o[ei];stop=min(l[si-4:si+1])-0.15*atr[si];risk=abs(entry-stop)
    if not np.isfinite(risk) or atr[si]!=atr[si] or atr[si]<=0: return None
    me=max(5*G.TICK,0.10*atr[si])
    if risk<me: risk=me;stop=entry-risk
    if risk<=0: return None
    tgt=entry+RR*risk;cost=G.RT["STRESS"];to=48;ex=None;xi=None
    for j in range(ei,min(ei+to,n)):
        if l[j]<=stop: ex=stop;xi=j;break
        if h[j]>=tgt: ex=tgt;xi=j;break
    if ex is None: xi=min(ei+to,n-1);ex=c[xi]
    return ((ex-entry)-cost)/risk,ei,xi
def greedy(order):
    t=[];last=-1
    for si in order:
        r=sim_xi(si)
        if r is None: continue
        R,ei,xi=r
        if ei>last: t.append(R);last=xi
    return np.array(t)
M1s=sorted(M1); canon=greedy(sorted(M1s)); rng=np.random.default_rng(0); avgs=[]
for k in range(200):
    ordr=list(M1s); rng.shuffle(ordr); tt=greedy(ordr)
    if len(tt): avgs.append(tt.mean())
avgs=np.array(avgs)
print("\n=== S8 TRAJECTORY INVARIANCE (M1 dispaccept) ===")
print(f"  canonical(frozen)={canon.mean():.4f} n={len(canon)} | 200 random: mean={avgs.mean():.4f} median={np.median(avgs):.4f} p05={np.percentile(avgs,5):.4f} p95={np.percentile(avgs,95):.4f} min={avgs.min():.4f} max={avgs.max():.4f}")
print(f"  raw per-signal mean(all M1)={raw(M1)['avg']} | canonical percentile={round(float((avgs<canon.mean()).mean())*100,1)}%")

# ---- S9 temporal + S11 geometry ----
print("\n=== S9 TEMPORAL (raw per-signal, STRESS) N/avgR/WR ===")
for nm,S in (("M0",M0),("M1",M1),("M2",M2)):
    m=raw(S);byy=defaultdict(list)
    for r,y in zip(m["_R"],m["_yr"]): byy[int(y)].append(r)
    print(f"  {nm}: "+" ".join(f"{y}:(n{len(v)},avg{round(float(np.mean(v)),3)},wr{round(float(np.mean(np.array(v)>=RR-0.05)),3)})" for y,v in sorted(byy.items())))
# S11 geometry (frozen serialized candidate): SL/TP pips
cfg=dict(G.mstrat.CFG);cfg["spread_ticks"]=0.0;cfg["slip_ticks"]=G.RT["STRESS"]/(2*G.TICK);setups=[]
risks=[]
for si in sorted(M1):
    ei=si+1
    if ei>=n-1: continue
    stop=min(l[si-4:si+1])-0.15*atr[si];entry=o[ei];risk=abs(entry-stop);me=max(5*G.TICK,0.10*atr[si])
    risks.append(max(risk,me))
risks=np.array(risks);tp=RR*risks/G.PIP;slp=risks/G.PIP
print("\n=== S11 GEOMETRY (frozen) ===")
print(f"  nominal RR=1.5 | median SL={np.median(slp):.1f}p median TP={np.median(tp):.1f}p | %TP>=80={np.mean(tp>=80):.2f} >=150={np.mean(tp>=150):.2f} >=200={np.mean(tp>=200):.2f} >=300={np.mean(tp>=300):.2f}")

"""Phase A (corrected): BREAKOUT-CONTINUATION + COMPRESSION-EXPANSION on RESEARCH_LOCAL_RANGE_STRUCTURE_v1.
Breakout = was-in-range then M15 CLOSE beyond boundary (acceptance). Enter next M15 open, M15 structural stop,
measured-move / fixed-RR targets. Path-first + DISC/CONF + year. NO M5 yet."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import range_m15m5 as A   # reuse structure + arrays
o=A.o;h=A.h;l=A.l;c=A.c;atr=A.atr;ama=A.ama;in_range=A.in_range;rhi=A.rhi;rlo=A.rlo;epi=A.epi
dev=A.dev;yr=A.yr;n=A.n;PIP=A.PIP;COST=A.COST;HOR=A.HOR;CUT=A.CUT;width=A.width
from collections import Counter

# breakout setups: bar i where in_range[i-1] and close beyond boundary (acceptance), first per episode-break
def breakout_setups():
    up=[]; dn=[]
    for i in range(A.W+3,n-1):
        if not dev[i] or not np.isfinite(atr[i]): continue
        if in_range[i-1] and np.isfinite(rhi[i]) and c[i]>rhi[i] and h[i-1]<=rhi[i]:   # fresh close above range high
            up.append(dict(i=i,hi=rhi[i],lo=rlo[i],mid=(rhi[i]+rlo[i])/2,w=width[i]))
        if in_range[i-1] and np.isfinite(rlo[i]) and c[i]<rlo[i] and l[i-1]>=rlo[i]:
            dn.append(dict(i=i,hi=rhi[i],lo=rlo[i],mid=(rhi[i]+rlo[i])/2,w=width[i]))
    return up,dn
BU,BD=breakout_setups()
print(f"BREAKOUT setups (M15 close beyond boundary, was-in-range): UP(long)={len(BU)} DOWN(short)={len(BD)}")

def evalbreak(setups, side, tmode, rr=2.0):
    rows=[]
    for s in setups:
        i=s["i"]; e1=i+1
        if e1>=n: continue
        entry=o[e1]; hi=s["hi"]; lo_=s["lo"]; w=s["w"]*PIP
        if side=="LONG":
            stop=min(lo_ if False else hi, l[i])-2.0*PIP  # structural: back inside below setup bar low / range high
            stop=min(hi,l[i])-2.0*PIP
            risk=(entry-stop)/PIP
            tgt=entry+rr*risk*PIP if tmode=="rr" else hi+w   # measured move = +range width above breakout
        else:
            stop=max(lo_,h[i])+2.0*PIP; risk=(stop-entry)/PIP
            tgt=entry-rr*risk*PIP if tmode=="rr" else lo_-w
        if risk<3: continue
        reach=None; mfe=0.0; mae=0.0
        for j in range(e1,min(e1+HOR,n)):
            mae=max(mae,(h[j]-entry)/PIP if side=="SHORT" else (entry-l[j])/PIP)
            mfe=max(mfe,(entry-l[j])/PIP if side=="SHORT" else (h[j]-entry)/PIP)
            hs=(h[j]>=stop) if side=="SHORT" else (l[j]<=stop)
            ht=(l[j]<=tgt) if side=="SHORT" else (h[j]>=tgt)
            if hs and ht: reach=("stop",j); break
            if hs: reach=("stop",j); break
            if ht: reach=("tgt",j); break
        if reach and reach[0]=="tgt": cls="A_clean"; R=(abs(entry-tgt)/PIP)/risk
        elif reach and reach[0]=="stop": cls="C_failure"; R=-1.0
        else: cls="D_stalled"; xb=min(e1+HOR-1,n-1); R=((c[xb]-entry)/PIP if side=="LONG" else (entry-c[xb])/PIP)/risk
        R-=COST/risk
        rows.append(dict(cls=cls,R=R,mfe=mfe,mae=mae,risk=risk,yr=int(yr[i]),i=i))
    return rows

def summ(rows,name):
    if not rows: print(f"  {name}: no rows"); return
    N=len(rows); cc=Counter(r["cls"] for r in rows); Rs=np.array([r["R"] for r in rows]); f=lambda k:cc[k]/N
    d=[r["R"] for r in rows if r["i"]<CUT]; cf=[r["R"] for r in rows if r["i"]>=CUT]
    yy={y:round(float(np.mean([r["R"] for r in rows if r["yr"]==y])),3) for y in (2021,2022,2023) if any(r["yr"]==y for r in rows)}
    s=np.sort(Rs)[::-1]; b10=s[int(len(s)*.1):].mean() if len(s)>10 else np.nan
    print(f"  {name:34}: N{N} A{f('A_clean'):.2f} C{f('C_failure'):.2f} D{f('D_stalled'):.2f} | avgR{Rs.mean():+.3f} medR{np.median(Rs):+.3f} WR{(Rs>0).mean():.2f} b10{b10:+.3f} | D{np.mean(d) if d else np.nan:+.3f} C{np.mean(cf) if cf else np.nan:+.3f} | yy{yy}")

print("\n=== BREAKOUT-CONTINUATION (net STRESS, M15 entry) ===")
for rr in (1.5,2.0,3.0):
    summ(evalbreak(BU,"LONG","rr",rr),f"UPPER-BREAKOUT-LONG rr{rr}")
summ(evalbreak(BU,"LONG","mm"),"UPPER-BREAKOUT-LONG measured-move")
for rr in (1.5,2.0,3.0):
    summ(evalbreak(BD,"SHORT","rr",rr),f"LOWER-BREAKOUT-SHORT rr{rr}")
summ(evalbreak(BD,"SHORT","mm"),"LOWER-BREAKOUT-SHORT measured-move")

# breakout opportunity magnitude
print("\n=== BREAKOUT opportunity magnitude (MFE continuation) ===")
for setups,side,name in ((BU,"LONG","UPPER breakout long"),(BD,"SHORT","LOWER breakout short")):
    r=evalbreak(setups,side,"rr",2.0); mfes=np.array([x["mfe"] for x in r])
    print(f"  {name}: "+" ".join(f">={t}p:{np.mean(mfes>=t):.2f}" for t in (30,50,80,100,150,200,300))+f" | medMFE{np.median(mfes):.0f} medMAE{np.median([x['mae'] for x in r]):.0f}")

# COMPRESSION -> EXPANSION: compression (atr<0.7*ama) in range, then expansion bar (range>1.5*atr) close beyond prior 6-bar hi/lo
def compexp():
    up=[]; dn=[]
    for i in range(A.W+8,n-1):
        if not dev[i] or not np.isfinite(ama[i]): continue
        comp=any(atr[k]<0.7*ama[k] for k in range(i-4,i) if np.isfinite(ama[k]))
        if not (in_range[i-1] and comp): continue
        rng=h[i]-l[i]
        if rng>1.5*atr[i] and c[i]>max(h[i-6:i]): up.append(dict(i=i,hi=rhi[i],lo=rlo[i],w=width[i]))
        if rng>1.5*atr[i] and c[i]<min(l[i-6:i]): dn.append(dict(i=i,hi=rhi[i],lo=rlo[i],w=width[i]))
    return up,dn
CU,CD=compexp()
print(f"\n=== COMPRESSION->EXPANSION setups: UP(long)={len(CU)} DOWN(short)={len(CD)} ===")
for rr in (2.0,3.0):
    summ(evalbreak(CU,"LONG","rr",rr),f"COMPRESSION-EXP-LONG rr{rr}")
    summ(evalbreak(CD,"SHORT","rr",rr),f"COMPRESSION-EXP-SHORT rr{rr}")

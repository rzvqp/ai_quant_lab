"""ALPHA-XAUUSD-RANGE-M15-M5-STRATEGY-DISCOVERY-001 -- PHASE A (M15 structural discovery).
RESEARCH_LOCAL_RANGE_STRUCTURE_v1 (causal, price-only, versioned; NOT canonical MI). Test fade vs
breakout-continuation, UPPER(short)/LOWER(long) SEPARATE, path-first 4-class + opportunity magnitude +
simple expectancy (M15 structural stop, next-M15-open entry). DISC/CONF + year. NO M5 yet (Phase B).
Native M5->M15 (gated). NO MI retuning. DEV-only."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
PIP=0.10; COST=2.4; HOR=48   # forward horizon 48 M15 bars (12h) or range-break, whichever first
tfs,META=D.build(); M=tfs["M15"]
o=M["open"].to_numpy();h=M["high"].to_numpy();l=M["low"].to_numpy();c=M["close"].to_numpy()
atr=M["atr"].to_numpy();ama=M["atr_ma"].to_numpy()
dev=M["is_dev"].to_numpy(); dt=pd.to_datetime(M["time"].to_numpy(),unit="s",utc=True); yr=dt.year.to_numpy(); n=len(o)

# ---- RESEARCH_LOCAL_RANGE_STRUCTURE_v1 (causal) ----
W=24  # trailing window (6h)
sh=pd.Series(h); sl=pd.Series(l); sc=pd.Series(c)
rhi=sh.rolling(W).max().shift(1).to_numpy()      # causal trailing range high
rlo=sl.rolling(W).min().shift(1).to_numpy()      # causal trailing range low
net=sc.shift(1)-sc.shift(W); path=sc.diff().abs().rolling(W).sum().shift(1)
effic=(net/path).to_numpy()                      # trailing directional efficiency
width=(rhi-rlo)/PIP
in_range=(np.abs(effic)<0.35)&(width>=50)&(width<=600)&np.isfinite(atr)&(c<=rhi)&(c>=rlo)
# episode id (contiguous in_range runs)
epi=np.full(n,-1); e=-1; prev=False
for i in range(n):
    if in_range[i] and not prev: e+=1
    if in_range[i]: epi[i]=e
    prev=in_range[i]
print(f"RESEARCH_LOCAL_RANGE_STRUCTURE_v1 (W=24, |effic|<0.35, width 50-600p): in_range bars={int(in_range.sum())} episodes={e+1} median width={np.nanmedian(width[in_range]):.0f}p")

# ---- setups: first UPPER attack + first LOWER attack per episode ----
def setups():
    up=[]; lo=[]; seen_u=set(); seen_l=set()
    for i in range(W+2,n-1):
        if not in_range[i] or not dev[i] or epi[i]<0: continue
        eid=epi[i]
        if h[i]>=rhi[i] and eid not in seen_u: seen_u.add(eid); up.append(dict(i=i,eid=eid,hi=rhi[i],lo=rlo[i],mid=(rhi[i]+rlo[i])/2,width=width[i]))
        if l[i]<=rlo[i] and eid not in seen_l: seen_l.add(eid); lo.append(dict(i=i,eid=eid,hi=rhi[i],lo=rlo[i],mid=(rhi[i]+rlo[i])/2,width=width[i]))
    return up,lo
UP,LO=setups()
print(f"setups: UPPER attacks={len(UP)} (unique episodes) | LOWER attacks={len(LO)}")

# ---- path-first 4-class + expectancy for a mechanism ----
def evaluate(setups, side, mode, target):
    """side SHORT/LONG; mode 'fade'(enter toward mid) or 'breakout'(enter continuation past boundary).
    target 'mid'|'opp'|('rr',x). M15 structural stop. Entry next M15 open. Path-first 4-class."""
    rows=[]
    for s in setups:
        i=s["i"]; e1=i+1
        if e1>=n: continue
        entry=o[e1]; hi=s["hi"]; lo_=s["lo"]; mid=s["mid"]; sweep=h[i] if side=="SHORT" else l[i]
        if mode=="fade":
            if side=="SHORT": stop=sweep+2.0*PIP; tgt=(mid if target=="mid" else lo_)
            else: stop=sweep-2.0*PIP; tgt=(mid if target=="mid" else hi)
        else:  # breakout continuation: enter in the direction of the break; stop back inside boundary
            if side=="LONG": stop=(hi if target!="mid" else mid)-2.0*PIP; tgt=entry+(entry-stop) if target=="rr1" else hi+ (hi-lo_)  # measured move up
            else: stop=(lo_ if target!="mid" else mid)+2.0*PIP; tgt=entry-(stop-entry) if target=="rr1" else lo_-(hi-lo_)
        risk=abs(stop-entry)/PIP
        if risk<3: continue
        adverse_first=False; reach=None; broke=False; mfe=0.0; mae=0.0
        for j in range(e1,min(e1+HOR,n)):
            if epi[j]!=s["eid"] and mode=="fade" and in_range[j]==False: broke=True  # range ended
            up_adv=(h[j]-entry)/PIP if side=="SHORT" else 0; dn_adv=(entry-l[j])/PIP if side=="LONG" else 0
            mae=max(mae,(h[j]-entry)/PIP if side=="SHORT" else (entry-l[j])/PIP)
            mfe=max(mfe,(entry-l[j])/PIP if side=="SHORT" else (h[j]-entry)/PIP)
            hit_stop=(h[j]>=stop) if side=="SHORT" else (l[j]<=stop)
            hit_tgt=(l[j]<=tgt) if side=="SHORT" else (h[j]>=tgt)
            if hit_stop and hit_tgt: reach=("stop",j); break
            if hit_stop: reach=("stop",j); break
            if hit_tgt: reach=("tgt",j); break
        # class
        if reach and reach[0]=="tgt":
            cls="A_clean" if not adverse_first else "B_adv_then_move"
            R=(abs(entry-tgt)/PIP)/risk
        elif reach and reach[0]=="stop":
            cls="C_failure"; R=-1.0
        else:
            cls="D_stalled"; xb=min(e1+HOR-1,n-1); R=((entry-c[xb])/PIP if side=="SHORT" else (c[xb]-entry)/PIP)/risk
        R=R-COST/risk
        rows.append(dict(cls=cls,R=R,mfe=mfe,mae=mae,risk=risk,yr=int(yr[i]),eid=s["eid"],i=i))
    return rows

def summ(rows,name):
    if not rows: print(f"  {name}: no rows"); return None
    from collections import Counter
    N=len(rows); cc=Counter(r["cls"] for r in rows); Rs=np.array([r["R"] for r in rows]); f=lambda k:cc[k]/N
    d=[r for r in rows if r["i"]<CUT]; cf=[r for r in rows if r["i"]>=CUT]
    aD=np.mean([r["R"] for r in d]) if d else np.nan; aC=np.mean([r["R"] for r in cf]) if cf else np.nan
    yy={y:round(float(np.mean([r["R"] for r in rows if r["yr"]==y])),3) for y in (2021,2022,2023) if any(r["yr"]==y for r in rows)}
    print(f"  {name:30}: N{N} A{f('A_clean'):.2f} B{f('B_adv_then_move'):.2f} C{f('C_failure'):.2f} D{f('D_stalled'):.2f} | avgR{Rs.mean():+.3f} medR{np.median(Rs):+.3f} WR{(Rs>0).mean():.2f} | DISC{aD:+.3f} CONF{aC:+.3f} | yy{yy}")
    return dict(N=N,avg=float(Rs.mean()),aD=aD,aC=aC,rows=rows)

# DISC/CONF cut (chronological, by all setups)
allidx=sorted([s["i"] for s in UP+LO]); CUT=allidx[int(len(allidx)*0.6)]
print(f"DISC/CONF cut at M15 idx {CUT} ({dt[CUT].date()})\n")
print("=== PHASE A: MECHANISM x SIDE (path-first 4-class + expectancy, net STRESS, M15 entry) ===")
summ(evaluate(UP,"SHORT","fade","mid"),"UPPER-FADE-SHORT ->mid")
summ(evaluate(UP,"SHORT","fade","opp"),"UPPER-FADE-SHORT ->oppLo")
summ(evaluate(LO,"LONG","fade","mid"),"LOWER-FADE-LONG ->mid")
summ(evaluate(LO,"LONG","fade","opp"),"LOWER-FADE-LONG ->oppHi")
summ(evaluate(UP,"LONG","breakout","mm"),"UPPER-BREAKOUT-LONG (measured move)")
summ(evaluate(LO,"SHORT","breakout","mm"),"LOWER-BREAKOUT-SHORT (measured move)")
summ(evaluate(UP,"LONG","breakout","rr1"),"UPPER-BREAKOUT-LONG rr1")
summ(evaluate(LO,"SHORT","breakout","rr1"),"LOWER-BREAKOUT-SHORT rr1")

# opportunity magnitude (MFE) per side
print("\n=== OPPORTUNITY MAGNITUDE (MFE toward mid, fade setups) ===")
for setups,side,name in ((UP,"SHORT","UPPER short"),(LO,"LONG","LOWER long")):
    r=evaluate(setups,side,"fade","mid"); mfes=np.array([x["mfe"] for x in r])
    print(f"  {name}: "+" ".join(f">={t}p:{np.mean(mfes>=t):.2f}" for t in (30,50,80,100,150,200,300))+f" | medMFE{np.median(mfes):.0f} medMAE{np.median([x['mae'] for x in r]):.0f}")

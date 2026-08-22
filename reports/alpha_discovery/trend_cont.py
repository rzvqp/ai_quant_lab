"""ALPHA-XAUUSD-M15-CONSOLIDATION-TREND-CONTINUATION-M5-ENTRY-001 -- PHASE A (M15 parent discovery).
H1/H4 causal PRICE-ONLY trend context -> M15 consolidation/pullback -> trend RESUMPTION. LONG/SHORT SEPARATE.
Path-first 4-class + opportunity magnitude + expectancy (M15 structural stop, next-M15-open entry, net STRESS).
DISC/CONF + year. NO M5 yet. NOT range research. Native M5->M15/H1/H4 (gated). DEV-only."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
PIP=0.10; COST=2.4; HOR=32
tfs,META=D.build(); M=tfs["M15"]; H1=tfs["H1"]; H4=tfs["H4"]
o=M["open"].to_numpy();h=M["high"].to_numpy();l=M["low"].to_numpy();c=M["close"].to_numpy()
e20=M["ema20"].to_numpy();e50=M["ema50"].to_numpy();atr=M["atr"].to_numpy();ama=M["atr_ma"].to_numpy();eff=M["effic"].to_numpy()
mct=M["close_time"].to_numpy().astype("int64"); dev=M["is_dev"].to_numpy()
yr=pd.to_datetime(M["time"].to_numpy(),unit="s",utc=True).year.to_numpy(); n=len(o)
# align H1/H4 regime to M15 (last completed bar by close_time)
h1ct=H1["close_time"].to_numpy().astype("int64"); h1reg=H1["regime"].to_numpy()
h4ct=H4["close_time"].to_numpy().astype("int64"); h4reg=H4["regime"].to_numpy()
ih1=np.searchsorted(h1ct,mct,side="right")-1; ih4=np.searchsorted(h4ct,mct,side="right")-1
h1_up=np.array([h1reg[k]=="TREND_UP" if k>=0 else False for k in ih1])
h1_dn=np.array([h1reg[k]=="TREND_DOWN" if k>=0 else False for k in ih1])
h4_up=np.array([h4reg[k]=="TREND_UP" if k>=0 else False for k in ih4])
h4_dn=np.array([h4reg[k]=="TREND_DOWN" if k>=0 else False for k in ih4])
print(f"M15 DEV={int(dev.sum())} | H1_up bars={int((h1_up&dev).sum())} H1_dn={int((h1_dn&dev).sum())} | H4_up={int((h4_up&dev).sum())} H4_dn={int((h4_dn&dev).sum())}")

def swings():
    sh=np.zeros(n,bool); sl=np.zeros(n,bool)
    for k in range(2,n-2):
        if h[k]==max(h[k-2:k+3]): sh[k]=True
        if l[k]==min(l[k-2:k+3]): sl[k]=True
    return sh,sl
SH,SL=swings()

# ---- M15 setups (LONG; mirror SHORT). Return list of dict(i, stopref) ----
def setups(mech, side):
    up = h1_up if side=="LONG" else h1_dn; out=[]
    for i in range(30,n-1):
        if not dev[i] or not up[i] or atr[i]!=atr[i]: continue
        if mech=="PB_EMA":   # pullback below ema20 in last 4, then reclaim (close back on trend side of ema20) turning
            if side=="LONG":
                dip=any(c[k]<e20[k] for k in range(i-4,i)); ok=c[i]>e20[i] and c[i]>c[i-1] and e20[i]>e50[i]
                if dip and ok: out.append(dict(i=i,stop=min(l[i-4:i+1])-2*PIP))
            else:
                dip=any(c[k]>e20[k] for k in range(i-4,i)); ok=c[i]<e20[i] and c[i]<c[i-1] and e20[i]<e50[i]
                if dip and ok: out.append(dict(i=i,stop=max(h[i-4:i+1])+2*PIP))
        elif mech=="PB_BREAK":  # shallow pullback then break of recent consolidation extreme in trend dir
            if side=="LONG":
                hh=max(h[i-8:i]); pb=min(l[i-4:i]); shallow=(hh-pb)<0.6*(hh-min(l[i-12:i-4]) if i>=12 else atr[i]*3)
                if c[i]>hh and c[i-1]<=hh and shallow: out.append(dict(i=i,stop=pb-2*PIP))
            else:
                ll=min(l[i-8:i]); pb=max(h[i-4:i]); shallow=(pb-ll)<0.6*(max(h[i-12:i-4])-ll if i>=12 else atr[i]*3)
                if c[i]<ll and c[i-1]>=ll and shallow: out.append(dict(i=i,stop=pb+2*PIP))
        elif mech=="COMP_EXP":  # compression in trend then trend-dir expansion bar
            comp=any(atr[k]<0.75*ama[k] for k in range(i-4,i) if np.isfinite(ama[k])); rng=h[i]-l[i]
            if side=="LONG":
                if comp and rng>1.4*atr[i] and c[i]>o[i] and c[i]>max(h[i-4:i]): out.append(dict(i=i,stop=min(l[i-2:i+1])-2*PIP))
            else:
                if comp and rng>1.4*atr[i] and c[i]<o[i] and c[i]<min(l[i-4:i]): out.append(dict(i=i,stop=max(h[i-2:i+1])+2*PIP))
    # ownership: dedupe within 4 bars (one event per cluster)
    ded=[]; last=-99
    for s in out:
        if s["i"]-last>=4: ded.append(s); last=s["i"]
    return ded

def evalr(sset, side, rr, mode="rr"):
    rows=[]
    for s in sset:
        i=s["i"]; e1=i+1
        if e1>=n: continue
        entry=o[e1]; stop=s["stop"]; risk=abs(entry-stop)/PIP
        if risk<3 or risk>200: continue
        tgt=entry+rr*risk*PIP if side=="LONG" else entry-rr*risk*PIP
        reach=None; mfe=0.0; mae=0.0
        for j in range(e1,min(e1+HOR,n)):
            fav=(h[j]-entry)/PIP if side=="LONG" else (entry-l[j])/PIP
            adv=(entry-l[j])/PIP if side=="LONG" else (h[j]-entry)/PIP
            mfe=max(mfe,fav); mae=max(mae,adv)
            hs=(l[j]<=stop) if side=="LONG" else (h[j]>=stop)
            ht=(h[j]>=tgt) if side=="LONG" else (l[j]<=tgt)
            if hs and ht: reach=("stop",j); break
            if hs: reach=("stop",j); break
            if ht: reach=("tgt",j); break
        if reach and reach[0]=="tgt":
            cls="A_clean" if mae<0.7*risk else "B_adv_then_cont"; R=rr
        elif reach and reach[0]=="stop": cls="C_reversal"; R=-1.0
        else: xb=min(e1+HOR-1,n-1); R=((c[xb]-entry)/PIP if side=="LONG" else (entry-c[xb])/PIP)/risk; cls="D_stall"
        R-=COST/risk
        rows.append(dict(cls=cls,R=R,mfe=mfe,mae=mae,risk=risk,yr=int(yr[i]),i=i))
    return rows

allidx=[]
for m in ("PB_EMA","PB_BREAK","COMP_EXP"):
    for sd in ("LONG","SHORT"): allidx+=[s["i"] for s in setups(m,sd)]
allidx=sorted(allidx); CUT=allidx[int(len(allidx)*0.6)]
from collections import Counter
def summ(rows,name):
    if not rows or len(rows)<10: print(f"  {name:26}: N{len(rows) if rows else 0} (too few)"); return
    N=len(rows); cc=Counter(r["cls"] for r in rows); Rs=np.array([r["R"] for r in rows]); f=lambda k:cc[k]/N
    d=[r["R"] for r in rows if r["i"]<CUT]; cf=[r["R"] for r in rows if r["i"]>=CUT]
    s=np.sort(Rs)[::-1]; b10=s[int(len(s)*.1):].mean() if len(s)>10 else np.nan
    yy={y:round(float(np.mean([r["R"] for r in rows if r["yr"]==y])),3) for y in (2021,2022,2023) if any(r["yr"]==y for r in rows)}
    flag="  <==" if (Rs.mean()>0 and (np.mean(d) if d else -9)>0 and (np.mean(cf) if cf else -9)>0) else ""
    print(f"  {name:26}: N{N} A{f('A_clean'):.2f} B{f('B_adv_then_cont'):.2f} C{f('C_reversal'):.2f} D{f('D_stall'):.2f} | avgR{Rs.mean():+.3f} medR{np.median(Rs):+.3f} WR{(Rs>0).mean():.2f} b10{b10:+.3f} | D{np.mean(d) if d else np.nan:+.3f} C{np.mean(cf) if cf else np.nan:+.3f} | {yy}{flag}")

print(f"\n=== PHASE A: M15 TREND-CONTINUATION (path-first, net STRESS, M15 entry) cut {pd.to_datetime(mct[CUT],unit='s',utc=True).date()} ===")
for m in ("PB_EMA","PB_BREAK","COMP_EXP"):
    for sd in ("LONG","SHORT"):
        ss=setups(m,sd)
        for rr in (1.5,2.0,3.0):
            summ(evalr(ss,sd,rr),f"{m}-{sd} rr{rr}")
print("\n=== OPPORTUNITY MAGNITUDE (MFE) per mechanism/side ===")
for m in ("PB_EMA","PB_BREAK","COMP_EXP"):
    for sd in ("LONG","SHORT"):
        r=evalr(setups(m,sd),sd,2.0);
        if len(r)<10: continue
        mfes=np.array([x["mfe"] for x in r])
        print(f"  {m}-{sd}: N{len(r)} "+" ".join(f">={t}:{np.mean(mfes>=t):.2f}" for t in (30,50,80,100,150,200))+f" medMFE{np.median(mfes):.0f} medMAE{np.median([x['mae'] for x in r]):.0f}")

"""ALPHA-H4-DISP-FOLLOW-L-COOLDOWN6-CALIB-001. ONE frozen CALIB pass. K=6 ONLY. No retuning.
Frozen identity recovered from eventize_dispfollow (commit 696e46b): H4 displacement (body>1.0*ATR up at d)
+ follow-through (close[d+1]>close[d]) -> entry OPEN[d+2], H4 structural SL, RR 1.5, one-at-a-time +
6-H4-bar post-exit cooldown. PROJECT TREND_UP baseline = ema20>ema50 AND effic>0.30. DEV untouched."""
import sys, os, numpy as np, pandas as pd
from collections import defaultdict
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import eventize_dispfollow as E
import gate_m_audit as G
o=E.o;h=E.h;l=E.l;c=E.c;atr=E.atr;e20=E.e20;e50=E.e50;eff=E.eff;n=E.n;PIP=E.PIP;RR=E.RR;RT=E.RT
cal=G.x["is_cal"].to_numpy(); dt=pd.to_datetime(G.x["time"],unit="s",utc=True)

# ---- CALIB population identity ----
cmask=cal & (~np.isnan(atr))
print("=== CALIB POPULATION IDENTITY ===")
print(f"  H4 CALIB bars={int(cal.sum())} | date range {dt[cal].min()} -> {dt[cal].max()}")
print(f"  (source: gated M5 CALIB 2024-01-01 23:00Z -> 2024-06-20 00:40Z, 33,309 M5 bars, ohlc_sha256 3c170953..., timeline 24e51ef4...; H4 causally aggregated)")

# ---- FROZEN COOLDOWN6 on CALIB (one pass) ----
CSIG=[i for i in range(51,n-1) if atr[i]==atr[i] and cal[i] and (c[i-1]-o[i-1])>1.0*atr[i-1] and c[i]>c[i-1] and i+1<n-1]
CRAW=[E.sim(i) for i in CSIG]; CRAW=[r for r in CRAW if r]
trades=E.execute(CRAW, cooldown=6)   # K=6 frozen
def full(trades, scen="STRESS"):
    R=np.array([E.sim(t['i'],scen)['R'] for t in trades]); nn=len(R)
    if nn==0: return None
    Rs=np.sort(R)[::-1]; w=R[R>0]; ll=R[R<=0]; net=R.sum()
    sl=np.array([t['sl_pips'] for t in trades]); tp=np.array([t['tp_pips'] for t in trades])
    mfe=np.array([t['mfe']/PIP for t in trades]); mae=np.array([t['mae']/PIP for t in trades]); holds=np.array([t['xi']-t['ei'] for t in trades])
    top=lambda p: round(float(Rs[:max(1,int(nn*p))].sum()/net*100),1) if net>0 else 999
    rem=lambda p: round(float(Rs[max(1,int(nn*p)):].mean()),4)
    return dict(n=nn,WR=round(float((R>=RR-0.05).mean()),3),avgR=round(float(R.mean()),4),medR=round(float(np.median(R)),3),
        pf=round(float(w.sum()/-ll.sum()),3) if ll.sum()<0 else None,maxDD=round(float((np.maximum.accumulate(np.cumsum(R))-np.cumsum(R)).max()),2),maxLoss=round(float(R.min()),3),
        avgW=round(float(w.mean()),3) if len(w) else None,nW=len(w),avgL=round(float(ll.mean()),3) if len(ll) else None,nL=len(ll),
        top1=top(.01),top5=top(.05),top10=top(.1),b1rem=rem(.01),b5rem=rem(.05),b10rem=rem(.1),
        medSL=round(float(np.median(sl)),1),medTP=round(float(np.median(tp)),1),TPp25=round(float(np.percentile(tp,25)),1),TPp75=round(float(np.percentile(tp,75)),1),
        pTP80=round(float(np.mean(tp>=80)),2),pTP100=round(float(np.mean(tp>=100)),2),pTP150=round(float(np.mean(tp>=150)),2),pTP200=round(float(np.mean(tp>=200)),2),pTP300=round(float(np.mean(tp>=300)),2),pTP400=round(float(np.mean(tp>=400)),2),
        medMAE=round(float(np.median(mae)),0),medMFE=round(float(np.median(mfe)),0),medHold=round(float(np.median(holds)),0),
        byyr={int(y):(len([1 for t in trades if t['yr']==y]),round(float(np.mean([E.sim(t['i'],scen)['R'] for t in trades if t['yr']==y])),3)) for y in sorted(set(t['yr'] for t in trades))},
        _R=R)
mS=full(trades,"STRESS"); mB=full(trades,"BASE")
# PROJECT TREND_UP baseline on CALIB
PBc=[]
for i in range(51,n-1):
    if atr[i]==atr[i] and cal[i] and e20[i]>e50[i] and eff[i]==eff[i] and eff[i]>0.30:
        r=E.sim(i)
        if r: PBc.append(r['R'])
PBc=np.array(PBc)
print(f"\n=== CALIB ECONOMICS (frozen COOLDOWN6, K=6, STRESS) ===")
if mS is None: print("  n=0 -- no CALIB signals"); sys.exit()
print(f"  N={mS['n']} WR={mS['WR']} BASE={mB['avgR']} STRESS={mS['avgR']} PF={mS['pf']} maxDD={mS['maxDD']}R maxLoss={mS['maxLoss']}R")
print(f"  medR={mS['medR']} avgWinner={mS['avgW']}(n{mS['nW']}) avgLoser={mS['avgL']}(n{mS['nL']}) medMAE={mS['medMAE']}p medMFE={mS['medMFE']}p medHold={mS['medHold']} nominal/effRR=1.5")
print(f"=== TAIL (Gate I: top-10% net-profit share <=60%) ===")
print(f"  top1/5/10 share={mS['top1']}/{mS['top5']}/{mS['top10']}% | best-1/5/10-removed={mS['b1rem']}/{mS['b5rem']}/{mS['b10rem']}")
print(f"=== MEDIAN TRADE ===  CALIB medR={mS['medR']} (DEV was +0.413)")
print(f"=== PROJECT TREND_UP (ema20>ema50 & effic>0.30) on CALIB ===")
print(f"  candidate STRESS={mS['avgR']} | PROJECT TREND_UP={round(float(PBc.mean()),4)}(n{len(PBc)}) | incremental={round(float(mS['avgR']-PBc.mean()),4)}")
print(f"=== GEOMETRY ===")
print(f"  medSL={mS['medSL']}p medTP={mS['medTP']}p TP P25/P75={mS['TPp25']}/{mS['TPp75']}p | %TP>=80={mS['pTP80']} >=100={mS['pTP100']} >=150={mS['pTP150']} >=200={mS['pTP200']} >=300={mS['pTP300']} >=400={mS['pTP400']}")
print(f"=== TEMPORAL (CALIB is one ~5.5mo segment; per-year) ===  {mS['byyr']}")
# monthly breakdown (report only if cells meaningful)
mon=defaultdict(list)
for t in trades: mon[pd.Timestamp(dt[t['i']]).strftime('%Y-%m')].append(E.sim(t['i'])['R'])
print(f"  monthly: {{ {', '.join(f'{k}:(n{len(v)},{round(float(np.mean(v)),2)})' for k,v in sorted(mon.items()))} }}")

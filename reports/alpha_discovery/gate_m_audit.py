"""GATE M audit: does `effic > 0.4` add alpha beyond simple H4 LONG trend beta?
Frozen candidate MT-H4-efficiency-L geometry UNCHANGED. Only the signal condition varies:
  M0_ALL_H4_REFERENCE   = every H4 bar LONG (remove effic filter entirely)
  M1_EFFICIENCY_FILTERED = effic[i] > 0.4        (the frozen candidate)
  M2_TREND_UP_REFERENCE  = ema20 > ema50 (bullish regime, NO efficiency)
Report raw opportunity populations + intersections (S4), then RAW per-signal expectancy
(trajectory-free -> pure SIGNAL FILTER value) AND SERIALIZED frozen-policy (mstrat) expectancy.
DEV-only. No CALIB for selection. No retuning."""
import sys, os, json, numpy as np, pandas as pd
from collections import defaultdict
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import multitf_campaign as MC
mstrat=MC.mstrat; TICK=MC.TICK; PIP=MC.PIP; RT=MC.RT
x=MC.tfs["H4"]
o=x["open"].to_numpy();h=x["high"].to_numpy();l=x["low"].to_numpy();c=x["close"].to_numpy()
atr=x["atr"].to_numpy();eff=x["effic"].to_numpy();e20=x["ema20"].to_numpy();e50=x["ema50"].to_numpy()
dev=x["is_dev"].to_numpy();yr=pd.to_datetime(x["time"],unit="s",utc=True).dt.year.to_numpy();n=len(x)
RR=1.5

# ---- raw opportunity populations (LONG), same i-range/atr gate as the frozen gen ----
def pop(kind):
    S=[]
    for i in range(51,n-1):
        if atr[i]!=atr[i] or not dev[i]: continue
        if kind=="M0": ok=True
        elif kind=="M1": ok=(eff[i]==eff[i] and eff[i]>0.4)
        elif kind=="M2": ok=(e20[i]>e50[i])
        if ok: S.append(i)
    return set(S)
M0,M1,M2=pop("M0"),pop("M1"),pop("M2")
print("=== S4 OPPORTUNITY POPULATIONS (H4 DEV, LONG) ===")
print(f"  raw M0(all H4)={len(M0)}  M1(effic>0.4)={len(M1)}  M2(ema20>ema50)={len(M2)}")
print(f"  M1 in M2 (effic signals that are in uptrend): {len(M1&M2)} ({len(M1&M2)/max(1,len(M1))*100:.1f}% of M1)")
print(f"  M1 as % of all H4 opps (M0): {len(M1)/len(M0)*100:.1f}% | M1 as % of TREND_UP opps (M2): {len(M1)/max(1,len(M2))*100:.1f}%")

# ---- per-signal simulator (NO serialization) replicating mstrat single-trade logic exactly ----
def sim_one(si, scen):
    ei=si+1
    if ei>=n-1: return None
    entry=o[ei]; stop=min(l[si-4:si+1])-0.15*atr[si]; risk=abs(entry-stop)
    if not np.isfinite(risk) or atr[si]!=atr[si] or atr[si]<=0: return None
    min_exec=max(5*TICK,0.10*atr[si])           # spread_ticks=0
    if risk<min_exec: risk=min_exec; stop=entry-risk
    if risk<=0: return None
    tgt=entry+RR*risk; cost=RT[scen]; to=48; ex=None
    for j in range(ei,min(ei+to,n)):
        if l[j]<=stop: ex=stop; break
        if h[j]>=tgt: ex=tgt; break
    if ex is None: ex=c[min(ei+to,n-1)]
    return ((ex-entry)-cost)/risk, risk, yr[si]

def raw_metrics(S, scen="STRESS"):
    R=[];risks=[];yrs=[]
    for si in sorted(S):
        r=sim_one(si,scen)
        if r is not None: R.append(r[0]);risks.append(r[1]);yrs.append(r[2])
    if not R: return dict(n=0)
    R=np.array(R);Rs=np.sort(R)[::-1];nn=len(R);w=R[R>0];lo=R[R<=0];tot=R.sum()
    return dict(n=nn,WR=round(float((R>=RR-0.05).mean()),3),avg=round(float(R.mean()),4),med=round(float(np.median(R)),3),
                pf=round(float(w.sum()/-lo.sum()),3) if lo.sum()<0 else None,
                maxDD=round(float((np.maximum.accumulate(np.cumsum(R))-np.cumsum(R)).max()),2),
                b1=round(float(Rs[max(1,int(nn*.01)):].mean()),4),b5=round(float(Rs[max(1,int(nn*.05)):].mean()),4),b10=round(float(Rs[max(1,int(nn*.1)):].mean()),4),
                top1=round(float(Rs[:max(1,int(nn*.01))].sum()/tot),3) if tot>0 else None,top5=round(float(Rs[:max(1,int(nn*.05))].sum()/tot),3) if tot>0 else None,top10=round(float(Rs[:max(1,int(nn*.1))].sum()/tot),3) if tot>0 else None,
                _R=R,_yr=np.array(yrs))
def ser_metrics(S, scen="STRESS"):  # SERIALIZED via mstrat (frozen policy, non-overlap guard)
    cfg=dict(mstrat.CFG);cfg["spread_ticks"]=0.0;cfg["slip_ticks"]=RT[scen]/(2*TICK);setups=[]
    for si in sorted(S):
        ei=si+1
        if ei>=n-1: continue
        stop=min(l[si-4:si+1])-0.15*atr[si]
        setups.append(dict(si=si,ei=ei,dir=1,stop=float(stop),exit_kind="rr",exit_param=float(RR)))
    led=mstrat.simulate(x,setups,cfg); R=led["R"].to_numpy()
    if len(R)==0: return dict(n=0)
    return dict(n=len(R),WR=round(float((R>=RR-0.05).mean()),3),avg=round(float(R.mean()),4),
                b5=round(float(np.sort(R)[::-1][max(1,int(len(R)*.05)):].mean()),4),b10=round(float(np.sort(R)[::-1][max(1,int(len(R)*.1)):].mean()),4))

print("\n=== RAW PER-SIGNAL (no serialization -> pure SIGNAL FILTER value), STRESS ===")
for nm,S in (("M0_ALL_H4",M0),("M1_EFFICIENCY",M1),("M2_TREND_UP",M2)):
    m=raw_metrics(S); print(f"  {nm}: n={m['n']} WR={m['WR']} avgR={m['avg']} PF={m['pf']} maxDD={m['maxDD']} b1rem={m['b1']} b5rem={m['b5']} b10rem={m['b10']} top1share={m['top1']} top5={m['top5']} top10={m['top10']}")
print("\n=== SERIALIZED (frozen mstrat policy), STRESS -- M1 must reproduce the frozen candidate ===")
for nm,S in (("M0_ALL_H4",M0),("M1_EFFICIENCY",M1),("M2_TREND_UP",M2)):
    m=ser_metrics(S); print(f"  {nm}: n={m['n']} WR={m['WR']} avgR={m['avg']} b5rem={m['b5']} b10rem={m['b10']}")

# ---- BASE too for the deltas ----
print("\n=== RAW PER-SIGNAL, BASE ===")
mb={nm:raw_metrics(S,"BASE") for nm,S in (("M0",M0),("M1",M1),("M2",M2))}
for nm in ("M0","M1","M2"): print(f"  {nm}: avgR(BASE)={mb[nm]['avg']}")

# ---- S8 THE KEY DIAGNOSTIC: within TREND_UP, effic subset vs all TREND_UP ----
print("\n=== S8 REGIME-CONDITIONED (within TREND_UP): effic>0.4 subset vs ALL TREND_UP ===")
m1m2=raw_metrics(M1&M2); m2only=raw_metrics(M2); m2_noeff=raw_metrics(M2-M1)
print(f"  (M1 in M2) effic-in-uptrend: n={m1m2['n']} avgR={m1m2['avg']} WR={m1m2['WR']} b10rem={m1m2['b10']}")
print(f"  M2 all TREND_UP:            n={m2only['n']} avgR={m2only['avg']} WR={m2only['WR']} b10rem={m2only['b10']}")
print(f"  M2 minus effic (uptrend, NOT effic>0.4): n={m2_noeff['n']} avgR={m2_noeff['avg']} WR={m2_noeff['WR']}")
print(f"  => incremental avgR of effic within TREND_UP: {round((m1m2['avg'] or 0)-(m2only['avg'] or 0),4)} (effic-subset minus all-TREND_UP)")

# ---- S6 temporal: M0/M1/M2 per year (raw per-signal, STRESS) ----
print("\n=== S6 TEMPORAL (raw per-signal, STRESS) N / avgR / WR per year ===")
for nm,S in (("M0",M0),("M1",M1),("M2",M2)):
    m=raw_metrics(S); byy=defaultdict(list)
    for r,y in zip(m["_R"],m["_yr"]): byy[int(y)].append(r)
    row={y:(len(v),round(float(np.mean(v)),3),round(float(np.mean(np.array(v)>=RR-0.05)),3)) for y,v in sorted(byy.items())}
    print(f"  {nm}: "+" ".join(f"{y}:(n{v[0]},avg{v[1]},wr{v[2]})" for y,v in row.items()))

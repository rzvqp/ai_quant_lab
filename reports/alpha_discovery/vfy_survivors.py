"""vfy_survivors.py — ADVERSARIAL verification of gov_screen survivors. (1) S49 artifact probe: median risk(ATR), median hold(bars), exit mix,
sub-scale scalp check. (2) long-beta control: buy-every-N baseline at real cost. (3) opposite-side / opposite-context counterparts of the believable
survivors (long-beta falsification) + era1 (2011-2016, incl 2013 crash) positivity."""
import os, sys, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery"); sys.path.insert(0, os.path.join(AA,"code"))
import mstrat; import mstrat_ext as ME
from alpha_lab import CFG
mstrat.TICK=0.01
if hasattr(ME,"TICK"): ME.TICK=0.01
d=mstrat.load(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); Lo=d["low"].to_numpy(float); C=d["close"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); T=d["time"].to_numpy(); n=len(d)
yr=pd.to_datetime(T,unit="s",utc=True).year.to_numpy()
def cfg(rt): c=dict(CFG); c["spread_ticks"]=rt/(2*mstrat.TICK); c["slip_ticks"]=0.0; return c
def instrumented(setups, rt):
    """re-sim recording risk(ATR-normalized) and hold bars + exit reason."""
    cost=rt/2; rows=[]; last=-1
    for s in sorted(setups,key=lambda x:x["ei"]):
        ei=s["ei"]; si=s["si"]
        if ei<=last or ei>=n-1 or ei<1: continue
        dirn=s["dir"]; entry=O[ei]; stop=s["stop"]; risk=abs(entry-stop)
        if not np.isfinite(risk) or ATR[si]<=0 or np.isnan(ATR[si]): continue
        min_exec=max(2*cfg(rt)["spread_ticks"]*mstrat.TICK,5*mstrat.TICK,0.10*ATR[si])
        if risk<min_exec: risk=min_exec; stop=entry-dirn*risk
        ek=s["exit_kind"]; ep=s.get("exit_param"); to=int(ep) if ek=="time" else 48
        tgt=entry+dirn*ep*risk if ek=="rr" else (ep if ek in ("opp_liq","opp_struct") else None)
        ex=None; xi=None
        for j in range(ei,min(ei+to,n)):
            if dirn>0:
                if Lo[j]<=stop: ex=stop;xi=j;reason="stop";break
                if tgt is not None and np.isfinite(tgt) and H[j]>=tgt: ex=tgt;xi=j;reason="tgt";break
            else:
                if H[j]>=stop: ex=stop;xi=j;reason="stop";break
                if tgt is not None and np.isfinite(tgt) and Lo[j]<=tgt: ex=tgt;xi=j;reason="tgt";break
        if ex is None: xi=min(ei+to,n-1); ex=C[xi]; reason="time"
        R=(dirn*(ex-entry)-2*cost)/risk
        rows.append(dict(R=R,riskATR=risk/ATR[si],hold=xi-ei,reason=reason,year=yr[ei]))
        last=xi
    return pd.DataFrame(rows)
# (1) S49 probe (top config: N=4, mode=fade, stop=bar, exit=time)
h49=dict(N=4,mode="fade",stop="bar",exit="time",family="S49")
su=ME.s49_setups(d,h49); tr=instrumented(su,0.24)
print(f"[S49 fade/bar/time] N={len(tr)} exp={tr.R.mean():+.4f} WR={(tr.R>0).mean():.3f} | median riskATR={tr.riskATR.median():.3f} median hold(bars)={tr.hold.median():.1f} exit_mix={tr.reason.value_counts(normalize=True).round(2).to_dict()}")
print(f"   -> sub-scale scalp? riskATR<0.25 in {100*(tr.riskATR<0.25).mean():.0f}% of trades; hold<=2 bars in {100*(tr.hold<=2).mean():.0f}%")
# (2) long-beta baseline: buy every 96 bars, 1ATR stop, rr2, full history at 0.24
lb=[]
last=-1
for i in range(60,n-2,1):
    if i<=last: continue
    if (i%96)!=0: continue
    ei=i+1; entry=O[ei]; risk=max(1.0*ATR[i],0.10*ATR[i]); stop=entry-risk; tgt=entry+2*risk
    end=min(ei+48,n-1); R=None
    for k in range(ei,end+1):
        if Lo[k]<=stop: R=-1.0;xi=k;break
        if H[k]>=tgt: R=2.0;xi=k;break
    else: xi=end; R=(C[end]-entry)/risk
    lb.append((R-0.24/risk, yr[i])); last=xi
lb=pd.DataFrame(lb,columns=["R","year"]); print(f"[LONG-BETA baseline buy-every-96 1ATR rr2 @0.24] N={len(lb)} exp={lb.R.mean():+.4f} recent2025+={lb[lb.year>=2025].R.mean():+.4f}")
# (3) opposite counterparts of believable survivors
def run(gen,h,rt=0.24):
    su=gen(d,h);
    if not su: return None
    tr=instrumented(su,rt);
    if len(tr)<50: return None
    th=np.array_split(tr.sort_index().R.to_numpy(),3) if False else None
    r=tr.R.to_numpy(); # era by year
    e1=r[tr.year<=2016]; e2=r[(tr.year>2016)&(tr.year<=2021)]; e3=r[tr.year>2021]; rec=r[tr.year>=2025]
    return dict(N=len(r),exp=round(float(r.mean()),4),WR=round(float((r>0).mean()),3),PF=round(float(r[r>0].sum()/(abs(r[r<=0].sum())+1e-9)),3),
                era1=round(float(e1.mean()),4) if len(e1)>20 else None,era2=round(float(e2.mean()),4) if len(e2)>20 else None,era3=round(float(e3.mean()),4) if len(e3)>20 else None,
                recent=round(float(rec.mean()),4) if len(rec)>20 else None)
print("\n== BELIEVABLE SURVIVORS: long vs opposite (long-beta falsification) + era1(2011-16 incl 2013 crash) ==")
pairs=[
 ("S5 ORB ny UP",   mstrat.s5_setups, dict(session="ny",mode="breakout",stop="or_opp",exit="rr3",side="up",family="S5")),
 ("S5 ORB ny DOWN", mstrat.s5_setups, dict(session="ny",mode="breakout",stop="or_opp",exit="rr3",side="down",family="S5")),
 ("S9 c4h=up align rr3", mstrat.s9_setups, dict(c4h="up",conf1h="align",lb=20,stop="atr",exit="rr3",family="S9")),
 ("S9 c4h=down align rr3", mstrat.s9_setups, dict(c4h="down",conf1h="align",lb=20,stop="atr",exit="rr3",family="S9")),
 ("S20 h4up breakout rr3", ME.s20_setups if hasattr(ME,'s20_setups') else mstrat.s20_setups, dict(ctx="h4up",trig="breakout",lb=50,stop="atr",exit="rr3",family="S20")),
 ("S20 h4down breakout rr3", ME.s20_setups if hasattr(ME,'s20_setups') else mstrat.s20_setups, dict(ctx="h4down",trig="breakout",lb=50,stop="atr",exit="rr3",family="S20")),
 ("S1 pdh sweep HIGH rr3", mstrat.s1_setups, dict(side="high",liq_ref="pdh_pdl",liq_lb=20,confirm="displacement",imb="none",stop="beyond_sweep",exit="rr3",window=8,family="S1")),
 ("S1 pdl sweep LOW rr3",  mstrat.s1_setups, dict(side="low",liq_ref="pdh_pdl",liq_lb=20,confirm="displacement",imb="none",stop="beyond_sweep",exit="rr3",window=8,family="S1")),
]
for name,gen,h in pairs:
    try: m=run(gen,h)
    except Exception as e: m=f"ERR {e}"
    print(f"  {name:28s} {m}")

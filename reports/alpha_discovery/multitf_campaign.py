"""ALPHA-XAUUSD-MULTITF-M5-M15-H1-H4-DISCOVERY-001.
Broad Alpha search across M5/M15/H1/H4 as PRIMARY edge timeframes. Corrected architecture:
STRUCTURAL SL on the EDGE timeframe (K-bar swing, NOT the smallest TF), economic RR target, coarse
edge-TF entry. Mechanism-diverse (pullback/breakout/compression/momentum/efficiency/disp-accept/structure),
both directions, regime recorded. Gated M5 -> causal M15/H1/H4 (m5_data). NO N4/2025+/read_csv.
Cost tick 0.01 / STRESS 0.24. DEV screen only; CALIB reserved for frozen survivors. <=80 IDs, ck 20/40/60."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
WP5B=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"
if WP5B not in sys.path: sys.path.insert(0,WP5B)
import mstrat
PIP=0.10; TICK=mstrat.TICK
RT={"GROSS":0.0,"BASE":0.05,"STRESS":0.24}
def log(m): print(f"[{int(time.time())}] {m}",flush=True); open(os.path.join(SP,"multitf.log"),"a").write(f"{int(time.time())} {m}\n")

tfs,META=D.build()
# ensure mstrat-compatible column + regime for all TFs
for tf in ("M5","M15","H1","H4"):
    x=tfs[tf]; x["m_atr"]=x["atr"]
    if "regime" not in x: x=D.regime_label(x); tfs[tf]=x
log(f"loader file_sha={META['data_file_sha256'][:16]} | "+", ".join(f"{tf}:DEV{int(tfs[tf]['is_dev'].sum())}" for tf in ('M5','M15','H1','H4')))

# ---------- generic mechanisms: yield (i, side) on a TF frame ----------
def arrs(x): return (x["open"].to_numpy(),x["high"].to_numpy(),x["low"].to_numpy(),x["close"].to_numpy(),
                     x["atr"].to_numpy(),x["ema20"].to_numpy(),x["ema50"].to_numpy(),x["hh20"].to_numpy(),
                     x["ll20"].to_numpy(),x["effic"].to_numpy(),x["atr_ma"].to_numpy())
def gen(mech,long,x):
    o,h,l,c,atr,e20,e50,hh,ll,eff,ama=arrs(x); n=len(x); out=[]; up=long
    for i in range(51,n-1):
        if atr[i]!=atr[i]: continue
        s=1 if up else -1; ok=False
        if mech=="pullback":
            if up: ok = e20[i]>e50[i] and l[i-1]<e20[i-1] and c[i]>c[i-1]
            else:  ok = e20[i]<e50[i] and h[i-1]>e20[i-1] and c[i]<c[i-1]
        elif mech=="breakout":
            if up: ok = np.isfinite(hh[i]) and c[i]>hh[i]
            else:  ok = np.isfinite(ll[i]) and c[i]<ll[i]
        elif mech=="compression":
            if not (np.isfinite(ama[i]) and atr[i-1]<0.8*ama[i]): continue
            if up: ok = (c[i]-o[i])>1.0*atr[i] and c[i]>o[i]
            else:  ok = (o[i]-c[i])>1.0*atr[i] and c[i]<o[i]
        elif mech=="momentum":
            if up: ok = c[i]>c[i-1]>c[i-2]>c[i-3]
            else:  ok = c[i]<c[i-1]<c[i-2]<c[i-3]
        elif mech=="efficiency":
            if up: ok = np.isfinite(eff[i]) and eff[i]>0.4
            else:  ok = np.isfinite(eff[i]) and eff[i]<-0.4
        elif mech=="dispaccept":
            b=c[i-1]-o[i-1]
            if up: ok = b>1.0*atr[i-1] and c[i]>c[i-1]
            else:  ok = b<-1.0*atr[i-1] and c[i]<c[i-1]
        elif mech=="structure":  # HL/LH continuation
            if up: ok = l[i-1]>l[i-2]>l[i-3] and c[i]>h[i-1]
            else:  ok = h[i-1]<h[i-2]<h[i-3] and c[i]<l[i-1]
        if ok: out.append((i,s))
    return out

def eval_tf(tf,mech,long,rr,scen,split="dev",regime_gate=None):
    x=tfs[tf]; o,h,l,c,atr=x["open"].to_numpy(),x["high"].to_numpy(),x["low"].to_numpy(),x["close"].to_numpy(),x["atr"].to_numpy()
    reg=x["regime"].to_numpy() if "regime" in x else None; msk=(x["is_dev"] if split=="dev" else x["is_cal"]).to_numpy()
    cfg=dict(mstrat.CFG); cfg["spread_ticks"]=0.0; cfg["slip_ticks"]=RT[scen]/(2*TICK)
    setups=[]; meta={}
    for (i,side) in gen(mech,long,x):
        if not msk[i]: continue
        if regime_gate and reg is not None and reg[i]!=regime_gate: continue
        a=atr[i]
        stop=(min(l[i-4:i+1])-0.15*a) if side>0 else (max(h[i-4:i+1])+0.15*a)  # EDGE-TF structural swing
        ei=i+1
        if ei>=len(x)-1: continue
        entry=o[ei]; risk=abs(entry-stop)
        if not (risk>0) or (side>0 and stop>=entry) or (side<0 and stop<=entry): continue
        setups.append(dict(si=i,ei=ei,dir=side,stop=float(stop),exit_kind="rr",exit_param=float(rr)))
        meta[i]=(risk, int(pd.Timestamp(x["dt"].iloc[i]).year))
    led=mstrat.simulate(x,setups,cfg)
    out=[]
    for r,si in zip(led["R"],led["si"]):
        risk,yr=meta.get(int(si),(np.nan,0)); out.append(dict(R=float(r),risk=risk,year=yr,si=int(si)))
    return out

def M(res,rr):
    if not res or len(res)<1: return dict(n=0)
    R=np.array([x["R"] for x in res]); n=len(R); Rs=np.sort(R)[::-1]; w=R[R>0]; l=R[R<=0]
    risk=np.array([x["risk"] for x in res if x["risk"]==x["risk"]]); tp_pips=rr*risk/PIP if len(risk) else np.array([0])
    byyr=defaultdict(list)
    for x in res: byyr[x["year"]].append(x["R"])
    return dict(n=n,WR=round(float((R>=rr-0.05).mean()),3),avg_R=round(float(R.mean()),4),med_R=round(float(np.median(R)),3),
                pf=round(float(w.sum()/-l.sum()),3) if l.sum()<0 else None,
                best5_rem=round(float(Rs[max(1,int(n*.05)):].mean()),4),best10_rem=round(float(Rs[max(1,int(n*.1)):].mean()),4),
                med_SL_pips=round(float(np.median(risk)/PIP),1) if len(risk) else None,med_TP_pips=round(float(np.median(tp_pips)),1),
                pct_TP70=round(float((tp_pips>=70).mean()),3) if len(risk) else 0,pct_TP80=round(float((tp_pips>=80).mean()),3) if len(risk) else 0,
                temporal={int(y):round(float(np.mean(v)),3) for y,v in sorted(byyr.items())})

MECHS=["pullback","breakout","compression","momentum","efficiency","dispaccept","structure"]
RRTF={"M5":4.0,"M15":3.0,"H1":2.5,"H4":1.5}  # per-TF RR sized for ~economic (>=70p) targets given each TF's stop
REG=[]
for tf in ("M5","M15","H1","H4"):
    for mech in MECHS:
        for long in (True,False):
            REG.append(dict(id=f"MT-{tf}-{mech}-{'L' if long else 'S'}",tf=tf,mech=mech,long=long,rr=RRTF[tf]))

def falsify(b,s):
    if b.get("n",0)<30: return "SPARSE"
    if (b.get("avg_R") or -9)<=0 or (s.get("avg_R") or -9)<=0: return "FAIL"
    if (s.get("best5_rem") or -9)<=0: return "TAIL_FRAGILE"
    if (s.get("pct_TP70") or 0)<0.5: return "SMALL_TARGET"
    return "SURVIVE"

log(f"MULTITF CAMPAIGN START ids={len(REG)}")
records=[]
for k,h in enumerate(REG):
    b=M(eval_tf(h["tf"],h["mech"],h["long"],h["rr"],"BASE"),h["rr"]); s=M(eval_tf(h["tf"],h["mech"],h["long"],h["rr"],"STRESS"),h["rr"])
    st=falsify(b,s)
    rec=dict(id=h["id"],tf=h["tf"],mech=h["mech"],dir=("LONG" if h["long"] else "SHORT"),rr=h["rr"],
             BASE_avg=b.get("avg_R"),STRESS=s,status=st)
    records.append(rec)
    log(f"{h['id']} [{h['tf']} {rec['dir']} rr{h['rr']}]: n={s.get('n')} WR={s.get('WR')} B={b.get('avg_R')} S={s.get('avg_R')} b5={s.get('best5_rem')} b10={s.get('best10_rem')} medSL={s.get('med_SL_pips')}p medTP={s.get('med_TP_pips')}p %TP70={s.get('pct_TP70')} -> {st}")
    if (k+1) in (20,40,60): json.dump(records,open(os.path.join(SP,f"multitf_ck_{k+1}.json"),"w"),indent=1,default=float); log(f"CHECKPOINT {k+1}: surv={[r['id'] for r in records if r['status']=='SURVIVE']}")
surv=[r["id"] for r in records if r["status"]=="SURVIVE"]
json.dump(dict(records=records,survivors=surv),open(os.path.join(SP,"multitf_records.json"),"w"),indent=1,default=float)
# per-TF summary
bytf=defaultdict(lambda: defaultdict(int))
for r in records: bytf[r["tf"]][r["status"]]+=1
log("PER-TF STATUS: "+" | ".join(f"{tf}:{dict(bytf[tf])}" for tf in ('M5','M15','H1','H4')))
log(f"MULTITF_COMPLETE ids={len(records)} survivors={surv}")

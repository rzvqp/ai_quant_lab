"""ALPHA-XAUUSD-H1-H4-TRANSITION-DISCOVERY-001.
Trade the CHANGE between market states on H1/H4. Transition-specific mechanisms: RANGE->TREND with
acceptance vs displacement-alone (tests S2), breakout+retest vs immediate (S21.3), false-break transition
(S6), trend-exhaustion reversal (S7), compression->expansion. Parent-TF structural SL (NOT M5). Economic
RR target (>=80p). Gated M5 -> causal H1/H4. NO N4/2025+/read_csv. Cost tick 0.01 / STRESS 0.24. <=40 IDs."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
WP5B=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"
if WP5B not in sys.path: sys.path.insert(0,WP5B)
import mstrat
PIP=0.10; TICK=mstrat.TICK; RT={"GROSS":0.0,"BASE":0.05,"STRESS":0.24}
def log(m): print(f"[{int(time.time())}] {m}",flush=True); open(os.path.join(SP,"transition.log"),"a").write(f"{int(time.time())} {m}\n")

tfs,META=D.build()
W={"H1":24,"H4":12}
PR={}
for tf in ("H1","H4"):
    x=tfs[tf]; x["m_atr"]=x["atr"]; h=x["high"].to_numpy(); l=x["low"].to_numpy()
    w=W[tf]
    PR[tf]=dict(hi=pd.Series(h).rolling(w).max().shift(1).to_numpy(), lo=pd.Series(l).rolling(w).min().shift(1).to_numpy(),
                hi4=pd.Series(h).rolling(w).max().shift(4).to_numpy(), lo4=pd.Series(l).rolling(w).min().shift(4).to_numpy())
log(f"loader sha={META['data_file_sha256'][:16]} H1 DEV={int(tfs['H1']['is_dev'].sum())} H4 DEV={int(tfs['H4']['is_dev'].sum())}")

def gen(mech,long,tf):
    x=tfs[tf]; o=x["open"].to_numpy();h=x["high"].to_numpy();l=x["low"].to_numpy();c=x["close"].to_numpy()
    atr=x["atr"].to_numpy();ama=x["atr_ma"].to_numpy();eff=x["effic"].to_numpy();e20=x["ema20"].to_numpy();e50=x["ema50"].to_numpy()
    P=PR[tf];hi=P["hi"];lo=P["lo"];hi4=P["hi4"];lo4=P["lo4"];n=len(x);out=[];up=long;s=1 if up else -1
    for i in range(60,n-1):
        if atr[i]!=atr[i]: continue
        ok=False
        wasrng = (abs(eff[i-2])<0.40) if eff[i-2]==eff[i-2] else False
        if mech=="rng2trend_accept":       # break + 2 closes outside + follow-through
            if not (np.isfinite(hi[i]) and np.isfinite(lo[i]) and wasrng): continue
            if up: ok = c[i-1]>hi[i-1] and c[i]>hi[i] and c[i]>c[i-1]
            else:  ok = c[i-1]<lo[i-1] and c[i]<lo[i] and c[i]<c[i-1]
        elif mech=="rng2trend_disponly":   # break + big displacement bar, enter immediately (NO acceptance)
            if not (np.isfinite(hi[i]) and wasrng): continue
            if up: ok = c[i]>hi[i] and (c[i]-o[i])>1.2*atr[i]
            else:  ok = c[i]<lo[i] and (o[i]-c[i])>1.2*atr[i]
        elif mech=="breakout_retest":      # broke, dipped back to broken level, held & closed in dir
            if not np.isfinite(hi[i]): continue
            if up: ok = c[i]>hi[i] and l[i]<=hi[i]*1.001 and c[i]>o[i]
            else:  ok = c[i]<lo[i] and h[i]>=lo[i]*0.999 and c[i]<o[i]
        elif mech=="breakout_immediate":   # first close beyond prior structure (baseline vs retest)
            if not np.isfinite(hi[i]): continue
            if up: ok = c[i]>hi[i] and c[i-1]<=hi[i-1]
            else:  ok = c[i]<lo[i] and c[i-1]>=lo[i-1]
        elif mech=="false_break":          # break one side, fail, displace through OTHER side -> new move
            if not (np.isfinite(hi4[i]) and np.isfinite(lo4[i])): continue
            if up:  # low-side false break -> long: broke low, failed back in, now breaks high
                ok = min(l[i-3:i])<lo4[i] and c[i-1]>lo4[i] and c[i]>hi4[i]
            else:   # high-side false break -> short
                ok = max(h[i-3:i])>hi4[i] and c[i-1]<hi4[i] and c[i]<lo4[i]
        elif mech=="trend_exhaustion":     # trend loses continuation -> reversal
            if up:  # from TREND_DOWN: failed new low + break prior swing high + accept
                ok = e20[i]<e50[i] and l[i]>l[i-1] and c[i]>max(h[i-3:i]) and c[i]>o[i]
            else:   # from TREND_UP: failed new high + break prior swing low
                ok = e20[i]>e50[i] and h[i]<h[i-1] and c[i]<min(l[i-3:i]) and c[i]<o[i]
        elif mech=="comp_expansion":       # compression then expansion beyond structure
            if not (np.isfinite(ama[i]) and np.isfinite(hi[i]) and atr[i-1]<0.8*ama[i]): continue
            if up: ok = c[i]>hi[i] and (c[i]-o[i])>1.0*atr[i]
            else:  ok = c[i]<lo[i] and (o[i]-c[i])>1.0*atr[i]
        if ok: out.append((i,s))
    return out

def evalc(tf,mech,long,rr,scen,split="dev"):
    x=tfs[tf];o=x["open"].to_numpy();h=x["high"].to_numpy();l=x["low"].to_numpy();atr=x["atr"].to_numpy()
    msk=(x["is_dev"] if split=="dev" else x["is_cal"]).to_numpy()
    cfg=dict(mstrat.CFG);cfg["spread_ticks"]=0.0;cfg["slip_ticks"]=RT[scen]/(2*TICK);setups=[];meta={}
    for (i,side) in gen(mech,long,tf):
        if not msk[i]: continue
        a=atr[i];stop=(min(l[i-3:i+1])-0.15*a) if side>0 else (max(h[i-3:i+1])+0.15*a);ei=i+1
        if ei>=len(x)-1: continue
        entry=o[ei];risk=abs(entry-stop)
        if not (risk>0) or (side>0 and stop>=entry) or (side<0 and stop<=entry): continue
        setups.append(dict(si=i,ei=ei,dir=side,stop=float(stop),exit_kind="rr",exit_param=float(rr)));meta[i]=(risk,int(pd.Timestamp(x["dt"].iloc[i]).year))
    led=mstrat.simulate(x,setups,cfg);out=[]
    for r,si in zip(led["R"],led["si"]):
        risk,yr=meta.get(int(si),(np.nan,0));out.append(dict(R=float(r),risk=risk,year=yr,si=int(si)))
    return out
def M(res,rr):
    if not res: return dict(n=0)
    R=np.array([x["R"] for x in res]);n=len(R);Rs=np.sort(R)[::-1];w=R[R>0];l=R[R<=0]
    risk=np.array([x["risk"] for x in res if x["risk"]==x["risk"]]);tp=rr*risk/PIP if len(risk) else np.array([0])
    byyr=defaultdict(list)
    for x in res: byyr[x["year"]].append(x["R"])
    return dict(n=n,WR=round(float((R>=rr-0.05).mean()),3),avg_R=round(float(R.mean()),4),med_R=round(float(np.median(R)),3),
                pf=round(float(w.sum()/-l.sum()),3) if l.sum()<0 else None,maxDD=round(float((np.maximum.accumulate(np.cumsum(R))-np.cumsum(R)).max()),2),
                best5_rem=round(float(Rs[max(1,int(n*.05)):].mean()),4),best10_rem=round(float(Rs[max(1,int(n*.1)):].mean()),4),
                med_SL_pips=round(float(np.median(risk)/PIP),1) if len(risk) else None,med_TP_pips=round(float(np.median(tp)),1),
                pct_TP80=round(float((tp>=80).mean()),3) if len(risk) else 0,pct_TP100=round(float((tp>=100).mean()),3) if len(risk) else 0,pct_TP150=round(float((tp>=150).mean()),3) if len(risk) else 0,
                temporal={int(y):round(float(np.mean(v)),3) for y,v in sorted(byyr.items())})

MECHS=["rng2trend_accept","rng2trend_disponly","breakout_retest","breakout_immediate","false_break","trend_exhaustion","comp_expansion"]
RRTF={"H1":2.5,"H4":1.5}
REG=[dict(id=f"TR-{tf}-{m}-{'L' if lg else 'S'}",tf=tf,mech=m,long=lg,rr=RRTF[tf]) for tf in ("H1","H4") for m in MECHS for lg in (True,False)]
def fals(b,s):
    if b.get("n",0)<25: return "SPARSE"
    if (b.get("avg_R") or -9)<=0 or (s.get("avg_R") or -9)<=0: return "FAIL"
    if (s.get("best5_rem") or -9)<=0: return "TAIL_FRAGILE"
    if (s.get("pct_TP80") or 0)<0.5: return "SMALL_TARGET"
    return "SURVIVE"
log(f"TRANSITION CAMPAIGN START ids={len(REG)}")
records=[]
for k,h in enumerate(REG):
    b=M(evalc(h["tf"],h["mech"],h["long"],h["rr"],"BASE"),h["rr"]);s=M(evalc(h["tf"],h["mech"],h["long"],h["rr"],"STRESS"),h["rr"])
    st=fals(b,s)
    records.append(dict(id=h["id"],tf=h["tf"],mech=h["mech"],dir=("LONG" if h["long"] else "SHORT"),rr=h["rr"],BASE_avg=b.get("avg_R"),STRESS=s,status=st))
    log(f"{h['id']} [{h['tf']} {('LONG' if h['long'] else 'SHORT')}]: n={s.get('n')} WR={s.get('WR')} B={b.get('avg_R')} S={s.get('avg_R')} b5={s.get('best5_rem')} b10={s.get('best10_rem')} medSL={s.get('med_SL_pips')}p medTP={s.get('med_TP_pips')}p %TP80={s.get('pct_TP80')} -> {st}")
    if (k+1)==20: json.dump(records,open(os.path.join(SP,"transition_ck20.json"),"w"),indent=1,default=float); log(f"CHECKPOINT 20 surv={[r['id'] for r in records if r['status']=='SURVIVE']}")
surv=[r["id"] for r in records if r["status"]=="SURVIVE"]
json.dump(dict(records=records,survivors=surv),open(os.path.join(SP,"transition_records.json"),"w"),indent=1,default=float)
bytf=defaultdict(lambda: defaultdict(int))
for r in records: bytf[r["tf"]][r["status"]]+=1
log("PER-TF: "+" | ".join(f"{tf}:{dict(bytf[tf])}" for tf in ('H1','H4')))
log(f"TRANSITION_COMPLETE ids={len(records)} survivors={surv}")

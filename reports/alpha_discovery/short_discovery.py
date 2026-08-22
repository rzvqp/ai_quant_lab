"""ALPHA-XAUUSD-H1-H4-SHORT-SPECIALIST-DISCOVERY-001. Dedicated SHORT search, H4+H1.
DISCIPLINE: RAW signal edge (trajectory-free) FIRST -> eventize survivors -> serialized. Baseline =
PROJECT TREND_DOWN (ema20<ema50 AND effic<-0.30). Incremental over baseline MANDATORY. Gate I (top-10%
net-profit <=60%) + best-5%-removed>0. Structural SL on edge TF (NOT M5). Gated M5 -> causal H1/H4.
NO N4/2025+/read_csv/V1. Cost tick 0.01 / STRESS 0.24. DEV-only (CALIB closed). <=50 IDs, ck 20/35."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
PIP=0.10; TICK=0.01; RT={"GROSS":0.0,"BASE":0.05,"STRESS":0.24}
def log(m): print(f"[{int(time.time())}] {m}",flush=True); open(os.path.join(SP,"short.log"),"a").write(f"{int(time.time())} {m}\n")
tfs,META=D.build()
for tf in ("H1","H4"): tfs[tf]["m_atr"]=tfs[tf]["atr"]
log(f"loader sha={META['data_file_sha256'][:16]} H1 DEV={int(tfs['H1']['is_dev'].sum())} H4 DEV={int(tfs['H4']['is_dev'].sum())}")
RRTF={"H1":2.5,"H4":1.5}

def A(tf): x=tfs[tf]; return (x["open"].to_numpy(),x["high"].to_numpy(),x["low"].to_numpy(),x["close"].to_numpy(),
    x["atr"].to_numpy(),x["ema20"].to_numpy(),x["ema50"].to_numpy(),x["hh20"].to_numpy(),x["ll20"].to_numpy(),
    x["hh50"].to_numpy(),x["ll50"].to_numpy(),x["effic"].to_numpy(),x["atr_ma"].to_numpy(),
    x["is_dev"].to_numpy(),x["is_cal"].to_numpy(),pd.to_datetime(x["time"],unit="s",utc=True).dt.year.to_numpy())

def sim_short(tf,i,rr,scen):  # signal bar i -> SHORT entry i+1, edge-TF structural stop
    o,h,l,c,atr,*_=A(tf); n=len(o); ei=i+1
    if ei>=n-1 or atr[i]!=atr[i]: return None
    entry=o[ei]; stop=max(h[i-4:i+1])+0.15*atr[i]; risk=stop-entry
    if not np.isfinite(risk): return None
    me=max(5*TICK,0.10*atr[i])
    if risk<me: risk=me; stop=entry+risk
    if risk<=0: return None
    tgt=entry-rr*risk; cost=RT[scen]; ex=None; xi=None
    for j in range(ei,min(ei+48,n)):
        if h[j]>=stop: ex=stop;xi=j;break
        if l[j]<=tgt: ex=tgt;xi=j;break
    if ex is None: xi=min(ei+48,n-1); ex=c[xi]
    return dict(i=i,ei=ei,xi=xi,R=((entry-ex)-cost)/risk,risk=risk,sl_pips=risk/PIP,tp_pips=rr*risk/PIP)

# ---- SHORT mechanisms: yield signal bar i (DEV) ----
def gen(mech,tf):
    o,h,l,c,atr,e20,e50,hh,ll,hh50,ll50,eff,ama,dev,cal,yr=A(tf); n=len(o); out=[]
    for i in range(55,n-1):
        if atr[i]!=atr[i] or not dev[i]: continue
        ok=False
        if mech=="disp_follow": ok=(o[i-1]-c[i-1])>1.0*atr[i-1] and c[i]<c[i-1]
        elif mech=="disp_only": ok=(o[i]-c[i])>1.0*atr[i]
        elif mech=="breakdown": ok=np.isfinite(ll[i]) and c[i]<ll[i] and c[i-1]>=ll[i-1]
        elif mech=="breakdown_disp": ok=np.isfinite(ll[i]) and c[i]<ll[i] and (o[i]-c[i])>1.0*atr[i]
        elif mech=="breakdown_retest": ok=np.isfinite(ll[i]) and c[i]<ll[i] and h[i]>=ll[i]
        elif mech=="lowerhigh_break": ok=h[i-1]<h[i-2] and h[i-2]<h[i-3] and c[i]<l[i-1]
        elif mech=="failed_rally": ok=np.isfinite(hh[i]) and h[i]>=hh[i] and c[i]<o[i] and c[i]<hh[i]
        elif mech=="failed_bull_cont": ok=e20[i]>e50[i] and c[i]<min(l[i-3:i]) and c[i]<o[i]
        elif mech=="comp_exp_down":
            ok=np.isfinite(ama[i]) and atr[i-1]<0.8*ama[i] and (o[i]-c[i])>1.0*atr[i] and c[i]<o[i]
        elif mech=="trend_exhaust_down": ok=e20[i]>e50[i] and h[i]<h[i-1] and c[i]<min(l[i-3:i]) and c[i]<o[i]
        elif mech=="momentum_down": ok=c[i]<c[i-1] and c[i-1]<c[i-2] and c[i-2]<c[i-3]
        elif mech=="efficiency_down": ok=eff[i]==eff[i] and eff[i]<-0.4
        elif mech=="range_low_break": ok=np.isfinite(ll50[i]) and c[i]<ll50[i] and c[i-1]>=ll50[i-1]
        if ok: out.append(i)
    return out
def project_td(tf):  # PROJECT TREND_DOWN raw per-signal short expectancy
    o,h,l,c,atr,e20,e50,hh,ll,hh50,ll50,eff,ama,dev,cal,yr=A(tf); R=[]
    for i in range(55,len(o)-1):
        if atr[i]==atr[i] and dev[i] and e20[i]<e50[i] and eff[i]==eff[i] and eff[i]<-0.30:
            r=sim_short(tf,i,RRTF[tf],"STRESS")
            if r: R.append(r['R'])
    return np.array(R)

def rawmetrics(tf,sigs,rr):
    S=[sim_short(tf,i,rr,"STRESS") for i in sigs]; S=[s for s in S if s]; B=[sim_short(tf,i,rr,"BASE") for i in sigs]; B=[b for b in B if b]
    if len(S)<20: return dict(n=len(S))
    R=np.array([s['R'] for s in S]); Rb=np.array([b['R'] for b in B]); nn=len(R); Rs=np.sort(R)[::-1]; net=R.sum(); w=R[R>0]
    yr=A(tf)[15]
    byy=defaultdict(list)
    for s in S: byy[int(yr[s['i']])].append(s['R'])
    return dict(n=nn,WR=round(float((R>=rr-0.05).mean()),3),BASE=round(float(Rb.mean()),4),avgR=round(float(R.mean()),4),medR=round(float(np.median(R)),3),
                b1rem=round(float(Rs[max(1,int(nn*.01)):].mean()),4),b5rem=round(float(Rs[max(1,int(nn*.05)):].mean()),4),b10rem=round(float(Rs[max(1,int(nn*.1)):].mean()),4),
                top10share=round(float(Rs[:max(1,int(nn*.1))].sum()/net*100),1) if net>0 else 999,
                medTP=round(float(np.median([s['tp_pips'] for s in S])),1),medSL=round(float(np.median([s['sl_pips'] for s in S])),1),
                temporal={y:(len(v),round(float(np.mean(v)),3)) for y,v in sorted(byy.items())})

MECHS=["disp_follow","disp_only","breakdown","breakdown_disp","breakdown_retest","lowerhigh_break",
       "failed_rally","failed_bull_cont","comp_exp_down","trend_exhaust_down","momentum_down","efficiency_down","range_low_break"]
PTD={tf:project_td(tf) for tf in ("H4","H1")}
for tf in ("H4","H1"): log(f"PROJECT_TREND_DOWN {tf}: n={len(PTD[tf])} avgR={PTD[tf].mean():.4f}")

log(f"SHORT RAW-SIGNAL FALSIFICATION START (mechs={len(MECHS)} x 2 TF)")
records=[]; k=0
for tf in ("H4","H1"):
    base=PTD[tf].mean()
    for mech in MECHS:
        k+=1; sigs=gen(mech,tf); m=rawmetrics(tf,sigs,RRTF[tf])
        if m.get("n",0)<20: st="SPARSE"; incr=None
        else:
            incr=round(m["avgR"]-base,4)
            st="RAW_SURVIVE" if (m["avgR"]>0 and incr>0 and m["b5rem"]>0 and m["top10share"]<=60) else "RAW_FAIL"
        records.append(dict(id=f"SH-{tf}-{mech}",tf=tf,mech=mech,rawN=m.get("n"),status=st,incr=incr,raw=m))
        log(f"SH-{tf}-{mech}: n={m.get('n')} STRESS={m.get('avgR')} incr_vs_TD={incr} medR={m.get('medR')} b5rem={m.get('b5rem')} top10%={m.get('top10share')} medTP={m.get('medTP')}p -> {st}")
        if k in (20,35): json.dump(records,open(os.path.join(SP,f"short_ck{k}.json"),"w"),indent=1,default=float); log(f"CHECKPOINT {k}: raw_survivors={[r['id'] for r in records if r['status']=='RAW_SURVIVE']}")
surv=[r for r in records if r["status"]=="RAW_SURVIVE"]
json.dump(dict(records=records,raw_survivors=[r['id'] for r in surv],project_td={tf:float(PTD[tf].mean()) for tf in PTD}),open(os.path.join(SP,"short_records.json"),"w"),indent=1,default=float)
log(f"RAW FALSIFICATION COMPLETE: {len(surv)} raw-survivors of {len(records)}: {[r['id'] for r in surv]}")

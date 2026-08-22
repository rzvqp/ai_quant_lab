"""Deepen the intra-range robust arm (coarse LONG-to-mid, lower/mid zone) + failcounter-L-mid M5 arm.
CRITICAL: CALIB generalization (the mean-reversion branch died here). Temporal, tail, location breakdown (§7),
disguised-mean-reversion check (does the H1-up-bar directional filter matter?), M5-value recap."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import range_intra as IR
PIP=IR.PIP; RT=IR.RT

def tail_temp(tr,dev=True):
    r=[x for x in tr if (x["is_dev"] if dev else x["is_cal"])]
    if not r: return {},{}
    R=np.sort(np.array([x["R"] for x in r]))[::-1]; n=len(R)
    t=dict(best1=round(float(R[max(1,int(n*.01)):].mean()),4),best5=round(float(R[max(1,int(n*.05)):].mean()),4),best10=round(float(R[max(1,int(n*.1)):].mean()),4))
    yr={}
    for x in r: yr.setdefault(pd.to_datetime(x["t"],unit="s",utc=True).year,[]).append(x["R"])
    return t, {int(y):(round(float(np.mean(v)),3),len(v)) for y,v in sorted(yr.items())}
def locbreak(tr):
    r=[x for x in tr if x["is_dev"]]; loc=np.array([x["loc"] for x in r]); R=np.array([x["R"] for x in r])
    zones=[(0,.10),(.10,.25),(.25,.50),(.50,.75)]; out={}
    for a,b in zones:
        m=(loc>=a)&(loc<b); out[f"{int(a*100)}-{int(b*100)}%"]=(round(float(R[m].mean()),3) if m.sum() else None, int(m.sum()))
    return out

# coarse L-mid (identical across mechanisms) -- use bos; also CALIB
dev=IR.run("bos",True,"mid","dev"); cal=IR.run("bos",True,"mid","cal")
A=IR.summ(dev["A"]); Ac=IR.summ(cal["A"],dev=False)
tA,tempA=tail_temp(dev["A"]); tAc,_=tail_temp(cal["A"],dev=False)
print("===== COARSE LONG-to-MID (lower/mid zone, H1 up bar) =====")
print(f"  DEV : n={A['n']} WR={A['WR']} avgR={A['avg_R']} PF={A['pf']} maxDD={A['maxDD']} medSL={A['med_SL_pips']}p medRoom={A['med_room_pips']}p rr={A['rr_eff']}")
print(f"        tail={tA}  temporal={tempA}")
print(f"        %room>=70={A['pct_room70']} >=80={A['pct_room80']} >=100={A['pct_room100']} >=150={A['pct_room150']} | medWidth={A['med_width']}p med_MAE={A['med_MAE']} med_MFE={A['med_MFE']}")
print(f"  CALIB: n={Ac['n']} WR={Ac.get('WR')} avgR={Ac.get('avg_R')} best5={tAc.get('best5')}  <-- GENERALIZATION GATE")
print(f"  location breakdown (DEV avgR,n): {locbreak(dev['A'])}")

# disguised-mean-reversion check: same setup WITHOUT the H1-up-bar filter (i.e., all lower-zone longs to mid)
import numpy as _np
def run_nofilter(long=True):
    side=1; A=[]; lastA=-1
    for i in range(IR.RG.W+2,IR.nH):
        if not IR.inr[i] or not (IR.width[i]>0) or not bool(IR.h1dev[i]): continue
        T=IR.h1ct[i]; jr=IR.m5_after(T)
        if jr<=0 or jr>=IR.n5-1: continue
        er=IR.m5o[jr]; loc=(er-IR.rlo[i])/IR.width[i]
        if loc>0.60: continue
        a=IR.h1atr[i]; a=a if a==a else .5; stop=min(IR.h1l[i-2:i+1])-0.10*a; tgt=IR.rmid[i]
        if not (stop<er<tgt): continue
        room=abs(tgt-er)
        if room<70*PIP or tgt>IR.rhi[i]: continue
        rr=room/abs(er-stop)
        if IR.m5t[jr]<=lastA: continue
        w=IR.RG.walk(jr,side,stop,tgt)
        if w is None: continue
        e,ex,mae,mfe=w; lastA=IR.m5t[min(jr+IR.MAXHOLD,IR.n5-1)]
        A.append(dict(R=(side*(ex-e)-RT["STRESS"])/abs(er-stop),win=abs(ex-tgt)<1e-6,is_dev=True,is_cal=False,loc=loc,t=int(IR.m5t[jr]),risk_ref=abs(er-stop),room=room,width=IR.width[i],rr_eff=rr,mae=mae,mfe=mfe))
    return A
nf=run_nofilter(); snf=IR.summ(nf)
print(f"\n  NO H1-up-filter (all lower/mid-zone longs to mid): n={snf['n']} WR={snf['WR']} avgR={snf['avg_R']} best5={snf['best5_rem']}")
print(f"  => H1-up-bar filter value: with={A['avg_R']}(n{A['n']}) vs without={snf['avg_R']}(n{snf['n']})  (does directional filter matter?)")

# failcounter-L-mid M5 arm CALIB
devf=IR.run("failcounter",True,"mid","dev"); calf=IR.run("failcounter",True,"mid","cal")
B=IR.summ(devf["B"]); Bc=IR.summ(calf["B"],dev=False); tB,tempB=tail_temp(devf["B"])
print(f"\n===== IR-failcounter-L-mid (M5 arm) =====")
print(f"  DEV : n={B['n']} WR={B['WR']} avgR={B['avg_R']} best5={B['best5_rem']} best10={B['best10_rem']} tail={tB} temporal={tempB}")
print(f"  CALIB: n={Bc['n']} WR={Bc.get('WR')} avgR={Bc.get('avg_R')} best5={Bc.get('best5_rem')}  <-- GENERALIZATION GATE")

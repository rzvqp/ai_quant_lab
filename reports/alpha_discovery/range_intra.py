"""ALPHA-XAUUSD-H1-RANGE-INTRARANGE-M5-001.
H1 RANGE = CONTAINER (where price is + how much room). M5 = the DIRECTIONAL LEG / entry.
Edge comes from a causal M5 directional mechanism (BOS / compression->expansion / failed-counter),
NOT from 'boundary = reverse'. Trade WITH the M5 direction toward an H1 interior target, with room.
STOP = H1 structural (same for both arms). Control A(coarse H1-directional entry) vs B(M5 mechanism entry).
Gated M5 only (via range_m5 container). NO N4, NO 2025+, NO read_csv. Cost tick 0.01 / STRESS 0.24. <=40 IDs."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import range_m5 as RG   # firewall-clean gated container: in_range, rhi/rlo/rmid/width, M5 arrays, walk
PIP=RG.PIP; RT=RG.RT
m5t=RG.m5t; m5o=RG.m5o; m5h=RG.m5h; m5l=RG.m5l; m5c=RG.m5c; n5=RG.n5
m5atr=RG.M5["atr"].to_numpy(); m5ema=RG.M5["close"].ewm(span=20,adjust=True).mean().to_numpy()
h1ct=RG.h1ct; h1dev=RG.h1dev; h1cal=RG.h1cal; h1o=RG.h1o; h1h=RG.h1h; h1l=RG.h1l; h1c=RG.h1c; h1atr=RG.h1atr
inr=RG.in_range; rhi=RG.rhi; rlo=RG.rlo; rmid=RG.rmid; width=RG.width; nH=RG.nH
def log(m): print(f"[{int(time.time())}] {m}",flush=True); open(os.path.join(SP,"intra.log"),"a").write(f"{int(time.time())} {m}\n")

TRIG_WIN=48; MAXHOLD=576  # 4h window to find the M5 leg; 2-day max hold
def m5_after(T): return int(np.searchsorted(m5t,T,side="right"))

# ---------- M5 directional-leg mechanisms: return first trigger index j in [j0,end), or None ----------
def leg_bos(j0,end,long):
    for j in range(max(j0,8),end):
        if long and m5c[j] > max(m5h[j-4:j]) and min(m5l[j-4:j]) > min(m5l[j-8:j-4]): return j+1
        if (not long) and m5c[j] < min(m5l[j-4:j]) and max(m5h[j-4:j]) < max(m5h[j-8:j-4]): return j+1
    return None
def leg_compexp(j0,end,long):
    for j in range(max(j0,32),end):
        a=m5atr[j]; ma=np.nanmean(m5atr[j-30:j])
        if not (a==a and ma==ma and ma>0): continue
        if m5atr[j-1] < 0.8*ma and abs(m5c[j]-m5o[j]) > 1.0*a:
            if long and m5c[j]>m5o[j]: return j+1
            if (not long) and m5c[j]<m5o[j]: return j+1
    return None
def leg_failcounter(j0,end,long):
    for j in range(max(j0,8),end):
        if long and m5c[j] > m5ema[j] and m5l[j-1] > min(m5l[j-5:j-1]) and m5c[j] > m5h[j-1]: return j+1
        if (not long) and m5c[j] < m5ema[j] and m5h[j-1] < max(m5h[j-5:j-1]) and m5c[j] < m5l[j-1]: return j+1
    return None
LEGS={"bos":leg_bos,"compexp":leg_compexp,"failcounter":leg_failcounter}

def target_px(i, long, mode, entry):
    if mode=="mid": t=rmid[i]
    elif mode=="q": t=(rlo[i]+0.75*width[i]) if long else (rhi[i]-0.75*width[i])
    elif mode=="opp": t=(rhi[i]-0.10*width[i]) if long else (rlo[i]+0.10*width[i])
    else: t=entry
    return t

def run(mech, long, tp_mode, split="dev"):
    side=1 if long else -1; legfn=LEGS[mech]; A=[]; B=[]; lastA=-1; lastB=-1
    for i in range(RG.W+2,nH):
        if not inr[i] or not (width[i]>0): continue
        is_d=bool(h1dev[i]); is_c=bool(h1cal[i])
        if split=="dev" and not is_d: continue
        if split=="cal" and not is_c: continue
        T=h1ct[i]; j_ref=m5_after(T)
        if j_ref<=0 or j_ref>=n5-1: continue
        entry_ref=m5o[j_ref]
        loc=(entry_ref-rlo[i])/width[i]   # 0=low 1=high
        # zone gate: LONG from lower/mid (loc<=0.6), SHORT from upper/mid (loc>=0.4)
        if long and loc>0.60: continue
        if (not long) and loc<0.40: continue
        # H1 structural stop (SAME for both arms), fixed at thesis
        a=h1atr[i]; a=a if a==a else 0.5
        stop_px=(min(h1l[i-2:i+1])-0.10*a) if long else (max(h1h[i-2:i+1])+0.10*a)
        tgt_px=target_px(i,long,tp_mode,entry_ref)
        # validity + room
        if long and not (stop_px<entry_ref<tgt_px): continue
        if (not long) and not (stop_px>entry_ref>tgt_px): continue
        room=abs(tgt_px-entry_ref)
        if room < 70*PIP or (long and tgt_px>rhi[i]) or ((not long) and tgt_px<rlo[i]): continue
        risk_ref=abs(entry_ref-stop_px)
        if not (risk_ref>0): continue
        rr_eff=room/risk_ref
        base=dict(i=int(i),risk_ref=risk_ref,width=width[i],loc=loc,room=room,rr_eff=rr_eff,is_dev=is_d,is_cal=is_c)
        # A coarse: H1 bar closes in direction (weak H1 directional entry), enter at next M5 open
        h1_dir_up = h1c[i]>h1o[i]
        if ((long and h1_dir_up) or ((not long) and not h1_dir_up)) and m5t[j_ref]>lastA:
            w=RG.walk(j_ref,side,stop_px,tgt_px)
            if w is not None:
                e,ex,mae,mfe=w; lastA=m5t[min(j_ref+MAXHOLD,n5-1)]
                Ra=(side*(ex-e)-RT["STRESS"])/risk_ref
                A.append({**base,"entry":e,"ex":ex,"mae":mae,"mfe":mfe,"R":Ra,"win":abs(ex-tgt_px)<1e-6,"t":int(m5t[j_ref])})
        # B M5 mechanism: find the M5 directional leg trigger in the window
        end=min(j_ref+TRIG_WIN,n5-2); ej=legfn(j_ref,end,long)
        if ej is not None and 0<ej<n5-1 and m5t[ej]>lastB:
            e0=m5o[ej]
            # entry must still be inside container with room to target (re-check after the leg formed)
            if (long and stop_px<e0<tgt_px) or ((not long) and stop_px>e0>tgt_px):
                w=RG.walk(ej,side,stop_px,tgt_px)
                if w is not None:
                    e,ex,mae,mfe=w; lastB=m5t[min(ej+MAXHOLD,n5-1)]
                    locb=(e-rlo[i])/width[i]
                    Rb=(side*(ex-e)-RT["STRESS"])/risk_ref
                    B.append({**base,"entry":e,"ex":ex,"mae":mae,"mfe":mfe,"R":Rb,"win":abs(ex-tgt_px)<1e-6,"loc":locb,"entry_edge":side*(entry_ref-e),"t":int(m5t[ej])})
    return dict(A=A,B=B)

def summ(tr,dev=True):
    r=[x for x in tr if (x["is_dev"] if dev else x["is_cal"])]
    if not r: return dict(n=0)
    R=np.array([x["R"] for x in r]); n=len(R); win=np.array([x["win"] for x in r]); Rs=np.sort(R)[::-1]
    sl=np.array([x["risk_ref"]/PIP for x in r]); room=np.array([x["room"]/PIP for x in r]); rr=np.array([x["rr_eff"] for x in r])
    loc=np.array([x["loc"] for x in r]); mae=np.array([x["mae"]/PIP for x in r]); mfe=np.array([x["mfe"]/PIP for x in r]); wid=np.array([x["width"]/PIP for x in r])
    eq=np.cumsum(R); dd=float((np.maximum.accumulate(eq)-eq).max()); l=R[R<=0]; w=R[R>0]
    return dict(n=n,WR=round(float(win.mean()),3),avg_R=round(float(R.mean()),4),med_R=round(float(np.median(R)),3),
                pf=round(float(w.sum()/-l.sum()),3) if l.sum()<0 else None,maxDD=round(dd,2),
                best1_rem=round(float(Rs[max(1,int(n*.01)):].mean()),4),best5_rem=round(float(Rs[max(1,int(n*.05)):].mean()),4),best10_rem=round(float(Rs[max(1,int(n*.1)):].mean()),4),
                rr_eff=round(float(np.median(rr)),2),med_SL_pips=round(float(np.median(sl)),1),med_room_pips=round(float(np.median(room)),1),
                pct_room70=round(float((room>=70).mean()),3),pct_room80=round(float((room>=80).mean()),3),pct_room100=round(float((room>=100).mean()),3),pct_room150=round(float((room>=150).mean()),3),
                med_width=round(float(np.median(wid)),1),med_loc=round(float(np.median(loc)),3),med_MAE=round(float(np.median(mae)),1),med_MFE=round(float(np.median(mfe)),1))

REG=[]
for mech in ("bos","compexp","failcounter"):
    for long in (True,False):
        for tp in ("mid","opp"):
            REG.append(dict(id=f"IR-{mech}-{'L' if long else 'S'}-{tp}",mech=mech,long=long,tp=tp))
def falsify(s):
    if s.get("n",0)<25: return "SPARSE"
    if (s.get("avg_R") or -9)<=0: return "FAIL"
    if (s.get("best5_rem") or -9)<=0: return "TAIL_FRAGILE"
    return "SURVIVE"

if __name__=="__main__":
    log(f"INTRA-RANGE CAMPAIGN START ids={len(REG)}")
    records=[]
    for k,h in enumerate(REG):
        res=run(h["mech"],h["long"],h["tp"],"dev")
        A=summ(res["A"]); B=summ(res["B"])
        Bsig=set(x["i"] for x in res["B"]); AonB=summ([a for a in res["A"] if a["i"] in Bsig])
        stB=falsify(B); stA=falsify(A)
        tim_dAvg=round((B.get("avg_R") or 0)-(AonB.get("avg_R") or 0),4)
        rec=dict(id=h["id"],mech=h["mech"],side=("LONG" if h["long"] else "SHORT"),tp=h["tp"],
                 A_coarse=A,A_onB=AonB,B_m5=B,status_m5=stB,status_coarse=stA,timing_dAvgR=tim_dAvg)
        records.append(rec)
        log(f"{h['id']} [{rec['side']} {h['tp']}]: coarse(n={A.get('n')},WR={A.get('WR')},avgR={A.get('avg_R')},b5={A.get('best5_rem')})->{stA} | "
            f"M5(n={B.get('n')},WR={B.get('WR')},avgR={B.get('avg_R')},b5={B.get('best5_rem')},rr={B.get('rr_eff')})->{stB} | "
            f"timing(matched)dAvg={tim_dAvg} medSL={B.get('med_SL_pips')}p medRoom={B.get('med_room_pips')}p loc={B.get('med_loc')}")
        if (k+1)%20==0: json.dump(records,open(os.path.join(SP,f"intra_ck_{k+1}.json"),"w"),indent=1,default=float); log(f"CHECKPOINT {k+1}")
    survM=[r["id"] for r in records if r["status_m5"]=="SURVIVE"]; survC=[r["id"] for r in records if r["status_coarse"]=="SURVIVE"]
    json.dump(dict(records=records,survivors_m5=survM,survivors_coarse=survC),open(os.path.join(SP,"intra_records.json"),"w"),indent=1,default=float)
    log(f"INTRA_COMPLETE ids={len(records)} m5_survivors={survM} coarse_survivors={survC}")

"""ALPHA-XAUUSD-POSTSWEEP-PULLBACK-SHORT-001. FROZEN parent predictor (H4 sweep + bearish displacement +
structure break, from the prior mandate, UNCHANGED). New research variable: WAIT for the post-break
bullish pullback to FAIL, then SHORT with the stop around the PULLBACK high (NOT the sweep high).
Entry on H1. Raw-first + common parent + A(immediate) vs B(pullback). DEV-only. NO CALIB/N4/2025+/read_csv."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict, Counter
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import liquidity_sweep_short as Q   # frozen sweeps() + arrs(); gated data
PIP=Q.PIP; TICK=Q.TICK; RT=Q.RT
def log(m): print(f"[{int(time.time())}] {m}",flush=True); open(os.path.join(SP,"psp.log"),"a").write(f"{int(time.time())} {m}\n")
tfs=Q.tfs
h4=Q.arrs("H4"); H4o,H4h,H4l,H4c,H4atr,H4e20,H4e50,H4eff,H4dev,H4yr=h4
H4ct=tfs["H4"]["close_time"].to_numpy(); n4=len(H4o)
h1=Q.arrs("H1"); h1o,h1h,h1l,h1c,h1atr,h1e20,h1e50,h1eff,h1dev,h1yr=h1
h1t=tfs["H1"]["time"].to_numpy(); n1=len(h1o)

# ---- FROZEN parent events: H4 sweep + bearish displacement + structure break (unchanged) ----
def parents():
    ev=[]
    for s in Q.sweeps("H4"):
        i=s['i']; lvl=s['lvl']; k=s['k']; prelow=min(H4l[max(0,k):i]) if i>k else H4l[i]
        disp=False; sweep_hi=H4h[i]; i_break=None
        for j in range(i,min(i+5,n4-1)):
            sweep_hi=max(sweep_hi,H4h[j])
            if (H4o[j]-H4c[j])>1.0*H4atr[j] and H4c[j]<H4o[j]: disp=True
            if disp and H4c[j]<prelow and H4c[j]<H4o[j]: i_break=j; break
        if i_break is None: continue
        ev.append(dict(i_sweep=i,i_break=i_break,T_break=int(H4ct[i_break]),broken=prelow,sweep_hi=sweep_hi,
                       reg=("TREND_UP" if (H4e20[i]>H4e50[i] and H4eff[i]==H4eff[i] and H4eff[i]>0.30) else ("TREND_DOWN" if (H4e20[i]<H4e50[i] and H4eff[i]<-0.30) else "OTHER")),
                       yr=int(H4yr[i_break]),i=i,k=k))
    return ev
PAR=parents()
log(f"FROZEN PARENT EVENTS (H4 sweep+disp+structbreak): n={len(PAR)}  regime={dict(Counter(p['reg'] for p in PAR))}")

def sim_short_h1(entry_j, stop_px, tgt_px, scen):
    if entry_j<=0 or entry_j>=n1-1: return None
    entry=h1o[entry_j]; risk=stop_px-entry
    if not np.isfinite(risk) or risk<=0: return None
    ex=None
    for j in range(entry_j,min(entry_j+72,n1)):  # up to 72 H1 = 12 H4 bars
        if h1h[j]>=stop_px: ex=stop_px;break
        if h1l[j]<=tgt_px: ex=tgt_px;break
    if ex is None: ex=h1c[min(entry_j+72,n1)-1]
    return dict(R=((entry-ex)-RT[scen])/risk, risk=risk, sl_pips=risk/PIP)

# ---- B: post-break PULLBACK entry on H1 (causal). mech in P1/P2/P3/P5. RR economic; stop=pullback high ----
def pullback_trade(p, mech, rr, scen):
    j0=int(np.searchsorted(h1t,p['T_break'],side="right"))   # first H1 bar after the H4 break is known
    if j0<=2 or j0>=n1-3: return None
    end=min(j0+18,n1-2)                                       # 18 H1 = 3 H4 bars pullback window
    broken=p['broken']; pull_hi=h1h[j0]; up_bars=0; retested=False; entry_j=None; ph=h1h[j0]
    for j in range(j0,end):
        ph=max(ph,h1h[j])                                     # causal running pullback high
        if h1c[j]>h1o[j]: up_bars+=1
        if h1h[j]>=broken: retested=True                     # rallied back to broken structure
        if mech=="P1_firstpull_turn":
            if up_bars>=1 and h1c[j]<h1o[j] and h1c[j]<h1c[j-1]: entry_j=j+1; pull_hi=ph; break
        elif mech=="P2_failed_reclaim":
            if retested and h1c[j]<broken and h1c[j]<h1o[j]: entry_j=j+1; pull_hi=ph; break
        elif mech=="P3_lower_high":
            if up_bars>=1 and h1c[j]<min(h1l[j-2:j]) and h1c[j]<h1o[j]: entry_j=j+1; pull_hi=ph; break
        elif mech=="P5_pull_disp":
            if up_bars>=1 and (h1o[j]-h1c[j])>1.0*h1atr[j] and h1c[j]<h1o[j]: entry_j=j+1; pull_hi=ph; break
    if entry_j is None or entry_j>=n1-1: return None
    a=h1atr[entry_j-1] if h1atr[entry_j-1]==h1atr[entry_j-1] else 0.5
    stop_px=pull_hi+0.15*a                                    # STOP AROUND THE PULLBACK HIGH (not sweep high)
    entry=h1o[entry_j]; risk=stop_px-entry
    me=max(5*TICK,0.10*a)
    if risk<me: risk=me; stop_px=entry+risk
    if risk<=0: return None
    tgt=entry-rr*risk
    r=sim_short_h1(entry_j,stop_px,tgt,scen)
    if r: r.update(yr=p['yr'],reg=p['reg'],entry_j=entry_j,tp_pips=rr*risk/PIP);
    return r

# ---- A: OLD immediate short (entry right after H4 break, stop above sweep high) same parent ----
def immediate_trade(p, rr, scen):
    ei=p['i_break']+1
    if ei>=n4-1: return None
    entry=H4o[ei]; stop=p['sweep_hi']+0.15*H4atr[p['i_break']]; risk=stop-entry
    me=max(5*TICK,0.10*H4atr[p['i_break']])
    if risk<me: risk=me; stop=entry+risk
    if risk<=0: return None
    tgt=entry-rr*risk; ex=None
    for j in range(ei,min(ei+48,n4)):
        if H4h[j]>=stop: ex=stop;break
        if H4l[j]<=tgt: ex=tgt;break
    if ex is None: ex=H4c[min(ei+48,n4)-1]
    return dict(R=((entry-ex)-RT[scen])/risk,yr=p['yr'])

def M(trades,rr):
    r=[t for t in trades if t]
    if len(r)<12: return dict(n=len(r))
    R=np.array([t['R'] for t in r]); nn=len(R); Rs=np.sort(R)[::-1]; net=R.sum(); w=R[R>0]
    byy=defaultdict(list)
    for t in r: byy[t['yr']].append(t['R'])
    return dict(n=nn,WR=round(float((R>=rr-0.05).mean()),3),avgR=round(float(R.mean()),4),medR=round(float(np.median(R)),3),
        pf=round(float(w.sum()/-R[R<=0].sum()),3) if R[R<=0].sum()<0 else None,
        b5rem=round(float(Rs[max(1,int(nn*.05)):].mean()),4),b10rem=round(float(Rs[max(1,int(nn*.1)):].mean()),4),
        top10=round(float(Rs[:max(1,int(nn*.1))].sum()/net*100),1) if net>0 else 999,
        medTP=round(float(np.median([t.get('tp_pips',np.nan) for t in r if 'tp_pips' in t])),1) if any('tp_pips' in t for t in r) else None,
        medSL=round(float(np.median([t.get('sl_pips',np.nan) for t in r if 'sl_pips' in t])),1) if any('sl_pips' in t for t in r) else None,
        temporal={y:(len(v),round(float(np.mean(v)),3)) for y,v in sorted(byy.items())})

# ---- S14 conversion diagnostic ----
convc=Counter()
for p in PAR:
    for mech in ("P1_firstpull_turn","P2_failed_reclaim","P3_lower_high","P5_pull_disp"):
        if pullback_trade(p,mech,2.0,"STRESS"): convc[mech]+=1
log(f"S14 CONVERSION of {len(PAR)} parents -> causal entry: "+", ".join(f"{k}:{v} ({v/len(PAR)*100:.0f}%)" for k,v in convc.items()))

# ---- A vs B + gates ----
log("=== POST-BREAK PULLBACK ENTRY (B) vs IMMEDIATE (A), STRESS ===")
records=[]
for rr in (2.0,3.0):
    Aimm=M([immediate_trade(p,rr,"STRESS") for p in PAR],rr)
    log(f"A_IMMEDIATE rr{rr}: n={Aimm.get('n')} WR={Aimm.get('WR')} avgR={Aimm.get('avgR')} medR={Aimm.get('medR')} b5rem={Aimm.get('b5rem')} top10%={Aimm.get('top10')}")
    for mech in ("P1_firstpull_turn","P2_failed_reclaim","P3_lower_high","P5_pull_disp"):
        B=M([pullback_trade(p,mech,rr,"STRESS") for p in PAR],rr)
        if B.get("n",0)<12: log(f"B-{mech}-rr{rr}: n={B.get('n')} SPARSE"); records.append(dict(id=f"PSP-{mech}-rr{rr}",m=B,status="SPARSE")); continue
        gate=B["avgR"]>0 and B["b5rem"]>0 and B["b10rem"]>0 and B["top10"]<=60 and B["avgR"]>(Aimm.get("avgR") or -9)
        st="SURVIVE" if gate else "FAIL"
        records.append(dict(id=f"PSP-{mech}-rr{rr}",m=B,status=st,vs_immediate=round(B["avgR"]-(Aimm.get("avgR") or 0),4)))
        log(f"B-{mech}-rr{rr}: n={B['n']} WR={B['WR']} avgR={B['avgR']} medR={B['medR']} b5rem={B['b5rem']} b10rem={B['b10rem']} top10%={B['top10']} medTP={B['medTP']}p vsImm={records[-1]['vs_immediate']} temporal={B['temporal']} -> {st}")
surv=[r for r in records if r['status']=='SURVIVE']
json.dump(dict(records=records,parents=len(PAR),survivors=[r['id'] for r in surv]),open(os.path.join(SP,"psp_records.json"),"w"),indent=1,default=float)
log(f"COMPLETE: {len(surv)} survivors: {[r['id'] for r in surv]}")

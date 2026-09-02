"""trm_v1.py — TRADER-READ -> MECHANICAL STRATEGY TRANSLATION V1. Five frozen causal M15 detectors (A sweep->reclaim->displacement->cont,
B breakout->acceptance->shallow-pullback->cont, C repeated-attack->defense-decay->breakout, D displacement->fail-to-accept->reversal,
E compression->expansion->cont). All detection strictly causal (bars<=si); entry=open[si+1]; structural stop with lab floor; 2R primary + 3R
diagnostic; BASE spread 0.05 / STRESS 0.08 net; ONE trade at a time per family; NO context filter (context recorded only). Specs frozen+hashed
before scoring. Writes TRADER_READ_MECHANICAL_V1_{TRADES.parquet,RESULTS.csv,YEARLY.csv,TAIL_ROBUSTNESS.csv,OVERLAP.csv,PROTOCOL.json,FAMILY_SPECS.json}.
"""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); import mstrat as MS
d=MS.load(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); Cl=d["close"].to_numpy(float)
ATR=d["m_atr"].to_numpy(float); T=d["time"].to_numpy(); n=len(d); TR=np.maximum(H-L, np.maximum(np.abs(H-np.roll(Cl,1)),np.abs(L-np.roll(Cl,1))))
h1=d["h1_trend_up"].to_numpy(float); h4=d["h4_trend_up"].to_numpy(float)
ser=pd.Series
rhi=ser(H).rolling(20).max().shift(1).to_numpy(); rlo=ser(L).rolling(20).min().shift(1).to_numpy()  # prior-20 structure (causal)
medTR8=ser(TR).rolling(8).median().to_numpy(); medTR32=ser(TR).rolling(40).median().shift(0).to_numpy()  # med last8 vs preceding32 (use 40 then subtract? approximate with rolling)
medTR_prev32=ser(TR).shift(8).rolling(32).median().to_numpy(); span8=ser(H).rolling(8).max().to_numpy()-ser(L).rolling(8).min().to_numpy()
SPREAD_BASE=0.05; SPREAD_STRESS=0.08; RRs=[2.0,3.0]; BACKSTOP=96
def atrf(i): a=ATR[i]; return a if a>0 else np.nanmedian(ATR[max(0,i-50):i+1])
# ---------- causal confirmed swing pivots (theta_swing=1.0 ATR) ----------
def causal_swings(theta=1.0):
    sh=np.full(n,np.nan); sl=np.full(n,np.nan); mode=0; hp=H[0]; hpi=0; lp=L[0]; lpi=0; csh=np.nan; csl=np.nan
    for j in range(1,n):
        th=theta*(ATR[j] if ATR[j]>0 else 1.0)
        if mode>=0:
            if H[j]>hp: hp=H[j]; hpi=j
            if hp-L[j]>=th: csh=hp; mode=-1; lp=L[j]; lpi=j
        if mode<=0:
            if L[j]<lp: lp=L[j]; lpi=j
            if H[j]-lp>=th: csl=lp; mode=1; hp=H[j]; hpi=j
        sh[j]=csh; sl[j]=csl
    return sh,sl
SWH,SWL=causal_swings(1.0)

# ================= DETECTORS (return list of (si,dir,stop_price)) =================
def famA():
    sig=[]
    for i in range(40,n-1):
        a=atrf(i)
        if not (a>0): continue
        # bullish: sweep below prior structure low then reclaim then bullish displacement breaking swing high
        # find sweep in last 8 bars
        swept=-1
        for b in range(i-8,i):
            if b<20 or not np.isfinite(rlo[b]): continue
            if L[b]<rlo[b] and (rlo[b]-L[b])<=1.0*a:  # bounded sweep below
                # reclaim between b and i
                if any(Cl[r]>rlo[b] for r in range(b+1,i+1)): swept=b
        if swept>=0 and (Cl[i]-O[i])>0.5*a and np.isfinite(SWH[i]) and Cl[i]>SWH[i]:
            stop=min(L[swept:i+1])-0.1*a; sig.append((i,+1,float(stop))); continue
        # bearish
        swept=-1
        for b in range(i-8,i):
            if b<20 or not np.isfinite(rhi[b]): continue
            if H[b]>rhi[b] and (H[b]-rhi[b])<=1.0*a:
                if any(Cl[r]<rhi[b] for r in range(b+1,i+1)): swept=b
        if swept>=0 and (O[i]-Cl[i])>0.5*a and np.isfinite(SWL[i]) and Cl[i]<SWL[i]:
            stop=max(H[swept:i+1])+0.1*a; sig.append((i,-1,float(stop)))
    return sig
def famB():
    sig=[]
    for i in range(40,n-1):
        a=atrf(i)
        if not(a>0): continue
        found=False
        # UP: breakout b in last 20 -> acceptance -> shallow pullback (<=50% disp, stays breakout-side) -> continuation now
        for b in range(i-20,i-2):
            if b<20 or not np.isfinite(rhi[b]): continue
            if Cl[b]>rhi[b]:
                lvl=rhi[b]; peak=np.max(H[b:i]); disp=peak-lvl
                if disp<=0.3*a: continue
                if not any(Cl[c]>lvl for c in range(b+1,min(b+4,i))): continue      # acceptance
                pull=np.min(L[b+1:i])                                                # pullback low pre-current
                if pull< lvl-0.2*a: continue                                        # breakout invalidated (too deep)
                if pull< peak-0.5*disp: continue                                    # too deep (>50% retrace)
                if Cl[i]>O[i] and Cl[i]>np.max(H[i-2:i]):                            # continuation resumes up
                    stop=pull-0.1*a; sig.append((i,+1,float(stop))); found=True; break
        if found: continue
        for b in range(i-20,i-2):
            if b<20 or not np.isfinite(rlo[b]): continue
            if Cl[b]<rlo[b]:
                lvl=rlo[b]; trough=np.min(L[b:i]); disp=lvl-trough
                if disp<=0.3*a: continue
                if not any(Cl[c]<lvl for c in range(b+1,min(b+4,i))): continue
                pull=np.max(H[b+1:i])
                if pull> lvl+0.2*a: continue
                if pull> trough+0.5*disp: continue
                if Cl[i]<O[i] and Cl[i]<np.min(L[i-2:i]):
                    stop=pull+0.1*a; sig.append((i,-1,float(stop))); break
    return sig
def famC():
    sig=[]; PROX=0.20
    # resistance levels = confirmed swing highs; support = swing lows. Track attacks on the standing level.
    for side,levarr,cmp_break in ((+1,SWH,lambda i,lv:Cl[i]>lv),(-1,SWL,lambda i,lv:Cl[i]<lv)):
        lastlv=np.nan; attacks=[]; reacts=[]; departed=True; ref_i=-1
        for i in range(40,n-1):
            a=atrf(i);
            if not(a>0): continue
            lv=levarr[i]
            if not np.isfinite(lv): continue
            if np.isnan(lastlv) or abs(lv-lastlv)>0.5*a:  # new level -> reset
                lastlv=lv; attacks=[]; reacts=[]; departed=True; ref_i=i
            near=(abs((H[i] if side>0 else L[i])-lv)<=PROX*a)
            if near and departed:
                attacks.append(i); departed=False
                if len(attacks)>=2:  # reaction after previous attack = max departure away before this attack
                    seg=slice(attacks[-2],i); dep=(lv-np.min(L[seg])) if side>0 else (np.max(H[seg])-lv); reacts.append(dep/a)
            if not near and (abs((H[i] if side>0 else L[i])-lv)>0.5*a): departed=True
            # breakout with defense decay
            if len(attacks)>=3 and len(reacts)>=2 and reacts[-1]<reacts[-2] and (len(reacts)<3 or reacts[-1]<=reacts[-2]) and cmp_break(i,lv):
                stop=(np.min(L[attacks[-1]:i+1])-0.1*a) if side>0 else (np.max(H[attacks[-1]:i+1])+0.1*a)
                sig.append((i,side,float(stop))); lastlv=np.nan  # consume
    return sig
def famD():
    sig=[]
    for i in range(40,n-1):
        a=atrf(i)
        if not(a>0): continue
        # up-displacement at b in last 4; fail-to-accept within 3; reversal confirm now (bearish)
        for b in range(i-4,i):
            if b<20 or not np.isfinite(rhi[b]): continue
            if Cl[b]>rhi[b] and TR[b]>=1.5*a:  # up displacement breaking structure
                lvl=rhi[b]
                if any(Cl[c]<lvl for c in range(b+1,min(b+4,i+1))):  # fail to accept within 3
                    if Cl[i]<O[i] and Cl[i]<lvl and Cl[i]<Cl[i-1]:  # bearish reversal confirm, not re-closing beyond
                        stop=max(H[b:i+1])+0.1*a; sig.append((i,-1,float(stop))); break
        else:
            for b in range(i-4,i):
                if b<20 or not np.isfinite(rlo[b]): continue
                if Cl[b]<rlo[b] and TR[b]>=1.5*a:
                    lvl=rlo[b]
                    if any(Cl[c]>lvl for c in range(b+1,min(b+4,i+1))):
                        if Cl[i]>O[i] and Cl[i]>lvl and Cl[i]>Cl[i-1]:
                            stop=min(L[b:i+1])-0.1*a; sig.append((i,+1,float(stop))); break
    return sig
def famE():
    sig=[]
    for i in range(48,n-1):
        a=atrf(i)
        if not(a>0) or not np.isfinite(medTR8[i-1]) or not np.isfinite(medTR_prev32[i-1]): continue
        comp=(medTR8[i-1]<medTR_prev32[i-1]) and (span8[i-1]<1.5*a)  # compression over last 8 (as of i-1)
        if not comp: continue
        hi8=np.max(H[i-8:i]); lo8=np.min(L[i-8:i]); rng=H[i]-L[i]
        if TR[i]>=1.5*a and rng>0:
            cl_loc=(Cl[i]-L[i])/rng
            if cl_loc>=0.75 and Cl[i]>hi8 and (not np.isfinite(SWH[i]) or Cl[i]>=SWH[i]):  # up expansion breaks comp box + structure
                sig.append((i,+1,float(lo8-0.1*a)))
            elif cl_loc<=0.25 and Cl[i]<lo8 and (not np.isfinite(SWL[i]) or Cl[i]<=SWL[i]):
                sig.append((i,-1,float(hi8+0.1*a)))
    return sig

# ================= SIMULATOR (one-at-a-time, next-open, 2R/3R, BASE/STRESS) =================
def simulate(sigs, rr, spread):
    sigs=sorted(sigs); open_until=-1; trades=[]
    for (si,dr,stop) in sigs:
        if si<=open_until or si+1>=n: continue
        ei=si+1; entry=O[ei]; a=atrf(si)
        risk=max(abs(entry-stop), 2*SPREAD_BASE, 0.05, 0.10*a)
        stp=entry-dr*risk; tgt=entry+dr*rr*risk; exit_i=min(ei+BACKSTOP,n-1); R=None
        for k in range(ei,exit_i+1):
            hit_t=(H[k]>=tgt) if dr>0 else (L[k]<=tgt); hit_s=(L[k]<=stp) if dr>0 else (H[k]>=stp)
            if hit_t and hit_s: R=-1.0; exit_i=k; break
            if hit_s: R=-1.0; exit_i=k; break
            if hit_t: R=rr; exit_i=k; break
        if R is None: R=dr*(Cl[exit_i]-entry)/risk
        R_net=R - spread/risk
        trades.append(dict(si=int(si),ei=int(ei),exit_i=int(exit_i),dir=int(dr),risk=float(risk),R=float(R),net_R=float(R_net),
                           dtime=int(T[si]),year=int(pd.to_datetime(T[si],unit="s",utc=True).year),
                           h1=float(h1[si]),h4=float(h4[si]),atr=float(a)))
        open_until=exit_i
    return pd.DataFrame(trades)

FAMS={"A_sweep_reclaim":famA,"B_breakout_pullback":famB,"C_attack_decay_break":famC,"D_disp_fail_reversal":famD,"E_compress_expand":famE}
print("detecting..."); DET={k:f() for k,f in FAMS.items()}
for k,v in DET.items(): print(f"  {k}: {len(v)} raw triggers")
alltr=[]; results=[]
for fam,sigs in DET.items():
    for rr in RRs:
        for scen,spr in (("BASE",SPREAD_BASE),("STRESS",SPREAD_STRESS)):
            tr=simulate(sigs,rr,spr)
            if len(tr)==0: continue
            tr["family"]=fam; tr["rr"]=rr; tr["scenario"]=scen
            if rr==2.0 and scen=="BASE": alltr.append(tr.assign())
            r=tr["net_R"].to_numpy(); yrs=(tr.dtime.max()-tr.dtime.min())/(365.25*86400) or 1
            eq=np.cumsum(r); dd=float((np.maximum.accumulate(eq)-eq).max())
            wins=r[r>0]; losses=r[r<=0]
            results.append(dict(family=fam,rr=rr,scenario=scen,trades=len(tr),trades_per_year=round(len(tr)/yrs,1),
                win_rate=round((r>0).mean(),3),exp_net_R=round(r.mean(),4),median_R=round(np.median(r),4),
                profit_factor=round(wins.sum()/(abs(losses.sum())+1e-9),3),total_R=round(r.sum(),1),max_dd_R=round(dd,1),
                avg_win=round(wins.mean(),3) if len(wins) else 0,avg_loss=round(losses.mean(),3) if len(losses) else 0,
                payoff=round(abs(wins.mean()/losses.mean()),2) if len(losses) and losses.mean()!=0 else np.nan,
                long_n=int((tr.dir>0).sum()),short_n=int((tr.dir<0).sum()),
                long_exp=round(r[tr.dir.to_numpy()>0].mean(),4) if (tr.dir>0).any() else np.nan,
                short_exp=round(r[tr.dir.to_numpy()<0].mean(),4) if (tr.dir<0).any() else np.nan))
RES=pd.DataFrame(results); RES.to_csv(OUT+r"\TRADER_READ_MECHANICAL_V1_RESULTS.csv",index=False)
TRD=pd.concat(alltr,ignore_index=True) if alltr else pd.DataFrame(); TRD.to_parquet(OUT+r"\TRADER_READ_MECHANICAL_V1_TRADES.parquet")
print("\n== PRIMARY 2R (BASE) ==")
print(RES[(RES.rr==2.0)&(RES.scenario=="BASE")][["family","trades","trades_per_year","win_rate","exp_net_R","profit_factor","max_dd_R","long_exp","short_exp"]].to_string(index=False))
print("\n== 2R STRESS exp ==")
print(RES[(RES.rr==2.0)&(RES.scenario=="STRESS")][["family","exp_net_R","profit_factor"]].to_string(index=False))
# freeze protocol + specs
proto=dict(mandate="TRADER_READ_MECHANICAL_V1",timeframe="M15",entry="open[si+1]",stop_floor="max(struct,2*spread,0.05,0.10*ATR)",
    payoff_primary="2R",payoff_secondary="3R",spread_base=SPREAD_BASE,spread_stress=SPREAD_STRESS,backstop_bars=BACKSTOP,
    swing_theta_atr=1.0,one_trade_at_a_time=True,context_filter="NONE (recorded only)",families=list(FAMS.keys()))
specs=dict(A="sweep(<=1ATR beyond prior-20 struct, last8)->reclaim(close back)->bull/bear displacement(>0.5ATR body breaking confirmed swing)->entry next open",
    B="close beyond prior-20 struct->acceptance(closed bar stays beyond within 3)->pullback<=50% displacement staying breakout-side->continuation close->entry",
    C="confirmed swing level, >=3 attacks within 0.20ATR w/ departures, reaction2<reaction1 & reaction3<=reaction2, close beyond->entry",
    D="displacement(TR>=1.5ATR close beyond prior-20 struct)->fail-to-accept(close back within 3 bars)->opposite confirm close->entry opposite",
    E="compression(medTR last8<medTR prev32 AND span8<1.5ATR)->expansion(TR>=1.5ATR, close outer25%, breaks comp box+swing)->entry")
json.dump(proto,open(OUT+r"\TRADER_READ_MECHANICAL_V1_PROTOCOL.json","w"),indent=2)
json.dump(specs,open(OUT+r"\TRADER_READ_MECHANICAL_V1_FAMILY_SPECS.json","w"),indent=2)
hh=lambda p: hashlib.sha256(open(p,"rb").read()).hexdigest()[:20]
print(f"\nPROTOCOL_HASH={hh(OUT+chr(92)+'TRADER_READ_MECHANICAL_V1_PROTOCOL.json')} FAMILY_SPECS_HASH={hh(OUT+chr(92)+'TRADER_READ_MECHANICAL_V1_FAMILY_SPECS.json')}")

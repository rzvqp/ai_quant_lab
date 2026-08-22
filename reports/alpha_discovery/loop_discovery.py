"""ALPHA-XAUUSD-AUTONOMOUS-DISCOVERY-LOOP-FIRST-ROBUST-001. Failure-mode-driven pivot: adverse-first is the
dominant killer -> enter AFTER the adverse move has already failed. NEW families: FAILED_REVERSAL_CONT,
HTF_LEVEL_REACT, SESSION_ACCEPT_CONT. Natural structural stops, RR {1,1.5,2} (alt-profile allowed, S27),
path-first, DISC/CONF, years, top-trade-removal, costs. Price-only, DEV-only. No MI/S5 change."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
PIP=0.10; COST=2.4; HOR=48
tfs,META=D.build(); M=tfs["M15"]; H1=tfs["H1"]; H4=tfs["H4"]
o=M["open"].to_numpy();h=M["high"].to_numpy();l=M["low"].to_numpy();c=M["close"].to_numpy()
e20=M["ema20"].to_numpy();e50=M["ema50"].to_numpy();atr=M["atr"].to_numpy()
mct=M["close_time"].to_numpy().astype("int64");mt=M["time"].to_numpy().astype("int64")
dev=M["is_dev"].to_numpy();dt=pd.to_datetime(mt,unit="s",utc=True);yr=dt.year.to_numpy();lon=dt.tz_convert("Europe/London").hour.to_numpy();n=len(o)
h1ct=H1["close_time"].to_numpy().astype("int64");h1reg=H1["regime"].to_numpy();h1l=H1["low"].to_numpy();h1h=H1["high"].to_numpy()
h4ct=H4["close_time"].to_numpy().astype("int64");h4reg=H4["regime"].to_numpy()
ih1=np.searchsorted(h1ct,mct,side="right")-1;ih4=np.searchsorted(h4ct,mct,side="right")-1
h1up=np.array([h1reg[k]=="TREND_UP" if k>=0 else False for k in ih1]);h1dn=np.array([h1reg[k]=="TREND_DOWN" if k>=0 else False for k in ih1])
h4up=np.array([h4reg[k]=="TREND_UP" if k>=0 else False for k in ih4]);h4dn=np.array([h4reg[k]=="TREND_DOWN" if k>=0 else False for k in ih4])

def parents(mech, side):
    up=(h4up&h1up) if side=="LONG" else (h4dn&h1dn); out=[]; last=-99
    for i in range(30,n-1):
        if not dev[i] or not up[i] or atr[i]!=atr[i]: continue
        sig=False; stop=None
        if mech=="FAILED_REV":  # structural reversal attempt then FAILS/reclaims (adverse already in)
            if side=="LONG":
                brokelvl=min(l[i-6:i-1])
                broke=any(c[k]<brokelvl for k in range(i-4,i))  # countertrend breakdown occurred
                if broke and c[i]>brokelvl and c[i]>e20[i] and c[i]>c[i-1]:
                    sig=True; stop=min(l[i-4:i+1])-2*PIP
            else:
                brokelvl=max(h[i-6:i-1]); broke=any(c[k]>brokelvl for k in range(i-4,i))
                if broke and c[i]<brokelvl and c[i]<e20[i] and c[i]<c[i-1]:
                    sig=True; stop=max(h[i-4:i+1])+2*PIP
        elif mech=="HTF_REACT":  # pullback to H1 structural swing, holds, reacts
            k=ih1[i]
            if k<4: continue
            if side=="LONG":
                sw=min(h1l[k-4:k]); near=abs(l[i]-sw)<0.5*atr[i] and l[i]>=sw*0.999; react=c[i]>o[i] and c[i]>c[i-1]
                if near and react and l[i]==min(l[i-3:i+1]): sig=True; stop=min(l[i-2:i+1])-2*PIP
            else:
                sw=max(h1h[k-4:k]); near=abs(h[i]-sw)<0.5*atr[i] and h[i]<=sw*1.001; react=c[i]<o[i] and c[i]<c[i-1]
                if near and react and h[i]==max(h[i-3:i+1]): sig=True; stop=max(h[i-2:i+1])+2*PIP
        elif mech=="SESSION_ACC":  # London directional first-leg + acceptance + pullback-hold continuation
            if not (7<=lon[i]<11): continue
            base=min(l[i-6:i]) if side=="LONG" else max(h[i-6:i])
            leg=(c[i-1]-base)/PIP if side=="LONG" else (base-c[i-1])/PIP
            if side=="LONG":
                if leg>40 and c[i-1]>e20[i-1] and l[i]<l[i-1] and c[i]>o[i]: sig=True; stop=min(l[i-3:i+1])-2*PIP
            else:
                if leg>40 and c[i-1]<e20[i-1] and h[i]>h[i-1] and c[i]<o[i]: sig=True; stop=max(h[i-3:i+1])+2*PIP
        if sig and stop is not None and i-last>=4: out.append(dict(i=i,stop=stop,side=side)); last=i
    return out

def evaluate(pset, side, rr):
    rows=[]
    for s in pset:
        i=s["i"]; e1=i+1
        if e1>=n: continue
        entry=o[e1]; stop=s["stop"]; risk=abs(entry-stop)/PIP
        if risk<20 or risk>160: continue
        tgt=entry+rr*risk*PIP if side=="LONG" else entry-rr*risk*PIP
        reach=None;mfe=0.;mae=0.
        for j in range(e1,min(e1+HOR,n)):
            mfe=max(mfe,(h[j]-entry)/PIP if side=="LONG" else (entry-l[j])/PIP)
            mae=max(mae,(entry-l[j])/PIP if side=="LONG" else (h[j]-entry)/PIP)
            hs=(l[j]<=stop) if side=="LONG" else (h[j]>=stop);ht=(h[j]>=tgt) if side=="LONG" else (l[j]<=tgt)
            if hs and ht: reach=("stop",j);break
            if hs: reach=("stop",j);break
            if ht: reach=("tgt",j);break
        if reach and reach[0]=="tgt": R=rr
        elif reach and reach[0]=="stop": R=-1.0
        else: xb=min(e1+HOR-1,n-1); R=((c[xb]-entry)/PIP if side=="LONG" else (entry-c[xb])/PIP)/risk
        R-=COST/risk
        rows.append(dict(R=R,mfe=mfe,mae=mae,risk=risk,yr=int(yr[i]),i=i))
    return rows

allidx=[]
for m in ("FAILED_REV","HTF_REACT","SESSION_ACC"):
    for sd in ("LONG","SHORT"): allidx+=[s["i"] for s in parents(m,sd)]
allidx=sorted(allidx); CUT=allidx[int(len(allidx)*0.6)] if allidx else 0
def metrics(rows):
    if not rows or len(rows)<20: return None
    Rs=np.array([r["R"] for r in rows]);wins=Rs[Rs>0].sum();losses=-Rs[Rs<0].sum()
    eq=np.cumsum(Rs);dd=float((np.maximum.accumulate(eq)-eq).max());s=np.sort(Rs)[::-1];b10=s[int(len(s)*.1):].mean()
    d=[r["R"] for r in rows if r["i"]<CUT];cf=[r["R"] for r in rows if r["i"]>=CUT]
    yy={y:round(float(np.mean([r["R"] for r in rows if r["yr"]==y])),3) for y in (2021,2022,2023) if any(r["yr"]==y for r in rows)}
    return dict(N=len(rows),WR=round(float((Rs>0).mean()),3),avg=round(float(Rs.mean()),3),PF=round(float(wins/losses),2) if losses>0 else 99,
                maxDD=round(dd,1),b10=round(float(b10),3),medSL=round(float(np.median([r["risk"] for r in rows])),0),
                medMFE=round(float(np.median([r["mfe"] for r in rows])),0),D=round(float(np.mean(d)),3) if d else np.nan,
                C=round(float(np.mean(cf)),3) if cf else np.nan,yy=yy)
print(f"AUTONOMOUS LOOP -- new families (H4+H1 aligned context, natural structural stop). DISC/CONF cut {dt[CUT].date() if allidx else 'NA'}")
print(f"{'mech-side rr':26} {'N':>4} {'WR':>5} {'avgR':>7} {'PF':>5} {'maxDD':>6} {'b10':>7} {'medSL':>5} {'medMFE':>6} {'DISC':>7} {'CONF':>7}  years")
robust=[]
for m in ("FAILED_REV","HTF_REACT","SESSION_ACC"):
    for sd in ("LONG","SHORT"):
        ps=parents(m,sd)
        for rr in (1.0,1.5,2.0):
            mt_=metrics(evaluate(ps,sd,rr))
            if not mt_: continue
            gate=(mt_["avg"]>0 and mt_["D"]>0 and mt_["C"]>0 and mt_["b10"]>0 and all(v>0 for v in mt_["yy"].values()) and mt_["N"]>=30)
            fl="  <== ROBUST?" if gate else ""
            print(f"  {m}-{sd} rr{rr:<4}: {mt_['N']:>4} {mt_['WR']:>5.2f} {mt_['avg']:>+7.3f} {mt_['PF']:>5} {mt_['maxDD']:>6} {mt_['b10']:>+7.3f} {mt_['medSL']:>5.0f} {mt_['medMFE']:>6.0f} {mt_['D']:>+7.3f} {mt_['C']:>+7.3f}  {mt_['yy']}{fl}")
            if gate: robust.append((m,sd,rr))
print(f"\nGate-passing (avgR>0, DISC>0, CONF>0, b10>0, all years>0, N>=30): {robust}")

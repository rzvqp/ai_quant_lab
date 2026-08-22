"""ALPHA-XAUUSD-AUTONOMOUS-HIGH-WR-PORTFOLIO-DISCOVERY-001. Search for high-WR ~1:1 (~70-100p SL/TP)
trend/continuation strategies. Mechanism-first, path-first, 1:1 geometry (H1-structural stop, TP=1R),
net STRESS. Funnel Stage1(MFE screen)->Stage2(path)->Stage3(1:1 conv)->Stage4(DISC/CONF)->Stage5(robustness).
LONG/SHORT separate. Autonomous. Price-only, DEV-only. No MI/S5 change."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import m5_data as D
PIP=0.10; COST=2.4; HOR=48
tfs,META=D.build(); M=tfs["M15"]; H1=tfs["H1"]; H4=tfs["H4"]
o=M["open"].to_numpy();h=M["high"].to_numpy();l=M["low"].to_numpy();c=M["close"].to_numpy()
e20=M["ema20"].to_numpy();e50=M["ema50"].to_numpy();atr=M["atr"].to_numpy();ama=M["atr_ma"].to_numpy()
mct=M["close_time"].to_numpy().astype("int64");mt=M["time"].to_numpy().astype("int64")
dev=M["is_dev"].to_numpy();yr=pd.to_datetime(mt,unit="s",utc=True).year.to_numpy();n=len(o)
h1ct=H1["close_time"].to_numpy().astype("int64");h1reg=H1["regime"].to_numpy();h1l=H1["low"].to_numpy();h1h=H1["high"].to_numpy()
h4ct=H4["close_time"].to_numpy().astype("int64");h4reg=H4["regime"].to_numpy()
ih1=np.searchsorted(h1ct,mct,side="right")-1;ih4=np.searchsorted(h4ct,mct,side="right")-1
h1up=np.array([h1reg[k]=="TREND_UP" if k>=0 else False for k in ih1]);h1dn=np.array([h1reg[k]=="TREND_DOWN" if k>=0 else False for k in ih1])
h4up=np.array([h4reg[k]=="TREND_UP" if k>=0 else False for k in ih4]);h4dn=np.array([h4reg[k]=="TREND_DOWN" if k>=0 else False for k in ih4])

def h1stop(i,side):
    k=ih1[i]
    if k<3: return None
    return (min(h1l[k-3:k+1])-2*PIP) if side=="LONG" else (max(h1h[k-3:k+1])+2*PIP)

# ---- M15 parent mechanisms (LONG; mirror SHORT via ctx) ----
def parents(mech, side):
    up=h1up if side=="LONG" else h1dn; broad=h4up if side=="LONG" else h4dn; out=[]; last=-99
    for i in range(30,n-1):
        if not dev[i] or not up[i] or atr[i]!=atr[i]: continue
        sig=False
        if mech=="TP_PB":         # trend pullback: dip past ema20 then reclaim
            if side=="LONG": sig=any(c[k]<e20[k] for k in range(i-4,i)) and c[i]>e20[i]>e50[i] and c[i]>c[i-1]
            else: sig=any(c[k]>e20[k] for k in range(i-4,i)) and c[i]<e20[i]<e50[i] and c[i]<c[i-1]
        elif mech=="TP_BREAK":    # shallow pullback then break consolidation extreme
            if side=="LONG":
                hh=max(h[i-8:i]); pb=min(l[i-4:i]); sig=c[i]>hh and c[i-1]<=hh and (hh-pb)<0.6*(hh-min(l[i-12:i-4]) if i>=12 else atr[i]*3)
            else:
                ll=min(l[i-8:i]); pb=max(h[i-4:i]); sig=c[i]<ll and c[i-1]>=ll and (pb-ll)<0.6*(max(h[i-12:i-4])-ll if i>=12 else atr[i]*3)
        elif mech=="FAILED_CT":   # failed countertrend: countertrend extreme then reclaim
            if side=="LONG": sig=l[i-1]<min(l[i-6:i-1]) and c[i]>c[i-1] and c[i]>o[i] and (c[i]-o[i])>0.5*atr[i]
            else: sig=h[i-1]>max(h[i-6:i-1]) and c[i]<c[i-1] and c[i]<o[i] and (o[i]-c[i])>0.5*atr[i]
        elif mech=="BREAK_1STPB": # structural break + first pullback holds
            if side=="LONG":
                brk=any(c[k]>max(h[k-12:k]) and (c[k]-o[k])>1.0*atr[k] for k in range(i-6,i-1))
                sig=brk and l[i]<l[i-1] and c[i]>o[i] and c[i]>e20[i]
            else:
                brk=any(c[k]<min(l[k-12:k]) and (o[k]-c[k])>1.0*atr[k] for k in range(i-6,i-1))
                sig=brk and h[i]>h[i-1] and c[i]<o[i] and c[i]<e20[i]
        elif mech=="DISP_ACCEPT": # displacement + acceptance (2nd close holds)
            if side=="LONG": sig=((c[i-1]-o[i-1])>1.0*atr[i-1]) and c[i]>c[i-1] and c[i]>o[i]
            else: sig=((o[i-1]-c[i-1])>1.0*atr[i-1]) and c[i]<c[i-1] and c[i]<o[i]
        if sig and i-last>=4: out.append(dict(i=i,side=side)); last=i
    return out

def evaluate(pset, side, rr=1.0, use_hor=False):
    rows=[]
    for s in pset:
        i=s["i"]; e1=i+1
        if e1>=n: continue
        entry=o[e1]; stop=h1stop(i,side)
        if stop is None: continue
        risk=abs(entry-stop)/PIP
        if risk<30 or risk>150: continue    # desired ~70-100p zone (allow 30-150 natural)
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
        else:
            xb=min(e1+HOR-1,n-1); R=((c[xb]-entry)/PIP if side=="LONG" else (entry-c[xb])/PIP)/risk if use_hor else -1.0
        R-=COST/risk
        rows.append(dict(R=R,mfe=mfe,mae=mae,risk=risk,yr=int(yr[i]),i=i,win=R>0))
    return rows

def metrics(rows):
    if not rows or len(rows)<15: return None
    Rs=np.array([r["R"] for r in rows]); wins=Rs[Rs>0].sum(); losses=-Rs[Rs<0].sum()
    eq=np.cumsum(Rs); dd=float((np.maximum.accumulate(eq)-eq).max())
    cl=mcl=0
    for r in Rs:
        cl=cl+1 if r<0 else 0; mcl=max(mcl,cl)
    s=np.sort(Rs)[::-1]; b10=s[int(len(s)*.1):].mean(); b5=s[int(len(s)*.05):].mean()
    d=[r["R"] for r in rows if r["i"]<CUT]; cf=[r["R"] for r in rows if r["i"]>=CUT]
    yy={y:(round(float(np.mean([r["R"] for r in rows if r["yr"]==y])),3),int(sum(r["yr"]==y for r in rows))) for y in (2021,2022,2023) if any(r["yr"]==y for r in rows)}
    return dict(N=len(rows),WR=round(float((Rs>0).mean()),3),avg=round(float(Rs.mean()),3),med=round(float(np.median(Rs)),3),
                PF=round(float(wins/losses),2) if losses>0 else 99,maxDD=round(dd,2),mcl=mcl,b5=round(float(b5),3),b10=round(float(b10),3),
                medSL=round(float(np.median([r["risk"] for r in rows])),0),medMFE=round(float(np.median([r["mfe"] for r in rows])),0),
                D=round(float(np.mean(d)),3) if d else np.nan,C=round(float(np.mean(cf)),3) if cf else np.nan,yy=yy)

MECHS=["TP_PB","TP_BREAK","FAILED_CT","BREAK_1STPB","DISP_ACCEPT"]
allidx=[]
for m in MECHS:
    for sd in ("LONG","SHORT"): allidx+=[s["i"] for s in parents(m,sd)]
allidx=sorted(allidx); CUT=allidx[int(len(allidx)*0.6)]
print(f"HP-PORTFOLIO search: {len(MECHS)} mechanisms x LONG/SHORT, 1:1 geometry (H1 stop 30-150p), net STRESS. DISC/CONF cut {pd.to_datetime(mct[CUT],unit='s',utc=True).date()}")
print(f"\n{'mech-side':20} {'N':>4} {'WR':>5} {'avgR':>7} {'PF':>5} {'maxDD':>6} {'mcl':>4} {'b10':>7} {'medSL':>5} {'DISC':>7} {'CONF':>7}  years")
surv=[]
for m in MECHS:
    for sd in ("LONG","SHORT"):
        mt_=metrics(evaluate(parents(m,sd),sd,1.0))
        if not mt_: print(f"  {m}-{sd:5}: too few"); continue
        flag=""
        if mt_["WR"]>=0.55 and mt_["avg"]>0 and mt_["D"]>0 and mt_["C"]>0 and mt_["b10"]>0 and all(v[0]>0 for v in mt_["yy"].values()): flag="  <== SURVIVOR"
        print(f"  {m}-{sd:5}: {mt_['N']:>4} {mt_['WR']:>5.2f} {mt_['avg']:>+7.3f} {mt_['PF']:>5} {mt_['maxDD']:>6} {mt_['mcl']:>4} {mt_['b10']:>+7.3f} {mt_['medSL']:>5.0f} {mt_['D']:>+7.3f} {mt_['C']:>+7.3f}  {mt_['yy']}{flag}")
        if flag: surv.append((f"{m}-{sd}",m,sd))
print(f"\nStage-4/5 survivors (WR>=0.55, avgR>0, DISC>0, CONF>0, b10>0, all years>0): {[s[0] for s in surv]}")
import pickle; pickle.dump(surv,open(os.path.join(SP,"_hp_surv.pkl"),"wb"))

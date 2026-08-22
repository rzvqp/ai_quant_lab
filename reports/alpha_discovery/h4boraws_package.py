"""ALPHA-H4-BO-RAW-S-VALIDATION-PACKAGE-COMPLETION-001. MECHANICAL completion of the FROZEN H4-bo-raw-S-rr1.5.
Recovers the exact frozen strategy from econ_campaign.py (functions copied VERBATIM, no logic change) and
DERIVES the missing economics (PF, maxDD, max-loss, consec-losses, WR gross/base/stress, best-1/5/10%-removed,
per-block/year, CALIB) on a SINGLE-SEQUENCE chronological ledger. NO retuning/parameter change. Derived metrics
are marked DERIVED_DURING_PACKAGE_COMPLETION, NOT used to retune. Cross-checked vs Statistician f890b0e."""
import sys, os, json, hashlib, numpy as np, pandas as pd
from collections import defaultdict
WP5B=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b"
if os.path.join(WP5B,"code") not in sys.path: sys.path.insert(0, os.path.join(WP5B,"code"))
import mstrat
SP=os.path.dirname(os.path.abspath(__file__)); TICK=mstrat.TICK; MKT=os.path.join(WP5B,"data","market"); PIP=0.10
# ---- FROZEN config (verbatim from econ_campaign.py) ----
BLOCKS={"b0":(1311697800,1380300300),"b1":(1452502800,1523015550),"calib":(1597128300,1630844100)}
DEVB=("b0","b1")
CM=json.load(open(r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"))
RT={"GROSS":0.0,"BASE":CM["base_ratified"]["round_trip_total"],"STRESS":CM["stress_ratified"]["round_trip_total"]}
def load_tf(kind):
    if kind=="M15": d=mstrat.load()[["time","open","high","low","close","m_atr"]].copy()
    else:
        f={"H1":"OANDA_XAUUSD_H1_from_M15_v2.csv","H4":"OANDA_XAUUSD_H4_from_M15_v2.csv"}[kind]
        d=pd.read_csv(os.path.join(MKT,f))
        tr=np.maximum(d["high"]-d["low"],np.maximum((d["high"]-d["close"].shift(1)).abs(),(d["low"]-d["close"].shift(1)).abs()))
        d["m_atr"]=tr.rolling(14).mean()
    d=d.sort_values("time").reset_index(drop=True)
    coarser={"M15":"OANDA_XAUUSD_H4_from_M15_v2.csv","H1":"OANDA_XAUUSD_H4_from_M15_v2.csv","H4":"OANDA_XAUUSD_D1_from_M15_v2.csv"}[kind]
    x=pd.read_csv(os.path.join(MKT,coarser)).sort_values("time")
    e20=x["close"].ewm(span=20,adjust=True).mean();e50=x["close"].ewm(span=50,adjust=True).mean();x["trend_up"]=(e20>e50).astype(float)
    d=pd.merge_asof(d,x[["time","trend_up"]].rename(columns={"time":"av"}),left_on="time",right_on="av",direction="backward").drop(columns="av")
    return d
def slices(kind):
    d=load_tf(kind);t=d["time"].astype("int64").to_numpy();out={}
    for bn,(s,e) in BLOCKS.items(): out[bn]=d[(t>=s)&(t<=e)].reset_index(drop=True)
    return out
def rmin(a,w): return pd.Series(a).rolling(w).min().shift(1).to_numpy()
def rmax(a,w): return pd.Series(a).rolling(w).max().shift(1).to_numpy()
def _arr(sl): return sl["open"].to_numpy(),sl["high"].to_numpy(),sl["low"].to_numpy(),sl["close"].to_numpy(),sl["m_atr"].to_numpy()
def mk_breakout_raw_short(sl):   # == mk_breakout(up=False, lb=20, accept=False)
    o,hi,lo,cl,atr=_arr(sl);L=rmin(lo,20);out=[]
    for i in range(22,len(sl)-2):
        if cl[i]<L[i] and np.isfinite(L[i]): out.append((i,"short",L[i]))
    return out
def build_signals(SL, blocks):   # verbatim logic (up=False)
    sig=[]
    for bn in blocks:
        sl=SL[bn];o,hi,lo,cl,atr=_arr(sl);tu=sl["trend_up"].to_numpy();tm=sl["time"].astype("int64").to_numpy();nb=len(sl);HOR=48
        for (i,side,brk) in mk_breakout_raw_short(sl):
            if not (0<i<nb-1): continue
            if not (tu[i]<=0.5): continue            # D1-down aligned (short)
            ei=i+1
            if ei>=nb-1: continue
            entry=o[ei]
            if atr[i]!=atr[i]: continue
            sl_usd=max(abs(entry-brk)+0.3*atr[i],0.8*atr[i])
            if not (sl_usd>0): continue
            j0=ei+1;j1=min(j0+HOR,nb)
            if j1<=j0: continue
            fh=hi[j0:j1];fl=lo[j0:j1];mfe=float(entry-fl.min());mae=float(fh.max()-entry)
            sig.append(dict(block=bn,si=i,ei=ei,entry=entry,sl_usd=sl_usd,mfe=mfe,mae=mae,dir=-1,etime=int(tm[ei])))
    return sig
def realized(SL, sig, k, scen, blocks):
    cfg=dict(mstrat.CFG);cfg["spread_ticks"]=0.0;cfg["slip_ticks"]=RT[scen]/(2*TICK);out=[]
    for bn in blocks:
        sl=SL[bn];setups=[]
        for s in sig:
            if s["block"]!=bn: continue
            stop=s["entry"]-s["dir"]*s["sl_usd"]
            setups.append(dict(si=s["si"],ei=s["ei"],dir=s["dir"],stop=float(stop),exit_kind="rr",exit_param=float(k)))
        led=mstrat.simulate(sl,setups,cfg)
        for r,si in zip(led["R"],led["si"]): out.append(dict(r=float(r),block=bn,si=int(si)))
    return out

K=1.5; SL=slices("H4")
sig=build_signals(SL,DEVB)
g=realized(SL,sig,K,"GROSS",DEVB);b=realized(SL,sig,K,"BASE",DEVB);s=realized(SL,sig,K,"STRESS",DEVB)
# match by (block, si) -> single-sequence chronological ledger by entry time
etime={(x["block"],x["si"]):x for x in sig}
key=lambda x:(x["block"],x["si"])
gm={key(x):x["r"] for x in g};bm={key(x):x["r"] for x in b};sm={key(x):x["r"] for x in s}
keys=sorted(sm.keys(),key=lambda kk:etime[kk]["etime"])
ledger=[]
for kk in keys:
    e=etime[kk]; ledger.append(dict(block=kk[0],etime=e["etime"],entry_utc=str(pd.to_datetime(e["etime"],unit="s",utc=True)),
        side="SHORT",entry=round(e["entry"],2),sl_usd=round(e["sl_usd"],2),sl_pips=round(e["sl_usd"]/PIP,1),
        tp_pips=round(K*e["sl_usd"]/PIP,1),R_gross=round(gm.get(kk,float("nan")),4),R_base=round(bm.get(kk,float("nan")),4),R_stress=round(sm[kk],4)))
rg=np.array([x["R_gross"] for x in ledger]);rb=np.array([x["R_base"] for x in ledger]);rs=np.array([x["R_stress"] for x in ledger])
N=len(ledger)
def wr(r): return round(float((r>0).mean()),4)
def wr_reachedtgt(r): return round(float((r>=K-0.05).mean()),4)   # frozen econ_campaign convention (gross reached target)
def pf(r): w=r[r>0].sum();lo=-r[r<0].sum();return round(float(w/lo),4) if lo>0 else 99.0
def maxdd(r): eq=np.cumsum(r);return round(float((np.maximum.accumulate(eq)-eq).max()),3)
def consec(r):
    c=m=0
    for x in r:
        c=c+1 if x<0 else 0;m=max(m,c)
    return m
def brem(r,p): srt=np.sort(r)[::-1];kk=max(1,int(len(r)*p));return round(float(srt[kk:].mean()),4)
per_yr={}; per_blk=defaultdict(list)
for x in ledger:
    y=pd.to_datetime(x["etime"],unit="s",utc=True).year;per_yr.setdefault(y,[]).append(x["R_stress"]);per_blk[x["block"]].append(x["R_stress"])
# CALIB
sigc=build_signals(SL,("calib",));sc=realized(SL,sigc,K,"STRESS",("calib",));rc=np.array([x["r"] for x in sc])
active_months=round(((BLOCKS["b0"][1]-BLOCKS["b0"][0])+(BLOCKS["b1"][1]-BLOCKS["b1"][0]))/(30*24*3600),1)
econ=dict(
 N=N,
 # §6/§13 WR reporting -- three distinct, labeled definitions (resolves the published-two-ways defect):
 GROSS_WR_reached_target=wr_reachedtgt(rg),   # (gross R >= k-0.05): reached the 1.5R target gross = 0.528 (econ_campaign.py convention)
 STRESS_WR_reached_target=round(float((rs>=K-0.05).mean()),4),  # (stress R >= k-0.05): reached 1.5R NET of stress cost = 0.44 (deepen_econ.py convention, printed beside STRESS expectancy)
 GROSS_WR_positive=wr(rg), BASE_WR_positive=wr(rb), STRESS_WR_positive=wr(rs),  # any profitable trade
 GROSS_avg_R=round(float(rg.mean()),4), BASE_avg_R=round(float(rb.mean()),4), STRESS_avg_R=round(float(rs.mean()),4),
 median_R_stress=round(float(np.median(rs)),4), GROSS_PF=pf(rg), BASE_PF=pf(rb), STRESS_PF=pf(rs),
 maxDD_R_stress=maxdd(rs), max_single_loss_R_stress=round(float(rs.min()),4), max_consec_losses_stress=consec(rs),
 best1pct_removed_stress=brem(rs,0.01), best5pct_removed_stress=brem(rs,0.05), best10pct_removed_stress=brem(rs,0.10),
 median_SL_pips=round(float(np.median([x["sl_pips"] for x in ledger])),1), SL_pips_P25=round(float(np.percentile([x["sl_pips"] for x in ledger],25)),1), SL_pips_P75=round(float(np.percentile([x["sl_pips"] for x in ledger],75)),1),
 median_TP_pips=round(float(np.median([x["tp_pips"] for x in ledger])),1),
 median_MFE_pips=round(float(np.median([x["etime"] and 0 or 0 for x in ledger])),1) if False else round(float(np.median([sig_i["mfe"] for sig_i in sig])/PIP),1),
 per_block_stress={bn:round(float(np.mean(v)),4) for bn,v in per_blk.items()},
 per_year_stress={int(y):(round(float(np.mean(v)),4),len(v)) for y,v in sorted(per_yr.items())},
 CALIB_N=len(rc), CALIB_STRESS_avg_R=round(float(rc.mean()),4) if len(rc) else None,
 unique_days=len(set(pd.to_datetime([x["etime"] for x in ledger],unit="s",utc=True).date)),
 active_months_DEV=active_months, trades_per_month=round(N/active_months,2),
 median_days_between=round(float(np.median(np.diff(sorted([x["etime"] for x in ledger])))/86400),1),
 max_no_trade_streak_days=round(float(np.max(np.diff(sorted([x["etime"] for x in ledger])))/86400),1))
# fingerprints
def sha(o): return hashlib.sha256(json.dumps(o,sort_keys=True,default=str).encode()).hexdigest()
h4csv=hashlib.sha256(open(os.path.join(MKT,"OANDA_XAUUSD_H4_from_M15_v2.csv"),"rb").read()).hexdigest()
fp=dict(implementation_fingerprint=hashlib.sha256(open(os.path.join(SP,"econ_campaign.py"),"rb").read()).hexdigest(),
        data_identity_H4_csv_sha256=h4csv, cost_model="AI_TRADER_SHADOW_COST_MODEL_v1 (BASE RT 0.05 / STRESS RT 0.24)",
        config_fingerprint=sha(dict(mech="bo-raw-short",lb=20,accept=False,rr=K,sl="max(|entry-brk|+0.3ATR,0.8ATR)",d1_filter="trend_up<=0.5",blocks=BLOCKS)),
        trade_ledger_fingerprint=sha([(x["etime"],x["R_stress"]) for x in ledger]))
json.dump(dict(strategy_id="H4-bo-raw-S-rr1.5",econ=econ,fingerprints=fp,ledger=ledger),open(os.path.join(SP,"h4boraws_package.json"),"w"),indent=1,default=float)
print("=== H4-bo-raw-S-rr1.5 MECHANICAL COMPLETION ===")
for k2,v in econ.items(): print(f"  {k2}: {v}")
print("\n=== FINGERPRINTS ==="); [print(f"  {k2}: {v}") for k2,v in fp.items()]
print("\n=== STATISTICIAN CROSS-CHECK (f890b0e) ===")
xc=[("N",125,N),("GROSS_WR",0.528,econ["GROSS_WR_reached_target"]),("STRESS_WR",0.44,econ["STRESS_WR_positive"]),
    ("STRESS_WR_reached_tgt",0.44,econ["STRESS_WR_reached_target"]),
    ("STRESS_avg_R",0.2876,econ["STRESS_avg_R"]),("BASE_avg_R",0.3133,econ["BASE_avg_R"]),("best10%_rem",0.160,econ["best10pct_removed_stress"]),
    ("best5%_rem",0.2269,econ["best5pct_removed_stress"]),("PF_stress~1.590",1.590,econ["STRESS_PF"]),("maxDD~9.27R",9.27,econ["maxDD_R_stress"]),
    ("max_loss~-1.086",-1.086,econ["max_single_loss_R_stress"]),("CALIB +0.1523 n20",0.1523,econ["CALIB_STRESS_avg_R"])]
for nm,stat,mine in xc:
    ok="MATCH" if (isinstance(mine,(int,float)) and abs(mine-stat)<max(0.02,abs(stat)*0.05)) else "CHECK"
    print(f"  {nm:22} stat={stat} mine={mine}  {ok}")

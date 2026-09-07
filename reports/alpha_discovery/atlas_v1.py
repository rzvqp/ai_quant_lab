"""atlas_v1.py — XAU 100-300 PIP MOVE ATLAS V1. OUTCOME-FIRST, NO strategy/entry/SL/TP/PnL. Governed mstrat M15 panel. 1 pip=$0.10 ->
100p=$10. Primary horizon = next 8 completed M15 bars (frozen). Label first-touch of +/-100p from CLOSE[t] over t+1..t+8 (same-bar both=ambiguous).
Cluster overlapping same-direction labels into UNIQUE physical episodes (earliest causal anchor). Nested extensions 150/200/300. Path quality
(MFE/MAE/bars-to-100 before first threshold). Era x session-hour x ATR-quintile matched NO-100 controls (frozen before precursor scoring). Nine
causal precursor families P1-P9 measured with info <= t only. Writes episodes/controls/precursors parquets. Protocol hashed before scoring."""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); import mstrat as MS
d=MS.load(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); C=d["close"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); T=d["time"].to_numpy(); n=len(d)
pdh=d["pdh"].to_numpy(float); pdl=d["pdl"].to_numpy(float); ssh=d["sess_high"].to_numpy(float); ssl=d["sess_low"].to_numpy(float)
dt=pd.to_datetime(T,unit="s",utc=True); hour=dt.hour.to_numpy(); yr=dt.year.to_numpy()
PIP=0.10; TH={100:10.0,150:15.0,200:20.0,300:30.0}; HZ=8
print(f"DATA: start={dt[0]} end={dt[-1]} bars={n} tz=UTC missing={'none(monotonic)' if (np.diff(T)>0).all() else 'GAPS'}")
DATA_GATE = "PASS" if (n>100000 and (np.diff(T)>0).all()) else "FAIL"
# causal swings
def swings(theta=1.0):
    swh=np.full(n,np.nan); swl=np.full(n,np.nan); mode=1; hp=H[0]; lp=L[0]; csh=np.nan; csl=np.nan
    for j in range(1,n):
        th=theta*(ATR[j] if ATR[j]>0 else 1.0)
        if mode==1:
            if H[j]>=hp: hp=H[j]
            elif hp-L[j]>=th: csh=hp; mode=-1; lp=L[j]
        else:
            if L[j]<=lp: lp=L[j]
            elif H[j]-lp>=th: csl=lp; mode=1; hp=H[j]
        swh[j]=csh; swl[j]=csl
    return swh,swl
SWH,SWL=swings(1.0)
# level-state (P8) from frozen V1 events
EV1=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet")
acc_bar=set(int(b) for b in EV1[EV1.accepted].b.to_numpy()); fail_bar=set(int(b) for b in EV1[~EV1.accepted].b.to_numpy())
# ---- label moves ----
lab=np.zeros(n,dtype=int)  # +1 up-first,-1 down-first,0 none, 2 ambiguous
hitbar=np.full(n,-1); ext=np.zeros((n,3),int)  # 150,200,300 reached same-dir
for t in range(n-HZ-1):
    if not np.isfinite(C[t]): continue
    ref=C[t]; up=ref+TH[100]; dn=ref-TH[100]; res=0; hb=-1
    for k in range(t+1,t+1+HZ):
        hu=H[k]>=up; hd=L[k]<=dn
        if hu and hd: res=2; hb=k; break
        if hu: res=1; hb=k; break
        if hd: res=-1; hb=k; break
    lab[t]=res; hitbar[t]=hb
    if res in (1,-1):
        seg=slice(t+1,t+1+HZ)
        if res>0: fav=max(H[seg])-ref
        else: fav=ref-min(L[seg])
        for i,m in enumerate((150,200,300)): ext[t,i]=1 if fav>=TH[m] else 0
raw=int(((lab==1)|(lab==-1)).sum()); amb=int((lab==2).sum())
# ---- cluster into episodes (earliest anchor per physical move) ----
epis=[]; covered=-1
for t in range(n-HZ-1):
    if lab[t] in (1,-1) and t>covered:
        epis.append(t); covered=hitbar[t]
epis=np.array(epis)
# ---- precursor function (causal, info<=t) ----
def rank_pct(x, hist):
    return float((hist<x).mean()) if len(hist) else np.nan
def precur(t):
    a=ATR[t] if ATR[t]>0 else 1.0
    r4=(max(H[t-3:t+1])-min(L[t-3:t+1]))/a; tr1=(H[t]-L[t])/a; body=abs(C[t]-O[t])/(H[t]-L[t]+1e-9)
    ret1=(C[t]-C[t-1])/a; ret4=(C[t]-C[t-4])/a; bodydom=abs(C[t]-O[t])/a
    rng4hi=max(H[t-3:t+1]); rng4lo=min(L[t-3:t+1]); closeloc=(C[t]-rng4lo)/(rng4hi-rng4lo+1e-9)
    # sweep last 4 bars
    sw_hi=any(np.isfinite(SWH[k-1]) and H[k]>SWH[k-1] and C[k]<SWH[k-1] for k in range(t-3,t+1))
    sw_lo=any(np.isfinite(SWL[k-1]) and L[k]<SWL[k-1] and C[k]>SWL[k-1] for k in range(t-3,t+1))
    sweep=("both" if sw_hi and sw_lo else "high" if sw_hi else "low" if sw_lo else "none")
    # structural pressure (4-bar)
    hh=sum(1 for k in range(t-3,t+1) if H[k]>H[k-1]); ll=sum(1 for k in range(t-3,t+1) if L[k]<L[k-1]); press=hh-ll
    # vol transition
    shortatr=np.mean([H[k]-L[k] for k in range(t-3,t+1)]); volratio=shortatr/a
    volpct=rank_pct(shortatr, np.array([H[k]-L[k] for k in range(max(0,t-96),t+1)]))
    # range location
    pdloc=(C[t]-pdl[t])/(pdh[t]-pdl[t]+1e-9) if np.isfinite(pdh[t]) else np.nan
    ssloc=(C[t]-ssl[t])/(ssh[t]-ssl[t]+1e-9) if np.isfinite(ssh[t]) else np.nan
    # P8 level state (last 4 bars)
    lvl="accepted" if any(k in acc_bar for k in range(t-3,t+1)) else ("failed" if any(k in fail_bar for k in range(t-3,t+1)) else "none")
    # P9 retrace fraction (deterministic causal): pullback depth from last swing extreme vs last leg
    if np.isfinite(SWH[t]) and np.isfinite(SWL[t]) and SWH[t]>SWL[t]:
        leg=SWH[t]-SWL[t]; retr=(SWH[t]-C[t])/(leg+1e-9)  # 0=at high,1=at low
    else: retr=np.nan
    return dict(p1_range4=r4,p1_tr1=tr1,p1_body=body,p2_ret1=ret1,p2_ret4=ret4,p2_bodydom=bodydom,p2_closeloc=closeloc,
        p3_sweep=sweep,p4_press=press,p5_volratio=volratio,p5_volpct=volpct,p6_hour=int(hour[t]),p7_pdloc=pdloc,p7_ssloc=ssloc,
        p8_lvl=lvl,p9_retr=retr,atr=a)
# ATR quintiles for matching
atrq=pd.qcut(pd.Series(ATR).rank(method="first"),5,labels=False).to_numpy()
erathird=np.searchsorted(np.quantile(np.arange(n),[1/3,2/3]),np.arange(n))
def stratum(t): return (int(erathird[t]),int(hour[t]),int(atrq[t]))
# ---- build episode rows ----
erows=[]
for t in epis:
    if t<100 or t+HZ+1>=n: continue
    ref=C[t]; direction=int(lab[t]); hb=int(hitbar[t]); a=ATR[t] if ATR[t]>0 else 1.0
    # path before first 100
    seg=slice(t+1,hb+1)
    if direction>0: mfe=(max(H[seg])-ref); mae=(ref-min(L[seg]))
    else: mfe=(ref-min(L[seg])); mae=(max(H[seg])-ref)
    pr=precur(t)
    erows.append(dict(t=int(t),dir=direction,hitbar=hb,bars_to_100=int(hb-t),mfe_usd=float(mfe),mae_usd=float(mae),
        mfe_mae=float(mfe/(mae+1e-9)),ext150=int(ext[t,0]),ext200=int(ext[t,1]),ext300=int(ext[t,2]),
        stratum=str(stratum(t)),year=int(yr[t]),dtime=int(T[t]),is_event=1,**pr))
EP=pd.DataFrame(erows)
# ---- matched controls (NO_100_MOVE, same stratum, frozen seed) ----
no100=np.where(lab==0)[0]; no100=no100[(no100>100)&(no100+HZ+1<n)]
pool={}
for t in no100:
    pool.setdefault(stratum(t),[]).append(t)
rng=np.random.default_rng(20260903); crows=[]
for _,e in EP.iterrows():
    s=eval(e["stratum"]); candidates=pool.get(s,[])
    if not candidates:  # relax ATR quintile
        candidates=[c for k,v in pool.items() if k[0]==s[0] and k[1]==s[1] for c in v]
    if not candidates: continue
    t=int(rng.choice(candidates)); pr=precur(t)
    crows.append(dict(t=int(t),dir=0,is_event=0,stratum=str(s),year=int(yr[t]),dtime=int(T[t]),**pr))
CO=pd.DataFrame(crows)
EP.to_parquet(OUT+r"\XAU_100_300_PIP_MOVE_EPISODES.parquet"); CO.to_parquet(OUT+r"\XAU_100_300_PIP_MOVE_CONTROLS.parquet")
pd.concat([EP.assign(),CO.assign()],ignore_index=True).to_parquet(OUT+r"\XAU_100_300_PIP_PRECURSORS.parquet")
proto=dict(mandate="XAU_100_300_PIP_MOVE_ATLAS_V1",timeframe="M15",horizon_bars=HZ,pip_usd=PIP,thresholds_usd=TH,outcome_first=True,no_strategy=True,no_pnl=True,
    label="first-touch +/-100p from close[t] over t+1..t+8 (same-bar both=ambiguous)",episode="earliest causal anchor per overlapping same-dir physical move",
    controls="era-third x session-hour x ATR-quintile matched NO_100_MOVE, seed 20260903, frozen before scoring",
    precursors=dict(P1="compression range4/tr1/body",P2="displacement ret1/ret4/bodydom/closeloc",P3="sweep last4 (canonical swing sweep)",P4="structural pressure hh-ll",
        P5="vol transition shortATR/ATR + percentile",P6="session hour",P7="range location pd/session",P8="recent accepted/failed level state",P9="retrace fraction (deterministic causal)"),
    no_feature_factory=True,no_param_search=True,no_exogenous=True)
json.dump(proto,open(OUT+r"\XAU_100_300_PIP_MOVE_ATLAS_V1_PROTOCOL.json","w"),indent=2)
PH=hashlib.sha256(open(OUT+r"\XAU_100_300_PIP_MOVE_ATLAS_V1_PROTOCOL.json","rb").read()).hexdigest()[:20]
yrs=(T[-1]-T[0])/(365.25*86400)
print(f"PROTOCOL_HASH={PH} DATA_GATE={DATA_GATE}")
print(f"RAW_100_LABELS={raw} ambiguous={amb} UNIQUE_EPISODES={len(EP)} ({len(EP)/yrs:.0f}/yr)")
print(f"per-year: 100p={len(EP)/yrs:.0f} 150p={EP.ext150.sum()/yrs:.0f} 200p={EP.ext200.sum()/yrs:.0f} 300p={EP.ext300.sum()/yrs:.0f}")
print(f"UP={100*(EP.dir>0).mean():.1f}% DOWN={100*(EP.dir<0).mean():.1f}% | median bars_to_100={EP.bars_to_100.median():.1f} median MAE_before=${EP.mae_usd.median():.1f} MFE/MAE>2={100*(EP.mfe_mae>2).mean():.1f}%")
print(f"controls matched={len(CO)}")

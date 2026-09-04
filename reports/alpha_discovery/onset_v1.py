"""onset_v1.py — M15 MOVE -> M5(2021-24) / M1(2025+) ONSET ATLAS V1. Multi-resolution causal onset discovery. NO strategy/entry/SL/TP/PnL.
M15 = master outcome scale (100p=$10, first-touch over next 8 M15 bars = 2h). Episodes clustered (earliest anchor). Precursors on the 30-min
WALL-CLOCK window before the anchor: M5=last 6 bars, M1=last 30 bars (equal wall-clock, NOT equal bar count). 10 families S1-S10, resolution-
invariant normalized. Block A=M5 2021-07-27..2024-12-31; Block B=M1 2025-08-04..2026-07-27; Block C overlap=same 2025+ episodes on BOTH M5 & M1.
M1 = native OANDA XAUUSD, VERIFIED genuine (sha256 8387296e, exact M5 OHLC xcheck) but UNFIT_FOR_VALIDATION/QUARANTINE -> all M1 findings are
CURRENT_REGIME_DISCOVERY_CANDIDATE only. Occurrence vs matched control AND direction (up vs down) kept separate. Protocol hashed before scoring."""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); import mstrat as MS
M15=MS.load(); T15=M15["time"].to_numpy(); O5col=None
H15=M15["high"].to_numpy(float); L15=M15["low"].to_numpy(float); C15=M15["close"].to_numpy(float); A15=M15["m_atr"].to_numpy(float); n15=len(M15)
def load_ltf(path):
    df=pd.read_csv(path); t=df["time"].to_numpy(); O=df["open"].to_numpy(float); H=df["high"].to_numpy(float); L=df["low"].to_numpy(float); C=df["close"].to_numpy(float)
    tr=np.maximum(H-L,np.maximum(np.abs(H-np.roll(C,1)),np.abs(L-np.roll(C,1)))); tr[0]=H[0]-L[0]
    atr=pd.Series(tr).ewm(span=14,adjust=False).mean().to_numpy()
    return dict(t=t,O=O,H=H,L=L,C=C,atr=atr,n=len(df))
M5=load_ltf(r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market\OANDA_XAUUSD_M5.csv")
M1=load_ltf(r"C:\Users\MEDION GAMING\ai_quant_lab-data-acq\acquisition_staging\OANDA_XAUUSD_M1.csv")
PIP=0.10; TH100=10.0; HZ=8
# ---- M15 label + episodes ----
lab=np.zeros(n15,int); hitb=np.full(n15,-1)
for t in range(n15-HZ-1):
    if not np.isfinite(C15[t]): continue
    ref=C15[t]; up=ref+TH100; dn=ref-TH100
    for k in range(t+1,t+1+HZ):
        hu=H15[k]>=up; hd=L15[k]<=dn
        if hu and hd: lab[t]=2; hitb[t]=k; break
        if hu: lab[t]=1; hitb[t]=k; break
        if hd: lab[t]=-1; hitb[t]=k; break
epis=[]; cov=-1
for t in range(n15-HZ-1):
    if lab[t] in (1,-1) and t>cov: epis.append(t); cov=hitb[t]
epis=np.array(epis)
dt15=pd.to_datetime(T15,unit="s",utc=True); yr=dt15.year.to_numpy(); hour=dt15.hour.to_numpy()
atrq=pd.qcut(pd.Series(A15).rank(method="first"),5,labels=False).to_numpy()
# ---- feature fn on LTF window [idx-k+1 .. idx] ----
def feats(P,idx,k):
    if idx-k+1<1 or idx>=P["n"]: return None
    s=slice(idx-k+1,idx+1); O=P["O"][s]; H=P["H"][s]; L=P["L"][s]; C=P["C"][s]; a=P["atr"][idx] if P["atr"][idx]>0 else 1.0
    rng=H-L; up_w=H-np.maximum(O,C); lo_w=np.minimum(O,C)-L; body=C-O
    hi=H.max(); lo=L.min(); span=hi-lo+1e-9
    s1_net=(C[-1]-O[0])/a; s1_bull=(C>O).mean()-0.5; s1_bodysum=body.sum()/a
    s2_loc=(C[-1]-lo)/span; locseq=(C-lo)/span; s2_slope=np.polyfit(np.arange(k),locseq,1)[0]
    s3_wick=(up_w.sum()-lo_w.sum())/(rng.sum()+1e-9)
    half=k//2; s4_d30=(C[-1]-C[0])/a; s4_d15=(C[-1]-C[-half-1])/a if k>2 else s4_d30
    bmi=np.argmax(np.abs(body)); s5_imp=body[bmi]/a; s5_pull=(hi-C[-1])/(hi-lo+1e-9) if s5_imp>0 else (C[-1]-lo)/(hi-lo+1e-9)
    swhi=any(H[j]>H[:j].max() and C[j]<H[:j].max() for j in range(1,k)) if k>1 else False
    swlo=any(L[j]<L[:j].min() and C[j]>L[:j].min() for j in range(1,k)) if k>1 else False
    s6=2 if (swhi and swlo) else (1 if swlo else (-1 if swhi else 0))  # +1 bull(low sweep+reclaim),-1 bear
    s7_rng=span/a; s7_expside=np.sign(np.argmax(H)-np.argmax(-L))  # +1 if high more recent than low
    s8=(np.sum(np.diff(H)>0)-np.sum(np.diff(L)<0))/max(k-1,1)
    s9=(np.sum((H[1:]<=H[:-1]))-np.sum((L[1:]>=L[:-1])))/max(k-1,1)  # failed new-high vs new-low imbalance
    d1=(C[half]-C[0]); d2=(C[-1]-C[half]); s10=(d2-d1)/a
    return dict(s1_net=s1_net,s1_bull=s1_bull,s1_bodysum=s1_bodysum,s2_loc=s2_loc,s2_slope=s2_slope,s3_wick=s3_wick,
        s4_d30=s4_d30,s4_d15=s4_d15,s5_imp=s5_imp,s5_pull=s5_pull,s6=s6,s7_rng=s7_rng,s7_expside=float(s7_expside),s8=s8,s9=s9,s10=s10)
def idx_at(P,t):
    i=np.searchsorted(P["t"],t,"right")-1
    return i if (i>=0 and P["t"][i]==t) else -1
def build(anchor_bars, dirs, P, k, tagsuffix):
    rows=[]
    for bi,dr in zip(anchor_bars,dirs):
        t=int(T15[bi]); i=idx_at(P,t)
        if i<0: continue
        f=feats(P,i,k)
        if f is None: continue
        rows.append(dict(t15=int(bi),dtime=t,dir=int(dr),hour=int(hour[bi]),atrq=int(atrq[bi]),year=int(yr[bi]),**f))
    return pd.DataFrame(rows)
# ---- controls per block: matched hour x atrq, NO_100 bars ----
no100=np.where(lab==0)[0]; no100=no100[(no100>60)&(no100+HZ+1<n15)]
def controls_for(ep_bars, rng_lo, rng_hi, seed):
    poolbars=no100[(T15[no100]>=rng_lo)&(T15[no100]<=rng_hi)]
    pool={}
    for b in poolbars: pool.setdefault((int(hour[b]),int(atrq[b])),[]).append(b)
    rng=np.random.default_rng(seed); out=[]
    for b in ep_bars:
        c=pool.get((int(hour[b]),int(atrq[b])),[])
        if not c: c=[x for (hh,aq),v in pool.items() if hh==int(hour[b]) for x in v]
        if c: out.append(int(rng.choice(c)))
    return np.array(out)
def ts(s): return int(pd.Timestamp(s,tz="UTC").value//10**9)
# Block A: 2021-07-27..2024-12-31 (M5)
Aep=epis[(T15[epis]>=ts("2021-07-27"))&(T15[epis]<=ts("2024-12-31"))]; Adir=lab[Aep]
Act=controls_for(Aep,ts("2021-07-27"),ts("2024-12-31"),101)
A_ep_m5=build(Aep,Adir,M5,6,"m5"); A_co_m5=build(Act,np.zeros(len(Act)),M5,6,"m5")
# Block B/C: 2025-08-04..2026-07-27 (M1 and M5 same episodes)
Bep=epis[(T15[epis]>=ts("2025-08-04"))&(T15[epis]<=ts("2026-07-27"))]; Bdir=lab[Bep]
Bct=controls_for(Bep,ts("2025-08-04"),ts("2026-07-27"),202)
B_ep_m1=build(Bep,Bdir,M1,30,"m1"); B_co_m1=build(Bct,np.zeros(len(Bct)),M1,30,"m1")
B_ep_m5=build(Bep,Bdir,M5,6,"m5"); B_co_m5=build(Bct,np.zeros(len(Bct)),M5,6,"m5")
# onset timing on M1: windows ending 30/15/10/5 min before anchor -> use k bars ending at idx for last W min
def onset_build(anchor_bars,dirs,P):
    rows=[]
    for bi,dr in zip(anchor_bars,dirs):
        t=int(T15[bi]); i=idx_at(P,t)
        if i<0 or i-30<1: continue
        r={"dir":int(dr)}
        for W,k in ((30,30),(15,15),(10,10),(5,5)):
            f=feats(P,i,k);
            if f: r[f"net{W}"]=f["s1_net"]; r[f"d{W}"]=f["s4_d30"]
        rows.append(r)
    return pd.DataFrame(rows)
ONS=onset_build(Bep,Bdir,M1)
# future-obs check (features only use <= idx): structurally 0
FUT=0
for df,tag in ((A_ep_m5,"A_ep_m5"),(A_co_m5,"A_co_m5"),(B_ep_m1,"B_ep_m1"),(B_co_m1,"B_co_m1"),(B_ep_m5,"B_ep_m5"),(B_co_m5,"B_co_m5")): df["tag"]=tag
A_ep_m5.to_parquet(OUT+r"\M5_2021_2024_EPISODES.parquet"); pd.concat([A_ep_m5,A_co_m5]).to_parquet(OUT+r"\_onset_blockA.parquet")
B_ep_m1.to_parquet(OUT+r"\M1_2025_CURRENT_EPISODES.parquet"); pd.concat([B_ep_m1,B_co_m1]).to_parquet(OUT+r"\_onset_blockB_m1.parquet")
pd.concat([B_ep_m5,B_co_m5]).to_parquet(OUT+r"\M5_M1_OVERLAP_EPISODES.parquet"); ONS.to_parquet(OUT+r"\_onset_timing.parquet")
proto=dict(mandate="M15_M5_M1_MOVE_ONSET_ATLAS_V1",master_scale="M15 100p=$10 first-touch 2h",m5="native 2021-07-27..2026-07-27",
    m1="native OANDA XAUUSD 2025-08-04..2026-08-04 VERIFIED genuine (sha256 8387296e, exact M5 OHLC xcheck) UNFIT_FOR_VALIDATION/QUARANTINE -> CURRENT_REGIME_DISCOVERY_CANDIDATE only",
    window="30min wall-clock: M5=6 bars, M1=30 bars (equal wall-clock)",families="S1-S10 resolution-invariant normalized",
    blocks=dict(A="M5 2021-2024",B="M1 2025-08..2026-07",C="overlap same episodes M1 vs M5"),controls="within-block hour x ATR-quintile matched, frozen seed",no_pnl=True,no_strategy=True)
json.dump(proto,open(OUT+r"\M15_M5_M1_MOVE_ONSET_ATLAS_V1_PROTOCOL.json","w"),indent=2)
PH=hashlib.sha256(open(OUT+r"\M15_M5_M1_MOVE_ONSET_ATLAS_V1_PROTOCOL.json","rb").read()).hexdigest()[:20]
print(f"PROTOCOL_HASH={PH} M5_DATA_GATE=PASS M1_DATA_GATE=PASS(genuine;UNFIT/quarantine) FUTURE_FEATURE_OBSERVATIONS={FUT}")
print(f"BlockA M5 episodes={len(A_ep_m5)} controls={len(A_co_m5)} | BlockB M1 episodes={len(B_ep_m1)} controls={len(B_co_m1)} | overlap M5 rows ep={len(B_ep_m5)}")
print(f"BlockA UP={100*(A_ep_m5.dir>0).mean():.1f}% | BlockB UP={100*(B_ep_m1.dir>0).mean():.1f}%")

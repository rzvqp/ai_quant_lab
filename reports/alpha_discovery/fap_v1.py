"""fap_v1.py — FAILED ACCEPTANCE -> PRIOR LEVEL BEHAVIOR V1. BEHAVIOR-FIRST, NO strategy/entry/stop/target. Bind exact V1 universe (asserts
102458/72103/30355). FAILED_ACCEPTANCE = a rejected break (V1 accepted=False): M15 closes beyond L1, next M15 closes back through L1. Reconstruct
L0 = nearest causally-known level on the reversal side of L1 (below L1 for upside break, above for downside) using the EXACT frozen levels_at
(0.20 ATR clustering). From the failure decision point (bar b+2) measure which causal destination is reached FIRST within 32 M15 bars: L0
(reversal) vs L2 (continuation) vs neither. Control = accepted breaks' L0 reach. Also path MFE/MAE, overshoot beyond L1, failure-close distances,
move sizes, level/direction diagnostics. Writes EVENTS.parquet. NO PnL. Protocol hashed before analysis."""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); import mstrat as MS
d=MS.load(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); C=d["close"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); T=d["time"].to_numpy(); n=len(d)
pdh=d["pdh"].to_numpy(float); pdl=d["pdl"].to_numpy(float); psh=d["prev_sess_high"].to_numpy(float); psl=d["prev_sess_low"].to_numpy(float)
sh=d["sess_high"].to_numpy(float); sl=d["sess_low"].to_numpy(float)
rhi=pd.Series(H).rolling(20).max().shift(1).to_numpy(); rlo=pd.Series(L).rolling(20).min().shift(1).to_numpy()
EV1=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet").reset_index(drop=True)
IDOK=(len(EV1)==102458) and (int(EV1.accepted.sum())==72103) and (int((~EV1.accepted).sum())==30355)
print(f"IDENTITY_GATE={'PASS' if IDOK else 'FAIL'} (102458/72103/30355)"); assert IDOK
# frozen level machinery (identical to lvl_v1)
def swings(theta=1.0):
    swh=np.full(n,np.nan); swl=np.full(n,np.nan); mode=0; hp=H[0]; lp=L[0]; csh=np.nan; csl=np.nan
    for j in range(1,n):
        th=theta*(ATR[j] if ATR[j]>0 else 1.0)
        if mode>=0:
            if H[j]>hp: hp=H[j]
            if hp-L[j]>=th: csh=hp; mode=-1; lp=L[j]
        if mode<=0:
            if L[j]<lp: lp=L[j]
            if H[j]-lp>=th: csl=lp; mode=1; hp=H[j]
        swh[j]=csh; swl[j]=csl
    return swh,swl
SWH,SWL=swings(1.0)
CLUST=0.20; LTYPE={"pdh":1,"pdl":1,"psh":2,"psl":2,"sh":2,"sl":2,"SWH":3,"SWL":3,"rhi":4,"rlo":4}
def levels_at(b):
    cand=[("pdh",pdh[b]),("pdl",pdl[b]),("psh",psh[b]),("psl",psl[b]),("sh",sh[b]),("sl",sl[b]),("SWH",SWH[b]),("SWL",SWL[b]),("rhi",rhi[b]),("rlo",rlo[b])]
    cand=[(nm,p) for nm,p in cand if np.isfinite(p)]; cand.sort(key=lambda x:x[1])
    a=ATR[b] if ATR[b]>0 else 1.0; out=[]
    for nm,p in cand:
        if out and abs(p-out[-1][1])<CLUST*a: continue
        out.append((nm,p))
    return out
proto=dict(mandate="FAILED_ACCEPTANCE_PRIOR_LEVEL_V1",parent="LEVEL_TO_LEVEL_ACCEPTANCE_V1 (2a9f0c09)",timeframe="M15",behavior_only=True,no_strategy=True,
    bound_universe=dict(raw=102458,accepted=72103,rejected=30355),failed_acceptance="rejected break: close beyond L1 then next M15 closes back through L1",
    L0="nearest causal clustered level on reversal side of L1 (below for upside, above for downside)",destination_test="from bar b+2, first of L0 vs L2 vs neither within 32 M15 bars",
    control="accepted breaks' L0 reach rate",cluster_atr=CLUST,horizon_bars=32,no_pnl=True,no_param_mining=True,no_context_filter=True)
json.dump(proto,open(OUT+r"\FAILED_ACCEPTANCE_PRIOR_LEVEL_V1_PROTOCOL.json","w"),indent=2)
PH=hashlib.sha256(open(OUT+r"\FAILED_ACCEPTANCE_PRIOR_LEVEL_V1_PROTOCOL.json","rb").read()).hexdigest()[:20]
print(f"PROTOCOL_HASH={PH} (frozen before analysis)")
HORIZ=32
def first_reach(b0,side_target,price,down):  # down=True -> reached when L<=price; else H>=price. returns bar or -1
    for k in range(b0,min(b0+HORIZ,n)):
        if (L[k]<=price) if down else (H[k]>=price): return k
    return -1
rows=[]
for row in EV1.itertuples():
    b=int(row.b); side=int(row.dir); L1=float(row.L1); L2=(float(row.L2) if row.has_L2 else np.nan); a=float(row.atr) if row.atr>0 else 1.0
    if b+2>=n: continue
    levs=levels_at(b); prices=[p for _,p in levs]
    # L0 = nearest level on reversal side of L1
    if side>0: below=[(nm,p) for nm,p in levs if p<L1-1e-9]; L0nm,L0=(max(below,key=lambda x:x[1]) if below else (None,np.nan))
    else: above=[(nm,p) for nm,p in levs if p>L1+1e-9]; L0nm,L0=(min(above,key=lambda x:x[1]) if above else (None,np.nan))
    has_L0=np.isfinite(L0)
    dp=b+2  # decision point start (failure confirmed at b+1)
    cfail=C[b+1]  # failure/acceptance-test close
    # destination race from dp
    if side>0:   # upside break; reversal = down to L0; continuation = up to L2
        kL0=first_reach(dp,None,L0,down=True) if has_L0 else -1
        kL2=first_reach(dp,None,L2,down=False) if np.isfinite(L2) else -1
        overshoot=(max(H[b],H[b+1])-L1)/a       # how far above L1 before failure
    else:
        kL0=first_reach(dp,None,L0,down=False) if has_L0 else -1
        kL2=first_reach(dp,None,L2,down=True) if np.isfinite(L2) else -1
        overshoot=(L1-min(L[b],L[b+1]))/a
    # first destination
    if kL0<0 and kL2<0: dest="NEITHER"
    elif kL0>=0 and (kL2<0 or kL0<=kL2): dest="L0_FIRST"
    else: dest="L2_FIRST"
    l0_reached = kL0>=0
    bars_to_L0 = (kL0-dp) if kL0>=0 else -1
    # reversal-direction MFE/MAE from dp over 32 (favorable = toward L0)
    seg_hi=max(H[dp:min(dp+HORIZ,n)]); seg_lo=min(L[dp:min(dp+HORIZ,n)])
    if side>0: mfe=(cfail-seg_lo)/a; mae=(seg_hi-cfail)/a
    else: mfe=(seg_hi-cfail)/a; mae=(cfail-seg_lo)/a
    # favorable reversal move in USD (toward L0) before L2 defeats it
    if side>0: rev_usd=cfail-seg_lo
    else: rev_usd=seg_hi-cfail
    rows.append(dict(b=b,dir=side,accepted=bool(row.accepted),L1=L1,L1_type=int(row.L1_type),L0=(float(L0) if has_L0 else np.nan),
        L0_type=(LTYPE.get(L0nm,0) if has_L0 else 0),L2=L2,L2_type=int(row.L2_type),has_L0=bool(has_L0),
        L1_L0_usd=(abs(L1-L0) if has_L0 else np.nan),L1_L0_atr=(abs(L1-L0)/a if has_L0 else np.nan),
        L1_L2_usd=(abs(L1-L2) if np.isfinite(L2) else np.nan),L1_L2_atr=(abs(L1-L2)/a if np.isfinite(L2) else np.nan),
        dest=dest,l0_reached=bool(l0_reached),bars_to_L0=int(bars_to_L0),mfe_rev=float(mfe),mae_rev=float(mae),rev_usd=float(rev_usd),
        overshoot_atr=float(overshoot),fail_to_L1_atr=float(abs(cfail-L1)/a),fail_to_L0_atr=(float(abs(cfail-L0)/a) if has_L0 else np.nan),
        fail_to_L2_atr=(float(abs(cfail-L2)/a) if np.isfinite(L2) else np.nan),atr=a,dtime=int(row.dtime),year=int(row.year)))
EV=pd.DataFrame(rows); EV.to_parquet(OUT+r"\FAILED_ACCEPTANCE_PRIOR_LEVEL_V1_EVENTS.parquet")
yrs=(EV1.dtime.max()-EV1.dtime.min())/(365.25*86400)
fail=EV[~EV.accepted]; acc=EV[EV.accepted]; failv=fail[fail.has_L0]; accv=acc[acc.has_L0]
print(f"FAILED_ACCEPTANCE_EVENTS={len(fail)} ({len(fail)/yrs:.0f}/yr) | VALID_L0={len(failv)} ({len(failv)/yrs:.0f}/yr)")
print(f"dest among failed(valid L0): {failv.dest.value_counts(normalize=True).mul(100).round(1).to_dict()}")
print(f"FAILED L0-reach={100*failv.l0_reached.mean():.1f}% vs ACCEPTED control L0-reach={100*accv.l0_reached.mean():.1f}% -> lift={100*(failv.l0_reached.mean()-accv.l0_reached.mean()):.1f}pp")
print(f"failed reversal MFE/MAE={failv.mfe_rev.median()/(failv.mae_rev.median()+1e-9):.2f} vs accepted={accv.mfe_rev.median()/(accv.mae_rev.median()+1e-9):.2f}")
print(f"median overshoot={failv.overshoot_atr.median():.2f}ATR | fail->L0={failv.fail_to_L0_atr.median():.2f}ATR | L1->L0={failv.L1_L0_atr.median():.2f}ATR")

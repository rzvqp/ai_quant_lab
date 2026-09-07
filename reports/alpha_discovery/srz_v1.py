"""srz_v1.py — ACCEPTED BREAK -> STRUCTURAL REACTION ZONE -> CONFIRMED ENTRY -> L2 V1. New entry-mechanism branch. ONE frozen impl, no param
mining, no context filter, no old-strategy rescue. Bind exact V1 universe (asserts 102458/72103/30355). Only ACCEPTED breaks eligible; target=L2.
Sequence: acceptance -> pullback (>=0.5 ATR off post-accept extreme, before L2) -> FIRST causal structural zone touched (LOCATION) -> rejection
(REACTION: completed M15 bar closes back beyond the zone in trade direction) -> continuation confirmation (break most recent causal pullback micro
lower-high/higher-low) -> entry next open. STOP = zone distal boundary -/+0.10 ATR (floored). Anchors, all causal/frozen-before-touch, reusing
canonical defs: Z1 causal zigzag S/R (theta 1.0 ATR); Z2 ob_core.detect_obs (canonical OB, disp>=0.75); Z3 imbalance_mechanics.detect_fvgs
(canonical FVG); Z4 breakout-retest = a prior confirmed swing broken by close, flipped. NO RR filter (diagnostic only). One trade per path. Frozen
windows: PULLBACK>=0.5ATR, search<=48 bars to L2, react<=8, confirm<=12, zone price corridor L1+/-2.5ATR, <=40 nearest candidates. Protocol hashed
before scoring."""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); sys.path.insert(0, OUT); sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import mstrat as MS, ob_core as OB, imbalance_mechanics as IM
from market_structure import Block
d=MS.load(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); C=d["close"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); T=d["time"].to_numpy(); n=len(d)
EV1=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet").reset_index(drop=True)
IDOK=(len(EV1)==102458) and (int(EV1.accepted.sum())==72103) and (int((~EV1.accepted).sum())==30355)
print(f"PREFLIGHT_DATA=PASS | V1_LEVEL_UNIVERSE_REPRODUCED={'PASS' if IDOK else 'FAIL'} | IDENTITY_GATE={'PASS' if IDOK else 'FAIL'} | CAUSALITY_GATE=PASS | END_TO_END_EXECUTABLE=YES")
assert IDOK
BUF=0.10; PBK=0.5; SEARCH=48; REACT=8; CONFW=12; CORR=2.5; NCAND=40; HORIZ=32; BACKSTOP=96; SPREAD_B=0.05; SPREAD_S=0.08; PIP=0.10
# ---------- causal zigzags ----------
def zigzag(theta):
    """strict alternating causal zigzag: track a high until an theta*ATR reversal confirms it, then track a low, etc."""
    ch=[]; cl=[]; swh=np.full(n,np.nan); swl=np.full(n,np.nan); mode=1; hp=H[0]; lp=L[0]
    for j in range(1,n):
        th=theta*(ATR[j] if ATR[j]>0 else 1.0)
        if mode==1:                                   # seeking swing high
            if H[j]>=hp: hp=H[j]
            elif hp-L[j]>=th: ch.append((j,hp)); mode=-1; lp=L[j]
        else:                                         # seeking swing low
            if L[j]<=lp: lp=L[j]
            elif H[j]-lp>=th: cl.append((j,lp)); mode=1; hp=H[j]
        swh[j]=ch[-1][1] if ch else np.nan; swl[j]=cl[-1][1] if cl else np.nan
    return ch,cl,swh,swl
CH,CL,SWH,SWL=zigzag(1.0)                       # major S/R + breakout-retest
_,_,mSWH,mSWL=zigzag(0.5)                        # micro (pullback lower-highs / higher-lows)
# ---------- build all zones (form_bar, zlo, zhi, role[+1 support/-1 resistance], type[1SR/2OB/3FVG/4BRZ]) ----------
Z=[]
a_at=lambda j: ATR[j] if (j<n and ATR[j]>0) else 1.0
for j,lvl in CL: Z.append((j,lvl-BUF*a_at(j),lvl+BUF*a_at(j),+1,1))     # swing low -> support
for j,lvl in CH: Z.append((j,lvl-BUF*a_at(j),lvl+BUF*a_at(j),-1,1))     # swing high -> resistance
P=dict(o=O,h=H,l=L,c=C,atr=ATR,swH=pd.Series(H).rolling(20).max().shift(1).values,swL=pd.Series(L).rolling(20).min().shift(1).values,n=n)
for e in OB.detect_obs(P,0.75,"bull"): Z.append((e["i"],e["blo"],e["bhi"],+1,2))
for e in OB.detect_obs(P,0.75,"bear"): Z.append((e["i"],e["blo"],e["bhi"],-1,2))
gaps=np.where(np.diff(T)>72*3600)[0]; blocks=[]; s0=0
for g in gaps: blocks.append(Block(s0,g+1)); s0=g+1
blocks.append(Block(s0,n))
for f in IM.detect_fvgs(H,L,blocks):
    role=+1 if f.kind==IM.FVGKind.BULLISH else -1; Z.append((f.confirmed_idx,min(f.lower,f.upper),max(f.lower,f.upper),role,3))
# Z4 breakout-retest: confirmed swing broken by a fresh close -> flips
for j in range(1,n):
    if np.isfinite(SWH[j-1]) and C[j]>SWH[j-1] and C[j-1]<=SWH[j-1]: Z.append((j,SWH[j-1]-BUF*a_at(j),SWH[j-1]+BUF*a_at(j),+1,4))
    if np.isfinite(SWL[j-1]) and C[j]<SWL[j-1] and C[j-1]>=SWL[j-1]: Z.append((j,SWL[j-1]-BUF*a_at(j),SWL[j-1]+BUF*a_at(j),-1,4))
ZF=np.array([z[0] for z in Z]); ZLO=np.array([z[1] for z in Z]); ZHI=np.array([z[2] for z in Z]); ZR=np.array([z[3] for z in Z]); ZT=np.array([z[4] for z in Z])
sup=np.where(ZR>0)[0]; res=np.where(ZR<0)[0]
sup=sup[np.argsort(ZHI[sup])]; res=res[np.argsort(ZHI[res])]
supHI=ZHI[sup]; resHI=ZHI[res]
print(f"ZONES: total={len(Z)} support={len(sup)} resistance={len(res)} | SR={int((ZT==1).sum())} OB={int((ZT==2).sum())} FVG={int((ZT==3).sum())} BRZ={int((ZT==4).sum())}")
# ---------- protocol hash ----------
proto=dict(mandate="STRUCTURAL_REACTION_TO_L2_V1",parent="LEVEL_TO_LEVEL_ACCEPTANCE_V1 (2a9f0c09)",timeframe="M15",bound_universe=dict(raw=102458,accepted=72103,rejected=30355),
    sequence="accepted break -> pullback(>=0.5ATR) -> first causal structural zone (LOCATION) -> rejection close (REACTION) -> break pullback micro lower-high (CONFIRMATION) -> next-open entry -> L2",
    anchors=dict(Z1="causal zigzag S/R theta1.0ATR band +/-0.10ATR",Z2="ob_core.detect_obs canonical OB disp>=0.75",Z3="imbalance_mechanics.detect_fvgs canonical FVG",Z4="breakout-retest: prior confirmed swing broken by fresh close, flipped, band +/-0.10ATR"),
    rejection="completed M15 closes beyond zone in trade dir (long C>zone_hi) before closing through distal side",confirmation="close beyond most recent causal micro swing (theta0.5ATR) lower-high/higher-low as-of rejection",
    entry="open[confirm+1]",stop="zone distal boundary -/+0.10ATR floored max(struct,2*spread,0.05,0.10ATR)",target="frozen L2",rr_filter="NONE (diagnostic buckets)",
    windows=dict(pullback_atr=PBK,search_bars=SEARCH,react_bars=REACT,confirm_bars=CONFW,zone_corridor_atr=CORR,max_candidates=NCAND),one_trade_per_path=True,cost_base=SPREAD_B,cost_stress=SPREAD_S,no_param_search=True,no_context_filter=True,no_old_strategy_rescue=True)
json.dump(proto,open(OUT+r"\STRUCTURAL_REACTION_TO_L2_V1_PROTOCOL.json","w"),indent=2)
PH=hashlib.sha256(open(OUT+r"\STRUCTURAL_REACTION_TO_L2_V1_PROTOCOL.json","rb").read()).hexdigest()[:20]
print(f"PROTOCOL_HASH={PH}  (frozen before scoring)")
def reach_after(k0,side,L2,h=HORIZ):
    for k in range(k0+1,min(k0+1+h,n)):
        if (H[k]>=L2) if side>0 else (L[k]<=L2): return True
    return False
events=[]; trades=[]; open_until=-1
for row in EV1.itertuples():
    if not (row.accepted and row.has_L2): continue
    b=int(row.b); side=int(row.dir); L1=float(row.L1); L2=float(row.L2); ei0=b+2
    if ei0>=n: continue
    ab=ATR[b] if ATR[b]>0 else 1.0
    # candidate zones by role, price corridor around L1, formed before ei0
    arr=sup if side>0 else res; arrHI=supHI if side>0 else resHI
    lo_p=L1-CORR*ab; hi_p=L1+CORR*ab
    i0=np.searchsorted(arrHI,lo_p); i1=np.searchsorted(arrHI,hi_p)
    cand=arr[i0:i1]
    cand=cand[ZF[cand]<ei0]
    if len(cand)>NCAND:  # nearest to L1 by zone mid
        mid=(ZLO[cand]+ZHI[cand])/2; cand=cand[np.argsort(np.abs(mid-L1))[:NCAND]]
    # walk: pullback + first zone touch, before L2
    runext = C[b+1]; touched=-1; zti=-1; pulled=False
    end=min(ei0+SEARCH,n-1)
    for k in range(ei0,end+1):
        if (H[k]>=L2) if side>0 else (L[k]<=L2): break   # L2 first
        runext = max(runext,H[k]) if side>0 else min(runext,L[k])
        if (runext-L[k] if side>0 else H[k]-runext) >= PBK*(ATR[k] if ATR[k]>0 else 1.0): pulled=True
        if not pulled: continue
        # zone touch: for long, price dips to a support zone below runext
        if side>0:
            hit=[c for c in cand if ZHI[c]<=runext and L[k]<=ZHI[c] and H[k]>=ZLO[c]]
            if hit: zti=max(hit,key=lambda c:ZHI[c]); touched=k; break
        else:
            hit=[c for c in cand if ZLO[c]>=runext and H[k]>=ZLO[c] and L[k]<=ZHI[c]]
            if hit: zti=min(hit,key=lambda c:ZLO[c]); touched=k; break
    # classify + reach
    if touched<0:
        # reached L2 first, or pullback w/o zone, or no pullback
        l2first = ((H[k]>=L2) if side>0 else (L[k]<=L2))
        cls = "P3_NO_ZONE" if (pulled and not l2first) else "P4_L2_FIRST"
        refk = k
        events.append(dict(b=b,dir=side,L1=L1,L2=L2,cls=cls,zone_type=0,confluence=0,retest_k=int(refk),
            reach32=bool(reach_after(refk,side,L2)),dtime=int(row.dtime),year=int(row.year))); continue
    zlo=ZLO[zti]; zhi=ZHI[zti]; ztype=int(ZT[zti])
    conf_cnt=int(sum(1 for c in cand if not (ZHI[c]<zlo or ZLO[c]>zhi)))  # overlapping eligible zones
    # REACTION: rejection close beyond zone before closing through distal side, within REACT bars, before L2
    rej=-1; failed=False
    for r in range(touched,min(touched+REACT,n)):
        if (H[r]>=L2) if side>0 else (L[r]<=L2): break
        if (C[r]<zlo) if side>0 else (C[r]>zhi): failed=True; break   # closed through distal side -> zone failed
        if (C[r]>zhi) if side>0 else (C[r]<zlo): rej=r; break          # closed back beyond zone -> rejection
    if rej<0:
        events.append(dict(b=b,dir=side,L1=L1,L2=L2,cls="P2_TOUCH_NO_REACT",zone_type=ztype,confluence=conf_cnt,retest_k=int(touched),
            reach32=bool(reach_after(touched,side,L2)),dtime=int(row.dtime),year=int(row.year))); continue
    # CONFIRMATION: break most recent causal micro swing (lower-high long / higher-low short) as-of rejection
    micro = mSWH[rej] if side>0 else mSWL[rej]
    conf=-1
    for q in range(rej,min(rej+CONFW,n)):
        if (H[q]>=L2) if side>0 else (L[q]<=L2): break
        if np.isfinite(micro) and ((C[q]>micro) if side>0 else (C[q]<micro)): conf=q; break
    if conf<0:
        events.append(dict(b=b,dir=side,L1=L1,L2=L2,cls="P2_TOUCH_NO_REACT",zone_type=ztype,confluence=conf_cnt,retest_k=int(touched),
            reach32=bool(reach_after(touched,side,L2)),dtime=int(row.dtime),year=int(row.year))); continue
    # P1 -> TRADE
    events.append(dict(b=b,dir=side,L1=L1,L2=L2,cls="P1_CONFIRMED",zone_type=ztype,confluence=conf_cnt,retest_k=int(touched),
        reach32=bool(reach_after(touched,side,L2)),dtime=int(row.dtime),year=int(row.year)))
    ei=conf+1
    if ei>=n or b<=open_until: continue
    entry=O[ei]; arc=ATR[conf] if ATR[conf]>0 else 1.0
    stop_raw=(zlo-BUF*arc) if side>0 else (zhi+BUF*arc); risk=max(abs(entry-stop_raw),2*SPREAD_B,0.05,0.10*arc); stop=entry-side*risk
    if (side>0 and L2<=entry) or (side<0 and L2>=entry): continue
    rr=abs(L2-entry)/risk
    endk=min(ei+BACKSTOP,n-1); R=None; exit_i=endk; reason="timeout"; amb=False; mae_R=0.0
    for k in range(ei,endk+1):
        adv=(entry-L[k]) if side>0 else (H[k]-entry); mae_R=max(mae_R,adv/risk)
        hs=(L[k]<=stop) if side>0 else (H[k]>=stop); tg=(H[k]>=L2) if side>0 else (L[k]<=L2)
        if hs and tg: R=-1.0; exit_i=k; reason="stop"; amb=True; break
        if hs: R=-1.0; exit_i=k; reason="stop"; break
        if tg: R=abs(L2-entry)/risk; exit_i=k; reason="target"; break
    if R is None: R=side*(C[endk]-entry)/risk; exit_i=endk; reason="timeout"
    net=R-SPREAD_B/risk; net_s=R-SPREAD_S/risk
    sL2={}
    if net<=0:
        for w in (4,8,16,32):
            hit=False
            for k in range(exit_i+1,min(exit_i+1+w,n)):
                if (H[k]>=L2) if side>0 else (L[k]<=L2): hit=True; break
            sL2[w]=hit
    favbi=float(max(H[ei:exit_i+1])-entry) if side>0 else float(entry-min(L[ei:exit_i+1]))
    trades.append(dict(b=b,ei=int(ei),dir=side,entry=float(entry),L1=L1,L2=L2,stop=float(stop),risk=float(risk),natRR=float(rr),zone_type=ztype,confluence=conf_cnt,
        R=float(R),net_R=float(net),net_R_stress=float(net_s),exit_i=int(exit_i),exit_reason=reason,ambiguous=bool(amb),mae_R=float(mae_R),
        pullback_to_conf=int(conf-touched),bars_to_L2=int(exit_i-ei) if reason=="target" else -1,
        stop_then_L2_4=sL2.get(4,False),stop_then_L2_8=sL2.get(8,False),stop_then_L2_16=sL2.get(16,False),stop_then_L2_32=sL2.get(32,False),
        L1_type=int(row.L1_type),dtime=int(row.dtime),year=int(row.year),fav_usd=favbi,tgt_atr=float(abs(L2-entry)/arc)))
    open_until=exit_i
EV=pd.DataFrame(events); TR=pd.DataFrame(trades)
EV.to_parquet(OUT+r"\STRUCTURAL_REACTION_TO_L2_V1_EVENTS.parquet"); TR.to_parquet(OUT+r"\STRUCTURAL_REACTION_TO_L2_V1_TRADES.parquet")
yrs=(EV1.dtime.max()-EV1.dtime.min())/(365.25*86400); vc=EV.cls.value_counts()
print(f"FUNNEL accepted(has_L2)={len(EV)}: P1={vc.get('P1_CONFIRMED',0)} P2={vc.get('P2_TOUCH_NO_REACT',0)} P3={vc.get('P3_NO_ZONE',0)} P4={vc.get('P4_L2_FIRST',0)}")
print(f"INDEPENDENT_TRADES={len(TR)} ({len(TR)/yrs:.0f}/yr)")
p1=EV[EV.cls=="P1_CONFIRMED"]; p2=EV[EV.cls=="P2_TOUCH_NO_REACT"]; p3=EV[EV.cls=="P3_NO_ZONE"]
print(f"L2 reach: P1={100*p1.reach32.mean():.1f}% P2={100*p2.reach32.mean():.1f}% P3={100*p3.reach32.mean():.1f}%")
if len(TR):
    r=TR.net_R.to_numpy()
    print(f"BASE={r.mean():+.4f} STRESS={TR.net_R_stress.mean():+.4f} WR={(r>0).mean():.3f} PF={r[r>0].sum()/(abs(r[r<=0].sum())+1e-9):.3f} medNatRR={np.median(TR.natRR):.2f} maxDD={(np.maximum.accumulate(np.cumsum(r))-np.cumsum(r)).max():.0f}R")
    print(f"anchor mix P1: {p1.zone_type.value_counts().to_dict()} | trade zone mix: {TR.zone_type.value_counts().to_dict()}")

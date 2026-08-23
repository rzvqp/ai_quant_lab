"""bfsd_engine.py — BLIND_FORWARD_STRUCTURE_DISCOVERY_V1, STRICT candle-by-candle replay engine (CEO mandate + 2 corrections
2026-08-23: (i) STRICT_CANDLE_BY_CANDLE_REPLAY / NO_FORWARD_WINDOW / OUTCOME_ONLY_AFTER_REPLAY; (ii) TOP-DOWN H4->H1->M15->M5).

HARD CAUSALITY WALL: this file NEVER computes any outcome (no MFE/MAE/target/return). It replays episodes ONE CANDLE AT A TIME.
At each candle T the analyzer is a pure function of history<=T: HTF/LTF primitives are filtered to their KNOWABLE bar
(swings/FVG confirmed_idx; breaks bar idx; OB formation_idx+1 [ratified 'OB cunoscut la bara i']; HTF bars by complete_at<=T),
price arrays read only via [:T+1]. Reading order is TOP-DOWN: H4 context -> H1 structure -> M15 setup (-> M5 optional). If H4/H1
do not justify, NO_TRADE (never manufacture an M15 setup). When a setup is valid at T, a PREDICTION is FROZEN (immutable) BEFORE
T+1 is revealed. Outcomes are computed only later by bfsd_score.py. Windows/episodes are mechanically stratified + seeded.

Writes: predictions.jsonl (frozen setups) + observations are implicit (per-candle state summarized in each prediction). No lookahead.
Data: cur_data M15 2011-2026."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
import market_structure as MS
from market_structure import Block
import imbalance_mechanics as IM
import order_flow as OF

SEED=20260823
N_EPISODES=60
EP_LEN=400            # M15 candles per episode (~4.2 trading days) replayed one-by-one
COOLDOWN=16          # candles after a freeze before another may be frozen (count-based, causal)
CTX=300              # min prior context bars before an episode may start

def build_blocks(t):
    gaps=np.where(np.diff(t)>72*3600)[0]; bs=[]; s=0
    for g in gaps: bs.append(Block(s,g+1)); s=g+1
    bs.append(Block(s,len(t))); return bs
def ema(x,span): return pd.Series(x).ewm(span=span,adjust=False).mean().to_numpy()

def resample(tsec,o,h,l,c,period):
    """Causal HTF bars. Returns per-HTF-bar arrays + complete_at (M15 index where the HTF bar closes = its last M15 bar)."""
    bucket=(tsec//period)*period
    df=pd.DataFrame({"b":bucket,"o":o,"h":h,"l":l,"c":c,"i":np.arange(len(tsec))})
    g=df.groupby("b",sort=True)
    O=g["o"].first().to_numpy(); H=g["h"].max().to_numpy(); L=g["l"].min().to_numpy(); C=g["c"].last().to_numpy()
    CA=g["i"].last().to_numpy()  # complete_at (M15 idx)
    return O,H,L,C,CA

def htf_state(O,H,L,C):
    """Per-HTF-bar structural state (causal within HTF series): trend(+1/-1/0), phase(impulse/correction), last swing hi/lo."""
    N=len(C); blk=[Block(0,N)]
    sw=MS.label_structure(MS.detect_swings(H,L,blk)); brk=MS.detect_breaks(C,sw,blk); BK=MS.BreakKind
    e20=ema(C,20); e50=ema(C,50)
    br=np.zeros(N,np.int8); cur=0; order=sorted(brk,key=lambda b:b.idx); bi=0
    for i in range(N):
        while bi<len(order) and order[bi].idx==i:
            cur=1 if order[bi].kind in (BK.BOS_BULL,BK.CHOCH_BULL) else -1; bi+=1
        br[i]=cur
    # last confirmed swing hi/lo available at each HTF bar
    swhi=np.full(N,np.nan); swlo=np.full(N,np.nan)
    sh=[s for s in sw if s.kind is MS.SwingKind.HIGH]; sl=[s for s in sw if s.kind is MS.SwingKind.LOW]
    shc=sorted([(s.confirmed_idx,s.price) for s in sh]); slc=sorted([(s.confirmed_idx,s.price) for s in sl])
    import bisect
    shx=[x[0] for x in shc]; slx=[x[0] for x in slc]
    for i in range(N):
        a=bisect.bisect_right(shx,i)-1;  swhi[i]=shc[a][1] if a>=0 else np.nan
        b=bisect.bisect_right(slx,i)-1;  swlo[i]=slc[b][1] if b>=0 else np.nan
    trend=np.zeros(N,np.int8); phase=np.array(["--"]*N,dtype=object)
    for i in range(N):
        up=(e20[i]>e50[i]) and br[i]>=0; dn=(e20[i]<e50[i]) and br[i]<=0
        trend[i]=1 if up else (-1 if dn else 0)
        hi=swhi[i]; lo=swlo[i]
        if np.isfinite(hi) and np.isfinite(lo) and hi>lo:
            pos=(C[i]-lo)/(hi-lo)
            if trend[i]>0: phase[i]="impulse" if pos>0.62 else ("correction" if pos<0.5 else "mid")
            elif trend[i]<0: phase[i]="impulse" if pos<0.38 else ("correction" if pos>0.5 else "mid")
            else: phase[i]="range"
        else: phase[i]="na"
    return trend,phase,swhi,swlo,CA_map_helper()  # placeholder

def CA_map_helper(): return None

def map_to_m15(state_arr, CA, n):
    """Forward-map an HTF-bar-indexed array to M15 bars: at M15 T, value of the last HTF bar with complete_at<=T."""
    out=np.empty(n,dtype=state_arr.dtype) if state_arr.dtype!=object else np.array(["na"]*n,dtype=object)
    import bisect
    calist=list(CA)
    k=0
    for T in range(n):
        while k+1<len(calist) and calist[k+1]<=T: k+=1
        out[T]= state_arr[k] if calist[k]<=T else (state_arr[0] if state_arr.dtype!=object else "na")
    return out

def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m)
    dt=m["dt"]; yr=dt.dt.year.to_numpy(); hr=dt.dt.hour.to_numpy(); dayk=dt.dt.date.to_numpy(); tsec=m["time"].to_numpy()
    e20=m["ema20"].to_numpy(); e50=m["ema50"].to_numpy()
    blocks=build_blocks(tsec)
    # ---- HTF causal structure H4 (14400s) and H1 (3600s) ----
    for period,nm in [(14400,"H4"),(3600,"H1")]:
        O,H,L,C,CA=resample(tsec,o,h,l,c,period)
        tr,ph,shi,slo,_=htf_state(O,H,L,C)
        if nm=="H4":
            h4_tr=map_to_m15(tr,CA,n); h4_ph=map_to_m15(ph,CA,n); h4_shi=map_to_m15(shi,CA,n); h4_slo=map_to_m15(slo,CA,n)
        else:
            h1_tr=map_to_m15(tr,CA,n); h1_ph=map_to_m15(ph,CA,n); h1_shi=map_to_m15(shi,CA,n); h1_slo=map_to_m15(slo,CA,n)
    # ---- M15 primitives (knowable-bar tagged) ----
    swings=MS.label_structure(MS.detect_swings(h,l,blocks))
    fvgs=IM.detect_fvgs(h,l,blocks); BULL=IM.FVGKind.BULLISH
    fv=sorted([(f.confirmed_idx,f.lower,f.upper,(f.kind is BULL)) for f in fvgs])
    fv_k=np.array([x[0] for x in fv]); fv_lo=np.array([x[1] for x in fv]); fv_hi=np.array([x[2] for x in fv]); fv_bull=np.array([x[3] for x in fv])
    obs=OF.detect_order_blocks(o,h,l,c,n); KIND=OF.OrderBlockKind; DEM=[k for k in KIND if 'DEM' in k.name or 'BULL' in k.name][0]
    ob=sorted([(ob.formation_idx+1,ob.zone_lower,ob.zone_upper,(ob.kind==DEM)) for ob in obs])  # knowable = formation_idx+1
    ob_k=np.array([x[0] for x in ob]); ob_lo=np.array([x[1] for x in ob]); ob_hi=np.array([x[2] for x in ob]); ob_dem=np.array([x[3] for x in ob])
    dfd=pd.DataFrame({"day":dayk,"h":h,"l":l}); dh=dfd.groupby("day")["h"].max(); dl=dfd.groupby("day")["l"].min()
    days=list(dh.index); pdh_m={days[i]:dh.iloc[i-1] for i in range(1,len(days))}; pdl_m={days[i]:dl.iloc[i-1] for i in range(1,len(days))}
    pdh=np.array([pdh_m.get(d,np.nan) for d in dayk]); pdl=np.array([pdl_m.get(d,np.nan) for d in dayk])
    def session(i):
        H=hr[i]; return "AS" if H<8 else ("LN" if H<13 else ("NY" if H<20 else "AS"))
    def era(i): return "D" if yr[i]<=2018 else ("C" if yr[i]<=2022 else "O")
    def vol(i):
        if not np.isfinite(atr_ma[i]) or atr_ma[i]<=0: return "m"
        r=atr[i]/atr_ma[i]; return "h" if r>1.2 else ("l" if r<0.8 else "m")
    # nearest causal demand/supply zone (M15) knowable<=T-? we test at candle j using knowable<=j
    def demand(i):
        z=[]
        k=np.searchsorted(fv_k,i,side="right")
        for jj in range(max(0,k-80),k):
            if not fv_bull[jj] or fv_hi[jj]>c[i]: continue
            cf=fv_k[jj]
            if cf<i and np.min(l[cf+1:i+1])<=fv_lo[jj]: continue
            z.append(("bFVG",fv_lo[jj],fv_hi[jj]))
        kb=np.searchsorted(ob_k,i,side="right")
        for jj in range(max(0,kb-80),kb):
            if not ob_dem[jj] or ob_hi[jj]>c[i]: continue
            z.append(("bOB",ob_lo[jj],ob_hi[jj]))
        if np.isfinite(pdl[i]) and pdl[i]<c[i]: z.append(("PDL",pdl[i]-0.1*atr[i],pdl[i]+0.1*atr[i]))
        if not z: return None
        z.sort(key=lambda x:-x[2]); return z[0]
    def supply(i):
        z=[]
        k=np.searchsorted(fv_k,i,side="right")
        for jj in range(max(0,k-80),k):
            if fv_bull[jj] or fv_lo[jj]<c[i]: continue
            cf=fv_k[jj]
            if cf<i and np.max(h[cf+1:i+1])>=fv_hi[jj]: continue
            z.append(("rFVG",fv_lo[jj],fv_hi[jj]))
        kb=np.searchsorted(ob_k,i,side="right")
        for jj in range(max(0,kb-80),kb):
            if ob_dem[jj] or ob_lo[jj]<c[i]: continue
            z.append(("rOB",ob_lo[jj],ob_hi[jj]))
        if np.isfinite(pdh[i]) and pdh[i]>c[i]: z.append(("PDH",pdh[i]-0.1*atr[i],pdh[i]+0.1*atr[i]))
        if not z: return None
        z.sort(key=lambda x:x[1]); return z[0]

    # ---- TOP-DOWN per-candle decision (pure fn of history<=T) ----
    def topdown(T):
        """Returns (action, detail) where action in {LONG,SHORT,NO_TRADE}. H4 context -> H1 structure -> M15 setup."""
        H4t=int(h4_tr[T]); H4p=h4_ph[T]; H1t=int(h1_tr[T]); H1p=h1_ph[T]
        # 1) H4 context gate
        if H4t>0:   # bullish context -> only look for LONGs, and only when H1 is correcting/pulling back within it
            if H1p in ("correction","mid","range") or H1t<=0:
                z=demand(T)
                if z is not None:
                    _,zl,zh=z
                    # M15 setup trigger: current candle taps demand & closes back up holding
                    if l[T]<=zh and l[T]>=zl-0.4*atr[T] and c[T]>o[T] and c[T]>zl:
                        entry=c[T]; inval=min(zl,l[T])-0.1*atr[T]
                        if entry-inval<0.15*atr[T]: inval=entry-0.5*atr[T]
                        return "LONG",dict(zone=z[0],entry=entry,inval=inval,h4=H4t,h4p=H4p,h1=H1t,h1p=H1p)
            return "NO_TRADE",dict(why="H4bull_noH1pullback_or_nozone",h4=H4t,h1=H1t,h1p=H1p)
        if H4t<0:
            if H1p in ("correction","mid","range") or H1t>=0:
                z=supply(T)
                if z is not None:
                    _,zl,zh=z
                    if h[T]>=zl and h[T]<=zh+0.4*atr[T] and c[T]<o[T] and c[T]<zh:
                        entry=c[T]; inval=max(zh,h[T])+0.1*atr[T]
                        if inval-entry<0.15*atr[T]: inval=entry+0.5*atr[T]
                        return "SHORT",dict(zone=z[0],entry=entry,inval=inval,h4=H4t,h4p=H4p,h1=H1t,h1p=H1p)
            return "NO_TRADE",dict(why="H4bear_noH1pullback_or_nozone",h4=H4t,h1=H1t,h1p=H1p)
        # H4 range/uncertain -> do NOT manufacture a trend setup; only clean H1 range-boundary fade if H4 truly ranging
        return "NO_TRADE",dict(why="H4_range_or_uncertain",h4=H4t,h1=H1t)

    # ---- episode sampling (stratified by era x H4-context x session at episode start; seeded) ----
    rng=np.random.default_rng(SEED)
    starts=[i for i in range(CTX, n-EP_LEN-1) if np.isfinite(atr[i]) and atr[i]>0]
    strata={}
    for i in starts:
        key=(era(i), int(h4_tr[i]), session(i)); strata.setdefault(key,[]).append(i)
    keys=sorted(strata.keys()); per=max(1,N_EPISODES//len(keys)); ep_starts=[]
    for k in keys:
        arr=np.array(strata[k]); take=min(per,len(arr)); ep_starts.extend(rng.choice(arr,size=take,replace=False).tolist())
    # spread if under target
    while len(ep_starts)<N_EPISODES and len(ep_starts)<len(starts):
        cand=int(rng.choice(starts));
        if cand not in ep_starts: ep_starts.append(cand)
    ep_starts=sorted(set(ep_starts))[:N_EPISODES]

    # ---- STRICT replay: one candle at a time; freeze predictions; NO outcome ----
    preds=[]; per_candle=0
    for es in ep_starts:
        last_freeze=-10**9
        for T in range(es, es+EP_LEN):
            per_candle+=1
            if T-last_freeze<COOLDOWN: continue
            act,det=topdown(T)
            if act in ("LONG","SHORT"):
                rec=dict(EPISODE=int(es), T=int(T), TS=str(dt.iloc[T]), ERA=era(T), SESSION=session(T), VOL=vol(T),
                         SIDE=act, ZONE=det["zone"], ENTRY=round(float(det["entry"]),2), INVAL=round(float(det["inval"]),2),
                         RISK_ATR=round(float(abs(det["entry"]-det["inval"])/atr[T]),2),
                         H4_TREND=int(det["h4"]), H4_PHASE=det["h4p"], H1_TREND=int(det["h1"]), H1_PHASE=det["h1p"],
                         EXP_DIR=(1 if act=="LONG" else -1),
                         MORPH=f"H4{det['h4']}|{det['h4p']}|H1{det['h1']}|{det['h1p']}|{det['zone']}|{session(T)}",
                         # frozen expectation (blind): expected next structural development
                         EXPECT="continuation_in_H4_direction_after_zone_reaction")
                preds.append(rec); last_freeze=T
    outp=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\predictions.jsonl"
    with open(outp,"w",encoding="utf-8") as f:
        for r in preds: f.write(json.dumps(r)+"\n")
    # NO outcome here. Summary counts only.
    from collections import Counter
    sc=Counter(r["SIDE"] for r in preds)
    print(f"BFSD-ENGINE (strict candle-by-candle, top-down): episodes={len(ep_starts)} candles_replayed={per_candle} frozen_predictions={len(preds)} ({dict(sc)})")
    print(f"  wrote {outp} — outcomes NOT computed here (walled off; run bfsd_score.py next).")
    # show a few frozen records (no outcome)
    for r in preds[:5]:
        print("  FROZEN:",r["TS"],r["SIDE"],r["ZONE"],"H4",r["H4_TREND"],r["H4_PHASE"],"H1",r["H1_TREND"],r["H1_PHASE"],"risk_atr",r["RISK_ATR"])
if __name__=="__main__": main()

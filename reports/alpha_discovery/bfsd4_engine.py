"""bfsd4_engine.py — BLIND_FORWARD_STRUCTURE_DISCOVERY_V1, BROADENED top-down reader (CEO 2026-08-24). PRIMARY method unchanged
(H4/N1 -> H1/N2 -> M15/N3 -> N6 BUY/SELL/NO_TRADE -> freeze -> reveal ONE candle). This iteration BROADENS what the reader may
OBSERVE and records it as descriptive TAGS (NOT predefined setup gates): displacement, failed-break/sweep, reclaim, acceptance,
rejection, compression/expansion, structural-failure, transition. Freeze occurs in a DIRECTIONAL H4/H1 context when ANY structural
event is observed at the candle; ALL observed tags are recorded. Morphology EMERGES later (secondary clustering) from the frozen
tags; NO tag is a hard entry gate. Writes to a NEW ledger (reading_ledger_b2.jsonl) — Batch-1 stays FROZEN. NEW seeds only.
Outcomes computed ONLY by bfsd4_score.py. N1/N2 live memoized; causal, bars<=T only, one candle at a time."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
import regime_classifier as RC, bias_h1 as BH, zone_map as ZM
from market_state import atr14
M5_START=1627344000; EP_LEN=400; N_EPISODES=80; COOLDOWN=10; CTX=900; ZW=400
def bull_dir(x): return x in ("up","weak_up")
def bear_dir(x): return x in ("down","weak_down")
def axlabel(ax):
    v=getattr(ax,'value',None); return v.label if v is not None and hasattr(v,'label') else "na"
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m); dt=m["dt"]; tsec=m["time"].to_numpy(); yr=dt.dt.year.to_numpy(); hr=dt.dt.hour.to_numpy()
    e20=m["ema20"].to_numpy(); e50=m["ema50"].to_numpy(); e200=pd.Series(c).ewm(span=200,adjust=False).mean().to_numpy()
    p20H=pd.Series(h).rolling(20).max().shift(1).to_numpy(); p20L=pd.Series(l).rolling(20).min().shift(1).to_numpy()
    SEED=int(sys.argv[1]) if len(sys.argv)>1 else 111
    APPEND=(len(sys.argv)>2 and sys.argv[2]=="append")
    def rs(period):
        b=(tsec//period)*period; df=pd.DataFrame({"b":b,"o":o,"h":h,"l":l,"c":c,"i":np.arange(n)}); g=df.groupby("b",sort=True)
        return (g["o"].first().to_numpy(),g["h"].max().to_numpy(),g["l"].min().to_numpy(),g["c"].last().to_numpy(),g["i"].last().to_numpy())
    O4,H4,L4,C4,CA4=rs(14400); O1,H1,L1,C1,CA1=rs(3600)
    h4_of=np.searchsorted(CA4,np.arange(n),side="right")-1; h1_of=np.searchsorted(CA1,np.arange(n),side="right")-1
    rc={}; bc={}
    def N1(T):
        k=int(h4_of[T])
        if k<0: return ("na","na",["unavailable"]*3)
        if k in rc: return rc[k]
        s=max(0,k-199); rg=RC.classify_regime(O4[s:k+1],H4[s:k+1],L4[s:k+1],C4[s:k+1]); rv=getattr(rg,'value',None)
        if rv is None: r=("na","na",["unavailable"]*3)
        else:
            ax=["available" if getattr(a,'value',None) is not None else "unavailable" for a in (rv.volatility,rv.structure,rv.direction)]
            r=(axlabel(rv.direction),axlabel(rv.volatility),ax)
        rc[k]=r; return r
    def N2(T,axes):
        k=int(h1_of[T])
        if k<0: return ("na",0.0)
        if k in bc: return bc[k]
        s=max(0,k-299)
        try:
            bs=BH.compute_bias(O1[s:k+1],H1[s:k+1],L1[s:k+1],C1[s:k+1],len(C1[s:k+1]),regime_axes_status=axes); bv=getattr(bs,'value',None); d="na"; mg=0.0
            if bv is not None:
                for f in bv.factors:
                    fv=getattr(f,'value',None)
                    if fv is not None and getattr(fv,'name','')=='structure_run_h1':
                        d=fv.direction.value if hasattr(fv.direction,'value') else str(fv.direction); rw=getattr(fv,'raw',None); mg=float(getattr(rw,'value',0.0) or 0.0)
            r=(d,mg)
        except Exception: r=("na",0.0)
        bc[k]=r; return r
    def era(i): return "D" if yr[i]<=2018 else ("C" if yr[i]<=2022 else "O")
    def session(i):
        H=hr[i]; return "AS" if H<8 else ("LN" if H<13 else ("NY" if H<20 else "AS"))
    def bias_of(d,b):
        if bull_dir(d) and b=="long": return "BULLISH"
        if bear_dir(d) and b=="short": return "BEARISH"
        if (bull_dir(d) and b=="short") or (bear_dir(d) and b=="long"): return "TRANSITION"
        if d in ("neutral","none","na"): return "RANGE/UNCERTAIN"
        return "UNCERTAIN"
    def observe(T):
        """causal structural observation tags at candle T (bars<=T). Returns (tags set, primary_trigger or None)."""
        tags=[]; body=abs(c[T]-o[T]); rng=h[T]-l[T]; a=atr[T]
        if a<=0 or not np.isfinite(p20H[T]): return tags,None
        # displacement
        if body>=1.5*a and c[T]>o[T]: tags.append("DISP_up")
        if body>=1.5*a and c[T]<o[T]: tags.append("DISP_dn")
        # break / sweep vs prior-20 extreme
        if c[T]>p20H[T]: tags.append("BREAK_up")
        elif h[T]>p20H[T] and c[T]<=p20H[T]: tags.append("SWEEP_up")   # failed break up
        if c[T]<p20L[T]: tags.append("BREAK_dn")
        elif l[T]<p20L[T] and c[T]>=p20L[T]: tags.append("SWEEP_dn")   # failed break down
        # rejection wicks
        uw=h[T]-max(o[T],c[T]); lw=min(o[T],c[T])-l[T]
        if lw>=1.5*max(body,1e-9) and lw>0.3*a: tags.append("REJ_low")   # rejection of lows -> bullish
        if uw>=1.5*max(body,1e-9) and uw>0.3*a: tags.append("REJ_high")  # rejection of highs -> bearish
        # compression/expansion state
        if np.isfinite(atr_ma[T]) and atr_ma[T]>0:
            if a<0.8*atr_ma[T]: tags.append("COMPRESS")
            elif a>1.2*atr_ma[T]: tags.append("EXPAND")
        triggers=[t for t in tags if t.split("_")[0] in ("DISP","BREAK","SWEEP","REJ")]
        return tags,(triggers[0] if triggers else None)
    def zonemap(T):
        s=max(0,T-ZW+1); H=list(h[s:T+1]); L=list(l[s:T+1]); C=list(c[s:T+1]); O=list(o[s:T+1]); TT=list(tsec[s:T+1])
        a=atr14(H,L,C); return ZM.build_zone_map(H,L,C,O,TT,atr=a,regime_available=True,bias_available=True)
    rng=np.random.default_rng(SEED)
    def tproxy(i):
        if e20[i]>e50[i] and c[i]>e200[i]: return "up"
        if e20[i]<e50[i] and c[i]<e200[i]: return "dn"
        return "fl"
    starts=[i for i in range(CTX,n-EP_LEN-1) if np.isfinite(atr[i]) and atr[i]>0]
    strata={}
    for i in starts: strata.setdefault((era(i),session(i),tproxy(i)),[]).append(i)
    keys=sorted(strata.keys()); per=max(1,N_EPISODES//max(1,len(keys))); es=[]
    for k in keys:
        arr=np.array(strata[k]); es.extend(rng.choice(arr,size=min(per,len(arr)),replace=False).tolist())
    es=sorted(set(es))[:N_EPISODES]
    frozen=[]; dec_ct={"BUY":0,"SELL":0,"NO_TRADE":0}; candles=0
    for e0 in es:
        last=-10**9
        for T in range(e0,e0+EP_LEN):
            candles+=1
            d,vol,axes=N1(T); b,mag=N2(T,axes); bias=bias_of(d,b)
            if bias not in ("BULLISH","BEARISH") or T-last<COOLDOWN: dec_ct["NO_TRADE"]+=1; continue
            tags,trig=observe(T)
            if trig is None: dec_ct["NO_TRADE"]+=1; continue   # freeze only when SOMETHING structural is observed
            # N3 zone context (canonical, computed only at trigger candles)
            zv=getattr(zonemap(T),"value",None); near="noZone"; zanchor=None
            if zv is not None and zv.zones:
                ref=zv.reference_price
                pool=[zz for zz in zv.zones if (zz.price_anchor<ref if bias=="BULLISH" else zz.price_anchor>ref)]
                if pool:
                    zb=min(pool,key=lambda x:x.distance_atr); zanchor=zb.price_anchor
                    if zb.distance_atr<=1.0: near="nearZone"
            n4="available" if tsec[T]>=M5_START else "unavailable(no_M5)"
            dec="BUY" if bias=="BULLISH" else "SELL"; dec_ct[dec]+=1; last=T
            entry=c[T]
            inval=(p20L[T]-0.2*atr[T]) if dec=="BUY" else (p20H[T]+0.2*atr[T])
            if dec=="BUY" and inval>=entry: inval=entry-0.8*atr[T]
            if dec=="SELL" and inval<=entry: inval=entry+0.8*atr[T]
            frozen.append(dict(EPISODE=int(e0),T=int(T),TS=str(dt.iloc[T]),ERA=era(T),SESSION=session(T),
                N1_DIR=d,N1_VOL=vol,N2_BIAS=b,N2_MAG=round(float(mag),1),N4_STATUS=n4,N6_DECISION=dec,STRUCTURAL_BIAS=bias,
                TRIGGER=trig,TAGS=tags,NEAR_ZONE=near,
                ENTRY=round(float(entry),2),INVALIDATION=round(float(inval),2),RISK_ATR=round(float(abs(entry-inval)/atr[T]),2),
                EXP_DIR=(1 if dec=="BUY" else -1),
                SIG=f"{bias}|{d}|{trig}|{near}|{session(T)}"))
    outp=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\reading_ledger_b2.jsonl"
    with open(outp,"a" if APPEND else "w",encoding="utf-8") as f:
        for r in frozen: f.write(json.dumps(r)+"\n")
    from collections import Counter
    print(f"BFSD4-ENGINE (broadened, seed={SEED} append={APPEND}): episodes={len(es)} candles={candles} decisions={dec_ct} frozen={len(frozen)}")
    print("  trigger dist:",dict(Counter(r['TRIGGER'] for r in frozen)))
    print(f"  wrote {outp} (Batch-1 frozen, untouched). NO outcome here.")
if __name__=="__main__": main()

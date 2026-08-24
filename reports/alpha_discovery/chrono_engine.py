"""chrono_engine.py — CHRONOLOGICAL_MARKET_LEARNING (CEO mandate 2026-08-24). PRIMARY method: walk XAUUSD M15 STRICTLY in time
from 2020-01-01 to the latest authorized bar, candle-by-candle, as if living through it. At each candle: top-down N1(H4 regime) ->
N2(H1 bias) -> N3(M15 zones, live) -> N4 status (M5 native only 2021-07-27+, else UNAVAILABLE, never synthesized) -> N6 BUY/SELL/
NO_TRADE + readiness components -> FREEZE -> reveal ONE candle -> repeat. NO future access, NO outcome computed here (outcomes are
computed per-quarter by chrono_checkpoint.py, using only data available by the checkpoint). Broadened observation tags (displacement/
break/failed-break/rejection/compression/expansion) recorded descriptively, NOT as gates. Freezes when directional context + a
structural event. Each reading tagged by QUARTER. N1/N2 live memoized. Output: reading_chrono.jsonl (+ per-quarter NO_TRADE counts)."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
import regime_classifier as RC, bias_h1 as BH, zone_map as ZM
from market_state import atr14
M5_START=1627344000; START_TS=1577836800  # 2021-07-27 ; 2020-01-01 UTC
COOLDOWN=10; ZW=400
def bull_dir(x): return x in ("up","weak_up")
def bear_dir(x): return x in ("down","weak_down")
def axlabel(ax):
    v=getattr(ax,'value',None); return v.label if v is not None and hasattr(v,'label') else "na"
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m); dt=m["dt"]; tsec=m["time"].to_numpy(); hr=dt.dt.hour.to_numpy()
    mon=dt.dt.month.to_numpy(); yr=dt.dt.year.to_numpy()
    p20H=pd.Series(h).rolling(20).max().shift(1).to_numpy(); p20L=pd.Series(l).rolling(20).min().shift(1).to_numpy()
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
        r=("na","na",["unavailable"]*3) if rv is None else (axlabel(rv.direction),axlabel(rv.volatility),["available" if getattr(a,'value',None) is not None else "unavailable" for a in (rv.volatility,rv.structure,rv.direction)])
        rc[k]=r; return r
    def N2(T,axes):
        k=int(h1_of[T])
        if k<0: return ("na",0.0)
        if k in bc: return bc[k]
        s=max(0,k-299); d="na"; mg=0.0
        try:
            bs=BH.compute_bias(O1[s:k+1],H1[s:k+1],L1[s:k+1],C1[s:k+1],len(C1[s:k+1]),regime_axes_status=axes); bv=getattr(bs,'value',None)
            if bv is not None:
                for f in bv.factors:
                    fv=getattr(f,'value',None)
                    if fv is not None and getattr(fv,'name','')=='structure_run_h1':
                        d=fv.direction.value if hasattr(fv.direction,'value') else str(fv.direction); rw=getattr(fv,'raw',None); mg=float(getattr(rw,'value',0.0) or 0.0)
        except Exception: pass
        bc[k]=(d,mg); return (d,mg)
    def session(i):
        H=hr[i]; return "AS" if H<8 else ("LN" if H<13 else ("NY" if H<20 else "AS"))
    def quarter(i): return f"{yr[i]}-Q{(mon[i]-1)//3+1}"
    def bias_of(d,b):
        if bull_dir(d) and b=="long": return "BULLISH"
        if bear_dir(d) and b=="short": return "BEARISH"
        if (bull_dir(d) and b=="short") or (bear_dir(d) and b=="long"): return "TRANSITION"
        if d in ("neutral","none","na"): return "RANGE/UNCERTAIN"
        return "UNCERTAIN"
    def observe(T):
        tags=[]; body=abs(c[T]-o[T]); a=atr[T]
        if a<=0 or not np.isfinite(p20H[T]): return tags,None
        if body>=1.5*a and c[T]>o[T]: tags.append("DISP_up")
        if body>=1.5*a and c[T]<o[T]: tags.append("DISP_dn")
        if c[T]>p20H[T]: tags.append("BREAK_up")
        elif h[T]>p20H[T] and c[T]<=p20H[T]: tags.append("SWEEP_up")
        if c[T]<p20L[T]: tags.append("BREAK_dn")
        elif l[T]<p20L[T] and c[T]>=p20L[T]: tags.append("SWEEP_dn")
        uw=h[T]-max(o[T],c[T]); lw=min(o[T],c[T])-l[T]
        if lw>=1.5*max(body,1e-9) and lw>0.3*a: tags.append("REJ_low")
        if uw>=1.5*max(body,1e-9) and uw>0.3*a: tags.append("REJ_high")
        if np.isfinite(atr_ma[T]) and atr_ma[T]>0:
            if a<0.8*atr_ma[T]: tags.append("COMPRESS")
            elif a>1.2*atr_ma[T]: tags.append("EXPAND")
        trig=[t for t in tags if t.split("_")[0] in ("DISP","BREAK","SWEEP","REJ")]
        return tags,(trig[0] if trig else None)
    def zonemap(T):
        s=max(0,T-ZW+1); H=list(h[s:T+1]); L=list(l[s:T+1]); C=list(c[s:T+1]); O=list(o[s:T+1]); TT=list(tsec[s:T+1])
        a=atr14(H,L,C); return ZM.build_zone_map(H,L,C,O,TT,atr=a,regime_available=True,bias_available=True)
    start=int(np.searchsorted(tsec,START_TS,side="left"))
    frozen=[]; notrade=[]; last=-10**9
    from collections import defaultdict
    ntr=defaultdict(lambda: defaultdict(int))
    for T in range(start, n-2):
        d,vol,axes=N1(T); b,mag=N2(T,axes); bias=bias_of(d,b); q=quarter(T)
        if bias not in ("BULLISH","BEARISH"): ntr[q]["ctx_not_directional"]+=1; continue
        tags,trig=observe(T)
        if trig is None: ntr[q]["no_structural_event"]+=1; continue
        if T-last<COOLDOWN: ntr[q]["cooldown"]+=1; continue
        zv=getattr(zonemap(T),"value",None); near="noZone"; dist=None
        if zv is not None and zv.zones:
            ref=zv.reference_price; pool=[z for z in zv.zones if (z.price_anchor<ref if bias=="BULLISH" else z.price_anchor>ref)]
            if pool:
                zb=min(pool,key=lambda x:x.distance_atr); dist=round(float(zb.distance_atr),2)
                if zb.distance_atr<=1.0: near="nearZone"
        n4="available" if tsec[T]>=M5_START else "UNAVAILABLE(no_M5)"
        dec="BUY" if bias=="BULLISH" else "SELL"; last=T
        entry=o[T+1]; inval=(p20L[T]-0.2*atr[T]) if dec=="BUY" else (p20H[T]+0.2*atr[T])
        if dec=="BUY" and inval>=entry: inval=entry-0.8*atr[T]
        if dec=="SELL" and inval<=entry: inval=entry+0.8*atr[T]
        n1s=1.0 if d in ("up","down") else 0.5
        frozen.append(dict(T=int(T),TS=str(dt.iloc[T]),QUARTER=q,SESSION=session(T),
            N1_DIR=d,N1_VOL=vol,N2_BIAS=b,N2_MAG=round(float(mag),1),N4_STATUS=n4,N6_DECISION=dec,STRUCTURAL_BIAS=bias,
            TRIGGER=trig,TAGS=tags,NEAR_ZONE=near,ZONE_DIST=dist,N1_STRENGTH=n1s,
            ENTRY=round(float(entry),2),INVALIDATION=round(float(inval),2),EXP_DIR=(1 if dec=="BUY" else -1),
            SIG=f"{bias}|{d}|{trig}|{near}|{session(T)}"))
    outp=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\reading_chrono.jsonl"
    with open(outp,"w",encoding="utf-8") as f:
        for r in frozen: f.write(json.dumps(r)+"\n")
    with open(r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\chrono_notrade.json","w",encoding="utf-8") as f:
        json.dump({q:dict(v) for q,v in ntr.items()},f,indent=0)
    from collections import Counter
    qc=Counter(r["QUARTER"] for r in frozen)
    print(f"CHRONO-ENGINE: start={dt.iloc[start]} candles={n-2-start} frozen_readings={len(frozen)} quarters={len(qc)}")
    print("  per-quarter frozen:", dict(sorted(qc.items())))
    print(f"  wrote {outp}. NO outcome here. Next: chrono_checkpoint.py (quarterly, forward-tested).")
if __name__=="__main__": main()

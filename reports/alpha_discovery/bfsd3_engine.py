"""bfsd3_engine.py — BLIND_FORWARD_STRUCTURE_DISCOVERY_V1 engine v3 (CEO correction 2026-08-24): PRIMARY discovery = the TOP-DOWN
canonical N-node candle-by-candle MARKET READING ledger. Mining is SECONDARY (later, on this ledger). Self-contained: N1/N2 computed
LIVE + memoized per HTF bar (no cache dependency).

Per candle T (STRICT, causal, bars<=T only, NO outcome): N1 regime (H4) -> N2 bias (H1) -> if H4/H1 justify, N3 zone map (M15, LIVE)
-> N4 status (M5 native only 2021-07-27+) -> N6 decision BUY/SELL/NO_TRADE + ENTRY_READINESS 0-100 -> FREEZE actionable BEFORE T+1.
If H4/H1 do not justify: NO_TRADE (never manufacture). Reveal ONE candle, rebuild, repeat. Morphology is NOT imposed/mined here — it
EMERGES later (bfsd3_score.py) from this frozen reading ledger. Outcomes computed ONLY there."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
import regime_classifier as RC, bias_h1 as BH, zone_map as ZM
from market_state import atr14
M5_START=1627344000  # 2021-07-27 UTC
EP_LEN=400; N_EPISODES=80; COOLDOWN=12; CTX=900; ZW=400
def bull_dir(x): return x in ("up","weak_up")
def bear_dir(x): return x in ("down","weak_down")
def axlabel(ax):
    v=getattr(ax,'value',None); return v.label if v is not None and hasattr(v,'label') else "na"
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); n=len(m); dt=m["dt"]; tsec=m["time"].to_numpy(); yr=dt.dt.year.to_numpy(); hr=dt.dt.hour.to_numpy()
    # HTF resample + complete_at
    def rs(period):
        b=(tsec//period)*period; df=pd.DataFrame({"b":b,"o":o,"h":h,"l":l,"c":c,"i":np.arange(n)}); g=df.groupby("b",sort=True)
        return (g["o"].first().to_numpy(),g["h"].max().to_numpy(),g["l"].min().to_numpy(),g["c"].last().to_numpy(),g["i"].last().to_numpy())
    O4,H4,L4,C4,CA4=rs(14400); O1,H1,L1,C1,CA1=rs(3600)
    h4_of=np.searchsorted(CA4,np.arange(n),side="right")-1   # last H4 bar with complete_at<=T
    h1_of=np.searchsorted(CA1,np.arange(n),side="right")-1
    reg_cache={}; bias_cache={}
    def N1(T):
        k=int(h4_of[T])
        if k<0: return ("na","na",["unavailable"]*3)
        if k in reg_cache: return reg_cache[k]
        s=max(0,k-199); reg=RC.classify_regime(O4[s:k+1],H4[s:k+1],L4[s:k+1],C4[s:k+1]); rv=getattr(reg,'value',None)
        if rv is None: r=("na","na",["unavailable"]*3)
        else:
            axes=["available" if getattr(a,'value',None) is not None else "unavailable" for a in (rv.volatility,rv.structure,rv.direction)]
            r=(axlabel(rv.direction),axlabel(rv.volatility),axes)
        reg_cache[k]=r; return r
    def N2(T,axes):
        k=int(h1_of[T])
        if k<0: return ("na",0.0)
        if k in bias_cache: return bias_cache[k]
        s=max(0,k-299)
        try:
            bias=BH.compute_bias(O1[s:k+1],H1[s:k+1],L1[s:k+1],C1[s:k+1],len(C1[s:k+1]),regime_axes_status=axes); bv=getattr(bias,'value',None)
            d="na"; mg=0.0
            if bv is not None:
                for f in bv.factors:
                    fv=getattr(f,'value',None)
                    if fv is not None and getattr(fv,'name','')=='structure_run_h1':
                        d=fv.direction.value if hasattr(fv.direction,'value') else str(fv.direction)
                        rw=getattr(fv,'raw',None); mg=float(getattr(rw,'value',0.0) or 0.0)
            r=(d,mg)
        except Exception: r=("na",0.0)
        bias_cache[k]=r; return r
    def era(i): return "D" if yr[i]<=2018 else ("C" if yr[i]<=2022 else "O")
    def session(i):
        H=hr[i]; return "AS" if H<8 else ("LN" if H<13 else ("NY" if H<20 else "AS"))
    def bias_of(dirl,bd):
        if bull_dir(dirl) and bd=="long": return "BULLISH"
        if bear_dir(dirl) and bd=="short": return "BEARISH"
        if (bull_dir(dirl) and bd=="short") or (bear_dir(dirl) and bd=="long"): return "TRANSITION"
        if dirl in ("neutral","none","na"): return "RANGE/UNCERTAIN"
        return "UNCERTAIN"
    def zonemap(T):
        s=max(0,T-ZW+1); H=list(h[s:T+1]); L=list(l[s:T+1]); C=list(c[s:T+1]); O=list(o[s:T+1]); TT=list(tsec[s:T+1])
        a=atr14(H,L,C); return ZM.build_zone_map(H,L,C,O,TT,atr=a,regime_available=True,bias_available=True)
    def readiness(dirl,mag,dist_atr):
        ds=1.0 if dirl in ("up","down") else 0.5
        ba=min(1.0,abs(mag)/8.0); pr=max(0.0,1.0-dist_atr/2.0)
        return int(round(100*(0.35*ds+0.25*ba+0.40*pr)))
    # episode sampling (stratified/seeded by era x session x CHEAP trend proxy — NO N1/N2 during stratification)
    rng=np.random.default_rng(20260824)
    e20=m["ema20"].to_numpy(); e50=m["ema50"].to_numpy(); e200=pd.Series(c).ewm(span=200,adjust=False).mean().to_numpy()
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
            n4="available" if tsec[T]>=M5_START else "unavailable(no_M5)"
            if bias not in ("BULLISH","BEARISH") or T-last<COOLDOWN: dec_ct["NO_TRADE"]+=1; continue
            zv=getattr(zonemap(T),"value",None)
            if zv is None or not zv.zones: dec_ct["NO_TRADE"]+=1; continue
            ref=zv.reference_price
            if bias=="BULLISH":
                cand=[zz for zz in zv.zones if zz.price_anchor<ref]
                if not cand: dec_ct["NO_TRADE"]+=1; continue
                zb=min(cand,key=lambda x:x.distance_atr); pa=zb.price_anchor; bd=zb.band
                interacting=l[T]<=pa+bd and c[T]>=pa-bd; rd=readiness(d,mag,zb.distance_atr)
                if not(interacting and rd>=50): dec_ct["NO_TRADE"]+=1; continue
                entry=c[T]; inval=pa-bd-0.2*atr[T]; dec="BUY"
            else:
                cand=[zz for zz in zv.zones if zz.price_anchor>ref]
                if not cand: dec_ct["NO_TRADE"]+=1; continue
                zb=min(cand,key=lambda x:x.distance_atr); pa=zb.price_anchor; bd=zb.band
                interacting=h[T]>=pa-bd and c[T]<=pa+bd; rd=readiness(d,mag,zb.distance_atr)
                if not(interacting and rd>=50): dec_ct["NO_TRADE"]+=1; continue
                entry=c[T]; inval=pa+bd+0.2*atr[T]; dec="SELL"
            dec_ct[dec]+=1; last=T
            frozen.append(dict(EPISODE=int(e0),T=int(T),TS=str(dt.iloc[T]),ERA=era(T),SESSION=session(T),
                N1_DIR=d,N1_VOL=vol,N2_BIAS=b,N2_MAG=round(float(mag),1),
                N3_ZONE_ANCHOR=round(float(pa),2),N3_ZONE_BAND=round(float(bd),2),N3_DIST_ATR=round(float(zb.distance_atr),2),
                N4_STATUS=n4,N6_DECISION=dec,STRUCTURAL_BIAS=bias,ENTRY_READINESS=rd,
                ENTRY=round(float(entry),2),ENTRY_ZONE=[round(float(pa-bd),2),round(float(pa+bd),2)],
                INVALIDATION=round(float(inval),2),RISK_ATR=round(float(abs(entry-inval)/atr[T]),2),
                EXP_DIR=(1 if dec=="BUY" else -1),
                EXPECTED_NEXT="reaction_at_zone_then_continuation_"+("up" if dec=="BUY" else "down"),
                CONFIDENCE=round(rd/100.0,2),
                SIG=f"{bias}|{d}|{vol}|{b}|{'disc' if pa<ref else 'prem'}|{session(T)}"))
    outp=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\reading_ledger.jsonl"
    with open(outp,"w",encoding="utf-8") as f:
        for r in frozen: f.write(json.dumps(r)+"\n")
    print(f"BFSD3-ENGINE (top-down N-node reading, live N1/N2): episodes={len(es)} candles={candles} decisions={dec_ct} frozen_actionable={len(frozen)}")
    print(f"  N4 available frozen: {sum(1 for r in frozen if r['N4_STATUS']=='available')}/{len(frozen)} | reg_cache={len(reg_cache)} bias_cache={len(bias_cache)}")
    print(f"  wrote {outp} — NO outcome here. Run bfsd3_score.py next.")
    for r in frozen[:4]: print("  FROZEN:",r["TS"],r["N6_DECISION"],"rd",r["ENTRY_READINESS"],r["STRUCTURAL_BIAS"],"N1",r["N1_DIR"],"N2",r["N2_BIAS"])
if __name__=="__main__": main()

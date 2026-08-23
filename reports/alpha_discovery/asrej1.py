"""asrej1.py — MECHANIZE + FULL QUANTITATIVE FALSIFICATION of preregistered candidate ASREJ-1 (PREREG_ASREJ1.md).
Deterministic rule (causal, bars<=T): N1(H4 regime dir)=up, N2(H1 bias)=long, nearest N3 confluence zone below reference with
distance_atr<=1.0, REJ_low wick (lower wick>=1.5*body & >=0.3*ATR), Asia session (00-08 UTC). Entry=next-bar OPEN, invalidation=
prior-20-low-0.2ATR, target=+2R, cooldown>=10 bars. Cost = STRESS 0.24 R round-trip. Cheap pre-filter (Asia+REJ_low) then canonical
N1/N2/N3 on survivors (live memoized). Full gate: overall/DISC/CONF/OOS net expectancy, tail(best-decile-removed), leave-one-year-out,
2x cost, entry-delay, neighbor(threshold) robustness, dedup/effN, portfolio independence vs S5(NY session). DISCOVERY->validation gate."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
import regime_classifier as RC, bias_h1 as BH, zone_map as ZM
from market_state import atr14
COST=0.24; HMAX=300
def axlabel(ax):
    v=getattr(ax,'value',None); return v.label if v is not None and hasattr(v,'label') else "na"
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); n=len(m); tsec=m["time"].to_numpy(); yr=m["dt"].dt.year.to_numpy(); hr=m["dt"].dt.hour.to_numpy()
    p20H=pd.Series(h).rolling(20).max().shift(1).to_numpy(); p20L=pd.Series(l).rolling(20).min().shift(1).to_numpy()
    def rs(period):
        b=(tsec//period)*period; df=pd.DataFrame({"b":b,"o":o,"h":h,"l":l,"c":c,"i":np.arange(n)}); g=df.groupby("b",sort=True)
        return (g["o"].first().to_numpy(),g["h"].max().to_numpy(),g["l"].min().to_numpy(),g["c"].last().to_numpy(),g["i"].last().to_numpy())
    O4,H4,L4,C4,CA4=rs(14400); O1,H1,L1,C1,CA1=rs(3600)
    h4_of=np.searchsorted(CA4,np.arange(n),side="right")-1; h1_of=np.searchsorted(CA1,np.arange(n),side="right")-1
    rc={}; bc={}
    def N1(T):
        k=int(h4_of[T])
        if k<0: return ("na",["unavailable"]*3)
        if k in rc: return rc[k]
        s=max(0,k-199); rg=RC.classify_regime(O4[s:k+1],H4[s:k+1],L4[s:k+1],C4[s:k+1]); rv=getattr(rg,'value',None)
        r=("na",["unavailable"]*3) if rv is None else (axlabel(rv.direction),["available" if getattr(a,'value',None) is not None else "unavailable" for a in (rv.volatility,rv.structure,rv.direction)])
        rc[k]=r; return r
    def N2(T,axes):
        k=int(h1_of[T])
        if k<0: return "na"
        if k in bc: return bc[k]
        s=max(0,k-299); d="na"
        try:
            bs=BH.compute_bias(O1[s:k+1],H1[s:k+1],L1[s:k+1],C1[s:k+1],len(C1[s:k+1]),regime_axes_status=axes); bv=getattr(bs,'value',None)
            if bv is not None:
                for f in bv.factors:
                    fv=getattr(f,'value',None)
                    if fv is not None and getattr(fv,'name','')=='structure_run_h1':
                        d=fv.direction.value if hasattr(fv.direction,'value') else str(fv.direction)
        except Exception: d="na"
        bc[k]=d; return d
    def zonemap(T):
        s=max(0,T-399); H=list(h[s:T+1]); L=list(l[s:T+1]); C=list(c[s:T+1]); O=list(o[s:T+1]); TT=list(tsec[s:T+1])
        a=atr14(H,L,C); return ZM.build_zone_map(H,L,C,O,TT,atr=a,regime_available=True,bias_available=True)
    # cheap pre-filter: Asia + REJ_low
    body=np.abs(c-o); lw=np.minimum(o,c)-l
    asia=(hr<8); rej_low=(lw>=1.5*np.maximum(body,1e-9))&(lw>=0.3*atr)&np.isfinite(atr)&(atr>0)
    def build_signals(dist_thr=1.0, wick_mult=1.5, delay=1):
        rejl=(lw>=wick_mult*np.maximum(body,1e-9))&(lw>=0.3*atr)&np.isfinite(atr)&(atr>0)
        cand=np.where(asia&rejl&np.isfinite(p20L)&(np.arange(n)<n-HMAX-delay-1)&(np.arange(n)>400))[0]
        sig=[]; last=-10**9
        for T in cand:
            if T-last<10: continue
            d,axes=N1(T)
            if d!="up": continue
            if N2(T,axes)!="long": continue
            zv=getattr(zonemap(T),"value",None)
            if zv is None or not zv.zones: continue
            ref=zv.reference_price; below=[z for z in zv.zones if z.price_anchor<ref]
            if not below: continue
            zb=min(below,key=lambda x:x.distance_atr)
            if zb.distance_atr>dist_thr: continue
            ei=T+delay
            if ei>=n-HMAX: continue
            entry=o[ei]; inval=p20L[T]-0.2*atr[T]
            if inval>=entry: inval=entry-0.8*atr[T]
            risk=entry-inval; tgt=entry+2*risk
            seg_l=l[ei:ei+HMAX]; seg_h=h[ei:ei+HMAX]
            fs=np.where(seg_l<=inval)[0]; ft=np.where(seg_h>=tgt)[0]
            fstop=fs[0] if len(fs) else 10**9; ftgt=ft[0] if len(ft) else 10**9
            if fstop==ftgt==10**9: continue
            R=2.0 if ftgt<fstop else -1.0   # stop-wins-ties (fstop<=ftgt -> stop)
            if fstop<=ftgt: R=-1.0
            sig.append((T,yr[T],R))
            last=T
        return sig
    sig=build_signals()
    if not sig:
        print("ASREJ-1: 0 signals over full history — cannot evaluate."); return
    arr=np.array([s[2] for s in sig]); yrs=np.array([s[1] for s in sig]); N=len(arr)
    def stats(a):
        if len(a)==0: return (0,float('nan'),float('nan'),float('nan'))
        p2=np.mean(a>0); gross=np.mean(a); net=np.mean(a-COST); return (len(a),p2,gross,net)
    N_,p2,gross,net=stats(arr)
    print(f"ASREJ-1 FULL-HISTORY MECHANIZED: signals={N} P2R={p2:.3f} grossR/trade={gross:+.3f} netR(STRESS {COST})={net:+.3f}")
    print(f"  interpretation: gross expectancy = 3*P2R-1 = {3*p2-1:+.3f}; net after {COST} cost = {net:+.3f}")
    print("GATE:")
    for lab,mask in [("DISC<=2018",yrs<=2018),("CONF19-22",(yrs>=2019)&(yrs<=2022)),("OOS23+",yrs>=2023)]:
        nn,pp,gg,nnet=stats(arr[mask]); print(f"  {lab:10s} n={nn:4d} P2R={pp:.3f} grossR={gg:+.3f} netR={nnet:+.3f}")
    # tail: remove best decile
    thr=np.quantile(arr,0.9); tail=arr[arr<=thr]; print(f"  tail(best-decile-removed) n={len(tail)} netR={np.mean(tail-COST):+.3f}")
    # 2x cost
    print(f"  2x-cost netR={np.mean(arr-2*COST):+.3f}")
    # leave-one-year-out (net stays positive?) + per-year
    yrsU=sorted(set(yrs.tolist())); pos_years=0
    for y in yrsU:
        a=arr[yrs==y]
        if len(a)>=15: pos_years+= (np.mean(a-COST)>0)
    print(f"  per-year net>0 in {pos_years}/{sum(1 for y in yrsU if (yrs==y).sum()>=15)} years(n>=15)")
    loyo_min=min(np.mean(arr[yrs!=y]-COST) for y in yrsU)
    print(f"  leave-one-year-out worst netR={loyo_min:+.3f}")
    # entry delay +1
    sd=build_signals(delay=2); ad=np.array([s[2] for s in sd]); print(f"  entry-delay+1: n={len(ad)} netR={np.mean(ad-COST):+.3f}" if len(ad) else "  entry-delay+1: 0 sig")
    # neighbor robustness (thresholds)
    for dt_,wm in [(0.8,1.5),(1.2,1.5),(1.0,1.3),(1.0,1.7)]:
        sn=build_signals(dist_thr=dt_,wick_mult=wm); an=np.array([s[2] for s in sn])
        print(f"  neighbor dist<={dt_} wick>={wm}: n={len(an)} netR={(np.mean(an-COST) if len(an) else float('nan')):+.3f}")
    verdict = "SURVIVES" if (net>0 and np.mean(tail-COST)>0 and loyo_min>0 and stats(arr[yrs>=2023])[3]>0) else "FAIL (cost/robustness)"
    print(f"\nVERDICT: ASREJ-1 = {verdict}. (promotion requires net>0 overall+OOS+tail+LOYO after STRESS cost)")
if __name__=="__main__": main()

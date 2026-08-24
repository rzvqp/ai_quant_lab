"""n_cache.py — precompute canonical N1 (regime/H4) + N2 (bias/H1) over full history, causally, mapped to M15. Cache -> npz.
Consumed by bfsd2 engine so canonical N1/N2 are available per-candle without recompute. Causal: each HTF bar classified from
bars <= it (bounded window); mapped to M15 by complete_at<=T (forward-fill). N3(M15)/N4(M5) handled live in the engine."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
import regime_classifier as RC, bias_h1 as BH
def resample(tsec,o,h,l,c,period):
    b=(tsec//period)*period
    df=pd.DataFrame({"b":b,"o":o,"h":h,"l":l,"c":c,"i":np.arange(len(tsec))})
    g=df.groupby("b",sort=True)
    return (g["o"].first().to_numpy(),g["h"].max().to_numpy(),g["l"].min().to_numpy(),g["c"].last().to_numpy(),g["i"].last().to_numpy())
def axlabel(ax):
    try:
        v=getattr(ax,'value',None)
        return v.label if v is not None and hasattr(v,'label') else "na"
    except Exception: return "na"
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); tsec=m["time"].to_numpy(); n=len(m)
    O4,H4,L4,C4,CA4=resample(tsec,o,h,l,c,14400); O1,H1,L1,C1,CA1=resample(tsec,o,h,l,c,3600)
    # N1 per H4 bar
    N4=len(C4); vol=np.empty(N4,object); stru=np.empty(N4,object); dire=np.empty(N4,object); axesst=[]
    W=200
    for k in range(N4):
        s=max(0,k-W+1)
        reg=RC.classify_regime(O4[s:k+1],H4[s:k+1],L4[s:k+1],C4[s:k+1])
        rv=getattr(reg,'value',None)
        if rv is not None:
            vol[k]=axlabel(rv.volatility); stru[k]=axlabel(rv.structure); dire[k]=axlabel(rv.direction)
            axesst.append(["available" if hasattr(a,'value') and getattr(a,'value',None) is not None else "unavailable" for a in (rv.volatility,rv.structure,rv.direction)])
        else:
            vol[k]=stru[k]=dire[k]="na"; axesst.append(["unavailable"]*3)
    # map H4->M15 by complete_at
    def mapm(arr,CA):
        out=np.empty(n,object); k=0; cal=list(CA)
        for T in range(n):
            while k+1<len(cal) and cal[k+1]<=T: k+=1
            out[T]=arr[k] if cal[k]<=T else "na"
        return out
    m_vol=mapm(vol,CA4); m_stru=mapm(stru,CA4); m_dire=mapm(dire,CA4)
    # H4 axes-status per H1 bar (needed by compute_bias): map H4 axes to H1 by time
    # approximate: for each H1 bar, find last H4 bar completed at or before it
    h1_axes=[]; k=0
    for kk in range(len(C1)):
        t_h1_close=CA1[kk]
        while k+1<len(CA4) and CA4[k+1]<=t_h1_close: k+=1
        h1_axes.append(axesst[k] if CA4[k]<=t_h1_close else ["unavailable"]*3)
    # N2 per H1 bar
    N1=len(C1); bdir=np.empty(N1,object); bmag=np.zeros(N1)
    Wb=300
    for k in range(N1):
        s=max(0,k-Wb+1); arrO=O1[s:k+1]; arrH=H1[s:k+1]; arrL=L1[s:k+1]; arrC=C1[s:k+1]
        try:
            bias=BH.compute_bias(arrO,arrH,arrL,arrC,len(arrC),regime_axes_status=h1_axes[k])
            bv=getattr(bias,'value',None); d="na"; mg=0.0
            if bv is not None:
                for f in bv.factors:
                    fv=getattr(f,'value',None)
                    if fv is not None and getattr(fv,'name','')=='structure_run_h1':
                        d=fv.direction.value if hasattr(fv.direction,'value') else str(fv.direction)
                        rw=getattr(fv,'raw',None); mg=float(getattr(rw,'value',0.0) or 0.0)
            bdir[k]=d; bmag[k]=mg
        except Exception:
            bdir[k]="na"; bmag[k]=0.0
    m_bdir=mapm(bdir,CA1)
    # bmag map (numeric)
    def mapmf(arr,CA):
        out=np.zeros(n); k=0; cal=list(CA)
        for T in range(n):
            while k+1<len(cal) and cal[k+1]<=T: k+=1
            out[T]=arr[k] if cal[k]<=T else 0.0
        return out
    m_bmag=mapmf(bmag,CA1)
    outp=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\n_cache.npz"
    np.savez_compressed(outp, vol=m_vol.astype(str), stru=m_stru.astype(str), dire=m_dire.astype(str),
                        bdir=m_bdir.astype(str), bmag=m_bmag)
    from collections import Counter
    print(f"n_cache: M15 rows={n}. N1 vol labels={dict(Counter(m_vol[300::500]))}")
    print(f"  N1 dir labels={dict(Counter(m_dire[300::500]))} | N2 bias dir={dict(Counter(m_bdir[300::500]))}")
    print(f"  wrote {outp}")
if __name__=="__main__": main()

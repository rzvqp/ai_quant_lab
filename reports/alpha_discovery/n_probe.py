"""n_probe.py — verify canonical N1/N2/N3 compute causally on cut arrays at sample anchors (N1-N6 presence check)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
import regime_classifier as RC, bias_h1 as BH, zone_map as ZM
from market_state import atr14
def resample_upto(tsec,o,h,l,c,period,as_of):
    mask=tsec<=tsec[as_of]; b=(tsec[mask]//period)*period
    df=pd.DataFrame({"b":b,"o":o[mask],"h":h[mask],"l":l[mask],"c":c[mask]})
    g=df.groupby("b",sort=True)
    return (g["o"].first().to_numpy(),g["h"].max().to_numpy(),g["l"].min().to_numpy(),g["c"].last().to_numpy(),
            np.array(sorted(df["b"].unique())))
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); tsec=m["time"].to_numpy(); n=len(m)
    for as_of in [50000, 150000, 300000]:
        O4,H4,L4,C4,T4=resample_upto(tsec,o,h,l,c,14400,as_of)
        O1,H1,L1,C1,T1=resample_upto(tsec,o,h,l,c,3600,as_of)
        # cut M15 to <= as_of
        o15,h15,l15,c15,t15=o[:as_of+1],h[:as_of+1],l[:as_of+1],c[:as_of+1],tsec[:as_of+1]
        reg=RC.classify_regime(O4[-200:],H4[-200:],L4[-200:],C4[-200:])
        axes=["available" if getattr(reg,'value',None) is not None else "unavailable"]*3
        try:
            rs=reg.value; axes=["available" if hasattr(ax,'value') else "unavailable" for ax in (rs.volatility,rs.structure,rs.direction)]
        except Exception: pass
        bias=BH.compute_bias(O1[-300:],H1[-300:],L1[-300:],C1[-300:],len(C1[-300:]),regime_axes_status=axes)
        from market_state import atr14
        a15=atr14(list(h15[-400:]),list(l15[-400:]),list(c15[-400:]))
        zones=ZM.build_zone_map(list(h15[-400:]),list(l15[-400:]),list(c15[-400:]),list(o15[-400:]),list(t15[-400:]),
                                atr=a15, regime_available=hasattr(reg,'value'), bias_available=hasattr(bias,'value'))
        print(f"as_of={as_of} dt={m['dt'].iloc[as_of]}")
        print("  N1 regime:", type(reg).__name__, repr(getattr(reg,'value',getattr(reg,'reason','?')))[:180])
        print("  N2 bias  :", type(bias).__name__, repr(getattr(bias,'value',getattr(bias,'reason','?')))[:180])
        zv=getattr(zones,'value',None)
        print("  N3 zones :", type(zones).__name__, (f"n_zones={len(zv.zones)}" if zv is not None else getattr(zones,'reason','?')))
if __name__=="__main__": main()

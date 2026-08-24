"""xscale_rangepos.py — Frontier F: CROSS-SCALE range-position (genuinely-new causal cross-scale, NOT CRS-1). Where does M15
price sit within the last FULLY-CLOSED H4 bar's range? pos=(close-H4low)/(H4high-H4low) in [0,1]. Bottom (oversold within H4)
-> bounce LONG? Top -> fade SHORT? Info-first: forward up-dn per position bucket. Causal H4 via merge_asof-backward on close_time
(the safe convention). No like_at. Data thru 2026-07-27."""
import numpy as np, pandas as pd
import cur_data as CD
import gate
H=96
def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4")
    hm=pd.DataFrame({"close_time":h4["close_time"].to_numpy(),"hi":h4["high"].to_numpy(),"lo":h4["low"].to_numpy()}).sort_values("close_time")
    mm=pd.DataFrame({"time":m["time"].to_numpy()}).sort_values("time")
    j=pd.merge_asof(mm,hm,left_on="time",right_on="close_time",direction="backward").sort_index()
    hi=j["hi"].to_numpy(); lo=j["lo"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy()
    pos=(c-lo)/np.where(hi-lo>0,hi-lo,np.nan)
    fmax=pd.Series(m["high"].to_numpy()).rolling(H).max().shift(-H).to_numpy(); fmin=pd.Series(m["low"].to_numpy()).rolling(H).min().shift(-H).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)&(atr>0)&np.isfinite(pos)
    print("FRONTIER F: M15 position within last-closed H4 range -> forward up-dn.")
    def row(msk):
        nn=int(msk.sum())
        if nn<300: return f"n={nn}(thin)"
        return f"n={nn:6d} up-dn={np.nanmedian(up[msk])-np.nanmedian(dn[msk]):+.2f}"
    for lab,pm in [("bottom(<0.2)",pos<0.2),("mid(0.4-0.6)",(pos>=0.4)&(pos<=0.6)),("top(>0.8)",pos>0.8)]:
        line=f"  {lab:14s}: {row(ok&pm)}"
        for pl,ym in [("D",yr<=2021),("C",(yr>=2022)&(yr<=2024)),("O",yr>=2025)]: line+=f" | {pl} {row(ok&pm&ym)}"
        print(line)
    print("  tradeable: bottom->LONG (bounce), top->SHORT (fade):")
    gate.screen(m, np.where(ok&(pos<0.2))[0], 1, atr, "H4-bottom LONG ")
    gate.screen(m, np.where(ok&(pos>0.8))[0], -1, atr, "H4-top    SHORT")
if __name__=="__main__": main()

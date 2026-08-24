"""multi_tf.py — Frontier G: MULTI-TF momentum confluence (causal). H4-up & H1-up & M15-up (triple-scale aligned) -> LONG
continuation; all-down -> SHORT. Causal HTF via merge_asof-backward on close_time. Info + gate. Expect era-split (confluence
= strong trend = era-trend). No like_at. Data thru 2026-07-27."""
import numpy as np, pandas as pd
import cur_data as CD
import gate
def tfup(m, tf):
    x=CD.agg(m,tf); up=(x["ema20"].to_numpy()>x["ema50"].to_numpy()).astype(float)
    hm=pd.DataFrame({"close_time":x["close_time"].to_numpy(),"up":up}).sort_values("close_time")
    mm=pd.DataFrame({"time":m["time"].to_numpy()}).sort_values("time")
    return pd.merge_asof(mm,hm,left_on="time",right_on="close_time",direction="backward").sort_index()["up"].to_numpy()
def main():
    m=CD.load_m15(); atr=m["atr"].to_numpy(); c=m["close"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy()
    h4=tfup(m,"H4"); h1=tfup(m,"H1"); m15=(m["ema20"].to_numpy()>m["ema50"].to_numpy()).astype(float)
    allup=(h4==1)&(h1==1)&(m15==1); alldn=(h4==0)&(h1==0)&(m15==0); ok=np.isfinite(atr)&(atr>0)
    H=96; fmax=pd.Series(h).rolling(H).max().shift(-H).to_numpy(); fmin=pd.Series(l).rolling(H).min().shift(-H).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy(); ok2=ok&np.isfinite(up)&np.isfinite(dn)
    def row(msk):
        nn=int(msk.sum())
        return f"n={nn:6d} up-dn={np.nanmedian(up[msk])-np.nanmedian(dn[msk]):+.2f}" if nn>=300 else f"n={nn}(thin)"
    print("FRONTIER G: triple-TF confluence. up-dn (all-up), dn-up (all-down):")
    print("  ALL-UP :", row(allup&ok2), "| D", row(allup&ok2&(yr<=2021)), "| C", row(allup&ok2&((yr>=2022)&(yr<=2024))), "| O", row(allup&ok2&(yr>=2025)))
    gate.screen(m, np.where(allup&ok)[0], 1, atr, "ALL-UP  LONG ")
    gate.screen(m, np.where(alldn&ok)[0], -1, atr, "ALL-DOWN SHORT")
if __name__=="__main__": main()

"""frontier_o.py — FRONTIER O: intraday SESSION DRIFT. Does any session carry a cross-era-stable open-to-close
directional drift (an intraday session bias independent of the daily trend)? S5 works long even in the b0 bear ->
maybe an intraday NY-long session bias. Measure per-session (Asia/London/NY) open-to-close return (pips) per era:
median, P(>0), and mean/atr. Cross-era same-sign material drift = a genuine session bias. Info-first, causal.
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _hr_day
SESS=[("Asia",0,7),("London",7,13),("NYopen",13,15),("NY",15,21)]
PIP=0.10

def main():
    print("Frontier O SESSION DRIFT: open-to-close return per session per era (pips). Cross-era-stable bias?")
    eras=bs.build_eras()
    for nm,lo,hi in SESS:
        print(f"\n  {nm} ({lo}-{hi} UTC):")
        for tag,fr,mask in eras:
            hr,day,_=_hr_day(fr); o=fr["open"].to_numpy(); c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy()
            insess=mask&(hr>=lo)&(hr<hi)
            df=pd.DataFrame({"day":day[insess],"o":o[insess],"c":c[insess],"atr":atr[insess]})
            if len(df)<200: print(f"    {tag}: thin"); continue
            g=df.groupby("day").agg(so=("o","first"),sc=("c","last"),atr=("atr","first"))
            ret=(g["sc"]-g["so"]); retp=ret/PIP; retn=ret/g["atr"]
            print(f"    {tag}: nDays={len(g)} medRet={retp.median():+.1f}p meanRet={retp.mean():+.1f}p P(>0)={float((ret>0).mean()):.2f} mean/atr={retn.mean():+.2f}")

if __name__=="__main__":
    main()

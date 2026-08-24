"""seasonality.py — Frontier H: CALENDAR seasonality (info-first, genuinely-untested class). Does any day-of-week or UTC-hour
carry a ROBUST cross-era directional lean? Info-only (per-bucket forward 96-bar return in ATR, partitioned). If a bucket is
cross-era-stable directional -> worth a tradeable test; else calendar has no generalizable directional edge. No like_at."""
import numpy as np, pandas as pd
import cur_data as CD
def main():
    m=CD.load_m15(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy()
    fret=(pd.Series(c).shift(-96).to_numpy()-c)/atr; yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(fret)&(atr>0)
    dow=m["dt"].dt.dayofweek.to_numpy(); hr=m["dt"].dt.hour.to_numpy()
    def med(msk): 
        nn=int(msk.sum()); return f"{np.nanmedian(fret[msk]):+.2f}({nn})" if nn>=200 else f"thin"
    print("FRONTIER H: day-of-week forward 96-bar return (ATR) by partition [ALL | D | C | O]:")
    for d in range(7):
        dm=ok&(dow==d)
        print(f"  dow{d}: {med(dm)} | {med(dm&(yr<=2021))} | {med(dm&((yr>=2022)&(yr<=2024)))} | {med(dm&(yr>=2025))}")
    print("  UTC-hour forward return (looking for cross-era-stable directional hour):")
    best=[]
    for hh in range(24):
        hm=ok&(hr==hh); a=np.nanmedian(fret[hm]); d=np.nanmedian(fret[hm&(yr<=2021)]); cc=np.nanmedian(fret[hm&((yr>=2022)&(yr<=2024))]); o=np.nanmedian(fret[hm&(yr>=2025)])
        if np.isfinite(d) and np.isfinite(cc) and np.isfinite(o) and (min(d,cc,o)>0.1 or max(d,cc,o)<-0.1): best.append((hh,a,d,cc,o))
    if best:
        for hh,a,d,cc,o in best: print(f"    hr{hh}: ALL {a:+.2f} D {d:+.2f} C {cc:+.2f} O {o:+.2f} (cross-era-stable sign)")
    else: print("    NONE: no UTC hour has a cross-era-stable directional lean (all era-split or ~0).")
if __name__=="__main__": main()

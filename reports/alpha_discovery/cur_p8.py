"""cur_p8.py — CONFIRMED_DOWNTREND regime short (economically principled = R4 trend-aligned continuation; the current
market IS a confirmed downtrend). Distinct regime hypothesis from the high-vol-correction signature. Regime = close <
20-day MA AND the 20-day MA is declining (sustained causal downtrend). Wide-stop (4 ATR) time-exit short. Test per-YEAR
+ TAIL (best-10%-removed) to see if it is robust across independent downtrend episodes or still crash-tail-carried.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
MA=1920; SLP=480  # 20-day MA (1920 M15), decline over 5 days (480 M15)

def downtrend_short(m):
    c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    ma=pd.Series(c).rolling(MA).mean().shift(1).to_numpy(); madecl=ma< pd.Series(ma).shift(SLP).to_numpy()
    dt=(c<ma)&madecl&np.isfinite(atr)&(atr>0)
    idx=np.where(dt)[0]; idx=idx[idx<n-1]; sl=4.0*atr[idx]
    return idx, sl, dt

def main():
    m=CD.load_m15(); idx,sl,dt=downtrend_short(m)
    o=np.argsort(idx); idx=idx[o]; sl=sl[o]; dd=sb.dedup_events(idx,24); p=np.isin(idx,dd); idx=idx[p]; sl=sl[p]
    tr=sb.simulate(m,idx,-1,sl,rr=3.0,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    print(f"CONFIRMED_DOWNTREND short (close<20dMA & MA declining), wide 4ATR rr3 H96, STRESS.")
    print(f"  regime coverage: {100*dt.mean():.1f}% of bars | trades N={len(r)} avgR={r.mean():+.3f} PF={sb._pf(r):.2f} WR={(r>0).mean():.2f}")
    print("  per-year:", {int(y):(round(float(r[yr==y].mean()),3),int((yr==y).sum())) for y in sorted(set(yr))})
    sr=np.sort(r); k1=max(1,len(r)//100); k10=max(1,len(r)//10)
    print(f"  best-1%-removed={sr[:-k1].mean():+.3f}  best-10%-removed={sr[:-k10].mean():+.3f}")
    # partition by independent downtrend episodes (year groups)
    early=r[yr<=2016]; mid=r[(yr>=2017)&(yr<=2022)]; late=r[yr>=2023]
    print(f"  episodes: <=2016 {early.mean():+.3f}(n{len(early)}) | 2017-2022 {mid.mean():+.3f}(n{len(mid)}) | 2023+ {late.mean():+.3f}(n{len(late)})")

if __name__=="__main__":
    main()

"""cur_cr13_robust.py — ROBUSTNESS PROBE for CRS-1 (does NOT modify/retune the frozen edge). Attacks the limitation flagged
to the Red Team: CRS-1's activation uses the CURRENT_XAUUSD_MARKET_SIGNATURE_V1 'current-like' label, which uses a global
percentile (mild in-sample normalization). Question: does the SAME entry mechanism (H4-trend-UP counter-trend bounce ->
M15 short) survive when the regime is defined LABEL-FREE — no SIGNATURE_V1 at all, just a plain causal structural proxy for
'high-vol down-correction'? If yes, CRS-1 does not depend on the specific label (stronger). If no, the label is load-bearing
(a real fragility). PURELY a robustness check — CRS-1 stays frozen; NO re-freezing to whatever scores better here.

Label-free regime (independent of SIGNATURE_V1): H4 ema50 sloping DOWN (ema50 < ema50[20 bars ago]) AND H4 atr/atr_ma > 1.0
(elevated vol). Bounce = H4 ema20>ema50 (short-term up within the macro down). Entry M15 short, 1.5ATR/rr2/H96/STRESS/dedup16.
Ratified sb.simulate. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from cur_screen import like_at

def labelfree_state(m):
    h4=CD.agg(m,"H4"); e20=h4["ema20"].to_numpy(); e50=h4["ema50"].to_numpy()
    vr=(h4["atr"]/h4["atr_ma"]).to_numpy()
    macro_down=e50<pd.Series(e50).shift(20).to_numpy()
    bounce=e20>e50
    state=macro_down & (vr>1.0) & bounce            # label-free 'high-vol down-correction & counter-trend bounce'
    hm=pd.DataFrame({"close_time":h4["close_time"].to_numpy(),"st":np.nan_to_num(state.astype(float),nan=0)}).sort_values("close_time")
    mm=pd.DataFrame({"time":m["time"].to_numpy()}).sort_values("time")
    j=pd.merge_asof(mm,hm,left_on="time",right_on="close_time",direction="backward").sort_index()
    return j["st"].to_numpy()

def run(m, mask, name):
    atr=m["atr"].to_numpy(); n=len(m)
    idx=np.where(mask&np.isfinite(atr)&(atr>0))[0]; idx=idx[idx<n-1]
    if len(idx)<40: print(f"  {name}: n={len(idx)} thin"); return
    dd=sb.dedup_events(idx,16); idx=idx[np.isin(idx,dd)]; sl=1.5*atr[idx]
    tr=sb.simulate(m,idx,-1,sl,rr=2.0,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  {name}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} best10%rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f}(n{len(d)}) C {cf.mean():+.3f}(n{len(cf)}) O {oos.mean():+.3f}(n{len(oos)}) -> {'HOLDS' if surv else 'weaker'}")

def main():
    m=CD.load_m15(); st=labelfree_state(m); t=m["time"].to_numpy(); cl=like_at(t)
    lf=st==1
    print("CRS-1 ROBUSTNESS PROBE: same entry (H4-up bounce -> M15 short) under a LABEL-FREE regime definition.")
    run(m, lf, "LABEL-FREE regime (no SIGNATURE_V1) ")
    run(m, lf&cl, "label-free AND current-like (overlap)")
    run(m, lf&(~cl), "label-free but NOT current-like    ")
    print("  (HOLDS on the label-free set => CRS-1 not dependent on the SIGNATURE_V1 global-percentile label.)")

if __name__=="__main__":
    main()

"""cur_info2.py — does a causal STATE robustly CONCENTRATE the current-like down-bias (info-first, not mining)? On
CURRENT_LIKE_POPULATION_V1, measure P(down 1.5ATR before up 1.5ATR) conditional on a small PRINCIPLED set of causal
states, per DISC/CONF/OOS partition. A state that robustly lifts the down-bias materially (>=0.55 all partitions) is
the foundation for a current-regime short specialist. No RR/threshold fitting. Data through 2026-07-27 (disclosed stale).
"""
import numpy as np, pandas as pd
import cur_data as CD
from cur_info import fp_order
from cur_screen import like_at

def main():
    m=CD.load_m15(); o=fp_order(m); t=m["time"].to_numpy(); cl=like_at(t); yr=m["dt"].dt.year.to_numpy(); valid=(o!=0)&cl
    c=m["close"].to_numpy(); h=m["high"].to_numpy(); atr=m["atr"].to_numpy(); e20=m["ema20"].to_numpy(); e50=m["ema50"].to_numpy()
    dnctx=e20<e50
    dnmom=c<pd.Series(c).shift(6).to_numpy()
    rh=pd.Series(h).rolling(20).max().shift(1).to_numpy(); atres=c>=(rh-0.3*atr)
    volexp=(atr/m["atr_ma"].to_numpy())>1.0
    states={"ALL current-like":np.ones(len(m),bool),"H4dn(ema20<50)":dnctx,"dn-mom(6bar)":dnmom,
            "at-resistance":atres,"vol-expansion":volexp,"dnctx&atres":dnctx&atres,"dnctx&dnmom":dnctx&dnmom}
    def pdown(msk):
        oo=o[msk]; return (int(msk.sum()), float((oo[oo!=0]==-1).mean()) if (oo!=0).sum() else float('nan'))
    print("P(down-first) | ALL-cur / DISC / CONF / OOS  (>=0.55 all = concentrated down-bias)")
    for nm,st in states.items():
        parts=[valid&st, valid&st&(yr<=2021), valid&st&(yr>=2022)&(yr<=2024), valid&st&(yr>=2025)]
        vals=[pdown(p) for p in parts]
        print(f"  {nm:16s}: " + "  ".join(f"{v[1]:.3f}(n{v[0]})" for v in vals))

if __name__=="__main__":
    main()

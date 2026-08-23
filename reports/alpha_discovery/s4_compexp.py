"""s4_compexp.py — S4 Volatility Compression->Expansion, §8 decomposition + §9 bilateral-vs-directional + §14
natural payoff. Mechanical COMPRESSION (range-box contraction + ATR ratio), DIRECTIONAL EXPANSION (close breaks
the compression envelope with range expansion), per frozen H4 mode. For each mode x expansion-direction report
BOTH long & short future-path lift (§9 separate bilateral vol-timing from directional alpha) + MFE/MAE (§14).
Cross-era, event-deduped. Frozen mode taxonomy. Causal, price-only.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from state_m15_discover import dedup
from market_mode import mode, MODES
from liquidity_event import align_mode
NB=8; COOL=8; H=32; LAB=(70,50)

def comp_exp(m):
    h=m["high"]; l=m["low"]; c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy()
    box_hi=h.rolling(NB).max().shift(1).to_numpy(); box_lo=l.rolling(NB).min().shift(1).to_numpy()
    box=box_hi-box_lo; box_ma=pd.Series(box).rolling(50).mean().shift(1).to_numpy()
    vr=atr/atr_ma
    comp=(box<0.7*box_ma)&(vr<0.9)&np.isfinite(box_ma)                 # compressed (envelope + ATR)
    comp_prev=pd.Series(comp).shift(1).fillna(False).to_numpy().astype(bool)
    rng=(h.to_numpy()-l.to_numpy())
    exp_up=comp_prev&(c>box_hi)&(rng>1.3*atr)                          # break above compression envelope w/ range expansion
    exp_dn=comp_prev&(c<box_lo)&(rng>1.3*atr)
    return np.nan_to_num(exp_up.astype(float),nan=0).astype(bool), np.nan_to_num(exp_dn.astype(float),nan=0).astype(bool), comp

def run_era(tag, m, h4, af, mask):
    regc,uniq=align_mode(m,h4,af); ou,od,mfe,mae=passage_m15(m); eu,ed,comp=comp_exp(m)
    print(f"\n[{tag}]")
    for md in MODES:
        if md not in uniq: continue
        code=uniq.index(md); modem=(regc==code)&mask
        if int(dedup(modem,COOL).sum())<40: continue
        bL=Pm(ou,od,LAB[0],LAB[1],'L',H,modem&dedup(modem,COOL))[0]; bS=Pm(ou,od,LAB[0],LAB[1],'S',H,modem&dedup(modem,COOL))[0]
        for ename,emask in (("EXP_UP",eu),("EXP_DN",ed)):
            cm=modem&emask; dd=cm&dedup(cm,COOL); nE=int(dd.sum())
            if nE<30: continue
            lL=Pm(ou,od,LAB[0],LAB[1],'L',H,dd)[0]-bL; lS=Pm(ou,od,LAB[0],LAB[1],'S',H,dd)[0]-bS
            idx=np.where(dd)[0]; kind="DIRECTIONAL" if abs(lL-lS)>=0.04 else ("BILATERAL" if (lL>0.03 and lS>0.03) else "weak")
            print(f"   {md[:12]:12s} {ename}: base L/S={bL:.2f}/{bS:.2f} liftL={lL:+.3f} liftS={lS:+.3f} [{kind}] (n{nE}) MFEmed={np.median(mfe[idx]):.0f}p MAEmed={np.median(mae[idx]):.0f}p")

def main():
    print(f"S4 COMPRESSION->EXPANSION decomposition. Directional expansion per mode; LONG & SHORT lift (bilateral vs directional) + MFE/MAE. P(+{LAB[0]}/-{LAB[1]}) {H//4}h, deduped.")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    run_era("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy())
    run_era("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy())
    for y in (2021,2022,2023): run_era(str(y),sm,sh4,sb.align_context,dev&(yr==y))

if __name__=="__main__":
    main()

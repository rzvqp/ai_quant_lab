"""displacement_info.py — S10 Displacement Continuation, §6 mandatory decomposition (information-first).
MODE base -> +DISPLACEMENT -> +DISPLACEMENT+ACCEPTANCE. Displacement = mechanical strong directional M15 bar
(body>0.7 ATR, close in far quartile, range>1.2 ATR). Direction aligned to frozen H4 mode; corrections measured
BOTH ways (primary-resume vs correction-continue). P(+70/-50) mode-dir lift vs SAME-mode base, per era, event-
deduped. Frozen MARKET_OPERATING_MODE_V1 (unmodified). Causal, price-only.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from state_m15_discover import dedup
from market_mode import mode
from liquidity_event import align_mode
COOL=8; H=32; LAB=(70,50)
# predeclared (mode, displacement-dir, trade-side, tag)
CELLS=[
 ("PRIMARY_BULL_IMPULSE",'up','L',"bull-disp->LONG"),
 ("PRIMARY_BEAR_IMPULSE",'dn','S',"bear-disp->SHORT"),
 ("BULL_CORRECTION",'up','L',"primary-resume LONG"),
 ("BULL_CORRECTION",'dn','S',"correction-continue SHORT"),
 ("BEAR_CORRECTION",'dn','S',"primary-resume SHORT"),
 ("BEAR_CORRECTION",'up','L',"correction-continue LONG"),
 ("NEUTRAL_ROTATION",'up','L',"neutral bull-disp LONG"),
 ("NEUTRAL_ROTATION",'dn','S',"neutral bear-disp SHORT"),
]

def disp(m):
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); o=m["open"].to_numpy(); atr=m["atr"].to_numpy()
    rng=np.maximum(h-l,1e-9)
    up=((c-o)>0.7*atr)&(c>l+0.75*rng)&(rng>1.2*atr)
    dn=((o-c)>0.7*atr)&(c<l+0.25*rng)&(rng>1.2*atr)
    return np.nan_to_num(up.astype(float),nan=0).astype(bool), np.nan_to_num(dn.astype(float),nan=0).astype(bool)

def run_era(tag, m, h4, af, mask):
    regc,uniq=align_mode(m,h4,af); ou,od,_,_=passage_m15(m); up,dn=disp(m)
    o=m["open"].to_numpy(); c=m["close"].to_numpy(); n=len(m)
    print(f"\n[{tag}]")
    for md,dd_dir,side,lab in CELLS:
        if md not in uniq: continue
        code=uniq.index(md); modem=(regc==code)&mask
        if int(dedup(modem,COOL).sum())<40: continue
        base=Pm(ou,od,LAB[0],LAB[1],side,H,modem&dedup(modem,COOL))[0]
        dmask=modem&(up if dd_dir=='up' else dn)
        dd=dmask&dedup(dmask,COOL); nD=int(dd.sum())
        if nD<30:
            print(f"   {md[:12]:12s} {lab:26s}: base={base:.2f} disp thin(n{nD})"); continue
        pdisp=Pm(ou,od,LAB[0],LAB[1],side,H,dd)[0]
        # acceptance: next bar holds beyond displacement origin (open of disp bar)
        di=np.where(dmask)[0]; di=di[di<n-1]
        if dd_dir=='up': acc=di[c[di+1]>o[di]]
        else:            acc=di[c[di+1]<o[di]]
        am=np.zeros(n,bool); am[acc+1]=True; am=am&modem  # decision at acceptance bar, still in mode
        aa=am&dedup(am,COOL); nA=int(aa.sum())
        pacc=Pm(ou,od,LAB[0],LAB[1],side,H,aa)[0] if nA>=30 else None
        pa=f"{pacc-base:+.3f}(n{nA})" if pacc is not None else f"na(n{nA})"
        print(f"   {md[:12]:12s} {lab:26s}: base={base:.2f} +disp={pdisp-base:+.3f}(n{nD}) +disp+accept={pa}")

def main():
    print(f"S10 DECOMPOSITION: MODE base -> +DISP -> +DISP+ACCEPT. P(+{LAB[0]}/-{LAB[1]}) {H//4}h mode-dir lift, deduped.")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    run_era("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy())
    run_era("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy())
    for y in (2021,2022,2023): run_era(str(y),sm,sh4,sb.align_context,dev&(yr==y))

if __name__=="__main__":
    main()

"""liquidity_event.py — FIRST structural-event family (§10-20): LIQUIDITY EVENT -> RECLAIM -> DISPLACEMENT ->
FUTURE PATH, M15 events conditioned on the FROZEN H4 market mode. Mandatory decomposition (§18):
MODE base -> +EVENT -> +EVENT+RECLAIM -> +EVENT+RECLAIM+DISPLACEMENT, to isolate which component changes the
XAUUSD future-path probability (§14). Direction separate (§15): sellside sweep -> LONG ; buyside sweep -> SHORT.
Causal, price-only, event-deduped (§20), cross-era within same mode (§17). Mechanical liquidity-event defs (§12).
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from state_m15_discover import dedup
from market_mode import mode, MODES
W=20; COOL=8; H=32   # swing lookback ~5h ; event-dedup ~2h ; outcome horizon 8h
LABEL=(70,50)

def events(m):
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); o=m["open"].to_numpy(); atr=m["atr"].to_numpy()
    swL=pd.Series(l).rolling(W).min().shift(1).to_numpy(); swH=pd.Series(h).rolling(W).max().shift(1).to_numpy()
    rng=np.maximum(h-l,1e-9)
    sell_ev=l<swL; sell_rc=sell_ev&(c>swL); disp_up=((c-o)/atr>0.5)&(c>(l+0.67*rng))
    buy_ev=h>swH; buy_rc=buy_ev&(c<swH); disp_dn=((o-c)/atr>0.5)&(c<(l+0.33*rng))
    return {"sell":(sell_ev, sell_rc, sell_rc&disp_up, 'L'), "buy":(buy_ev, buy_rc, buy_rc&disp_dn, 'S')}

def align_mode(m, h4, align_fn):
    labs=mode(h4); codes,uniq=pd.factorize(labs); h4=h4.copy(); h4["modec"]=codes.astype(float)
    a=align_fn(m,h4,["modec"],""); return a["modec"].to_numpy(), list(uniq)

def decomp(ou,od,mask,side,base_mask,ev,rc,dp):
    b=Pm(ou,od,LABEL[0],LABEL[1],side,H,base_mask)[0]
    def P(cond):
        mm=mask&np.nan_to_num(cond.astype(float),nan=0).astype(bool); dd=mm&dedup(mm,COOL); n=int(dd.sum())
        return (Pm(ou,od,LABEL[0],LABEL[1],side,H,dd)[0]-b, n) if n>=30 else (None,n)
    return b,P(ev),P(rc),P(dp)

def run_era(tag, m, h4, align_fn, mask):
    regc,uniq=align_mode(m,h4,align_fn); ou,od,_,_=passage_m15(m); E=events(m)
    print(f"\n[{tag}]")
    for md in MODES:
        if md not in uniq: continue
        code=uniq.index(md); mmask=mask&(regc==code)
        if int(dedup(mmask,COOL).sum())<40: continue
        for sk in ("sell","buy"):
            ev,rc,dp,side=E[sk]
            b,(le,ne),(lr,nr),(ld,nd)=decomp(ou,od,mmask,side,mmask&dedup(mmask,COOL),ev,rc,dp)
            if nd<30: continue
            fmt=lambda x:(f"{x:+.3f}" if x is not None else "na")
            print(f"   {md:20s} {sk}->{side}: base={b:.2f}  +evt={fmt(le)}(n{ne})  +rcl={fmt(lr)}(n{nr})  +disp={fmt(ld)}(n{nd})")

def main():
    print(f"LIQUIDITY EVENT family: decomposition MODE base -> +evt -> +rcl -> +disp. P(+{LABEL[0]}/-{LABEL[1]}) {H//4}h, dedup {COOL}. Directed side.")
    # b0/b1 : hist M15 + hist H4 (add close_time = open+4h for causal align)
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    for tag,col in (("b0","is_b0"),("b1","is_b1")):
        run_era(tag, hm, hh4, m15d.align_causal, hm[col].to_numpy())
    # 2021/2022/2023 : gated M15 + gated H4
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    for y in (2021,2022,2023):
        run_era(f"{y}", sm, sh4, sb.align_context, dev&(yr==y))

if __name__=="__main__":
    main()

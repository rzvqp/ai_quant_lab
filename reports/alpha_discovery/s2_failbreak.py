"""s2_failbreak.py — S2 Failed Breakout/Sweep, §9 mandatory decomposition (information-first). Structural level =
recent 20-bar swing high/low. §6 SEPARATE branches: WICK failure (penetrate high, close back inside = 1-bar; ~S1
overlap) vs CLOSE-BEYOND failure (close beyond, then next close loses the level = the NEW mechanism). Reversal
direction (§10): failed UPSIDE break -> SHORT ; failed DOWNSIDE break -> LONG. Decomposition per frozen H4 mode:
MODE base -> +BREAK -> +FAILED -> +FAILED+OPPOSITE-RESPONSE (opposite displacement). P(+70/-50 reversal-side)
lift vs same-mode base, per era, event-deduped. Causal (close-beyond failure observable only at next close).
Frozen mode taxonomy. Price-only.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from state_m15_discover import dedup
from market_mode import mode, MODES
from displacement_info import disp
from liquidity_event import align_mode
W=20; COOL=8; H=32; LAB=(70,50)

def levels(m):
    h=m["high"]; l=m["low"]
    return h.rolling(W).max().shift(1).to_numpy(), l.rolling(W).min().shift(1).to_numpy()

def events(m):
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); n=len(m)
    up,dn=levels(m); c1=pd.Series(c).shift(-1).to_numpy()  # next close (for close-beyond failure, decision at t+1)
    updn={}
    # UPSIDE break -> reversal SHORT
    brk_up = h>up
    wick_up = brk_up & (c<up)                       # A: closed back inside same bar (short at t)
    closeb_up = c>up                                # B: closed beyond
    closefail_up = closeb_up & (pd.Series(c).shift(-1).to_numpy()<up)  # lost next close (short decision at t+1)
    # DOWNSIDE break -> reversal LONG
    brk_dn = l<dn
    wick_dn = brk_dn & (c>dn)
    closeb_dn = c<dn
    closefail_dn = closeb_dn & (pd.Series(c).shift(-1).to_numpy()>dn)
    return dict(brk_up=brk_up,wick_up=wick_up,closefail_up=closefail_up,
                brk_dn=brk_dn,wick_dn=wick_dn,closefail_dn=closefail_dn)

def run_era(tag, m, h4, af, mask):
    regc,uniq=align_mode(m,h4,af); ou,od,_,_=passage_m15(m); E=events(m); up_d,dn_d=disp(m); n=len(m)
    print(f"\n[{tag}]")
    for md in MODES:
        if md not in uniq: continue
        code=uniq.index(md); modem=(regc==code)&mask
        if int(dedup(modem,COOL).sum())<40: continue
        for brk,wick,cf,side,oppdisp,lab in (
            ("brk_up","wick_up","closefail_up",'S',dn_d,"UPbreak->SHORT"),
            ("brk_dn","wick_dn","closefail_dn",'L',up_d,"DNbreak->LONG")):
            base=Pm(ou,od,LAB[0],LAB[1],side,H,modem&dedup(modem,COOL))[0]
            def P(condmask, shift=0):
                cm=condmask.copy()
                if shift:
                    idx=np.where(cm)[0]; idx=idx[idx+shift<n]; cm=np.zeros(n,bool); cm[idx+shift]=True
                cm=modem&np.nan_to_num(cm.astype(float),nan=0).astype(bool); dd=cm&dedup(cm,COOL); nn=int(dd.sum())
                return (Pm(ou,od,LAB[0],LAB[1],side,H,dd)[0]-base, nn) if nn>=30 else (None,nn)
            lb,nb=P(E[brk]); lw,nw=P(E[wick]); lc,nc=P(E[cf],shift=1)  # close-beyond failure decision at t+1
            # opposite response: close-beyond failure at t, with an opposite displacement at t+1 (decision t+1)
            od_=np.nan_to_num(oppdisp.astype(float),nan=0).astype(bool)
            cfi=np.where(E[cf])[0]; cfi=cfi[cfi+1<n]; oppdec=cfi[od_[cfi+1]]
            oc=np.zeros(n,bool); oc[oppdec]=True; lo,no=P(oc,shift=1)
            f=lambda x:(f"{x:+.3f}" if x is not None else "na")
            print(f"   {md[:11]:11s} {lab:14s}: base={base:.2f} +break={f(lb)}(n{nb}) +WICKfail={f(lw)}(n{nw}) +CLOSEfail={f(lc)}(n{nc}) +CLOSEfail+opp={f(lo)}(n{no})")

def main():
    print(f"S2 §9 DECOMPOSITION: MODE base -> +break -> +WICKfail(~S1) -> +CLOSEfail(NEW) -> +CLOSEfail+opp. P(+{LAB[0]}/-{LAB[1]}) reversal-side lift, deduped.")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    run_era("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy())
    run_era("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy())
    for y in (2021,2022,2023): run_era(str(y),sm,sh4,sb.align_context,dev&(yr==y))

if __name__=="__main__":
    main()

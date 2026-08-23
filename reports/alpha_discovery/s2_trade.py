"""s2_trade.py — S2 tradeability (§17/§18/§19) of the failed-break + opposite-displacement reversal cells.
Event: CLOSE-beyond break fails (close beyond level at t, next close t+1 loses it) + opposite displacement at t+1;
decision = t+1; entry = open[t+2] (strict next-bar, §19). STRUCTURAL stop = break extreme (max high[t..t+1] for
an up-break / min low for a down-break; breach invalidates the failed-break thesis). Reversal side. Net STRESS
per mode x era, small predeclared rr. Frozen mode taxonomy. Causal, event-deduped.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_m15_discover import dedup
from market_mode import mode, MODES
from displacement_info import disp
from liquidity_event import align_mode
W=20; COOL=8; H=32

def sig_events(m, side):  # side 'S' = failed UP-break->short ; 'L' = failed DN-break->long
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); n=len(m)
    up=pd.Series(m["high"]).rolling(W).max().shift(1).to_numpy(); dn=pd.Series(m["low"]).rolling(W).min().shift(1).to_numpy()
    up_d,dn_d=disp(m); c1=pd.Series(c).shift(-1).to_numpy()
    dec=[]; stp=[]
    for t in range(n-2):
        if side=='S':
            if not (c[t]>up[t] and c1[t]<up[t]): continue      # close-beyond then lose next close
            if not dn_d[t+1]: continue                          # opposite (bearish) displacement at t+1
            dec.append(t+1); stp.append(max(h[t],h[t+1]))       # structural stop = break high
        else:
            if not (c[t]<dn[t] and c1[t]>dn[t]): continue
            if not up_d[t+1]: continue
            dec.append(t+1); stp.append(min(l[t],l[t+1]))
    return np.array(dec,dtype=int), np.array(stp,dtype=float)

def run_era(tag, m, h4, af, mask):
    regc,uniq=align_mode(m,h4,af); o=m["open"].to_numpy(); n=len(m)
    print(f"\n[{tag}]")
    for side,side_num,lab in (('S',-1,"failedUP->SHORT"),('L',1,"failedDN->LONG")):
        dec,stp=sig_events(m,side)
        for md in MODES:
            if md not in uniq: continue
            code=uniq.index(md); modem=(regc==code)&mask
            keep=np.zeros(n,bool); keep[dec]=True; cellmask=keep&modem
            ded=dedup(cellmask,COOL)                     # event-dedup
            cell2=np.where(cellmask&ded)[0]; cell2=cell2[cell2<n-1]
            if len(cell2)<25: continue
            pos={d:s for d,s in zip(dec,stp)}; st=np.array([pos[d] for d in cell2])
            entry=o[cell2+1]; sl=np.abs(entry-st); ok=np.isfinite(sl)&(sl>0); cell2=cell2[ok]; sl=sl[ok]
            best=[]
            for rr in (1.0,1.5,2.0):
                tr=sb.simulate(m, cell2, side_num, sl, rr=rr, horizon=H, scenario="STRESS")
                if len(tr): mm=sb.metrics(tr,m,rr); best.append(f"rr{rr}:{mm['avgR']:+.3f}")
            print(f"   {md[:11]:11s} {lab:15s}: events={len(cell2)} medSL={np.median(sl)/0.10:.0f}p {' '.join(best)}")

def _mk(n,idx):
    x=np.zeros(n,bool); x[idx]=True; return x

def main():
    print(f"S2 TRADEABILITY (failed-break+opp displacement, strict next-bar entry, structural stop=break extreme, STRESS). H={H//4}h.")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    run_era("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy())
    run_era("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy())
    for y in (2021,2022,2023): run_era(str(y),sm,sh4,sb.align_context,dev&(yr==y))

if __name__=="__main__":
    main()

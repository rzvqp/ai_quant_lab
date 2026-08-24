"""s4_verify.py — §26/§28 ADVERSARIAL verification of S4 correction-resumption candidates C3/C4.
C3 = BULL_CORRECTION + compression + bullish expansion + HOLD -> LONG (primary resume).
C4 = BEAR_CORRECTION + compression + bearish expansion + HOLD -> SHORT (primary resume).
Checks: per-era (b0/b1/pooled DEV 2021-2023) avgR + DISC/CONF + unique days + session distribution;
PARAMETER-NEIGHBOR stability (compression threshold 0.65/0.70/0.75); redundancy vs COMP-CONT-L (day overlap).
Strict sb.simulate (next-bar entry, stop-first). Structural stop = compression origin. Frozen mode taxonomy.
"""
import numpy as np, pandas as pd, os, json
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_m15_discover import dedup
from market_mode import mode
from liquidity_event import align_mode
NB=8; COOL=8; H=32

def events(m, side, ct):  # side 1 (bull-exp up in BULL_CORR) / -1 (bear-exp dn in BEAR_CORR); ct=comp threshold
    h=m["high"]; l=m["low"]; c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m)
    box_hi=h.rolling(NB).max().shift(1).to_numpy(); box_lo=l.rolling(NB).min().shift(1).to_numpy()
    box=box_hi-box_lo; box_ma=pd.Series(box).rolling(50).mean().shift(1).to_numpy(); vr=atr/atr_ma
    comp=(box<ct*box_ma)&(vr<0.9)&np.isfinite(box_ma); cp=pd.Series(comp).shift(1).fillna(False).to_numpy().astype(bool)
    rng=(h.to_numpy()-l.to_numpy()); c1=pd.Series(c).shift(-1).to_numpy()
    if side==1: ev=cp&(c>box_hi)&(rng>1.3*atr); hold=c1>box_hi; stoplvl=box_lo
    else:       ev=cp&(c<box_lo)&(rng>1.3*atr); hold=c1<box_lo; stoplvl=box_hi
    ev=np.nan_to_num(ev.astype(float),nan=0).astype(bool)
    return ev, np.nan_to_num(hold.astype(float),nan=0).astype(bool), stoplvl

def trade(m, sig, side, sl):
    tr=sb.simulate(m, sig, side, sl, rr=1.5, horizon=H, scenario="STRESS")
    return sb.metrics(tr,m,1.5), tr

def run_cell(name, md, side, frames):
    print(f"\n===== {name}: {md} side={side} =====")
    for tag,m,h4,af,mask in frames:
        regc,uniq=align_mode(m,h4,af)
        if md not in uniq: continue
        code=uniq.index(md); modem=(regc==code)&mask; o=m["open"].to_numpy(); n=len(m)
        # neighbor stability across compression thresholds
        line=f"  [{tag}] "
        base_sig=None; base_sl=None; base_tr=None
        for ct in (0.65,0.70,0.75):
            ev,hold,stoplvl=events(m,side,ct); cm=modem&ev; di=np.where(cm&dedup(cm,COOL))[0]; di=di[di<n-1]
            di=di[hold[di]]                        # HOLD-confirmed
            if len(di)<20: line+=f"ct{ct}:n{len(di)}(thin) "; continue
            entry=o[di+1]; sl=np.abs(entry-stoplvl[di]); ok=np.isfinite(sl)&(sl>0); di=di[ok]; sl=sl[ok]
            mm,tr=trade(m,di,side,sl); line+=f"ct{ct}:avgR{mm['avgR']:+.3f}(n{len(di)}) "
            if ct==0.70: base_sig,base_sl,base_tr=di,sl,tr
        print(line)
        if base_tr is not None and len(base_tr):
            te=pd.to_datetime(base_tr["t_entry"],unit="s",utc=True); r=base_tr["R"].to_numpy(); cut=int(len(r)*0.6)
            days=len(set(te.dt.floor('D'))); hrs=te.dt.hour.to_numpy()
            sess={"Asia":int(((hrs>=0)&(hrs<7)).sum()),"Lon":int(((hrs>=7)&(hrs<13)).sum()),"NY":int(((hrs>=13)&(hrs<21)).sum()),"Off":int((hrs>=21).sum())}
            print(f"       DISC={r[:cut].mean():+.3f} CONF={r[cut:].mean():+.3f} uniqueDays={days} sessions={sess}")

def main():
    print("S4 ADVERSARIAL VERIFICATION of C3 (BULL_CORR->L) / C4 (BEAR_CORR->S). rr1.5, structural stop=compression origin, STRESS.")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; dev=sm["is_dev"].to_numpy()
    frames=[("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy()),("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy()),
            ("y2123",sm,sh4,sb.align_context,dev)]
    run_cell("C3", "BULL_CORRECTION", 1, frames)
    run_cell("C4", "BEAR_CORRECTION", -1, frames)

if __name__=="__main__":
    main()

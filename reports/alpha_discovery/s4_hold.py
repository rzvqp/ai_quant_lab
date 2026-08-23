"""s4_hold.py — S4 HOLD/FAIL (§12) + larger payoff (§13) + tradeability (§18-20). Mode-aligned directional
expansion: PRIMARY_BULL EXP_UP->LONG ; PRIMARY_BEAR EXP_DN->SHORT ; correction resolutions. HOLD = next close
stays beyond compression envelope; FAIL = returns inside. Compare HOLD vs FAIL continuation P. Tradeability:
HOLD-confirmed, entry = bar after hold (strict), STRUCTURAL stop = compression origin (box_lo long / box_hi short),
net STRESS. Frozen mode taxonomy. Causal, event-deduped.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from state_m15_discover import dedup
from market_mode import mode
from liquidity_event import align_mode
NB=8; COOL=8; H=32
CELLS=[("PRIMARY_BULL_IMPULSE",'up',1,"C1"),("PRIMARY_BEAR_IMPULSE",'dn',-1,"C2"),
       ("BULL_CORRECTION",'up',1,"C3 resume"),("BEAR_CORRECTION",'dn',-1,"C4 resume")]

def env(m):
    h=m["high"]; l=m["low"]; atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy()
    box_hi=h.rolling(NB).max().shift(1).to_numpy(); box_lo=l.rolling(NB).min().shift(1).to_numpy()
    box=box_hi-box_lo; box_ma=pd.Series(box).rolling(50).mean().shift(1).to_numpy(); vr=atr/atr_ma
    comp=(box<0.7*box_ma)&(vr<0.9)&np.isfinite(box_ma); comp_prev=pd.Series(comp).shift(1).fillna(False).to_numpy().astype(bool)
    rng=(h.to_numpy()-l.to_numpy())
    return box_hi,box_lo,comp_prev,rng

def run_era(tag, m, h4, af, mask):
    regc,uniq=align_mode(m,h4,af); ou,od,mfe,mae=passage_m15(m); box_hi,box_lo,cp,rng=env(m)
    c=m["close"].to_numpy(); o=m["open"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    exp_up=cp&(c>box_hi)&(rng>1.3*atr); exp_dn=cp&(c<box_lo)&(rng>1.3*atr)
    c1=pd.Series(c).shift(-1).to_numpy()
    print(f"\n[{tag}]")
    for md,d,side,lab in CELLS:
        if md not in uniq: continue
        code=uniq.index(md); modem=(regc==code)&mask
        ev=modem&(exp_up if d=='up' else exp_dn); ev=np.nan_to_num(ev.astype(float),nan=0).astype(bool)
        di=np.where(ev&dedup(ev,COOL))[0]; di=di[di<n-2]
        if len(di)<30: continue
        sidc='L' if side==1 else 'S'
        # HOLD vs FAIL
        if d=='up': hold=c1[di]>box_hi[di]
        else:       hold=c1[di]<box_lo[di]
        ph=Pm(ou,od,70,50,sidc,H,_mk(n,di[hold]))[0] if hold.sum()>=25 else None
        pf=Pm(ou,od,70,50,sidc,H,_mk(n,di[~hold]))[0] if (~hold).sum()>=25 else None
        p100=Pm(ou,od,100,70,sidc,H,_mk(n,di[hold]))[0] if hold.sum()>=25 else None
        # tradeability: HOLD-confirmed, entry t+2 open, structural stop = compression origin
        hi=di[hold]; hi=hi[hi<n-1]; entry=o[hi+1]
        stop=box_lo[hi] if side==1 else box_hi[hi]; sl=np.abs(entry-stop); ok=np.isfinite(sl)&(sl>0); hi=hi[ok]; sl=sl[ok]
        tr_s=""
        if len(hi)>=25:
            for rr in (1.0,1.5,2.0):
                tr=sb.simulate(m, hi, side, sl, rr=rr, horizon=H, scenario="STRESS")
                if len(tr): mm=sb.metrics(tr,m,rr); tr_s+=f" rr{rr}:{mm['avgR']:+.3f}"
        f=lambda x:(f"{x:.2f}" if x is not None else "na")
        print(f"   {lab:11s} {md[:11]:11s} {d}->{sidc}: HOLD P70={f(ph)}(n{int(hold.sum())}) FAIL P70={f(pf)}(n{int((~hold).sum())}) HOLD P100/70={f(p100)} | trade(structSL med={np.median(sl)/0.10:.0f}p n{len(hi)}):{tr_s}")

def _mk(n,idx):
    x=np.zeros(n,bool); x[idx]=True; return x

def main():
    print(f"S4 HOLD/FAIL + larger payoff + tradeability (mode-aligned dir expansion, structural stop=compression origin, STRESS). H={H//4}h.")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    run_era("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy())
    run_era("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy())
    for y in (2021,2022,2023): run_era(str(y),sm,sh4,sb.align_context,dev&(yr==y))

if __name__=="__main__":
    main()

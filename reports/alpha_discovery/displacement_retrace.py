"""displacement_retrace.py — S10 CONTROLLED-RETRACEMENT / HOLD-confirmed entry (§8/§14/§15/§16), the CEO
architecture: MODE -> displacement -> origin HOLDS (controlled retracement, no reclaim) -> continuation entry.
After a mode-aligned displacement at t (origin = opposite extreme), require the origin to HOLD for HOLDK bars
(controlled retracement, filters the FAIL cases). Two variants: HOLD-only and HOLD+PULLBACK (a real pullback of
>=25% of the displacement range occurred). Enter at open[t+HOLDK+1]; STRUCTURAL stop = displacement origin.
Net STRESS per cell x era; small predeclared rr. Frozen mode taxonomy. Causal, price-only, event-deduped.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_m15_discover import dedup
from displacement_info import disp
from liquidity_event import align_mode
COOL=8; H=32; HOLDK=2
CELLS=[
 ("PRIMARY_BULL_IMPULSE",'up',1,"C1 bull-disp->L"),
 ("BULL_CORRECTION",'dn',-1,"C2 bear-disp->S"),
 ("BEAR_CORRECTION",'dn',-1,"C3 bear-disp->S"),
 ("PRIMARY_BEAR_IMPULSE",'dn',-1,"C4 bear-disp->S"),
]

def entries(m, di, side, want_pullback):
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); n=len(m)
    sig=[];
    for t in di:
        if t+HOLDK+1>=n: continue
        origin=l[t] if side==1 else h[t]; dhi=h[t]; dlo=l[t]; rng=max(dhi-dlo,1e-9)
        held=True; pl=l[t] if side==1 else h[t]
        for j in range(t+1,t+1+HOLDK):
            if side==1:
                if l[j]<origin: held=False; break
                pl=min(pl,l[j])
            else:
                if h[j]>origin: held=False; break
                pl=max(pl,h[j])
        if not held: continue
        if want_pullback:
            # a controlled pullback of >=25% of the displacement range toward origin
            if side==1 and (dhi-pl) < 0.25*rng: continue
            if side==-1 and (pl-dlo) < 0.25*rng: continue
        sig.append(t+HOLDK)   # signal bar -> entry at open[t+HOLDK+1]
    return np.array(sig,dtype=int)

def trade(m, sig, side, tag):
    o=m["open"].to_numpy(); l=m["low"].to_numpy(); h=m["high"].to_numpy(); n=len(m)
    sig=sig[sig<n-1]
    if len(sig)<25: print(f"     [{tag}] events={len(sig)}(thin)"); return
    entry=o[sig+1]
    # structural stop = displacement origin (opposite extreme of the disp bar = HOLDK bars before signal)
    dispbar=sig-HOLDK; sl=(entry-l[dispbar]) if side==1 else (h[dispbar]-entry); ok=np.isfinite(sl)&(sl>0)
    sig=sig[ok]; sl=sl[ok]
    print(f"     [{tag}] events={len(sig)} medSL={np.median(sl)/0.10:.0f}p")
    for rr in (1.0,1.5,2.0):
        tr=sb.simulate(m, sig, side, sl, rr=rr, horizon=H, scenario="STRESS")
        if len(tr): mm=sb.metrics(tr,m,rr); print(f"        rr{rr}: avgR={mm['avgR']:+.3f} WR={mm['WR_pos']:.2f} best10={mm['best10']:+.3f} tpm={mm['trades_per_month']:.1f}")

def run_era(tag, m, h4, af, mask, want_pullback):
    regc,uniq=align_mode(m,h4,af); up,dn=disp(m)
    print(f"\n[{tag}] {'HOLD+PULLBACK' if want_pullback else 'HOLD-only'}")
    for md,dd_dir,side,lab in CELLS:
        if md not in uniq: continue
        code=uniq.index(md); dmask=(regc==code)&mask&(up if dd_dir=='up' else dn)
        di=np.where(dmask&dedup(dmask,COOL))[0]
        if len(di)<30: continue
        sig=entries(m,di,side,want_pullback); trade(m,sig,side,lab)

def main():
    print(f"S10 CONTROLLED-RETRACEMENT/HOLD entry (HOLDK={HOLDK}, structural stop=disp origin, STRESS). H={H//4}h.")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    for wp in (False, True):
        print(f"\n===== variant: {'HOLD+PULLBACK' if wp else 'HOLD-only'} =====")
        run_era("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy(),wp)
        run_era("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy(),wp)
        for y in (2021,2022,2023): run_era(str(y),sm,sh4,sb.align_context,dev&(yr==y),wp)

if __name__=="__main__":
    main()

"""displacement_trade.py — S10 tradeability + FAILURE branch (§9/§14/§15/§16) for the cross-era-consistent cells.
Immediate continuation entry at displacement bar close (entry = next open); STRUCTURAL stop = displacement bar's
opposite extreme (origin/invalidation, §15; healthy since range>1.2 ATR). Net STRESS per cell x era, small
predeclared rr. FAILURE branch: P(+70/-50) for displacement+HOLD (origin not reclaimed within K) vs +FAIL.
Frozen mode taxonomy. Causal, price-only, event-deduped.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from state_m15_discover import dedup
from displacement_info import disp
from liquidity_event import align_mode
COOL=8; H=32; K=4
CELLS=[
 ("PRIMARY_BULL_IMPULSE",'up',1,"C1 bull-disp->L"),
 ("BULL_CORRECTION",'dn',-1,"C2 bear-disp->S"),
 ("BEAR_CORRECTION",'dn',-1,"C3 bear-disp->S"),
 ("PRIMARY_BEAR_IMPULSE",'dn',-1,"C4 bear-disp->S"),
]

def run_era(tag, m, h4, af, mask):
    regc,uniq=align_mode(m,h4,af); ou,od,_,_=passage_m15(m); up,dn=disp(m)
    o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); n=len(m)
    print(f"\n[{tag}]")
    for md,dd_dir,side,lab in CELLS:
        if md not in uniq: continue
        code=uniq.index(md); dmask=(regc==code)&mask&(up if dd_dir=='up' else dn)
        di=np.where(dmask&dedup(dmask,COOL))[0]; di=di[di<n-1]
        if len(di)<30: print(f"   {lab:16s}: events={len(di)}(thin)"); continue
        entry=o[di+1]; sl=(entry-l[di]) if side==1 else (h[di]-entry); ok=np.isfinite(sl)&(sl>0); di=di[ok]; sl=sl[ok]
        # FAILURE branch: origin (disp bar low[long]/high[short]) reclaimed within K bars?
        orig=l[di] if side==1 else h[di]; hold=np.ones(len(di),bool)
        for a in range(len(di)):
            t=di[a]
            for j in range(t+1,min(t+1+K,n)):
                if (side==1 and l[j]<orig[a]) or (side==-1 and h[j]>orig[a]): hold[a]=False; break
        m_all=np.zeros(n,bool); m_all[di]=True
        ph=Pm(ou,od,70,50,'L' if side==1 else 'S',H, (lambda mm: mm)(_mk(n,di[hold])))[0] if hold.sum()>=25 else None
        pf=Pm(ou,od,70,50,'L' if side==1 else 'S',H, _mk(n,di[~hold]))[0] if (~hold).sum()>=25 else None
        print(f"   {lab:16s}: events={len(di)} medSL={np.median(sl)/0.10:.0f}p | FAILbr: HOLD P={('%.2f'%ph) if ph else 'na'}(n{int(hold.sum())}) FAIL P={('%.2f'%pf) if pf else 'na'}(n{int((~hold).sum())})")
        for rr in (1.0,1.5,2.0):
            tr=sb.simulate(m, di, side, sl, rr=rr, horizon=H, scenario="STRESS")
            if len(tr): mm=sb.metrics(tr,m,rr); print(f"        rr{rr}: avgR={mm['avgR']:+.3f} WR={mm['WR_pos']:.2f} best10={mm['best10']:+.3f} tpm={mm['trades_per_month']:.1f}")

def _mk(n,idx):
    x=np.zeros(n,bool); x[idx]=True; return x

def main():
    print(f"S10 TRADEABILITY (immediate entry, structural stop=disp origin, STRESS) + FAILURE branch. H={H//4}h.")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    run_era("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy())
    run_era("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy())
    for y in (2021,2022,2023): run_era(str(y),sm,sh4,sb.align_context,dev&(yr==y))

if __name__=="__main__":
    main()

"""HF6 (historical) — D1 overnight/GAP + day-after-big-day directional (temporal-structural class, genuinely
different from the H4-swing mechanism frontiers). On b0/b1. Entry at the gap-day OPEN (causal: gap known at open).
Path-first. Causal hist_data. DISCOVERY_CONSUMED -> NOT validation. Low prior (temporal edges weak on 2021-23).
"""
import numpy as np, pandas as pd
import hist_data as hd, swing_base as sb, external_common as ec
from frontier_hist1 import refeat

H=10  # D1 bars (~2 weeks)
def report(df, groups, rr, tag):
    trs=[]
    for ev,side,risk in groups:
        if len(ev)==0: continue
        trs.append(sb.simulate(df,ev,side,risk,rr=rr,horizon=H,scenario="STRESS"))
    if not trs: print(f"    [{tag} rr{rr}] no trades"); return
    tr=pd.concat(trs,ignore_index=True); m=sb.metrics(tr,df,rr)
    te=tr["t_entry"].to_numpy()
    b0=(te>=hd.BLOCKS["b0"][0])&(te<=hd.BLOCKS["b0"][1]); b1=(te>=hd.BLOCKS["b1"][0])&(te<=hd.BLOCKS["b1"][1])
    rB=tr["R"].to_numpy(); advF=(tr["mae_R"].to_numpy()>=1.0).mean(); medMFE=np.median(tr["mfe_R"]); medMAE=np.median(tr["mae_R"])
    py=" ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
    print(f"    [{tag} rr{rr}] N={m['N']} medMFE={medMFE:.2f} medMAE={medMAE:.2f} advF={advF:.2f} avgR={m['avgR']:+.3f} "
          f"PF={m['PF']:.2f} best5={m['best5']:+.3f} best10={m['best10']:+.3f} maxDD={m['maxDD_R']:.1f} "
          f"| b0 {rB[b0].mean():+.2f}(n{int(b0.sum())}) b1 {rB[b1].mean():+.2f}(n{int(b1.sum())}) | {py}")

def main():
    tfs=hd.load(); d1=refeat(tfs["D1"])
    o=d1["open"].to_numpy(); c=d1["close"].to_numpy(); h=d1["high"].to_numpy(); l=d1["low"].to_numpy()
    atr=d1["atr"].to_numpy(); atr_ma=d1["atr_ma"].to_numpy(); disc=d1["is_disc"].to_numpy(); seg=d1["seg"].to_numpy()
    n=len(d1)
    prev_c=np.roll(c,1); gap=o-prev_c
    same=np.zeros(n,bool); same[1:]=(seg[1:]==seg[:-1])  # i-1 same segment as i
    # meaningful gap and day-after-big-day, entry at open[i] => signal index = i-1
    print(f"HF6 D1 gap/temporal  D1 DISC days={int(disc.sum())} (b0+b1)")
    gmask=(np.abs(gap)>0.3*atr_ma)&same&disc&np.isfinite(gap)&np.isfinite(atr)
    gidx=np.array([i for i in np.where(gmask)[0] if 0<i<n-1])
    ev=gidx-1  # entry=open[gidx]
    risk=atr[gidx-1]  # causal ATR (known before open[i])
    ok=np.isfinite(risk)&(risk>0); ev,gidx,risk=ev[ok],gidx[ok],risk[ok]
    gs=np.sign(gap[gidx])
    print(f"  D1 GAP events={len(ev)} (upgaps={(gs>0).mean():.2f})")
    for rr in (1.0,1.5,2.0):
        # continuation
        report(d1,[(ev[gs>0],+1,risk[gs>0]),(ev[gs<0],-1,risk[gs<0])],rr,"GAP-CONT")
    for rr in (1.0,1.5):
        report(d1,[(ev[gs>0],-1,risk[gs>0]),(ev[gs<0],+1,risk[gs<0])],rr,"GAP-FADE")
    # day-after-big-day: big range day i-1 -> trade day i in prior-day close-direction (continuation)
    rng=h-l; big=(rng>1.5*atr_ma)
    bidx=np.array([i for i in np.where(big&same&disc)[0] if 0<i<n-1])
    ev2=bidx-1; risk2=atr[bidx-1]; ok2=np.isfinite(risk2)&(risk2>0); ev2,bidx,risk2=ev2[ok2],bidx[ok2],risk2[ok2]
    dirn=np.sign(c[bidx-1]-o[bidx-1])  # prior big day's body direction (causal)
    print(f"  DAY-AFTER-BIG events={len(ev2)}")
    for rr in (1.0,1.5):
        report(d1,[(ev2[dirn>0],+1,risk2[dirn>0]),(ev2[dirn<0],-1,risk2[dirn<0])],rr,"BIGDAY-CONT")

if __name__=="__main__":
    main()

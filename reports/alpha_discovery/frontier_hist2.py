"""HF2 (historical) — RANGE-regime mean-reversion (fade the range extremes). CEO priority: RANGE / mean-reversion
alpha (§8). Tested where a GENUINE range exists (2011-2012 top/range in b0) — unlike trend-dominated 2021-2023.
Causal (hist_data), features per segment. Upper-fade SHORT / lower-fade LONG, structural stop beyond boundary.
Path-first (§15). DISCOVERY_CONSUMED -> NOT validation.
"""
import numpy as np, pandas as pd
import hist_data as hd, swing_base as sb, external_common as ec
from frontier_hist1 import refeat

WB=30; H=42
def boxes(df):
    bh=np.full(len(df),np.nan); bl=np.full(len(df),np.nan)
    for s,g in df.groupby("seg"):
        i=g.index.to_numpy(); h=g["high"].to_numpy(); l=g["low"].to_numpy()
        bh[i]=pd.Series(h).rolling(WB).max().shift(1).to_numpy(); bl[i]=pd.Series(l).rolling(WB).min().shift(1).to_numpy()
    return bh,bl

def convert(df,ev,side,risk,tag):
    if len(ev)<8: print(f"    [{tag}] N={len(ev)} (too few)"); return
    ps=ec.path_stats(df,ev,side,risk,H)
    print(f"    [{tag}] N={ps['N']} medMFE={ps['medMFE']:.2f} medMAE={ps['medMAE']:.2f} advF={ps['advFirst']:.2f} "
          f"P(+.5<-1)={ps['P_05']:.2f} P(+1<-1)={ps['P_1']:.2f} mfe70={ps['mfe70']:.2f} mfe100={ps['mfe100']:.2f}")
    for rr in (1.0,1.5,2.0):
        tr=sb.simulate(df,ev,side,risk,rr=rr,horizon=H,scenario="STRESS"); m=sb.metrics(tr,df,rr); dc=sb.disc_conf(tr,df,rr)
        t_ev=df["time"].to_numpy()[ev+1]
        b0m=(t_ev>=hd.BLOCKS["b0"][0])&(t_ev<=hd.BLOCKS["b0"][1]); b1m=(t_ev>=hd.BLOCKS["b1"][0])&(t_ev<=hd.BLOCKS["b1"][1])
        rB=tr["R"].to_numpy(); pb=f"b0 {rB[b0m].mean():+.2f}(n{int(b0m.sum())}) b1 {rB[b1m].mean():+.2f}(n{int(b1m.sum())})"
        py=" ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
        print(f"      rr={rr}: WRt={m['WR_target']:.2f} avgR={m['avgR']:+.3f} PF={m['PF']:.2f} best5={m['best5']:+.3f} "
              f"best10={m['best10']:+.3f} maxDD={m['maxDD_R']:.1f} medSL={m['med_sl_pips']:.0f}p tpm={m['trades_per_month']:.2f} "
              f"| DISC{(dc['disc_avgR'] if dc else 0):+.2f}/CONF{(dc['conf_avgR'] if dc else 0):+.2f} | {pb} | {py}")

def main():
    tfs=hd.load(); h4=refeat(tfs["H4"])
    bh,bl=boxes(h4); mid=(bh+bl)/2; height=bh-bl
    o=h4["open"].to_numpy(); h=h4["high"].to_numpy(); l=h4["low"].to_numpy(); c=h4["close"].to_numpy(); atr=h4["atr"].to_numpy()
    reg=h4["regime"].to_numpy(); disc=h4["is_disc"].to_numpy(); seg=h4["seg"].to_numpy()
    same=np.zeros(len(h4),bool); same[WB:]=(seg[WB:]==seg[:-WB])
    real_range=(reg=="RANGE")&(height>2.0*atr)&np.isfinite(height)&same&disc
    # upper-fade SHORT: reached near top + close rejection
    up_touch=(h>=bh-0.10*height)&(c<h)&real_range
    dn_touch=(l<=bl+0.10*height)&(c>l)&real_range
    print(f"HF2 range mean-reversion  H4 DISC bars={int(disc.sum())} RANGE-regime real-range bars={int(real_range.sum())}")
    for side,name,touch in ((-1,"UPPER-FADE SHORT",up_touch),(+1,"LOWER-FADE LONG",dn_touch)):
        raw=[i for i in np.where(touch)[0] if i+1<len(h4)]
        ev=sb.dedup_events(np.array(raw),cooldown=WB)
        if side<0: risk=np.array([(bh[i]+0.3*atr[i])-o[i+1] for i in ev])
        else:      risk=np.array([o[i+1]-(bl[i]-0.3*atr[i]) for i in ev])
        ok=np.isfinite(risk)&(risk>0); ev,risk=ev[ok],risk[ok]
        print(f"  {name}: events={len(ev)}")
        convert(h4,ev,side,risk,name)

if __name__=="__main__":
    main()

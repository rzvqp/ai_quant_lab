"""HF3 (historical, bearish) — two distinct SHORT mechanisms in a confirmed D1 downtrend on b0/b1:
 A) pullback-to-falling-EMA short (rally into a falling H4 EMA20 that fails -> resume down). Distinct from
    HF1 (compression) and from H4-bo-raw-S (raw breakout).
 B) breakdown-momentum short with chandelier trailing ride (distinct payoff; discloses overlap vs H4-bo-raw-S).
Causal (hist_data), features per segment. Path-first (§15). DISCOVERY_CONSUMED -> NOT validation.
"""
import numpy as np, pandas as pd
import hist_data as hd, swing_base as sb, external_common as ec
from frontier_hist1 import refeat
from frontier6_crashmom import sim_trail

H=42
def emit(df, ev, side, risk, tag, trail=None, atr=None):
    if len(ev)<8: print(f"    [{tag}] N={len(ev)} (too few)"); return
    ps=ec.path_stats(df,ev,side,risk,H)
    print(f"    [{tag}] N={ps['N']} medMFE={ps['medMFE']:.2f} medMAE={ps['medMAE']:.2f} advF={ps['advFirst']:.2f} "
          f"P(+.5<-1)={ps['P_05']:.2f} P(+1<-1)={ps['P_1']:.2f} P(+1.5<-1)={ps['P_15']:.2f} mfe100={ps['mfe100']:.2f}")
    t_ev=df["time"].to_numpy()[ev+1]
    b0m=(t_ev>=hd.BLOCKS["b0"][0])&(t_ev<=hd.BLOCKS["b0"][1]); b1m=(t_ev>=hd.BLOCKS["b1"][0])&(t_ev<=hd.BLOCKS["b1"][1])
    if trail is not None:
        for tm in trail:
            tr=sim_trail(df,ev,side,risk,atr,trail_mult=tm,horizon=H,scenario="STRESS")
            m=sb.metrics(tr.assign(tp_pips=0),df,1.0); dc=sb.disc_conf(tr,df,1.0); rB=tr["R"].to_numpy()
            pb=f"b0 {rB[b0m].mean():+.2f}(n{int(b0m.sum())}) b1 {rB[b1m].mean():+.2f}(n{int(b1m.sum())})"
            py=" ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
            print(f"      trail={tm}ATR: posRate={m['WR_pos']:.2f} avgR={m['avgR']:+.3f} PF={m['PF']:.2f} best10={m['best10']:+.3f} "
                  f"maxDD={m['maxDD_R']:.1f} | DISC{(dc['disc_avgR'] if dc else 0):+.2f}/CONF{(dc['conf_avgR'] if dc else 0):+.2f} | {pb} | {py}")
    else:
        for rr in (1.5,2.0,3.0):
            tr=sb.simulate(df,ev,side,risk,rr=rr,horizon=H,scenario="STRESS"); m=sb.metrics(tr,df,rr); dc=sb.disc_conf(tr,df,rr)
            rB=tr["R"].to_numpy(); pb=f"b0 {rB[b0m].mean():+.2f}(n{int(b0m.sum())}) b1 {rB[b1m].mean():+.2f}(n{int(b1m.sum())})"
            py=" ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
            print(f"      rr={rr}: WRt={m['WR_target']:.2f} avgR={m['avgR']:+.3f} PF={m['PF']:.2f} best5={m['best5']:+.3f} "
                  f"best10={m['best10']:+.3f} maxDD={m['maxDD_R']:.1f} medSL={m['med_sl_pips']:.0f}p tpm={m['trades_per_month']:.2f} "
                  f"| DISC{(dc['disc_avgR'] if dc else 0):+.2f}/CONF{(dc['conf_avgR'] if dc else 0):+.2f} | {pb} | {py}")

def main():
    tfs=hd.load(); h4=refeat(tfs["H4"]); d1=refeat(tfs["D1"]).copy()
    d1["d1_dn"]=(d1["ema20"]<d1["ema50"]).astype(float)
    d1_dn=(hd.align_causal(h4,d1,["d1_dn"],"")["d1_dn"].to_numpy()>0.5)
    o=h4["open"].to_numpy(); h=h4["high"].to_numpy(); l=h4["low"].to_numpy(); c=h4["close"].to_numpy()
    atr=h4["atr"].to_numpy(); atr_ma=h4["atr_ma"].to_numpy(); e20=h4["ema20"].to_numpy()
    disc=h4["is_disc"].to_numpy(); seg=h4["seg"].to_numpy()
    same6=np.zeros(len(h4),bool); same6[6:]=(seg[6:]==seg[:-6])
    e20_fall=np.zeros(len(h4),bool); e20_fall[5:]=(e20[5:]<e20[:-5])
    print(f"HF3 bearish shorts  H4 DISC bars={int(disc.sum())} (b0 2011-13 + b1 2016-18)")

    # A) pullback-to-falling-EMA short
    swh=pd.Series(h).rolling(4).max().to_numpy()
    sigA = d1_dn & e20_fall & (h>=e20) & (c<e20) & (c<o) & disc & same6
    rawA=[i for i in np.where(sigA)[0] if i+1<len(h4)]
    evA=sb.dedup_events(np.array(rawA),cooldown=6)
    riskA=np.array([(swh[i]+0.2*atr[i])-o[i+1] for i in evA]); okA=np.isfinite(riskA)&(riskA>0); evA,riskA=evA[okA],riskA[okA]
    print(f"  A) pullback-to-falling-EMA SHORT: events={len(evA)}")
    emit(h4,evA,-1,riskA,"A pullback-EMA-short")

    # B) breakdown-momentum short with trailing ride (discloses overlap vs H4-bo-raw-S)
    ll10=pd.Series(l).rolling(10).min().shift(1).to_numpy()
    tr_=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1))))
    rng=h-l; closepos=np.where(rng>0,(c-l)/rng,0.5)
    sigB = d1_dn & (c<ll10) & (tr_>1.3*atr_ma) & (closepos<0.33) & disc & same6
    rawB=[i for i in np.where(sigB)[0] if i+1<len(h4)]
    evB=sb.dedup_events(np.array(rawB),cooldown=10)
    riskB=np.array([(h[i]+0.2*atr[i])-o[i+1] for i in evB]); okB=np.isfinite(riskB)&(riskB>0); evB,riskB=evB[okB],riskB[okB]
    print(f"  B) breakdown-momentum SHORT (trailing; overlap-vs-H4-bo-raw-S disclosed): events={len(evB)}")
    emit(h4,evB,-1,riskB,"B breakdown-mom-short",trail=[2.0,3.0],atr=atr)

if __name__=="__main__":
    main()

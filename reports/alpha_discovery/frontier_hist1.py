"""HF1 (historical, bearish regime) — compression-timed SHORT continuation in a confirmed D1 DOWNTREND.
Principled SHORT mirror of COMP-CONT-L, tested on b0+b1 (incl. 2013 bear) where a real downtrend exists.
Distinct from H4-bo-raw-S (raw breakout) and NOT a LONG-beta clone. Causal (hist_data), features per segment
(multi-year gaps do not contaminate rolling/ewm). Path-first (§15). DISCOVERY_CONSUMED data -> NOT validation.
"""
import numpy as np, pandas as pd
import hist_data as hd, swing_base as sb, external_common as ec

W=20; H=42
def segize(df,gap_days=10):
    t=df["time"].to_numpy(); brk=np.zeros(len(df),int)
    if len(df)>1: brk[1:]=(np.diff(t)>gap_days*86400).cumsum()
    df=df.copy(); df["seg"]=brk; return df
def refeat(df):
    df=segize(df); parts=[hd._regime(hd._feat(g.copy())) for _,g in df.groupby("seg")]
    return pd.concat(parts).sort_values("time").reset_index(drop=True)
def boxes_perseg(df):
    bh=np.full(len(df),np.nan); bl=np.full(len(df),np.nan); bma=np.full(len(df),np.nan)
    for s,g in df.groupby("seg"):
        i=g.index.to_numpy(); h=g["high"].to_numpy(); l=g["low"].to_numpy()
        H_=pd.Series(h).rolling(W).max().shift(1).to_numpy(); L_=pd.Series(l).rolling(W).min().shift(1).to_numpy()
        br=H_-L_; bm=pd.Series(br).rolling(50).mean().shift(1).to_numpy()
        bh[i]=H_; bl[i]=L_; bma[i]=bm
    return bh,bl,bma

def convert(df, ev, side, risk, tag, blockmask):
    if len(ev)<8: print(f"    [{tag}] N={len(ev)} (too few)"); return
    ps=ec.path_stats(df,ev,side,risk,H)
    print(f"    [{tag}] N={ps['N']} medMFE={ps['medMFE']:.2f} medMAE={ps['medMAE']:.2f} P75MAE={ps['P75_MAE']:.2f} "
          f"advF={ps['advFirst']:.2f} P(+.5<-1)={ps['P_05']:.2f} P(+1<-1)={ps['P_1']:.2f} P(+1.5<-1)={ps['P_15']:.2f} "
          f"mfe70={ps['mfe70']:.2f} mfe100={ps['mfe100']:.2f} mfe150={ps['mfe150']:.2f}")
    for rr in (1.5,2.0,3.0):
        for scen in ("BASE","STRESS"):
            tr=sb.simulate(df,ev,side,risk,rr=rr,horizon=H,scenario=scen)
            m=sb.metrics(tr,df,rr); dc=sb.disc_conf(tr,df,rr)
            if scen=="STRESS":
                # per-block
                t_ev=df["time"].to_numpy()[ev+1]
                b0m=(t_ev>=hd.BLOCKS["b0"][0])&(t_ev<=hd.BLOCKS["b0"][1]); b1m=(t_ev>=hd.BLOCKS["b1"][0])&(t_ev<=hd.BLOCKS["b1"][1])
                rB=tr["R"].to_numpy()
                pb=f"b0 {rB[b0m].mean():+.2f}(n{b0m.sum()}) b1 {rB[b1m].mean():+.2f}(n{b1m.sum()})" if len(rB)==len(b0m) else ""
                py=" ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
                dctxt=(f"DISC{dc['disc_avgR']:+.2f}/CONF{dc['conf_avgR']:+.2f}" if dc else "dc n/a")
                print(f"      rr={rr} STRESS: WRt={m['WR_target']:.2f} avgR={m['avgR']:+.3f} PF={m['PF']:.2f} "
                      f"best5={m['best5']:+.3f} best10={m['best10']:+.3f} maxDD={m['maxDD_R']:.1f} medSL={m['med_sl_pips']:.0f}p "
                      f"tpm={m['trades_per_month']:.2f} | {dctxt} | {pb} | {py}")
            else:
                print(f"      rr={rr} BASE  : avgR={m['avgR']:+.3f} PF={m['PF']:.2f}")

def main():
    tfs=hd.load(); h4=refeat(tfs["H4"]); d1=refeat(tfs["D1"])
    d1=d1.copy(); d1["d1_dn"]=(d1["ema20"]<d1["ema50"]).astype(float); d1["d1_up"]=(d1["ema20"]>d1["ema50"]).astype(float)
    h4c=hd.align_causal(h4,d1,["d1_dn","d1_up"],""); d1_dn=(h4c["d1_dn"].to_numpy()>0.5); d1_up=(h4c["d1_up"].to_numpy()>0.5)
    bh,bl,bma=boxes_perseg(h4)
    atr=h4["atr"].to_numpy(); atr_ma=h4["atr_ma"].to_numpy(); c=h4["close"].to_numpy(); o=h4["open"].to_numpy()
    br=bh-bl; comp=(atr<atr_ma)&(br<bma)&np.isfinite(br)&np.isfinite(atr)
    disc=h4["is_disc"].to_numpy(); seg=h4["seg"].to_numpy()
    # require prior-W window in same segment (no cross-gap)
    same_seg=np.zeros(len(h4),bool); s=seg
    same_seg[W:]=(s[W:]==s[:-W])
    print(f"HF1 compression-timed continuation  H4 DISC bars={int(disc.sum())}  (b0 2011-13 incl 2013 bear + b1 2016-18)")
    for side,name,ctx in ((-1,"SHORT (D1 downtrend)",d1_dn),(+1,"LONG (D1 uptrend, ref only)",d1_up)):
        cond=comp&ctx&disc&same_seg
        raw=[i for i in np.where(cond)[0] if i+1<len(h4)]
        ev=sb.dedup_events(np.array(raw),cooldown=W)
        if side<0: risk=np.array([bh[i]-o[i+1] for i in ev])
        else:      risk=np.array([o[i+1]-bl[i] for i in ev])
        ok=np.isfinite(risk)&(risk>0); ev,risk=ev[ok],risk[ok]
        print(f"  {name}: events={len(ev)}")
        convert(h4,ev,side,risk,name,disc)

if __name__=="__main__":
    main()

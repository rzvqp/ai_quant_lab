"""F5-COMPCONT — compression-TIMED trend CONTINUATION (distinct from F1 expansion-breakout and F4 time-drift).
Thesis: in a confirmed D1 trend, an H4 volatility compression is a low-risk RE-ENTRY TIMING point; trade in the
HTF-trend direction (NOT the break direction), with a STRUCTURAL stop at the compression floor/ceiling.
Adds natural invalidation that F4 lacked. Both sides (SHORT only in D1-down). RR {1.5,2,3}, swing horizon. DEV.
"""
import numpy as np, pandas as pd
import swing_base as sb

W=20; H=42
def comp_mask(h4):
    h=h4["high"].to_numpy(); l=h4["low"].to_numpy(); atr=h4["atr"].to_numpy(); atr_ma=h4["atr_ma"].to_numpy()
    bh=pd.Series(h).rolling(W).max().shift(1).to_numpy(); bl=pd.Series(l).rolling(W).min().shift(1).to_numpy()
    br=bh-bl; bma=pd.Series(br).rolling(50).mean().shift(1).to_numpy()
    comp=(atr<atr_ma)&(br<bma)&np.isfinite(br)&np.isfinite(atr)
    return comp, bh, bl

def run(h4, d1_up_aligned, dev_mask):
    o=h4["open"].to_numpy(); comp,bh,bl=comp_mask(h4)
    for side,name in ((+1,"LONG"),(-1,"SHORT")):
        want_up = side>0
        cond = comp & (d1_up_aligned==want_up) & dev_mask
        raw=[i for i in np.where(cond)[0] if i+1<len(h4)]
        ev=sb.dedup_events(np.array(raw),cooldown=W)  # one re-entry per compression window
        if side>0: risk=np.array([o[i+1]-bl[i] for i in ev])
        else:      risk=np.array([bh[i]-o[i+1] for i in ev])
        ok=np.isfinite(risk)&(risk>0); ev,risk=ev[ok],risk[ok]
        if len(ev)<8:
            print(f"  {name}: N={len(ev)} (too few)"); continue
        scr=sb.simulate(h4,ev,side,risk,rr=10.0,horizon=H,scenario="STRESS")
        print(f"  {name}: events={len(ev)} SCREEN medMFE={scr['mfe_R'].median():.2f}R medMAE={scr['mae_R'].median():.2f}R "
              f"advFirst={(scr['mae_R']>=1.0).mean():.2f} medSL={scr['sl_pips'].median():.0f}p")
        for rr in (1.5,2.0,3.0):
            for scen in ("BASE","STRESS"):
                tr=sb.simulate(h4,ev,side,risk,rr=rr,horizon=H,scenario=scen)
                m=sb.metrics(tr,h4,rr); dc=sb.disc_conf(tr,h4,rr)
                if scen=="STRESS":
                    py=" ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
                    dctxt=(f"DISC{dc['disc_avgR']:+.2f} CONF{dc['conf_avgR']:+.2f}" if dc else "dc n/a")
                    print(f"     rr={rr} STRESS: N={m['N']} WRt={m['WR_target']:.2f} avgR={m['avgR']:+.3f} "
                          f"PF={m['PF']:.2f} best5={m['best5']:+.3f} best10={m['best10']:+.3f} maxDD={m['maxDD_R']:.1f} "
                          f"tpm={m['trades_per_month']:.1f} | {dctxt} | {py}")
                else:
                    print(f"     rr={rr} BASE  : avgR={m['avgR']:+.3f} PF={m['PF']:.2f}")

def main():
    tfs=sb.build_frames(); h4,d1=tfs["H4"],tfs["D1"]; dev_mask=h4["is_dev"].to_numpy()
    d1=d1.copy(); d1["d1_up"]=(d1["ema20"]>d1["ema50"]).astype(float)
    h4c=sb.align_context(h4,d1,["d1_up"],"_d1"); d1_up_aligned=(h4c["d1_up_d1"].to_numpy()>0.5)
    print(f"F5-COMPCONT  H4 DEV bars={int(dev_mask.sum())}")
    run(h4,d1_up_aligned,dev_mask)

if __name__=="__main__":
    main()

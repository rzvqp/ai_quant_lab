"""F4-DRIFT — time-based trend-drift, HORIZON payoff (not RR target). Different payoff mechanism (§7C).
Event = onset of a confirmed H4 trend regime (first bar regime flips to TREND_UP / TREND_DOWN).
Hold H bars (time exit) with only a WIDE structural safety stop (3*ATR). R normalized by 3*ATR risk.
Measures harvestable swing drift per regime onset, both sides, unconditional + D1-aligned. DEV selection.
"""
import numpy as np, pandas as pd
import swing_base as sb

HORS=[12,24,42]  # ~2d,4d,7d in H4 bars
SAFE=3.0         # safety stop in ATR

def onsets(regime, target):
    r=np.asarray(regime, object); on=np.zeros(len(r),bool)
    on[1:]=(r[1:]==target)&(r[:-1]!=target); return np.where(on)[0]

def run(h4, d1_up_aligned, dev_mask):
    atr=h4["atr"].to_numpy(); reg=h4["regime"].to_numpy()
    for target,side,name in (("TREND_UP",+1,"LONG"),("TREND_DOWN",-1,"SHORT")):
        raw=[i for i in onsets(reg,target) if i+1<len(h4) and dev_mask[i]]
        ev=sb.dedup_events(np.array(raw),cooldown=6)
        risk=np.array([SAFE*atr[i] for i in ev]); ok=np.isfinite(risk)&(risk>0); ev,risk=ev[ok],risk[ok]
        al = d1_up_aligned[ev] if side>0 else (~d1_up_aligned[ev])
        for tag,sel in (("ALL",np.ones(len(ev),bool)),("D1aligned",al)):
            e2,r2=ev[sel],risk[sel]
            if len(e2)<8:
                print(f"  {name} [{tag}]: N={len(e2)} (too few)"); continue
            for H in HORS:
                tr=sb.simulate(h4,e2,side,r2,rr=99.0,horizon=H,scenario="STRESS")
                m=sb.metrics(tr,h4,99.0)
                dc=sb.disc_conf(tr,h4,99.0)
                py=" ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
                dctxt=(f"DISC{dc['disc_avgR']:+.2f} CONF{dc['conf_avgR']:+.2f}" if dc else "dc n/a")
                # avgR here is in units of 3*ATR risk; convert to ATR-units captured for intuition
                atr_units=m['avgR']*SAFE
                print(f"  {name} [{tag}] H={H}: N={m['N']} posRate={m['WR_pos']:.2f} avgR(3ATR)={m['avgR']:+.3f} "
                      f"~{atr_units:+.2f}ATR PF={m['PF']:.2f} best10={m['best10']:+.3f} maxDD={m['maxDD_R']:.1f} "
                      f"| {dctxt} | {py}")

def main():
    tfs=sb.build_frames(); h4,d1=tfs["H4"],tfs["D1"]; dev_mask=h4["is_dev"].to_numpy()
    d1=d1.copy(); d1["d1_up"]=(d1["ema20"]>d1["ema50"]).astype(float)
    h4c=sb.align_context(h4,d1,["d1_up"],"_d1"); d1_up_aligned=(h4c["d1_up_d1"].to_numpy()>0.5)
    n_up=int(((pd.Series(h4['regime']).values=='TREND_UP')&dev_mask).sum())
    n_dn=int(((pd.Series(h4['regime']).values=='TREND_DOWN')&dev_mask).sum())
    print(f"F4-DRIFT  H4 DEV bars={int(dev_mask.sum())}  TREND_UP bars={n_up} TREND_DOWN bars={n_dn}")
    run(h4, d1_up_aligned, dev_mask)

if __name__=="__main__":
    main()

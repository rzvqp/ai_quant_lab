"""F7-PDHBREAK — prior-day-high breakout CONTINUATION LONG (faster daily-structure event) in a confirmed D1 uptrend.
Goal = FREQUENCY / LOW-OVERLAP diversification (§7-8), NOT a new direction. Explicit trade-overlap check vs the
frozen COMP-CONT-L (§9): if robust but high-overlap -> REDUNDANT_LONG_TREND_BETA (do not promote). DEV selection.
"""
import numpy as np, pandas as pd, json, os
import swing_base as sb

H=42
def run(h4,d1,dev_mask,cal_mask,d1_up_aligned):
    # prior-day high aligned causally: last COMPLETED D1 bar's HIGH
    d1=d1.copy()
    h4c=sb.align_context(h4,d1,["high","ema20","ema50"],"_d1")
    pdh=h4c["high_d1"].to_numpy()  # last completed daily high (= prior day's high once today is forming)
    o=h4["open"].to_numpy(); c=h4["close"].to_numpy(); atr=h4["atr"].to_numpy()
    # breakout = first H4 close above the completed-daily high, in a D1 uptrend
    above=(c>pdh); first=np.zeros(len(h4),bool); first[1:]=above[1:]&(~above[:-1])
    def events(mask):
        cond=first & d1_up_aligned & mask & np.isfinite(pdh)
        raw=[i for i in np.where(cond)[0] if i+1<len(h4)]
        ev=sb.dedup_events(np.array(raw),cooldown=6)
        stop=np.array([pdh[i]-0.2*atr[i] for i in ev]); risk=np.array([o[i+1]-s for i,s in zip(ev,stop)])
        ok=np.isfinite(risk)&(risk>0); return ev[ok],risk[ok]
    evd,rd=events(dev_mask)
    print(f"  DEV events={len(evd)}")
    for rr in (1.5,2.0):
        tr=sb.simulate(h4,evd,+1,rd,rr=rr,horizon=H,scenario="STRESS")
        m=sb.metrics(tr,h4,rr); dc=sb.disc_conf(tr,h4,rr)
        py=" ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
        dctxt=(f"DISC{dc['disc_avgR']:+.2f} CONF{dc['conf_avgR']:+.2f}" if dc else "dc n/a")
        print(f"  rr={rr} STRESS: N={m['N']} WRt={m['WR_target']:.2f} avgR={m['avgR']:+.3f} PF={m['PF']:.2f} "
              f"best5={m['best5']:+.3f} best10={m['best10']:+.3f} maxDD={m['maxDD_R']:.1f} tpm={m['trades_per_month']:.1f} "
              f"medSL={m['med_sl_pips']:.0f}p advFirst={(tr['mae_R']>=1.0).mean():.2f} | {dctxt} | {py}")
    # CALIB
    evc,rc=events(cal_mask)
    if len(evc)>=8:
        tr=sb.simulate(h4,evc,+1,rc,rr=2.0,horizon=H,scenario="STRESS"); m=sb.metrics(tr,h4,2.0)
        print(f"  CALIB rr2.0: N={m['N']} avgR={m['avgR']:+.3f} PF={m['PF']:.2f} posRate={m['WR_pos']:.2f}")
    # OVERLAP vs frozen COMP-CONT-L (trade-day Jaccard)
    pkg=os.path.join(sb._HERE,"comp_cont_L_package.json")
    if os.path.exists(pkg):
        cc=json.load(open(pkg)); cc_days=set(pd.to_datetime([t["t_entry"] for t in cc["ledger"]],unit="s",utc=True).floor("D"))
        tr2=sb.simulate(h4,evd,+1,rd,rr=2.0,horizon=H,scenario="STRESS")
        f7_days=set(pd.to_datetime(tr2["t_entry"],unit="s",utc=True).dt.floor("D"))
        inter=len(cc_days & f7_days); uni=len(cc_days | f7_days)
        print(f"  OVERLAP vs COMP-CONT-L: F7 trade-days={len(f7_days)} CCL days={len(cc_days)} "
              f"shared={inter} Jaccard={inter/max(uni,1):.2f}")

def main():
    tfs=sb.build_frames(); h4,d1=tfs["H4"],tfs["D1"]; dev_mask=h4["is_dev"].to_numpy(); cal_mask=h4["is_cal"].to_numpy()
    dd=d1.copy(); dd["d1_up"]=(dd["ema20"]>dd["ema50"]).astype(float)
    h4a=sb.align_context(h4,dd,["d1_up"],"_d1"); d1_up_aligned=(h4a["d1_up_d1"].to_numpy()>0.5)
    print(f"F7-PDHBREAK  H4 DEV bars={int(dev_mask.sum())}")
    run(h4,d1,dev_mask,cal_mask,d1_up_aligned)

if __name__=="__main__":
    main()

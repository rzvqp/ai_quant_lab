"""HF4 transition-onset SHORT — adversarial vetting (§20). Parameter neighborhood (stability not peak),
+1-bar execution degradation, CALIB 2020-21 readout (out-of-discovery, NOT validation), and CRITICAL
trade-overlap vs the frozen H4-bo-raw-S (same b0/b1 population, also SHORT). Overlap-high => REDUNDANT.
Ledger + fingerprints if it survives. Causal hist_data; swing_base untouched.
"""
import numpy as np, pandas as pd, json, os, hashlib
import hist_data as hd, swing_base as sb, external_common as ec
from frontier_hist1 import refeat

H=42
def onset(reg,target):
    r=np.asarray(reg,object); on=np.zeros(len(r),bool); on[1:]=(r[1:]==target)&(r[:-1]!=target); return on

def events(h4,d1_up,mask,W,cd):
    o=h4["open"].to_numpy(); h=h4["high"].to_numpy(); atr=h4["atr"].to_numpy(); reg=h4["regime"].to_numpy(); seg=h4["seg"].to_numpy()
    sameW=np.zeros(len(h4),bool); sameW[W:]=(seg[W:]==seg[:-W]); swh=pd.Series(h).rolling(W).max().to_numpy()
    sig=onset(reg,"TREND_DOWN") & (~d1_up) & mask & sameW
    raw=[i for i in np.where(sig)[0] if i+1<len(h4)]; ev=sb.dedup_events(np.array(raw),cooldown=cd)
    risk=np.array([(swh[i]+0.2*atr[i])-o[i+1] for i in ev]); ok=np.isfinite(risk)&(risk>0)
    return ev[ok],risk[ok]

def main():
    tfs=hd.load(); h4=refeat(tfs["H4"]); d1=refeat(tfs["D1"]).copy(); d1["d1_up"]=(d1["ema20"]>d1["ema50"]).astype(float)
    d1_up=(hd.align_causal(h4,d1,["d1_up"],"")["d1_up"].to_numpy()>0.5)
    disc=h4["is_disc"].to_numpy(); calib=h4["is_calib"].to_numpy()
    print("== NEIGHBORHOOD (STRESS, DISC b0+b1) core=W10/cd10/rr2 ==")
    print("  W  cd  rr |  N  avgR   PF   best5  best10 allYr+  b0     b1    DISC  CONF")
    for W in (6,10,14):
        for cd in (6,10):
            ev,risk=events(h4,d1_up,disc,W,cd)
            if len(ev)<10: continue
            for rr in (1.5,2.0,3.0):
                tr=sb.simulate(h4,ev,-1,risk,rr=rr,horizon=H,scenario="STRESS"); m=sb.metrics(tr,h4,rr); dc=sb.disc_conf(tr,h4,rr)
                t=tr["time"].to_numpy() if "time" in tr else h4["time"].to_numpy()[ev+1]
                te=h4["time"].to_numpy()[ev+1]; b0=(te>=hd.BLOCKS["b0"][0])&(te<=hd.BLOCKS["b0"][1]); b1=(te>=hd.BLOCKS["b1"][0])&(te<=hd.BLOCKS["b1"][1])
                rB=tr["R"].to_numpy(); allp=all(v[0]>0 for v in m["per_year"].values())
                core="<==CORE" if (W==10 and cd==10 and rr==2.0) else ""
                print(f"  {W:2d} {cd:2d} {rr:.1f} | {m['N']:3d} {m['avgR']:+.3f} {m['PF']:.2f} {m['best5']:+.3f} {m['best10']:+.3f} "
                      f"{str(allp)[0]}    {rB[b0].mean():+.2f}  {rB[b1].mean():+.2f}  {(dc['disc_avgR'] if dc else 0):+.2f} {(dc['conf_avgR'] if dc else 0):+.2f} {core}")
    # core + delay + BASE
    ev,risk=events(h4,d1_up,disc,10,10)
    print(f"\n== CORE robustness (W10/cd10/rr2, N={len(ev)}) ==")
    for scen in ("BASE","STRESS"):
        tr=sb.simulate(h4,ev,-1,risk,rr=2.0,horizon=H,scenario=scen); m=sb.metrics(tr,h4,2.0)
        print(f"  {scen}: avgR={m['avgR']:+.3f} PF={m['PF']:.2f} WRt={m['WR_target']:.2f} maxDD={m['maxDD_R']:.1f} "
              f"best1={m['best1']:+.3f} medSL={m['med_sl_pips']:.0f}p tpm={m['trades_per_month']:.2f}")
    trd=ec.sim_rr(h4,ev,-1,risk,2.0,H,"STRESS",delay=1); md=sb.metrics(trd,h4,2.0)
    print(f"  +1bar delay: avgR={md['avgR']:+.3f} PF={md['PF']:.2f}")
    # CALIB 2020-21 readout (out-of-discovery, NOT validation)
    evc,riskc=events(h4,d1_up,calib,10,10)
    if len(evc)>=6:
        trc=sb.simulate(h4,evc,-1,riskc,rr=2.0,horizon=H,scenario="STRESS"); mc=sb.metrics(trc,h4,2.0)
        print(f"  CALIB 2020-21 readout: N={mc['N']} avgR={mc['avgR']:+.3f} PF={mc['PF']:.2f} (out-of-discovery, NOT validation)")
    else:
        print(f"  CALIB 2020-21 readout: N={len(evc)} (too few)")
    # OVERLAP vs frozen H4-bo-raw-S (same b0/b1 population, also SHORT)
    pkg=os.path.join(hd._HERE,"h4boraws_package.json")
    if os.path.exists(pkg):
        bo=json.load(open(pkg)); bo_days=set(pd.to_datetime([t["t_entry"] for t in bo["ledger"]],unit="s",utc=True).floor("D"))
        hf_days=set(pd.to_datetime(h4["time"].to_numpy()[ev+1],unit="s",utc=True).floor("D"))
        inter=len(bo_days & hf_days);
        print(f"\n== OVERLAP vs frozen H4-bo-raw-S (both SHORT on b0/b1) ==")
        print(f"  HF4 trade-days={len(hf_days)} H4-bo-raw-S days={len(bo_days)} shared-days={inter} "
              f"HF4-share={inter/max(len(hf_days),1):.2f} Jaccard={inter/max(len(bo_days|hf_days),1):.2f}")
    else:
        print("  (h4boraws_package.json not found for overlap)")

if __name__=="__main__":
    main()

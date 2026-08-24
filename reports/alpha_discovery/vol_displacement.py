"""vol_displacement.py — candidate VOL-1: VOLUME-CONFIRMED displacement continuation (genuinely-new dimension; all prior
mechanisms OHLC-only). Hypothesis: a large directional bar (displacement) with HIGH tick-volume = real participation ->
continuation; with LOW volume = fakeout. Causal volume normalization: vol_z = volume / TRAILING rolling-median(volume,V).shift(1)
(bars<t, no global stat). Displacement = |c-o|>=DISP*atr. Entry high-vol up-disp -> LONG, high-vol down-disp -> SHORT (continue).
Controls: low-vol displacement (should be worse if volume informs). Full gate (DISC/CONF/OOS, tail, per-year). STRESS, 1.5ATR, rr2.
Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
V=50; DISP=1.0

def run(m, idx, side, atr, label, verbose=True):
    n=len(m); idx=idx[idx<n-1]; dd=sb.dedup_events(idx,8); idx=idx[np.isin(idx,dd)]; sl=1.5*atr[idx]
    tr=sb.simulate(m,idx,side,sl,rr=2.0,horizon=96,scenario="STRESS")
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr
    if len(r)<40: print(f"  {label}: N={len(r)} thin"); return r,yr
    sr=np.sort(r); k1=max(1,len(r)//100); k10=max(1,len(r)//10)
    d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]; negyr=sum(1 for y in set(yr) if r[yr==y].mean()<0)
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0
    print(f"  {label}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} best1rm={sr[:-k1].mean():+.4f} best10rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {oos.mean():+.3f} negyr{negyr}/{len(set(yr))} -> {'SURVIVOR' if surv else 'no'}")
    return r,yr

def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); vol=m["volume"].to_numpy()
    # volume validity
    print(f"VOLUME check: nonzero={np.mean(vol>0):.2f} median={np.median(vol[vol>0]):.0f} p10={np.percentile(vol[vol>0],10):.0f} p90={np.percentile(vol[vol>0],90):.0f}")
    vbase=pd.Series(vol).rolling(V).median().shift(1).to_numpy(); vz=vol/vbase
    up_disp=((c-o)>=DISP*atr)&np.isfinite(atr)&(atr>0)
    dn_disp=((o-c)>=DISP*atr)&np.isfinite(atr)&(atr>0)
    hv=vz>=1.5; lv=(vz<=0.8)&np.isfinite(vz)
    print(f"VOL-1 volume-confirmed displacement. up-disp={int(up_disp.sum())} dn-disp={int(dn_disp.sum())}")
    run(m, np.where(up_disp&hv)[0], 1, atr, "HIGH-vol UP-disp  LONG ")
    run(m, np.where(dn_disp&hv)[0], -1, atr, "HIGH-vol DN-disp  SHORT")
    print("  controls (low-vol displacement, should be worse if volume informs):")
    run(m, np.where(up_disp&lv)[0], 1, atr, "LOW-vol  UP-disp  LONG ", verbose=True)
    run(m, np.where(dn_disp&lv)[0], -1, atr, "LOW-vol  DN-disp  SHORT", verbose=True)
    # info: forward path high vs low vol displacement (short lens for dn, long for up) - quick fwdRet
    fret=(pd.Series(c).shift(-96).to_numpy()-c)/atr
    print("  info fwdRet(96): up-disp hi {:+.2f} lo {:+.2f} | dn-disp hi {:+.2f} lo {:+.2f}".format(
        np.nanmedian(fret[up_disp&hv]), np.nanmedian(fret[up_disp&lv]), np.nanmedian(fret[dn_disp&hv]), np.nanmedian(fret[dn_disp&lv])))

if __name__=="__main__":
    main()

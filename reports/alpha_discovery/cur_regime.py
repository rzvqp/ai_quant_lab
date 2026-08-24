"""cur_regime.py — CAUSAL multi-regime taxonomy for XAUUSD (mandate: MULTI-REGIME SPECIALIST PORTFOLIO, 2026-08-23).
Purpose: measure structurally-distinct H4 regimes so the NEXT specialist regime is selected from EVIDENCE, and every regime
label is CAUSALLY AUDITABLE (fixes the SIGNATURE_V1 global-percentile dependency flagged on CRS-1).

CAUSAL NORMALIZATION PROOF: every feature at bar t uses ONLY bars <= t.
- ema20/ema50, effic, atr from _feat (ewm/rolling+shift, causal).
- vol level = atr / TRAILING rolling-median(atr, W).shift(1)  -> baseline uses bars strictly < t (shift(1)); NO global stat.
- trend strength = (ema20-ema50)/atr (causal ratio).
- effic (net/path over 20 bars, shift(1)) causal.
Regime rules are FIXED thresholds on these causal features (no percentile over the whole history). A warmup (first WARM H4
bars = NaN baseline) is excluded (UNCLASSIFIED), never back-filled.

Axes: TREND {up: ema20>ema50 & effic>+E ; down: ema20<ema50 & effic<-E ; range: |effic|<R} x VOL {hi: ratio>=VHI ; lo: ratio<=VLO ; mid}.
Reports per regime: count, % of classified, #episodes (contiguous runs, >1 H4-bar gap = new), median episode len (H4 bars),
recency (% of regime bars in 2024+/2025+), and whether it overlaps CRS-1's turf (HIGHVOL_BEAR). Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD
W=360; WARM=400; VHI=1.20; VLO=0.90; E=0.30; R=0.15

def label_h4(h4):
    atr=h4["atr"].to_numpy(); e20=h4["ema20"].to_numpy(); e50=h4["ema50"].to_numpy(); eff=h4["effic"].to_numpy()
    base=pd.Series(atr).rolling(W).median().shift(1).to_numpy()   # causal trailing baseline (bars < t)
    vr=atr/base
    up=(e20>e50)&(eff>E); dn=(e20<e50)&(eff<-E); rng=np.abs(eff)<R
    vhi=vr>=VHI; vlo=vr<=VLO
    lab=np.full(len(h4),"UNCLASSIFIED",dtype=object)
    valid=np.isfinite(vr)&np.isfinite(eff)&(np.arange(len(h4))>=WARM)
    def setr(mask,name): lab[valid&mask]=name
    setr(up&vlo,"LOWVOL_BULL"); setr(up&vhi,"HIGHVOL_BULL")
    setr(dn&vlo,"LOWVOL_BEAR"); setr(dn&vhi,"HIGHVOL_BEAR")
    setr(rng&vlo,"RANGE_LOWVOL"); setr(rng&vhi,"RANGE_HIGHVOL")
    # mid-vol trend/range -> generic buckets so nothing silently drops
    setr(up&~vhi&~vlo,"MIDVOL_BULL"); setr(dn&~vhi&~vlo,"MIDVOL_BEAR"); setr(rng&~vhi&~vlo,"RANGE_MIDVOL")
    return lab, vr

def episodes(mask):
    idx=np.where(mask)[0]
    if len(idx)==0: return 0,0
    gaps=np.diff(idx); nep=1+int((gaps>1).sum())
    # episode lengths
    lens=[]; start=idx[0]; prev=idx[0]
    for i in idx[1:]:
        if i-prev>1: lens.append(prev-start+1); start=i
        prev=i
    lens.append(prev-start+1)
    return nep, int(np.median(lens))

def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4"); lab,vr=label_h4(h4)
    yr=h4["dt"].dt.year.to_numpy(); nclass=int((lab!="UNCLASSIFIED").sum())
    print(f"CAUSAL REGIME TAXONOMY (H4, causal trailing-median vol baseline W={W}, warmup {WARM}). classified {nclass}/{len(h4)} H4 bars.")
    print(f"{'regime':16s} {'count':>6s} {'%cls':>6s} {'#epis':>6s} {'medLen':>7s} {'%2024+':>7s} {'%2025+':>7s}")
    order=["LOWVOL_BULL","MIDVOL_BULL","HIGHVOL_BULL","RANGE_LOWVOL","RANGE_MIDVOL","RANGE_HIGHVOL","LOWVOL_BEAR","MIDVOL_BEAR","HIGHVOL_BEAR"]
    for nm in order:
        mask=lab==nm; c=int(mask.sum())
        if c==0: print(f"{nm:16s} {0:>6d}"); continue
        nep,ml=episodes(mask); r24=float(((yr>=2024)&mask).sum())/c; r25=float(((yr>=2025)&mask).sum())/c
        print(f"{nm:16s} {c:>6d} {100*c/nclass:>5.1f}% {nep:>6d} {ml:>7d} {100*r24:>6.1f}% {100*r25:>6.1f}%")
    # per-year dominant regime (structural map)
    print("\nDominant regime by year:")
    for y in range(2012,2027):
        ym=yr==y;
        if ym.sum()<50: continue
        from collections import Counter; cc=Counter(lab[ym & (lab!='UNCLASSIFIED')])
        top=" ".join(f"{k.split('_')[0][:3]}{k.split('_')[1][:2] if '_' in k else ''}:{v*100//max(1,ym.sum())}%" for k,v in cc.most_common(3))
        print(f"  {y}: {top}")

if __name__=="__main__":
    main()

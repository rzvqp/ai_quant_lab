"""dxy_voltime.py — DXY_INCREMENTAL_INFORMATION_DISCOVERY_V1. NEW angle the prior DXY frontier did NOT test: NON-DIRECTIONAL
incremental information (timing/magnitude/hazard), and specifically on the XAU compression->expansion state (VOLTIME-1). Prior DXY
work was DIRECTIONAL-only and sign-inverted across eras (NOT_SUPPORTED). Magnitude/timing have NO sign to invert -> a DXY vol signal
could be cross-era-stable where DXY->direction was not.

PREREGISTERED HYPOTHESES (economic rationale, no mining):
 H-NDX1 (primary, non-directional): XAU and DXY both respond to macro shocks. Within XAU-compressed bars, a causal DXY VOL-EXPANSION
   (d_vr_l0 high) or DXY IMPULSE (|d_imp_l0| large) predicts a LARGER/FASTER XAU expansion than XAU-compression alone. Direction-free.
   Test: information delta P(2R timing)/fwdRange/medT2R for (XAU-comp & DXY-vol-high) vs (XAU-comp & DXY-vol-low) and vs XAU-comp base.
 H-DIR1 (secondary, expected era-inverting per prior): within XAU-comp, does causal DXY d_ret1_l0 sign resolve the XAU expansion
   direction? (Prior: inverts b0/b1 vs y2123 — measure at the compression setup specifically.)
Causal: DXY features are lag0 = last-closed DXY H1 bar at the XAU decision (contract enforced by dxy_data.align). Blocks b0/b1/y2123
(all <=2023-12-29; 2024+ PROTECTED, never loaded). Baseline = XAU price-only. Cross-block sign-stability is the gate."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import dxy_data as DX
K=8  # forward horizon in H1 bars (8h) = matches the M15 K=32 VOLTIME window
def xau_feats(m):
    c=m["close"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); n=len(c)
    tr=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1)))); tr[0]=h[0]-l[0]
    atr=pd.Series(tr).rolling(14).mean().to_numpy(); atr_ma=pd.Series(atr).rolling(30).mean().shift(1).to_numpy()
    comp=(atr<atr_ma).astype(float); comp_dur=np.zeros(n)
    for i in range(1,n): comp_dur[i]=comp_dur[i-1]+1 if comp[i]>0 else 0
    fhi=pd.Series(h).rolling(K).max().shift(-K).to_numpy(); flo=pd.Series(l).rolling(K).min().shift(-K).to_numpy()
    fwd_range=np.where(atr>0,(fhi-flo)/atr,np.nan)
    # P(2R either dir within K) + time-to-2R + forward direction (sign of larger excursion)
    p2=np.full(n,np.nan); t2=np.full(n,np.nan); fdir=np.full(n,np.nan)
    for i in range(n-K-1):
        if not np.isfinite(atr[i]) or atr[i]<=0: continue
        tg=2*atr[i]; sh=h[i+1:i+1+K]-c[i]; sl=c[i]-l[i+1:i+1+K]
        up=np.where(sh>=tg)[0]; dn=np.where(sl>=tg)[0]; fu=up[0] if len(up) else 10**9; fd=dn[0] if len(dn) else 10**9
        f=min(fu,fd)
        if f<10**9: p2[i]=1; t2[i]=f; fdir[i]=1 if fu<fd else -1
        else: p2[i]=0
        # eventual direction by net K move sign (magnitude resolution)
        if not np.isfinite(fdir[i]): fdir[i]=np.sign(c[i+K]-c[i]) if i+K<n else np.nan
    return dict(atr=atr,comp_dur=comp_dur,fwd_range=fwd_range,p2=p2,t2=t2,fdir=fdir,c=c)
def main():
    frames=DX.build()
    print(f"DXY-VOLTIME incremental (K={K}h). Blocks b0/b1/y2123 (<=2023-12-29, 2024+ PROTECTED). XAU-only baseline vs +DXY state.")
    print("H-NDX1 non-directional: does DXY vol-expansion add to XAU expansion magnitude/timing WITHIN XAU-compressed bars?\n")
    def rate(v,idx): return np.nanmean(v[idx]) if len(idx) else float('nan')
    results={}
    for era,m in frames.items():
        f=xau_feats(m)
        d_vr=m["d_vr_l0"].to_numpy(); d_imp=np.abs(m["d_imp_l0"].to_numpy()); d_ret1=m["d_ret1_l0"].to_numpy()
        comp=(f["comp_dur"]>=6)&np.isfinite(f["fwd_range"])&np.isfinite(d_vr)   # XAU compressed + DXY available
        base=np.where(comp)[0]
        if len(base)<150: print(f"  {era}: n(comp)={len(base)} thin"); continue
        # DXY vol-high vs vol-low within compressed (median split, DISC-free per-era median = descriptive, not tuned)
        thr=np.nanmedian(d_vr[base]); hi=base[d_vr[base]>=thr]; lo=base[d_vr[base]<thr]
        # DXY impulse-high vs low
        ithr=np.nanmedian(d_imp[base]); ih=base[d_imp[base]>=ithr]; il=base[d_imp[base]<ithr]
        bR=rate(f["fwd_range"],base); bP=rate(f["p2"],base); bT=np.nanmedian(f["t2"][base])
        hR=rate(f["fwd_range"],hi); hP=rate(f["p2"],hi); hT=np.nanmedian(f["t2"][hi])
        lR=rate(f["fwd_range"],lo); lP=rate(f["p2"],lo)
        iR=rate(f["fwd_range"],ih); iP=rate(f["p2"],ih)
        print(f"  [{era}] XAU-comp base(n={len(base)}): fwdRange={bR:.2f} P2R={bP:.3f} medT2R={bT:.1f}")
        print(f"     +DXY vol-HIGH(n={len(hi)}): fwdRange={hR:.2f}(d{hR-bR:+.2f}) P2R={hP:.3f}(d{hP-bP:+.3f}) medT2R={hT:.1f} | vol-LOW fwdRange={lR:.2f} P2R={lP:.3f}")
        print(f"     +DXY imp-HIGH(n={len(ih)}): fwdRange={iR:.2f}(d{iR-bR:+.2f}) P2R={iP:.3f}(d{iP-bP:+.3f})")
        results[era]=dict(dR_vol=hR-lR, dP_vol=hP-lP, dR_imp=iR-bR)
        # H-DIR1: DXY d_ret1 sign -> XAU expansion direction (expect era-invert). corr sign.
        okd=base[np.isfinite(d_ret1[base])&np.isfinite(f["fdir"][base])]
        if len(okd)>100:
            # DXY up (d_ret1>0) should -> XAU down (fdir<0) if inverse holds
            dxup=okd[d_ret1[okd]>0]; dxdn=okd[d_ret1[okd]<0]
            pdown_when_dxup=np.mean(f["fdir"][dxup]<0) if len(dxup)>30 else float('nan')
            pup_when_dxdn=np.mean(f["fdir"][dxdn]>0) if len(dxdn)>30 else float('nan')
            print(f"     H-DIR1: P(XAU down | DXY up)={pdown_when_dxup:.3f}  P(XAU up | DXY dn)={pup_when_dxdn:.3f}  (0.5=no info; >0.5=inverse holds)")
    # cross-block stability of the non-directional delta
    if len(results)==3:
        dRv=[results[e]["dR_vol"] for e in ["b0","b1","y2123"]]; dPv=[results[e]["dP_vol"] for e in ["b0","b1","y2123"]]
        stable=all(x>0 for x in dRv) or all(x<0 for x in dRv)
        print(f"\nCROSS-BLOCK non-directional delta (DXY vol-high vs vol-low): dFwdRange b0/b1/y2123 = {dRv[0]:+.2f}/{dRv[1]:+.2f}/{dRv[2]:+.2f}  SIGN-STABLE={stable}")
        print(f"  dP2R = {dPv[0]:+.3f}/{dPv[1]:+.3f}/{dPv[2]:+.3f}")
        print("=> if the non-directional delta is MATERIAL and SIGN-STABLE across all 3 blocks, DXY adds real timing/magnitude info")
        print("   (unlike DXY->direction which inverts). That would be the first stable DXY incremental signal -> preregister+robustness.")
if __name__=="__main__": main()

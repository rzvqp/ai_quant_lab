"""dxy_incremental.py — DECISIVE §7-style test: are the sign-stable DXY non-directional deltas (dxy_voltime.py) genuinely
INCREMENTAL over XAU's OWN concurrent volatility/impulse state, or REDUNDANT (DXY just re-encoding XAU vol via contemporaneous
coupling)? Within XAU-compressed bars, CONTROL for XAU-own vol-ratio (terciles); within each control cell, measure the RESIDUAL DXY
delta on forward expansion (fwdRange, P2R). If the DXY delta persists across XAU-vol terciles AND is material AND sign-stable across
b0/b1/y2123 -> genuine incremental information. If it collapses once XAU-own-vol is controlled -> redundant. Causal (DXY lag0). 2024+
PROTECTED. Same K=8h forward window."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import dxy_data as DX
from dxy_voltime import xau_feats, K
def main():
    frames=DX.build()
    print(f"DXY §7 INCREMENTAL test (K={K}h): DXY delta on XAU forward expansion, CONTROLLING for XAU-own vol-ratio terciles.")
    print("Redundant if DXY effect vanishes after controlling XAU-own vol; genuine if it persists + sign-stable cross-block.\n")
    agg={}
    for era,m in frames.items():
        f=xau_feats(m); atr=f["atr"]
        # XAU own vol-ratio (concurrent state)
        atr_ma=pd.Series(atr).rolling(30).mean().shift(1).to_numpy(); xvr=np.where(atr_ma>0,atr/atr_ma,np.nan)
        d_vr=m["d_vr_l0"].to_numpy(); d_imp=np.abs(m["d_imp_l0"].to_numpy())
        comp=(f["comp_dur"]>=6)&np.isfinite(f["fwd_range"])&np.isfinite(d_imp)&np.isfinite(xvr)
        base_all=np.where(comp)[0]
        # EVENT-DEDUP: non-overlapping forward windows (>=K apart) to kill autocorrelation-inflated effective-N
        base=[]; last=-10**9
        for i in base_all:
            if i-last>=K: base.append(i); last=i
        base=np.array(base,int)
        if len(base)<200: print(f"  {era}: thin (deduped n={len(base)})"); continue
        print(f"  [{era}] deduped events n={len(base)} (from {len(base_all)} overlapping)")
        # XAU-own vol terciles (within compressed)
        q=np.nanquantile(xvr[base],[0.33,0.66])
        t1=base[xvr[base]<q[0]]; t2=base[(xvr[base]>=q[0])&(xvr[base]<q[1])]; t3=base[xvr[base]>=q[1]]
        print(f"  [{era}] (n_comp={len(base)}) — within each XAU-own-vol tercile, DXY-impulse HIGH vs LOW -> dP2R (residual DXY effect):")
        dImp_res=[]
        for name,tc in [("Tlo",t1),("Tmid",t2),("Thi",t3)]:
            if len(tc)<80: print(f"     {name}: thin"); continue
            ith=np.nanmedian(d_imp[tc]); ih=tc[d_imp[tc]>=ith]; il=tc[d_imp[tc]<ith]
            dP=np.nanmean(f["p2"][ih])-np.nanmean(f["p2"][il]); dR=np.nanmean(f["fwd_range"][ih])-np.nanmean(f["fwd_range"][il])
            dImp_res.append(dP)
            print(f"     {name}(n={len(tc)}): DXY-imp dP2R={dP:+.3f} dFwdRange={dR:+.2f}")
        agg[era]=np.nanmean(dImp_res) if dImp_res else float('nan')
    if len(agg)==3:
        v=[agg[e] for e in ["b0","b1","y2123"]]
        stable=(all(x>0.01 for x in v) or all(x<-0.01 for x in v))
        print(f"\nRESIDUAL DXY-impulse dP2R (avg across XAU-vol terciles) b0/b1/y2123 = {v[0]:+.3f}/{v[1]:+.3f}/{v[2]:+.3f}")
        print(f"  material(|>0.03| all) = {all(abs(x)>0.03 for x in v)} ; sign-stable = {stable}")
        print("  => if residual DXY-impulse effect is material + sign-stable AFTER controlling XAU-own-vol, DXY carries GENUINE")
        print("     incremental non-directional info -> preregister DXY-timing mechanism + robustness. Else REDUNDANT with XAU vol.")
if __name__=="__main__": main()

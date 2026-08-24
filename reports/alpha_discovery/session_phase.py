"""session_phase.py — SESSION_TIMING_LIQUIDITY_DISCOVERY_V1 family-5 (+ diurnal opportunity structure). NON-DIRECTIONAL: does
opportunity quality fall during the London-lunch/pre-US quiet and improve into US participation? A useful NO_TRADE window is a valid
edge. Phase = session-relative (DST-correct), from the London-open & US-macro anchors. Per phase measure (forward K=8 bars=2h, no
direction): forward-range/ATR, P(reach 1.5ATR either dir), median time-to-1.5ATR (bars), WHIPSAW rate (both +1ATR AND -1ATR hit within
K = chop). Per era D<=2018/C19-22/O23+ for stability. cur_data M15 UTC."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import cur_data as CD
import session_tz as STZ
K=8
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); ts=m["time"].to_numpy(); n=len(m); yr=m["dt"].dt.year.to_numpy(); dd=m["dt"].dt.date.to_numpy()
    amaps=STZ.build_anchor_maps(dd); lo_map=amaps["london_open"]; us_map=amaps["us_macro"]; ny_map=amaps["nyse_open"]
    # per-bar session phase (DST-correct, session-relative)
    phase=np.array(["OTHER"]*n,dtype=object)
    for i in range(n):
        d=dd[i]; lo=lo_map.get(d); us=us_map.get(d); t=ts[i]
        if lo is None or us is None: continue
        if t<lo: phase[i]="1_ASIA"
        elif t<lo+3*3600: phase[i]="2_LDN_AM"
        elif t<us: phase[i]="3_LDN_LUNCH_preUS"
        elif t<us+3600: phase[i]="4_US_MACRO"
        elif t<us+4*3600: phase[i]="5_US_SESSION"
        else: phase[i]="6_LATE"
    # forward non-directional metrics
    fhi=pd.Series(h).rolling(K).max().shift(-K).to_numpy(); flo=pd.Series(l).rolling(K).min().shift(-K).to_numpy()
    fwd_range=np.where(atr>0,(fhi-flo)/atr,np.nan)
    pmove=np.full(n,np.nan); tmove=np.full(n,np.nan); whip=np.full(n,np.nan)
    for i in range(n-K-1):
        if not np.isfinite(atr[i]) or atr[i]<=0: continue
        a=atr[i]; sh=h[i+1:i+1+K]-c[i]; sl=c[i]-l[i+1:i+1+K]
        up15=np.where(sh>=1.5*a)[0]; dn15=np.where(sl>=1.5*a)[0]
        fu=up15[0] if len(up15) else 10**9; fd=dn15[0] if len(dn15) else 10**9
        f=min(fu,fd); pmove[i]=1 if f<10**9 else 0
        if f<10**9: tmove[i]=f
        up1=(sh>=1.0*a).any(); dn1=(sl>=1.0*a).any(); whip[i]=1 if (up1 and dn1) else 0
    era=np.where(yr<=2018,"D",np.where(yr<=2022,"C","O"))
    valid=np.isfinite(fwd_range)&(atr>0); valid[:250]=False; valid[n-K-1:]=False
    def summ(mask):
        idx=np.where(mask&valid)[0]
        if len(idx)<300: return f"n={len(idx)}(thin)"
        return (f"n={len(idx):6d} fwdRange={np.mean(fwd_range[idx]):.2f} P(1.5ATR)={np.nanmean(pmove[idx]):.3f} "
                f"medT={np.nanmedian(tmove[idx]):.1f}b whipsaw={np.nanmean(whip[idx]):.3f}")
    order=["1_ASIA","2_LDN_AM","3_LDN_LUNCH_preUS","4_US_MACRO","5_US_SESSION","6_LATE"]
    print(f"SESSION-PHASE opportunity structure (K={K}b=2h fwd, non-directional). Higher fwdRange/P(move) + lower whipsaw = better window.")
    print("Baseline: "+summ(np.ones(n,bool)))
    for ph in order:
        print(f"  {ph:20s}: "+summ(phase==ph))
    print("\nCROSS-ERA stability (fwdRange | P(1.5ATR) | whipsaw) for key phases:")
    for ph in ["3_LDN_LUNCH_preUS","4_US_MACRO","5_US_SESSION"]:
        cells=" ".join(f"{e}[{np.mean(fwd_range[(phase==ph)&(era==e)&valid]):.2f}/{np.nanmean(pmove[(phase==ph)&(era==e)&valid]):.2f}/{np.nanmean(whip[(phase==ph)&(era==e)&valid]):.2f}]" for e in ["D","C","O"])
        print(f"  {ph:20s}: {cells}")
    print("\n=> a phase with materially LOW fwdRange/P(move) + HIGH whipsaw, cross-era-stable, is a valid NO_TRADE window discovery;")
    print("   a phase with HIGH fwdRange/P(move) + LOW whipsaw concentrates opportunity (where a direction-mechanism like S5 should live).")
if __name__=="__main__": main()

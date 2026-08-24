"""range_fade.py — RANGE-regime specialist discovery (candidate RS-1). Re-screens the old REVERSION/fade mechanism — which
failed UNCONDITIONALLY — now GATED to the FROZEN causal RANGE_REGIME_V1 (new identity per mandate §6). Natural range play:
on a touch of the range boundary while the regime is ON, fade back toward the MID, with a STRUCTURAL stop beyond the boundary
(range break = thesis dead -> caps the fade's tail-loss). Two-sided (long at lower boundary, short at upper).

Entry (M15, causal): in_range AND high>=rhi-TB*width -> SHORT ; in_range AND low<=rlo+TB*width -> LONG. Stop beyond boundary
= SM*width outside the box. Target = range MID. Horizon 48 M15 bars. STRESS. dedup 8. Skepticism gate: per-year, DISC/CONF/OOS
all>0 (within RANGE population), tail (best AND worst 10% removed — fades have inverted tails), neighbor (TB,SM), both sides>0,
regime-specificity (same fade when NOT in-range must be worse), effective N / episodes. Ratified sb.simulate. Data thru 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
import range_regime as RR
TB=0.10; SM=0.25; H=48

def build(m):
    h4=CD.agg(m,"H4"); inr,rlo,rhi=RR.build_h4_range(h4)
    i,lo_,hi_,mid_=RR.map_to_m15(m,h4,inr,rlo,rhi)
    return i,lo_,hi_,mid_

def entries(m,i,lo_,hi_,mid_,gated=True):
    hi=m["high"].to_numpy(); lo=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    if gated:
        wid=hi_-lo_; RLO=lo_; RHI=hi_; MID=mid_; reg=(i==1)&np.isfinite(wid)&(wid>0)
    else:
        # regime-specificity control: an ALWAYS-ON rolling box (same L window) regardless of regime state
        RHI=pd.Series(hi).rolling(48).max().shift(1).to_numpy(); RLO=pd.Series(lo).rolling(48).min().shift(1).to_numpy()
        wid=RHI-RLO; MID=(RHI+RLO)/2.0; reg=(i!=1)&np.isfinite(wid)&(wid>0)   # NOT in-range = trend/other
    floor=0.5*atr
    # SHORT fade: touched upper boundary AND closed back INSIDE (rejection, not breakout)
    up=reg&(hi>=RHI-TB*wid)&(c<RHI)
    dn=reg&(lo<=RLO+TB*wid)&(c>RLO)
    S=np.where(up)[0]; Lg=np.where(dn)[0]; S=S[S<n-1]; Lg=Lg[Lg<n-1]
    sl_S=np.maximum((RHI[S]+SM*wid[S])-c[S], floor[S]); tg_S=c[S]-MID[S]
    sl_L=np.maximum(c[Lg]-(RLO[Lg]-SM*wid[Lg]), floor[Lg]); tg_L=MID[Lg]-c[Lg]
    return (S,sl_S,tg_S),(Lg,sl_L,tg_L)

def sim_side(m,idx,sl,tg,side,dedup=8):
    good=np.isfinite(sl)&np.isfinite(tg)&(sl>0)&(tg>0)
    idx=idx[good]; sl=sl[good]; tg=tg[good]
    if len(idx)==0: return np.array([]),np.array([])
    dd=sb.dedup_events(idx,dedup); p=np.isin(idx,dd); idx=idx[p]; sl=sl[p]; tg=tg[p]
    rr=float(np.clip(np.median(tg/np.maximum(sl,1e-9)),0.3,3.0))
    tr=sb.simulate(m,idx,side,sl,rr=rr,horizon=H,scenario="STRESS")
    r=tr["R"].to_numpy(); yr=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
    return r,yr

def report(name,rS,yS,rL,yL):
    r=np.concatenate([rS,rL]); yr=np.concatenate([yS,yL]); sd=np.concatenate([np.full(len(rS),-1),np.full(len(rL),1)])
    if len(r)<40: print(f"{name}: N={len(r)} thin"); return r,yr
    sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    both=len(rS)>=20 and len(rL)>=20 and rS.mean()>0 and rL.mean()>0
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0 and sr[k10:].mean()>0 and both
    print(f"{name}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} | short {rS.mean():+.3f}(n{len(rS)}) long {rL.mean():+.3f}(n{len(rL)})")
    print(f"  best10%rm={sr[:-k10].mean():+.4f} worst10%rm={sr[k10:].mean():+.4f} worst={sr[0]:+.2f} | D {d.mean():+.3f}(n{len(d)}) C {cf.mean():+.3f}(n{len(cf)}) O {oos.mean():+.3f}(n{len(oos)}) -> {'SURVIVOR' if surv else 'no'}")
    return r,yr

def main():
    m=CD.load_m15(); i,lo_,hi_,mid_=build(m)
    print(f"RANGE-FADE specialist (RS-1 candidate), gated to {RR.FP}")
    (S,slS,tgS),(Lg,slL,tgL)=entries(m,i,lo_,hi_,mid_,gated=True)
    rS,yS=sim_side(m,S,slS,tgS,-1); rL,yL=sim_side(m,Lg,slL,tgL,1)
    report("  GATED (in-range fade)   ",rS,yS,rL,yL)
    (S2,slS2,tgS2),(Lg2,slL2,tgL2)=entries(m,i,lo_,hi_,mid_,gated=False)
    rS2,yS2=sim_side(m,S2,slS2,tgS2,-1); rL2,yL2=sim_side(m,Lg2,slL2,tgL2,1)
    report("  UNGATED (regime-spec chk)",rS2,yS2,rL2,yL2)
    print("  (gated should beat ungated => the RANGE regime materially matters)")

if __name__=="__main__":
    main()

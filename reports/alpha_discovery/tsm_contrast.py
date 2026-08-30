"""tsm_contrast.py — TEMPORAL_SEQUENCE_MINING_V1 Phase 1-2: matched-state PATH contrast + information value.

Central question (§8): among anchors with SIMILAR current state, does the preceding PATH (order/trajectory) shift the outcome?
Two outcome framings:
  (a) UP/DOWN absolute directional resolution  P(up_first)
  (b) CONTINUE/REVERSE relative to the path's own net direction  P(continue)  <- the monetizable framing
Baseline = P(outcome | current-state cell). Sequence = P(outcome | cell + path-motif bin). Incremental = within-cell spread.
Positive control = a FUTURE-return "motif" that MUST separate (proves the test has power). Chronological DEV(<=2019)/OOS(2020+).
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import tsm_core as TC

def build_anchors(P):
    """AN1 = fresh RANGE_EDGE arrival (close enters top/bottom 15% of rolling-20 range) — broad continue/reverse decision surface,
    NOT limited to the falsified structural-break population. Deduped to fresh arrivals (rng crosses into the extreme zone)."""
    rng=P["rng"]; n=P["n"]
    hot=(rng>0.85)|(rng<0.15)
    fresh=np.zeros(n,bool); prev=False
    for i in range(n):
        if hot[i] and not prev: fresh[i]=True
        prev=hot[i]
    idx=np.where(fresh)[0]
    idx=idx[(idx>400)&(idx<n-64)]
    return idx

def state_cell(P, t, netdir):
    """Coarse CURRENT-STATE cell (the baseline the path must beat): range-third x vol-state x htf x session x anchor-dir."""
    rng=P["rng"][t]; rb= 0 if rng<0.34 else (1 if rng<0.67 else 2)
    v=P["atr"][t]/P["atr_ma"][t] if P["atr_ma"][t]>0 else 1.0; vb=0 if v<0.9 else (1 if v<1.3 else 2)
    return (rb, vb, int(P["htf"][t]), P["sess"](t), int(netdir))

def main():
    P=TC.load_panel(); n=P["n"]; yr=P["yr"]
    L=32; b=1.5; H=32
    idx=build_anchors(P)
    print(f"AN1 RANGE_EDGE anchors={len(idx)}")
    # path features + outcome
    pf=TC.path_features(P, idx, L)
    lab,ttr,mfe,mae=TC.triple_barrier(P, idx, b=b, H=H)
    keep=np.array([i for i,(x,f) in enumerate(zip(idx,pf)) if f is not None and np.isfinite(f["net"])])
    idx=idx[keep]; pf=[pf[i] for i in keep]; lab=lab[keep]; ttr=ttr[keep]; mfe=mfe[keep]; mae=mae[keep]
    netL=np.array([f["net"] for f in pf]); pdir=np.sign(netL); pdir[pdir==0]=1
    up_first=(lab>0).astype(int); resolved=(lab!=0)
    cont=np.where(lab==0,0, np.where(((pdir>0)&(lab>0))|((pdir<0)&(lab<0)),1,-1))  # +1 continue, -1 reverse, 0 unresolved
    # motif features
    F={k:np.array([f[k] for f in pf],float) for k in ["eff","sc","energy_late","argH","argL","pull","rc","net_r"]}
    # positive control: FUTURE 3-bar return sign (leakage motif — MUST separate)
    c=P["c"]; fut3=np.array([ (c[min(t+3,n-1)]-c[t]) for t in idx ],float)
    F["_POSCTRL_fut3"]=fut3
    era=np.array([P["era"](t) for t in idx]); dev=(yr[idx]<=2019); oos=~dev
    print(f"usable anchors={len(idx)} resolved={resolved.mean():.3f}  base P(up)={up_first[resolved].mean():.4f}  base P(continue)={ (cont[resolved]>0).mean():.4f}")

    # cell index
    cells=np.array([hash(state_cell(P,t,pdir[k])) for k,t in enumerate(idx)])
    def within_cell_spread(feat, outcome_pos, mask):
        """Within each state cell, split feat by median; report outcome_pos-rate(high)-rate(low) pooled across cells (state-controlled)."""
        hi_n=hi_p=lo_n=lo_p=0
        for cel in np.unique(cells[mask]):
            m=mask&(cells==cel)
            if m.sum()<20: continue
            fv=feat[m]; ov=outcome_pos[m]; med=np.median(fv)
            hi=fv>med; lo=fv<=med
            if hi.sum()<5 or lo.sum()<5: continue
            hi_p+=ov[hi].sum(); hi_n+=hi.sum(); lo_p+=ov[lo].sum(); lo_n+=lo.sum()
        if hi_n<50 or lo_n<50: return np.nan,np.nan,np.nan,0
        rh=hi_p/hi_n; rl=lo_p/lo_n; return rh-rl, rh, rl, hi_n+lo_n

    print("\n== INFORMATION TEST: within-state-cell outcome spread by PATH motif (high-tercile vs low, state-controlled) ==")
    print(f"{'motif':16s} {'frame':9s} {'ALL Δ':>8s} {'DEV Δ':>8s} {'OOS Δ':>8s} {'D Δ':>7s} {'C Δ':>7s} {'O Δ':>7s}  N")
    res_mask=resolved
    for fname,feat in F.items():
        for frame,opos in [("up/down",up_first),("continue",(cont>0).astype(int))]:
            dA,_,_,NA=within_cell_spread(feat,opos,res_mask)
            dD,_,_,_=within_cell_spread(feat,opos,res_mask&dev)
            dO,_,_,_=within_cell_spread(feat,opos,res_mask&oos)
            de,_,_,_=within_cell_spread(feat,opos,res_mask&(era=="D"))
            dc,_,_,_=within_cell_spread(feat,opos,res_mask&(era=="C"))
            do,_,_,_=within_cell_spread(feat,opos,res_mask&(era=="O"))
            def s(x): return f"{x:+.3f}" if np.isfinite(x) else "  nan "
            print(f"{fname:16s} {frame:9s} {s(dA):>8s} {s(dD):>8s} {s(dO):>8s} {s(de):>7s} {s(dc):>7s} {s(do):>7s}  {NA}")
    # independent-episode count for honest N
    ie=TC.independent_episodes(idx, H)
    print(f"\nINDEPENDENT_EPISODES(H={H})={len(ie)}  raw_anchors={len(idx)}  (ratio {len(ie)/len(idx):.2f})")

if __name__=="__main__":
    main()

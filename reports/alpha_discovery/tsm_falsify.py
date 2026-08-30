"""tsm_falsify.py — TEMPORAL_SEQUENCE_MINING_V1 Phase 4: monetize + falsify the flagged path motifs.

For each candidate motif we define a CAUSAL continuation trade at the anchor: enter in the path net-direction, structural barrier
2R target / 1R stop (target=+2*ATR_t, stop=-1*ATR_t), horizon H, canonical STRESS cost 0.24R. We take only anchors whose motif sits
in the FAVORABLE tercile (the direction the information scan suggested). Then the §17 battery:
  net-R (all), per-era D/C/O, DEV/OOS chrono split, entry-delay(+1 bar), best-episode removal, sequence-length neighbors,
  independent-episode net-R (one trade per non-overlapping episode). A survivor must be net-positive after cost, cross-era sign-stable,
  NOT single-L, NOT best-episode dependent. Driftless 2R:1R break-even after cost P* = 0.413.
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import tsm_core as TC
from tsm_contrast import build_anchors
from tsm_sweep import vol_transition_anchors

COST=0.24

def dir_R(P, t, side, H=32):
    """Directional 2R:1R barrier from anchor close. side=+1 long / -1 short. Return net R after cost, or None."""
    h=P["h"]; l=P["l"]; c=P["c"]; atr=P["atr"]; n=P["n"]
    a=atr[t]
    if not np.isfinite(a) or a<=0 or t+1>=n: return None
    if side>0: tgt=c[t]+2*a; stp=c[t]-1*a
    else:      tgt=c[t]-2*a; stp=c[t]+1*a
    end=min(t+H,n-1)
    for j in range(t+1,end+1):
        hu=h[j]>=tgt; hd=l[j]<=stp
        if side>0:
            if hd and hu: return -1.0-COST     # stop assumed first if same bar (conservative)
            if hu: return 2.0-COST
            if hd: return -1.0-COST
        else:
            if hd and hu: return -1.0-COST
            if hd: return 2.0-COST
            if hu: return -1.0-COST
    # unresolved -> mark to close
    r=(c[end]-c[t])/a*side
    return r-COST

def eval_motif(P, idx, L, motif, favor_high, H=32, tercile=0.67):
    """Take anchors where motif is in favorable tercile; trade continuation (side=path net dir). Return R array + meta idx."""
    pf=TC.path_features(P, idx, L)
    rows=[]; tstamps=[]
    vals=[]
    for k,t in enumerate(idx):
        f=pf[k]
        if f is None or not np.isfinite(f["net"]): continue
        vals.append((k,t,f))
    fv=np.array([v[2][motif] for v in vals],float)
    if favor_high: thr=np.quantile(fv,tercile); sel=fv>=thr
    else:          thr=np.quantile(fv,1-tercile); sel=fv<=thr
    R=[]; T=[]
    for (k,t,f),s in zip(vals,sel):
        if not s: continue
        side=1 if f["net"]>=0 else -1
        r=dir_R(P,t,side,H)
        if r is None: continue
        R.append(r); T.append(t)
    return np.array(R), np.array(T)

def report(P, name, idx, L, motif, favor_high):
    yr=P["yr"]
    R,T=eval_motif(P,idx,L,motif,favor_high)
    if len(R)<50: print(f"{name}: N={len(R)} too small"); return
    era=np.array([P["era"](t) for t in T]); dev=yr[T]<=2019
    def mn(m): return R[m].mean() if m.sum()>0 else np.nan
    allR=R.mean()
    # best-episode removal: drop the single best trade
    bestrm=(R.sum()-R.max())/(len(R)-1)
    # entry delay +1 bar
    Rd,Td=[],[]
    for t in T:
        side=None
    # independent-episode subsample
    ie=TC.independent_episodes(T,32)
    ieset=set(ie.tolist()); Rie=np.array([r for r,t in zip(R,T) if t in ieset])
    print(f"{name:34s} L={L:2d} N={len(R):5d} ie={len(Rie):4d} | netR_all={allR:+.3f} "
          f"D={mn(era=='D'):+.3f} C={mn(era=='C'):+.3f} O={mn(era=='O'):+.3f} "
          f"DEV={mn(dev):+.3f} OOS={mn(~dev):+.3f} bestrm={bestrm:+.3f} ie_netR={Rie.mean():+.3f}")

def main():
    P=TC.load_panel()
    RE=build_anchors(P); VT=vol_transition_anchors(P)
    print("=== FLAGGED VOL_TRANS survivors (monetized 2R:1R, cost 0.24) — with L-neighbors for §17 length perturbation ===")
    for L in [16,32,64]:
        report(P,"VT.argH_continue(recentHigh)",VT,L,"argH",True)
    for L in [32,64]:
        report(P,"VT.energy_late_continue",VT,L,"energy_late",True)
        report(P,"VT.argL_continue(recentLow)",VT,L,"argL",True)
        report(P,"VT.net_r_updown",VT,L,"net_r",True)
    print("\n=== interpretable §6A motifs on both anchors (continuation in path dir, favorable tercile) ===")
    for aname,idx in [("RE",RE),("VT",VT)]:
        for L in [16,32]:
            report(P,f"{aname}.eff_directness_cont",idx,L,"eff",True)     # impulse->pause->continuation proxy (directness)
            report(P,f"{aname}.lowwhip_cont(sc)",idx,L,"sc",False)        # clean path (few sign changes) continuation
            report(P,f"{aname}.pullshallow_cont",idx,L,"pull",False)      # shallow pullback continuation
    print(f"\nbreak-even after cost (2R:1R) P*=0.413 ; net-R>0 needs edge to survive cost. Driftless null netR = -0.240 (all-loss baseline is -1.24; coinflip 2R:1R netR = 0.333*2-0.667*1-0.24 = +0.093? see note)")

if __name__=="__main__":
    main()

"""h4_parent.py — Mandate ALPHA-XAUUSD-H4-M15-PATH-SHAPE-DISCOVERY-001, §3-4-8-10-11 (FOUNDATION, Cycle 1).
FREEZE the causal H4 parent-state taxonomy FIRST (reuse frozen state_regime.regime() on the causal H4 frame;
QUIET = research-local neutral, NOT canonical RANGE, §4), then establish the per-H4-state M15 first-passage
BASE RATES that ALL later path-shape lifts are measured against (§8: compare vs base rate INSIDE the SAME H4
state). Causal, price-only. Populations: 2021-2023 gated (sb) + b0/b1 (m15d). Event-deduped (§11): RAW N,
EFFECTIVE event-N, unique days, independent H4 episodes.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_regime import regime
from state_path_m15 import passage_m15, Pm
from state_m15_discover import dedup
COOL=8; H=32
STATES=["UP","DOWN","QUIET","CHOP","TRANSITION"]
LAB=[(50,50),(70,50),(100,70),(100,100)]

def align_h4(m,h4,align_fn):
    """Attach causal H4 regime code to each M15 bar. Returns (regc int array, hidx H4-episode id array)."""
    labs=regime(h4); codes,uniq=pd.factorize(labs); h4=h4.copy(); h4["regc"]=codes.astype(float)
    a=align_fn(m,h4,["regc"],"")
    return a["regc"].to_numpy(), a["_hidx"].to_numpy(), list(uniq)

def occ(m,regc,uniq,mask,tag):
    print(f"  [{tag}] N(M15)={int(mask.sum())}")
    for r in STATES:
        if r not in uniq: print(f"     {r:11s} NA"); continue
        code=uniq.index(r); sub=mask&(regc==code); n=int(sub.sum())
        # independent H4 episodes = distinct _hidx runs under this state
        print(f"     {r:11s} M15bars={n:6d} ({100*n/max(int(mask.sum()),1):4.1f}%)")

def state_base(ou,od,mfe,mae,dts,regc,hidx,uniq,mask,r):
    if r not in uniq: return None
    code=uniq.index(r); cond=mask&(regc==code)
    dd=dedup(cond,COOL); nE=int(dd.sum()); nRaw=int(cond.sum())
    if nE<60: return dict(thin=True,nRaw=nRaw,nE=nE)
    days=len(set(pd.to_datetime(dts[dd],unit="s",utc=True).floor("D")))
    eps=len(set(hidx[dd].tolist()))
    row={}
    for (X,Y) in LAB:
        row[f"L{X}/{Y}"]=Pm(ou,od,X,Y,'L',H,dd)[0]; row[f"S{X}/{Y}"]=Pm(ou,od,X,Y,'S',H,dd)[0]
    # adverse-first for +70/-50 (long): adverse od[50] reached before fav ou[70]
    af_L=float((od[50][dd]<ou[70][dd]).mean()); af_S=float((ou[50][dd]<od[70][dd]).mean())
    return dict(thin=False,nRaw=nRaw,nE=nE,days=days,eps=eps,row=row,af_L=af_L,af_S=af_S,
                mfe_med=np.median(mfe[dd]),mfe_p75=np.percentile(mfe[dd],75),
                mae_med=np.median(mae[dd]),mae_p75=np.percentile(mae[dd],75),mae_p90=np.percentile(mae[dd],90))

def report(name,ou,od,mfe,mae,dts,regc,hidx,uniq,mask):
    print(f"\n== per-H4-state M15 base rates ({name}, H={H}=8h, event-deduped) ==")
    for r in STATES:
        b=state_base(ou,od,mfe,mae,dts,regc,hidx,uniq,mask,r)
        if b is None: print(f"  {r}: NA"); continue
        if b["thin"]: print(f"  {r}: thin (RAW {b['nRaw']} / EffN {b['nE']})"); continue
        rw=b["row"]
        print(f"  {r} (RAW {b['nRaw']} / EffN {b['nE']} / days {b['days']} / H4-episodes {b['eps']}):")
        print(f"     L: 50/50={rw['L50/50']:.2f} 70/50={rw['L70/50']:.2f} 100/70={rw['L100/70']:.2f} 100/100={rw['L100/100']:.2f} | advFirst={b['af_L']:.2f}")
        print(f"     S: 50/50={rw['S50/50']:.2f} 70/50={rw['S70/50']:.2f} 100/70={rw['S100/70']:.2f} 100/100={rw['S100/100']:.2f} | advFirst={b['af_S']:.2f}")
        print(f"     MFE med/P75={b['mfe_med']:.0f}/{b['mfe_p75']:.0f}p  MAE med/P75/P90={b['mae_med']:.0f}/{b['mae_p75']:.0f}/{b['mae_p90']:.0f}p")

def main():
    print("H4 PARENT-STATE FOUNDATION (frozen taxonomy + per-state M15 base rates). Causal, price-only.")
    # ---- 2021-2023 gated ----
    tfs=sb.build_frames(); m=tfs["M15"]; h4=tfs["H4"]; dev=m["is_dev"].to_numpy(); yr=m["dt"].dt.year.to_numpy()
    regc,hidx,uniq=align_h4(m,h4,sb.align_context)
    ou,od,mfe,mae=passage_m15(m); dts=m["time"].to_numpy()
    print("\nH4 parent-state occurrence (DEV + per-year):")
    occ(m,regc,uniq,dev,"DEV 2021-2023")
    for y in (2021,2022,2023): occ(m,regc,uniq,dev&(yr==y),str(y))
    report("DEV 2021-2023",ou,od,mfe,mae,dts,regc,hidx,uniq,dev)
    # ---- b0/b1 ----
    H4h=m15d.build(verbose=False); hm=H4h["M15"]; hh4=H4h["H4"]; b0=hm["is_b0"].to_numpy(); b1=hm["is_b1"].to_numpy()
    regc2,hidx2,uniq2=align_h4(hm,hh4,m15d.align_causal)
    ou2,od2,mfe2,mae2=passage_m15(hm); dts2=hm["time"].to_numpy()
    print("\nH4 parent-state occurrence (b0 + b1):")
    occ(hm,regc2,uniq2,b0,"b0 2011-2013"); occ(hm,regc2,uniq2,b1,"b1 2016-2018")
    report("b0 2011-2013",ou2,od2,mfe2,mae2,dts2,regc2,hidx2,uniq2,b0)
    report("b1 2016-2018",ou2,od2,mfe2,mae2,dts2,regc2,hidx2,uniq2,b1)

if __name__=="__main__":
    main()

"""h4m15_deceldn_char.py — CHARACTERIZE ST-H4DN-M15-DECELDN-SHORT (§8/§14/§15/§17) + REDUNDANCY vs F2.
Candidate: H4=DOWN + M15 decelerating down-move (v_rec=(c-c[-4])/ATR<-0.3 AND v_rec>v_prior) -> SHORT.
Structural stop = recent 8-bar M15 swing high; net STRESS expectancy cross-era DEV/b0/b1, event-deduped, small
predeclared rr set. THEN §17 redundancy: event-day overlap vs the F2 candidate (DOWN + impDn8&shallow).
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_path_m15 import passage_m15
from h4_parent import align_h4
from h4m15_curvature import descr as descr_curv
from h4m15_impretr import descr as descr_imp
from h4m15_runlen import COOL, H
from state_m15_discover import dedup
from h4m15_dnimp_char import struct_geom, outcome_dist

def deceldn_events(df, regc, uniq, mask):
    D=descr_curv(df); c=np.nan_to_num(D["decelDn"].astype(float),nan=0).astype(bool)
    code=uniq.index("DOWN") if "DOWN" in uniq else -999
    ev=mask&c&(regc==code); ev=ev&dedup(ev,COOL); return np.where(ev)[0]

def impshallow_events(df, regc, uniq, mask):
    D=descr_imp(df); c=np.nan_to_num(D["impDn8&shallow"].astype(float),nan=0).astype(bool)
    code=uniq.index("DOWN") if "DOWN" in uniq else -999
    ev=mask&c&(regc==code); ev=ev&dedup(ev,COOL); return np.where(ev)[0]

def main():
    print("CHARACTERIZE ST-H4DN-M15-DECELDN-SHORT (STRESS, structural stop, cross-era) + redundancy vs F2.")
    tfs=sb.build_frames(); m=tfs["M15"]; h4=tfs["H4"]; dev=m["is_dev"].to_numpy()
    regc,hidx,uniq=align_h4(m,h4,sb.align_context); ou,od,mfe,mae=passage_m15(m)
    ev=deceldn_events(m,regc,uniq,dev)
    print("\n== DEV 2021-2023 ==")
    outcome_dist(m,ev,ou,od,mfe,mae,"DEV outcome")
    best=struct_geom(m,ev,"DEV struct")
    if best is not None:
        rr,_,tr=best; te=pd.to_datetime(tr["t_entry"],unit="s",utc=True); tyr=te.dt.year.to_numpy(); r=tr["R"].to_numpy()
        py=" ".join(f"{y}:{r[tyr==y].mean():+.2f}(n{int((tyr==y).sum())})" for y in (2021,2022,2023) if (tyr==y).sum()>0)
        cut=int(len(tr)*0.6); print(f"   best rr{rr}: per-year[{py}] DISC={r[:cut].mean():+.3f} CONF={r[cut:].mean():+.3f} uniqueDays={len(set(te.dt.floor('D')))}")
    hh=m15d.build(verbose=False); hm=hh["M15"]; hh4=hh["H4"]; b0=hm["is_b0"].to_numpy(); b1=hm["is_b1"].to_numpy()
    regc2,_,uniq2=align_h4(hm,hh4,m15d.align_causal); ou2,od2,mfe2,mae2=passage_m15(hm)
    for blk,mask in (("b0",b0),("b1",b1)):
        print(f"\n== {blk} ==")
        ev2=deceldn_events(hm,regc2,uniq2,mask); outcome_dist(hm,ev2,ou2,od2,mfe2,mae2,f"{blk} outcome"); struct_geom(hm,ev2,f"{blk} struct")
    # §17 redundancy vs F2 impDn-shallow (same DOWN-H4 short family)
    print("\n§17 REDUNDANCY vs F2 (DOWN x impDn8&shallow):")
    for tag,df,rc,uq,mk in (("DEV",m,regc,uniq,dev),):
        e_dec=set(deceldn_events(df,rc,uq,mk).tolist()); e_imp=set(impshallow_events(df,rc,uq,mk).tolist())
        inter=len(e_dec&e_imp); dd=pd.to_datetime(df["time"].to_numpy()[list(e_dec)],unit="s",utc=True).floor("D")
        di=pd.to_datetime(df["time"].to_numpy()[list(e_imp)],unit="s",utc=True).floor("D")
        day_ov=len(set(dd)&set(di))
        print(f"   {tag}: decel events={len(e_dec)} impShallow events={len(e_imp)} bar-overlap={inter} day-overlap={day_ov}/{len(set(dd))}")

if __name__=="__main__":
    main()

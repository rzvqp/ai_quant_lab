"""h4m15_dnimp_char.py — CHARACTERIZATION of ST-H4DN-M15DNIMP-SHALLOW-SHORT (§8/§14/§15/§16/§17).
Candidate: H4=DOWN + M15 down-impulse(imp8<-1.0)-shallow-retrace(rd_dn<0.30) -> SHORT continuation.
§8 full outcome distribution (MFE/MAE/adverse-first/P short); §15 STRUCTURAL stop = recent 8-bar M15 swing high
(the level that invalidates the continuation thesis; M15 does NOT own a tight stop) with a small predeclared
target set (NO forced RR mining); net STRESS expectancy cross-era DEV/b0/b1, event-deduped; §16 frequency;
§17 independence vs COMP-CONT-L. Price-only, causal.
"""
import numpy as np, pandas as pd, json, os
import swing_base as sb, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from h4_parent import align_h4
from h4m15_impretr import descr
from h4m15_runlen import COOL, H
from state_m15_discover import dedup

def cand_events(df, regc, uniq, mask):
    D=descr(df); cond=np.nan_to_num(D["impUp8&shallow"].astype(float),nan=0)  # placeholder to keep keys hot
    c=np.nan_to_num(D["impDn8&shallow"].astype(float),nan=0).astype(bool)
    code=uniq.index("DOWN") if "DOWN" in uniq else -999
    ev=mask&c&(regc==code)
    ev=ev&dedup(ev,COOL)
    return np.where(ev)[0]

def outcome_dist(df, ev, ou, od, mfe, mae, tag):
    n=len(ev)
    if n<40: print(f"  [{tag}] events={n} (thin)"); return
    Ps={f"+{X}/-{Y}":Pm(ou,od,X,Y,'S',H,_mask(len(df),ev))[0] for (X,Y) in [(50,50),(70,50),(100,70),(100,100)]}
    m=_mask(len(df),ev)
    af=float((ou[50][m]<od[70][m]).mean())  # short adverse-first: up(adverse) 50 before down(fav) 70
    # time-to first favorable +70 (down) and adverse +50 (up), medians among reached
    tf=od[70][m]; ta=ou[50][m]; tf=tf[np.isfinite(tf)]; ta=ta[np.isfinite(ta)]
    print(f"  [{tag}] events={n}  P short "+" ".join(f"{k}={v:.2f}" for k,v in Ps.items()))
    print(f"       MFE med/P75/P90={np.median(mfe[ev]):.0f}/{np.percentile(mfe[ev],75):.0f}/{np.percentile(mfe[ev],90):.0f}p"
          f"  MAE med/P75/P90={np.median(mae[ev]):.0f}/{np.percentile(mae[ev],75):.0f}/{np.percentile(mae[ev],90):.0f}p"
          f"  advFirst={af:.2f}  t2fav(med)={np.median(tf) if len(tf) else float('nan'):.0f}b t2adv(med)={np.median(ta) if len(ta) else float('nan'):.0f}b")

def _mask(n, ev):
    m=np.zeros(n,bool); m[ev]=True; return m

def struct_geom(df, ev, tag):
    o=df["open"].to_numpy(); hi8=df["high"].rolling(8).max().to_numpy()
    ev=ev[ev<len(df)-1]; entry=o[ev+1]; sl=hi8[ev]-entry  # structural stop = recent swing high above entry
    ok=np.isfinite(sl)&(sl>0); ev=ev[ok]; sl=sl[ok]
    print(f"  [{tag}] tradeable events={len(ev)}  structural SL med={np.median(sl)/0.10:.0f}p (recent 8-bar swing high)")
    best=None
    for rr in (1.0,1.5,2.0,3.0):
        tr=sb.simulate(df, ev, -1, sl, rr=rr, horizon=H, scenario="STRESS")
        if not len(tr): continue
        mm=sb.metrics(tr, df, rr)
        print(f"     struct-SL rr{rr}: avgR={mm['avgR']:+.3f} WR={mm['WR_pos']:.2f} best10={mm['best10']:+.3f} medSL={mm['med_sl_pips']:.0f}p tpm={mm['trades_per_month']:.1f}")
        if best is None or mm['avgR']>best[1]: best=(rr,mm['avgR'],tr)
    return best

def main():
    print("CHARACTERIZE ST-H4DN-M15DNIMP-SHALLOW-SHORT (STRESS, event-deduped, structural stop).")
    tfs=sb.build_frames(); m=tfs["M15"]; h4=tfs["H4"]; dev=m["is_dev"].to_numpy()
    regc,hidx,uniq=align_h4(m,h4,sb.align_context); ou,od,mfe,mae=passage_m15(m)
    ev=cand_events(m,regc,uniq,dev)
    print("\n== DEV 2021-2023 ==")
    outcome_dist(m,ev,ou,od,mfe,mae,"DEV outcome")
    best=struct_geom(m,ev,"DEV struct")
    # per-year + DISC/CONF on best rr
    if best is not None:
        rr,_,tr=best; te=pd.to_datetime(tr["t_entry"],unit="s",utc=True); tyr=te.dt.year.to_numpy(); r=tr["R"].to_numpy()
        py=" ".join(f"{y}:{r[tyr==y].mean():+.2f}(n{int((tyr==y).sum())})" for y in (2021,2022,2023) if (tyr==y).sum()>0)
        cut=int(len(tr)*0.6); ud=len(set(te.dt.floor('D')))
        print(f"   best rr{rr}: per-year[{py}] DISC={r[:cut].mean():+.3f} CONF={r[cut:].mean():+.3f} uniqueDays={ud} trades={len(tr)}")
    # cross-era
    hh=m15d.build(verbose=False); hm=hh["M15"]; hh4=hh["H4"]; b0=hm["is_b0"].to_numpy(); b1=hm["is_b1"].to_numpy()
    regc2,_,uniq2=align_h4(hm,hh4,m15d.align_causal); ou2,od2,mfe2,mae2=passage_m15(hm)
    for blk,mask in (("b0",b0),("b1",b1)):
        print(f"\n== {blk} ==")
        ev2=cand_events(hm,regc2,uniq2,mask)
        outcome_dist(hm,ev2,ou2,od2,mfe2,mae2,f"{blk} outcome")
        struct_geom(hm,ev2,f"{blk} struct")
    # §17 independence vs COMP-CONT-L (opposite direction -> non-redundant; report shared days)
    pkg=os.path.join(sb._HERE,"comp_cont_L_package.json")
    if os.path.exists(pkg) and best is not None:
        cc=json.load(open(pkg)); ccd=set(pd.to_datetime([t["t_entry"] for t in cc["ledger"]],unit="s",utc=True).floor("D"))
        sd=set(pd.to_datetime(best[2]["t_entry"],unit="s",utc=True).dt.floor("D")); inter=len(ccd&sd)
        print(f"\n§17 independence vs COMP-CONT-L (LONG QUIET->UP): shared-days={inter}/{len(sd)} (opposite direction + DOWN H4 vs QUIET->UP -> non-redundant)")

if __name__=="__main__":
    main()

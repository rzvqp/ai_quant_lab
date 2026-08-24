"""state_m15_downparent.py — DECISIVE same-regime cross-era check for ST-M15-HIGHVOL-SHORT-DOWNPARENT.
High-vol M15 short conditioned on H1 DOWN parent regime: DEV (per-year, DISC/CONF, eff-N, session) + b0/b1
same-regime. Stage-C decision. Causal, price-only, STRESS, event-deduped.
"""
import numpy as np, pandas as pd, json, os
import swing_base as sb, hist_m15_data as m15d
from state_regime import regime
from state_m15_discover import feats, dedup
PIP=0.10; H=32; COOL=8

def down_hv_events(m, h1frame, align_fn, mask):
    F=feats(m); vr=F["vr"]; vc=F["vc"]; hv=((vr>1.3)|(vc>1.2))&np.isfinite(vr)
    labs=regime(h1frame); codes,uniq=pd.factorize(labs); h1frame=h1frame.copy(); h1frame["regc"]=codes.astype(float)
    a=align_fn(m,h1frame,["regc"],""); regc=a["regc"].to_numpy()
    down_code=list(uniq).index("DOWN") if "DOWN" in uniq else -999
    cond=mask&np.nan_to_num(hv,nan=0).astype(bool)&(regc==down_code)
    ev=np.where(dedup(cond,COOL))[0]; return ev,F

def econ(m,ev,rr,mult):
    atr=m["atr"].to_numpy(); risk=mult*atr[ev]; ok=np.isfinite(risk)&(risk>0)
    tr=sb.simulate(m,ev[ok],-1,risk[ok],rr=rr,horizon=H,scenario="STRESS")
    return (sb.metrics(tr,m,rr),tr) if len(tr) else (None,None)

def main():
    print("DECISIVE cross-era check: DOWN-parent high-vol M15 SHORT (STRESS, event-deduped).")
    m=sb.build_frames()["M15"]; dev=m["is_dev"].to_numpy(); yr=m["dt"].dt.year.to_numpy()
    h1=sb.build_frames()["H1"]
    ev,F=down_hv_events(m,h1,sb.align_context,dev)
    print(f"  DEV DOWN-parent high-vol-short events (deduped)={len(ev)}")
    for mult in (1.5,2.0):
        for rr in (1.0,1.5,2.0):
            mm,tr=econ(m,ev,rr,mult)
            if mm: print(f"   struct {mult}ATR rr{rr}: avgR={mm['avgR']:+.3f} WR={mm['WR_pos']:.2f} best5={mm['best5']:+.3f} best10={mm['best10']:+.3f} medSL={mm['med_sl_pips']:.0f}p tpm={mm['trades_per_month']:.1f}")
    # per-year + DISC/CONF at struct 1.5ATR rr1.5 (the headline)
    mm,tr=econ(m,ev,1.5,1.5)
    if tr is not None:
        te=pd.to_datetime(tr["t_entry"],unit="s",utc=True); tyr=te.dt.year.to_numpy(); r=tr["R"].to_numpy()
        py=" ".join(f"{y}:{r[tyr==y].mean():+.2f}(n{int((tyr==y).sum())})" for y in (2021,2022,2023) if (tyr==y).sum()>0)
        cut=int(len(tr)*0.6); dl=r[:cut].mean(); cl=r[cut:].mean()
        ud=len(set(te.dt.floor('D'))); hrs=te.dt.hour.to_numpy()
        sess={"Asia":int(((hrs>=0)&(hrs<7)).sum()),"London":int(((hrs>=7)&(hrs<13)).sum()),"NY":int(((hrs>=13)&(hrs<21)).sum())}
        print(f"   headline 1.5ATR rr1.5: per-year[{py}] DISC={dl:+.3f} CONF={cl:+.3f} uniqueDays={ud} session={sess}")
    # cross-era b0/b1
    tfs=m15d.build(verbose=False); hm=tfs["M15"]; hh1=tfs["H1"]; b0=hm["is_b0"].to_numpy(); b1=hm["is_b1"].to_numpy()
    for blk,mask in (("b0",b0),("b1",b1)):
        ev2,_=down_hv_events(hm,hh1,m15d.align_causal,mask)
        print(f"  {blk} DOWN-parent high-vol-short events={len(ev2)}"+(" INSUFFICIENT_SAME_REGIME_EVIDENCE" if len(ev2)<60 else ""))
        if len(ev2)>=60:
            for mult in (1.5,2.0):
                for rr in (1.0,1.5,2.0):
                    mm2,_=econ(hm,ev2,rr,mult)
                    if mm2: print(f"     {blk} struct {mult}ATR rr{rr}: avgR={mm2['avgR']:+.3f} WR={mm2['WR_pos']:.2f} best10={mm2['best10']:+.3f}")
    # overlap vs COMP-CONT-L (different direction/TF -> non-redundant regardless; report trade-day overlap)
    pkg=os.path.join(sb._HERE,"comp_cont_L_package.json")
    if os.path.exists(pkg) and tr is not None:
        cc=json.load(open(pkg)); ccd=set(pd.to_datetime([t["t_entry"] for t in cc["ledger"]],unit="s",utc=True).floor("D"))
        sd=set(pd.to_datetime(tr["t_entry"],unit="s",utc=True).dt.floor("D")); inter=len(ccd&sd)
        print(f"  overlap vs COMP-CONT-L (LONG H4): shared-days={inter}/{len(sd)} (opposite direction -> non-redundant regardless)")

if __name__=="__main__":
    main()

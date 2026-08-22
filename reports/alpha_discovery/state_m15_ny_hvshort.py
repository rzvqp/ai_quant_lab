"""state_m15_ny_hvshort.py — DECISIVE tradeability of ST-M15-NY-HIGHVOL-SHORT (the first directional cross-era-
stable M15 candidate). NY-session (13-21 UTC) M15 high/rising-vol -> SHORT. Does ANY geometry (fixed brackets OR
structural ATR stop, §19 no tight-forcing) yield net-positive STRESS expectancy, cross-era (DEV + b0 + b1),
event-deduped? + per-year/DISC/CONF + best10 robustness + overlap vs frozen. Price-only, causal.
"""
import numpy as np, pandas as pd, json, os
import swing_base as sb, hist_m15_data as m15d
from state_m15_discover import feats, dedup
PIP=0.10; H=32; COOL=8

def ny_hv_events(df,mask):
    F=feats(df); vr=F["vr"]; vc=F["vc"]; hv=((vr>1.3)|(vc>1.2))&np.isfinite(vr)
    ny=(df["dt"].dt.hour.to_numpy()>=13)&(df["dt"].dt.hour.to_numpy()<21)
    cond=mask&ny&np.nan_to_num(hv,nan=0).astype(bool)
    return np.where(dedup(cond,COOL))[0]

def geom(df,ev,tag):
    atr=df["atr"].to_numpy(); print(f"  [{tag}] events={len(ev)}")
    best=None
    for fav,adv in [(50,40),(70,50),(100,70),(150,75)]:
        risk=np.full(len(ev),adv*PIP); tr=sb.simulate(df,ev,-1,risk,rr=fav/adv,horizon=H,scenario="STRESS")
        if len(tr): mm=sb.metrics(tr,df,fav/adv); print(f"     fixed +{fav}/-{adv}: avgR={mm['avgR']:+.3f} WR={mm['WR_pos']:.2f} best10={mm['best10']:+.3f} tpm={mm['trades_per_month']:.1f}")
    for mult in (1.0,1.5,2.0):
        for rr in (1.0,1.5,2.0):
            risk=mult*atr[ev]; ok=np.isfinite(risk)&(risk>0)
            tr=sb.simulate(df,ev[ok],-1,risk[ok],rr=rr,horizon=H,scenario="STRESS")
            if not len(tr): continue
            mm=sb.metrics(tr,df,rr)
            print(f"     struct {mult}ATR rr{rr}: avgR={mm['avgR']:+.3f} WR={mm['WR_pos']:.2f} best10={mm['best10']:+.3f} medSL={mm['med_sl_pips']:.0f}p tpm={mm['trades_per_month']:.1f}")
            if best is None or mm['avgR']>best[1]: best=(f"{mult}ATR rr{rr}",mm['avgR'],mm['best10'],tr,rr)
    return best

def main():
    print("DECISIVE tradeability: NY-session high-vol M15 SHORT (STRESS, event-deduped). Any geometry net-positive cross-era?")
    m=sb.build_frames()["M15"]; dev=m["is_dev"].to_numpy()
    ev=ny_hv_events(m,dev); best=geom(m,ev,"DEV 2021-2023")
    if best is not None:
        _,_,_,tr,rr=best; te=pd.to_datetime(tr["t_entry"],unit="s",utc=True); tyr=te.dt.year.to_numpy(); r=tr["R"].to_numpy()
        py=" ".join(f"{y}:{r[tyr==y].mean():+.2f}(n{int((tyr==y).sum())})" for y in (2021,2022,2023) if (tyr==y).sum()>0)
        cut=int(len(tr)*0.6); print(f"   headline best-avgR geom [{best[0]}]: per-year[{py}] DISC={r[:cut].mean():+.3f} CONF={r[cut:].mean():+.3f} uniqueDays={len(set(te.dt.floor('D')))}")
    hh=m15d.build(verbose=False)["M15"]
    for blk in ("is_b0","is_b1"):
        ev2=ny_hv_events(hh,hh[blk].to_numpy()); geom(hh,ev2,blk[3:])
    # overlap vs COMP-CONT-L (opposite direction -> non-redundant; report shared days)
    pkg=os.path.join(sb._HERE,"comp_cont_L_package.json")
    if os.path.exists(pkg) and best is not None:
        cc=json.load(open(pkg)); ccd=set(pd.to_datetime([t["t_entry"] for t in cc["ledger"]],unit="s",utc=True).floor("D"))
        sd=set(pd.to_datetime(best[3]["t_entry"],unit="s",utc=True).dt.floor("D")); print(f"  overlap vs COMP-CONT-L (LONG H4): shared-days={len(ccd&sd)}/{len(sd)} (opposite direction -> non-redundant)")

if __name__=="__main__":
    main()

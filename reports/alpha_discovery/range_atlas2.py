"""range_atlas2.py — RANGE vNext EVENT ATLAS driver (Phase 1 + Phase 2). Reads __range_cache__/{era}.parquet
(per-bar lifecycle events/state from the ratified vNext) + reconstructs each era sub-frame, verifies alignment,
computes forward first-passage, and reports per lifecycle event, cross-era:
  Phase 1: n, unique days, session distribution, ATR-normalized range width, concurrent-candidate count, bars-since-confirm.
  Phase 2: forward P(+X/-Y) LONG & SHORT at the 5 predeclared labels + asym(L-S) + MFE/MAE.
Implied economic direction annotated per event (BO_up->L accepted-escape-up; SWEEP_up->S failed-escape rotation; etc.).
Info-only, no P&L, no strategy. Material+stable directional event -> Phase 3/5 + S5-independence next.
"""
import os, numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from batch_a import _hr_day
_HERE=os.path.dirname(os.path.abspath(__file__)); CACHE=os.path.join(_HERE,"__range_cache__")
LABELS=[(50,50),(70,50),(100,70),(100,100),(150,75)]; HB=48
SESS=[("As",0,7),("Lo",7,13),("NY",13,21),("Of",21,24)]
# event -> implied direction ('L','S', or None=neutral)
EVENTS=[("BO_up","E_BO_up","L"),("BO_dn","E_BO_dn","S"),
        ("SWEEP_up","E_SWEEP_up","S"),("SWEEP_dn","E_SWEEP_dn","L"),
        ("SWEEP_REV_up","E_SWEEP_REV_up","S"),("SWEEP_REV_dn","E_SWEEP_REV_dn","L"),
        ("OK_MACRO","E_OK_MACRO",None),("BIRTH","E_BIRTH",None),("MERGED","E_MERGED",None),
        ("ABANDON","E_ABANDON",None),("CONTIN","E_CONTIN",None),("TREND_up","E_TREND_up","L"),("TREND_dn","E_TREND_dn","S")]
ERAS=[("b0","hist","is_b0"),("b1","hist","is_b1"),("DEV","sb","is_dev"),("CAL","sb","is_cal")]

def load():
    hm=m15d.build(verbose=False)["M15"]; sm=sb.build_frames()["M15"]; FR={"hist":hm,"sb":sm}
    data={}
    for tag,fk,mk in ERAS:
        fr=FR[fk]; sub=fr[fr[mk].to_numpy()].reset_index(drop=True)
        ev=pd.read_parquet(os.path.join(CACHE,f"{tag}.parquet"))
        assert len(ev)==len(sub) and bool((ev["time"].to_numpy()==sub["time"].to_numpy()).all()), f"{tag} ALIGN FAIL"
        ev["E_TREND_up"]=ev["E_TREND"]&(ev["regime"]=="TREND_UP"); ev["E_TREND_dn"]=ev["E_TREND"]&(ev["regime"]=="TREND_DOWN")
        ou,od,mfe,mae=passage_m15(sub,Hmax=HB)
        data[tag]=dict(sub=sub,ev=ev,ou=ou,od=od,mfe=mfe,mae=mae)
    return data

def main():
    print(f"RANGE vNext EVENT ATLAS (ratified read-only). Hbars={HB} (={HB//4}h). Labels {LABELS}. Info-only, cross-era.")
    D=load()
    for name,col,dirn in EVENTS:
        print(f"\n=== EVENT {name}  (implied dir: {dirn or 'neutral'}) ===")
        for tag,_,_ in ERAS:
            d=D[tag]; sub=d["sub"]; ev=d["ev"]; m=ev[col].to_numpy().astype(bool)
            idx=np.where(m)[0]; idx=idx[idx<len(sub)-1]
            if len(idx)<25: print(f"  [{tag}] n={len(idx)} (thin)"); continue
            hr,day,_=_hr_day(sub); h=hr[idx]; tot=len(idx)
            sess="/".join(f"{nm}{int(((h>=lo)&(h<hi)).sum()/tot*100)}" for nm,lo,hi in SESS)
            atr=sub["atr"].to_numpy(); w=(ev["bup"].to_numpy()-ev["blo"].to_numpy()); wa=w[idx]/atr[idx]; wa=wa[np.isfinite(wa)]
            since=((sub["time"].to_numpy()-ev["confts"].to_numpy())/900.0)[idx]; since=since[np.isfinite(since)]
            nc=ev["ncand"].to_numpy()[idx]
            mm=np.zeros(len(sub),bool); mm[idx]=True
            ls="  ".join(f"+{X}/-{Y}:L{Pm(d['ou'],d['od'],X,Y,'L',HB,mm)[0]:.2f}/S{Pm(d['ou'],d['od'],X,Y,'S',HB,mm)[0]:.2f}" for X,Y in LABELS)
            a70=Pm(d['ou'],d['od'],70,50,'L',HB,mm)[0]-Pm(d['ou'],d['od'],70,50,'S',HB,mm)[0]
            print(f"  [{tag}] n={tot} days={len(set(day[idx]))} sess={sess} wATR={np.median(wa):.1f} ncand~{np.median(nc):.0f} sinceCf={np.median(since) if len(since) else float('nan'):.0f}b | asym70={a70:+.2f}")
            print(f"        {ls} | MFE{np.median(d['mfe'][idx]):.0f}/MAE{np.median(d['mae'][idx]):.0f}p")

if __name__=="__main__":
    main()

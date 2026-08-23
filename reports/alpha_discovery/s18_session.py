"""s18_session.py — S18 Time-of-Day Edge (autonomous selection), Cycle 1 information map. Does the SESSION at the
M15 decision bar, conditioned on the frozen H4 mode, shift XAUUSD future-path odds DIRECTIONALLY (not just
bilaterally)? For each mode x session: P(+70/-50) LONG & SHORT lift vs the mode's all-session base; classify
DIRECTIONAL vs BILATERAL (§9 carried from S4). Sessions UTC: Asia 0-7, London 7-13, NYopen 13-15, NYrest 15-21,
Off 21-24. Reports session vol (atr/atr_ma) to check R11 (Asia low-vol). Cross-era, event-deduped. Frozen mode.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from state_m15_discover import dedup
from market_mode import mode, MODES
from liquidity_event import align_mode
COOL=8; H=32
SESS=[("Asia",0,7),("London",7,13),("NYopen",13,15),("NYrest",15,21),("Off",21,24)]

def run_era(tag, m, h4, af, mask):
    regc,uniq=align_mode(m,h4,af); ou,od,_,_=passage_m15(m); hr=m["dt"].dt.hour.to_numpy() if "dt" in m.columns else pd.to_datetime(m["time"],unit="s",utc=True).dt.hour.to_numpy()
    vr=(m["atr"]/m["atr_ma"]).to_numpy()
    print(f"\n[{tag}]")
    for md in MODES:
        if md not in uniq: continue
        code=uniq.index(md); modem=(regc==code)&mask
        if int(dedup(modem,COOL).sum())<60: continue
        bL=Pm(ou,od,70,50,'L',H,modem&dedup(modem,COOL))[0]; bS=Pm(ou,od,70,50,'S',H,modem&dedup(modem,COOL))[0]
        row=[]
        for nm,lo,hi in SESS:
            sm=modem&(hr>=lo)&(hr<hi); dd=sm&dedup(sm,COOL); nE=int(dd.sum())
            if nE<30: continue
            lL=Pm(ou,od,70,50,'L',H,dd)[0]-bL; lS=Pm(ou,od,70,50,'S',H,dd)[0]-bS
            kind="DIR" if abs(lL-lS)>=0.04 else ("BIL" if (lL>0.03 and lS>0.03) else "-")
            vmed=np.nanmedian(vr[np.where(dd)[0]])
            row.append(f"{nm}:L{lL:+.2f}/S{lS:+.2f}[{kind}]vr{vmed:.2f}(n{nE})")
        print(f"   {md[:12]:12s} baseL/S={bL:.2f}/{bS:.2f}: "+"  ".join(row))

def main():
    print(f"S18 SESSION x MODE future-path map. P(+70/-50) L/S lift vs mode base; DIR vs BIL; session vr. deduped H={H//4}h.")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    run_era("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy())
    run_era("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy())
    run_era("y2123",sm,sh4,sb.align_context,dev)

if __name__=="__main__":
    main()

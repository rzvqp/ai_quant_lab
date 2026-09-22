"""arch_b_run.py — ARCHITECTURE B test: does an M1-triggered entry improve the top M15 survivors over the M1 year (2025-08..2026-08)?
M1 = QUARANTINE/DISCOVERY-ONLY. Compares M15-open entry vs M1-trigger(+M15 stop) vs M1-trigger(+tight M1 stop), all at STRESS cost 0.24."""
import os, sys, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery"); sys.path.insert(0, os.path.join(AA,"code"))
sys.path.insert(0, os.path.join(AA,"reports","alpha_discovery"))
import mstrat; import mstrat_ext as ME; import m1_confirm as MC
mstrat.TICK=0.01
if hasattr(ME,"TICK"): ME.TICK=0.01
d=mstrat.load(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); Lo=d["low"].to_numpy(float); T=d["time"].to_numpy(); n=len(d)
M1=MC.load_m1(); m1_lo=M1["t"][0]; m1_hi=M1["t"][-1]
def signals_from(setups, rr):
    sig=[]
    for s in setups:
        si=s["si"]; ei=s["ei"]; dirn=s["dir"]
        if ei>=n: continue
        if not (m1_lo <= T[si] <= m1_hi): continue   # only M1-covered window
        entry=O[ei]; stop=s["stop"]; risk=abs(entry-stop)
        if risk<=0: continue
        tgt=entry+dirn*rr*risk
        sig.append(dict(t15_close_unix=int(T[si]+900), side=int(dirn), sig_high=float(H[si]), sig_low=float(Lo[si]),
                        target_price=float(tgt), m15_stop=float(stop)))
    return sig
tops=[
 ("S5 ny ORB up rr3", mstrat.s5_setups(d,dict(session="ny",mode="breakout",stop="or_opp",exit="rr3",side="up",family="S5")), 3.0),
 ("S9 c4h=up align structural rr3", mstrat.s9_setups(d,dict(c4h="up",conf1h="align",lb=20,stop="structural",exit="rr3",family="S9")), 3.0),
 ("S20 h4up breakout atr rr3", (ME.s20_setups if hasattr(ME,'s20_setups') else mstrat.s20_setups)(d,dict(ctx="h4up",trig="breakout",lb=50,stop="atr",exit="rr3",family="S20")), 3.0),
]
print(f"M1 window: {pd.to_datetime(m1_lo,unit='s',utc=True).date()} -> {pd.to_datetime(m1_hi,unit='s',utc=True).date()} | STRESS cost 0.24")
for name,su,rr in tops:
    sig=signals_from(su,rr)
    if len(sig)<20: print(f"\n{name}: only {len(sig)} signals in M1 window -> too thin"); continue
    r=MC.run(sig,None,M1,base_rt=0.05,stress_rt=0.24,trig_win=15,horizon_min=480)
    print(f"\n{name}: {len(sig)} M15 signals in M1 window")
    for k in ("M15_OPEN","M1_TRIG_M15stop","M1_TRIG_M1stop"):
        v=r[k]; print(f"   {k:18s} N={v['N']:4d} exp={v['exp']} WR={v['WR']} PF={v['PF']}")

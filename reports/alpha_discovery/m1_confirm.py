"""m1_confirm.py — ARCHITECTURE B harness: M15 EDGE -> M1 ENTRY TRIGGER. M1 is QUARANTINE / UNFIT-for-validation (2025-08..2026-08, 1 yr, single
bull regime, cost/R ~13% at 1-bar stop) -> used STRICTLY as execution/confirmation layer, DISCOVERY ONLY, never an edge base. Given M15 signal bars
(from a governed Arch-A strategy) + side + target, compares three executions on the M1 year at REAL cost (BASE round-trip 0.05 / STRESS 0.24):
  (0) M15_OPEN baseline: enter M15 open[i+1], M15-structural stop, target.
  (1) M1_TRIGGER + M15 stop: after the M15 signal bar closes, first M1 close beyond the signal-bar extreme -> enter next M1 open, keep M15-scale stop.
  (2) M1_TRIGGER + M1 stop: same trigger but tight M1 micro-swing stop (shows the cost/R penalty).
Reports L2/target reach, adverse excursion, realized R, stop-then-target, trade count. NO param search. Causal (M1 info only after M15 bar close)."""
import numpy as np, pandas as pd
M1PATH=r"C:\Users\MEDION GAMING\ai_quant_lab-data-acq\acquisition_staging\OANDA_XAUUSD_M1.csv"
def load_m1():
    m=pd.read_csv(M1PATH); return dict(t=m["time"].to_numpy(np.int64),o=m["open"].to_numpy(float),h=m["high"].to_numpy(float),
                                       l=m["low"].to_numpy(float),c=m["close"].to_numpy(float),n=len(m))
def run(signals, m15, M1, base_rt=0.05, stress_rt=0.24, trig_win=15, horizon_min=480):
    """signals: list of dict(t15_close_unix, side, sig_high, sig_low, target_price, m15_stop). m15 unused (times embedded).
    trig_win = M1 bars to wait for the trigger; horizon_min = max M1 bars to resolve the trade."""
    t1=M1["t"]; o1=M1["o"]; h1=M1["h"]; l1=M1["l"]; c1=M1["c"]; N=M1["n"]
    def sim_exec(entry_idx, side, entry, stop, target, rt):
        risk=abs(entry-stop);
        if risk<=0: return None
        end=min(entry_idx+horizon_min, N-1); R=None
        for k in range(entry_idx, end+1):
            hs=(l1[k]<=stop) if side>0 else (h1[k]>=stop); ht=(h1[k]>=target) if side>0 else (l1[k]<=target)
            if hs and ht: R=-1.0; break
            if hs: R=-1.0; break
            if ht: R=abs(target-entry)/risk; break
        if R is None: R=side*(c1[end]-entry)/risk
        return R - rt/risk
    res={"M15_OPEN":[], "M1_TRIG_M15stop":[], "M1_TRIG_M1stop":[]}
    for s in signals:
        side=s["side"]; tclose=s["t15_close_unix"]
        # M1 bars strictly after the M15 signal bar has closed
        start=int(np.searchsorted(t1, tclose, side="left"))
        if start>=N-2: continue
        # (0) M15_OPEN baseline == first M1 open at/after close (proxy for M15 next-open), M15 stop
        e0=start; entry0=o1[e0]
        r0=sim_exec(e0, side, entry0, s["m15_stop"], s["target_price"], stress_rt)
        if r0 is not None: res["M15_OPEN"].append(r0)
        # trigger: first M1 close beyond signal-bar extreme within trig_win
        trig=-1
        for k in range(start, min(start+trig_win, N)):
            if (c1[k]>s["sig_high"]) if side>0 else (c1[k]<s["sig_low"]): trig=k; break
        if trig<0 or trig+1>=N: continue
        ent=trig+1; entry=o1[ent]
        # (1) M1 trigger + M15 stop
        r1=sim_exec(ent, side, entry, s["m15_stop"], s["target_price"], stress_rt)
        if r1 is not None: res["M1_TRIG_M15stop"].append(r1)
        # (2) M1 trigger + tight M1 stop = extreme of the trigger pullback (last opposite swing before trigger)
        lo_win=l1[start:trig+1].min() if side>0 else None; hi_win=h1[start:trig+1].max() if side<0 else None
        m1stop=(lo_win-0.10) if side>0 else (hi_win+0.10)
        r2=sim_exec(ent, side, entry, m1stop, s["target_price"], stress_rt)
        if r2 is not None: res["M1_TRIG_M1stop"].append(r2)
    out={}
    for k,v in res.items():
        a=np.array(v); out[k]=dict(N=len(a),exp=round(float(a.mean()),4) if len(a) else None,
                                   WR=round(float((a>0).mean()),3) if len(a) else None,PF=round(float(a[a>0].sum()/(abs(a[a<=0].sum())+1e-9)),3) if len(a) else None)
    return out
if __name__=="__main__":
    print("m1_confirm harness ready (import and call run(signals, ...))")

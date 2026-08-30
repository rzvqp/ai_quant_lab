"""htf_m5.py — §22/§28.2 M5 execution comparison (measurement, not a rescue).

No H4/H1 family produced a cross-era-stable baseline survivor (all falsified), so per §12 no thesis qualifies for M5 optimization.
We still answer the CEO's Q2 empirically: for TGT_BREAK signals in the NATIVE-M5 window (2021-07-27+), compare
  BASELINE entry  = M15 anchor close, structural stop, target = 2R (baseline risk)
  M5-REFINED      = wait <=6 M5 bars (30min) for a pullback of >=0.33*risk toward stop; enter there (better price), tighter M5 stop,
                    SAME price target as baseline. If no pullback within window -> MISSED (counts as no-trade).
Report N, missed-trade rate, median entry improvement (pips), MAE, net-R, and classify VALUE_ADD / NEUTRAL / HARMFUL.
No fabricated M5 history; strictly native 2021-07-27+.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import htf_core as HC
from htf_setups import prep, detect, evaluate

def load_m5():
    d=pd.read_csv(r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\data\market\OANDA_XAUUSD_M5.csv")
    d["t"]=d["time"].values.astype("int64")
    return d["t"].values, d["open"].values, d["high"].values, d["low"].values, d["close"].values

def m5_outcome(t5,h5,l5,c5, start_i, entry, side, stop_px, tgt_px, max_m5=64*3):
    """Resolve a trade on M5 from index start_i: which of stop/target first. Return R on risk=|entry-stop|."""
    risk=abs(entry-stop_px)
    if risk<=0: return None
    n=len(t5); end=min(start_i+max_m5, n-1)
    for j in range(start_i, end+1):
        hit_t=(h5[j]>=tgt_px) if side>0 else (l5[j]<=tgt_px)
        hit_s=(l5[j]<=stop_px) if side>0 else (h5[j]>=stop_px)
        if hit_s and hit_t: return -1.0
        if hit_t: return abs(tgt_px-entry)/risk
        if hit_s: return -1.0
    return side*(c5[end]-entry)/risk

def main():
    m,H1,H4=prep()
    t5,o5,h5,l5,c5=load_m5()
    m5start=t5[0]
    tr=detect(m,H1,H4,"TGT_BREAK",htf_on=True)
    rows=evaluate(m,tr)   # gives ent, side, risk_px, and structural target implicitly (2R)
    ct=m["time"].values.astype("int64")+900; cpx=m["close"].values; catr=m["atr"].values  # M15 close time in unix seconds (matches M5)
    base=[]; refi=[]; missed=0; entry_impr=[]; base_mae=[]; refi_mae=[]; used=0
    COST=HC.COST_PRICE
    for r in rows:
        ent=r["ent"]; side=r["side"]; risk=r["risk_px"]
        anchor_t=ct[ent]
        if anchor_t< m5start: continue        # native M5 only
        used+=1
        entry_b=cpx[ent]; stop_b=entry_b-side*risk; tgt=entry_b+side*2*risk
        # baseline resolved on M5 for apples-to-apples
        i5=np.searchsorted(t5, anchor_t, side="left")
        if i5>=len(t5)-1: continue
        rb=m5_outcome(t5,h5,l5,c5,i5,entry_b,side,stop_b,tgt)
        if rb is None: continue
        base.append(rb-COST/risk)
        # M5-refined: seek pullback of >=0.33*risk toward stop within 6 M5 bars
        pull=0.33*risk; got=False
        for j in range(i5, min(i5+6,len(t5))):
            better = (l5[j]<=entry_b-pull) if side>0 else (h5[j]>=entry_b+pull)
            if better:
                entry_r=entry_b-side*pull
                # tighter M5 stop: local extreme of the pullback window +-buffer
                if side>0: stop_r=min(l5[i5:j+1])-0.1
                else:      stop_r=max(h5[i5:j+1])+0.1
                floor=0.5*catr[ent]                       # M5 stop can't be microscopic (avoids R-inflation)
                if abs(entry_r-stop_r)<floor: stop_r=entry_r-side*floor
                risk_r=abs(entry_r-stop_r)
                if risk_r<=0: break
                rr=m5_outcome(t5,h5,l5,c5,j,entry_r,side,stop_r,tgt)
                if rr is None: break
                refi.append(rr-COST/risk_r); entry_impr.append(side*(entry_b-entry_r)/HC.PIP)
                got=True; break
        if not got: missed+=1
    base=np.array(base); refi=np.array(refi)
    print(f"native-M5 TGT_BREAK signals used={used}")
    print(f"BASELINE  N={len(base):4d} netR={base.mean():+.3f} WR={(base>0).mean():.3f}")
    print(f"M5-REFINED N={len(refi):4d} netR={refi.mean():+.3f} WR={(refi>0).mean():.3f} missed={missed} missed_rate={missed/max(used,1):.2f}")
    if len(entry_impr): print(f"median entry improvement = {np.median(entry_impr):+.1f} pips (positive = better price)")
    # classification
    if len(refi)>=30 and len(base)>=30:
        delta=refi.mean()-base.mean()
        cls = "VALUE_ADD" if delta>0.05 else ("HARMFUL" if delta<-0.05 else "NEUTRAL")
        print(f"M5 net-R delta vs baseline = {delta:+.3f} -> {cls} (but underlying thesis FAILED cross-era; execution measure only)")

if __name__=="__main__":
    main()

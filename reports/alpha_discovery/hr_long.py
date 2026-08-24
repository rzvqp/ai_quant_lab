"""hr_long.py — Frontier H tradeable check: is the hr21 forward-return spike a real edge or a drift/ATR artifact? LONG entered
one-per-day at the given UTC hour (minute 0), ATR-bracket (scaling-artifact cancels), STRESS, full gate. Compare hr21 vs
neighbors vs all-hours baseline. No cherry-pick: if only hr21 survives and neighbors don't, it's noise/artifact. No like_at."""
import numpy as np, pandas as pd
import cur_data as CD
import gate
def main():
    m=CD.load_m15(); hr=m["dt"].dt.hour.to_numpy(); mn=m["dt"].dt.minute.to_numpy(); atr=m["atr"].to_numpy(); ok=np.isfinite(atr)&(atr>0)
    print("Frontier H tradeable: LONG one/day at UTC hour, 2ATR stop rr2 H96 STRESS:")
    for HH in [4,5,19,20,21,22,23]:
        idx=np.where(ok&(hr==HH)&(mn==0))[0]
        gate.screen(m, idx, 1, atr, f"hr{HH:02d} LONG", sm=2.0, rr=2.0, dedup=1)
    print("  baseline all-hours LONG (one/day at 12:00):")
    gate.screen(m, np.where(ok&(hr==12)&(mn==0))[0], 1, atr, "hr12 LONG", sm=2.0, rr=2.0, dedup=1)
if __name__=="__main__": main()

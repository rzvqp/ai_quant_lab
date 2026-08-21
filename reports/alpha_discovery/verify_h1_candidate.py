"""Final verification of the LONE deep-survivor H1-B-bo-acc-SHORT (20-breakout+acceptance, SHORT).
Param neighborhood (lb, hold), gate value (uncond vs H4 vs D1), deeper tail, by-year, S5/S20 overlap.
Also re-confirm the mandatory M15-vs-H1 cost-wall picture. DEVELOPMENT (b0+b1) + CALIB reported."""
import sys, os, json
import numpy as np, pandas as pd
from collections import defaultdict
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
import h1_protrend as HP
mstrat = HP.mstrat; TICK = HP.TICK; SLICES = HP.SLICES; RT = HP.RT; SPREAD = HP.SPREAD
from deepen_h1 import eval_rich, stats

def geval(gen, hold, scen, align="h4", blocks=("b0", "b1")):
    return stats(eval_rich(gen, hold, scen, blocks_use=blocks, align=align))

# ── the candidate generator: 20-breakout + acceptance, SHORT (up=False) ──
mk = HP.mk_breakout
gen = mk(False, 20, True, False)   # up=False, lb=20, accept=True, retest=False
HOLD = 10

print("=== BASELINE (H4-aligned SHORT) ===")
for scen in ("GROSS", "BASE", "STRESS"):
    s = geval(gen, HOLD, scen); print(f"  {scen}: avg={s['avg_R']} n={s['n']} win={s['win']} pf={s['pf']} med={s['median']} b5rem={s['best5_rem']} b10rem={s['best10_rem']}")

print("=== GATE VALUE (STRESS) ===")
for al in (None, "h4", "d1"):
    s = geval(gen, HOLD, "STRESS", align=al); print(f"  align={al}: avg={s['avg_R']} n={s['n']}")

print("=== PARAM NEIGHBORHOOD (STRESS, H4) ===")
print("  lb:", {lb: geval(mk(False, lb, True, False), HOLD, "STRESS")["avg_R"] for lb in (15, 20, 25, 30)})
print("  hold:", {h: geval(gen, h, "STRESS")["avg_R"] for h in (6, 8, 10, 12, 15)})
print("  accept on/off (STRESS):", dict(accept=geval(mk(False,20,True,False),HOLD,"STRESS")["avg_R"], raw=geval(mk(False,20,False,False),HOLD,"STRESS")["avg_R"]))

print("=== DEEP TAIL + BY YEAR (STRESS, H4) ===")
s = geval(gen, HOLD, "STRESS")
print(f"  best1_rem={s['best1_rem']} best2_rem={s['best2_rem']} best5_rem={s['best5_rem']} best10_rem={s['best10_rem']}")
print(f"  top1_share={s['top1_share']} max_year_share={s['max_year_share']} med_risk=${s['med_risk']}")
print(f"  by_year={s['by_year']}  pb_avg={s['pb_avg']}")

print("=== CALIBRATION (block2, out-of-DEV) ===")
sc = geval(gen, HOLD, "STRESS", blocks=("calib",)); print(f"  STRESS avg={sc['avg_R']} n={sc['n']} b5rem={sc['best5_rem']} by_year={sc['by_year']}")

# ── S5 / S20 overlap (they are LONG M15; candidate is SHORT H1). Confirm independence by trading-day. ──
print("=== OVERLAP with S5 / S20 (trading-day level) ===")
# candidate short-signal H1 timestamps (DEV blocks), H4-down aligned
cand_days = set()
for bn in ("b0", "b1"):
    sl = SLICES[bn]; h4u = sl["h4_up"].to_numpy(); o = sl["open"].to_numpy(); nb = len(sl)
    ts = sl["time"].to_numpy(); day = pd.to_datetime(ts, unit="s", utc=True).strftime("%Y-%m-%d")
    for (i, side, raw) in gen(sl):
        if 0 < i < nb-1 and h4u[i] <= 0.5: cand_days.add(day[i])
# S5/S20 on M15 (mstrat native), DEV-gated days
try:
    dM = mstrat.load(); dM["dt"] = pd.to_datetime(dM["time"], unit="s", utc=True)
    dev_mask = dM["dt"] < pd.Timestamp("2018-05-01", tz="UTC")
    dM2 = dM[dev_mask].reset_index(drop=True); nM = len(dM2)
    def sday(setups):
        ds = set()
        for x in setups:
            si = x["si"]
            if 0 < si < nM: ds.add(dM2["dt"].iloc[si].strftime("%Y-%m-%d"))
        return ds
    s5 = mstrat.REGISTRY["S5"][1](dM2, dict(session="ny", mode="breakout", side="up", stop="or_opp", exit="rr3"))
    s20 = mstrat.REGISTRY["S20"][1](dM2, dict(ctx="h4up", trig="breakout", lb=50, stop="atr", exit="rr3"))
    s5d = sday(s5); s20d = sday(s20)
    jac = lambda a, b: round(len(a & b) / max(1, len(a | b)), 3)
    print(f"  candidate short-days={len(cand_days)}  S5 long-days={len(s5d)} (jac {jac(cand_days,s5d)})  S20 long-days={len(s20d)} (jac {jac(cand_days,s20d)})")
    print(f"  same-day co-occur: S5={len(cand_days & s5d)} S20={len(cand_days & s20d)} — opposite direction (cand SHORT vs S5/S20 LONG)")
except Exception as e:
    print("  overlap err:", str(e)[:150])

"""S3 EXECUTABILITY — the decisive test (CEO warning: the 0.05 floor / tiny stop may be below gold spread).

mstrat assumes spread_ticks=1.0 (1 cent) — wildly optimistic for XAUUSD (real retail ~15-30 cents).
The S3 stop is tiny (beyond-level, floored to ~0.10*atr), so cost-in-R is large and spread-sensitive.
For the 3 CEO-named configs: report the floored-risk distribution + floor-term binding, and re-run
avg_R / median / fat-tail across REALISTIC spreads. If the edge survives realistic cost, it is real;
if it collapses, S3 is theoretical (as the CEO warned).
"""
from __future__ import annotations
import os, sys, json
import numpy as np, pandas as pd
for _c in [os.environ.get("RATIFIED_CODE_DIR"),
           r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad\ratified_code\code"]:
    if _c and os.path.isdir(_c):
        sys.path.insert(0, _c); break
from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
from edge_research._screen import metrics, screen_verdict

TICK = 0.01
NAMED = [dict(ref='swing', lb=50, retest_within=4, stop='beyond_level', exit='rr3', side='down', hid='4fb5dffe'),
         dict(ref='swing', lb=50, retest_within=8, stop='beyond_level', exit='rr3', side='down', hid='e06421b7'),
         dict(ref='swing', lb=20, retest_within=4, stop='beyond_level', exit='rr3', side='down', hid='47df1185')]


def setups(h, o, hi, lo, cl, atr, refH, refL):
    up = h['side'] == 'up'; dirn = 1 if up else -1; W = int(h['retest_within']); n = len(cl)
    brk = (cl > refH) & np.isfinite(refH) if up else (cl < refL) & np.isfinite(refL)
    out = []
    for t0 in np.flatnonzero(brk):
        lvl = refH[t0] if up else refL[t0]; rt = None
        for t1 in range(t0 + 1, min(t0 + W + 1, n)):
            if (up and lo[t1] <= lvl) or ((not up) and hi[t1] >= lvl):
                rt = t1; break
        if rt is None:
            continue
        ei = rt + 1
        if ei >= n - 1 or not np.isfinite(atr[t0]):
            continue
        out.append((t0, ei, dirn, (lvl - 2 * TICK) if up else (lvl + 2 * TICK)))
    return out


def sim(setups, o, hi, lo, cl, atr, spread_ticks, slip_ticks=1.0):
    n = len(cl); cost = (spread_ticks + slip_ticks) * TICK
    Rs = []; sis = []; risks = []; floor_bind = []; last = -1
    for s in sorted(setups, key=lambda x: x[1]):
        t0, ei, dirn, stop = s
        if ei <= last or ei >= n - 1 or ei < 1:
            continue
        entry = o[ei]; risk = abs(entry - stop)
        if not np.isfinite(risk) or np.isnan(atr[t0]) or atr[t0] <= 0:
            continue
        terms = (2 * spread_ticks * TICK, 5 * TICK, 0.10 * atr[t0])
        min_exec = max(terms)
        if risk < min_exec:
            risk = min_exec; stop = entry - dirn * risk
            floor_bind.append(int(np.argmax(terms)))  # 0=spread,1=0.05,2=0.10atr
        if risk <= 0:
            continue
        tgt = entry + dirn * 3.0 * risk; to = 48
        ex = None; xi = None
        for j in range(ei, min(ei + to, n)):
            if dirn > 0:
                if lo[j] <= stop: ex = stop; xi = j; break
                if hi[j] >= tgt: ex = tgt; xi = j; break
            else:
                if hi[j] >= stop: ex = stop; xi = j; break
                if lo[j] <= tgt: ex = tgt; xi = j; break
        if ex is None:
            xi = min(ei + to, n - 1); ex = cl[xi]
        Rs.append((dirn * (ex - entry) - 2 * cost) / risk); sis.append(t0); risks.append(risk); last = xi
    return Rs, sis, risks, floor_bind


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); hi = d["high"].to_numpy(); lo = d["low"].to_numpy()
    cl = d["close"].to_numpy(); atr = d["atr14"].to_numpy(); H = d["high"]; L = d["low"]
    refs = {lb: (H.rolling(lb).max().shift(1).to_numpy(), L.rolling(lb).min().shift(1).to_numpy()) for lb in (20, 50)}

    out = {}
    for h in NAMED:
        refH, refL = refs[h['lb']]
        st = setups(h, o, hi, lo, cl, atr, refH, refL)
        # baseline floor/risk profile (spread=1)
        _, _, risks0, fb0 = sim(st, o, hi, lo, cl, atr, spread_ticks=1.0)
        risks0 = np.array(risks0)
        fb = np.array(fb0)
        prof = dict(median_risk_price=round(float(np.median(risks0)), 3),
                    median_risk_cents=round(float(np.median(risks0)) * 100, 1),
                    p10_risk=round(float(np.percentile(risks0, 10)), 3),
                    floor_bound_frac=round(len(fb0) / max(len(risks0), 1), 3),
                    floor_bind_005_frac=round(float((fb == 1).mean()) if len(fb) else 0, 3),
                    floor_bind_010atr_frac=round(float((fb == 2).mean()) if len(fb) else 0, 3))
        # spread sensitivity
        sens = {}
        for sp in (1, 10, 20, 30):   # 1c(mstrat), 10c, 20c, 30c spread
            Rs, sis, _, _ = sim(st, o, hi, lo, cl, atr, spread_ticks=float(sp))
            m = metrics([dict(r=r, reason="", signal_idx=si) for r, si in zip(Rs, sis)])
            sens[f"spread_{sp}c"] = dict(n=m["n"], avg_R=m["avg_R"], median=m["median_R"], PF=m["profit_factor"],
                                        trimmed=m.get("trimmed_top1pct", {}).get("avg_R"),
                                        verdict=screen_verdict(m).split(" \u2014")[0])
        out[h['hid']] = dict(config=f"{h['ref']}/{h['lb']}/{h['retest_within']}/{h['exit']}/{h['side']}",
                             risk_profile=prof, spread_sensitivity=sens)
    result = dict(experiment="S3_executability", note="mstrat spread=1c is optimistic; real XAUUSD ~15-30c",
                  configs=out)
    print(json.dumps(result, indent=2, default=float))
    with open(os.path.join(os.path.dirname(__file__), "cand_s3_execution_results.json"), "w") as f:
        json.dump(result, f, indent=2, default=float)


if __name__ == "__main__":
    main()

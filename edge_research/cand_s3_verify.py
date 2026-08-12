"""S3 FAMILY (Breakout-Retest Continuation) — INDEPENDENT verification for the CEO priority.

VE's numbers come from mstrat. This reproduces the S3 mechanism + the corrected engine (TICK=0.01 ->
floor max(0.05, 0.10*atr)) INDEPENDENTLY on holdout-sealed data (_common.load), and adds the FAT-TAIL
check (best-trade share + top-1%-trimmed avg_R) that mstrat did not compute, plus year stability.

Faithful to mstrat @38e7165:
  features: rmax{lb}=high.rolling(lb).max().shift(1); rmin=low.rolling.min.shift(1);
            sess_high/low = high/low groupby(session-run).cummax/min().shift(1)   (lookahead-safe)
  setup S3: break (cl>refH up / cl<refL down) -> retest within W -> entry ei=retest+1
  stop: beyond_level = lvl -/+ 2*TICK ; atr = o[ei] -/+ 1.5*atr[t0]
  exit: rr2/rr3 (tgt=entry+dir*R*risk), trailing (1.5*atr), timeout 48 bars
  engine: entry@next-open, WORST-CASE intrabar (stop before target), no-overlap, floor, cost 0.04 RT,
          R = (dir*(exit-entry) - 2*cost)/risk   (net of cost)
CFG: tick=0.01, spread_ticks=slip_ticks=1.0 -> cost=0.02/side, floor=max(0.02,0.05,0.10*atr).
"""
from __future__ import annotations
import os, sys, json, itertools, hashlib
import numpy as np, pandas as pd
for _c in [os.environ.get("RATIFIED_CODE_DIR"),
           r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad\ratified_code\code"]:
    if _c and os.path.isdir(_c):
        sys.path.insert(0, _c); break
from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
from edge_research._screen import metrics, screen_verdict

TICK = 0.01; SPREAD = 1.0; SLIP = 1.0
COST = (SPREAD + SLIP) * TICK          # 0.02 per side
S3_DIMS = dict(ref=['swing', 'session'], lb=[20, 50], retest_within=[4, 8],
               stop=['beyond_level', 'atr'], exit=['rr2', 'rr3', 'trailing'], side=['up', 'down'])


def hid_of(h):
    key = tuple(sorted({**h, 'family': 'S3'}.items()))
    return hashlib.md5(('S3' + str(key)).encode()).hexdigest()[:12]


def s3_setups(h, o, hi, lo, cl, atr, refs):
    up = (h['side'] == 'up'); dirn = 1 if up else -1; W = int(h['retest_within']); n = len(cl)
    refH, refL = refs[('swing' if h['ref'] == 'swing' else 'session', int(h['lb']))]
    brk = (cl > refH) & np.isfinite(refH) if up else (cl < refL) & np.isfinite(refL)
    rrmap = {'rr2': 3.0 if False else 2.0, 'rr3': 3.0}
    out = []
    for t0 in np.flatnonzero(brk):
        lvl = refH[t0] if up else refL[t0]
        rt = None
        for t1 in range(t0 + 1, min(t0 + W + 1, n)):
            if (up and lo[t1] <= lvl) or ((not up) and hi[t1] >= lvl):
                rt = t1; break
        if rt is None:
            continue
        ei = rt + 1
        if ei >= n - 1 or not np.isfinite(atr[t0]):
            continue
        stop = (lvl - 2 * TICK) if up else (lvl + 2 * TICK)
        if h['stop'] == 'atr':
            stop = o[ei] - dirn * 1.5 * atr[t0]
        out.append((t0, ei, dirn, stop, h['exit']))
    return out


def sim(setups, o, hi, lo, cl, atr):
    n = len(cl); Rs = []; sis = []; last = -1
    for s in sorted(setups, key=lambda x: x[1]):
        t0, ei, dirn, stop, exk = s
        if ei <= last or ei >= n - 1 or ei < 1:
            continue
        entry = o[ei]; risk = abs(entry - stop)
        if not np.isfinite(risk) or np.isnan(atr[t0]) or atr[t0] <= 0:
            continue
        min_exec = max(2 * SPREAD * TICK, 5 * TICK, 0.10 * atr[t0])
        if risk < min_exec:
            risk = min_exec; stop = entry - dirn * risk
        if risk <= 0:
            continue
        trail = (exk == 'trailing'); to = 48
        tgt = entry + dirn * (2.0 if exk == 'rr2' else 3.0) * risk if exk in ('rr2', 'rr3') else None
        best = entry; ex = None; xi = None
        for j in range(ei, min(ei + to, n)):
            if trail:
                best = max(best, hi[j]) if dirn > 0 else min(best, lo[j])
                ts = best - dirn * 1.5 * atr[t0]
                stop = max(stop, ts) if dirn > 0 else min(stop, ts)
            if dirn > 0:
                if lo[j] <= stop: ex = stop; xi = j; break
                if tgt is not None and hi[j] >= tgt: ex = tgt; xi = j; break
            else:
                if hi[j] >= stop: ex = stop; xi = j; break
                if tgt is not None and lo[j] <= tgt: ex = tgt; xi = j; break
        if ex is None:
            xi = min(ei + to, n - 1); ex = cl[xi]
        Rs.append((dirn * (ex - entry) - 2 * COST) / risk); sis.append(t0); last = xi
    return Rs, sis


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); hi = d["high"].to_numpy(); lo = d["low"].to_numpy()
    cl = d["close"].to_numpy(); atr = d["atr14"].to_numpy()
    years = d["dt"].dt.year.to_numpy()
    H = d["high"]; L = d["low"]
    # session-run block for sess refs
    sess = d["session"].to_numpy()
    blk = (pd.Series(sess) != pd.Series(sess).shift(1)).cumsum().to_numpy()
    refs = {}
    for lb in (20, 50):
        refs[('swing', lb)] = (H.rolling(lb).max().shift(1).to_numpy(), L.rolling(lb).min().shift(1).to_numpy())
    sh = H.groupby(blk).cummax().shift(1).to_numpy(); sl = L.groupby(blk).cummin().shift(1).to_numpy()
    for lb in (20, 50):
        refs[('session', lb)] = (sh, sl)

    keys = list(S3_DIMS)
    rows = []
    for combo in itertools.product(*[S3_DIMS[k] for k in keys]):
        h = dict(zip(keys, combo))
        setups = s3_setups(h, o, hi, lo, cl, atr, refs)
        Rs, sis = sim(setups, o, hi, lo, cl, atr)
        if not Rs:
            continue
        res = [dict(r=r, reason="", signal_idx=si) for r, si in zip(Rs, sis)]
        m = metrics(res)
        by = {}
        for r, si in zip(Rs, sis):
            by.setdefault(int(years[si]), []).append(r)
        yp = sum(1 for v in by.values() if sum(v) / len(v) > 0)
        rows.append(dict(hid=hid_of(h), **{k: h[k] for k in keys},
                         n=m["n"], avg_R=m["avg_R"], PF=m["profit_factor"], median=m["median_R"],
                         best_share=m.get("best_share_of_total"),
                         trimmed_avg_R=m.get("trimmed_top1pct", {}).get("avg_R"),
                         years_pos=f"{yp}/{len(by)}", verdict=screen_verdict(m).split(" —")[0].split(" \u2014")[0]))
    rows.sort(key=lambda r: (r["avg_R"] if r["avg_R"] is not None else -9), reverse=True)
    named = {"4fb5dffe", "e06421b7", "47df1185"}
    out = dict(experiment="S3_independent_verification", data=dict(rows=len(d)),
               n_configs=len(rows),
               named_hashes={r["hid"][:8]: r for r in rows if r["hid"][:8] in named},
               top10=rows[:10])
    print(json.dumps(out, indent=2, default=float))
    with open(os.path.join(os.path.dirname(__file__), "cand_s3_verify_results.json"), "w") as f:
        json.dump(dict(all_configs=rows, **out), f, indent=2, default=float)


if __name__ == "__main__":
    main()

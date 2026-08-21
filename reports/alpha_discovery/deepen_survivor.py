"""Deepen the lone pro-trend survivor PT-C-bo50-UP (50-bar high breakout, LONG, N1-TREND_UP gated).
Tail, per-block (DEV vs CALIB), param neighborhood, hold neighborhood, S5 overlap. DEVELOPMENT+CALIBRATION only."""
import sys, os, json, numpy as np, pandas as pd
from collections import defaultdict
WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"; ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
for p in (WP5B, ALPHA, os.path.join(ALPHA, "code")):
    if p not in sys.path: sys.path.insert(0, p)
import mstrat
SP = r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad"; TICK = mstrat.TICK
d = mstrat.load(); d["dt"] = pd.to_datetime(d["time"], unit="s", utc=True)
d = d[d["dt"] < pd.Timestamp("2022-01-01", tz="UTC")].reset_index(drop=True)
n = len(d); ts = d["time"].astype("int64").to_numpy(); years = d["dt"].dt.year.to_numpy()
o = d["open"].to_numpy(); hi = d["high"].to_numpy(); lo = d["low"].to_numpy(); cl = d["close"].to_numpy(); atr = d["m_atr"].to_numpy()
DEV = (d["dt"] < pd.Timestamp("2018-05-01", tz="UTC")).to_numpy(); CAL = (d["dt"] >= pd.Timestamp("2020-01-01", tz="UTC")).to_numpy()
Z = np.load(os.path.join(SP, "n1_ledger.npz"), allow_pickle=True)
pos = np.searchsorted(Z["ts_open"].astype(np.int64), ts); ok = Z["ts_open"].astype(np.int64)[pos] == ts
bit = {x: 1 << i for i, x in enumerate(list(Z["vocab"]))}; reg_up = np.where(ok, (Z["mask"][pos] & bit["TREND_UP"]) != 0, False)
CM = json.load(open(r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"))
RT = {"GROSS": 0.0, "BASE": CM["base_ratified"]["round_trip_total"], "STRESS": CM["stress_ratified"]["round_trip_total"]}; SPREAD = {"GROSS": 0.0, "BASE": 0.05, "STRESS": 0.08}
def rmax(a, w): return pd.Series(a).rolling(w).max().shift(1).to_numpy()
def evals(sig, hold, scen, keep=None):
    cfg = dict(mstrat.CFG); cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = RT[scen] / (2 * TICK); su = []
    for (i, side, raw) in sig:
        if not (0 < i < n - 1) or (keep is not None and not keep[i]): continue
        ref = o[min(i + 1, n - 1)]; fl = max(2 * SPREAD[scen], 0.05, 0.10 * atr[i]) if atr[i] == atr[i] else max(2 * SPREAD[scen], 0.05)
        st = ref - max(abs(ref - raw), fl)
        if st >= ref: continue
        su.append(dict(si=i, ei=i + 1, dir=1, stop=float(st), exit_kind="time", exit_param=float(hold)))
    led = mstrat.simulate(d, su, cfg); return [dict(r=float(r), si=int(s)) for r, s in zip(led["R"], led["si"])]
def M(res):
    if not res: return dict(n=0)
    r = np.array([x["r"] for x in res]); nn = len(r); w = r[r > 0]; tot = float(r.sum())
    return dict(n=nn, avg_R=round(float(r.mean()), 4), win=round(len(w) / nn, 3))
def tailp(res):
    r = np.sort(np.array([x["r"] for x in res]))[::-1]; nn = len(r); tot = r.sum()
    rem = lambda p: round(float(r[max(1, int(nn * p)):].mean()), 4)
    return dict(median=round(float(np.median([x["r"] for x in res])), 3), top1_share=round(float(r[:max(1, int(nn * 0.01))].sum() / tot), 3),
                exp_rem_top1=rem(0.01), exp_rem_top2=rem(0.02), exp_rem_top5=rem(0.05))
def rmin(a, w): return pd.Series(a).rolling(w).min().shift(1).to_numpy()
def bo(lb):
    H = rmax(hi, lb); L = rmin(lo, lb); out = []
    for i in range(lb + 2, n - 1):
        if np.isfinite(H[i]) and cl[i] > H[i]: out.append((i, "long", L[i]))   # raw stop = rolling-min low (as in campaign g_breakout)
    return out
sig = bo(50)
base = evals(sig, 40, "BASE", keep=reg_up)
out = dict(candidate="PT-C-bo50-UP (50-bar high breakout, LONG, N1 TREND_UP gated, hold 40)",
           baseline=dict(BASE=M(base)["avg_R"], STRESS=M(evals(sig, 40, "STRESS", keep=reg_up))["avg_R"], n=M(base)["n"], win=M(base)["win"]),
           per_block=dict(DEV=M(evals(sig, 40, "BASE", keep=reg_up & DEV))["avg_R"], CALIB=M(evals(sig, 40, "BASE", keep=reg_up & CAL))["avg_R"]),
           tail=tailp(base),
           param_lb={lb: M(evals(bo(lb), 40, "BASE", keep=reg_up))["avg_R"] for lb in (40, 50, 60, 70)},
           hold={h: M(evals(sig, h, "BASE", keep=reg_up))["avg_R"] for h in (30, 40, 60)})
s5 = mstrat.REGISTRY["S5"][1](d, dict(session="ny", mode="breakout", side="up", stop="or_opp", exit="rr3"))
s5b = set(x["si"] for x in s5 if 0 < x["si"] < n); pb = set(i for (i, s, r) in sig if 0 < i < n and reg_up[i])
out["s5_overlap"] = dict(jaccard=round(len(s5b & pb) / max(1, len(s5b | pb)), 3), simultaneous=len(s5b & pb),
                         classification="INDEPENDENT" if len(s5b & pb) / max(1, len(s5b | pb)) < 0.1 else "REDUNDANT")
print(json.dumps(out, indent=1, default=float))
json.dump(out, open(os.path.join(SP, "protrend_survivor_deepen.json"), "w"), indent=1, default=float)

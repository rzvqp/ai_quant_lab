"""Campaign extension: (1) reclassify with a STRESS gate (CEO ruling: STRESS 0.24 is authoritative NET);
(2) add remaining DISTINCT mechanisms (failed-counter UP/DOWN, gap, session-regime, multi-scale displacement,
opening-range); (3) robustness on the displacement+acceptance survivor (time stability, best-trade removal,
regime-conditioning value). DEVELOPMENT only. Early-stop justification: info gain from new distinct mechanisms."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import Counter, defaultdict
ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"
os.environ.setdefault("RATIFIED_CODE_DIR", WP5B); os.environ["ALPHA_FROZEN_TS"] = "1787300000"
for p in (ALPHA, os.path.join(ALPHA, "code"), WP5B):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ALPHA)
from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
from edge_research._screen import _canonical, trades_to_setups, Trade
import mstrat
SP = os.path.dirname(os.path.abspath(__file__)); TICK = mstrat.TICK
def log(m): print(f"[{int(time.time())}] {m}", flush=True); open(os.path.join(SP, "campaign2.log"), "a").write(f"{int(time.time())} {m}\n")
d0, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
dev = d0[d0["dt"] < pd.Timestamp("2018-05-01", tz="UTC")].reset_index(drop=True)
n = len(dev); o = dev["open"].to_numpy(); hi = dev["high"].to_numpy(); lo = dev["low"].to_numpy()
cl = dev["close"].to_numpy(); atr = dev["atr14"].to_numpy(); ts = dev["time"].astype("int64").to_numpy()
years = dev["dt"].dt.year.to_numpy(); utc_hour = ((ts // 3600) % 24)
Z = np.load(os.path.join(SP, "n1_ledger.npz"), allow_pickle=True)
pos = np.searchsorted(Z["ts_open"].astype(np.int64), ts); bit = {x: 1 << i for i, x in enumerate(list(Z["vocab"]))}
mask = Z["mask"][pos]; is_disp = Z["is_disp"][pos].astype(bool)
reg_up = (mask & bit["TREND_UP"]) != 0; reg_down = (mask & bit["TREND_DOWN"]) != 0
reg_trend = reg_up | reg_down
CM = json.load(open(r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"))
SCEN = {"GROSS": (0.0, 0.0), "BASE": (0.05, CM["base_ratified"]["round_trip_total"]), "STRESS": (0.08, CM["stress_ratified"]["round_trip_total"])}
def widened(i, side, raw, spread):
    ref = o[min(i + 1, n - 1)]; fl = max(2 * spread, 0.05, 0.10 * atr[i]) if atr[i] == atr[i] else max(2 * spread, 0.05)
    return ref - (1 if side == "long" else -1) * max(abs(ref - raw), fl)
def evaluate(sig, hold, scen, mask_keep=None):
    spread, rt = SCEN[scen]; sim, CFG = _canonical(); cfg = dict(CFG); cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = rt / (2 * TICK)
    tr = []
    for (i, side, raw) in sig:
        if not (0 < i < n - 1): continue
        if mask_keep is not None and not mask_keep[i]: continue
        st = widened(i, side, raw, spread); ref = o[min(i + 1, n - 1)]
        if (side == "long" and st >= ref) or (side == "short" and st <= ref): continue
        tr.append(Trade(i, side, float(st), hold, exit_kind="time", exit_param=float(hold)))
    dd = dev.copy(); dd["m_atr"] = dd["atr14"]; led = sim(dd, trades_to_setups(tr), cfg)
    return [dict(r=float(r), si=int(s)) for r, s in zip(led["R"], led["si"])]
def metrics(res):
    if not res: return dict(n=0)
    rs = np.array([x["r"] for x in res]); nn = len(rs); w = rs[rs > 0]; l = rs[rs <= 0]; srt = np.sort(rs)[::-1]
    tot = float(rs.sum()); yr = defaultdict(float)
    for x in res: yr[int(years[x["si"]])] += x["r"]
    return dict(n=nn, avg_R=round(float(rs.mean()), 4), total_R=round(tot, 2), win_rate=round(len(w) / nn, 3),
                profit_factor=round(float(w.sum() / -l.sum()), 3) if l.sum() < 0 else None,
                best_share=round(float(srt[0] / tot), 3) if tot > 0 else None,
                temporal_concentration=round(max(abs(v) for v in yr.values()) / abs(tot), 3) if tot else None)
def status_of(mg, mb, ms, mins):
    nn = mg.get("n", 0)
    if nn < 30: return "EVENT_SPARSE"
    if nn < mins: return "INSUFFICIENT_EVIDENCE"
    g, b, s = mg.get("avg_R"), mb.get("avg_R"), ms.get("avg_R")
    if g is None or g <= 0: return "FAST_FALSIFICATION_FAIL"
    if b is None or b <= 0: return "FAST_FALSIFICATION_FAIL"
    tc, bs = mb.get("temporal_concentration"), mb.get("best_share")
    if (tc and tc > 0.6) or (bs and bs > 0.35): return "FAST_FALSIFICATION_FAIL"
    if s is None or s <= 0: return "COST_FRAGILE_STRESS_NEGATIVE"     # BASE-positive but cost-eaten at STRESS
    return "FAST_FALSIFICATION_PASS"

# ── (1) reclassify prior campaign records with the STRESS gate ──────────────────────────────────────
prior = json.load(open(os.path.join(SP, "campaign_records.json")))["records"]
recl = []
for r in prior:
    if r["id"] == "C-R-boundary-mid": r["status"] = "RERUN_ERROR_EXCLUDED"; r["reason"] = "opp_liq exit path bug; boundary-fade already tested as H08 (fail)"; recl.append(r); continue
    st = status_of(r["GROSS"], r["BASE"], r["STRESS"], r["min_sample"]); r["status_stress_gated"] = st; recl.append(r)
log("reclassified prior campaign under STRESS gate")

# ── (2) new distinct mechanisms ─────────────────────────────────────────────────────────────────────
def rmin(a, w): return pd.Series(a).rolling(w).min().shift(1).to_numpy()
def rmax(a, w): return pd.Series(a).rolling(w).max().shift(1).to_numpy()
def g_failed_counter(regime):  # trend + failed opposing break + reclaim within 3 bars
    up = regime == "UP"; reg = reg_up if up else reg_down
    lv = rmin(lo, 10) if up else rmax(hi, 10); out = []
    for i in range(12, n - 4):
        if not reg[i]: continue
        if up and cl[i] < lv[i] and cl[i-1] >= lv[i-1]:
            for j in range(i+1, i+4):
                if cl[j] > hi[i]: out.append((j, "long", lo[i] - 0.1*atr[j])); break
        elif (not up) and cl[i] > lv[i] and cl[i-1] <= lv[i-1]:
            for j in range(i+1, i+4):
                if cl[j] < lo[i]: out.append((j, "short", hi[i] + 0.1*atr[j])); break
    return out
def g_gap():  # session-open gap continuation (first NY bar gap vs prior close)
    out = []
    for i in range(2, n - 1):
        if utc_hour[i] == 13 and utc_hour[i-1] != 13:
            gap = o[i] - cl[i-1]
            if abs(gap) > 0.5 * atr[i]:
                side = "long" if gap > 0 else "short"; out.append((i, side, cl[i] - (1 if side=="long" else -1)*1.0*atr[i]))
    return out
def g_multiscale_disp():  # displacement confirmed on the bar AND the prior 4-bar aggregate (multi-scale)
    out = []; agg = cl - pd.Series(cl).shift(4).to_numpy()
    for j in range(5, n - 3):
        if not is_disp[j]: continue
        dirn = 1 if cl[j] > o[j] else -1
        if not np.isfinite(agg[j]) or (agg[j] > 0) != (dirn > 0) or abs(agg[j]) < 1.0*atr[j]: continue
        if cl[j+1] > cl[j] if dirn > 0 else cl[j+1] < cl[j]:
            out.append((j+1, "long" if dirn>0 else "short", o[j] - dirn*0.1*atr[j]))
    return out
def g_session_trend():  # NY-open momentum CONDITIONED on N1 trend agreement (regime-conditioned session)
    out = []
    for i in range(26, n - 34):
        if utc_hour[i] == 13 and utc_hour[i-1] != 13:
            mv = cl[i] - cl[i-24]
            if abs(mv) < 0.2*atr[i]: continue
            side = "long" if mv > 0 else "short"
            if (side == "long" and reg_up[i]) or (side == "short" and reg_down[i]):  # only when trend agrees
                out.append((i, side, cl[i] - (1 if side=="long" else -1)*1.0*atr[i]))
    return out
def g_opening_range():  # first-hour range breakout of the NY session
    out = []
    for i in range(30, n - 1):
        if utc_hour[i] == 13 and utc_hour[i-1] != 13:
            orh = max(hi[i:i+4]); orl = min(lo[i:i+4])
            for j in range(i+4, min(i+20, n-1)):
                if cl[j] > orh: out.append((j, "long", orl - 0.1*atr[j])); break
                if cl[j] < orl: out.append((j, "short", orh + 0.1*atr[j])); break
    return out

NEW = [("C-TU-failedcounter","failed-counter","TREND_UP_DEPENDENT","failed bearish break + reclaim LONG",lambda:g_failed_counter("UP"),30,150),
       ("C-TD-failedcounter","failed-counter","TREND_DOWN_DEPENDENT","failed bullish break + reclaim SHORT",lambda:g_failed_counter("DOWN"),30,150),
       ("C-RI-gap","gap","REGIME_INDEPENDENT","NY-open gap continuation",lambda:g_gap(),32,150),
       ("C-TR-multiscale","multiscale-displacement","TRANSITION_DEPENDENT","multi-scale displacement + accept",lambda:g_multiscale_disp(),48,150),
       ("C-RI-session-trend","session-regime","MULTI_REGIME","NY momentum only when N1 trend agrees",lambda:g_session_trend(),32,150),
       ("C-RI-openrange","opening-range","REGIME_INDEPENDENT","NY opening-range breakout",lambda:g_opening_range(),40,150)]
new_recs = []
for (hid, fam, rr, mech, fn, hold, mins) in NEW:
    try:
        sig = [(s[0], s[1], s[2]) for s in fn()]
        mg, mb, ms = metrics(evaluate(sig, hold, "GROSS")), metrics(evaluate(sig, hold, "BASE")), metrics(evaluate(sig, hold, "STRESS"))
        st = status_of(mg, mb, ms, mins)
    except Exception as e:
        st, mg, mb, ms, sig = "RERUN_ERROR", {}, {}, {}, []
        log(f"{hid} ERROR {str(e)[:120]}")
    rec = dict(id=hid, family=fam, regime_relationship=rr, mechanism=mech, n_signals=len(sig), GROSS=mg, BASE=mb, STRESS=ms, status_stress_gated=st, min_sample=mins, data="DEVELOPMENT 2011-2018")
    new_recs.append(rec); log(f"{hid} [{fam}]: n={len(sig)} G={mg.get('avg_R')} B={mb.get('avg_R')} S={ms.get('avg_R')} -> {st}")

# ── (3) robustness on the displacement+acceptance survivor (best version w=0.8,a=2) ─────────────────
def g_da(w, nacc):
    out = []
    for j in range(2, n - nacc - 1):
        if not is_disp[j]: continue
        dirn = 1 if cl[j] > o[j] else -1
        if abs(cl[j] - o[j]) < w * atr[j]: continue
        if all((cl[j+1+k] > cl[j]) == (dirn > 0) for k in range(nacc)):
            i = j + nacc; out.append((i, "long" if dirn>0 else "short", o[j] - dirn*0.1*atr[j]))
    return out
da = [(s[0], s[1], s[2]) for s in g_da(0.8, 2)]
block1 = dev["dt"] < pd.Timestamp("2014-01-01", tz="UTC"); block2 = dev["dt"] >= pd.Timestamp("2015-01-01", tz="UTC")
rb = evaluate(da, 48, "BASE"); rs = evaluate(da, 48, "STRESS")
rob = dict(candidate="displacement+acceptance (rep C-TR-da-w08-a2)", hold=48,
           full_BASE=metrics(rb), full_STRESS=metrics(rs),
           block1_2011_2013_BASE=metrics([x for x in rb if block1.to_numpy()[x["si"]]]),
           block2_2016_2018_BASE=metrics([x for x in rb if block2.to_numpy()[x["si"]]]),
           param_neighborhood={f"w{w}_a{a}": metrics(evaluate([(s[0],s[1],s[2]) for s in g_da(w,a)],48,"BASE"))["avg_R"]
                               for (w,a) in [(0.6,2),(0.8,2),(1.0,2),(1.2,2),(1.0,3),(0.8,3)]},
           best_trade_removed_BASE=None, regime_conditioning=None)
# best-trade removal (drop top 1%)
rvals = sorted([x["r"] for x in rb], reverse=True); kbest = max(1, int(len(rvals)*0.01))
kept = sorted(rb, key=lambda x: x["r"], reverse=True)[kbest:]
rob["best_trade_removed_BASE"] = metrics(kept)["avg_R"]
# regime-conditioning value: unconditional vs TREND-only vs non-trend
rob["regime_conditioning"] = dict(unconditional_BASE=metrics(rb)["avg_R"],
    trend_only_BASE=metrics(evaluate(da,48,"BASE",mask_keep=reg_trend))["avg_R"],
    nontrend_only_BASE=metrics(evaluate(da,48,"BASE",mask_keep=~reg_trend))["avg_R"])
log(f"ROBUSTNESS disp-accept: full BASE {rob['full_BASE']['avg_R']} STRESS {rob['full_STRESS']['avg_R']} | b1 {rob['block1_2011_2013_BASE'].get('avg_R')} b2 {rob['block2_2016_2018_BASE'].get('avg_R')} | best-removed {rob['best_trade_removed_BASE']}")
log(f"  param neighborhood: {rob['param_neighborhood']}")
log(f"  regime-conditioning: {rob['regime_conditioning']}")

json.dump(dict(reclassified=recl, new=new_recs, robustness=rob), open(os.path.join(SP, "campaign2_records.json"), "w"), indent=1, default=float)
log("CAMPAIGN2_COMPLETE")

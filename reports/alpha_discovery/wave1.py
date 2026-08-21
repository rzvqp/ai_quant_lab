"""ALPHA WAVE 1 — fast falsification of H14/H05/H11/H02/H08 on DEVELOPMENT only (blocks 1-2, <2018-05).
Pre-registered defs from ALPHA_DISCOVERY_STAGE1_PLAN.md; not redefined after seeing outcomes.
Cost: RATIFIED AI_TRADER_SHADOW_COST_MODEL_v1 (BASE round-trip 0.05, STRESS 0.24 per CEO ruling). Floor per
mandate: max(2*spread, 0.05, 0.10*ATR) applied via scenario stop pre-widening; round-trip via slip_ticks.
SEALED/VALIDATION untouched. Fast falsification only — no post-hoc filters."""
import sys, os, json, time, math
import numpy as np, pandas as pd
ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"
os.environ.setdefault("RATIFIED_CODE_DIR", WP5B); os.environ["ALPHA_FROZEN_TS"] = "1787300000"
for p in (ALPHA, os.path.join(ALPHA, "code"), WP5B):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ALPHA)
from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
from edge_research._screen import _canonical, trades_to_setups, Trade
import mstrat
SP = os.path.dirname(os.path.abspath(__file__)); TICK = mstrat.TICK
def log(m): print(f"[{int(time.time())}] {m}", flush=True); open(os.path.join(SP, "wave1.log"), "a").write(f"{int(time.time())} {m}\n")

# ── data: DEVELOPMENT only ────────────────────────────────────────────────────────────────────────
d0, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
dev = d0[d0["dt"] < pd.Timestamp("2018-05-01", tz="UTC")].reset_index(drop=True)
n = len(dev); o = dev["open"].to_numpy(); hi = dev["high"].to_numpy(); lo = dev["low"].to_numpy()
cl = dev["close"].to_numpy(); atr = dev["atr14"].to_numpy(); ts = dev["time"].astype("int64").to_numpy()
years = dev["dt"].dt.year.to_numpy(); utc_hour = ((ts // 3600) % 24)
log(f"DEVELOPMENT bars={n} span={dev['dt'].iloc[0]}..{dev['dt'].iloc[-1]}")

# ── N1 regime aligned to dev ──────────────────────────────────────────────────────────────────────
Z = np.load(os.path.join(SP, "n1_ledger.npz"), allow_pickle=True)
led_ts = Z["ts_open"].astype(np.int64); pos = np.searchsorted(led_ts, ts)
assert (led_ts[pos] == ts).all(), "n1 ledger misaligned"
VOCAB = list(Z["vocab"]); bit = {name: 1 << i for i, name in enumerate(VOCAB)}
mask = Z["mask"][pos]; is_disp = Z["is_disp"][pos].astype(bool)
reg_up = (mask & bit["TREND_UP"]) != 0; reg_down = (mask & bit["TREND_DOWN"]) != 0

def rollmin(a, w):
    s = pd.Series(a); return s.rolling(w).min().shift(1).to_numpy()
def rollmax(a, w):
    s = pd.Series(a); return s.rolling(w).max().shift(1).to_numpy()

# ── cost / evaluation with scenario floor (mandate) + exact round-trip (ratified) ──────────────────
CM = json.load(open(r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"))
assert CM["calibration_status"] == "RATIFIED"
BASE_RT, STRESS_RT = CM["base_ratified"]["round_trip_total"], CM["stress_ratified"]["round_trip_total"]
SCEN = {"GROSS": (0.0, 0.0), "BASE": (0.05, BASE_RT), "STRESS": (0.08, STRESS_RT)}  # (spread, round_trip)

def widened_stop(i, side, raw_stop, spread):
    ref = o[min(i + 1, n - 1)]
    floor = max(2 * spread, 0.05, 0.10 * atr[i]) if atr[i] == atr[i] else max(2 * spread, 0.05)
    risk = abs(ref - raw_stop)
    risk = max(risk, floor)
    return ref - (1 if side == "long" else -1) * risk

def evaluate(signals, hold, ek, ep, scenario):
    spread, rt = SCEN[scenario]
    sim, CFG = _canonical(); cfg = dict(CFG); cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = rt / (2 * TICK)
    trades = []
    for (i, side, raw_stop) in signals:
        if not (0 < i < n - 1): continue
        st = widened_stop(i, side, raw_stop, spread)
        ref = o[min(i + 1, n - 1)]
        if (side == "long" and st >= ref) or (side == "short" and st <= ref): continue
        trades.append(Trade(i, side, float(st), hold, exit_kind=ek, exit_param=ep))
    dd = dev.copy(); dd["m_atr"] = dd["atr14"]
    led = sim(dd, trades_to_setups(trades), cfg)
    return [dict(r=float(r), si=int(si), ei=int(ei)) for r, si, ei in zip(led["R"], led["si"], led["ei"])], len(trades)

def metrics(res):
    if not res: return dict(n=0)
    rs = np.array([x["r"] for x in res]); n_ = len(rs); wins = rs[rs > 0]; losses = rs[rs <= 0]
    srt = np.sort(rs)[::-1]; tail = rs[rs <= np.percentile(rs, 5)]
    cum = np.cumsum(rs); peak = np.maximum.accumulate(cum); dd = float((cum - peak).min())
    hold = np.array([x["ei"] for x in res])  # ei is entry index; holding measured below via si..exit not returned; approx by turnover
    yr = {}
    for x in res: yr.setdefault(int(years[x["si"]]), 0.0); yr[int(years[x["si"]])] += x["r"]
    tot = float(rs.sum()); temporal = round(max(abs(v) for v in yr.values()) / abs(tot), 3) if tot else None
    return dict(n=n_, total_R=round(tot, 2), avg_R=round(float(rs.mean()), 4),
                win_rate=round(len(wins) / n_, 4), avg_win=round(float(wins.mean()), 3) if len(wins) else 0.0,
                avg_loss=round(float(losses.mean()), 3) if len(losses) else 0.0,
                profit_factor=round(float(wins.sum() / -losses.sum()), 3) if losses.sum() < 0 else None,
                tail_loss=round(float(tail.mean()), 3) if len(tail) else None, max_dd_R=round(dd, 2),
                best_share=round(float(srt[0] / tot), 3) if tot > 0 else None,
                temporal_concentration=temporal)

def falsify(H, m_gross, m_base, m_stress, n_sig, min_sample):
    n_ = m_gross.get("n", 0)
    if n_ < 30: return "EVENT_SPARSE", f"n={n_}<30"
    if n_ < min_sample: return "INSUFFICIENT_EVIDENCE", f"n={n_}<min_sample={min_sample}"
    g = m_gross.get("avg_R"); b = m_base.get("avg_R")
    if g is None or g <= 0: return "FAST_FALSIFICATION_FAIL", f"gross expectancy<=0 ({g}) — mechanism absent"
    if b is None or b <= 0: return "FAST_FALSIFICATION_FAIL", f"BASE net expectancy<=0 ({b}) — cost failure"
    tc = m_base.get("temporal_concentration"); bs = m_base.get("best_share")
    if tc is not None and tc > 0.6: return "FAST_FALSIFICATION_FAIL", f"temporal concentration {tc}>0.6 — one period dominates"
    if bs is not None and bs > 0.35: return "FAST_FALSIFICATION_FAIL", f"single-trade dependence {bs}>0.35"
    return "FAST_FALSIFICATION_PASS", f"gross {g}>0, BASE net {b}>0, stable — worth deeper research"

# ── signal generators (pre-registered) ─────────────────────────────────────────────────────────────
def H02():  # TREND_UP failed-bearish-counter: minor-low break then reclaim within k=3 bars -> long
    lv = rollmin(lo, 10); sig = []
    for i in range(12, n - 4):
        if not reg_up[i]: continue
        if cl[i] < lv[i] and cl[i - 1] >= lv[i - 1]:      # fresh break below minor low
            bh = hi[i]
            for j in range(i + 1, i + 4):                  # reclaim within k=3
                if cl[j] > bh:
                    sig.append((j, "long", lo[i] - 0.1 * atr[j])); break
    return sig, 30, "time", 30.0, 150

def H05():  # TREND_DOWN breakdown-acceptance: 2 closes below a prior support, no reclaim -> short
    lv = rollmin(lo, 20); sig = []
    for i in range(22, n - 2):
        if not reg_down[i]: continue
        if cl[i] < lv[i] and cl[i - 1] < lv[i - 1] and cl[i - 2] >= lv[i - 2]:  # fresh 2-close acceptance
            sig.append((i, "short", rollmax(hi, 20)[i] + 0.1 * atr[i]))
    return sig, 40, "time", 40.0, 150

def H11():  # TRANSITION displacement+acceptance: N1 displacement bar + 2 confirming closes -> continuation
    sig = []
    for j in range(2, n - 3):
        if not is_disp[j]: continue
        dirn = 1 if cl[j] > o[j] else -1
        if dirn > 0 and cl[j + 1] > cl[j] and cl[j + 2] > cl[j]:
            sig.append((j + 2, "long", o[j] - 0.1 * atr[j]))
        elif dirn < 0 and cl[j + 1] < cl[j] and cl[j + 2] < cl[j]:
            sig.append((j + 2, "short", o[j] + 0.1 * atr[j]))
    return sig, 48, "time", 48.0, 120

def H14():  # REGIME_INDEPENDENT session: NY-open (13:00 UTC) momentum in direction of last 24-bar return
    sig = []
    for i in range(26, n - 34):
        if utc_hour[i] == 13 and utc_hour[i - 1] != 13:     # first bar of NY session
            mv = cl[i] - cl[i - 24]                          # London-session net move
            if abs(mv) < 0.20 * atr[i]: continue             # need a real prior move
            side = "long" if mv > 0 else "short"
            sig.append((i, side, cl[i] - (1 if side == "long" else -1) * 1.0 * atr[i]))
    return sig, 32, "time", 32.0, 300

def H08():  # RANGE boundary-rejection from V4.4 CONFIRMED spans -> fade toward mid
    f = os.path.join(SP, "v44_dev.json")
    if not os.path.exists(f): return None
    v = json.load(open(f)); byidx = {c["idx"]: c for c in v["confirmed"]}
    sig = []
    for c in v["confirmed"]:
        i = c["idx"]; up = c.get("upper"); low = c.get("lower")
        if up is None or low is None or not (0 < i < n - 1) or atr[i] != atr[i]: continue
        tol = 0.25 * atr[i]
        if hi[i] >= up - tol and cl[i] < up:                 # tagged upper & rejected -> short toward mid
            sig.append((i, "short", up + 0.5 * tol))
        elif lo[i] <= low + tol and cl[i] > low:             # tagged lower & rejected -> long
            sig.append((i, "long", low - 0.5 * tol))
    return sig, 96, "time", 96.0, 100, v

# ── run Wave 1 ──────────────────────────────────────────────────────────────────────────────────────
HYPOS = [("H14", "session", "REGIME_INDEPENDENT", H14), ("H05", "breakdown-acceptance", "TREND_DOWN_DEPENDENT", H05),
         ("H11", "displacement+acceptance", "TRANSITION_DEPENDENT", H11), ("H02", "failed-bearish-counter", "TREND_UP_DEPENDENT", H02),
         ("H08", "boundary-rejection", "RANGE_DEPENDENT", H08)]
records = []
for (hid, fam, regrel, gen) in HYPOS:
    g = gen()
    if g is None:
        records.append(dict(hypothesis=hid, family=fam, regime_relationship=regrel, status="PENDING_V44_DEV")); log(f"{hid}: v44_dev not ready"); continue
    extra = None
    if len(g) == 6: sig, hold, ek, ep, mins, extra = g
    else: sig, hold, ek, ep, mins = g
    rg, ns = evaluate(sig, hold, ek, ep, "GROSS"); rb, _ = evaluate(sig, hold, ek, ep, "BASE"); rst, _ = evaluate(sig, hold, ek, ep, "STRESS")
    mg, mb, ms = metrics(rg), metrics(rb), metrics(rst)
    st, reason = falsify(hid, mg, mb, ms, len(sig), mins)
    # regime concentration
    reg_conc = None
    if rg:
        from collections import Counter
        rc = Counter("UP" if reg_up[x["si"]] else ("DOWN" if reg_down[x["si"]] else "OTHER") for x in rg)
        reg_conc = {k: round(v / len(rg), 2) for k, v in rc.items()}
    rec = dict(hypothesis=hid, family=fam, regime_relationship=regrel, n_signals=len(sig), n_trades=ns,
               GROSS=mg, BASE=mb, STRESS=ms, status=st, reason=reason, min_sample=mins,
               regime_concentration=reg_conc, hold=hold, data="DEVELOPMENT (2011-2018, blocks 1-2)")
    if extra: rec["v44_confirmed_frac"] = extra.get("confirmed_frac"); rec["v44_state_counts"] = extra.get("state_counts")
    records.append(rec)
    log(f"{hid} {fam}: n={len(sig)} GROSS_exp={mg.get('avg_R')} BASE_exp={mb.get('avg_R')} STRESS_exp={ms.get('avg_R')} -> {st}")

json.dump(records, open(os.path.join(SP, "wave1_records.json"), "w"), indent=1, default=float)
log(f"WAVE1_COMPLETE records={len(records)}")

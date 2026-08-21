"""ALPHA PORTFOLIO DEEP RESEARCH — S5 (C_2d587447) + ALPHA_CANDIDATE-001 (displacement+acceptance).
DEVELOPMENT (<2018-05) + bounded CALIBRATION (2020-01..2022-01) only. NO VALIDATION (>=2022-12) / NO SEALED.
Cost RATIFIED BASE round-trip 0.05 / STRESS 0.24. No unrestricted optimization (pre-registered neighborhoods).
Two independent lines; baselines frozen; not merged."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict
WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"; ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
for p in (WP5B, ALPHA, os.path.join(ALPHA, "code")):
    if p not in sys.path: sys.path.insert(0, p)
import mstrat
SP = os.path.dirname(os.path.abspath(__file__)); TICK = mstrat.TICK
def log(m): print(f"[{int(time.time())}] {m}", flush=True); open(os.path.join(SP, "deep.log"), "a").write(f"{int(time.time())} {m}\n")

log("mstrat.load ...")
d = mstrat.load(); d["dt"] = pd.to_datetime(d["time"], unit="s", utc=True)
CUT_DEV = pd.Timestamp("2018-05-01", tz="UTC"); CAL_A = pd.Timestamp("2020-01-01", tz="UTC"); CAL_B = pd.Timestamp("2022-01-01", tz="UTC")
VAL = pd.Timestamp("2022-12-01", tz="UTC")   # never touched
d = d[d["dt"] < CAL_B].reset_index(drop=True)  # cap at CALIBRATION end -> VALIDATION never loaded into evaluation
assert d["dt"].max() < VAL, "VALIDATION leak"
n = len(d); dt = d["dt"]; ts = d["time"].astype("int64").to_numpy(); years = dt.dt.year.to_numpy()
o = d["open"].to_numpy(); cl = d["close"].to_numpy(); atrv = d["m_atr"].to_numpy()
DEV = (dt < CUT_DEV).to_numpy(); CAL = ((dt >= CAL_A) & (dt < CAL_B)).to_numpy()
log(f"loaded {n} bars ({dt.iloc[0]}..{dt.iloc[-1]}); DEV={int(DEV.sum())} CALIB={int(CAL.sum())}; VALIDATION never loaded")

# N1 regime aligned
Z = np.load(os.path.join(SP, "n1_ledger.npz"), allow_pickle=True)
pos = np.searchsorted(Z["ts_open"].astype(np.int64), ts); ok = Z["ts_open"].astype(np.int64)[pos] == ts
bit = {x: 1 << i for i, x in enumerate(list(Z["vocab"]))}
mask = np.where(ok, Z["mask"][pos], 0); is_disp = np.where(ok, Z["is_disp"][pos], False).astype(bool)
reg_up = (mask & bit["TREND_UP"]) != 0; reg_down = (mask & bit["TREND_DOWN"]) != 0; reg_trend = reg_up | reg_down
v44 = json.load(open(os.path.join(SP, "v44_dev.json"))); v44ts = set(int(c["ts"]) for c in v44["confirmed"])
range_conf = np.array([int(t) in v44ts for t in ts], bool)   # V4.4 CONFIRMED available on DEV only

CM = json.load(open(r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"))
RT = {"GROSS": 0.0, "BASE": CM["base_ratified"]["round_trip_total"], "STRESS": CM["stress_ratified"]["round_trip_total"]}
def widened(i, side, raw, spread):
    ref = o[min(i + 1, n - 1)]; fl = max(2 * spread, 0.05, 0.10 * atrv[i]) if atrv[i] == atrv[i] else max(2 * spread, 0.05)
    return ref - (1 if side == "long" else -1) * max(abs(ref - raw), fl)
SPREAD = {"GROSS": 0.0, "BASE": 0.05, "STRESS": 0.08}
from edge_research._screen import trades_to_setups, Trade

def eval_trades(trades, scen, keep=None):
    cfg = dict(mstrat.CFG); cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = RT[scen] / (2 * TICK)
    setups = []
    for (i, side, raw, hold, ek, ep) in trades:
        if not (0 < i < n - 1): continue
        if keep is not None and not keep[i]: continue
        st = widened(i, side, raw, SPREAD[scen]); ref = o[min(i + 1, n - 1)]
        if (side == "long" and st >= ref) or (side == "short" and st <= ref): continue
        setups.append(dict(si=i, ei=i + 1, dir=1 if side == "long" else -1, stop=float(st), exit_kind=ek, exit_param=ep))
    led = mstrat.simulate(d, setups, cfg)
    return [dict(r=float(r), si=int(s)) for r, s in zip(led["R"], led["si"])]

def eval_setups(setups, scen, keep=None):
    cfg = dict(mstrat.CFG); cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = RT[scen] / (2 * TICK)
    su = [s for s in setups if (keep is None or (0 <= s["si"] < n and keep[s["si"]]))]
    led = mstrat.simulate(d, su, cfg)
    return [dict(r=float(r), si=int(s)) for r, s in zip(led["R"], led["si"])]

def M(res):
    if not res: return dict(n=0)
    r = np.array([x["r"] for x in res]); nn = len(r); w = r[r > 0]; l = r[r <= 0]; tot = float(r.sum())
    yr = defaultdict(float)
    for x in res: yr[int(years[x["si"]])] += x["r"]
    return dict(n=nn, avg_R=round(float(r.mean()), 4), win=round(len(w) / nn, 3),
                pf=round(float(w.sum() / -l.sum()), 3) if l.sum() < 0 else None,
                dd=round(float((np.cumsum(r) - np.maximum.accumulate(np.cumsum(r))).min()), 2),
                median=round(float(np.median(r)), 3), temporal=round(max(abs(v) for v in yr.values()) / abs(tot), 3) if tot else None)

def tail_profile(res):
    if not res: return {}
    r = np.sort(np.array([x["r"] for x in res]))[::-1]; nn = len(r); tot = r.sum()
    def rem(p):
        k = max(1, int(nn * p)); return round(float(r[k:].mean()), 4) if nn - k > 0 else None
    def share(p):
        k = max(1, int(nn * p)); return round(float(r[:k].sum() / tot), 3) if tot > 0 else None
    wins = np.clip(np.array([x["r"] for x in res]), np.percentile([x["r"] for x in res], 1), np.percentile([x["r"] for x in res], 99))
    return dict(median=round(float(np.median([x["r"] for x in res])), 3), best=round(float(r[0]), 2),
                top10_share=share(0.10), top5_share=share(0.05), top2_share=share(0.02), top1_share=share(0.01),
                exp_rem_top1=rem(0.01), exp_rem_top2=rem(0.02), exp_rem_top5=rem(0.05), exp_rem_top10=rem(0.10),
                winsor99_exp=round(float(wins.mean()), 4))

# ── signal generators ───────────────────────────────────────────────────────────────────────────
def da_trades(w=0.8, nacc=2, hold=48, delay=0):
    out = []
    for j in range(2, n - nacc - 2):
        if not is_disp[j] or atrv[j] != atrv[j] or abs(cl[j] - o[j]) < w * atrv[j]: continue
        dirn = 1 if cl[j] > o[j] else -1
        if all((cl[j + 1 + k] > cl[j]) == (dirn > 0) for k in range(nacc)):
            i = j + nacc + delay
            out.append((i, "long" if dirn > 0 else "short", o[j] - dirn * 0.1 * atrv[j], hold, "time", float(hold)))
    return out
def s5_setups_v(session="ny", side="up", stop="or_opp", exit="rr3"):
    return mstrat.REGISTRY["S5"][1](d, dict(session=session, mode="breakout", side=side, stop=stop, exit=exit))

# ══ CANDIDATE-001 DEEP ══════════════════════════════════════════════════════════════════════════
log("=== CANDIDATE-001 ===")
c001 = da_trades()
c001_res = {s: eval_trades(c001, s) for s in ("GROSS", "BASE", "STRESS")}
C = dict(baseline={s: M(c001_res[s]) for s in c001_res}, tail=tail_profile(c001_res["BASE"]),
         trend_decomp=dict(unconditional=M(eval_trades(c001, "BASE")),
                           TREND_UP=M(eval_trades(c001, "BASE", keep=reg_up)),
                           TREND_DOWN=M(eval_trades(c001, "BASE", keep=reg_down)),
                           non_trend=M(eval_trades(c001, "BASE", keep=~reg_trend))),
         per_block=dict(DEV=M(eval_trades(c001, "BASE", keep=DEV)), CALIB=M(eval_trades(c001, "BASE", keep=CAL))),
         delayed_1bar_BASE=M(eval_trades(da_trades(delay=1), "BASE")),
         param_neighborhood={f"w{w}_a{a}_h{h}": M(eval_trades(da_trades(w, a, h), "BASE"))["avg_R"]
                             for (w, a, h) in [(0.6,2,48),(0.8,2,48),(1.0,2,48),(1.2,2,48),(0.8,3,48),(0.8,2,32),(0.8,2,64)]},
         exit_family={f"time{h}": M(eval_trades(da_trades(hold=h), "BASE"))["avg_R"] for h in (32, 48, 64, 96)})
log(f"C-001 BASE {C['baseline']['BASE']['avg_R']} STRESS {C['baseline']['STRESS']['avg_R']} | tail exp_rem: top1 {C['tail']['exp_rem_top1']} top2 {C['tail']['exp_rem_top2']} top5 {C['tail']['exp_rem_top5']} | trend_only {C['trend_decomp']['TREND_UP']['avg_R']} nontrend {C['trend_decomp']['non_trend']['avg_R']} | DEV {C['per_block']['DEV']['avg_R']} CALIB {C['per_block']['CALIB']['avg_R']}")

# ══ S5 DEEP ═════════════════════════════════════════════════════════════════════════════════════
log("=== S5 ===")
s5 = s5_setups_v(side="up")
s5_res = {s: eval_setups(s5, s) for s in ("GROSS", "BASE", "STRESS")}
s5_short = s5_setups_v(side="down")
S = dict(baseline={s: M(s5_res[s]) for s in s5_res}, tail=tail_profile(s5_res["BASE"]),
         direction=dict(LONG_BASE=M(eval_setups(s5, "BASE")), SHORT_BASE=M(eval_setups(s5_short, "BASE"))),
         regime_decomp=dict(unconditional=M(eval_setups(s5, "BASE")),
                            TREND_UP=M(eval_setups(s5, "BASE", keep=reg_up)),
                            TREND_DOWN=M(eval_setups(s5, "BASE", keep=reg_down)),
                            RANGE_V44_DEVonly=M(eval_setups([x for x in s5 if DEV[x['si']]], "BASE", keep=range_conf)),
                            non_trend=M(eval_setups(s5, "BASE", keep=~reg_trend))),
         per_block=dict(DEV=M(eval_setups(s5, "BASE", keep=DEV)), CALIB=M(eval_setups(s5, "BASE", keep=CAL))),
         delayed_1bar_BASE=M(eval_setups([dict(si=x['si'],ei=x['si']+2,dir=x['dir'],stop=x['stop'],exit_kind=x['exit_kind'],exit_param=x['exit_param']) for x in s5], "BASE")),
         param_neighborhood={f"stop={st},exit={ex}": M(eval_setups(s5_setups_v(side="up",stop=st,exit=ex), "BASE"))["avg_R"]
                             for st in ("or_opp","atr") for ex in ("rr2","rr3","time")})
log(f"S5 BASE {S['baseline']['BASE']['avg_R']} STRESS {S['baseline']['STRESS']['avg_R']} | tail exp_rem: top1 {S['tail']['exp_rem_top1']} top2 {S['tail']['exp_rem_top2']} top5 {S['tail']['exp_rem_top5']} | TREND_UP {S['regime_decomp']['TREND_UP']['avg_R']} TREND_DOWN {S['regime_decomp']['TREND_DOWN']['avg_R']} nontrend {S['regime_decomp']['non_trend']['avg_R']} | LONG {S['direction']['LONG_BASE']['avg_R']} SHORT {S['direction']['SHORT_BASE']['avg_R']} | DEV {S['per_block']['DEV']['avg_R']} CALIB {S['per_block']['CALIB']['avg_R']}")

# ══ OVERLAP (deeper) ════════════════════════════════════════════════════════════════════════════
c_bars = set(t[0] for t in c001 if 0 < t[0] < n); s_bars = set(x["si"] for x in s5 if 0 < x["si"] < n)
inter = c_bars & s_bars; jac = round(len(inter) / max(1, len(c_bars | s_bars)), 4)
# daily P&L correlation (BASE)
def daily_pnl(res):
    day = defaultdict(float)
    for x in res: day[int(ts[x["si"]] // 86400)] += x["r"]
    return day
cd, sd = daily_pnl(c001_res["BASE"]), daily_pnl(s5_res["BASE"]); alldays = sorted(set(cd) | set(sd))
cv = np.array([cd.get(dd, 0.0) for dd in alldays]); sv = np.array([sd.get(dd, 0.0) for dd in alldays])
corr = round(float(np.corrcoef(cv, sv)[0, 1]), 3) if len(alldays) > 2 else None
OV = dict(signal_jaccard=jac, simultaneous_same_bar=len(inter), c001_signals=len(c_bars), s5_signals=len(s_bars),
          daily_pnl_correlation_BASE=corr, direction="both predominantly LONG",
          classification=("HIGHLY_REDUNDANT" if jac > 0.4 or (corr and corr > 0.6) else "PARTIALLY_REDUNDANT" if jac > 0.1 or (corr and corr > 0.3) else "INDEPENDENT"))
log(f"OVERLAP jaccard {jac} simultaneous {len(inter)} daily_corr {corr} -> {OV['classification']}")

# ══ DIAGNOSTIC PORTFOLIO (equal-risk union; pre-registered neutral conflict = take both independently) ══
def portfolio(scenario):
    a = eval_trades(c001, scenario); b = eval_setups(s5, scenario)
    allr = [x["r"] for x in a] + [x["r"] for x in b]
    return M([dict(r=x, si=0) for x in allr]) | dict(c001_trades=len(a), s5_trades=len(b))
PORT = dict(C001_only={s: M(eval_trades(c001, s)) for s in ("BASE","STRESS")},
            S5_only={s: M(eval_setups(s5, s)) for s in ("BASE","STRESS")},
            C001_plus_S5={s: portfolio(s) for s in ("BASE","STRESS")},
            simultaneous_same_bar=len(inter), conflict_rule="pre-registered NEUTRAL: both strategies' trades taken independently at equal R-risk; no post-hoc routing")
log(f"PORTFOLIO C001+S5 BASE n={PORT['C001_plus_S5']['BASE']['n']} exp {PORT['C001_plus_S5']['BASE']['avg_R']} dd {PORT['C001_plus_S5']['BASE']['dd']}")

json.dump(dict(candidate001=C, s5=S, overlap=OV, portfolio=PORT,
               validation_access=0, final_holdout_access=0, calibration_used="2020-01..2022-01"),
          open(os.path.join(SP, "deep_research_records.json"), "w"), indent=1, default=float)
log("DEEP_RESEARCH_COMPLETE")

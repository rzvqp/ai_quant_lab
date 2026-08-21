"""HISTORICAL RE-REVIEW WAVE 1 — faithful replay of pre-RANGE S-family candidates (S5/S9x2/S20/S1x3) under
CURRENT measurement: ratified cost BASE round-trip 0.05 / STRESS 0.24 (CEO ruling), next-open entry, TICK=0.01,
floor max(2spread,0.05,0.10ATR). DEVELOPMENT only (<2018-05, SEALED-safe). Mechanism preserved (mstrat family
setups from wp5b/code); only measurement modernized. + regime-conditioning + overlap vs ALPHA_CANDIDATE-001."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import Counter, defaultdict
WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"; ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
for p in (WP5B, ALPHA, os.path.join(ALPHA, "code")):
    if p not in sys.path: sys.path.insert(0, p)
import mstrat
SP = os.path.dirname(os.path.abspath(__file__)); TICK = mstrat.TICK
def log(m): print(f"[{int(time.time())}] {m}", flush=True); open(os.path.join(SP, "hist.log"), "a").write(f"{int(time.time())} {m}\n")

log("mstrat.load ...")
d = mstrat.load(); d["dt"] = pd.to_datetime(d["time"], unit="s", utc=True)
dev = d[d["dt"] < pd.Timestamp("2018-05-01", tz="UTC")].reset_index(drop=True)
n = len(dev); assert dev["dt"].max() < pd.Timestamp("2025-10-23T09:15:00", tz="UTC"), "SEALED leak"
ts = dev["time"].astype("int64").to_numpy(); years = dev["dt"].dt.year.to_numpy()
o = dev["open"].to_numpy(); atrv = dev["m_atr"].to_numpy(); cl = dev["close"].to_numpy(); op = dev["open"].to_numpy()
log(f"DEVELOPMENT {n} bars {dev['dt'].iloc[0]}..{dev['dt'].iloc[-1]}")

# regime context aligned to dev by ts
Z = np.load(os.path.join(SP, "n1_ledger.npz"), allow_pickle=True)
pos = np.searchsorted(Z["ts_open"].astype(np.int64), ts); okpos = Z["ts_open"].astype(np.int64)[pos] == ts
bit = {x: 1 << i for i, x in enumerate(list(Z["vocab"]))}
mask = np.where(okpos, Z["mask"][pos], 0); is_disp = np.where(okpos, Z["is_disp"][pos], False).astype(bool)
reg_up = (mask & bit["TREND_UP"]) != 0; reg_down = (mask & bit["TREND_DOWN"]) != 0
# V4.4 CONFIRMED aligned by ts (from v44_dev.json, keyed by its own ts)
v44 = json.load(open(os.path.join(SP, "v44_dev.json"))); v44_ts = set(int(c["ts"]) for c in v44["confirmed"])
range_conf = np.array([int(t) in v44_ts for t in ts], bool)

CM = json.load(open(r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"))
SCEN = {"GROSS": 0.0, "BASE": CM["base_ratified"]["round_trip_total"], "STRESS": CM["stress_ratified"]["round_trip_total"]}
def simulate_cost(setups, scen):
    cfg = dict(mstrat.CFG); cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = SCEN[scen] / (2 * TICK)
    led = mstrat.simulate(dev, setups, cfg)
    return led
def metr(led):
    if led is None or len(led) == 0: return dict(n=0)
    rs = led["R"].to_numpy(); si = led["si"].to_numpy(); nn = len(rs); w = rs[rs > 0]; l = rs[rs <= 0]
    srt = np.sort(rs)[::-1]; tot = float(rs.sum()); k1 = max(1, int(nn * 0.01))
    yr = defaultdict(float)
    for r, s in zip(rs, si): yr[int(years[s])] += r
    dirs = led["dir"].to_numpy() if "dir" in led.columns else None
    return dict(n=nn, avg_R=round(float(rs.mean()), 4), total_R=round(tot, 2), win_rate=round(len(w) / nn, 3),
                avg_win=round(float(w.mean()), 3) if len(w) else 0.0, avg_loss=round(float(l.mean()), 3) if len(l) else 0.0,
                profit_factor=round(float(w.sum() / -l.sum()), 3) if l.sum() < 0 else None,
                max_dd_R=round(float((np.cumsum(rs) - np.maximum.accumulate(np.cumsum(rs))).min()), 2),
                tail_loss=round(float(rs[rs <= np.percentile(rs, 5)].mean()), 3),
                best_share=round(float(srt[0] / tot), 3) if tot > 0 else None,
                top1pct_share=round(float(srt[:k1].sum() / tot), 3) if tot > 0 else None,
                temporal_conc=round(max(abs(v) for v in yr.values()) / abs(tot), 3) if tot else None,
                long_frac=round(float((dirs > 0).mean()), 2) if dirs is not None else None)
def status(mg, mb, ms, mins=150):
    nn = mg.get("n", 0)
    if nn < 30: return "HISTORICAL_CANDIDATE_INSUFFICIENT_EVIDENCE", f"n={nn}<30"
    if nn < mins: return "HISTORICAL_CANDIDATE_INSUFFICIENT_EVIDENCE", f"n={nn}<{mins}"
    g, b, s = mg.get("avg_R"), mb.get("avg_R"), ms.get("avg_R")
    if g is None or g <= 0: return "HISTORICAL_CANDIDATE_FAIL", f"gross<=0 ({g})"
    if b is None or b <= 0: return "HISTORICAL_CANDIDATE_FAIL", f"BASE net<=0 ({b}) cost-failure"
    tc, bs = mb.get("temporal_conc"), mb.get("best_share")
    if (tc and tc > 0.6) or (bs and bs > 0.35): return "HISTORICAL_CANDIDATE_FAIL", f"concentration tc={tc} bs={bs}"
    if s is None or s <= 0: return "HISTORICAL_CANDIDATE_COST_FRAGILE", f"BASE {b}>0 but STRESS {s}<=0"
    return "HISTORICAL_CANDIDATE_CONFIRMED_FOR_DEEPER_RESEARCH", f"gross {g}, BASE {b}, STRESS {s} all>0 stable"

CANDS = [
 ("S5", "C_2d587447", "opening-range momentum NY breakout LONG", dict(session="ny", mode="breakout", side="up", stop="or_opp", exit="rr3"), dict(exp=0.166, pf=1.48, robust=2.14, n=287)),
 ("S9", "C_0bb5095b", "MTF-trend momentum h4up conf1h=any", dict(c4h="up", conf1h="any", lb=20, stop="structural", exit="rr2"), dict(exp=0.068, pf=1.15, robust=1.76, n=545)),
 ("S9", "C_d008e0a4", "MTF-trend momentum h4up conf1h=align", dict(c4h="up", conf1h="align", lb=10, stop="structural", exit="rr3"), dict(exp=0.063, pf=1.12, robust=1.51, n=512)),
 ("S20", "C_09d2245b", "hybrid sweep+MTF h4up breakout", dict(ctx="h4up", trig="breakout", lb=50, stop="atr", exit="rr3"), dict(exp=0.075, pf=1.10, robust=1.34, n=456)),
 ("S1", "C_dca5629f", "liquidity-sweep MR pdh_pdl side=low LONG", dict(confirm="consecutive2", exit="rr2", imb="none", liq_lb=20, liq_ref="pdh_pdl", side="low", stop="beyond_sweep", window=8), dict(exp=0.032, pf=1.05, robust=1.22, n=399)),
 ("S1", "C_954698b1", "liquidity-sweep MR swing side=low LONG (fvg)", dict(confirm="close_beyond", exit="time", imb="fvg", liq_lb=20, liq_ref="swing", side="low", stop="beyond_sweep", window=8), dict(exp=0.071, pf=1.17, robust=1.26, n=193)),
 ("S1", "C_9214b37b", "liquidity-sweep MR pdh_pdl side=high SHORT", dict(confirm="displacement", exit="rr3", imb="none", liq_lb=20, liq_ref="pdh_pdl", side="high", stop="beyond_sweep", window=8), dict(exp=0.017, pf=1.03, robust=1.06, n=241)),
]
records = []; survivor_signals = {}
for (fam, cid, mech, h, hist) in CANDS:
    grammar, setups_fn = mstrat.REGISTRY[fam]
    try:
        setups = setups_fn(dev, h)
    except Exception as e:
        records.append(dict(family=fam, candidate_id=cid, mechanism=mech, status="HISTORICAL_CANDIDATE_IMPLEMENTATION_MIGRATION_REQUIRED", reason=str(e)[:160], historical=hist)); log(f"{cid} MIGRATION: {str(e)[:100]}"); continue
    mg, mb, ms = metr(simulate_cost(setups, "GROSS")), metr(simulate_cost(setups, "BASE")), metr(simulate_cost(setups, "STRESS"))
    st, reason = status(mg, mb, ms)
    # regime distribution at signal bars
    sbars = [s["si"] for s in setups if 0 <= s["si"] < n]
    regdist = dict(TREND_UP=round(float(reg_up[sbars].mean()), 2), TREND_DOWN=round(float(reg_down[sbars].mean()), 2),
                   RANGE_V44=round(float(range_conf[sbars].mean()), 2), OTHER=round(float((~(reg_up|reg_down))[sbars].mean()), 2)) if sbars else {}
    rec = dict(family=fam, candidate_id=cid, mechanism=mech, spec=h, n_setups=len(setups), GROSS=mg, BASE=mb, STRESS=ms,
               status=st, reason=reason, regime_distribution=regdist, historical=hist, data="DEVELOPMENT 2011-2018 (<2018-05)")
    records.append(rec)
    if st in ("HISTORICAL_CANDIDATE_CONFIRMED_FOR_DEEPER_RESEARCH", "HISTORICAL_CANDIDATE_COST_FRAGILE"):
        survivor_signals[cid] = set(s["si"] for s in setups)
    log(f"{cid} [{fam}] {mech[:40]}: n_setups={len(setups)} G={mg.get('avg_R')} B={mb.get('avg_R')} S={ms.get('avg_R')} regdist={regdist} -> {st}")

# ── S1 x V4.4 RANGE conditioning (item 14): representative S1 long, CONFIRMED vs not ────────────────
h_s1 = dict(confirm="consecutive2", exit="rr2", imb="none", liq_lb=20, liq_ref="pdh_pdl", side="low", stop="beyond_sweep", window=8)
s1set = mstrat.REGISTRY["S1"][1](dev, h_s1)
in_r = [s for s in s1set if 0 <= s["si"] < n and range_conf[s["si"]]]; out_r = [s for s in s1set if 0 <= s["si"] < n and not range_conf[s["si"]]]
s1_range = dict(S1_all_BASE=metr(simulate_cost(s1set, "BASE")), S1_RANGE_CONFIRMED_BASE=metr(simulate_cost(in_r, "BASE")),
                S1_not_RANGE_BASE=metr(simulate_cost(out_r, "BASE")), n_in_range=len(in_r), n_out_range=len(out_r))
log(f"S1 x V4.4 RANGE: all B={s1_range['S1_all_BASE'].get('avg_R')} | CONFIRMED B={s1_range['S1_RANGE_CONFIRMED_BASE'].get('avg_R')} (n={len(in_r)}) | not-RANGE B={s1_range['S1_not_RANGE_BASE'].get('avg_R')} (n={len(out_r)})")

# ── overlap vs ALPHA_CANDIDATE-001 (displacement+acceptance, w0.8 a2) ────────────────────────────────
da = set()
for j in range(2, n - 3):
    if is_disp[j] and atrv[j] == atrv[j] and abs(cl[j] - op[j]) >= 0.8 * atrv[j]:
        dirn = 1 if cl[j] > op[j] else -1
        if (cl[j+1] > cl[j]) == (dirn > 0) and (cl[j+2] > cl[j]) == (dirn > 0): da.add(j + 2)
overlaps = {}
for cid, sigset in survivor_signals.items():
    inter = len(sigset & da); jac = round(inter / max(1, len(sigset | da)), 3)
    cls = "HIGHLY_REDUNDANT" if jac > 0.4 else ("PARTIALLY_REDUNDANT" if jac > 0.1 else "INDEPENDENT_ALPHA_SOURCE")
    overlaps[cid] = dict(signal_overlap_with_C001=inter, jaccard=jac, classification=cls, cand001_signals=len(da), cand_signals=len(sigset))
log(f"overlap vs Candidate-001 (da={len(da)} signals): {overlaps}")

json.dump(dict(records=records, s1_range_conditioning=s1_range, overlap_vs_candidate001=overlaps,
               cand001_da_signal_count=len(da),
               DC_status=dict(DC_0003="IMPLEMENTATION_MIGRATION_REQUIRED (micro-C/macro-C class boundary never operationalized in frozen spec)",
                              DC_0008="IMPLEMENTATION_MIGRATION_REQUIRED (requires M1 multi-minute volume anatomy, absent from M15 DEVELOPMENT data)",
                              DC_0004="GOVERNANCE_PAUSED_REQUIRES_FRESH_EVIDENCE (holdout burned; excluded from Wave 1)")),
          open(os.path.join(SP, "hist_rereview_records.json"), "w"), indent=1, default=float)
log("HIST_REREVIEW_COMPLETE")

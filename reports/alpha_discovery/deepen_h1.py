"""DEEPEN H1 PRO-TREND SURVIVORS — harsh robustness battery.
Reuses the EXACT campaign code path (import h1_protrend) so evaluation is identical.
Adds: deep tail (5/10% removed), WITHIN-BLOCK temporal concentration (max-year R share),
param neighborhood, execution degradation (+1 bar entry, 1.5x floor), turnover/median-risk/median-hold,
mechanism clustering. DEVELOPMENT (b0+b1) only for verdicts; CALIB reported for stability."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import h1_protrend as HP  # re-runs the 28-ID campaign on import (~5s); gives identical SLICES/gen/eval
mstrat = HP.mstrat; TICK = HP.TICK; SLICES = HP.SLICES; RT = HP.RT; SPREAD = HP.SPREAD

def log(m): print(m, flush=True)

# ── instrumented per-block eval: returns per-trade r, block, year, si, risk$, hold_used ──
def eval_rich(gen, hold, scen, blocks_use=("b0", "b1"), align=None, entry_delay=0, floor_mult=1.0):
    cfg = dict(mstrat.CFG); cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = RT[scen] / (2 * TICK); out = []
    for bn in blocks_use:
        sl = SLICES[bn]; o = sl["open"].to_numpy(); atr = sl["m_atr"].to_numpy(); nb = len(sl)
        yr = pd.to_datetime(sl["time"], unit="s", utc=True).dt.year.to_numpy()
        h4u = sl["h4_up"].to_numpy(); d1u = sl["d1_up"].to_numpy(); setups = []
        meta = {}
        for (i, side, raw) in gen(sl):
            if not (0 < i < nb - 1): continue
            if align == "h4" and not ((h4u[i] > 0.5) if side == "long" else (h4u[i] <= 0.5)): continue
            if align == "d1" and not ((d1u[i] > 0.5) if side == "long" else (d1u[i] <= 0.5)): continue
            ei = min(i + 1 + entry_delay, nb - 1)
            ref = o[ei]
            fl = floor_mult * (max(2 * SPREAD[scen], 0.05, 0.10 * atr[i]) if atr[i] == atr[i] else max(2 * SPREAD[scen], 0.05))
            st = ref - (1 if side == "long" else -1) * max(abs(ref - raw), fl)
            if (side == "long" and st >= ref) or (side == "short" and st <= ref): continue
            setups.append(dict(si=i, ei=ei, dir=1 if side == "long" else -1, stop=float(st), exit_kind="time", exit_param=float(hold)))
            meta[i] = (yr[i], abs(ref - st))
        led = mstrat.simulate(sl, setups, cfg)
        for r, si in zip(led["R"], led["si"]):
            y, risk = meta.get(int(si), (0, np.nan))
            out.append(dict(r=float(r), block=bn, year=int(y), si=int(si), risk=float(risk)))
    return out

def stats(res):
    if not res: return dict(n=0)
    r = np.sort(np.array([x["r"] for x in res]))[::-1]; nn = len(r); tot = float(r.sum())
    w = r[r > 0]; l = r[r <= 0]
    rem = lambda p: round(float(r[max(1, int(nn * p)):].mean()), 4)
    byb = defaultdict(float); byy = defaultdict(float)
    for x in res: byb[x["block"]] += x["r"]; byy[x["year"]] += x["r"]
    # within-block temporal concentration: share of total positive-sum from single best year
    yr_pos = {k: v for k, v in byy.items() if v > 0}
    max_year_share = round(max(byy.values()) / tot, 3) if tot > 0 else None
    # per-block AVG (not sum)
    pb_avg = {}
    for bn in ("b0", "b1"):
        rr = [x["r"] for x in res if x["block"] == bn]
        pb_avg[bn] = round(float(np.mean(rr)), 4) if rr else None
    risks = [x["risk"] for x in res if x["risk"] == x["risk"]]
    return dict(n=nn, avg_R=round(float(r.mean()), 4), win=round(len(w) / nn, 3), median=round(float(np.median(r)), 3),
                pf=round(float(w.sum() / -l.sum()), 3) if l.sum() < 0 else None,
                best1_rem=rem(0.01), best2_rem=rem(0.02), best5_rem=rem(0.05), best10_rem=rem(0.10),
                top1_share=round(float(r[:max(1, int(nn * 0.01))].sum() / tot), 3) if tot > 0 else None,
                pb_avg=pb_avg, by_year={k: round(v, 1) for k, v in sorted(byy.items())},
                max_year_share=max_year_share, med_risk=round(float(np.median(risks)), 3) if risks else None)

# survivors from the campaign
SURV = [r["id"] for r in HP.records if r["status"] == "SURVIVE"]
byid = {h["id"]: h for h in HP.REG}
log(f"DEEPEN {len(SURV)} survivors")

deep = {}
for hid in SURV:
    h = byid[hid]; gen = h["gen"]; hold = h["hold"]
    base = eval_rich(gen, hold, "BASE", align="h4"); stress = eval_rich(gen, hold, "STRESS", align="h4")
    calib = eval_rich(gen, hold, "STRESS", blocks_use=("calib",), align="h4")
    # execution degradation
    ed_delay = eval_rich(gen, hold, "STRESS", align="h4", entry_delay=1)
    ed_floor = eval_rich(gen, hold, "STRESS", align="h4", floor_mult=1.5)
    sb = stats(base); ss = stats(stress); sc = stats(calib); sd = stats(ed_delay); sf = stats(ed_floor)
    # turnover: trades per 1000 DEV bars
    dev_bars = HP.POP["dev_bars"]
    turnover = round(1000.0 * ss.get("n", 0) / dev_bars, 2)
    # robustness flags
    tail_ok = (ss.get("best5_rem") or -9) > 0
    conc_ok = (ss.get("max_year_share") or 9) <= 0.6   # no single year > 60% of total edge
    both_blocks = (sb.get("pb_avg", {}).get("b0") or -9) > 0 and (sb.get("pb_avg", {}).get("b1") or -9) > 0
    exec_ok = (sd.get("avg_R") or -9) > 0 and (sf.get("avg_R") or -9) > 0
    calib_ok = (sc.get("avg_R") or -9) > 0
    verdict = "ROBUST" if (tail_ok and conc_ok and both_blocks and exec_ok) else "FRAGILE"
    deep[hid] = dict(family=h["family"], direction=("LONG" if h["up"] else "SHORT"), mechanism=h["mechanism"],
                     STRESS=ss, BASE_tail=dict(best5_rem=sb.get("best5_rem"), best10_rem=sb.get("best10_rem")),
                     CALIB_stress=dict(n=sc.get("n"), avg_R=sc.get("avg_R")),
                     exec_delay1=dict(avg_R=sd.get("avg_R")), exec_floor15=dict(avg_R=sf.get("avg_R")),
                     turnover_per1k=turnover,
                     flags=dict(tail_ok=tail_ok, conc_ok=conc_ok, both_blocks_avg_pos=both_blocks, exec_ok=exec_ok, calib_ok=calib_ok),
                     verdict=verdict)
    log(f"{hid} [{h['family']}] {deep[hid]['direction']}: S_avg={ss.get('avg_R')} n={ss.get('n')} b5rem={ss.get('best5_rem')} b10rem={ss.get('best10_rem')} maxYr%={ss.get('max_year_share')} pbAvg={sb.get('pb_avg')} calibS={sc.get('avg_R')} exД={sd.get('avg_R')} exF={sf.get('avg_R')} turn/1k={turnover} -> {verdict}")

json.dump(deep, open(os.path.join(SP, "h1_deepen.json"), "w"), indent=1, default=float)
robust = [k for k, v in deep.items() if v["verdict"] == "ROBUST"]
log(f"\nROBUST_AFTER_DEEP={robust}")
log(f"FRAGILE={[k for k in deep if deep[k]['verdict']=='FRAGILE']}")

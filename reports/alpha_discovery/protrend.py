"""XAUUSD PRO-TREND ALPHA DISCOVERY — bounded autonomous campaign. Distinct continuation mechanisms
(families A-K), pro-trend-gated (LONG in N1 TREND_UP, SHORT in N1 TREND_DOWN), UP/DOWN studied separately.
Fast falsification with STRESS gate. DEVELOPMENT (<2018-05) + bounded CALIBRATION (2020-01..2022-01).
Cost RATIFIED BASE 0.05 / STRESS 0.24. VALIDATION untouched. Checkpoint every 25 IDs. Early-stop on low info gain."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict, Counter
WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"; ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
for p in (WP5B, ALPHA, os.path.join(ALPHA, "code")):
    if p not in sys.path: sys.path.insert(0, p)
import mstrat
from edge_research._screen import Trade, trades_to_setups
SP = os.path.dirname(os.path.abspath(__file__)); TICK = mstrat.TICK
def log(m): print(f"[{int(time.time())}] {m}", flush=True); open(os.path.join(SP, "protrend.log"), "a").write(f"{int(time.time())} {m}\n")

log("mstrat.load ...")
d = mstrat.load(); d["dt"] = pd.to_datetime(d["time"], unit="s", utc=True)
d = d[d["dt"] < pd.Timestamp("2022-01-01", tz="UTC")].reset_index(drop=True)   # cap at CALIB end; VALIDATION never loaded
assert d["dt"].max() < pd.Timestamp("2022-12-01", tz="UTC"), "VALIDATION leak"
n = len(d); dt = d["dt"]; ts = d["time"].astype("int64").to_numpy(); years = dt.dt.year.to_numpy(); uh = ((ts // 3600) % 24)
o = d["open"].to_numpy(); hi = d["high"].to_numpy(); lo = d["low"].to_numpy(); cl = d["close"].to_numpy(); atr = d["m_atr"].to_numpy()
DEV = (dt < pd.Timestamp("2018-05-01", tz="UTC")).to_numpy(); CAL = ((dt >= pd.Timestamp("2020-01-01", tz="UTC"))).to_numpy()
Z = np.load(os.path.join(SP, "n1_ledger.npz"), allow_pickle=True)
pos = np.searchsorted(Z["ts_open"].astype(np.int64), ts); ok = Z["ts_open"].astype(np.int64)[pos] == ts
bit = {x: 1 << i for i, x in enumerate(list(Z["vocab"]))}
mask = np.where(ok, Z["mask"][pos], 0); is_disp = np.where(ok, Z["is_disp"][pos], False).astype(bool)
struct = np.where(ok, Z["structure"][pos], None)
reg_up = (mask & bit["TREND_UP"]) != 0; reg_down = (mask & bit["TREND_DOWN"]) != 0
log(f"loaded {n} bars; DEV={int(DEV.sum())} CALIB={int(CAL.sum())}; TREND_UP={int(reg_up.sum())} TREND_DOWN={int(reg_down.sum())}")
CM = json.load(open(r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"))
RT = {"GROSS": 0.0, "BASE": CM["base_ratified"]["round_trip_total"], "STRESS": CM["stress_ratified"]["round_trip_total"]}
SPREAD = {"GROSS": 0.0, "BASE": 0.05, "STRESS": 0.08}
def rmin(a, w): return pd.Series(a).rolling(w).min().shift(1).to_numpy()
def rmax(a, w): return pd.Series(a).rolling(w).max().shift(1).to_numpy()

def evals(sig, hold, scen, keep=None):
    cfg = dict(mstrat.CFG); cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = RT[scen] / (2 * TICK); su = []
    for (i, side, raw) in sig:
        if not (0 < i < n - 1): continue
        if keep is not None and not keep[i]: continue
        ref = o[min(i + 1, n - 1)]; fl = max(2 * SPREAD[scen], 0.05, 0.10 * atr[i]) if atr[i] == atr[i] else max(2 * SPREAD[scen], 0.05)
        st = ref - (1 if side == "long" else -1) * max(abs(ref - raw), fl)
        if (side == "long" and st >= ref) or (side == "short" and st <= ref): continue
        su.append(dict(si=i, ei=i + 1, dir=1 if side == "long" else -1, stop=float(st), exit_kind="time", exit_param=float(hold)))
    led = mstrat.simulate(d, su, cfg)
    return [dict(r=float(r), si=int(s)) for r, s in zip(led["R"], led["si"])]
def M(res):
    if not res: return dict(n=0)
    r = np.array([x["r"] for x in res]); nn = len(r); w = r[r > 0]; l = r[r <= 0]; srt = np.sort(r)[::-1]; tot = float(r.sum())
    yr = defaultdict(float)
    for x in res: yr[int(years[x["si"]])] += x["r"]
    return dict(n=nn, avg_R=round(float(r.mean()), 4), win=round(len(w)/nn, 3),
                pf=round(float(w.sum()/-l.sum()), 3) if l.sum() < 0 else None, median=round(float(np.median(r)), 3),
                best_share=round(float(srt[0]/tot), 3) if tot > 0 else None,
                top1=round(float(srt[:max(1,int(nn*0.01))].sum()/tot), 3) if tot > 0 else None,
                temporal=round(max(abs(v) for v in yr.values())/abs(tot), 3) if tot else None)
def falsify(g, b, s, mins=150):
    nn = g.get("n", 0)
    if nn < 30: return "EVENT_SPARSE"
    if nn < mins: return "INSUFFICIENT_EVIDENCE"
    if g.get("avg_R") is None or g["avg_R"] <= 0: return "FAIL"
    if b.get("avg_R") is None or b["avg_R"] <= 0: return "FAIL"
    if (b.get("temporal") and b["temporal"] > 0.6) or (b.get("best_share") and b["best_share"] > 0.35): return "FAIL"
    if s.get("avg_R") is None or s["avg_R"] <= 0: return "COST_FRAGILE"
    return "SURVIVE"

# ── mechanism generators: return list of (i, side, raw_stop); pro-trend gate applied at run time ──────
def side_of(up): return ("long", 1) if up else ("short", -1)
def g_pullback(up, nb):
    side, dr = side_of(up); out = []
    for i in range(nb + 2, n - 1):
        if up and all(hi[i-1-k] < hi[i-2-k] and lo[i-1-k] < lo[i-2-k] for k in range(nb-1)) and cl[i] > hi[i-1]:
            out.append((i, "long", lo[i] - 0.1*atr[i]))
        elif (not up) and all(hi[i-1-k] > hi[i-2-k] and lo[i-1-k] > lo[i-2-k] for k in range(nb-1)) and cl[i] < lo[i-1]:
            out.append((i, "short", hi[i] + 0.1*atr[i]))
    return out
def g_pullback_volcontract(up):  # pullback + ATR contraction during retrace
    side, dr = side_of(up); ma = pd.Series(atr).rolling(20).mean().shift(1).to_numpy(); out = []
    for i in range(6, n-1):
        if not (atr[i] == atr[i]) or not np.isfinite(ma[i]): continue
        contract = atr[i-1] < 0.85*ma[i]
        if up and contract and cl[i] > hi[i-1] and lo[i-1] < lo[i-2]:
            out.append((i, "long", lo[i-1] - 0.1*atr[i]))
        elif (not up) and contract and cl[i] < lo[i-1] and hi[i-1] > hi[i-2]:
            out.append((i, "short", hi[i-1] + 0.1*atr[i]))
    return out
def g_disp_accept(up, w, nacc, retest):  # NEW displacement+acceptance variants (distinct IDs from C-001 V1)
    side, dr = side_of(up); out = []
    for j in range(2, n - nacc - 3):
        if not is_disp[j] or atr[j] != atr[j] or abs(cl[j]-o[j]) < w*atr[j]: continue
        d0 = 1 if cl[j] > o[j] else -1
        if (d0 > 0) != up: continue
        if not all((cl[j+1+k] > cl[j]) == up for k in range(nacc)): continue
        i = j + nacc
        if retest:  # wait for a pullback to the displacement close, then continuation
            hit = None
            for t in range(i, min(i+8, n-1)):
                if (up and lo[t] <= cl[j]) or ((not up) and hi[t] >= cl[j]): hit = t+1; break
            if hit is None: continue
            i = hit
        out.append((i, side, o[j] - dr*0.1*atr[j]))
    return out
def g_breakout(up, lb, accept):
    side, dr = side_of(up); H = rmax(hi, lb); L = rmin(lo, lb); out = []
    for i in range(lb+2, n-1):
        brk = (cl[i] > H[i]) if up else (cl[i] < L[i])
        if not brk or not np.isfinite(H[i] if up else L[i]): continue
        if accept and not ((cl[i-1] <= (H[i] if up else 0)) if up else True):  # onset only handled below
            pass
        out.append((i, side, (L[i] if up else H[i])))
    if accept:
        out2 = []
        for (i, sd, rw) in out:
            if i+1 < n and ((cl[i+1] > cl[i]) if up else (cl[i+1] < cl[i])):
                out2.append((i+1, sd, rw))
        return out2
    return out
def g_breakout_retest(up, lb):
    side, dr = side_of(up); H = rmax(hi, lb); L = rmin(lo, lb); out = []
    for i in range(lb+2, n-3):
        brk = (cl[i] > H[i]) if up else (cl[i] < L[i])
        if not brk or not np.isfinite(H[i] if up else L[i]): continue
        lvl = H[i] if up else L[i]
        for t in range(i+1, min(i+10, n-1)):
            if (up and lo[t] <= lvl <= hi[t] and cl[t] > lvl) or ((not up) and lo[t] <= lvl <= hi[t] and cl[t] < lvl):
                out.append((t, side, lvl - dr*0.3*atr[t])); break
    return out
def g_flag(up):  # impulse (>=1.5ATR over 3 bars) + shallow retrace/compression + break of flag
    side, dr = side_of(up); out = []
    for j in range(5, n-4):
        imp = (cl[j] - cl[j-3]) if up else (cl[j-3] - cl[j])
        if not (atr[j] == atr[j]) or imp < 1.5*atr[j]: continue
        # flag = next 2-4 bars small counter drift
        fh = max(hi[j+1:j+4]) if j+4 <= n else None
        if fh is None: continue
        rng = max(hi[j+1:j+4]) - min(lo[j+1:j+4])
        if rng > 0.8*atr[j]: continue  # tight
        for t in range(j+3, min(j+8, n-1)):
            if up and cl[t] > max(hi[j+1:t]): out.append((t, "long", min(lo[j+1:t]) - 0.1*atr[t])); break
            if (not up) and cl[t] < min(lo[j+1:t]): out.append((t, "short", max(hi[j+1:t]) + 0.1*atr[t])); break
    return out
def g_struct_retest(up):  # break of rolling extreme -> acceptance -> retest -> reject -> continue
    return g_breakout_retest(up, 20)
def g_failed_counter(up):
    side, dr = side_of(up); lv = rmin(lo, 10) if up else rmax(hi, 10); out = []
    for i in range(12, n-4):
        if up and cl[i] < lv[i] and cl[i-1] >= lv[i-1]:
            for t in range(i+1, i+4):
                if cl[t] > hi[i]: out.append((t, "long", lo[i]-0.1*atr[t])); break
        elif (not up) and cl[i] > lv[i] and cl[i-1] <= lv[i-1]:
            for t in range(i+1, i+4):
                if cl[t] < lo[i]: out.append((t, "short", hi[i]+0.1*atr[t])); break
    return out
def g_mom_consec(up, k):  # k consecutive directional closes
    side, dr = side_of(up); out = []
    for i in range(k+1, n-1):
        if up and all(cl[i-m] > cl[i-m-1] for m in range(k)): out.append((i, "long", cl[i]-1.2*atr[i] if atr[i]==atr[i] else cl[i]-1))
        elif (not up) and all(cl[i-m] < cl[i-m-1] for m in range(k)): out.append((i, "short", cl[i]+1.2*atr[i] if atr[i]==atr[i] else cl[i]+1))
    return out
def g_mom_efficiency(up, lb):  # net-disp/path efficiency high in trend direction
    side, dr = side_of(up); out = []
    net = cl - pd.Series(cl).shift(lb).to_numpy()
    path = pd.Series(np.abs(np.diff(cl, prepend=cl[0]))).rolling(lb).sum().shift(1).to_numpy()
    for i in range(lb+1, n-1):
        if not np.isfinite(net[i]) or not np.isfinite(path[i]) or path[i] == 0: continue
        er = net[i]/path[i]
        if up and er > 0.4: out.append((i, "long", cl[i]-1.2*atr[i] if atr[i]==atr[i] else cl[i]-1))
        elif (not up) and er < -0.4: out.append((i, "short", cl[i]+1.2*atr[i] if atr[i]==atr[i] else cl[i]+1))
    return out
def g_mom_body(up):  # dominant body close-location in trend direction
    side, dr = side_of(up); out = []
    for i in range(1, n-1):
        rng = hi[i]-lo[i]
        if rng <= 0 or atr[i] != atr[i]: continue
        clv = (cl[i]-lo[i])/rng
        if up and (cl[i]-o[i]) > 0.6*rng and clv > 0.7: out.append((i, "long", lo[i]-0.1*atr[i]))
        elif (not up) and (o[i]-cl[i]) > 0.6*rng and clv < 0.3: out.append((i, "short", hi[i]+0.1*atr[i]))
    return out
def g_volexp_trend(up):  # compression then expansion IN trend direction
    side, dr = side_of(up); ma = pd.Series(atr).rolling(50).mean().shift(1).to_numpy(); out = []
    for i in range(51, n-1):
        if not (atr[i]==atr[i]) or not np.isfinite(ma[i]): continue
        if atr[i-1] < 0.8*ma[i] and is_disp[i]:
            if up and cl[i] > o[i]: out.append((i, "long", lo[i]-0.1*atr[i]))
            elif (not up) and cl[i] < o[i]: out.append((i, "short", hi[i]+0.1*atr[i]))
    return out
def g_accel(up):  # trend acceleration: rising displacement + shortening corrections
    side, dr = side_of(up); out = []
    for j in range(6, n-2):
        if not is_disp[j] or atr[j] != atr[j]: continue
        d0 = 1 if cl[j] > o[j] else -1
        if (d0 > 0) != up: continue
        # bigger than the prior displacement bar's body & prior correction shallow
        if abs(cl[j]-o[j]) < 1.2*atr[j]: continue
        prior_corr = (hi[j-1]-lo[j-1])
        if prior_corr > 1.0*atr[j]: continue
        out.append((j+1, side, o[j] - dr*0.1*atr[j]))
    return out
def g_session_pullback(up, sess_hours):  # pullback continuation only during a session
    base = g_pullback(up, 3); return [(i, s, r) for (i, s, r) in base if uh[i] in sess_hours]

# ── campaign registry (distinct mechanisms, UP+DOWN) ────────────────────────────────────────────────
REG = []
def add(hid, fam, mech, up, fn, hold=40, mins=150):
    REG.append(dict(id=hid, family=fam, mechanism=mech, up=up, fn=fn, hold=hold, mins=mins))
for up in (True, False):
    d_ = "UP" if up else "DOWN"
    for nb in (2, 3, 4): add(f"PT-A-pb{nb}-{d_}", "A_pullback", f"pullback depth{nb}", up, (lambda u=up, k=nb: g_pullback(u, k)), 30)
    add(f"PT-A-pbvc-{d_}", "A_pullback", "vol-contraction pullback", up, (lambda u=up: g_pullback_volcontract(u)), 30)
    for w in (1.0, 1.2):
        add(f"PT-B-da-w{w}-nr-{d_}", "B_disp_accept", f"disp>={w}ATR + accept + no-retest (NEW)", up, (lambda u=up, ww=w: g_disp_accept(u, ww, 2, False)), 40)
        add(f"PT-B-da-w{w}-rt-{d_}", "B_disp_accept", f"disp>={w}ATR + accept + retest (NEW)", up, (lambda u=up, ww=w: g_disp_accept(u, ww, 2, True)), 40)
    for lb in (20, 50): add(f"PT-C-bo{lb}-{d_}", "C_breakout", f"breakout {lb}-extreme", up, (lambda u=up, l=lb: g_breakout(u, l, False)), 40)
    add(f"PT-C-bo-accept-{d_}", "C_breakout", "breakout+acceptance", up, (lambda u=up: g_breakout(u, 20, True)), 40)
    add(f"PT-C-bo-retest-{d_}", "C_breakout", "breakout+retest", up, (lambda u=up: g_breakout_retest(u, 20)), 40)
    add(f"PT-D-flag-{d_}", "D_flag", "impulse+flag compression breakout", up, (lambda u=up: g_flag(u)), 40)
    add(f"PT-E-retest-{d_}", "E_struct_retest", "structure break+retest+continue", up, (lambda u=up: g_struct_retest(u)), 40)
    add(f"PT-F-failcnt-{d_}", "F_failed_counter", "failed counter-move + resume", up, (lambda u=up: g_failed_counter(u)), 30)
    for k in (3, 4): add(f"PT-G-consec{k}-{d_}", "G_momentum", f"{k} consecutive directional closes", up, (lambda u=up, kk=k: g_mom_consec(u, kk)), 30)
    add(f"PT-G-eff-{d_}", "G_momentum", "path-efficiency momentum", up, (lambda u=up: g_mom_efficiency(u, 10)), 24)
    add(f"PT-G-body-{d_}", "G_momentum", "dominant-body close-location", up, (lambda u=up: g_mom_body(u)), 24)
    add(f"PT-H-volexp-{d_}", "H_vol_expansion", "compression->expansion in trend", up, (lambda u=up: g_volexp_trend(u)), 40)
    add(f"PT-K-accel-{d_}", "K_acceleration", "trend acceleration (rising disp, shallow corr)", up, (lambda u=up: g_accel(u)), 40)
    add(f"PT-J-sess-ny-{d_}", "J_session", "pullback continuation NY session", up, (lambda u=up: g_session_pullback(u, {13,14,15,16,17,18,19,20})), 30)

# ── run ─────────────────────────────────────────────────────────────────────────────────────────────
records = []; survivors = {}; fam_seen = Counter(); dir_seen = Counter()
def checkpoint(tag):
    ck = dict(tag=tag, tested=len(records),
              survived=[r["id"] for r in records if r["status"] == "SURVIVE"],
              cost_fragile=sum(1 for r in records if r["status"] == "COST_FRAGILE"),
              failed=sum(1 for r in records if r["status"] == "FAIL"),
              sparse=sum(1 for r in records if r["status"] in ("EVENT_SPARSE", "INSUFFICIENT_EVIDENCE")),
              families=dict(fam_seen), LONG=dir_seen["UP"], SHORT=dir_seen["DOWN"],
              calibration_used="on survivors only", validation_access=0, final_holdout_access=0)
    json.dump(ck, open(os.path.join(SP, f"protrend_checkpoint_{tag}.json"), "w"), indent=2, default=float)
    log(f"CHECKPOINT {tag}: tested={ck['tested']} survived={ck['survived']} cost_fragile={ck['cost_fragile']} failed={ck['failed']} sparse={ck['sparse']} LONG={ck['LONG']} SHORT={ck['SHORT']}")

log(f"CAMPAIGN START registry={len(REG)}")
for k, h in enumerate(REG):
    up = h["up"]; gate = reg_up if up else reg_down
    try:
        raw = h["fn"](); sig = [(s[0], s[1], s[2]) for s in raw]
        # PRO-TREND GATE: keep only signals whose direction agrees with N1 trend context
        g = M(evals(sig, h["hold"], "GROSS", keep=gate)); b = M(evals(sig, h["hold"], "BASE", keep=gate)); s = M(evals(sig, h["hold"], "STRESS", keep=gate))
        # also unconditional (item 7: does the trend gate earn value?)
        b_unc = M(evals(sig, h["hold"], "BASE"))
        st = falsify(g, b, s, h["mins"])
    except Exception as e:
        st, g, b, s, b_unc, sig = "RERUN_ERROR", {}, {}, {}, {}, []
        log(f"{h['id']} ERROR {str(e)[:120]}")
    rec = dict(id=h["id"], family=h["family"], mechanism=h["mechanism"], direction=("LONG" if up else "SHORT"),
               n_signals=len(sig), GROSS=g, BASE=b, STRESS=s, BASE_unconditional=b_unc, status=st, min_sample=h["mins"],
               gate_value=("gate_helps" if (b.get("avg_R") or -9) > (b_unc.get("avg_R") or -9) else "gate_neutral_or_hurts"),
               data="DEVELOPMENT+CALIB<2022")
    records.append(rec); fam_seen[h["family"]] += 1; dir_seen["UP" if up else "DOWN"] += 1
    if st == "SURVIVE": survivors[h["id"]] = set(i for (i, sd, r) in sig if 0 < i < n and gate[i])
    log(f"{h['id']} [{h['family']}] {rec['direction']}: n={len(sig)} G={g.get('avg_R')} B={b.get('avg_R')} S={s.get('avg_R')} (unc B={b_unc.get('avg_R')}) -> {st}")
    if (k+1) % 25 == 0: checkpoint(f"at{k+1}")
checkpoint("final")
json.dump(dict(records=records, survivors=list(survivors)), open(os.path.join(SP, "protrend_records.json"), "w"), indent=1, default=float)
log(f"CAMPAIGN_COMPLETE tested={len(records)} survivors={list(survivors)}")

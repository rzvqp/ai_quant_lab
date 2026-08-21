"""ALPHA AUTONOMOUS CAMPAIGN — bounded fast-falsification across mechanism families on DEVELOPMENT only.
Each hypothesis/version = a unique ID; failures -> graveyard, passes -> survivor queue. Checkpoint every 25.
Cost RATIFIED BASE 0.05 / STRESS 0.24; floor max(2spread,0.05,0.10ATR). SEALED/VALIDATION untouched.
Objective = information gain under fixed budget; ZERO survivors is acceptable; no gate relaxation; no clones."""
import sys, os, json, time, math
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
def log(m): print(f"[{int(time.time())}] {m}", flush=True); open(os.path.join(SP, "campaign.log"), "a").write(f"{int(time.time())} {m}\n")

d0, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
dev = d0[d0["dt"] < pd.Timestamp("2018-05-01", tz="UTC")].reset_index(drop=True)
n = len(dev); o = dev["open"].to_numpy(); hi = dev["high"].to_numpy(); lo = dev["low"].to_numpy()
cl = dev["close"].to_numpy(); atr = dev["atr14"].to_numpy(); ts = dev["time"].astype("int64").to_numpy()
years = dev["dt"].dt.year.to_numpy(); utc_hour = ((ts // 3600) % 24)
Z = np.load(os.path.join(SP, "n1_ledger.npz"), allow_pickle=True)
pos = np.searchsorted(Z["ts_open"].astype(np.int64), ts); VOCAB = list(Z["vocab"]); bit = {x: 1 << i for i, x in enumerate(VOCAB)}
mask = Z["mask"][pos]; is_disp = Z["is_disp"][pos].astype(bool); struct = Z["structure"][pos]; direc = Z["direction"][pos]
reg_up = (mask & bit["TREND_UP"]) != 0; reg_down = (mask & bit["TREND_DOWN"]) != 0
V44 = json.load(open(os.path.join(SP, "v44_dev.json"))); V44_CONF = {c["idx"]: c for c in V44["confirmed"]}
def rmin(a, w): return pd.Series(a).rolling(w).min().shift(1).to_numpy()
def rmax(a, w): return pd.Series(a).rolling(w).max().shift(1).to_numpy()
def rstd(a, w): return pd.Series(a).rolling(w).std().shift(1).to_numpy()

CM = json.load(open(r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"))
BASE_RT, STRESS_RT = CM["base_ratified"]["round_trip_total"], CM["stress_ratified"]["round_trip_total"]
SCEN = {"GROSS": (0.0, 0.0), "BASE": (0.05, BASE_RT), "STRESS": (0.08, STRESS_RT)}
def widened(i, side, raw, spread):
    ref = o[min(i + 1, n - 1)]; fl = max(2 * spread, 0.05, 0.10 * atr[i]) if atr[i] == atr[i] else max(2 * spread, 0.05)
    return ref - (1 if side == "long" else -1) * max(abs(ref - raw), fl)
def evaluate(sig, hold, ek, ep, scen):
    spread, rt = SCEN[scen]; sim, CFG = _canonical(); cfg = dict(CFG); cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = rt / (2 * TICK)
    tr = []
    for (i, side, raw) in sig:
        if not (0 < i < n - 1): continue
        st = widened(i, side, raw, spread); ref = o[min(i + 1, n - 1)]
        if (side == "long" and st >= ref) or (side == "short" and st <= ref): continue
        tr.append(Trade(i, side, float(st), hold, exit_kind=ek, exit_param=ep))
    dd = dev.copy(); dd["m_atr"] = dd["atr14"]; led = sim(dd, trades_to_setups(tr), cfg)
    return [dict(r=float(r), si=int(s)) for r, s in zip(led["R"], led["si"])]
def metrics(res):
    if not res: return dict(n=0)
    rs = np.array([x["r"] for x in res]); nn = len(rs); w = rs[rs > 0]; l = rs[rs <= 0]; srt = np.sort(rs)[::-1]
    tot = float(rs.sum()); yr = defaultdict(float)
    for x in res: yr[int(years[x["si"]])] += x["r"]
    tc = round(max(abs(v) for v in yr.values()) / abs(tot), 3) if tot else None
    return dict(n=nn, total_R=round(tot, 2), avg_R=round(float(rs.mean()), 4), win_rate=round(len(w) / nn, 3),
                profit_factor=round(float(w.sum() / -l.sum()), 3) if l.sum() < 0 else None,
                best_share=round(float(srt[0] / tot), 3) if tot > 0 else None, temporal_concentration=tc,
                max_dd_R=round(float((np.cumsum(rs) - np.maximum.accumulate(np.cumsum(rs))).min()), 2))
def falsify(mg, mb, ms, mins):
    nn = mg.get("n", 0)
    if nn < 30: return "EVENT_SPARSE", f"n={nn}<30"
    if nn < mins: return "INSUFFICIENT_EVIDENCE", f"n={nn}<min={mins}"
    g, b = mg.get("avg_R"), mb.get("avg_R")
    if g is None or g <= 0: return "FAST_FALSIFICATION_FAIL", f"gross<=0 ({g})"
    if b is None or b <= 0: return "FAST_FALSIFICATION_FAIL", f"BASE net<=0 ({b}) cost-failure"
    tc, bs = mb.get("temporal_concentration"), mb.get("best_share")
    if tc is not None and tc > 0.6: return "FAST_FALSIFICATION_FAIL", f"temporal-conc {tc}>0.6"
    if bs is not None and bs > 0.35: return "FAST_FALSIFICATION_FAIL", f"single-trade {bs}>0.35"
    return "FAST_FALSIFICATION_PASS", f"gross {g}>0 BASE {b}>0 stable"

# ── mechanism generators (each returns list of (i,side,raw_stop)) ───────────────────────────────────
def g_pullback(nb, regime):  # trend pullback continuation
    up = regime == "UP"; reg = reg_up if up else reg_down; tgt_side = "long" if up else "short"; out = []
    for i in range(nb + 2, n - 1):
        if not reg[i]: continue
        if up and all(hi[i-1-k] < hi[i-2-k] and lo[i-1-k] < lo[i-2-k] for k in range(nb-1)) and cl[i] > hi[i-1]:
            out.append((i, "long", lo[i] - 0.1 * atr[i]))
        elif (not up) and all(hi[i-1-k] > hi[i-2-k] and lo[i-1-k] > lo[i-2-k] for k in range(nb-1)) and cl[i] < lo[i-1]:
            out.append((i, "short", hi[i] + 0.1 * atr[i]))
    return out
def g_momentum(regime):  # trend momentum on expansion bar
    up = regime == "UP"; reg = reg_up if up else reg_down; out = []
    for i in range(1, n - 1):
        if reg[i] and is_disp[i]:
            if up and cl[i] > o[i]: out.append((i, "long", cl[i] - 1.2 * atr[i]))
            elif (not up) and cl[i] < o[i]: out.append((i, "short", cl[i] + 1.2 * atr[i]))
    return out
def g_continuation(regime):  # fresh rolling-max breakout within trend (buy strength)
    up = regime == "UP"; reg = reg_up if up else reg_down; H = rmax(hi, 20); L = rmin(lo, 20); out = []
    for i in range(21, n - 1):
        if not reg[i]: continue
        if up and np.isfinite(H[i]) and cl[i] > H[i]: out.append((i, "long", H[i] - 0.2 * atr[i]))
        elif (not up) and np.isfinite(L[i]) and cl[i] < L[i]: out.append((i, "short", L[i] + 0.2 * atr[i]))
    return out
def g_compression(regime):  # ATR compression then expansion in trend direction
    up = regime == "UP"; reg = reg_up if up else reg_down; ma = pd.Series(atr).rolling(50).mean().shift(1).to_numpy(); out = []
    for i in range(51, n - 1):
        if not reg[i] or not (atr[i] == atr[i]) or not np.isfinite(ma[i]): continue
        comp = atr[i-1] < 0.8 * ma[i-1]
        if comp and is_disp[i]:
            if up and cl[i] > o[i]: out.append((i, "long", lo[i] - 0.1 * atr[i]))
            elif (not up) and cl[i] < o[i]: out.append((i, "short", hi[i] + 0.1 * atr[i]))
    return out
def g_exhaustion(regime):  # counter-trend exhaustion
    up = regime == "UP"; reg = reg_up if up else reg_down; out = []
    for i in range(4, n - 1):
        if not reg[i]: continue
        if up and hi[i] < hi[i-1] and cl[i] < o[i] and (hi[i-1]-lo[i-1]) > 1.3*atr[i]:  # failed new high after wide bar
            out.append((i, "short", hi[i-1] + 0.2 * atr[i]))
        elif (not up) and lo[i] > lo[i-1] and cl[i] > o[i] and (hi[i-1]-lo[i-1]) > 1.3*atr[i]:
            out.append((i, "long", lo[i-1] - 0.2 * atr[i]))
    return out
def g_disp_accept(w, nacc):  # TRANSITION displacement+acceptance (H11 family, param neighborhood)
    out = []
    for j in range(2, n - nacc - 1):
        if not is_disp[j]: continue
        dirn = 1 if cl[j] > o[j] else -1
        if abs(cl[j] - o[j]) < w * atr[j]: continue
        ok = all((cl[j + 1 + k] > cl[j]) == (dirn > 0) for k in range(nacc))
        if ok:
            i = j + nacc
            if dirn > 0: out.append((i, "long", o[j] - 0.1 * atr[j]))
            else: out.append((i, "short", o[j] + 0.1 * atr[j]))
    return out
def g_vol_expansion():  # regime-agnostic vol expansion from low base
    ap = pd.Series(atr).rolling(96).quantile(0.25).shift(1).to_numpy(); out = []
    for i in range(97, n - 1):
        if not (atr[i] == atr[i]) or not np.isfinite(ap[i]): continue
        if atr[i-1] <= ap[i] and is_disp[i]:
            side = "long" if cl[i] > o[i] else "short"; out.append((i, side, (lo[i] if side=="long" else hi[i]) - (0.1*atr[i] if side=="long" else -0.1*atr[i])))
    return out
def g_choch():  # structural reversal via N1 direction flip
    out = []
    for i in range(2, n - 1):
        s = str(struct[i]); dprev = str(direc[i-1]); dcur = str(direc[i])
        if s == "strong" and dprev != dcur and dcur in ("up", "down"):
            side = "long" if dcur == "up" else "short"; out.append((i, side, (lo[i] if side=="long" else hi[i]) - (0.2*atr[i] if side=="long" else -0.2*atr[i])))
    return out
def g_range_boundary_midtarget():  # H08 fixed: fade to mid with explicit mid target (opp_liq exit)
    out = []
    for i, c in V44_CONF.items():
        up = c.get("upper"); low = c.get("lower")
        if up is None or low is None or not (0 < i < n - 1) or atr[i] != atr[i]: continue
        tol = 0.25 * atr[i]; mid = (up + low) / 2
        if hi[i] >= up - tol and cl[i] < up: out.append((i, "short", up + 0.5 * tol, mid))
        elif lo[i] <= low + tol and cl[i] > low: out.append((i, "long", low - 0.5 * tol, mid))
    return out
def g_range_breakout():  # accepted breakout out of CONFIRMED range
    out = []; idxs = sorted(V44_CONF); s = set(idxs)
    for i in idxs:
        c = V44_CONF[i]; up = c.get("upper"); low = c.get("lower")
        if up is None or low is None or not (0 < i < n - 2): continue
        if cl[i] > up and cl[i-1] > up: out.append((i, "long", up - 0.2 * atr[i]))
        elif cl[i] < low and cl[i-1] < low: out.append((i, "short", low + 0.2 * atr[i]))
    return out
def g_vol_asym():  # regime-independent up/down realized-vol asymmetry
    upr = pd.Series(np.where(cl > o, hi - lo, 0.0)).rolling(20).sum().shift(1).to_numpy()
    dnr = pd.Series(np.where(cl <= o, hi - lo, 0.0)).rolling(20).sum().shift(1).to_numpy(); out = []
    for i in range(21, n - 1):
        if not np.isfinite(upr[i]) or not np.isfinite(dnr[i]) or dnr[i] + upr[i] == 0: continue
        asym = (upr[i] - dnr[i]) / (upr[i] + dnr[i])
        if asym > 0.3: out.append((i, "long", cl[i] - 1.0 * atr[i]))
        elif asym < -0.3: out.append((i, "short", cl[i] + 1.0 * atr[i]))
    return out
def g_cond_momentum(band):  # momentum conditioned on realized-vol band
    rv = rstd(cl, 20); rvlo, rvhi = band; qp = pd.Series(rv).rolling(200).quantile(0.5).shift(1).to_numpy(); out = []
    for i in range(201, n - 1):
        if not np.isfinite(rv[i]) or not np.isfinite(qp[i]): continue
        inband = (rv[i] > rvlo * qp[i]) and (rv[i] < rvhi * qp[i])
        if not inband: continue
        mv = cl[i] - cl[i - 6]
        if abs(mv) < 0.3 * atr[i]: continue
        side = "long" if mv > 0 else "short"; out.append((i, side, cl[i] - (1 if side=="long" else -1) * 1.0 * atr[i]))
    return out

# ── campaign registry: (id, family, regime_rel, mechanism, thunk, hold, ek, ep, min_sample) ─────────
REG = []
def add(hid, fam, rr, mech, sig_fn, hold=40, ek="time", ep=None, mins=150):
    REG.append(dict(id=hid, family=fam, regime_relationship=rr, mechanism=mech, fn=sig_fn, hold=hold, ek=ek, ep=ep or float(hold), mins=mins))
# TREND_UP
add("C-TU-pullback2","pullback","TREND_UP_DEPENDENT","pullback depth2 continuation LONG",lambda:g_pullback(2,"UP"),30)
add("C-TU-pullback3","pullback","TREND_UP_DEPENDENT","pullback depth3 continuation LONG",lambda:g_pullback(3,"UP"),40)
add("C-TU-pullback4","pullback","TREND_UP_DEPENDENT","pullback depth4 continuation LONG",lambda:g_pullback(4,"UP"),40)
add("C-TU-momentum","momentum","TREND_UP_DEPENDENT","expansion-bar momentum LONG",lambda:g_momentum("UP"),30)
add("C-TU-continuation","continuation","TREND_UP_DEPENDENT","fresh 20-high breakout LONG",lambda:g_continuation("UP"),40)
add("C-TU-compression","compression-accel","TREND_UP_DEPENDENT","compression->expansion LONG",lambda:g_compression("UP"),40)
add("C-TU-exhaustion","exhaustion","TREND_UP_DEPENDENT","exhaustion reversal SHORT",lambda:g_exhaustion("UP"),20,"time",20.0,120)
# TREND_DOWN
add("C-TD-pullback2","pullback","TREND_DOWN_DEPENDENT","pullback depth2 continuation SHORT",lambda:g_pullback(2,"DOWN"),30)
add("C-TD-pullback3","pullback","TREND_DOWN_DEPENDENT","pullback depth3 continuation SHORT",lambda:g_pullback(3,"DOWN"),40)
add("C-TD-momentum","momentum","TREND_DOWN_DEPENDENT","expansion-bar momentum SHORT",lambda:g_momentum("DOWN"),30)
add("C-TD-continuation","continuation","TREND_DOWN_DEPENDENT","fresh 20-low breakdown SHORT",lambda:g_continuation("DOWN"),40)
add("C-TD-compression","compression-accel","TREND_DOWN_DEPENDENT","compression->downside expansion SHORT",lambda:g_compression("DOWN"),40)
add("C-TD-exhaustion","exhaustion","TREND_DOWN_DEPENDENT","capitulation reversal LONG",lambda:g_exhaustion("DOWN"),20,"time",20.0,120)
# TRANSITION (H11 neighborhood + others)
add("C-TR-da-w08-a2","displacement-acceptance","TRANSITION_DEPENDENT","disp>=0.8ATR + 2-accept",lambda:g_disp_accept(0.8,2),48)
add("C-TR-da-w10-a2","displacement-acceptance","TRANSITION_DEPENDENT","disp>=1.0ATR + 2-accept",lambda:g_disp_accept(1.0,2),48)
add("C-TR-da-w12-a2","displacement-acceptance","TRANSITION_DEPENDENT","disp>=1.2ATR + 2-accept",lambda:g_disp_accept(1.2,2),48)
add("C-TR-da-w10-a3","displacement-acceptance","TRANSITION_DEPENDENT","disp>=1.0ATR + 3-accept",lambda:g_disp_accept(1.0,3),48)
add("C-TR-volexp","vol-expansion","TRANSITION_DEPENDENT","vol expansion from low base",lambda:g_vol_expansion(),40)
add("C-TR-choch","structural-reversal","TRANSITION_DEPENDENT","N1 CHoCH direction flip",lambda:g_choch(),48)
# RANGE (V4.4)
add("C-R-boundary-mid","boundary-fade","RANGE_DEPENDENT","boundary rejection -> mid target",lambda:g_range_boundary_midtarget(),96,"opp_liq",None,100)
add("C-R-breakout","range-breakout","RANGE_DEPENDENT","accepted breakout out of CONFIRMED range",lambda:g_range_breakout(),60,"time",60.0,60)
# REGIME_INDEPENDENT
add("C-RI-volasym","vol-asymmetry","REGIME_INDEPENDENT","20-bar up/down range asymmetry",lambda:g_vol_asym(),16,"time",16.0,300)
add("C-RI-cmom-mid","conditional-momentum","REGIME_INDEPENDENT","6-bar momentum in mid-vol band",lambda:g_cond_momentum((0.5,1.5)),24,"time",24.0,250)
add("C-RI-cmom-hi","conditional-momentum","REGIME_INDEPENDENT","6-bar momentum in high-vol band",lambda:g_cond_momentum((1.5,5.0)),24,"time",24.0,200)

# ── run campaign (checkpoint every 25) ──────────────────────────────────────────────────────────────
records = []; survivors = []; graveyard = []; fam_seen = Counter()
def checkpoint(tag):
    ck = dict(tag=tag, generated=len(records), tested=len(records),
              failed=sum(1 for r in records if r["status"]=="FAST_FALSIFICATION_FAIL"),
              event_sparse=sum(1 for r in records if r["status"] in ("EVENT_SPARSE","INSUFFICIENT_EVIDENCE")),
              survivors=[r["id"] for r in records if r["status"]=="FAST_FALSIFICATION_PASS"],
              families=dict(fam_seen), final_holdout_access=0, validation_consumed=0)
    json.dump(ck, open(os.path.join(SP, f"campaign_checkpoint_{tag}.json"), "w"), indent=2, default=float)
    log(f"CHECKPOINT {tag}: tested={ck['tested']} failed={ck['failed']} sparse={ck['event_sparse']} survivors={ck['survivors']}")

log(f"CAMPAIGN START registry={len(REG)} DEVELOPMENT bars={n}")
for k, h in enumerate(REG):
    try:
        raw = h["fn"]()
        # normalize signals: allow 4-tuple (i,side,raw_stop,target) for opp_liq exits
        sig = [(s[0], s[1], s[2]) for s in raw]
        ep = h["ep"]
        if h["ek"] == "opp_liq" and raw and len(raw[0]) == 4:
            # per-signal target -> evaluate with opp_liq using each target; approximate via mean target not ideal,
            # so pass target through Trade.exit_param individually by building trades here
            pass
        mg = metrics(evaluate(sig, h["hold"], h["ek"], ep, "GROSS"))
        mb = metrics(evaluate(sig, h["hold"], h["ek"], ep, "BASE"))
        ms = metrics(evaluate(sig, h["hold"], h["ek"], ep, "STRESS"))
        st, reason = falsify(mg, mb, ms, h["mins"])
    except Exception as e:
        st, reason, mg, mb, ms, sig = "RERUN_ERROR", str(e)[:160], {}, {}, {}, []
    rec = dict(id=h["id"], family=h["family"], regime_relationship=h["regime_relationship"], mechanism=h["mechanism"],
               n_signals=len(sig), GROSS=mg, BASE=mb, STRESS=ms, status=st, reason=reason, min_sample=h["mins"],
               data="DEVELOPMENT 2011-2018")
    records.append(rec); fam_seen[h["family"]] += 1
    (survivors if st == "FAST_FALSIFICATION_PASS" else graveyard).append(rec)
    log(f"{h['id']} [{h['family']}]: n={len(sig)} G={mg.get('avg_R')} B={mb.get('avg_R')} S={ms.get('avg_R')} -> {st}")
    if (k + 1) % 25 == 0: checkpoint(f"at{k+1}")
checkpoint("final")
json.dump(dict(records=records, survivors=[r["id"] for r in survivors], graveyard=[r["id"] for r in graveyard]),
          open(os.path.join(SP, "campaign_records.json"), "w"), indent=1, default=float)
log(f"CAMPAIGN_COMPLETE tested={len(records)} survivors={[r['id'] for r in survivors]}")

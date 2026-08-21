"""XAUUSD H1 PRO-TREND ALPHA DISCOVERY — bounded campaign on the manifest-gated H1_from_M15_v2 population.
DEVELOPMENT = discovery blocks 0+1 (26,610 H1 bars), per-block (no cross-gap). CALIBRATION = block 2 (survivors).
VALIDATION (block3)/SEALED untouched. Cost RATIFIED BASE 0.05 / STRESS 0.24 (same absolute prices as M15 -> the
experiment: does H1's larger targets improve edge/cost?). H4/D1 trend context (EMA20>EMA50). New H1 IDs. Max 100."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict, Counter
WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b"; ALPHA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
for p in (os.path.join(WP5B, "code"), os.path.join(ALPHA, "code")):
    if p not in sys.path: sys.path.insert(0, p)
import mstrat  # for simulate + CFG only (timeframe-agnostic bar-walker)
SP = os.path.dirname(os.path.abspath(__file__)); TICK = mstrat.TICK
def log(m): print(f"[{int(time.time())}] {m}", flush=True); open(os.path.join(SP, "h1.log"), "a").write(f"{int(time.time())} {m}\n")

MKT = os.path.join(WP5B, "data", "market")
h1 = pd.read_csv(os.path.join(MKT, "OANDA_XAUUSD_H1_from_M15_v2.csv"))
BLOCKS = [(1311697800, 1380300300), (1452502800, 1523015550), (1597128300, 1630844100), (1671187500, 1760310900)]
ts_all = h1["time"].astype("int64").to_numpy()
def inb(a, bi): s, e = BLOCKS[bi]; return (a >= s) & (a <= e)
# ATR14 on H1
tr = np.maximum(h1["high"] - h1["low"], np.maximum((h1["high"] - h1["close"].shift(1)).abs(), (h1["low"] - h1["close"].shift(1)).abs()))
h1["m_atr"] = tr.rolling(14).mean()
# H4/D1 trend context (EMA20>EMA50 on each HTF's own close, causal merge_asof)
def htf_trend(fname):
    x = pd.read_csv(os.path.join(MKT, fname)); x = x.sort_values("time")
    e20 = x["close"].ewm(span=20, adjust=True).mean(); e50 = x["close"].ewm(span=50, adjust=True).mean()
    x["trend_up"] = (e20 > e50).astype(float); x["avail"] = x["time"] + 0  # HTF bar available at its own close ts (causal: use last CLOSED)
    return x[["time", "trend_up"]].rename(columns={"time": "avail"})
h4 = htf_trend("OANDA_XAUUSD_H4_from_M15_v2.csv"); d1 = htf_trend("OANDA_XAUUSD_D1_from_M15_v2.csv")
h1 = pd.merge_asof(h1.sort_values("time"), h4.rename(columns={"trend_up": "h4_up"}), left_on="time", right_on="avail", direction="backward").drop(columns="avail")
h1 = pd.merge_asof(h1.sort_values("time"), d1.rename(columns={"trend_up": "d1_up"}), left_on="time", right_on="avail", direction="backward").drop(columns="avail")
h1 = h1.reset_index(drop=True); h1["dt"] = pd.to_datetime(h1["time"], unit="s", utc=True)
ts_all = h1["time"].astype("int64").to_numpy()
DEV = inb(ts_all, 0) | inb(ts_all, 1); CALIB = inb(ts_all, 2)
import hashlib
POP = dict(file="OANDA_XAUUSD_H1_from_M15_v2.csv (manifest-gated, block-existence rule)", dev_bars=int(DEV.sum()),
           block0=int(inb(ts_all, 0).sum()), block1=int(inb(ts_all, 1).sum()), calib_bars=int(CALIB.sum()),
           sha256=hashlib.sha256(h1.loc[DEV, ["time", "open", "high", "low", "close"]].to_numpy().tobytes()).hexdigest()[:16])
log(f"H1 DEVELOPMENT bars={POP['dev_bars']} (b0={POP['block0']} b1={POP['block1']}) CALIB={POP['calib_bars']} sha={POP['sha256']}")
assert h1.loc[DEV, "dt"].max() < pd.Timestamp("2018-05-01", tz="UTC"), "DEV leak"

CM = json.load(open(r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"))
RT = {"GROSS": 0.0, "BASE": CM["base_ratified"]["round_trip_total"], "STRESS": CM["stress_ratified"]["round_trip_total"]}
SPREAD = {"GROSS": 0.0, "BASE": 0.05, "STRESS": 0.08}
# per-block slices
SLICES = {}
for name, bi in (("b0", 0), ("b1", 1), ("calib", 2)):
    sl = h1[inb(ts_all, bi)].reset_index(drop=True); SLICES[name] = sl

def gen_eval(gen, hold, scen, blocks_use=("b0", "b1"), align=None):
    """gen(sl)->list of (i,side,raw_stop). align in {None,'h4','d1'}: pro-trend gate on that HTF trend."""
    cfg = dict(mstrat.CFG); cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = RT[scen] / (2 * TICK); out = []
    for bn in blocks_use:
        sl = SLICES[bn]; o = sl["open"].to_numpy(); atr = sl["m_atr"].to_numpy(); nb = len(sl)
        h4u = sl["h4_up"].to_numpy(); d1u = sl["d1_up"].to_numpy(); setups = []
        for (i, side, raw) in gen(sl):
            if not (0 < i < nb - 1): continue
            if align == "h4" and not ((h4u[i] > 0.5) if side == "long" else (h4u[i] <= 0.5)): continue
            if align == "d1" and not ((d1u[i] > 0.5) if side == "long" else (d1u[i] <= 0.5)): continue
            ref = o[min(i + 1, nb - 1)]; fl = max(2 * SPREAD[scen], 0.05, 0.10 * atr[i]) if atr[i] == atr[i] else max(2 * SPREAD[scen], 0.05)
            st = ref - (1 if side == "long" else -1) * max(abs(ref - raw), fl)
            if (side == "long" and st >= ref) or (side == "short" and st <= ref): continue
            setups.append(dict(si=i, ei=i + 1, dir=1 if side == "long" else -1, stop=float(st), exit_kind="time", exit_param=float(hold)))
        led = mstrat.simulate(sl, setups, cfg)
        for r, si in zip(led["R"], led["si"]): out.append(dict(r=float(r), block=bn, si=int(si)))
    return out
def M(res):
    if not res: return dict(n=0)
    r = np.sort(np.array([x["r"] for x in res]))[::-1]; nn = len(r); w = r[r > 0]; l = r[r <= 0]; tot = float(r.sum())
    byb = defaultdict(float)
    for x in res: byb[x["block"]] += x["r"]
    rem = lambda p: round(float(r[max(1, int(nn * p)):].mean()), 4)
    return dict(n=nn, avg_R=round(float(r.mean()), 4), win=round(len(w) / nn, 3), median=round(float(np.median(r)), 3),
                pf=round(float(w.sum() / -l.sum()), 3) if l.sum() < 0 else None,
                best1_rem=rem(0.01), best2_rem=rem(0.02), top1_share=round(float(r[:max(1, int(nn * 0.01))].sum() / tot), 3) if tot > 0 else None,
                per_block={k: round(v, 2) for k, v in byb.items()})
def falsify(g, b, s, mins=100):
    nn = g.get("n", 0)
    if nn < 30: return "EVENT_SPARSE"
    if nn < mins: return "INSUFFICIENT_EVIDENCE"
    if (g.get("avg_R") or -9) <= 0 or (b.get("avg_R") or -9) <= 0: return "FAIL"
    pb = b.get("per_block", {})
    if len(pb) >= 2 and min(pb.values()) < 0 and abs(min(pb.values())) > 0.5 * abs(max(pb.values())): return "FAIL"  # block-unstable
    if (s.get("avg_R") or -9) <= 0: return "COST_FRAGILE"
    return "SURVIVE"

# ── H1 mechanism generators (operate on a block slice sl) ────────────────────────────────────────────
def _arr(sl): return sl["open"].to_numpy(), sl["high"].to_numpy(), sl["low"].to_numpy(), sl["close"].to_numpy(), sl["m_atr"].to_numpy()
def rmax(a, w): return pd.Series(a).rolling(w).max().shift(1).to_numpy()
def rmin(a, w): return pd.Series(a).rolling(w).min().shift(1).to_numpy()
def mk_pullback(up, nb):
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); out = []
        for i in range(nb + 2, len(sl) - 1):
            if up and all(hi[i-1-k] < hi[i-2-k] and lo[i-1-k] < lo[i-2-k] for k in range(nb-1)) and cl[i] > hi[i-1]: out.append((i, "long", lo[i]-0.1*atr[i]))
            elif (not up) and all(hi[i-1-k] > hi[i-2-k] and lo[i-1-k] > lo[i-2-k] for k in range(nb-1)) and cl[i] < lo[i-1]: out.append((i, "short", hi[i]+0.1*atr[i]))
        return out
    return g
def mk_breakout(up, lb, accept, retest):
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); H = rmax(hi, lb); L = rmin(lo, lb); out = []
        for i in range(lb+2, len(sl)-2):
            brk = (cl[i] > H[i]) if up else (cl[i] < L[i])
            if not brk or not np.isfinite(H[i] if up else L[i]): continue
            lvl = L[i] if up else H[i]; blvl = H[i] if up else L[i]
            if retest:
                for t in range(i+1, min(i+6, len(sl)-1)):
                    if (up and lo[t] <= blvl <= hi[t] and cl[t] > blvl) or ((not up) and lo[t] <= blvl <= hi[t] and cl[t] < blvl): out.append((t, "long" if up else "short", blvl - (1 if up else -1)*0.3*atr[t])); break
            elif accept:
                if i+1 < len(sl) and ((cl[i+1] > cl[i]) if up else (cl[i+1] < cl[i])): out.append((i+1, "long" if up else "short", lvl))
            else: out.append((i, "long" if up else "short", lvl))
        return out
    return g
def mk_disp_accept(up, w, nacc):
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); out = []
        for j in range(2, len(sl)-nacc-2):
            if atr[j] != atr[j] or abs(cl[j]-o[j]) < w*atr[j]: continue
            d0 = 1 if cl[j] > o[j] else -1
            if (d0 > 0) != up: continue
            if all((cl[j+1+k] > cl[j]) == up for k in range(nacc)): out.append((j+nacc, "long" if up else "short", o[j] - d0*0.1*atr[j]))
        return out
    return g
def mk_compression(up):
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); ma = pd.Series(atr).rolling(30).mean().shift(1).to_numpy(); out = []
        for i in range(31, len(sl)-1):
            if atr[i] != atr[i] or not np.isfinite(ma[i]): continue
            if atr[i-1] < 0.8*ma[i] and abs(cl[i]-o[i]) > 1.0*atr[i]:
                if up and cl[i] > o[i]: out.append((i, "long", lo[i]-0.1*atr[i]))
                elif (not up) and cl[i] < o[i]: out.append((i, "short", hi[i]+0.1*atr[i]))
        return out
    return g
def mk_failed_counter(up):
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); lv = rmin(lo, 8) if up else rmax(hi, 8); out = []
        for i in range(10, len(sl)-3):
            if up and cl[i] < lv[i] and cl[i-1] >= lv[i-1]:
                for t in range(i+1, i+3):
                    if cl[t] > hi[i]: out.append((t, "long", lo[i]-0.1*atr[t])); break
            elif (not up) and cl[i] > lv[i] and cl[i-1] <= lv[i-1]:
                for t in range(i+1, i+3):
                    if cl[t] < lo[i]: out.append((t, "short", hi[i]+0.1*atr[t])); break
        return out
    return g
def mk_momentum(up, k):
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); out = []
        for i in range(k+1, len(sl)-1):
            if up and all(cl[i-x] > cl[i-x-1] for x in range(k)): out.append((i, "long", cl[i]-1.2*atr[i] if atr[i]==atr[i] else cl[i]-1))
            elif (not up) and all(cl[i-x] < cl[i-x-1] for x in range(k)): out.append((i, "short", cl[i]+1.2*atr[i] if atr[i]==atr[i] else cl[i]+1))
        return out
    return g
def mk_efficiency(up, lb):
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); net = cl - pd.Series(cl).shift(lb).to_numpy(); path = pd.Series(np.abs(np.diff(cl, prepend=cl[0]))).rolling(lb).sum().shift(1).to_numpy(); out = []
        for i in range(lb+1, len(sl)-1):
            if not np.isfinite(net[i]) or not np.isfinite(path[i]) or path[i] == 0: continue
            er = net[i]/path[i]
            if up and er > 0.4: out.append((i, "long", cl[i]-1.2*atr[i] if atr[i]==atr[i] else cl[i]-1))
            elif (not up) and er < -0.4: out.append((i, "short", cl[i]+1.2*atr[i] if atr[i]==atr[i] else cl[i]+1))
        return out
    return g
def mk_hllh(up):  # higher-low / lower-high structure continuation
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); out = []
        for i in range(4, len(sl)-1):
            if up and lo[i-1] > lo[i-2] and lo[i-2] > lo[i-3] and cl[i] > hi[i-1]: out.append((i, "long", lo[i-1]-0.1*atr[i]))
            elif (not up) and hi[i-1] < hi[i-2] and hi[i-2] < hi[i-3] and cl[i] < lo[i-1]: out.append((i, "short", hi[i-1]+0.1*atr[i]))
        return out
    return g
def mk_accel(up):
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); out = []
        for j in range(4, len(sl)-1):
            if atr[j] != atr[j] or abs(cl[j]-o[j]) < 1.2*atr[j]: continue
            d0 = 1 if cl[j] > o[j] else -1
            if (d0 > 0) != up or (hi[j-1]-lo[j-1]) > 1.0*atr[j]: continue
            out.append((j+1, "long" if up else "short", o[j]-d0*0.1*atr[j]))
        return out
    return g

REG = []
def add(hid, fam, mech, up, gen, hold=8, mins=100):
    REG.append(dict(id=hid, family=fam, mechanism=mech, up=up, gen=gen, hold=hold, mins=mins))
for up in (True, False):
    D = "LONG" if up else "SHORT"
    for nb in (2, 3): add(f"H1-A-pb{nb}-{D}", "A_pullback", f"H1 pullback depth{nb}", up, mk_pullback(up, nb), 8)
    add(f"H1-B-bo-acc-{D}", "B_breakout_accept", "H1 20-breakout + acceptance", up, mk_breakout(up, 20, True, False), 10)
    add(f"H1-B-bo-raw-{D}", "B_breakout_accept", "H1 20-breakout raw", up, mk_breakout(up, 20, False, False), 10)
    add(f"H1-C-bo-retest-{D}", "C_breakout_retest", "H1 breakout + retest", up, mk_breakout(up, 20, False, True), 10)
    for w in (1.0, 1.5): add(f"H1-D-da-w{w}-{D}", "D_disp_accept", f"H1 disp>={w}ATR + accept (NEW id)", up, mk_disp_accept(up, w, 2), 8)
    add(f"H1-E-comp-{D}", "E_compression", "H1 compression->expansion", up, mk_compression(up), 8)
    add(f"H1-F-failcnt-{D}", "F_failed_counter", "H1 failed counter-move", up, mk_failed_counter(up), 8)
    for k in (3, 4): add(f"H1-G-consec{k}-{D}", "G_momentum", f"H1 {k} consecutive closes", up, mk_momentum(up, k), 6)
    add(f"H1-G-eff-{D}", "G_momentum", "H1 path-efficiency", up, mk_efficiency(up, 8), 6)
    add(f"H1-H-hllh-{D}", "H_structure", "H1 HL/LH structure continuation", up, mk_hllh(up), 8)
    add(f"H1-L-accel-{D}", "L_acceleration", "H1 trend acceleration", up, mk_accel(up), 8)

# ── run (compare unconditional vs H4-aligned vs D1-aligned; candidate = pro-trend aligned) ───────────
records = []; survivors = {}; fam_seen = Counter(); dir_seen = Counter()
def checkpoint(tag):
    ck = dict(tag=tag, tested=len(records), survived=[r["id"] for r in records if r["status"] == "SURVIVE"],
              cost_fragile=sum(1 for r in records if r["status"] == "COST_FRAGILE"), failed=sum(1 for r in records if r["status"] == "FAIL"),
              sparse=sum(1 for r in records if r["status"] in ("EVENT_SPARSE", "INSUFFICIENT_EVIDENCE")),
              families=dict(fam_seen), LONG=dir_seen["L"], SHORT=dir_seen["S"], validation_access=0, final_holdout_access=0)
    json.dump(ck, open(os.path.join(SP, f"h1_checkpoint_{tag}.json"), "w"), indent=2, default=float)
    log(f"CHECKPOINT {tag}: tested={ck['tested']} survived={ck['survived']} cost_fragile={ck['cost_fragile']} failed={ck['failed']} sparse={ck['sparse']} L={ck['LONG']} S={ck['SHORT']}")

log(f"H1 CAMPAIGN START registry={len(REG)}")
for k, h in enumerate(REG):
    try:
        # pro-trend candidate = H4-aligned; also record unconditional + D1-aligned for gate-value analysis
        gb = M(gen_eval(h["gen"], h["hold"], "GROSS", align="h4")); bb = M(gen_eval(h["gen"], h["hold"], "BASE", align="h4")); sb = M(gen_eval(h["gen"], h["hold"], "STRESS", align="h4"))
        unc = M(gen_eval(h["gen"], h["hold"], "BASE", align=None)); d1a = M(gen_eval(h["gen"], h["hold"], "BASE", align="d1"))
        st = falsify(gb, bb, sb, h["mins"])
    except Exception as e:
        st, gb, bb, sb, unc, d1a = "RERUN_ERROR", {}, {}, {}, {}, {}; log(f"{h['id']} ERR {str(e)[:120]}")
    rec = dict(id=h["id"], family=h["family"], mechanism=h["mechanism"], direction=("LONG" if h["up"] else "SHORT"),
               GROSS_h4=gb, BASE_h4=bb, STRESS_h4=sb, BASE_unconditional=unc, BASE_d1aligned=d1a, status=st, min_sample=h["mins"],
               gate_value_h4=("h4_helps" if (bb.get("avg_R") or -9) > (unc.get("avg_R") or -9) else "h4_neutral_or_hurts"))
    records.append(rec); fam_seen[h["family"]] += 1; dir_seen["L" if h["up"] else "S"] += 1
    if st == "SURVIVE": survivors[h["id"]] = rec
    log(f"{h['id']} [{h['family']}] {rec['direction']}: n={bb.get('n')} G={gb.get('avg_R')} B={bb.get('avg_R')} S={sb.get('avg_R')} (unc {unc.get('avg_R')}) best1_rem={bb.get('best1_rem')} pb={bb.get('per_block')} -> {st}")
    if (k+1) % 25 == 0: checkpoint(f"at{k+1}")
checkpoint("final")
json.dump(dict(population=POP, records=records, survivors=list(survivors)), open(os.path.join(SP, "h1_records.json"), "w"), indent=1, default=float)
log(f"H1_CAMPAIGN_COMPLETE tested={len(records)} survivors={list(survivors)}")

"""INTERIM ECONOMIC-PROFILE CAMPAIGN (CEO directive, option C).
Edge sources M15 / H1 / H4 (gated DEV, per-block). Continuation families, both directions, HTF-aligned.
Entry = next-edge-bar open (M5 PROXY -> M5-execution-quality flagged PENDING_M5). Structural SL.
Exit = RR-target k in {1.5,2 (Profile A), 3,4 (Profile B)} via mstrat.simulate (conservative intrabar
stop-wins-ties => WR/expectancy are a LOWER bound a true M5 layer would improve).
Full mandated per-candidate reporting. Cost RATIFIED BASE 0.05 / STRESS 0.24. VALIDATION untouched."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict
WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b"
if os.path.join(WP5B, "code") not in sys.path: sys.path.insert(0, os.path.join(WP5B, "code"))
import mstrat
SP = os.path.dirname(os.path.abspath(__file__)); TICK = mstrat.TICK; MKT = os.path.join(WP5B, "data", "market")
PIP = 0.10
def log(m): print(f"[{int(time.time())}] {m}", flush=True); open(os.path.join(SP, "econ.log"), "a").write(f"{int(time.time())} {m}\n")
BLOCKS = {"b0": (1311697800, 1380300300), "b1": (1452502800, 1523015550), "calib": (1597128300, 1630844100)}
DEVB = ("b0", "b1")
CM = json.load(open(r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"))
RT = {"GROSS": 0.0, "BASE": CM["base_ratified"]["round_trip_total"], "STRESS": CM["stress_ratified"]["round_trip_total"]}

def load_tf(kind):
    if kind == "M15":
        d = mstrat.load()[["time", "open", "high", "low", "close", "m_atr"]].copy()
    else:
        f = {"H1": "OANDA_XAUUSD_H1_from_M15_v2.csv", "H4": "OANDA_XAUUSD_H4_from_M15_v2.csv"}[kind]
        d = pd.read_csv(os.path.join(MKT, f))
        tr = np.maximum(d["high"] - d["low"], np.maximum((d["high"] - d["close"].shift(1)).abs(), (d["low"] - d["close"].shift(1)).abs()))
        d["m_atr"] = tr.rolling(14).mean()
    d = d.sort_values("time").reset_index(drop=True)
    coarser = {"M15": "OANDA_XAUUSD_H4_from_M15_v2.csv", "H1": "OANDA_XAUUSD_H4_from_M15_v2.csv", "H4": "OANDA_XAUUSD_D1_from_M15_v2.csv"}[kind]
    x = pd.read_csv(os.path.join(MKT, coarser)).sort_values("time")
    e20 = x["close"].ewm(span=20, adjust=True).mean(); e50 = x["close"].ewm(span=50, adjust=True).mean()
    x["trend_up"] = (e20 > e50).astype(float)
    d = pd.merge_asof(d, x[["time", "trend_up"]].rename(columns={"time": "av"}), left_on="time", right_on="av", direction="backward").drop(columns="av")
    return d

def slices(kind):
    d = load_tf(kind); t = d["time"].astype("int64").to_numpy(); out = {}
    for bn, (s, e) in BLOCKS.items(): out[bn] = d[(t >= s) & (t <= e)].reset_index(drop=True)
    return out
def rmax(a, w): return pd.Series(a).rolling(w).max().shift(1).to_numpy()
def rmin(a, w): return pd.Series(a).rolling(w).min().shift(1).to_numpy()
def _arr(sl): return sl["open"].to_numpy(), sl["high"].to_numpy(), sl["low"].to_numpy(), sl["close"].to_numpy(), sl["m_atr"].to_numpy()

# ── generator library (returns (i, side, raw_break_level)) ──
def mk_pullback(up, nb):
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); out = []
        for i in range(nb + 2, len(sl) - 1):
            if up and all(hi[i-1-k] < hi[i-2-k] and lo[i-1-k] < lo[i-2-k] for k in range(nb-1)) and cl[i] > hi[i-1]: out.append((i, "long", hi[i-1]))
            elif (not up) and all(hi[i-1-k] > hi[i-2-k] and lo[i-1-k] > lo[i-2-k] for k in range(nb-1)) and cl[i] < lo[i-1]: out.append((i, "short", lo[i-1]))
        return out
    return g
def mk_breakout(up, lb, accept):
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); H = rmax(hi, lb); L = rmin(lo, lb); out = []
        for i in range(lb+2, len(sl)-2):
            brk = (cl[i] > H[i]) if up else (cl[i] < L[i]); lvl = H[i] if up else L[i]
            if not brk or not np.isfinite(lvl): continue
            if accept:
                if i+1 < len(sl) and ((cl[i+1] > cl[i]) if up else (cl[i+1] < cl[i])): out.append((i+1, "long" if up else "short", lvl))
            else: out.append((i, "long" if up else "short", lvl))
        return out
    return g
def mk_disp_accept(up, w):
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); out = []
        for j in range(2, len(sl)-4):
            if atr[j] != atr[j] or abs(cl[j]-o[j]) < w*atr[j]: continue
            d0 = 1 if cl[j] > o[j] else -1
            if (d0 > 0) != up: continue
            if all((cl[j+1+k] > cl[j]) == up for k in range(2)): out.append((j+2, "long" if up else "short", o[j]))
        return out
    return g
def mk_compression(up):
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); ma = pd.Series(atr).rolling(30).mean().shift(1).to_numpy(); out = []
        for i in range(31, len(sl)-1):
            if atr[i] != atr[i] or not np.isfinite(ma[i]): continue
            if atr[i-1] < 0.8*ma[i] and abs(cl[i]-o[i]) > 1.0*atr[i]:
                if up and cl[i] > o[i]: out.append((i, "long", lo[i]))
                elif (not up) and cl[i] < o[i]: out.append((i, "short", hi[i]))
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
def mk_hllh(up):
    def g(sl):
        o, hi, lo, cl, atr = _arr(sl); out = []
        for i in range(4, len(sl)-1):
            if up and lo[i-1] > lo[i-2] > lo[i-3] and cl[i] > hi[i-1]: out.append((i, "long", lo[i-1]))
            elif (not up) and hi[i-1] < hi[i-2] < hi[i-3] and cl[i] < lo[i-1]: out.append((i, "short", hi[i-1]))
        return out
    return g

def mechs():
    M = []
    for up in (True, False):
        d = "L" if up else "S"
        M.append((f"pb2-{d}", "pullback", up, mk_pullback(up, 2)))
        M.append((f"bo-acc-{d}", "breakout_accept", up, mk_breakout(up, 20, True)))
        M.append((f"bo-raw-{d}", "breakout_raw", up, mk_breakout(up, 20, False)))
        M.append((f"da-{d}", "disp_accept", up, mk_disp_accept(up, 1.0)))
        M.append((f"comp-{d}", "compression", up, mk_compression(up)))
        M.append((f"mom3-{d}", "momentum", up, mk_momentum(up, 3)))
        M.append((f"eff-{d}", "efficiency", up, mk_efficiency(up, 8)))
        M.append((f"hllh-{d}", "structure", up, mk_hllh(up)))
    return M

def build_signals(SL, gen, up):
    """returns list of dict(block,ei_idx,entry,sl_usd,mfe,mae,tp_would_pips_by_rr...) per DEV signal + structural SL."""
    sig = []
    for bn in DEVB:
        sl = SL[bn]; o, hi, lo, cl, atr = _arr(sl); tu = sl["trend_up"].to_numpy(); nb = len(sl)
        HOR = 48
        for (i, side, brk) in gen(sl):
            if not (0 < i < nb-1): continue
            if not ((tu[i] > 0.5) if up else (tu[i] <= 0.5)): continue
            ei = i + 1
            if ei >= nb-1: continue
            entry = o[ei]
            if atr[i] != atr[i]: continue
            sl_usd = max(abs(entry - brk) + 0.3*atr[i], 0.8*atr[i])
            if not (sl_usd > 0): continue
            j0 = ei+1; j1 = min(j0+HOR, nb)
            if j1 <= j0: continue
            fh = hi[j0:j1]; fl = lo[j0:j1]
            mfe = float(fh.max()-entry) if up else float(entry-fl.min()); mae = float(entry-fl.min()) if up else float(fh.max()-entry)
            sig.append(dict(block=bn, si=i, ei=ei, entry=entry, sl_usd=sl_usd, mfe=mfe, mae=mae, dir=1 if up else -1))
    return sig

def realized(SL, sig, k, scen):
    """run mstrat rr-exit at target k*risk. returns per-trade R + block."""
    cfg = dict(mstrat.CFG); cfg["spread_ticks"] = 0.0; cfg["slip_ticks"] = RT[scen]/(2*TICK)
    out = []
    for bn in DEVB:
        sl = SL[bn]; setups = []
        for s in sig:
            if s["block"] != bn: continue
            stop = s["entry"] - s["dir"]*s["sl_usd"]
            setups.append(dict(si=s["si"], ei=s["ei"], dir=s["dir"], stop=float(stop), exit_kind="rr", exit_param=float(k)))
        led = mstrat.simulate(sl, setups, cfg)
        for r, si in zip(led["R"], led["si"]): out.append(dict(r=float(r), block=bn, si=int(si)))
    return out

def report_candidate(kind, name, fam, up, SL, sig, k):
    if len(sig) < 60: return None
    g = realized(SL, sig, k, "GROSS"); b = realized(SL, sig, k, "BASE"); s = realized(SL, sig, k, "STRESS")
    if not s: return None
    rg = np.array([x["r"] for x in g]); rb = np.array([x["r"] for x in b]); rs = np.array([x["r"] for x in s])
    n = len(rs)
    wr = float((rg >= k-0.05).mean())  # gross reached target => win
    # SL/TP economics from the signals that produced trades (approx: all sig)
    sl_usd = np.array([x["sl_usd"] for x in sig]); tp_usd = k*sl_usd
    sl_pips = sl_usd/PIP; tp_pips = tp_usd/PIP
    mfe = np.array([x["mfe"] for x in sig]); mae = np.array([x["mae"] for x in sig])
    rss = np.sort(rs)[::-1]; best1 = float(rss[max(1,int(n*0.01)):].mean())
    byb = defaultdict(list)
    for x in s: byb[x["block"]].append(x["r"])
    pb = {bn: round(float(np.mean(v)), 4) for bn, v in byb.items()}
    dev_bars = sum(len(SL[bn]) for bn in DEVB)
    prof = "A" if k <= 2.0 else "B"
    fit = ((prof=="A" and wr>=0.62) or (prof=="B" and wr>=0.40)) and float(rs.mean())>0 and best1>0 and (min(pb.values()) if pb else -9)>0 and float(np.median(tp_pips))>=70
    return dict(id=f"{kind}-{name}-rr{k}", edge_tf=kind, entry_tf="M5_PROXY(next-bar-open)_PENDING_M5", family=fam,
                direction="LONG" if up else "SHORT", intended_RR=f"1:{k}", profile_target=prof,
                n=n, win_rate=round(wr,3), avg_realized_R=round(float(rs.mean()),4), median_realized_R=round(float(np.median(rs)),4),
                median_SL_usd=round(float(np.median(sl_usd)),2), median_SL_pips=round(float(np.median(sl_pips)),1),
                median_TP_usd=round(float(np.median(tp_usd)),2), median_TP_pips=round(float(np.median(tp_pips)),1),
                TP_pips_P25=round(float(np.percentile(tp_pips,25)),1), TP_pips_P50=round(float(np.median(tp_pips)),1), TP_pips_P75=round(float(np.percentile(tp_pips,75)),1),
                pct_TP_ge70=round(float((tp_pips>=70).mean()),3), pct_TP_ge80=round(float((tp_pips>=80).mean()),3), pct_TP_ge100=round(float((tp_pips>=100).mean()),3),
                MFE_pips_P50=round(float(np.median(mfe)/PIP),1), MFE_pips_P75=round(float(np.percentile(mfe,75)/PIP),1),
                MAE_pips_P50=round(float(np.median(mae)/PIP),1), MAE_pips_P75=round(float(np.percentile(mae,75)/PIP),1),
                BASE_expectancy=round(float(rb.mean()),4), STRESS_expectancy=round(float(rs.mean()),4), best1pct_removed=round(best1,4),
                temporal_pb=pb, trade_freq_per1k=round(1000.0*n/dev_bars,2), profile_fit=bool(fit))

records = []
for kind in ("M15", "H1", "H4"):
    SL = slices(kind); log(f"{kind} loaded b0={len(SL['b0'])} b1={len(SL['b1'])}")
    for name, fam, up, gen in mechs():
        sig = build_signals(SL, gen, up)
        for k in (1.5, 2.0, 3.0, 4.0):
            rec = report_candidate(kind, name, fam, up, SL, sig, k)
            if rec:
                records.append(rec)
                tag = "  ***FIT***" if rec["profile_fit"] else ""
                log(f"{rec['id']} {rec['direction']} n={rec['n']} WR={rec['win_rate']} avgR={rec['avg_realized_R']} STRESS={rec['STRESS_expectancy']} b1rem={rec['best1pct_removed']} medTP={rec['median_TP_pips']}p pb={rec['temporal_pb']} P{rec['profile_target']}{tag}")
fits = [r for r in records if r["profile_fit"]]
json.dump(dict(records=records, fits=[r["id"] for r in fits]), open(os.path.join(SP, "econ_campaign.json"), "w"), indent=1, default=float)
log(f"ECON_CAMPAIGN_COMPLETE tested={len(records)} profile_fits={len(fits)}: {[r['id'] for r in fits]}")

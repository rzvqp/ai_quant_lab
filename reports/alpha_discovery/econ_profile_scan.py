"""ALPHA ECONOMIC-PROFILE FEASIBILITY SCAN (CEO directive 2026-08-21).
On the MANIFEST-GATED DEVELOPMENT population (per-block, no cross-gap), for each EDGE timeframe
M15 / H1 / H4, characterize the ECONOMIC profile of a canonical robust continuation entry:
target-size distribution (project pips, 10 pips = $1), % opportunities >=70/80/100 pips, structural SL
economics, MAE/MFE, and whether Profile A (WR ~70-80% @ RR 1:1.5-2) or Profile B (WR ~50% @ RR 1:3-4)
is naturally achievable. NO M5 layer (M5 has ZERO DEV coverage -> reported separately as a blocker).
Cost RATIFIED BASE 0.05 / STRESS 0.24. VALIDATION/SEALED untouched."""
import sys, os, json
import numpy as np, pandas as pd
WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b"
if os.path.join(WP5B, "code") not in sys.path: sys.path.insert(0, os.path.join(WP5B, "code"))
import mstrat
TICK = mstrat.TICK; MKT = os.path.join(WP5B, "data", "market")
PIP = 0.10  # 10 project pips = $1.00  => 1 project pip = $0.10
BLOCKS = {"b0": (1311697800, 1380300300), "b1": (1452502800, 1523015550), "calib": (1597128300, 1630844100)}
DEVB = ("b0", "b1")
CM = json.load(open(r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"))
RT = {"GROSS": 0.0, "BASE": CM["base_ratified"]["round_trip_total"], "STRESS": CM["stress_ratified"]["round_trip_total"]}

def load_tf(kind):
    """kind in {M15,H1,H4}. Returns df with time/o/h/l/c + m_atr + HTF-align trend (h4_up for M15/H1, d1_up for H4)."""
    if kind == "M15":
        d = mstrat.load()[["time", "open", "high", "low", "close", "m_atr"]].copy()
    else:
        f = {"H1": "OANDA_XAUUSD_H1_from_M15_v2.csv", "H4": "OANDA_XAUUSD_H4_from_M15_v2.csv"}[kind]
        d = pd.read_csv(os.path.join(MKT, f))
        tr = np.maximum(d["high"] - d["low"], np.maximum((d["high"] - d["close"].shift(1)).abs(), (d["low"] - d["close"].shift(1)).abs()))
        d["m_atr"] = tr.rolling(14).mean()
    d = d.sort_values("time").reset_index(drop=True)
    # align trend from the next-coarser TF
    coarser = {"M15": "OANDA_XAUUSD_H4_from_M15_v2.csv", "H1": "OANDA_XAUUSD_H4_from_M15_v2.csv", "H4": "OANDA_XAUUSD_D1_from_M15_v2.csv"}[kind]
    x = pd.read_csv(os.path.join(MKT, coarser)).sort_values("time")
    e20 = x["close"].ewm(span=20, adjust=True).mean(); e50 = x["close"].ewm(span=50, adjust=True).mean()
    x["trend_up"] = (e20 > e50).astype(float)
    d = pd.merge_asof(d, x[["time", "trend_up"]].rename(columns={"time": "av"}), left_on="time", right_on="av", direction="backward").drop(columns="av")
    return d

def rmax(a, w): return pd.Series(a).rolling(w).max().shift(1).to_numpy()
def rmin(a, w): return pd.Series(a).rolling(w).min().shift(1).to_numpy()

def scan(kind, horizon_bars):
    d = load_tf(kind); t = d["time"].astype("int64").to_numpy()
    rows = []
    for bn in DEVB:
        s, e = BLOCKS[bn]; sl = d[(t >= s) & (t <= e)].reset_index(drop=True)
        o = sl["open"].to_numpy(); hi = sl["high"].to_numpy(); lo = sl["low"].to_numpy(); cl = sl["close"].to_numpy()
        atr = sl["m_atr"].to_numpy(); tu = sl["trend_up"].to_numpy(); nb = len(sl)
        H = rmax(hi, 20); L = rmin(lo, 20)
        for i in range(22, nb - 2):
            for up in (True, False):
                brk = (cl[i] > H[i]) if up else (cl[i] < L[i])
                lvl = H[i] if up else L[i]
                if not brk or not np.isfinite(lvl): continue
                if i + 1 >= nb or not ((cl[i + 1] > cl[i]) if up else (cl[i + 1] < cl[i])): continue  # acceptance
                if not ((tu[i] > 0.5) if up else (tu[i] <= 0.5)): continue  # HTF pro-trend align
                ei = i + 1; entry = o[min(ei + 1, nb - 1)] if ei + 1 < nb else o[ei]
                # structural SL = REASONABLE risk unit: broken level +/- 0.3 ATR buffer (tight, like the H1 winner),
                # floored to a sane structural distance; NOT the far 20-bar opposite extreme.
                if atr[i] != atr[i]: continue
                brk_lvl = H[i] if up else L[i]
                sl_usd = max(abs(entry - brk_lvl) + 0.3 * atr[i], 0.8 * atr[i])
                if not (sl_usd > 0): continue
                # forward MFE / MAE over horizon (USD)
                j0 = ei + 1; j1 = min(j0 + horizon_bars, nb)
                if j1 <= j0: continue
                fh = hi[j0:j1]; fl = lo[j0:j1]
                if up: mfe = float(fh.max() - entry); mae = float(entry - fl.min())
                else:  mfe = float(entry - fl.min()); mae = float(fh.max() - entry)
                rows.append(dict(block=bn, up=up, entry=entry, sl_usd=sl_usd, mfe=mfe, mae=mae))
    return pd.DataFrame(rows)

def pips(x): return x / PIP  # USD -> project pips

def profile_tests(df, kind):
    """TARGET-anchored: structural SL (from scan) + economic TP in {70,80,100} project pips.
    RR = TP/SL falls out of the timeframe's ATR. WR from MFE/MAE excursions with an explicit
    path-ambiguity RANGE (pess=ambiguous->loss, opt=ambiguous->win). Expectancy in R (per SL), net of cost.
    Uses the pessimistic (ambiguous=loss) accounting for expectancy (conservative)."""
    out = {}
    sl = df["sl_usd"].to_numpy(); mfe = df["mfe"].to_numpy(); mae = df["mae"].to_numpy(); n = len(df)
    for tp_pips in (70, 80, 100):
        tp = tp_pips * PIP
        rr = tp / sl  # per-trade RR
        hit_tp = mfe >= tp; hit_sl = mae >= sl
        win = hit_tp & ~hit_sl; loss = hit_sl & ~hit_tp; ambig = hit_tp & hit_sl; none = ~hit_tp & ~hit_sl
        wr_pess = float(win.sum()) / n; wr_opt = float((win.sum() + ambig.sum())) / n
        # expectancy (R units, pessimistic: ambiguous->loss; none->time-exit at MFE-capped, floored at -? -> 0 approx)
        res = np.where(win, rr, np.where(loss | ambig, -1.0, np.minimum(mfe, tp) / sl))
        cost_b = RT["BASE"] / sl; cost_s = RT["STRESS"] / sl
        rb = res - cost_b; rs = res - cost_s
        b1 = np.sort(rb)[::-1]; best1 = float(b1[max(1, int(len(b1) * 0.01)):].mean()) if len(b1) else 0
        out[f"TP{tp_pips}p"] = dict(median_RR=round(float(np.median(rr)), 2), WR_pess=round(wr_pess, 3), WR_opt=round(wr_opt, 3),
                                    BASE_exp=round(float(rb.mean()), 4), STRESS_exp=round(float(rs.mean()), 4), best1rem=round(best1, 4),
                                    n_win=int(win.sum()), n_loss=int(loss.sum()), n_ambig=int(ambig.sum()), n_none=int(none.sum()))
    return out

HOR = {"M15": 96, "H1": 24, "H4": 6}  # ~24h forward horizon each
report = {}
for kind in ("M15", "H1", "H4"):
    df = scan(kind, HOR[kind])
    if df.empty: report[kind] = dict(n=0); continue
    mfe_p = pips(df["mfe"]); sl_p = pips(df["sl_usd"]); mae_p = pips(df["mae"])
    econ = dict(
        n=len(df), n_long=int(df["up"].sum()), n_short=int((~df["up"]).sum()),
        horizon_bars=HOR[kind],
        median_SL_usd=round(float(df["sl_usd"].median()), 2), median_SL_pips=round(float(sl_p.median()), 1),
        MFE_pips_P25=round(float(mfe_p.quantile(.25)), 1), MFE_pips_P50=round(float(mfe_p.median()), 1), MFE_pips_P75=round(float(mfe_p.quantile(.75)), 1),
        MAE_pips_P50=round(float(mae_p.median()), 1), MAE_pips_P75=round(float(mae_p.quantile(.75)), 1),
        pct_MFE_ge70=round(float((mfe_p >= 70).mean()), 3), pct_MFE_ge80=round(float((mfe_p >= 80).mean()), 3), pct_MFE_ge100=round(float((mfe_p >= 100).mean()), 3),
        profiles=profile_tests(df, kind))
    report[kind] = econ
    print(f"\n=== {kind} EDGE (20-breakout+accept, HTF-aligned, gated DEV, ~24h fwd) ===")
    print(f"  n={econ['n']} (L{econ['n_long']}/S{econ['n_short']})  median SL=${econ['median_SL_usd']} ({econ['median_SL_pips']} pips)")
    print(f"  MFE pips P25/P50/P75 = {econ['MFE_pips_P25']}/{econ['MFE_pips_P50']}/{econ['MFE_pips_P75']}   MAE pips P50/P75={econ['MAE_pips_P50']}/{econ['MAE_pips_P75']}")
    print(f"  %MFE >=70={econ['pct_MFE_ge70']}  >=80={econ['pct_MFE_ge80']}  >=100={econ['pct_MFE_ge100']}")
    for tp, v in econ["profiles"].items():
        print(f"  {tp}: medRR=1:{v['median_RR']} WR={v['WR_pess']}-{v['WR_opt']} BASE_exp={v['BASE_exp']} STRESS_exp={v['STRESS_exp']} best1rem={v['best1rem']} (W{v['n_win']}/L{v['n_loss']}/amb{v['n_ambig']}/none{v['n_none']})")
json.dump(report, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "econ_profile_scan.json"), "w"), indent=1, default=float)
print("\nsaved econ_profile_scan.json")

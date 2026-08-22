"""swing_base.py — shared SWING-horizon research harness for ALPHA-XAUUSD-CONTINUOUS-RESEARCH-LOOP-001.

Firewall: consumes ONLY the gated M5 via m5_data (edge_research._common.load); NO read_csv on data/market.
Builds M15/H1/H4/D1 by CAUSAL aggregation (reuses m5_data's ratified feature/regime functions).
DEV 2021-07-27->2023-12-29 for selection; CALIB 2024-01->2024-06-20 for out-of-selection robustness only.
Price-only. No N4/V1/2025+/protected-2024/exogenous. Cost: TICK 0.01, BASE RT 0.05, STRESS RT 0.24 USD.

Conventions (match frozen candidates, conservative):
- Entry = NEXT signal-TF bar OPEN (no same-bar fill).
- Structural stop owned by the signal TF; target = RR * risk OR structural/horizon exit.
- Intrabar: STOP WINS same-bar ties (lower-bound WR/expectancy).
- R = (net USD PnL) / risk_usd, risk_usd = |entry - stop|. Cost applied once per round trip in USD.
- Project pip = 0.10 USD (10 pips = $1). pips = usd * 10.
"""
import sys, os
import numpy as np, pandas as pd
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path: sys.path.insert(0, _HERE)
import m5_data

TICK = 0.01
COST = {"GROSS": 0.00, "BASE": 0.05, "STRESS": 0.24}  # round-trip USD
PIP = 0.10  # 1 project pip = 0.10 USD
CACHE = os.path.join(_HERE, "__swing_cache__")

# ---------------- frame construction (adds D1 to the ratified M5/M15/H1/H4 set) ----------------
def _agg_d1(m5):
    """Causal daily aggregation with the same convention as m5_data.aggregate (bucket start epoch = time,
    last M5 epoch = close_time). Keep days with >= 100 M5 sub-bars (drop thin holiday/half sessions)."""
    g = m5.assign(bucket=m5["dt"].dt.floor("1D")).groupby("bucket")
    agg = g.agg(open=("open","first"), high=("high","max"), low=("low","min"), close=("close","last"),
                volume=("volume","sum"), nsub=("open","size"), open_time=("time","first"),
                close_time=("time","last")).reset_index()
    agg = agg[agg["nsub"] >= 100].reset_index(drop=True)
    agg["dt"] = agg["bucket"]; agg["time"] = agg["open_time"].astype("int64")
    return agg[["time","dt","open","high","low","close","volume","nsub","close_time"]]

def build_frames(use_cache=True):
    if use_cache and os.path.isdir(CACHE) and os.path.exists(os.path.join(CACHE,"H4.parquet")):
        tfs = {tf: pd.read_parquet(os.path.join(CACHE, f"{tf}.parquet")) for tf in ("M15","H1","H4","D1")}
        return tfs
    m5, meta = m5_data.load_m5()
    tfs = {}
    for tf in ("M15","H1","H4"):
        x = m5_data.aggregate(m5, tf); x = m5_data.add_features(x)
        if tf in ("H1","H4"): x = m5_data.regime_label(x)
        x["is_dev"] = x["dt"] <= m5_data.DEV_END
        x["is_cal"] = (x["dt"] >= m5_data.CAL_START) & (x["dt"] <= m5_data.CAL_END)
        tfs[tf] = x.reset_index(drop=True)
    d1 = _agg_d1(m5); d1 = m5_data.add_features(d1); d1 = m5_data.regime_label(d1)
    d1["is_dev"] = d1["dt"] <= m5_data.DEV_END
    d1["is_cal"] = (d1["dt"] >= m5_data.CAL_START) & (d1["dt"] <= m5_data.CAL_END)
    tfs["D1"] = d1.reset_index(drop=True)
    os.makedirs(CACHE, exist_ok=True)
    for tf, x in tfs.items(): x.to_parquet(os.path.join(CACHE, f"{tf}.parquet"))
    # leak assertions
    for tf, x in tfs.items():
        assert (x["dt"] < pd.Timestamp("2025-01-01", tz="UTC")).all(), f"{tf} LEAK 2025+"
    return tfs

# ---------------- causal cross-TF alignment ----------------
def align_context(low, high, cols, suffix):
    """Attach higher-TF cols to lower-TF rows using the LAST COMPLETED higher bar
    (higher.close_time <= low.time). No partial-HTF leakage."""
    lo = low.sort_values("time").reset_index(drop=True)
    hi = high.sort_values("close_time").reset_index(drop=True)
    idx = np.searchsorted(hi["close_time"].to_numpy(), lo["time"].to_numpy(), side="right") - 1
    out = lo.copy()
    for c in cols:
        vals = np.full(len(lo), np.nan, dtype=float) if np.issubdtype(hi[c].dtype, np.number) else np.full(len(lo), None, dtype=object)
        ok = idx >= 0
        vals[ok] = hi[c].to_numpy()[idx[ok]]
        out[c + suffix] = vals
    out["_hidx"] = idx
    return out

# ---------------- conservative swing simulator ----------------
def simulate(df, sig_idx, side, sl_usd, rr, horizon, scenario="STRESS"):
    """df: signal-TF frame (sorted, reset). sig_idx: array of signal bar positions (entry = open[i+1]).
    side: +1 long / -1 short. sl_usd: per-signal structural risk (array or scalar). rr: target multiple.
    horizon: max bars held after entry. Returns trades DataFrame with net R (given scenario) + gross R + MFE/MAE R."""
    o = df["open"].to_numpy(); h = df["high"].to_numpy(); l = df["low"].to_numpy()
    n = len(df); cost = COST[scenario]
    sl_arr = np.full(len(sig_idx), sl_usd, float) if np.isscalar(sl_usd) else np.asarray(sl_usd, float)
    rows = []
    for k, i in enumerate(sig_idx):
        ei = i + 1
        if ei >= n: continue
        risk = sl_arr[k]
        if not np.isfinite(risk) or risk <= 0: continue
        entry = o[ei]
        if side > 0:
            stop = entry - risk; targ = entry + rr * risk
        else:
            stop = entry + risk; targ = entry - rr * risk
        exit_px = None; exit_reason = "horizon"; exit_j = min(ei + horizon, n - 1)
        mfe = 0.0; mae = 0.0
        for j in range(ei, min(ei + horizon + 1, n)):
            hi_j, lo_j = h[j], l[j]
            fav = (hi_j - entry) if side > 0 else (entry - lo_j)
            adv = (entry - lo_j) if side > 0 else (hi_j - entry)
            if fav > mfe: mfe = fav
            if adv > mae: mae = adv
            hit_stop = (lo_j <= stop) if side > 0 else (hi_j >= stop)
            hit_targ = (hi_j >= targ) if side > 0 else (lo_j <= targ)
            if hit_stop:  # stop wins same-bar ties
                exit_px = stop; exit_reason = "stop"; exit_j = j; break
            if hit_targ:
                exit_px = targ; exit_reason = "target"; exit_j = j; break
        if exit_px is None:
            exit_px = df["close"].to_numpy()[exit_j]; exit_reason = "horizon"
        gross_usd = side * (exit_px - entry)
        net_usd = gross_usd - cost
        rows.append(dict(k=k, i=int(i), ei=int(ei), t_entry=int(df["time"].to_numpy()[ei]),
                         side=side, entry=entry, stop=stop, targ=targ, risk=risk,
                         exit_px=exit_px, exit_j=int(exit_j), exit_reason=exit_reason,
                         hold=int(exit_j - ei),
                         gross_R=gross_usd / risk, R=net_usd / risk,
                         mfe_R=mfe / risk, mae_R=mae / risk,
                         sl_pips=risk / PIP, tp_pips=rr * risk / PIP))
    return pd.DataFrame(rows)

def dedup_events(sig_idx, cooldown):
    """One opportunity per cooldown window (event-level dedup, no re-entry spam)."""
    out = []; last = -10**9
    for i in sorted(sig_idx):
        if i - last >= cooldown:
            out.append(i); last = i
    return np.array(out, dtype=int)

# ---------------- metrics ----------------
def _pf(r):
    g = r[r > 0].sum(); b = -r[r < 0].sum()
    return (g / b) if b > 0 else np.inf

def _maxdd(r):
    eq = np.cumsum(r); peak = np.maximum.accumulate(eq); return float((eq - peak).min())

def _best_removed(r, frac):
    if len(r) == 0: return np.nan
    k = int(np.ceil(len(r) * frac)); k = min(k, len(r) - 1) if len(r) > 1 else 0
    return float(np.sort(r)[:len(r) - k].mean()) if len(r) - k > 0 else np.nan

def metrics(tr, df, rr):
    """Full battery on a trades frame. df supplies year via t_entry."""
    if len(tr) == 0:
        return dict(N=0)
    r = tr["R"].to_numpy(); rg = tr["gross_R"].to_numpy()
    yrs = pd.to_datetime(tr["t_entry"], unit="s", utc=True).dt.year.to_numpy()
    per_year = {int(y): (float(r[yrs == y].mean()), int((yrs == y).sum())) for y in np.unique(yrs)}
    months = pd.to_datetime(tr["t_entry"], unit="s", utc=True).dt.to_period("M").nunique()
    m = dict(
        N=len(tr),
        WR_target=float((r >= rr - 0.05).mean()),
        WR_pos=float((r > 0).mean()),
        avgR=float(r.mean()), avgR_gross=float(rg.mean()), medR=float(np.median(r)),
        PF=float(_pf(r)), maxDD_R=_maxdd(r), maxloss_R=float(r.min()),
        best1=_best_removed(r, 0.01), best5=_best_removed(r, 0.05), best10=_best_removed(r, 0.10),
        adverse_first=float((tr["mae_R"].to_numpy() >= 1.0).mean()),  # hit full risk adverse at some point
        med_sl_pips=float(tr["sl_pips"].median()), med_tp_pips=float(tr["tp_pips"].median()),
        med_mfe_R=float(tr["mfe_R"].median()), med_hold=float(tr["hold"].median()),
        trades_per_month=len(tr) / max(months, 1),
        per_year=per_year,
    )
    return m

def disc_conf(tr, df, rr, split_frac=0.6):
    """Chronological DISC/CONF split by entry time (no shuffle)."""
    if len(tr) < 10: return None
    t = tr.sort_values("t_entry").reset_index(drop=True)
    cut = int(len(t) * split_frac)
    d, c = t.iloc[:cut], t.iloc[cut:]
    return dict(disc_avgR=float(d["R"].mean()), disc_N=len(d),
                conf_avgR=float(c["R"].mean()), conf_N=len(c),
                split_time=int(t["t_entry"].to_numpy()[cut]))

if __name__ == "__main__":
    tfs = build_frames(use_cache=False)
    for tf, x in tfs.items():
        dev = x[x["is_dev"]]
        print(f"{tf}: total={len(x)} DEV={len(dev)} range={x['dt'].min()}..{x['dt'].max()}")
        if "regime" in x:
            print("   DEV regimes:", dev["regime"].value_counts().to_dict())
    print("swing_base OK")

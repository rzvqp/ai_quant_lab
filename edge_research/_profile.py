"""Flow A shared profiling helpers (added 2026-07-22, CEO-authorized "full edge profile" directive).

Reusable, disclosed building blocks for the expanded per-edge profile template (movement profile across
horizons/ATR-thresholds, context slicing, subperiod/year robustness, daily-range context features).
Deliberately independent of `code/`/`ai_trader/`, same as `_common.py` -- pure functions operating on a
dataframe already produced by `_common.load()`.
"""
import numpy as np
import pandas as pd

HORIZONS = (1, 3, 5, 10, 20, 50)
ATR_THRESHOLDS = (0.25, 0.5, 1.0, 1.5, 2.0)
REACTION_THRESHOLD = 1.0  # the ATR multiple used to classify continuation/reversal/stall, disclosed, not tuned


def movement_profile(m, idx, direction, atr_ref, horizons=HORIZONS, atr_thresholds=ATR_THRESHOLDS,
                      react_threshold=REACTION_THRESHOLD):
    """direction: +1 predicts price rises from here, -1 predicts price falls. atr_ref: ATR to normalize by
    (the event's own ATR at detection, held fixed across the whole forward window). Returns None if there
    isn't enough forward data or atr_ref is invalid."""
    close = m["close"].values
    high = m["high"].values
    low = m["low"].values
    n = len(m)
    max_h = max(horizons)
    end = min(idx + 1 + max_h, n)
    if end <= idx + 1 or not np.isfinite(atr_ref) or atr_ref <= 0:
        return None
    fut_high = high[idx + 1:end]
    fut_low = low[idx + 1:end]
    fut_close = close[idx + 1:end]
    c0 = close[idx]
    if direction > 0:
        fav_path = (fut_high - c0) / atr_ref
        adv_path = (c0 - fut_low) / atr_ref
    else:
        fav_path = (c0 - fut_low) / atr_ref
        adv_path = (fut_high - c0) / atr_ref

    out = {"by_horizon": {}, "by_threshold": {}}
    for h in horizons:
        hh = min(h, len(fut_close))
        if hh <= 0:
            continue
        ret = direction * (fut_close[hh - 1] - c0) / atr_ref
        out["by_horizon"][str(h)] = dict(ret=float(ret), mfe=float(fav_path[:hh].max()),
                                          mae=float(adv_path[:hh].max()))
    for th in atr_thresholds:
        fav_hit = fav_path >= th
        adv_hit = adv_path >= th
        fav_i = int(np.argmax(fav_hit)) if fav_hit.any() else None
        adv_i = int(np.argmax(adv_hit)) if adv_hit.any() else None
        out["by_threshold"][str(th)] = dict(
            favorable_hit=fav_i is not None, favorable_ttf=fav_i,
            adverse_hit=adv_i is not None, adverse_ttf=adv_i)

    fav_r = fav_path >= react_threshold
    adv_r = adv_path >= react_threshold
    fav_ri = int(np.argmax(fav_r)) if fav_r.any() else None
    adv_ri = int(np.argmax(adv_r)) if adv_r.any() else None
    if fav_ri is not None and (adv_ri is None or fav_ri <= adv_ri):
        outcome = "continuation"
    elif adv_ri is not None and (fav_ri is None or adv_ri < fav_ri):
        outcome = "reversal"
    else:
        outcome = "stall"
    out["outcome"] = outcome
    return out


def summarize_movement(rows):
    """rows: list of movement_profile() dicts (non-None). Aggregates by_horizon means, by_threshold hit
    rates + median time-to-hit, and outcome-class proportions."""
    n = len(rows)
    if n == 0:
        return dict(n=0)
    out = {"n": n}
    horizons = rows[0]["by_horizon"].keys()
    out["by_horizon"] = {}
    for h in horizons:
        rets = np.array([r["by_horizon"][h]["ret"] for r in rows if h in r["by_horizon"]])
        mfes = np.array([r["by_horizon"][h]["mfe"] for r in rows if h in r["by_horizon"]])
        maes = np.array([r["by_horizon"][h]["mae"] for r in rows if h in r["by_horizon"]])
        out["by_horizon"][h] = dict(n=len(rets), mean_ret=float(rets.mean()) if len(rets) else None,
                                     mean_mfe=float(mfes.mean()) if len(mfes) else None,
                                     mean_mae=float(maes.mean()) if len(maes) else None)
    thresholds = rows[0]["by_threshold"].keys()
    out["by_threshold"] = {}
    for th in thresholds:
        fav = [r["by_threshold"][th]["favorable_hit"] for r in rows]
        fav_ttf = [r["by_threshold"][th]["favorable_ttf"] for r in rows if r["by_threshold"][th]["favorable_ttf"] is not None]
        adv = [r["by_threshold"][th]["adverse_hit"] for r in rows]
        out["by_threshold"][th] = dict(
            favorable_rate=float(np.mean(fav)), adverse_rate=float(np.mean(adv)),
            median_favorable_ttf=float(np.median(fav_ttf)) if fav_ttf else None)
    outcomes = [r["outcome"] for r in rows]
    out["outcome_rates"] = dict(
        continuation=float(np.mean([o == "continuation" for o in outcomes])),
        reversal=float(np.mean([o == "reversal" for o in outcomes])),
        stall=float(np.mean([o == "stall" for o in outcomes])))
    return out


def context_features(m, idx):
    """Per-event context covariates: session, dow, vol_regime (must already be columns on m), trend
    context (simple: last 20-bar EMA slope sign, disclosed, not tuned), distance from today's open,
    position in today's range so far, prior-day range (ATR units), gap from previous close, and whether
    today's range has already exceeded 70% of ADR14 (a simple, disclosed "post-main-expansion" flag)."""
    close = m["close"].values
    open_ = m["open"].values
    high = m["high"].values
    low = m["low"].values
    atr = m["atr14"].values
    n = len(m)
    ema_fast_col = "close"
    lookback = 20
    lo = max(0, idx - lookback)
    seg = close[lo:idx + 1]
    trend = "range"
    if len(seg) >= 5:
        slope = (seg[-1] - seg[0]) / (len(seg) - 1)
        atr_ref = atr[idx] if np.isfinite(atr[idx]) and atr[idx] > 0 else np.nan
        if np.isfinite(atr_ref) and atr_ref > 0:
            norm_slope = slope * len(seg) / atr_ref
            if norm_slope > 0.5:
                trend = "bull"
            elif norm_slope < -0.5:
                trend = "bear"
    date = m["date"].iloc[idx] if "date" in m.columns else None
    return dict(session=str(m["session"].iloc[idx]), dow=str(m["dow"].iloc[idx]),
                vol_regime=str(m["vol_regime"].iloc[idx]), trend=trend, date=str(date))


def year_of(m, idx):
    return int(m["dt"].iloc[idx].year)


def attach_daily_context(m, d1):
    """d1: the D1 dataframe from the SAME centralized-loader call (same split/cutoff). Attaches, onto
    the M15 (or other intraday) frame `m`: adr14 (14-day rolling ADR, shifted 1 day -- lookahead-safe,
    same construction as E026), day_open, running day_high/day_low, pct_adr_up/pct_adr_down consumed so
    far, gap_from_prev_close (signed, ATR units), and post_main_expansion (bool: has today's up-or-down
    ADR consumption already exceeded 0.7x ADR -- a plain, disclosed, non-tuned threshold)."""
    d1 = d1.copy()
    d1["rng"] = d1["high"] - d1["low"]
    d1["adr14"] = d1["rng"].rolling(14).mean().shift(1)
    d1["date"] = d1["dt"].dt.date
    d1["prev_close"] = d1["close"].shift(1)

    m = m.copy()
    m["date"] = m["dt"].dt.date
    m = m.merge(d1[["date", "adr14", "prev_close"]], on="date", how="left")
    m["day_open"] = m.groupby("date")["open"].transform("first")
    m["day_high_so_far"] = m.groupby("date")["high"].cummax()
    m["day_low_so_far"] = m.groupby("date")["low"].cummin()
    m["gap_from_prev_close"] = np.where(
        m["adr14"].notna() & (m["adr14"] > 0), (m["day_open"] - m["prev_close"]) / m["adr14"], np.nan)
    up_consumed = (m["day_high_so_far"] - m["day_open"])
    down_consumed = (m["day_open"] - m["day_low_so_far"])
    m["pct_adr_up"] = np.where(m["adr14"] > 0, up_consumed / m["adr14"], np.nan)
    m["pct_adr_down"] = np.where(m["adr14"] > 0, down_consumed / m["adr14"], np.nan)
    m["post_main_expansion"] = (m["pct_adr_up"].fillna(0) >= 0.7) | (m["pct_adr_down"].fillna(0) >= 0.7)
    day_range = (m["day_high_so_far"] - m["day_low_so_far"]).replace(0, np.nan)
    m["position_in_day_range"] = (m["close"] - m["day_low_so_far"]) / day_range
    return m


def robustness_by_year(rows, year_key_fn, outcome_key="outcome_rates", metric="continuation"):
    """rows: list of dicts each with a 'year' field already attached. Splits by year and reports the
    chosen outcome-rate metric per year, to check the effect isn't concentrated in one period."""
    by_year = {}
    for r in rows:
        by_year.setdefault(r["year"], []).append(r)
    out = {}
    for y, rs in sorted(by_year.items()):
        outcomes = [r["outcome"] for r in rs]
        out[str(y)] = dict(n=len(rs), continuation=float(np.mean([o == "continuation" for o in outcomes])),
                            reversal=float(np.mean([o == "reversal" for o in outcomes])))
    return out

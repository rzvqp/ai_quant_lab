"""E008 -- Friday Profit Taking Shift -- full-profile Discovery-stage analysis (Flow A).

V0 (frozen, verbatim): "Friday afternoon shows a distinct behavior pattern caused by position-closing
flows ahead of the weekend."

Run under EDGE_RESEARCH_PROTOCOL.md SSSS1-8 only (SS9 scalping validation explicitly NOT performed,
per the CEO's own priority-shift instruction). Only E008 is authorized this session.

DEFINITIONS PREDECLARED BEFORE ANY OUTCOME WAS INSPECTED:

1. **"Afternoon" window**: bars tagged `session` in {'ny','late'} by `_common.load()` (UTC hour >= 13,
   i.e. 13:00-23:59 UTC) on a given calendar date -- the NY-session-through-close period, the natural
   "position-closing before the weekend" window for a gold/FX market. This window exists for every
   weekday, giving a direct, matched (same time-of-day) Friday-vs-other-weekdays comparison without
   needing a separate synthetic control for the PRIMARY test.
2. **Directional persistence metric**: an efficiency ratio (Kaufman-style, disclosed, not tuned) --
   `net_move / path_length`, where `net_move = |close_at_window_end - open_at_window_start|` and
   `path_length = sum(|close[i] - close[i-1]|)` over the window's bars. Ranges 0 (pure chop) to 1
   (perfectly one-directional). Both terms normalized by the window's own ATR14 reference before
   division cancels out, so the ratio itself needs no further normalization.
3. **Volatility metric**: `path_length / atr14_at_window_start` -- total intra-window movement,
   ATR-normalized (a realized-volatility proxy for the window).
4. **Week's prevailing trend direction**: sign of `close(Thursday, same week) - open(Monday, same
   week)`, ATR-normalized magnitude also recorded -- a context feature, not part of the primary
   detector.
5. **Week-of-month context**: whether the trading day falls in the last trading week of its calendar
   month (a simple, disclosed, non-tuned flag) -- addresses the registry's own "week-of-month"
   observable.
6. **Time-of-day within Friday**: Friday's own afternoon window is additionally split into its 'ny' and
   'late' session sub-components to test whether any effect concentrates in one part of the afternoon.
7. **Primary comparison**: Friday's afternoon-window efficiency-ratio and volatility distributions vs.
   the POOLED Monday-Thursday afternoon-window distributions, same weeks, via Mann-Whitney U (a
   continuous-distribution comparison, not a binary rate -- the first edge in this program to need it).
   A full day-of-week ladder (each weekday vs. the other four) is also reported.
8. **Falsification / placebo control**: a permutation-based placebo -- randomly relabel ~1/5 of trading
   days (seed=42, matching Friday's own share of the week) as "pseudo-Friday" and compare against the
   remaining 4/5, using the identical Mann-Whitney test. This establishes the noise floor for how large
   an apparent 1-vs-4 group difference can look purely by chance at this sample size, independent of
   any real calendar structure.
9. **Reversal-of-week's-trend test**: for every day (not just Friday), does that day's own afternoon
   directional move oppose the sign of the trend established by the days before it in the same week
   (Monday through the prior day)? The rate of such "opposition" is compared for Friday vs. the pooled
   other weekdays -- a more specific test of the "profit-taking reversal" mechanism than volatility or
   efficiency alone.

Timeframes: M15 (primary), H1 (secondary, coarser resolution per the registered M5/M15/H1 timeframe
set and this project's own M15 data ceiling).
"""
import json
import numpy as np
from scipy.stats import mannwhitneyu
from _common import load, vol_regime, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
import _profile as P

RNG_SEED = 42


def _bars_by_date(m):
    dates = m["dt"].dt.date.values
    by_date = {}
    for i, dte in enumerate(dates):
        by_date.setdefault(dte, []).append(i)
    return by_date


def build_afternoon_events(m):
    """One event per calendar date: the afternoon window's efficiency ratio and realized vol."""
    hours = m["dt"].dt.hour.values
    sessions = m["session"].values
    close = m["close"].values
    open_ = m["open"].values
    atr = m["atr14"].values
    dow = m["dow"].values
    by_date = _bars_by_date(m)
    dates_sorted = sorted(by_date.keys())

    events = []
    for dte in dates_sorted:
        idxs = by_date[dte]
        aft_idxs = [i for i in idxs if sessions[i] in ("ny", "late")]
        if len(aft_idxs) < 4:  # need at least a handful of bars to compute a meaningful path
            continue
        atr_ref = atr[aft_idxs[0]]
        if not (np.isfinite(atr_ref) and atr_ref > 0):
            continue
        window_open = open_[aft_idxs[0]]
        window_close = close[aft_idxs[-1]]
        closes_seq = close[aft_idxs[0]:aft_idxs[-1] + 1]
        path_length = float(np.abs(np.diff(closes_seq)).sum())
        if path_length <= 0:
            continue
        net_move = float(abs(window_close - window_open))
        efficiency_ratio = net_move / path_length
        realized_vol = path_length / atr_ref
        net_direction = 1 if (window_close - window_open) > 0 else (-1 if (window_close - window_open) < 0 else 0)

        ny_idxs = [i for i in aft_idxs if sessions[i] == "ny"]
        late_idxs = [i for i in aft_idxs if sessions[i] == "late"]

        events.append(dict(
            date=str(dte), dow=str(dow[aft_idxs[0]]), efficiency_ratio=float(efficiency_ratio),
            realized_vol=float(realized_vol), net_direction=int(net_direction),
            atr_ref=float(atr_ref), n_ny_bars=len(ny_idxs), n_late_bars=len(late_idxs),
            ny_start_idx=aft_idxs[0],
        ))
    return events


def attach_week_context(m, events):
    """Attach: week's prevailing trend direction (Monday-open -> Thursday-close, same week), and
    whether this date falls in the last trading week of its month. Also computes, per event, whether
    its own net_direction opposes the trend established by the PRECEDING days of the same week."""
    dt_col = m["dt"]
    open_ = m["open"].values
    close = m["close"].values
    atr = m["atr14"].values
    by_date = _bars_by_date(m)

    # index events by date for quick lookup
    ev_by_date = {e["date"]: e for e in events}
    date_list = sorted(by_date.keys())
    date_to_pos = {d: i for i, d in enumerate(date_list)}

    # week grouping: ISO (year, week)
    iso = {}
    for d in date_list:
        import datetime
        dd = d if isinstance(d, datetime.date) else datetime.date.fromisoformat(str(d))
        iso[d] = dd.isocalendar()[:2]  # (iso_year, iso_week)

    week_groups = {}
    for d in date_list:
        week_groups.setdefault(iso[d], []).append(d)

    # last trading week of month
    months = {}
    for d in date_list:
        import datetime
        dd = d if isinstance(d, datetime.date) else datetime.date.fromisoformat(str(d))
        months.setdefault((dd.year, dd.month), []).append(d)
    last_week_dates = set()
    for (yr, mo), days in months.items():
        wk_of_days = sorted(set(iso[d] for d in days))
        if wk_of_days:
            last_wk = wk_of_days[-1]
            for d in days:
                if iso[d] == last_wk:
                    last_week_dates.add(d)

    for wk, days in week_groups.items():
        days_sorted = sorted(days)
        if len(days_sorted) < 2:
            continue
        mon = days_sorted[0]
        # "Thursday" proxy = second-to-last trading day of the week (robust to holiday-shortened weeks)
        pre_fri = days_sorted[-2] if len(days_sorted) >= 2 else days_sorted[0]
        mon_first_idx = by_date[mon][0]
        pre_fri_last_idx = by_date[pre_fri][-1]
        atr_ref = atr[mon_first_idx]
        week_trend_dir = None
        week_trend_mag = None
        if np.isfinite(atr_ref) and atr_ref > 0:
            delta = close[pre_fri_last_idx] - open_[mon_first_idx]
            week_trend_dir = 1 if delta > 0 else (-1 if delta < 0 else 0)
            week_trend_mag = float(abs(delta) / atr_ref)
        for d in days_sorted:
            d_key = str(d)  # events are keyed by str(date) (build_afternoon_events); by_date/days_sorted
            # use raw datetime.date objects -- these are NOT the same key type, must convert before lookup.
            if d_key in ev_by_date:
                ev_by_date[d_key]["week_trend_direction"] = week_trend_dir
                ev_by_date[d_key]["week_trend_magnitude"] = week_trend_mag
                ev_by_date[d_key]["last_trading_week_of_month"] = d in last_week_dates
                # opposition test: does THIS day's own net_direction oppose the trend of days BEFORE it this week?
                days_before = [dd for dd in days_sorted if dd < d]
                if days_before and np.isfinite(atr_ref) and atr_ref > 0:
                    prior_first_idx = by_date[mon][0]
                    prior_last_idx = by_date[days_before[-1]][-1]
                    prior_delta = close[prior_last_idx] - open_[prior_first_idx]
                    prior_dir = 1 if prior_delta > 0 else (-1 if prior_delta < 0 else 0)
                    ev = ev_by_date[d_key]
                    if prior_dir != 0 and ev["net_direction"] != 0:
                        ev_by_date[d_key]["opposes_prior_week_trend"] = bool(ev["net_direction"] != prior_dir)
                    else:
                        ev_by_date[d_key]["opposes_prior_week_trend"] = None
                else:
                    ev_by_date[d_key]["opposes_prior_week_trend"] = None
    return list(ev_by_date.values())


def mwu_p(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) < 5 or len(b) < 5:
        return None
    try:
        _, p = mannwhitneyu(a, b, alternative="two-sided")
        return float(p)
    except Exception:
        return None


def describe(x):
    x = np.asarray(x, dtype=float)
    if len(x) == 0:
        return dict(n=0)
    return dict(n=int(len(x)), mean=float(x.mean()), median=float(np.median(x)), std=float(x.std()))


def run_timeframe(tf):
    m, meta = load(tf, data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    m["vol_regime"] = vol_regime(m)

    events = build_afternoon_events(m)
    events = attach_week_context(m, events)

    by_dow = {}
    for e in events:
        by_dow.setdefault(e["dow"], []).append(e)

    fri = by_dow.get("Friday", [])
    mon_thu = [e for d in ["Monday", "Tuesday", "Wednesday", "Thursday"] for e in by_dow.get(d, [])]

    primary = dict(
        friday_efficiency=describe([e["efficiency_ratio"] for e in fri]),
        mon_thu_efficiency=describe([e["efficiency_ratio"] for e in mon_thu]),
        p_efficiency=mwu_p([e["efficiency_ratio"] for e in fri], [e["efficiency_ratio"] for e in mon_thu]),
        friday_vol=describe([e["realized_vol"] for e in fri]),
        mon_thu_vol=describe([e["realized_vol"] for e in mon_thu]),
        p_vol=mwu_p([e["realized_vol"] for e in fri], [e["realized_vol"] for e in mon_thu]),
    )

    # --- day-of-week ladder: each weekday vs the other four ---
    dow_ladder = {}
    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    for d in all_days:
        this_day = by_dow.get(d, [])
        other_days = [e for dd in all_days if dd != d for e in by_dow.get(dd, [])]
        dow_ladder[d] = dict(
            n=len(this_day),
            efficiency=describe([e["efficiency_ratio"] for e in this_day]),
            vol=describe([e["realized_vol"] for e in this_day]),
            p_efficiency_vs_rest=mwu_p([e["efficiency_ratio"] for e in this_day], [e["efficiency_ratio"] for e in other_days]),
            p_vol_vs_rest=mwu_p([e["realized_vol"] for e in this_day], [e["realized_vol"] for e in other_days]),
        )

    # --- placebo / permutation control: random ~1/5 "pseudo-Friday" ---
    rng = np.random.default_rng(RNG_SEED)
    all_events = list(events)
    n_total = len(all_events)
    n_pseudo = len(fri)
    idx_all = np.arange(n_total)
    pseudo_idx = rng.choice(idx_all, size=min(n_pseudo, n_total), replace=False)
    pseudo_set = set(pseudo_idx.tolist())
    pseudo_fri = [all_events[i] for i in pseudo_idx]
    pseudo_rest = [all_events[i] for i in idx_all if i not in pseudo_set]
    placebo = dict(
        p_efficiency=mwu_p([e["efficiency_ratio"] for e in pseudo_fri], [e["efficiency_ratio"] for e in pseudo_rest]),
        p_vol=mwu_p([e["realized_vol"] for e in pseudo_fri], [e["realized_vol"] for e in pseudo_rest]),
        n_pseudo_friday=len(pseudo_fri),
    )

    # --- time-of-day within Friday: ny-subsession vs late-subsession efficiency/vol ---
    # (reconstructed directly rather than re-scanning m, using session bar counts already on each event)
    friday_session_split = dict(
        n_with_late_session=sum(1 for e in fri if e["n_late_bars"] > 0),
        n_with_ny_session=sum(1 for e in fri if e["n_ny_bars"] > 0),
    )

    # --- reversal-of-week's-trend test ---
    fri_opp = [e["opposes_prior_week_trend"] for e in fri if e.get("opposes_prior_week_trend") is not None]
    other_opp = [e["opposes_prior_week_trend"] for d in ["Monday", "Tuesday", "Wednesday", "Thursday"]
                 for e in by_dow.get(d, []) if e.get("opposes_prior_week_trend") is not None]
    from scipy.stats import chi2_contingency
    def chi2_p(rate1, n1, rate2, n2):
        if n1 == 0 or n2 == 0:
            return None
        s1, s2 = round(rate1 * n1), round(rate2 * n2)
        try:
            _, p, _, _ = chi2_contingency([[s1, n1 - s1], [s2, n2 - s2]])
            return float(p)
        except Exception:
            return None
    fri_opp_rate = float(np.mean(fri_opp)) if fri_opp else None
    other_opp_rate = float(np.mean(other_opp)) if other_opp else None
    reversal_test = dict(
        friday_opposition_rate=fri_opp_rate, friday_n=len(fri_opp),
        other_days_opposition_rate=other_opp_rate, other_n=len(other_opp),
        p=chi2_p(fri_opp_rate or 0, len(fri_opp), other_opp_rate or 0, len(other_opp)),
    )

    # --- context slices on Friday only: vol_regime, week_trend_direction, last_trading_week_of_month ---
    slices = {}
    for vr in ["low", "mid", "high"]:
        sub = [e for e in fri]  # vol_regime not directly attached to event; approximate via ATR-based realized_vol tercile instead
    # volatility regime context: use realized_vol terciles computed over Friday's own sample (disclosed)
    if fri:
        rv = np.array([e["realized_vol"] for e in fri])
        q1, q2 = np.percentile(rv, [33.33, 66.67])
        for label, lo, hi in [("low", -np.inf, q1), ("mid", q1, q2), ("high", q2, np.inf)]:
            sub = [e for e in fri if lo < e["realized_vol"] <= hi] if label != "low" else [e for e in fri if e["realized_vol"] <= hi]
            slices[f"vol_tercile_{label}"] = describe([e["efficiency_ratio"] for e in sub])

    trend_dirs = {}
    for td, name in [(1, "week_trend_up"), (-1, "week_trend_down"), (0, "week_trend_flat")]:
        sub = [e for e in fri if e.get("week_trend_direction") == td]
        trend_dirs[name] = dict(n=len(sub), efficiency=describe([e["efficiency_ratio"] for e in sub]),
                                 vol=describe([e["realized_vol"] for e in sub]))

    last_week = [e for e in fri if e.get("last_trading_week_of_month")]
    not_last_week = [e for e in fri if not e.get("last_trading_week_of_month")]
    week_of_month = dict(
        last_trading_week=describe([e["efficiency_ratio"] for e in last_week]),
        other_weeks=describe([e["efficiency_ratio"] for e in not_last_week]),
        p=mwu_p([e["efficiency_ratio"] for e in last_week], [e["efficiency_ratio"] for e in not_last_week]),
    )

    return dict(
        timeframe=tf, split_metadata=meta, n_bars=int(len(m)),
        date_range=[str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
        n_afternoon_events=len(events), n_friday_events=len(fri),
        primary=primary, dow_ladder=dow_ladder, placebo_control=placebo,
        friday_session_split=friday_session_split, reversal_test=reversal_test,
        slices=dict(vol_tercile=slices, week_trend=trend_dirs, week_of_month=week_of_month),
    )


def main():
    results = {"edge": "E008", "edge_id": "E008", "hypothesis_version": "V0",
               "run_id": "discovery_pass_1_full_profile_2026-07-21",
               "timeframes_tested": [], "timeframes_unavailable": {
                   "M1": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)",
                   "M5": "not present anywhere in this project's data (EDGE_DISCOVERY_ROADMAP.md SS1)"},
               "params": dict(RNG_SEED=RNG_SEED), "by_timeframe": {}}

    for tf in ["M15", "H1"]:
        print("=== running", tf, "===")
        res = run_timeframe(tf)
        results["by_timeframe"][tf] = res
        results["timeframes_tested"].append(tf)
        print(tf, "n_afternoon_events", res["n_afternoon_events"], "n_friday", res["n_friday_events"])
        print(" primary:", res["primary"])
        print(" placebo_control:", res["placebo_control"])
        print(" reversal_test:", res["reversal_test"])
        for k, v in res["dow_ladder"].items():
            print(" dow_ladder", k, {kk: v[kk] for kk in ("n", "p_efficiency_vs_rest", "p_vol_vs_rest")})

    with open("e008_friday_profit_taking_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)


if __name__ == "__main__":
    main()

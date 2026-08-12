"""EXPERIMENT — is the weekly-breakout edge the PERIOD or the STOP AMPLITUDE? (discovery, not a candidate)

CAND-0037 confounds three things: weekly SIGNAL + weekly-range STOP + week-long HORIZON. Isolate the stop
by holding the DAILY breakout signal fixed and swapping in a WEEKLY-range stop (and, separately, horizon):

  V1 baseline  : daily break, stop = opposite DAILY level,  horizon = day boundary   (the flat PDH/PDL break)
  V2 stop-only : daily break, stop = opposite WEEKLY level, horizon = day boundary   (isolates STOP size)
  V3 stop+hz   : daily break, stop = opposite WEEKLY level, horizon = week boundary  (stop + horizon)
  V4 reference : WEEKLY break (CAND-0037)                                            (weekly signal too)

Same daily break SIGNALS across V1-V3 (only stop/horizon change) -> clean isolation.
If V2/V3 reach CAND-0037's robust edge -> the STOP amplitude was the driver, timeframe did not matter.
If V2/V3 stay flat -> the weekly PERIOD genuinely matters.

Ratified primitives imported @5443077. Holdout sealed. Worst-case intrabar. No lookahead.
"""
from __future__ import annotations
import os, sys, json
import numpy as np
for _c in [os.environ.get("RATIFIED_CODE_DIR"),
           r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad\ratified_code\code"]:
    if _c and os.path.isdir(_c):
        os.environ["RATIFIED_CODE_DIR"] = _c
        if _c not in sys.path:
            sys.path.insert(0, _c)
        break
from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
from edge_research._screen import (derive_blocks, simulate, metrics, screen_verdict, Trade,
                                   day_index_ny17, bars_to_period_end, breakout_trades)
from institutional_levels import (compute_prior_day_levels, compute_prior_week_levels,
                                  derive_week_index, LevelKind)


def _be_fn(blocks, n):
    def be(idx):
        for b in blocks:
            if b.start <= idx < b.end:
                return b.end
        return n
    return be


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); h = d["high"].to_numpy(); l = d["low"].to_numpy()
    c = d["close"].to_numpy(); t = d["time"].to_numpy()
    n = len(c); blocks = derive_blocks(d)
    be = _be_fn(blocks, n)
    day_idx = day_index_ny17(t); week_idx = derive_week_index(day_idx)
    years = d["dt"].dt.year.to_numpy()

    day_levels = compute_prior_day_levels(h, l, day_idx, blocks)
    week_levels = compute_prior_week_levels(h, l, day_idx, week_idx, blocks)

    # active prior-week PWH/PWL per bar (the weekly stop reference)
    active_pwh = np.full(n, np.nan); active_pwl = np.full(n, np.nan)
    wk_pair = {}
    for lv in week_levels:
        if lv.kind in (LevelKind.WEEKLY_HIGH, LevelKind.WEEKLY_LOW):
            wk_pair.setdefault((lv.block_index, lv.available_idx), {})[lv.kind] = lv.price
    for (bi, avail), pair in wk_pair.items():
        wend = min(avail + bars_to_period_end(week_idx, avail, be(avail)), n)
        for j in range(avail, wend):
            if LevelKind.WEEKLY_HIGH in pair:
                active_pwh[j] = pair[LevelKind.WEEKLY_HIGH]
            if LevelKind.WEEKLY_LOW in pair:
                active_pwl[j] = pair[LevelKind.WEEKLY_LOW]

    # daily break signals (same across V1-V3)
    day_opp = {}
    for lv in day_levels:
        day_opp.setdefault((lv.block_index, lv.source_period_start), {})[lv.kind] = lv.price
    signals = []  # (j, side, daily_opp, weekly_opp)
    for lv in day_levels:
        if lv.kind not in (LevelKind.PDH, LevelKind.PDL):
            continue
        avail = lv.available_idx; wend = min(avail + bars_to_period_end(day_idx, avail, be(avail)), n)
        is_high = lv.kind is LevelKind.PDH
        sig = None
        for j in range(avail, wend):
            if (is_high and c[j] > lv.price) or ((not is_high) and c[j] < lv.price):
                sig = j; break
        if sig is None:
            continue
        pair = day_opp.get((lv.block_index, lv.source_period_start), {})
        d_opp = pair.get(LevelKind.PDL) if is_high else pair.get(LevelKind.PDH)
        w_opp = active_pwl[sig] if is_high else active_pwh[sig]
        signals.append((sig, "long" if is_high else "short", d_opp, w_opp))

    def build(stop_kind, horizon):
        tr = []
        for sig, side, d_opp, w_opp in signals:
            stop = d_opp if stop_kind == "daily" else w_opp
            if stop is None or (isinstance(stop, float) and np.isnan(stop)):
                continue
            pidx = day_idx if horizon == "day" else week_idx
            tsb = bars_to_period_end(pidx, sig, be(sig))
            tr.append(Trade(signal_idx=sig, side=side, stop=float(stop), time_stop_bars=tsb))
        return tr

    def evl(trades):
        res = simulate(o, h, l, c, trades)
        m = metrics(res)
        by = {}
        for x in res:
            by.setdefault(int(years[x["signal_idx"]]), []).append(x["r"])
        yp = sum(1 for v in by.values() if sum(v) / len(v) > 0)
        return dict(n=m.get("n"), win=m.get("win_rate"), avg_R=m.get("avg_R"), median=m.get("median_R"),
                    PF=m.get("profit_factor"), best_share=m.get("best_share_of_total"),
                    trimmed_avg_R=m.get("trimmed_top1pct", {}).get("avg_R"),
                    years_pos=f"{yp}/{len(by)}", verdict=screen_verdict(m))

    out = {
        "V1_daily_dailyStop_dayHz": evl(build("daily", "day")),
        "V2_daily_weeklyStop_dayHz": evl(build("weekly", "day")),
        "V3_daily_weeklyStop_weekHz": evl(build("weekly", "week")),
    }
    # V4 weekly reference
    wk_norm = []
    for lv in week_levels:
        if lv.kind not in (LevelKind.WEEKLY_HIGH, LevelKind.WEEKLY_LOW):
            continue
        pair = wk_pair.get((lv.block_index, lv.available_idx), {})
        is_high = lv.kind is LevelKind.WEEKLY_HIGH
        opp = pair.get(LevelKind.WEEKLY_LOW) if is_high else pair.get(LevelKind.WEEKLY_HIGH)
        wk_norm.append(dict(price=lv.price, is_high=is_high, avail=lv.available_idx, opp=opp))
    trv4, _ = breakout_trades(wk_norm, h, l, c, week_idx, blocks)
    out["V4_weekly_reference"] = evl(trv4)

    result = dict(experiment="stop_amplitude_vs_period", data=dict(rows=n, blocks=len(blocks)),
                  n_daily_break_signals=len(signals), variants=out)
    print(json.dumps(result, indent=2))
    with open(os.path.join(os.path.dirname(__file__), "exp_stop_vs_period_results.json"), "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()

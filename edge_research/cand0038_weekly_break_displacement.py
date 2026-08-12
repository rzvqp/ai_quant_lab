"""CAND-0038 — WEEKLY breakout confirmed by DISPLACEMENT — Flow B quick screen.

Refinement of CAND-0037 (the confirmed weekly-breakout edge): require the break bar to ALSO be a
same-direction expansion bar (market_state.expansion). Question: does displacement confirmation sharpen
the edge (higher/robust avg_R, fewer false weekly breaks) or just cut sample without adding?

POLICY (pre-registered): identical to CAND-0037 EXCEPT the trigger adds the displacement filter.
  signal = first bar in the current week that closes THROUGH the prior-week level AND is an expansion
           bar in the break direction
  side   = WITH the break ; stop = OPPOSITE prior-week level (structural) ; exit = week-boundary time-stop
Ratified compute_prior_week_levels + expansion (@5443077). Holdout sealed. Worst-case intrabar. No lookahead.
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
                                   day_index_ny17, bars_to_period_end)
from institutional_levels import compute_prior_week_levels, derive_week_index, LevelKind
from market_state import expansion


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); h = d["high"].to_numpy(); l = d["low"].to_numpy()
    c = d["close"].to_numpy(); t = d["time"].to_numpy()
    n = len(c); blocks = derive_blocks(d)
    day_idx = day_index_ny17(t); week_idx = derive_week_index(day_idx)
    years = d["dt"].dt.year.to_numpy()
    exp = expansion(o, h, l, c)
    exp_dir = [(1 if c[i] > o[i] else -1) for i in range(n)]

    def be(idx):
        for b in blocks:
            if b.start <= idx < b.end:
                return b.end
        return n

    levels = compute_prior_week_levels(h, l, day_idx, week_idx, blocks)
    pair = {}
    for lv in levels:
        if lv.kind in (LevelKind.WEEKLY_HIGH, LevelKind.WEEKLY_LOW):
            pair.setdefault((lv.block_index, lv.available_idx), {})[lv.kind] = lv.price

    trades = []
    n_broke_plain = 0
    for lv in levels:
        if lv.kind not in (LevelKind.WEEKLY_HIGH, LevelKind.WEEKLY_LOW):
            continue
        is_high = lv.kind is LevelKind.WEEKLY_HIGH
        avail = lv.available_idx; wend = min(avail + bars_to_period_end(week_idx, avail, be(avail)), n)
        opp = pair.get((lv.block_index, lv.available_idx), {}).get(
            LevelKind.WEEKLY_LOW if is_high else LevelKind.WEEKLY_HIGH)
        if opp is None:
            continue
        sig = None
        for j in range(avail, wend):
            broke = (c[j] > lv.price) if is_high else (c[j] < lv.price)
            if broke:
                n_broke_plain += 1 if sig is None else 0
                disp = exp[j] and exp_dir[j] == (1 if is_high else -1)
                if disp:
                    sig = j; break
                # if first close-through is not a displacement, this weekly break is not confirmed -> skip
                break
        if sig is None:
            continue
        tsb = bars_to_period_end(week_idx, sig, be(sig))
        trades.append(Trade(signal_idx=sig, side=("long" if is_high else "short"),
                            stop=float(opp), time_stop_bars=tsb))

    res = simulate(o, h, l, c, trades)
    m = metrics(res)
    by = {}
    for x in res:
        by.setdefault(int(years[x["signal_idx"]]), []).append(x["r"])
    yp = sum(1 for v in by.values() if sum(v) / len(v) > 0)
    out = dict(candidate="CAND-0038", family="weekly_breakout_x_displacement",
               data=dict(rows=n, blocks=len(blocks)),
               detector="compute_prior_week_levels + expansion @5443077",
               n_trades=len(trades), metrics=m,
               year_stability={str(y): dict(n=len(v), avg_R=round(sum(v)/len(v), 3)) for y, v in sorted(by.items())},
               years_positive=f"{yp}/{len(by)}", SCREEN_VERDICT=screen_verdict(m))
    print(json.dumps(out, indent=2))
    with open(os.path.join(os.path.dirname(__file__), "cand0038_weekly_break_displacement_results.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()

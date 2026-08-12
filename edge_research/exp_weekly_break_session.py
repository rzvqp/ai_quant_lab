"""EXPERIMENT — weekly breakout x SESSION alignment. Does the session in which the weekly break occurs
matter? (refinement test of CAND-0037; discovery-style, per-session split.)

Same CAND-0037 weekly-break trades, grouped by the SESSION label of the break bar (asia/london/ny/late).
If one session's weekly breaks are robustly stronger -> a sharper candidate; if flat across -> session
does not add and CAND-0037 (all-session) stands.
Ratified compute_prior_week_levels @5443077. Holdout sealed. Worst-case intrabar. No lookahead.
"""
from __future__ import annotations
import os, sys, json
for _c in [os.environ.get("RATIFIED_CODE_DIR"),
           r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad\ratified_code\code"]:
    if _c and os.path.isdir(_c):
        os.environ["RATIFIED_CODE_DIR"] = _c
        if _c not in sys.path:
            sys.path.insert(0, _c)
        break
from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
from edge_research._screen import (derive_blocks, simulate, metrics, screen_verdict,
                                   day_index_ny17, breakout_trades)
from institutional_levels import compute_prior_week_levels, derive_week_index, LevelKind


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); h = d["high"].to_numpy(); l = d["low"].to_numpy()
    c = d["close"].to_numpy(); t = d["time"].to_numpy()
    n = len(c); blocks = derive_blocks(d)
    sess = d["session"].to_numpy()
    day_idx = day_index_ny17(t); week_idx = derive_week_index(day_idx)

    levels = compute_prior_week_levels(h, l, day_idx, week_idx, blocks)
    pair = {}
    for lv in levels:
        if lv.kind in (LevelKind.WEEKLY_HIGH, LevelKind.WEEKLY_LOW):
            pair.setdefault((lv.block_index, lv.available_idx), {})[lv.kind] = lv.price
    norm = []
    for lv in levels:
        if lv.kind not in (LevelKind.WEEKLY_HIGH, LevelKind.WEEKLY_LOW):
            continue
        is_high = lv.kind is LevelKind.WEEKLY_HIGH
        opp = pair.get((lv.block_index, lv.available_idx), {}).get(
            LevelKind.WEEKLY_LOW if is_high else LevelKind.WEEKLY_HIGH)
        norm.append(dict(price=lv.price, is_high=is_high, avail=lv.available_idx, opp=opp))

    trades, _ = breakout_trades(norm, h, l, c, week_idx, blocks)
    res = simulate(o, h, l, c, trades)
    # group by session of the break (signal) bar
    bysess = {}
    for x in res:
        bysess.setdefault(str(sess[x["signal_idx"]]), []).append(x)
    out = {}
    for s, rr in bysess.items():
        m = metrics(rr)
        out[s] = dict(n=m["n"], win=m["win_rate"], avg_R=m["avg_R"], median=m["median_R"],
                      PF=m["profit_factor"], best_share=m.get("best_share_of_total"),
                      trimmed_avg_R=m.get("trimmed_top1pct", {}).get("avg_R"),
                      verdict=screen_verdict(m, min_n=15))
    result = dict(experiment="weekly_breakout_x_session", n_all=len(res), by_session=out)
    print(json.dumps(result, indent=2))
    with open(os.path.join(os.path.dirname(__file__), "exp_weekly_break_session_results.json"), "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()

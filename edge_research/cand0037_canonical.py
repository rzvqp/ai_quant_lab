"""CAND-0037 weekly breakout — RE-EVALUATED on the CANONICAL evaluator (Step 6).

Signal logic UNCHANGED (breakout_trades). Evaluation is now the ONE lab evaluator (mstrat.simulate, NET
of CFG cost). This is the first strategy re-expressed on the canonical basis; its prior GROSS numbers are
HISTORICAL / NON-COMPARABLE.
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
from edge_research._screen import (derive_blocks, day_index_ny17, breakout_trades,
                                   canonical_evaluate, metrics, screen_verdict)
from institutional_levels import compute_prior_week_levels, derive_week_index, LevelKind


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    h = d["high"].to_numpy(); l = d["low"].to_numpy(); c = d["close"].to_numpy(); t = d["time"].to_numpy()
    blocks = derive_blocks(d)
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

    res = canonical_evaluate(d, trades)     # NET, canonical
    m = metrics(res)
    years = d["dt"].dt.year.to_numpy()
    by = {}
    for x in res:
        by.setdefault(int(years[x["signal_idx"]]), []).append(x["r"])
    yp = sum(1 for v in by.values() if sum(v) / len(v) > 0)
    out = dict(candidate="CAND-0037", basis="CANONICAL (mstrat.simulate, NET)",
               n_trades=len(trades), n_evaluated=m["n"], metrics=m,
               years_positive=f"{yp}/{len(by)}", SCREEN_VERDICT=screen_verdict(m),
               note="prior gross numbers are HISTORICAL / NON-COMPARABLE")
    print(json.dumps(out, indent=2, default=float))
    with open(os.path.join(os.path.dirname(__file__), "cand0037_canonical_results.json"), "w") as f:
        json.dump(out, f, indent=2, default=float)


if __name__ == "__main__":
    main()

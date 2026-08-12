"""CAND-0006 — PRIOR-WEEK HIGH/LOW (PWH/PWL), Route 3 — Flow B quick economic screen.

Route 3 (decided before results): NO bias filter — the level alone decides, direction from the level
kind (WEEKLY_HIGH = resistance -> SHORT ; WEEKLY_LOW = support -> LONG). The weekly sibling of the
level-fade family (CAND-0001 PDH/PDL, CAND-0027 session). The bias stage was the sole collapse
(275 touched -> 6 aligned); removed.

POLICY (Part A + Part B, chosen BEFORE results):
  population = COMPLETE weeks only (>=5 contributing days); PARTIAL -> no trade (ratified flag)
  entry   = next-open after the ratified weekly-level touch (detect_weekly_level_touches, penetration)
  side    = WEEKLY_HIGH -> SHORT ; WEEKLY_LOW -> LONG
  stop    = touch-bar extreme (short -> high[touch] ; long -> low[touch])
  target  = the opposite prior-week level (same source week)
  exit    = week-boundary live time-stop (bars until week_index changes) as backstop
  sizing  = 1R

Uses RATIFIED compute_prior_week_levels + detect_weekly_level_touches (@5443077) + the verbatim
17:00-NY day_index / derive_week_index anchor (caller-side). Imported, never reimplemented.
Data via _common.load (M15_v2, holdout sealed). No lookahead.
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
from edge_research._screen import (derive_blocks, simulate, metrics, screen_verdict, Trade,
                                   day_index_ny17, bars_to_period_end)
from institutional_levels import compute_prior_week_levels, LevelKind, derive_week_index
from reaction_detectors import detect_weekly_level_touches


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); h = d["high"].to_numpy(); l = d["low"].to_numpy()
    c = d["close"].to_numpy(); t = d["time"].to_numpy()
    blocks = derive_blocks(d)

    day_idx = day_index_ny17(t)
    week_idx = derive_week_index(day_idx)

    levels = compute_prior_week_levels(h, l, day_idx, week_idx, blocks)
    # opposite-level map: (block_index, source_period_start) -> {kind: price}
    opp = {}
    for lv in levels:
        opp.setdefault((lv.block_index, lv.source_period_start), {})[lv.kind] = lv.price

    touches = detect_weekly_level_touches(h, l, levels, week_idx, blocks)
    n_touch = len(touches)
    n_complete = sum(1 for tc in touches if tc.completeness == "COMPLETE")

    block_end_of = {}
    for b in blocks:
        for _ in range(1):
            block_end_of[b.start] = b.end
    def _block_end(idx):
        for b in blocks:
            if b.start <= idx < b.end:
                return b.end
        return len(c)

    trades = []
    for tc in touches:
        if tc.completeness != "COMPLETE":
            continue                                   # PARTIAL -> no trade (fail-closed)
        lv = tc.level; j = tc.touch_idx
        key = (lv.block_index, lv.source_period_start)
        if lv.kind is LevelKind.WEEKLY_HIGH:
            side = "short"; stop = float(h[j]); tgt = opp.get(key, {}).get(LevelKind.WEEKLY_LOW)
        else:
            side = "long"; stop = float(l[j]); tgt = opp.get(key, {}).get(LevelKind.WEEKLY_HIGH)
        tsb = bars_to_period_end(week_idx, j, _block_end(j))
        trades.append(Trade(signal_idx=j, side=side, stop=stop,
                            time_stop_bars=tsb, target=(float(tgt) if tgt is not None else None)))

    res = simulate(o, h, l, c, trades)
    m = metrics(res)
    verdict = screen_verdict(m)

    out = dict(candidate="CAND-0006", family="weekly_reference_levels_route3",
               data=dict(rows=len(d), range=[meta["min_date_used"][:10], meta["max_date_used"][:10]],
                         segments=meta["n_discovery_segments"], blocks=len(blocks)),
               detector="detect_weekly_level_touches @5443077 (17:00-NY anchor verbatim)",
               n_weekly_levels=len(levels), n_touches=n_touch, n_complete_touches=n_complete,
               n_trades_simulated=len(trades), metrics=m, SCREEN_VERDICT=verdict)
    print(json.dumps(out, indent=2))
    with open(os.path.join(os.path.dirname(__file__), "cand0006_weekly_level_results.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()

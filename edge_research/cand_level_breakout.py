"""LEVEL BREAKOUT / continuation (Route 2) — Flow B quick economic screen, same 3 populations as the fade.

Pre-registered variant (BEFORE results), directly comparable to the fade on the SAME populations:
  signal = FIRST close THROUGH the level in its active period (break)
  side   = WITH the break (HIGH break -> LONG ; LOW break -> SHORT)
  stop   = the OPPOSITE prior-period level (STRUCTURAL, non-microscopic — the far side of the range)
  exit   = period-boundary live time-stop ; no fixed target ; 1R
The structural stop is the whole point: the tiny touch-bar stop caused the fade's fat-tail. With a
full-range stop, either the breakout edge is real or it disappears — no tiny-stop lottery.

PDH/PDL, session, weekly — all three. Ratified level primitives imported @5443077. Holdout sealed.
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
from institutional_levels import (compute_prior_day_levels, compute_prior_week_levels,
                                  derive_week_index, LevelKind)
from session_levels import (compute_prior_session_levels, derive_session_index, session_labels,
                            SessionLevelKind)


def _norm(levels, high_kind, low_kind, keyfn):
    """Pair each level with its opposite (same source period) -> breakout levels_norm dicts."""
    opp = {}
    for lv in levels:
        opp.setdefault(keyfn(lv), {})[lv.kind] = lv.price
    out = []
    for lv in levels:
        if lv.kind not in (high_kind, low_kind):
            continue
        pair = opp.get(keyfn(lv), {})
        is_high = lv.kind is high_kind
        opp_price = pair.get(low_kind) if is_high else pair.get(high_kind)
        out.append(dict(price=lv.price, is_high=is_high, avail=lv.available_idx, opp=opp_price))
    return out


def run_one(name, levels_norm, h, l, c, period_index, blocks):
    o = None
    trades, diag = breakout_trades(levels_norm, h, l, c, period_index, blocks)
    return trades, diag


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); h = d["high"].to_numpy(); l = d["low"].to_numpy()
    c = d["close"].to_numpy(); t = d["time"].to_numpy()
    blocks = derive_blocks(d)
    day_idx = day_index_ny17(t); week_idx = derive_week_index(day_idx)
    sess_idx = derive_session_index(t); sess_lbl = session_labels(t)

    day_levels = compute_prior_day_levels(h, l, day_idx, blocks)
    week_levels = compute_prior_week_levels(h, l, day_idx, week_idx, blocks)
    sess_levels = compute_prior_session_levels(h, l, sess_idx, sess_lbl, blocks)

    cases = {
        "PDH_PDL_break": (_norm(day_levels, LevelKind.PDH, LevelKind.PDL,
                                lambda lv: (lv.block_index, lv.source_period_start)), day_idx),
        "session_break": (_norm(sess_levels, SessionLevelKind.SESSION_HIGH, SessionLevelKind.SESSION_LOW,
                                lambda lv: (lv.block_index, lv.source_session_start)), sess_idx),
        "weekly_break": (_norm([lv for lv in week_levels if lv.kind in (LevelKind.WEEKLY_HIGH, LevelKind.WEEKLY_LOW)],
                               LevelKind.WEEKLY_HIGH, LevelKind.WEEKLY_LOW,
                               lambda lv: (lv.block_index, lv.source_period_start)), week_idx),
    }

    years = d["dt"].dt.year.to_numpy()
    allout = {}
    for name, (lv_norm, pidx) in cases.items():
        trades, diag = breakout_trades(lv_norm, h, l, c, pidx, blocks)
        res = simulate(o, h, l, c, trades, cost=0.08)   # realistic measured XAUUSD spread (p75)
        m = metrics(res)
        # per-year stability (avg_R, n) — is the edge spread across years or concentrated?
        by_year = {}
        for x in res:
            yr = int(years[x["signal_idx"]])
            by_year.setdefault(yr, []).append(x["r"])
        yr_stab = {str(yr): dict(n=len(v), avg_R=round(sum(v) / len(v), 3))
                   for yr, v in sorted(by_year.items())}
        yrs_pos = sum(1 for v in by_year.values() if sum(v) / len(v) > 0)
        allout[name] = dict(diag=diag, n_trades=len(trades), metrics=m,
                            year_stability=yr_stab, years_positive=f"{yrs_pos}/{len(by_year)}",
                            SCREEN_VERDICT=screen_verdict(m))

    out = dict(candidate="LEVEL-BREAKOUT (Route 2, structural stop)", family="level_breakout_continuation",
               data=dict(rows=len(d), blocks=len(blocks)), cases=allout)
    print(json.dumps(out, indent=2))
    with open(os.path.join(os.path.dirname(__file__), "cand_level_breakout_results.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()

"""CAND-0009 — LEVEL BREAK-AND-DRIVE — Flow B quick economic screen (CEO-named hypothesis).

The only candidate that traded the RUPTURE (not the fade). Pre-screen (pre-repair) had +146R, 4/8yr,
2/3 regimes. Now: run through the screener WITH the fat-tail check.

POLICY (v3.0, pre-registered): a PDH/PDL break confirmed by a same-direction DISPLACEMENT (expansion bar).
  signal = first bar in the level window that BOTH closes through the level AND is an expansion bar in
           the break direction (market_state.expansion; range>1.5*ATR14[i-1] & body>=0.5*range)
  side   = break direction (PDH break -> LONG ; PDL break -> SHORT)
  stop   = the broken level (PDH long / PDL short)   [small stop -> fat-tail test]
  exit   = first OPPOSING-direction expansion bar, else 14-bar (ATR_WINDOW) time-stop
  sizing = 1R
Ratified compute_prior_day_levels + expansion (@5443077). Imported. Holdout sealed. No lookahead.
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
from institutional_levels import compute_prior_day_levels, LevelKind
from market_state import expansion

ATR_WINDOW = 14


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); h = d["high"].to_numpy(); l = d["low"].to_numpy()
    c = d["close"].to_numpy(); t = d["time"].to_numpy()
    blocks = derive_blocks(d)
    day_idx = day_index_ny17(t)
    levels = compute_prior_day_levels(h, l, day_idx, blocks)
    exp = expansion(o, h, l, c)
    exp_dir = [(1 if c[i] > o[i] else -1) for i in range(len(c))]  # displacement direction

    def _be(idx):
        for b in blocks:
            if b.start <= idx < b.end:
                return b.end
        return len(c)

    trades = []
    for lv in levels:
        if lv.kind not in (LevelKind.PDH, LevelKind.PDL):
            continue
        avail = lv.avail if hasattr(lv, "avail") else lv.available_idx
        bend = _be(avail)
        wend = min(avail + bars_to_period_end(day_idx, avail, bend), len(c))
        is_high = lv.kind is LevelKind.PDH
        sig = None
        for j in range(avail, wend):
            broke = (c[j] > lv.price) if is_high else (c[j] < lv.price)
            disp = exp[j] and (exp_dir[j] == (1 if is_high else -1))
            if broke and disp:
                sig = j; break
        if sig is None:
            continue
        side = "long" if is_high else "short"
        stop = float(lv.price)
        # exit horizon: first OPPOSING-direction expansion bar after entry, else 14-bar
        ei = sig + 1
        want_opp = -1 if is_high else 1
        tsb = ATR_WINDOW
        for k in range(ei, min(ei + ATR_WINDOW, len(c))):
            if exp[k] and exp_dir[k] == want_opp:
                tsb = max(1, k - ei); break
        trades.append(Trade(signal_idx=sig, side=side, stop=stop, time_stop_bars=tsb, target=None))

    res = simulate(o, h, l, c, trades)
    m = metrics(res)
    years = d["dt"].dt.year.to_numpy()
    by_year = {}
    for x in res:
        by_year.setdefault(int(years[x["signal_idx"]]), []).append(x["r"])
    yr_stab = {str(y): dict(n=len(v), avg_R=round(sum(v)/len(v), 3)) for y, v in sorted(by_year.items())}
    yrs_pos = sum(1 for v in by_year.values() if sum(v)/len(v) > 0)
    out = dict(candidate="CAND-0009", family="level_break_with_displacement",
               data=dict(rows=len(d), blocks=len(blocks)),
               detector="compute_prior_day_levels + expansion @5443077",
               n_levels=len(levels), n_trades=len(trades), metrics=m,
               year_stability=yr_stab, years_positive=f"{yrs_pos}/{len(by_year)}",
               SCREEN_VERDICT=screen_verdict(m))
    print(json.dumps(out, indent=2))
    with open(os.path.join(os.path.dirname(__file__), "cand0009_level_break_drive_results.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()

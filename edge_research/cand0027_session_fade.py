"""CAND-0027 — session level-fade (touch+rejection) — Flow B quick economic screen.

POLICY (pre-registered, Primitive A): fade the prior-session level, direction from kind.
  entry = next-open after detect_session_level_touches (penetration)
  side  = SESSION_HIGH -> SHORT ; SESSION_LOW -> LONG
  stop  = touch-bar extreme ; target = opposite prior-session level ; exit = session-boundary time-stop
Uses RATIFIED compute_prior_session_levels + detect_session_level_touches (@5443077). Imported.
Data via _common.load (M15_v2, holdout sealed). No lookahead.
FEED-ALIGNMENT WARNING: session clock uses fixed UTC hours; OANDA-historic vs MT5-live bar sets
diverge ~3h -> backtest session level != live. Carried.
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
                                   bars_to_period_end)
from session_levels import (compute_prior_session_levels, detect_session_level_touches,
                            derive_session_index, session_labels, SessionLevelKind)


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); h = d["high"].to_numpy(); l = d["low"].to_numpy()
    c = d["close"].to_numpy(); t = d["time"].to_numpy()
    blocks = derive_blocks(d)
    sess_idx = derive_session_index(t)
    sess_lbl = session_labels(t)
    levels = compute_prior_session_levels(h, l, sess_idx, sess_lbl, blocks)
    opp = {}
    for lv in levels:
        opp.setdefault((lv.block_index, lv.source_session_start), {})[lv.kind] = lv.price
    touches = detect_session_level_touches(h, l, levels)

    def _block_end(idx):
        for b in blocks:
            if b.start <= idx < b.end:
                return b.end
        return len(c)

    trades = []
    for tc in touches:
        lv = tc.level; j = tc.touch_idx; key = (lv.block_index, lv.source_session_start)
        if lv.kind is SessionLevelKind.SESSION_HIGH:
            side, stop, tgt = "short", float(h[j]), opp.get(key, {}).get(SessionLevelKind.SESSION_LOW)
        else:
            side, stop, tgt = "long", float(l[j]), opp.get(key, {}).get(SessionLevelKind.SESSION_HIGH)
        tsb = bars_to_period_end(sess_idx, j, _block_end(j))
        trades.append(Trade(signal_idx=j, side=side, stop=stop, time_stop_bars=tsb,
                            target=(float(tgt) if tgt is not None else None)))
    res = simulate(o, h, l, c, trades)
    m = metrics(res); verdict = screen_verdict(m)
    out = dict(candidate="CAND-0027", family="session_level_fade",
               data=dict(rows=len(d), blocks=len(blocks)),
               detector="detect_session_level_touches @5443077",
               n_levels=len(levels), n_touches=len(touches), n_trades=len(trades),
               metrics=m, SCREEN_VERDICT=verdict)
    print(json.dumps(out, indent=2))
    with open(os.path.join(os.path.dirname(__file__), "cand0027_session_fade_results.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()

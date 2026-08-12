"""CAND-0004 — LIQUIDITY-VOID REACTION — Flow B quick economic screen.

IDEA: a liquidity void (gap between close[c] and open[c+1]) acts as support/resistance; price that
dips into the void and CLOSES BACK OUTSIDE (the ratified D6 rejection) reverses away from it.

POLICY (Part A + Part B, chosen BEFORE results):
  entry   = next-open after `rejection_idx` (VoidReaction with a real D6 rejection)
  side    = BULLISH void (support) -> LONG ; BEARISH void (resistance) -> SHORT
  stop    = the void's FAR edge (full-fill boundary): long -> zone_lower ; short -> zone_upper
  exit    = 20-bar GROUP_A_HORIZON live time-stop (no invented fixed target)
  sizing  = 1R (screen reads R-multiples)

Uses the RATIFIED detector detect_void_reactions (reaction_detectors.py @ 5443077), imported —
never reimplemented. Data via _common.load (M15_v2, holdout sealed). No lookahead.
"""
from __future__ import annotations
import os, sys, json

os.environ.setdefault("RATIFIED_CODE_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                 "ratified_code_5443077"))
# fall back to the scratchpad snapshot if the repo copy is absent
_CANDS = [os.environ.get("RATIFIED_CODE_DIR"),
          r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad\ratified_code\code"]
for _c in _CANDS:
    if _c and os.path.isdir(_c):
        os.environ["RATIFIED_CODE_DIR"] = _c
        if _c not in sys.path:
            sys.path.insert(0, _c)
        break

from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
from edge_research._screen import derive_blocks, simulate, metrics, screen_verdict, Trade
from reaction_detectors import detect_void_reactions
from imbalance_mechanics import FVGKind

GROUP_A_HORIZON = 20


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); h = d["high"].to_numpy(); l = d["low"].to_numpy()
    c = d["close"].to_numpy(); t = d["time"].to_numpy()
    blocks = derive_blocks(d)

    reactions = detect_void_reactions(o, h, l, c, t, blocks)
    n_react = len(reactions)
    n_rej = sum(1 for r in reactions if r.rejection_idx is not None)

    trades = []
    for r in reactions:
        if r.rejection_idx is None:
            continue
        if r.polarity is FVGKind.BULLISH:
            trades.append(Trade(signal_idx=r.rejection_idx, side="long",
                                stop=r.zone_lower, time_stop_bars=GROUP_A_HORIZON))
        else:
            trades.append(Trade(signal_idx=r.rejection_idx, side="short",
                                stop=r.zone_upper, time_stop_bars=GROUP_A_HORIZON))

    res = simulate(o, h, l, c, trades)
    m = metrics(res)
    verdict = screen_verdict(m)

    out = dict(candidate="CAND-0004", family="liquidity_void_reaction",
               data=dict(rows=len(d), range=[meta["min_date_used"][:10], meta["max_date_used"][:10]],
                         segments=meta["n_discovery_segments"], blocks=len(blocks)),
               detector="detect_void_reactions @5443077",
               n_void_reactions=n_react, n_with_rejection=n_rej, n_trades_simulated=len(trades),
               metrics=m, SCREEN_VERDICT=verdict)
    print(json.dumps(out, indent=2))
    with open(os.path.join(os.path.dirname(__file__), "cand0004_void_reaction_results.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()

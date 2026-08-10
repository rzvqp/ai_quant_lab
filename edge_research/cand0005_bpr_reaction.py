"""CAND-0005 — BPR (Balanced Price Range) REACTION — Flow B quick economic screen.

IDEA: a BPR (overlapping bull×bear FVG pair) is a balanced zone; price that enters it and CLOSES
BACK on the side it came from (ratified D6 rejection) continues in that entry-side direction.

POLICY (Part A + Part B, chosen BEFORE results):
  entry   = next-open after `reject_idx` (BprReaction with a real D6 rejection + a defined entry_side)
  side    = DECLARED by policy (BPR is direction-agnostic): entry_side ABOVE (came from above, BPR
            held as support) -> LONG ; entry_side BELOW (held as resistance) -> SHORT
  stop    = the BPR zone FAR edge (full-traverse boundary): long -> zone_lower ; short -> zone_upper
  exit    = 20-bar GROUP_A_HORIZON live time-stop (no invented fixed target)
  sizing  = 1R

Uses RATIFIED detect_fvgs + detect_bpr_reactions (@5443077), imported. Data via _common.load
(M15_v2, holdout sealed). No lookahead. Direction is a DISCLOSED policy declaration (like the Mid).
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
from edge_research._screen import derive_blocks, simulate, metrics, screen_verdict, Trade
from imbalance_mechanics import detect_fvgs
from reaction_detectors import detect_bpr_reactions, EntrySide

GROUP_A_HORIZON = 20


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); h = d["high"].to_numpy(); l = d["low"].to_numpy()
    c = d["close"].to_numpy()
    blocks = derive_blocks(d)

    fvgs = detect_fvgs(h, l, blocks)
    reactions = detect_bpr_reactions(h, l, c, fvgs, blocks, tolerance=0.0)
    n_react = len(reactions)
    n_rej = sum(1 for r in reactions if r.reject_idx is not None and r.entry_side is not None)

    trades = []
    for r in reactions:
        if r.reject_idx is None or r.entry_side is None:
            continue
        if r.entry_side is EntrySide.ABOVE:
            trades.append(Trade(signal_idx=r.reject_idx, side="long",
                                stop=r.zone_lower, time_stop_bars=GROUP_A_HORIZON))
        else:
            trades.append(Trade(signal_idx=r.reject_idx, side="short",
                                stop=r.zone_upper, time_stop_bars=GROUP_A_HORIZON))

    res = simulate(o, h, l, c, trades)
    m = metrics(res)
    verdict = screen_verdict(m)

    out = dict(candidate="CAND-0005", family="balanced_price_range_reaction",
               data=dict(rows=len(d), range=[meta["min_date_used"][:10], meta["max_date_used"][:10]],
                         segments=meta["n_discovery_segments"], blocks=len(blocks)),
               detector="detect_bpr_reactions @5443077 (over detect_fvgs)",
               n_fvgs=len(fvgs), n_bpr_reactions=n_react, n_with_rejection=n_rej,
               n_trades_simulated=len(trades), metrics=m, SCREEN_VERDICT=verdict)
    print(json.dumps(out, indent=2))
    with open(os.path.join(os.path.dirname(__file__), "cand0005_bpr_reaction_results.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()

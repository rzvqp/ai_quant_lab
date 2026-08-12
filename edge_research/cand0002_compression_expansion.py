"""CAND-0002 family — COMPRESSION -> EXPANSION breakout — Flow B screen, REALISTIC spread.

CEO target: large stop + better frequency than weekly + SIGNIFICANT event. Compression->expansion fits:
the accumulated compression range is the (large ~$5) stop; a compression-then-expansion is a real regime
event (not a fixed period, so it dodges the 'period matters' finding); ~1.5/day frequency.

POLICY (pre-registered, one variant):
  compression = atr14 < 0.8*rolling50(atr14) ; accumulate [hh,ll] over the compression run
  signal = an EXPANSION bar (market_state.expansion) that CLOSES beyond the accumulated range edge
  side   = expansion direction (close>open -> LONG breaking hh ; close<open -> SHORT breaking ll)
  stop   = the OPPOSITE edge of the accumulated compression range (structural, large): long->ll, short->hh
  target = 1x-range measured move beyond the broken edge (RR ~1, symmetric — no invented multiple)
  exit   = 48-bar time-stop backstop ; 1R ; cost = 0.08 (measured p75 XAUUSD spread)
Ratified expansion + atr14 @5443077. Holdout sealed. Worst-case intrabar. No lookahead.
"""
from __future__ import annotations
import os, sys, json
import numpy as np, pandas as pd
for _c in [os.environ.get("RATIFIED_CODE_DIR"),
           r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\44ba92ba-04ad-40f2-a48e-0ee6a8aca893\scratchpad\ratified_code\code"]:
    if _c and os.path.isdir(_c):
        sys.path.insert(0, _c); break
from edge_research._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID
from edge_research._screen import derive_blocks, simulate, metrics, screen_verdict, Trade
from market_state import expansion

SPREAD = 0.08  # measured XAUUSD p75


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); h = d["high"].to_numpy(); l = d["low"].to_numpy()
    c = d["close"].to_numpy(); n = len(d); blocks = derive_blocks(d)
    years = d["dt"].dt.year.to_numpy()
    exp = expansion(o, h, l, c)
    atr = d["atr14"].to_numpy(); atr_ma = pd.Series(atr).rolling(50).mean().to_numpy()
    compress = atr < 0.8 * atr_ma

    def be(idx):
        for b in blocks:
            if b.start <= idx < b.end:
                return b.end
        return n

    trades = []
    for i in np.flatnonzero(exp):
        # accumulate the compression range immediately preceding bar i
        j = i - 1; hh = -np.inf; ll = np.inf; steps = 0
        while j >= 0 and compress[j] and steps < 200:
            hh = max(hh, h[j]); ll = min(ll, l[j]); j -= 1; steps += 1
        if steps < 2 or not np.isfinite(hh) or not np.isfinite(ll) or hh <= ll:
            continue
        rng = hh - ll
        up = c[i] > o[i]
        # close-confirmed breakout of the accumulated range
        if up and c[i] > hh:
            side = "long"; stop = ll; tgt = hh + rng
        elif (not up) and c[i] < ll:
            side = "short"; stop = hh; tgt = ll - rng
        else:
            continue
        if i + 1 >= be(i):
            continue
        trades.append(Trade(signal_idx=i, side=side, stop=float(stop), time_stop_bars=48, target=float(tgt)))

    res = simulate(o, h, l, c, trades, cost=SPREAD)
    m = metrics(res)
    by = {}
    for x in res:
        by.setdefault(int(years[x["signal_idx"]]), []).append(x["r"])
    yp = sum(1 for v in by.values() if sum(v) / len(v) > 0)
    days = (d["dt"].max() - d["dt"].min()).days
    out = dict(candidate="CAND-0002", family="compression_expansion_breakout", spread_used=SPREAD,
               n_trades=len(trades), per_day=round(len(trades) / days, 3), metrics=m,
               year_stability={str(y): dict(n=len(v), avg_R=round(sum(v)/len(v), 3)) for y, v in sorted(by.items())},
               years_positive=f"{yp}/{len(by)}", SCREEN_VERDICT=screen_verdict(m))
    print(json.dumps(out, indent=2, default=float))
    with open(os.path.join(os.path.dirname(__file__), "cand0002_compression_expansion_results.json"), "w") as f:
        json.dump(out, f, indent=2, default=float)


if __name__ == "__main__":
    main()

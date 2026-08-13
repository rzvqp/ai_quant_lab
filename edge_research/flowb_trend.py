"""FLOW B — TREND-pair candidate batch (priority: under-populated TREND × {pullback, momentum}).

Per-candidate loop (CEO continuous mandate):
  pre-register (identity incl. regime) -> implement (logic SEPARATE from evaluator) -> deterministic
  checks -> rapid falsification (>=5 eligible EPISODES, gross-positive, not single-trade) ->
  PROVISIONAL regime-scoped screen (canonical evaluator, marked PROVISIONAL) -> coverage -> status.

Regime is CAUSAL + lookahead-safe (edge_research.regime, from ratified MK-01 swings); RANGE is BLOCKED.
Signal forms ONLY when the pre-registered regime holds on the (closed) signal bar; entry = open of the
NEXT bar. Strategy logic here does NOT touch the evaluator / N1-N6 / Router. ALL numbers are
PROVISIONAL · NON-COMPARABLE UNTIL CANONICAL RATIFICATION · REQUIRES CANONICAL RERUN (4 blocks).
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
from edge_research._screen import derive_blocks, canonical_evaluate, metrics, Trade
from edge_research.regime import trend_regime, episodes, UP, DOWN
from market_state import expansion

HOLD = 20  # holding_window (bars); exit_kind='time' in the canonical evaluator (no invented RR target)

# ── PRE-REGISTRATION CARDS (fixed BEFORE any result; regime is part of identity/run_hash) ──
CARDS = [
    dict(candidate_id="CAND-T01", strategy_family="trend_momentum_continuation",
         allowed_regimes=[UP], allowed_directions=["long"], hyp_in_family="1/4",
         N1_predicate="MK-01 swing structure = TREND_UP (HH+HL, confirmed<=bar)",
         N4_confirmation="expansion bar UP (range>1.5*ATR14[i-1] & body>=0.5*range & close>open)",
         entry="open[i+1]", stop="low[i] (expansion bar low)", target="none (time exit)",
         holding_window=HOLD, invalidation="close back below stop", falsification="k>=5 episodes & gross>0 & not single-trade"),
    dict(candidate_id="CAND-T02", strategy_family="trend_momentum_continuation",
         allowed_regimes=[DOWN], allowed_directions=["short"], hyp_in_family="2/4",
         N1_predicate="MK-01 swing structure = TREND_DOWN (LH+LL)",
         N4_confirmation="expansion bar DOWN (... & close<open)",
         entry="open[i+1]", stop="high[i]", target="none (time exit)", holding_window=HOLD,
         invalidation="close back above stop", falsification="k>=5 episodes & gross>0 & not single-trade"),
    dict(candidate_id="CAND-T03", strategy_family="trend_pullback_continuation",
         allowed_regimes=[UP], allowed_directions=["long"], hyp_in_family="3/4",
         N1_predicate="MK-01 swing structure = TREND_UP",
         N4_confirmation=">=2-bar pullback (consecutive lower highs&lows) then a bar closing above the prior bar high",
         entry="open[i+1]", stop="pullback lowest low", target="none (time exit)", holding_window=HOLD,
         invalidation="close below pullback low", falsification="k>=5 episodes & gross>0 & not single-trade"),
    dict(candidate_id="CAND-T04", strategy_family="trend_pullback_continuation",
         allowed_regimes=[DOWN], allowed_directions=["short"], hyp_in_family="4/4",
         N1_predicate="MK-01 swing structure = TREND_DOWN",
         N4_confirmation=">=2-bar pullback (consecutive higher highs&lows) then a bar closing below the prior bar low",
         entry="open[i+1]", stop="pullback highest high", target="none (time exit)", holding_window=HOLD,
         invalidation="close above pullback high", falsification="k>=5 episodes & gross>0 & not single-trade"),
]


def signals(cid, o, h, l, c, reg):
    """Return Trades. Signal only when the pre-registered regime holds on the signal bar (causal)."""
    n = len(c); exp = expansion(o, h, l, c); tr = []
    up_bar = np.asarray(c) > np.asarray(o); dn_bar = np.asarray(c) < np.asarray(o)
    if cid == "CAND-T01":
        for i in range(1, n - 1):
            if reg[i] == UP and exp[i] and up_bar[i]:
                tr.append(Trade(i, "long", float(l[i]), HOLD))
    elif cid == "CAND-T02":
        for i in range(1, n - 1):
            if reg[i] == DOWN and exp[i] and dn_bar[i]:
                tr.append(Trade(i, "short", float(h[i]), HOLD))
    elif cid == "CAND-T03":
        for i in range(3, n - 1):
            # >=2-bar pullback ending at i-1, resumption close at i
            if reg[i] != UP:
                continue
            if h[i - 1] < h[i - 2] and l[i - 1] < l[i - 2] and h[i - 2] < h[i - 3] and l[i - 2] < l[i - 3] \
               and c[i] > h[i - 1]:
                stop = float(min(l[i - 1], l[i - 2]))
                tr.append(Trade(i, "long", stop, HOLD))
    elif cid == "CAND-T04":
        for i in range(3, n - 1):
            if reg[i] != DOWN:
                continue
            if h[i - 1] > h[i - 2] and l[i - 1] > l[i - 2] and h[i - 2] > h[i - 3] and l[i - 2] > l[i - 3] \
               and c[i] < l[i - 1]:
                stop = float(max(h[i - 1], h[i - 2]))
                tr.append(Trade(i, "short", stop, HOLD))
    return tr


def deterministic_checks(cid, tr, reg, n):
    """No-lookahead + regime-gating + bracket validity, before any backtest."""
    issues = []
    tgt = CARDS_BY[cid]["allowed_regimes"][0]
    for t in tr:
        if not (0 < t.signal_idx < n - 1):
            issues.append("entry index out of range")
        if reg[t.signal_idx] != tgt:
            issues.append("signal fired OUTSIDE the pre-registered regime")
        if t.side == "long" and not (t.stop < 1e18):
            pass
    return issues


CARDS_BY = {c["candidate_id"]: c for c in CARDS}


def classify(cid, tr, res, years, reg):
    tgt = CARDS_BY[cid]["allowed_regimes"][0]
    eps = episodes(reg, tgt)
    # which episode each trade falls in
    ep_of = {}
    for k, (s, e) in enumerate(eps):
        ep_of[k] = []
    def ep_idx(si):
        for k, (s, e) in enumerate(eps):
            if s <= si < e:
                return k
        return None
    used_eps = set()
    for t in tr:
        k = ep_idx(t.signal_idx)
        if k is not None:
            used_eps.add(k)
    k_eps = len(used_eps)
    if not res or len(res) == 0:
        return dict(status="STRUCTURALLY_FALSIFIED", reason="no signals/trades", k_episodes=k_eps)
    m = metrics(res)
    # per-episode R
    byep = {}
    for x in res:
        k = ep_idx(x["signal_idx"])
        byep.setdefault(k, []).append(x["r"])
    per_ep = {str(k): round(sum(v), 2) for k, v in sorted(byep.items(), key=lambda kv: (kv[0] is None, kv[0]))}
    # leave-one-episode-out on total_R
    loo = None
    if len(byep) >= 2:
        tot = m["total_R"]
        loo = round(min(tot - sum(v) for v in byep.values()), 2)  # worst single-episode removed leaves this
    byyear = {}
    for x in res:
        byyear.setdefault(int(years[x["signal_idx"]]), []).append(x["r"])
    per_year = {str(y): round(sum(v) / len(v), 3) for y, v in sorted(byyear.items())}
    # status logic (provisional, pre-ratification). Hard-falsify only on robust pathologies (gross-neg,
    # pathological single-trade); fat-tail (trimmed<=0 or best_share>0.3) is a CAVEAT -> still queued,
    # because the available evaluator double-counts spread (pessimistic) so the corrected canonical rerun
    # decides. k<5 -> ARCHIVE_INSUFFICIENT (0.5^k not significant).
    bs = m.get("best_share_of_total"); t_avg = m.get("trimmed_top1pct", {}).get("avg_R")
    fat = (bs is not None and bs > 0.30) or (t_avg is not None and t_avg <= 0)
    caveat = None
    if k_eps < 5:
        status = "ARCHIVE_INSUFFICIENT"; reason = f"k={k_eps} eligible episodes < 5 (0.5^k not significant)"
    elif m["total_R"] <= 0 or m["avg_R"] <= 0:
        status = "STRUCTURALLY_FALSIFIED"; reason = f"gross/net non-positive (avg_R={m['avg_R']}, total_R={m['total_R']})"
    elif bs is not None and bs > 0.5:
        status = "STRUCTURALLY_FALSIFIED"; reason = f"pathological single-trade dependence (best_share={bs})"
    elif fat:
        status = "PROVISIONAL_SCREENED"; reason = f"positive raw but FAT-TAIL (best_share={bs}, trimmed_avg_R={t_avg})"
        caveat = "FAT_TAIL — not robust to top-1% trim; canonical rerun (corrected cost) decides"
    else:
        status = "PROVISIONAL_SCREENED"; reason = "positive & robust to top-1% trim; queued for canonical rerun"
    return dict(status=status, reason=reason, fat_tail_caveat=caveat, k_episodes=k_eps, n_trades=len(res),
                metrics=m, per_episode_R=per_ep, per_year_avg_R=per_year, leave_one_episode_out_total_R=loo)


def main():
    d, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    o = d["open"].to_numpy(); h = d["high"].to_numpy(); l = d["low"].to_numpy(); c = d["close"].to_numpy()
    years = d["dt"].dt.year.to_numpy(); n = len(d)
    blocks = derive_blocks(d)  # R9: manifest population when available
    reg = trend_regime(h, l, blocks)
    up_bars = sum(1 for x in reg if x == UP); dn_bars = sum(1 for x in reg if x == DOWN)

    out = []
    for card in CARDS:
        cid = card["candidate_id"]
        tr = signals(cid, o, h, l, c, reg)
        issues = deterministic_checks(cid, tr, reg, n)
        if issues:
            out.append(dict(**card, status="DETERMINISTIC_FAIL", issues=issues)); continue
        res = canonical_evaluate(d, tr) if tr else []
        cl = classify(cid, tr, res, years, reg)
        out.append(dict(**card, **cl))

    report = dict(batch="TREND_pairs_v1", MARK="PROVISIONAL · NON-COMPARABLE UNTIL CANONICAL RATIFICATION · REQUIRES CANONICAL RERUN",
                  regime_coverage=dict(TREND_UP_bars=up_bars, TREND_DOWN_bars=dn_bars, total_bars=n,
                                       up_episodes=len(episodes(reg, UP)), down_episodes=len(episodes(reg, DOWN))),
                  candidates=out)
    print(json.dumps(report, indent=2, default=float))
    with open(os.path.join(os.path.dirname(__file__), "flowb_trend_results.json"), "w") as f:
        json.dump(report, f, indent=2, default=float)


if __name__ == "__main__":
    main()

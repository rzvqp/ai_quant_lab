"""Mandate 4.1 -- transactional evaluation of E001/E002/E004 on the M15_v2 discovery half.

Runs the FROZEN V1 structural events (V1_OPERATIONALIZED_CONTRACTS.md) through the PATCHED §9.4.1
execution contract (ai_quant_lab statistician-foundation @ 3ef47b7). Nothing here optimizes, tunes, or
reformulates any V1 parameter; the execution layer (entry timing, stop, target, tie-break, cost) is taken
verbatim from the patched contract.

Data via the OFFICIAL loader v5 only (`_common.load`, which delivers the discovery half: union of
manifest discovery ranges, quarantine + sealed excluded, hash/status gated). M15_v2 discovery = 130,491
bars over 3 regimes (bear 2011-2015, bull 2015-2020, correction 2020-2022). The 4th regime (2022-2026
bull) is NOT in M15_v2's delivered discovery -- it is M15 legacy and SAME-WINDOW-RESAMPLED (the V1
parametrization window) -- so it is excluded from this confirmation run.

Reports per edge x regime x RR (no aggregation over regimes): winrate, expectancy in R, concentration on
NET (best/sumR, top-3, top-5), wo1, n trades, undetermined %. Family of 6 (3 edges x 2 RR at official
stop $4.00) with BH-FDR. $5.00 stop = sensitivity. Full worst/best tie-break bracket. Order-block family
(E010/E013/E015/E016) untouched.
"""
import json

import numpy as np
from scipy.stats import binom

from ._common import load, RESEARCH_HOLDOUT_CUTOFF_UTC

COST = 0.4                       # round-trip, points (§5)
STOPS = [4.0, 5.0]               # official 4.0 ; 5.0 sensitivity (§2)
RRS = [1, 2]                     # RR 1:1 and 1:2 (§3, patched: target = RR x stop)
FVG_FILL_HORIZON = 50            # E004 fill window (V1)

REGIMES = [                      # manifest v2.2.0 segment_ranges (M15_v2), CEO regime table
    ("bear_2011_2015",     1311697800, 1451602800, "-42.0%"),
    ("bull_2015_2020",     1451602800, 1596228300, "+86.3%"),
    ("corr_2020_2022",     1596228300, 1667259900, "-17.4%"),
]


# --------------------------------------------------------------------------- entry generation
def _asia_range(day_bars):
    a = day_bars[(day_bars["dt"].dt.hour < 8)]
    if len(a) < round(0.875 * 32):          # >=0.875 completeness of a 32-bar Asia window (V1)
        return None
    return float(a["low"].min()), float(a["high"].max())


def gen_E001(g):
    """Sweep of an Asia extreme in the London window; entry next bar after the sweep, INVERSE direction."""
    out = []
    for date, day in g.groupby(g["dt"].dt.date):
        ar = _asia_range(day)
        if ar is None:
            continue
        alow, ahigh = ar
        lon = day[(day["dt"].dt.hour >= 8) & (day["dt"].dt.hour < 13)]
        for _, b in lon.iterrows():
            atr = b["atr14"]
            if not (np.isfinite(atr) and atr > 0):
                continue
            up = b["high"] >= ahigh + 0.25 * atr
            dn = b["low"] <= alow - 0.25 * atr
            if up or dn:
                gi = int(b["gi"])
                if gi + 1 >= len(g):
                    break
                direction = -1 if up else 1          # INVERSE of the break (patched §1)
                out.append((gi + 1, direction))
                break                                # one entry per day
    return out


def gen_E002(g):
    """Aggressive Frankfurt move (|Δ|>=1.5xATR14@06:00); entry at the 08:00 bar, OPPOSITE the move."""
    out = []
    for date, day in g.groupby(g["dt"].dt.date):
        fk = day[(day["dt"].dt.hour >= 6) & (day["dt"].dt.hour < 8)].sort_values("time")
        if len(fk) < 6:                              # need a materially complete 2h window (8 bars)
            continue
        atr0 = fk.iloc[0]["atr14"]
        if not (np.isfinite(atr0) and atr0 > 0):
            continue
        delta = fk.iloc[-1]["close"] - fk.iloc[0]["open"]
        if abs(delta) < 1.5 * atr0:
            continue
        opn = day[(day["dt"].dt.hour == 8)].sort_values("time")   # first London (08:00) bar
        if len(opn) == 0:
            continue
        gi = int(opn.iloc[0]["gi"])
        direction = -1 if delta > 0 else 1           # OPPOSITE Frankfurt (patched §1)
        out.append((gi, direction))
    return out


def gen_E004(g):
    """First 3-bar FVG whose middle bar is in 13:30-15:30 UTC; entry next bar after formation, FVG
    polarity. Also returns the `fill` flag (price re-enters the zone within 50 bars)."""
    out = []
    hi = g["high"].values
    lo = g["low"].values
    hh = g["dt"].dt.hour.values
    mm = g["dt"].dt.minute.values
    for date, day in g.groupby(g["dt"].dt.date):
        idx = day["gi"].values
        found = False
        for k in idx:
            if k < 2 or found:
                continue
            mid = k - 1                              # middle bar of the 3-bar pattern
            t = hh[mid] * 60 + mm[mid]
            if not (13 * 60 + 30 <= t < 15 * 60 + 30):   # 13:30-15:30 UTC window (V1; DST caveat)
                continue
            bull = lo[k] > hi[k - 2]
            bear = hi[k] < lo[k - 2]
            if not (bull or bear):
                continue
            zlow, zhigh = (hi[k - 2], lo[k]) if bull else (lo[k - 2], hi[k])
            if k + 1 >= len(g):
                found = True
                continue
            direction = 1 if bull else -1
            end = min(k + 1 + FVG_FILL_HORIZON, len(g))
            fill = bool(((lo[k + 1:end] <= zhigh) & (hi[k + 1:end] >= zlow)).any())
            out.append((k + 1, direction, fill))
            found = True
    return out


# --------------------------------------------------------------------------- trade simulation
def simulate(o, h, l, entry_i, direction, S, RR):
    """Walk forward within the (contiguous, per-regime) arrays from the entry bar. Returns
    (outcome, R_worst, R_best, undetermined, timeout). Entry at open of entry_i; SL/TP bracket held until
    one is hit. Undetermined = the decisive bar touches BOTH levels (worst=stop-first, best=target-first)."""
    entry = o[entry_i]
    sl = entry - direction * S
    tp = entry + direction * RR * S
    r_win = (RR * S - COST) / S
    r_loss = -(S + COST) / S
    n = len(o)
    for k in range(entry_i, n):
        if direction > 0:
            hit_sl = l[k] <= sl
            hit_tp = h[k] >= tp
        else:
            hit_sl = h[k] >= sl
            hit_tp = l[k] <= tp
        if hit_sl and hit_tp:
            return ("undetermined", r_loss, r_win, True, False)
        if hit_tp:
            return ("win", r_win, r_win, False, False)
        if hit_sl:
            return ("loss", r_loss, r_loss, False, False)
    return ("timeout", 0.0, 0.0, False, True)


def _conc(rs):
    """Concentration on NET R. rs: list of per-trade net R (resolved). Returns best/sumR, top3, top5, wo1."""
    if not rs:
        return dict(n=0)
    a = np.sort(np.asarray(rs, float))[::-1]
    s = float(a.sum())
    d = dict(n=len(a), sumR=round(s, 3), mean_R=round(float(a.mean()), 4))
    if s > 0:
        d["best_over_sumR"] = round(float(a[0]) / s, 4)
        d["top3_over_sumR"] = round(float(a[:3].sum()) / s, 4)
        d["top5_over_sumR"] = round(float(a[:5].sum()) / s, 4)
        wo1 = s - float(a[0])
        d["wo1_sumR"] = round(wo1, 3)
        d["wo1_still_positive"] = bool(wo1 > 0)
    else:
        d["concentration"] = "N/A (net sumR <= 0)"
        d["wo1_sumR"] = round(s - float(a[0]), 3)
        d["wo1_still_positive"] = False
    return d


def evaluate(g, entries_fn, edge, is_e004=False):
    hh = {}
    o = g["open"].values; h = g["high"].values; l = g["low"].values
    ep = g["time"].values
    regime_of = np.full(len(g), None, dtype=object)
    for name, s, e, _ in REGIMES:
        regime_of[(ep >= s) & (ep < e)] = name
    fills = []
    ents = entries_fn(g)
    per = {}
    for name, _s, _e, _lbl in REGIMES:
        per[name] = {(S, RR): dict(win=0, loss=0, undet=0, timeout=0, R_worst=[], R_best=[])
                     for S in STOPS for RR in RRS}
    for ent in ents:
        if is_e004:
            entry_i, direction, fill = ent
            fills.append((regime_of[entry_i], fill))
        else:
            entry_i, direction = ent
        reg = regime_of[entry_i]
        if reg is None:
            continue
        for S in STOPS:
            for RR in RRS:
                outcome, rw, rb, undet, to = simulate(o, h, l, entry_i, direction, S, RR)
                c = per[reg][(S, RR)]
                if to:
                    c["timeout"] += 1
                    continue
                if undet:
                    c["undet"] += 1
                c["R_worst"].append(rw)
                c["R_best"].append(rb)
                if outcome == "win":
                    c["win"] += 1
                elif outcome == "loss":
                    c["loss"] += 1
                else:  # undetermined -> worst=loss for the win/loss tally
                    c["loss"] += 1
    hh["edge"] = edge
    hh["by_regime"] = {}
    for name, _s, _e, lbl in REGIMES:
        hh["by_regime"][name] = {"label": lbl, "cells": {}}
        for S in STOPS:
            for RR in RRS:
                c = per[name][(S, RR)]
                resolved = c["win"] + c["loss"]
                cell = dict(stop=S, RR=RR, n_resolved=resolved, timeouts=c["timeout"],
                            undetermined=c["undet"],
                            undet_pct=round(c["undet"] / resolved, 4) if resolved else None,
                            not_resolvable_at_m15=bool(resolved and c["undet"] / resolved > 0.25),
                            winrate=round(c["win"] / resolved, 4) if resolved else None,
                            expectancy_R_worst=round(float(np.mean(c["R_worst"])), 4) if c["R_worst"] else None,
                            expectancy_R_best=round(float(np.mean(c["R_best"])), 4) if c["R_best"] else None,
                            concentration_worst=_conc(c["R_worst"]))
                hh["by_regime"][name]["cells"][f"stop{S}_RR{RR}"] = cell
    if is_e004:
        fr = {}
        for name, _s, _e, _l in REGIMES:
            sub = [f for r, f in fills if r == name]
            fr[name] = dict(n=len(sub), fill_rate=round(float(np.mean(sub)), 4) if sub else None)
        hh["fill_by_regime"] = fr
    hh["_raw_per"] = per                                   # for pooled BH
    return hh


def bh_family(results):
    """Family of 6 = 3 edges x 2 RR at the official stop 4.0, pooled across regimes. One-sided binomial
    vs the cost-adjusted break-even winrate w* = (1 + COST/S)/(RR+1). BH-FDR at alpha=0.05."""
    S = 4.0
    fam = {}
    for edge, res in results.items():
        for RR in RRS:
            win = loss = 0
            for name, _s, _e, _l in REGIMES:
                c = res["_raw_per"][name][(S, RR)]
                win += c["win"]; loss += c["loss"]
            n = win + loss
            w_star = (1 + COST / S) / (RR + 1)
            p = float(binom.sf(win - 1, n, w_star)) if n > 0 else None   # P(X>=win) one-sided
            fam[f"{edge}_RR{RR}"] = dict(n=n, wins=win, breakeven_winrate=round(w_star, 4),
                                         winrate=round(win / n, 4) if n else None, p_one_sided=p)
    ps = [(k, v["p_one_sided"]) for k, v in fam.items() if v["p_one_sided"] is not None]
    ranked = sorted(ps, key=lambda kv: kv[1])
    m = len(fam)
    max_rank = 0
    for i, (k, pv) in enumerate(ranked, 1):
        if pv <= 0.05 * i / m:
            max_rank = i
    passing = set()
    for i, (k, pv) in enumerate(ranked, 1):
        fam[k]["bh_rank"] = i
        fam[k]["bh_crit"] = round(0.05 * i / m, 5)
        fam[k]["passes"] = i <= max_rank
        if i <= max_rank:
            passing.add(k)
    return dict(family_size=m, alpha=0.05, tests=fam, passing=sorted(passing))


def main():
    g, meta = load("M15_v2", data_split_id="mandate4.1_M15_v2_discovery", cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    g = g.reset_index(drop=True)
    g["gi"] = np.arange(len(g))
    results = {}
    results["E001"] = evaluate(g, gen_E001, "E001")
    results["E002"] = evaluate(g, gen_E002, "E002")
    results["E004"] = evaluate(g, gen_E004, "E004", is_e004=True)
    bh = bh_family(results)

    out = {"mandate": "4.1", "data": dict(tf="M15_v2", split="discovery",
                                          n_bars=meta["n_bars_delivered"],
                                          range=[meta["min_date_used"][:10], meta["max_date_used"][:10]],
                                          loader=meta["loader_version"], manifest=meta["manifest_version"]),
           "note_regime4": "2022-2026 bull (+223.3%) NOT in M15_v2 discovery; = M15 legacy = SAME-WINDOW-RESAMPLED; excluded from confirmation.",
           "results": {k: {kk: vv for kk, vv in v.items() if kk != "_raw_per"} for k, v in results.items()},
           "bh_family_6": bh}
    with open("mandate41_eval_results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)

    # console summary
    for edge in ["E001", "E002", "E004"]:
        print("=" * 90)
        print(edge, "| entries by regime (resolved n at stop4/RR2):")
        for name, _s, _e, lbl in REGIMES:
            cells = results[edge]["by_regime"][name]["cells"]
            c = cells["stop4.0_RR2"]
            c1 = cells["stop4.0_RR1"]
            print(f"  {name} ({lbl}): RR1[n={c1['n_resolved']} wr={c1['winrate']} E={c1['expectancy_R_worst']}] "
                  f"RR2[n={c['n_resolved']} wr={c['winrate']} E={c['expectancy_R_worst']} undet%={c['undet_pct']} "
                  f"best/sumR={c['concentration_worst'].get('best_over_sumR')} wo1+={c['concentration_worst'].get('wo1_still_positive')}]")
        if edge == "E004":
            print("  fill_by_regime:", {k: v["fill_rate"] for k, v in results[edge]["fill_by_regime"].items()})
    print("=" * 90)
    print("BH family of 6 (stop 4.0, pooled across regimes):")
    for k, v in bh["tests"].items():
        print(f"  {k}: n={v['n']} wr={v['winrate']} vs breakeven {v['breakeven_winrate']} p={v['p_one_sided']:.4g} "
              f"bh_crit={v.get('bh_crit')} PASS={v.get('passes')}")
    print("PASSING:", bh["passing"] if bh["passing"] else "NONE")


if __name__ == "__main__":
    main()

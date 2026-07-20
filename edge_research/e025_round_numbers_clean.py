"""E025 -- Round Numbers -- CLEAN RERUN (holdout-excluded), 2026-07-21.

Remediation of the TERMINAL HOLDOUT BREACH incident (PROJECT_STATE_v2.md SS8.23,
EDGE_RESEARCH_PROTOCOL.md SS8). The original contaminated pass is `e025_round_numbers.py` /
`e025_round_numbers_results.json` -- both preserved UNCHANGED as the audit trail. This file is a
byte-identical copy of the original's own METHOD (same COOLDOWN, N windows, granularities,
detect_events/compare logic -- nothing tuned, nothing added, nothing removed) with exactly one
substantive change: data now loads through `_common.load()`'s mandatory holdout-cutoff enforcement
instead of the old unfiltered `load("M15")` call. Do not edit the method below to chase a different
result -- if the method needs to change, that is a new, separately-versioned edge, not a "clean rerun."

V0 hypothesis (frozen, verbatim, unchanged from the original pass): "Price reacts (as support/
resistance/magnet) at round psychological levels (e.g. multiples of $10/$50/$100)."
"""
import json
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from _common import load, vol_regime, summarize, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID

COOLDOWN = 8
NS = [4, 16]
GRANS = [10, 50, 100]


def detect_events(d: pd.DataFrame, g: float, offset: float) -> pd.DataFrame:
    low = d["low"].values
    high = d["high"].values
    close = d["close"].values
    n = len(d)
    lvl = np.floor((high - offset) / g) * g + offset
    touch = lvl >= (low - 1e-9)
    level_id = np.round((lvl - offset) / g).astype("int64")

    last_kept = {}
    ev_idx = []
    for i in range(1, n - max(NS) - 1):
        if not touch[i]:
            continue
        li = level_id[i]
        if li in last_kept and (i - last_kept[li]) < COOLDOWN:
            continue
        last_kept[li] = i
        ev_idx.append(i)
    ev_idx = np.array(ev_idx, dtype=int)
    if len(ev_idx) == 0:
        return pd.DataFrame()

    events = pd.DataFrame({"i": ev_idx, "level": lvl[ev_idx]})
    events["direction"] = np.where(close[ev_idx - 1] < events["level"].values, 1, -1)
    events["session"] = d["session"].values[ev_idx]
    events["dow"] = d["dow"].values[ev_idx]
    events["vol_regime"] = d["vol_regime"].values[ev_idx]
    atr_e = d["atr14"].values[ev_idx]
    events["atr_valid"] = np.isfinite(atr_e) & (atr_e > 0)
    for N in NS:
        fut = close[ev_idx + N]
        with np.errstate(invalid="ignore", divide="ignore"):
            reaction = -events["direction"].values * (fut - events["level"].values) / atr_e
        reaction[~events["atr_valid"].values] = np.nan
        events[f"reaction_{N}"] = reaction
    events = events[events["atr_valid"]].drop(columns=["atr_valid"])
    return events.reset_index(drop=True)


def compare(round_ev, ctrl_ev, col):
    r = round_ev[col].dropna().values
    c = ctrl_ev[col].dropna().values
    out = dict(round=summarize(r), control=summarize(c))
    if len(r) > 20 and len(c) > 20:
        u, p = mannwhitneyu(r, c, alternative="two-sided")
        out["mannwhitney_p"] = float(p)
        out["diff_of_means"] = out["round"]["mean"] - out["control"]["mean"]
    return out


def main():
    d, meta = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    d["vol_regime"] = vol_regime(d)
    results = {"edge": "E025", "run_id": "clean_rerun_2026-07-21",
               "supersedes_contaminated_artifact": "e025_round_numbers_results.json",
               "split_metadata": meta,
               "n_bars": int(len(d)),
               "price_range": [float(d["low"].min()), float(d["high"].max())],
               "date_range": [str(d["dt"].iloc[0]), str(d["dt"].iloc[-1])],
               "by_granularity": {}}

    for g in GRANS:
        round_ev = detect_events(d, g, 0.0)
        ctrl_ev = detect_events(d, g, g / 2.0)
        gkey = f"g{g}"
        results["by_granularity"][gkey] = {
            "n_round_events": int(len(round_ev)), "n_control_events": int(len(ctrl_ev)),
            "overall": {f"reaction_{N}": compare(round_ev, ctrl_ev, f"reaction_{N}") for N in NS},
        }
        col = "reaction_16"
        slices = {}
        for direction, label in [(1, "approach_from_below"), (-1, "approach_from_above")]:
            slices[label] = compare(round_ev[round_ev.direction == direction],
                                     ctrl_ev[ctrl_ev.direction == direction], col)
        for sess in ["asia", "london", "ny", "late"]:
            slices[f"session_{sess}"] = compare(round_ev[round_ev.session == sess],
                                                 ctrl_ev[ctrl_ev.session == sess], col)
        for vr in ["low", "mid", "high"]:
            slices[f"vol_{vr}"] = compare(round_ev[round_ev.vol_regime == vr],
                                           ctrl_ev[ctrl_ev.vol_regime == vr], col)
        for dow in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            slices[f"dow_{dow}"] = compare(round_ev[round_ev.dow == dow],
                                            ctrl_ev[ctrl_ev.dow == dow], col)
        results["by_granularity"][gkey]["slices"] = slices

    with open("e025_round_numbers_clean_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(json.dumps({g: results["by_granularity"][g]["overall"] for g in results["by_granularity"]},
                      indent=2, default=str))
    print("split_metadata", json.dumps(meta, indent=2, default=str))
    for g in GRANS:
        gk = f"g{g}"
        print(gk, "n_round", results["by_granularity"][gk]["n_round_events"],
              "n_control", results["by_granularity"][gk]["n_control_events"])


if __name__ == "__main__":
    main()

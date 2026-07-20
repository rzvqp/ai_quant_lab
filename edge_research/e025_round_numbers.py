"""E025 -- Round Numbers -- Discovery-stage analysis (Flow A, Alpha Discovery Laboratory).

V0 hypothesis (frozen, verbatim from EDGE_DISCOVERY_REGISTRY_v1.md, never edited):
"Price reacts (as support/resistance/magnet) at round psychological levels (e.g. multiples of
$10/$50/$100)."

Method (disclosed, exploratory -- Discovery stage only, no tuning/optimization):
1. For each granularity g in {10, 50, 100}, define ROUND levels = multiples of g, and a matched
   CONTROL level set = round levels shifted by g/2 (same density, same price range, deliberately
   non-round).
2. Detect a "touch" on an M15 bar as: floor(high/g)*g >= low (the largest multiple of g at or
   below the bar's high is still >= the bar's low, i.e. the bar's [low,high] range spans a
   multiple of g). Same construction for control levels (offset grid).
3. Merge repeated touches of the SAME level into one independent event only if at least
   `COOLDOWN`=8 bars (2h) have passed since the last kept event on that level (reduces
   pseudo-replication from chop/whipsaw around one level).
4. Approach direction dir = +1 if price was below the level the bar before the touch (rising into
   it), -1 if above (falling into it).
5. Reaction, measured N bars later (N in {4 (~1h), 16 (~4h)}):
   reaction_magnitude = -dir * (close[event+N] - level) / ATR14[event]
   Positive = price reversed AWAY from the level (round level acted as support/resistance).
   Negative = price continued THROUGH the level in the approach direction (level acted as no
   barrier / was a magnet through which price passed).
6. Round vs control is compared via bootstrap mean + 95% CI and a Mann-Whitney U test (two-sided,
   distribution-free -- appropriate given this project's own established finding, PROJECT_AUDIT.md
   D1, that R-like outcome variables here are heavy-tailed and analytic normal-approx tests are
   unreliable).

No filter/parameter above was chosen by looking at the outcome first (N and COOLDOWN are the
literal, disclosed defaults; no search was run over them for this Discovery pass).
"""
import json
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from _common import load, vol_regime, summarize

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
    d = load("M15")
    d["vol_regime"] = vol_regime(d)
    results = {"edge": "E025", "n_bars": int(len(d)),
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
        # slices, using the N=16 (~4h) reaction as primary per-slice metric
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

    with open("e025_round_numbers_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(json.dumps({g: results["by_granularity"][g]["overall"] for g in results["by_granularity"]},
                      indent=2, default=str))
    print("n_bars", results["n_bars"], "date_range", results["date_range"])
    for g in GRANS:
        gk = f"g{g}"
        print(gk, "n_round", results["by_granularity"][gk]["n_round_events"],
              "n_control", results["by_granularity"][gk]["n_control_events"])


if __name__ == "__main__":
    main()

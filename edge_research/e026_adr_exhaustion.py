"""E026 -- ADR Exhaustion -- Discovery-stage analysis (Flow A, Alpha Discovery Laboratory).

V0 (frozen, verbatim): "Once price has moved a large fraction of its Average Daily Range, further
continuation in the same direction becomes statistically less likely for the remainder of the
session."

Method (disclosed):
- ADR_prior = rolling 14-day mean of D1 (high-low), available strictly BEFORE the day it applies to
  (shifted 1 day -- lookahead-safe: today's ADR budget is based on the trailing 14 CLOSED days).
- Per calendar day (UTC), per M15 bar t within the day: consumed_up_t = (running_high_t - day_open) /
  ADR_prior; consumed_down_t = (day_open - running_low_t) / ADR_prior.
- For each of a set of thresholds, find the FIRST bar in the day where consumed_up_t (resp.
  consumed_down_t) crosses the threshold -- one event per day per threshold per direction (avoids
  massive within-day autocorrelation from sampling every bar).
- At that event bar, continuation_t = max(0, future_extreme_from_t_to_day_end - running_extreme_t) /
  ADR_prior -- how much FURTHER the day's range extended in the SAME direction after this point,
  already in ADR units, >=0 by construction.
- Hypothesis predicts continuation should DECREASE as the crossed threshold increases (mean reversion
  after large ADR consumption). Tested via per-threshold-bucket means + a Spearman correlation between
  threshold and continuation, plus a low-vs-high-threshold Mann-Whitney split.
"""
import json
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr
from _common import load, summarize

THRESH = [0.3, 0.5, 0.7, 0.9, 1.1, 1.3]


def build():
    d1 = load("D1")
    d1["rng"] = d1["high"] - d1["low"]
    d1["adr14"] = d1["rng"].rolling(14).mean().shift(1)
    d1["date"] = d1["dt"].dt.date

    m = load("M15")
    m["date"] = m["dt"].dt.date
    m = m.merge(d1[["date", "adr14"]], on="date", how="left")
    m["dow"] = m["dt"].dt.day_name()
    return m


def events_for_direction(m, direction):
    """direction: 'up' or 'down'. Returns df of one row per (day, threshold) event."""
    out = []
    for date, g in m.groupby("date"):
        g = g.reset_index(drop=True)
        adr = g["adr14"].iloc[0]
        if not np.isfinite(adr) or adr <= 0 or len(g) < 4:
            continue
        day_open = g["open"].iloc[0]
        if direction == "up":
            running = g["high"].cummax()
            consumed = (running - day_open) / adr
        else:
            running = g["low"].cummin()
            consumed = (day_open - running) / adr
        for th in THRESH:
            hit = np.where(consumed.values >= th)[0]
            if len(hit) == 0:
                continue
            i = hit[0]
            if i >= len(g) - 2:
                continue
            if direction == "up":
                future_extreme = g["high"].iloc[i:].max()
                cont = max(0.0, future_extreme - running.iloc[i]) / adr
            else:
                future_extreme = g["low"].iloc[i:].min()
                cont = max(0.0, running.iloc[i] - future_extreme) / adr
            out.append(dict(date=date, threshold=th, dow=g["dow"].iloc[i],
                             session=g["session"].iloc[i], continuation=cont,
                             continued_meaningfully=int(cont > 0.1)))
    return pd.DataFrame(out)


def main():
    m = build()
    results = {"edge": "E026", "n_bars": int(len(m)),
               "date_range": [str(m["dt"].iloc[0]), str(m["dt"].iloc[-1])],
               "n_days": int(m["date"].nunique()), "by_direction": {}}

    for direction in ["up", "down"]:
        ev = events_for_direction(m, direction)
        by_th = {}
        for th in THRESH:
            sub = ev[ev.threshold == th]["continuation"].values
            rate = ev[ev.threshold == th]["continued_meaningfully"].mean() if len(sub) else np.nan
            by_th[str(th)] = dict(summarize(sub), continuation_rate=float(rate) if np.isfinite(rate) else None)
        low = ev[ev.threshold <= 0.5]["continuation"].values
        high = ev[ev.threshold >= 1.1]["continuation"].values
        mw = mannwhitneyu(low, high, alternative="two-sided") if len(low) > 20 and len(high) > 20 else (None, None)
        sp = spearmanr(ev["threshold"], ev["continuation"]) if len(ev) > 20 else (None, None)
        results["by_direction"][direction] = dict(
            n_events=int(len(ev)), by_threshold=by_th,
            low_vs_high_mannwhitney_p=float(mw[1]) if mw[1] is not None else None,
            low_mean=float(low.mean()) if len(low) else None,
            high_mean=float(high.mean()) if len(high) else None,
            spearman_r=float(sp[0]) if sp[0] is not None else None,
            spearman_p=float(sp[1]) if sp[1] is not None else None,
        )
        ev.to_csv(f"e026_events_{direction}.csv", index=False)

    with open("e026_adr_exhaustion_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()

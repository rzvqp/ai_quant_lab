"""E026 -- ADR Exhaustion -- CLEAN RERUN (holdout-excluded), 2026-07-21.

Remediation of the TERMINAL HOLDOUT BREACH incident (PROJECT_STATE_v2.md SS8.23,
EDGE_RESEARCH_PROTOCOL.md SS8). The original contaminated pass is `e026_adr_exhaustion.py` /
`e026_adr_exhaustion_results.json` / `e026_events_{up,down}.csv` -- all preserved UNCHANGED as the
audit trail. This file is the same METHOD (same THRESH list, same event/continuation construction --
nothing tuned) with exactly one substantive change: both D1 and M15 now load through `_common.load()`'s
mandatory holdout-cutoff enforcement instead of the old unfiltered `load(tf)` calls.

V0 hypothesis (frozen, verbatim, unchanged): "Once price has moved a large fraction of its Average
Daily Range, further continuation in the same direction becomes statistically less likely for the
remainder of the session."
"""
import json
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr
from _common import load, summarize, RESEARCH_HOLDOUT_CUTOFF_UTC, PRE_HOLDOUT_SPLIT_ID

THRESH = [0.3, 0.5, 0.7, 0.9, 1.1, 1.3]


def build():
    d1, meta_d1 = load("D1", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    d1["rng"] = d1["high"] - d1["low"]
    d1["adr14"] = d1["rng"].rolling(14).mean().shift(1)
    d1["date"] = d1["dt"].dt.date

    m, meta_m15 = load("M15", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    m["date"] = m["dt"].dt.date
    m = m.merge(d1[["date", "adr14"]], on="date", how="left")
    m["dow"] = m["dt"].dt.day_name()
    return m, dict(D1=meta_d1, M15=meta_m15)


def events_for_direction(m, direction):
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
    m, split_meta = build()
    results = {"edge": "E026", "run_id": "clean_rerun_2026-07-21",
               "supersedes_contaminated_artifact": "e026_adr_exhaustion_results.json",
               "split_metadata": split_meta,
               "n_bars": int(len(m)),
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
        ev.to_csv(f"e026_events_{direction}_clean.csv", index=False)

    with open("e026_adr_exhaustion_clean_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()

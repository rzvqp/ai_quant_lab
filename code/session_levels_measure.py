"""Măsurători pentru nivelurile de sesiune (v2.7.39). READ-ONLY, fără P&L, GARD 1/2 neatinse. Descoperirea M15_v2.

1) FRECVENȚA DE STRADDLE — ceasul de sesiune (ore UTC) și ancora de zi (17:00 NY) nu se aliniază: câte sesiuni
   traversează o graniță de zi. Se MĂSOARĂ, nu se presupune.
2) PRECONDIȚIA DURĂ (primitiva B, persistentă): câte niveluri sunt ACTIVE simultan (distribuție/max) — volumul
   mare fără filtru e tiparul care pierde cel mai mult.
3) VERIFICARE PROGRAM OANDA vs MT5 — observația AI Trader: programul diferă ~3h. Pauza zilnică OANDA ≈20:45-22:00
   UTC; MT5 începe weekendul la 23:45. Detectez pauza reală din date și raportez discrepanța de aliniere.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT, os.path.join(_ROOT, "edge_research")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from edge_research._common import PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC, load
import split_manifest as SM  # type: ignore[import-not-found]
from market_structure import Block
from institutional_levels import _runs
from session_levels import (compute_persistent_session_levels, count_active_persistent_levels,
                            derive_session_index, detect_session_level_touches, detect_session_mid_touches,
                            session_labels)

REGIMES = ["bear", "bull", "correction"]
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}


def _day_index(time: Any) -> np.ndarray:
    dt = pd.to_datetime(time, unit="s", utc=True)
    ny = dt.dt.tz_convert("America/New_York").dt.tz_localize(None)
    d = (ny - pd.Timedelta(hours=17)).dt.floor("D").values.astype("datetime64[D]").astype("int64")
    return np.asarray(d, dtype=np.int64)


def _dist(a: list[int]) -> dict[str, Any]:
    if not a:
        return {}
    arr = np.asarray(a)
    return dict(n=len(a), min=int(arr.min()), median=float(np.percentile(arr, 50)),
                p90=float(np.percentile(arr, 90)), max=int(arr.max()), mean=round(float(arr.mean()), 2))


def main() -> int:
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | M15={len(dfm)}")
    if len(dfm) != 130_491:
        print(f"STOP: M15 {len(dfm)}."); return 2
    dfm = dfm.sort_values("time").reset_index(drop=True)
    t_all = dfm["time"].to_numpy()
    segs = [s for s in SM.load_manifest()["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]

    out: dict[str, Any] = {"regimes": {}}
    tot_sessions = tot_straddle = 0
    active_all: list[int] = []
    for i, seg in enumerate(segs):
        label = REGIMES[i]
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        h = sub["high"].tolist(); l = sub["low"].tolist(); tm = [int(x) for x in sub["time"].tolist()]
        sidx = derive_session_index(tm); slab = session_labels(tm)
        day = _day_index(sub["time"])

        # (1) straddle: sesiune care traversează o graniță de zi (17:00 NY)
        sessions = _runs(sidx, 0, n)
        straddle = sum(1 for (p0, p1) in sessions if day[p0] != day[p1])
        # (2) precondiție: niveluri persistente active simultan
        plevels = compute_persistent_session_levels(h, l, sidx, slab, [Block(0, n)])
        ptouch = list(detect_session_level_touches(h, l, plevels)) + list(detect_session_mid_touches(h, l, plevels))
        active = count_active_persistent_levels(plevels, ptouch, n)
        active_all.extend(active)

        out["regimes"][label] = {
            "n_bars": n, "sessions": len(sessions), "straddle_sessions": straddle,
            "straddle_fraction": round(straddle / len(sessions), 4) if sessions else None,
            "persistent_levels_total": len(plevels), "active_simultaneous": _dist(active)}
        tot_sessions += len(sessions); tot_straddle += straddle
        sfrac = 100.0 * straddle / len(sessions) if sessions else 0.0
        print(f"\n=== {label.upper()} ({n} bare) ===")
        print(f"  sesiuni={len(sessions)} | straddle graniță-zi={straddle} ({sfrac:.2f}%)")
        print(f"  primitiva B: {len(plevels)} niveluri; ACTIVE simultan {_dist(active)}")

    # (3) verificare program OANDA vs MT5 — pauza zilnică observată
    diffs = np.diff(t_all)
    gap_pos = np.where(diffs > 900)[0]                          # tranziții cu gol > o bară M15
    hours = pd.to_datetime(t_all[gap_pos], unit="s", utc=True).hour
    gsecs = diffs[gap_pos]
    daily = gap_pos[(gsecs > 900) & (gsecs <= 3 * 3600)]        # goluri „zilnice" (<=3h), excludem weekendul (>3h)
    daily_hours = Counter(int(x) for x in pd.to_datetime(t_all[daily], unit="s", utc=True).hour)
    weekend = gap_pos[gsecs > 3 * 3600]
    wk_hours = Counter(int(x) for x in pd.to_datetime(t_all[weekend], unit="s", utc=True).hour)

    out["straddle_aggregate"] = {"sessions": tot_sessions, "straddle": tot_straddle,
                                 "fraction": round(tot_straddle / tot_sessions, 4) if tot_sessions else None}
    out["active_aggregate"] = _dist(active_all)
    out["schedule_check"] = {
        "note": "ceasul de sesiune = ore UTC fixe (session_of); pauza OANDA reală detectată din date",
        "daily_gap_start_hour_utc_counts": dict(sorted(daily_hours.items())),
        "weekend_gap_start_hour_utc_counts": dict(sorted(wk_hours.items())),
        "mt5_reference": "OANDA pauză ≈20:45-22:00 UTC; MT5 weekend la 23:45 → aliniere backtest↔live poate diferi ~3h"}
    print(f"\n########## AGREGAT ##########")
    print(f"  straddle graniță-zi: {tot_straddle}/{tot_sessions} = "
          f"{100.0 * tot_straddle / tot_sessions:.2f}% din sesiuni")
    print(f"  niveluri B active simultan (agregat): {_dist(active_all)}")
    print(f"\n########## PROGRAM OANDA (pauza zilnică, ora UTC a barei ÎNAINTE de gol) ##########")
    print(f"  goluri ZILNICE (<=3h) pe oră UTC: {dict(sorted(daily_hours.items()))}")
    print(f"  goluri WEEKEND (>3h) pe oră UTC: {dict(sorted(wk_hours.items()))}")
    print(f"  ⚠ MT5 diferă ~3h (weekend 23:45 vs OANDA ≈20:45-22:00) → sesiunile din ore UTC fixe se pot alinia diferit live")

    path = os.path.join(_ROOT, "reports", "session_levels_measure_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/session_levels_measure_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

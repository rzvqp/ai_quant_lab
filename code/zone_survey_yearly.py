"""Cele 9 tipuri (PWH/PWL exclus, n=6) — caracterizare descriptivă pe AN CALENDARISTIC. Mandat 2026-07-30.

READ-ONLY date, in-sample, M15_v2. Contract OBDZ-002 NEMODIFICAT (SL/TP1/TP2/podea 1,0/2,0/3,0/0,60×ATR14[t],
entry t+1, orizont min(entry+20,EOD), ieșire parțială 75/25, cost 0,20). ACEEAȘI populație ca „fișele medicale"
(v2.7.29) — prima atingere aliniată la bias, REUTILIZATĂ prin import (SOURCES/Ctx), nu recalculată; metricile
prin `_cell` importat (identice cu fișele medicale).

STRATIFICARE: per AN CALENDARISTIC (UTC) al barei-declanșator t (=entry−1), din datele de descoperire.
  Per celulă an×tip: n, winrate, expectancy R & $, edge brut $, net total R & $. Sub n=25/an → statistici
  SUPRIMATE complet, doar n (regula celulei mici, ca la fișe).
PER TIP: câți ani sunt POZITIVI (expectancy_$ > 0) din câți au n>=25.
PRAG DE CONSISTENȚĂ (fixat de CEO acum): un mecanism e CANDIDAT dacă e pozitiv în CEL PUȚIN 12 dintre anii cu
  n>=25. Sub 12 → NU. (Datele acoperă 2011–2022 = 12 ani calendaristici; pragul cere efectiv pozitivitate în toți.)

FĂRĂ p-value, FĂRĂ verdict. Nicio celulă nu e dovadă. Anii cu vârfuri mari și restul zero se raportează CA ATARE,
nu se mediază. PWH/PWL EXCLUS. NU consumă familia (descriptiv, fără test). GARD 1 ridicat EXCLUSIV pentru rulare,
coborât imediat după. GARD 2 neatins, sigilat intact. JSON necomis. NU interpretez.
"""

from __future__ import annotations

import json
import os
import sys
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
from institutional_levels import derive_week_index
from obdz001 import HORIZON, _eod_per_bar
from partial_exit import simulate_partial_exit
from zone_survey_three_arm import SOURCES, Ctx, _day_index, _htf_trend, _regime_label, src_bpr
from zone_survey_execution import SL_M, TP1_M, TP2_M, COST, N_MIN, Trade, _cell

REGIMES = ["bear", "bull", "correction"]
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}
EXCLUDE = {"PWH_PWL"}
CONSISTENCY_MIN_YEARS = 12


def main() -> int:
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh1, _ = load("H1_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh4, _ = load("H4_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | M15={len(dfm)} | contract OBDZ-002 | strat=AN calendaristic | prag consistență>={CONSISTENCY_MIN_YEARS}")
    if len(dfm) != 130_491:
        print(f"STOP: M15 {len(dfm)}."); return 2
    dfm = dfm.sort_values("time").reset_index(drop=True)
    for name, dfh, per in (("h1", dfh1, 3600), ("h4", dfh4, 4 * 3600)):
        htf = _htf_trend(dfh, per).sort_values("avail")
        dfm = pd.merge_asof(dfm, htf.rename(columns={"trend_up": name}), left_on="time", right_on="avail",
                            direction="backward").drop(columns="avail")
    dfm["day"] = _day_index(dfm["time"])
    t_all = dfm["time"].to_numpy()
    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]

    names = [nm for (_w, nm, _f) in SOURCES if nm not in EXCLUDE]
    # per tip: {an -> list[Trade]}
    by_type_year: dict[str, dict[int, list[Trade]]] = {nm: {} for nm in names}

    for ri, seg in enumerate(segs):
        rshort = REGIMES[ri]
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(rshort) not in (None, len(sub)):
            print(f"STOP: {rshort} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        tm = [int(x) for x in sub["time"].tolist()]
        atr = sub["atr14"].to_numpy(); h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy(); day = sub["day"].to_numpy()
        year_arr = pd.to_datetime(sub["time"], unit="s", utc=True).dt.year.to_numpy()   # anul UTC per bară
        bias_up = (h1 > 0.5) & (h4 > 0.5)
        bias_dn = (h1 <= 0.5) & (h4 <= 0.5) & np.isfinite(h1) & np.isfinite(h4)
        week = derive_week_index(day.tolist())
        ctx = Ctx(o, h, l, c, tm, atr, bias_up, bias_dn, day, week, n)
        eod = _eod_per_bar(day.tolist(), n)

        for (_w, nm, fn) in SOURCES:
            if nm in EXCLUDE:
                continue
            if nm == "BPR":
                events = []
                for tol in (0.0, 0.10, 0.25):
                    events = src_bpr(ctx, tol)
                    if len(events) >= 25:
                        break
            else:
                events = fn(ctx)
            for (entry, d, a, ep) in events:
                if d > 0:
                    sl, tp1, tp2 = ep - SL_M * a, ep + TP1_M * a, ep + TP2_M * a
                else:
                    sl, tp1, tp2 = ep + SL_M * a, ep - TP1_M * a, ep - TP2_M * a
                res = simulate_partial_exit(entry, d, ep, sl, tp1, tp2, h, l, c, horizon=HORIZON,
                                            day_end_idx=int(eod[entry]), cost=COST)
                yr = int(year_arr[entry - 1])                    # anul barei-declanșator
                pol = "demand" if d > 0 else "supply"
                by_type_year[nm].setdefault(yr, []).append(
                    Trade(rshort, "", pol, res.net_R, res.net_R * (SL_M * a), res.exit_reason))

    all_years = sorted({y for nm in names for y in by_type_year[nm]})
    out: dict[str, Any] = {"contract": "OBDZ-002", "N_MIN": N_MIN, "consistency_min_years": CONSISTENCY_MIN_YEARS,
                           "year_anchor": "trigger bar t (UTC year)", "years": all_years, "types": {}}
    print(f"\nani calendaristici prezenți: {all_years}\n")
    for (wave, nm, _f) in SOURCES:
        if nm in EXCLUDE:
            continue
        cells: dict[str, Any] = {}
        eligible = 0; positive = 0
        line: list[str] = []
        for y in all_years:
            cell = _cell(by_type_year[nm].get(y, []))
            cells[str(y)] = cell
            if cell.get("INSUFFICIENT_N") or "winrate" not in cell:
                line.append(f"{y}:n{cell['n']}·—")
            else:
                eligible += 1
                pos = cell["expectancy_dollars"] > 0
                if pos:
                    positive += 1
                line.append(f"{y}:n{cell['n']} E$={cell['expectancy_dollars']:+.3f}{'+' if pos else ' '}")
        candidate = positive >= CONSISTENCY_MIN_YEARS
        out["types"][nm] = {"wave": wave, "cells": cells, "eligible_years": eligible,
                            "positive_years": positive, "candidate_consistency": candidate}
        print(f"[{wave}] {nm}")
        print("   " + "  ".join(line))
        print(f"   → pozitivi {positive}/{eligible} ani cu n>=25  |  CANDIDAT(>= {CONSISTENCY_MIN_YEARS}): "
              f"{'DA' if candidate else 'NU'}\n")

    path = os.path.join(_ROOT, "reports", "zone_survey_yearly_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("record -> reports/zone_survey_yearly_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

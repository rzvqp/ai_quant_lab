"""Cele 10 tipuri — RULARE ca tranzacții, contract OBDZ-002 ("fișele medicale"). Statistician v2.7.29 (3a88343).

In-sample, M15_v2. Contract OBDZ-002 NEMODIFICAT: SL=1,0×/TP1=2,0×/TP2=3,0×/podea=0,60× ATR14[t], entry=t+1
(fără confirmare), orizont=min(entry+20,EOD), ieșire parțială 75/25 cu breakeven, cost 0,20. Declanșator =
PRIMA ATINGERE aliniată la bias per convenția înghețată a fiecărui tip — ACEEAȘI populație ca survey-ul
MFE/MAE (v2.7.27), REUTILIZATĂ prin import din `zone_survey_three_arm` (SOURCES/Ctx), nu recalculată.

STRATIFICARE (22 celule/tip): 1 agregat + 3 regim + 4 sesiune + 12 regim×sesiune + 2 polaritate.
  Sesiunea unei tranzacții = `market_state.session_of(time[t])` la bara-declanșator t (=entry−1, unde
  ancorează ATR14[t] și setup-ul). ⚠ DISCLOSURE: sesiune atribuită pe bara-declanșator, nu pe entry.
REGULA CELULEI MICI (v2.7.29): sub n=25, TOATE statisticile se SUPRIMĂ complet (nu se marchează) — se
  raportează DOAR n + eticheta INSUFFICIENT_N. O cifră flatantă pe puține tranzacții arată identic cu una reală.
RAPORT/celulă (n>=25): winrate, expectancy R & $, edge brut $, net total R & $, best/sumR, wo1, conv TP1→TP2.
FĂRĂ p-value. Caracterizare DESCRIPTIVĂ. NICIO celulă nu e dovadă de edge (necesită pre-înregistrare separată,
consumatoare de familie). NU consumă familia (=12, fixat v2.7.19). Pe valuri (wave1→2→3). NU interpretez.

GARD 1 ridicat EXCLUSIV pentru rulare, coborât imediat după. GARD 2 neatins, sigilat intact. JSON necomis.
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
from market_state import session_of
from obdz001 import HORIZON, _eod_per_bar
from partial_exit import simulate_partial_exit
from zone_survey_three_arm import SOURCES, Ctx, _day_index, _htf_trend, _regime_label, src_bpr

SL_M, TP1_M, TP2_M, FLOOR, COST = 1.0, 2.0, 3.0, 0.60, 0.20
N_MIN = 25
REGIMES = ["bear", "bull", "correction"]
SESSIONS = ["asia", "london", "ny", "late"]
POLARITIES = ["demand", "supply"]
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}


class Trade:
    __slots__ = ("regime", "session", "pol", "net_R", "net_d", "reason")

    def __init__(self, regime: str, session: str, pol: str, net_R: float, net_d: float, reason: str) -> None:
        self.regime = regime; self.session = session; self.pol = pol
        self.net_R = net_R; self.net_d = net_d; self.reason = reason


def _cell(trades: list[Trade]) -> dict[str, Any]:
    """Metricile unei celule; SUPRIMATE integral dacă n<25 (doar n + INSUFFICIENT_N)."""
    n = len(trades)
    if n < N_MIN:
        return {"n": n, "INSUFFICIENT_N": True}
    nr = np.asarray([t.net_R for t in trades]); nd = np.asarray([t.net_d for t in trades])
    srt = np.sort(nr)[::-1]; sumR = float(nr.sum())
    reasons: dict[str, int] = {}
    for t in trades:
        reasons[t.reason] = reasons.get(t.reason, 0) + 1
    reach1 = reasons.get("tp1_then_tp2", 0) + reasons.get("tp1_then_breakeven", 0) + reasons.get("tp1_then_timeout", 0)
    reach2 = reasons.get("tp1_then_tp2", 0)
    return {
        "n": n, "winrate": round(float((nr > 0).mean()), 4),
        "expectancy_R": round(float(nr.mean()), 5), "expectancy_dollars": round(float(nd.mean()), 5),
        "edge_brut_dollars": round(float(nd.mean()) + COST, 5),
        "net_sumR": round(sumR, 3), "net_sum_dollars": round(float(nd.sum()), 3),
        "best_over_sumR": round(float(srt[0]) / sumR, 4) if sumR else None,
        "wo1_netR": round(sumR - float(srt[0]), 3),
        "conv_TP1_TP2": round(reach2 / reach1, 3) if reach1 else None,
    }


def _cells_for_type(trades: list[Trade]) -> dict[str, Any]:
    cells: dict[str, Any] = {"aggregate": _cell(trades)}
    for r in REGIMES:
        cells[f"regime:{r}"] = _cell([t for t in trades if t.regime == r])
    for s in SESSIONS:
        cells[f"session:{s}"] = _cell([t for t in trades if t.session == s])
    for r in REGIMES:
        for s in SESSIONS:
            cells[f"regime×session:{r}×{s}"] = _cell([t for t in trades if t.regime == r and t.session == s])
    for p in POLARITIES:
        cells[f"polarity:{p}"] = _cell([t for t in trades if t.pol == p])
    return cells


def main() -> int:
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh1, _ = load("H1_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh4, _ = load("H4_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | M15={len(dfm)} | contract OBDZ-002 SL/TP/podea={SL_M}/{TP1_M}/{TP2_M}/{FLOOR}×ATR14[t] | N_MIN={N_MIN}")
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

    names = [nm for (_w, nm, _f) in SOURCES]
    trades_by_type: dict[str, list[Trade]] = {nm: [] for nm in names}

    for ri, seg in enumerate(segs):
        label = _regime_label(seg, ri); rshort = REGIMES[ri]
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(rshort) not in (None, len(sub)):
            print(f"STOP: {rshort} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        tm = [int(x) for x in sub["time"].tolist()]
        atr = sub["atr14"].to_numpy(); h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy(); day = sub["day"].to_numpy()
        bias_up = (h1 > 0.5) & (h4 > 0.5)
        bias_dn = (h1 <= 0.5) & (h4 <= 0.5) & np.isfinite(h1) & np.isfinite(h4)
        week = derive_week_index(day.tolist())                   # pt. PWH/PWL, ca în survey
        ctx = Ctx(o, h, l, c, tm, atr, bias_up, bias_dn, day, week, n)
        eod = _eod_per_bar(day.tolist(), n)

        for (_w, nm, fn) in SOURCES:
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
                sess = session_of(tm[entry - 1])                 # sesiunea barei-declanșator t=entry-1
                pol = "demand" if d > 0 else "supply"
                trades_by_type[nm].append(Trade(rshort, sess, pol, res.net_R, res.net_R * (SL_M * a), res.exit_reason))

    out: dict[str, Any] = {"contract": "OBDZ-002", "mults": [SL_M, TP1_M, TP2_M, FLOOR], "N_MIN": N_MIN,
                           "session_anchor": "trigger bar t (=entry-1)", "types": {}}
    for (wave, nm, _f) in SOURCES:
        cells = _cells_for_type(trades_by_type[nm])
        out["types"][nm] = {"wave": wave, "n_total": len(trades_by_type[nm]), "cells": cells}
        agg = cells["aggregate"]
        print(f"\n########## [{wave}] {nm}  (N={len(trades_by_type[nm])}) ##########")
        if agg.get("INSUFFICIENT_N"):
            print(f"  AGREGAT: n={agg['n']} INSUFFICIENT_N")
        else:
            print(f"  AGREGAT n={agg['n']} WR={agg['winrate']} E_R={agg['expectancy_R']:+.4f} "
                  f"E_$={agg['expectancy_dollars']:+.4f} edge_brut_$={agg['edge_brut_dollars']:+.4f} "
                  f"netR={agg['net_sumR']:+.2f} net$={agg['net_sum_dollars']:+.2f} best/sumR={agg['best_over_sumR']} "
                  f"wo1R={agg['wo1_netR']:+.2f} conv={agg['conv_TP1_TP2']}")
        # regime + polarity linie compactă (sesiunile + cross în JSON)
        for key in [f"regime:{r}" for r in REGIMES] + [f"polarity:{p}" for p in POLARITIES]:
            cc = cells[key]
            if cc.get("INSUFFICIENT_N"):
                print(f"    {key:22s} n={cc['n']} INSUFFICIENT_N")
            else:
                print(f"    {key:22s} n={cc['n']} WR={cc['winrate']} E_$={cc['expectancy_dollars']:+.4f} "
                      f"net$={cc['net_sum_dollars']:+.2f} edge_brut_$={cc['edge_brut_dollars']:+.4f} conv={cc['conv_TP1_TP2']}")
        n_sess_ok = sum(1 for s in SESSIONS if not cells[f"session:{s}"].get("INSUFFICIENT_N"))
        n_cross_ok = sum(1 for r in REGIMES for s in SESSIONS if not cells[f"regime×session:{r}×{s}"].get("INSUFFICIENT_N"))
        print(f"    (sesiuni n>=25: {n_sess_ok}/4 | regim×sesiune n>=25: {n_cross_ok}/12 — vezi JSON)")

    path = os.path.join(_ROOT, "reports", "zone_survey_execution_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/zone_survey_execution_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

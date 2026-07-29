"""SARCINA 2 (Mandat cost-correction) — re-rularea SMC_S1 + 7 familii cu COSTUL CORECT (0,20).

Contract EXISTENT, o singură variabilă schimbată = COSTUL (0,40→0,20). Familii: S1 + S2,S3,S7,S11,S13,
S16,S17 (orizonturi 20/20/20/20/20/20/92/460). S10 EXCLUS (rebuclă deschisă). Read-only, in-sample, M15_v2.

DOUĂ VARIANTE DE FILTRU (izolează efectul filtrului de cel al costului), în DOLARI pe geometria brută:
  VECHI  spike_$ ∈ [1,01 ; 6,50)   = [10,1;65) pips @TICK0,10;  buffer R = 2×0,10 = 0,20$
  NOU    spike_$ ∈ [0,58 ; 6,50)   = [58;650) pips @TICK0,01 (re-derivat v2.7.8: podea (3×0,20−2×0,01)/0,01=58,
                                     plafon 650 = relabelarea p90 la $6,50);  buffer R = 2×0,01 = 0,02$
distanța_$ e independentă de TICK; DOAR bufferul R și eticheta-pips se schimbă. edge_brut_$ = media gross_$
e INDEPENDENTĂ de cost ȘI TICK (depinde doar de populația eligibilă + prețuri).

DECIZIE: edge_brut_$ vs cost. Coloană de comparație: cost 0,40 (anterior) lângă cost 0,20 (nou), pe filtrul
VECHI → izolează efectul costului. VECHI vs NOU la 0,20 → izolează efectul filtrului. Fără FDR, fără
portofoliu. WP-5' per familie L=28 (caveat: oracol pe sume-orizont/net_R; NEVALIDAT S16/S17 L<H). NU interpretez.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Callable

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT, os.path.join(_ROOT, "edge_research"), os.path.join(_ROOT, "edge_research", "lm001_s8")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from edge_research._common import PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC, load
import split_manifest as SM
from market_structure import Block
from institutional_levels import derive_week_index
import trading_strategies as TS
import block_bootstrap as BB

FROZEN_TICK = 0.10                    # TICK-ul cu care detect_sX calculează spike_pips (frozen)
L, BOOT, SEED = 28, 2000, 20260729
COST_NEW, COST_OLD = 0.20, 0.40
FILTERS = {"vechi": (1.01, 6.50, 0.20), "nou": (0.58, 6.50, 0.02)}   # (lo_$, hi_$, buffer_R_$)
EXPECTED = {"bear": 52_403, "bull": 52_851, "correction": 25_237}

FAMILIES: list[tuple[str, Callable[[Any], list[TS.StrategySignal]], int]] = [
    ("S1", lambda a: TS.detect_s1(a["o"], a["h"], a["l"], a["c"], a["blocks"]), 20),
    ("S2", lambda a: TS.detect_s2(a["o"], a["h"], a["l"], a["c"], a["blocks"]), 20),
    ("S3", lambda a: TS.detect_s3(a["o"], a["h"], a["l"], a["c"], a["blocks"]), 20),
    ("S7", lambda a: TS.detect_s7(a["o"], a["h"], a["l"], a["c"], a["blocks"]), 20),
    ("S11", lambda a: TS.detect_s11(a["o"], a["h"], a["l"], a["c"], a["blocks"]), 20),
    ("S13", lambda a: TS.detect_s13(a["o"], a["h"], a["l"], a["c"], a["blocks"]), 20),
    ("S16", lambda a: TS.detect_s16(a["o"], a["h"], a["l"], a["c"], a["day"], a["blocks"]), 92),
    ("S17", lambda a: TS.detect_s17(a["o"], a["h"], a["l"], a["c"], a["day"], a["week"], a["blocks"]), 460),
]


def _day_index(sub: Any) -> list[int]:
    dt = pd.to_datetime(sub["time"], unit="s", utc=True)
    ny = dt.dt.tz_convert("America/New_York").dt.tz_localize(None)
    return (ny - pd.Timedelta(hours=17)).dt.floor("D").values.astype("datetime64[D]").astype("int64").tolist()


def _context(sub: Any) -> dict[str, Any]:
    o = sub["open"].to_numpy(); h = sub["high"].to_numpy(); lo = sub["low"].to_numpy(); c = sub["close"].to_numpy()
    day = _day_index(sub)
    return {"o": o.tolist(), "h": h.tolist(), "l": lo.tolist(), "c": c.tolist(), "blocks": [Block(0, len(sub))],
            "day": day, "week": derive_week_index(day), "O": o, "C": c, "n": len(sub)}


def _all_triggers(detect: Callable[[Any], list[TS.StrategySignal]], ctx: dict[str, Any]) -> list[TS.StrategySignal]:
    lo0, hi0 = TS.ELIG_LO, TS.ELIG_HI
    TS.ELIG_LO, TS.ELIG_HI = -1.0, 1e18
    try:
        return detect(ctx)
    finally:
        TS.ELIG_LO, TS.ELIG_HI = lo0, hi0


def _metrics(eligible: list[TS.StrategySignal], ctx: dict[str, Any], horizon: int, buffer_r: float,
             cost: float, want_p: bool) -> dict[str, Any]:
    O, C, n = ctx["O"], ctx["C"], ctx["n"]
    gross: list[float] = []; net_r: list[float] = []; net_d: list[float] = []; rs: list[float] = []
    for s in eligible:
        exit_idx = s.entry_idx + horizon
        if exit_idx >= n:
            continue
        g = s.direction * (float(C[exit_idx]) - float(O[s.entry_idx]))
        spike_d = s.spike_pips * FROZEN_TICK                    # distanța structurală în DOLARI
        r_d = spike_d + buffer_r
        nd = g - cost
        gross.append(g); net_d.append(nd); net_r.append(nd / r_d); rs.append(r_d)
    nt = len(net_d)
    if nt == 0:
        return {"n_trades": 0}
    nr = np.asarray(net_r); nd_a = np.asarray(net_d); gr = np.asarray(gross)
    sumR = float(nr.sum()); best = float(np.sort(nr)[::-1][0])
    p = (BB.run(nr, block_length=L, B=BOOT, tail="right", centering="zero", seed=SEED)["p_hat"]
         if want_p and nt > L else None)
    return dict(
        n_trades=nt, winrate=round(float((nd_a > 0).mean()), 4), R_mediu=round(float(np.mean(rs)), 4),
        expectancy_R=round(float(nr.mean()), 5), expectancy_dollars=round(float(nd_a.mean()), 5),
        net_sumR=round(sumR, 2), net_sum_dollars=round(float(nd_a.sum()), 2),
        edge_brut_dollars=round(float(gr.mean()), 5),          # media gross_$ (cost/TICK-independentă)
        best_over_sumR=round(best / sumR, 4) if sumR else None, wo1_netR=round(sumR - best, 2), p_wp5=p)


def _cell(fam: str, horizon: int, ctx: dict[str, Any]) -> dict[str, Any]:
    detect = next(fn for nm, fn, _h in FAMILIES if nm == fam)
    triggers = _all_triggers(detect, ctx)
    total = len(triggers)
    out: dict[str, Any] = {}
    for fname, (lo_d, hi_d, buf) in FILTERS.items():
        elig = [s for s in triggers if lo_d <= s.spike_pips * FROZEN_TICK < hi_d]
        pct_excl = round(100.0 * (total - len(elig)) / total, 2) if total else 0.0
        cell_new = _metrics(elig, ctx, horizon, buf, COST_NEW, want_p=True)
        cell_new["pct_excluded"] = pct_excl
        out[fname] = cell_new
        if fname == "vechi":                                   # comparație: cost 0,40 pe filtrul VECHI
            prev = _metrics(elig, ctx, horizon, buf, COST_OLD, want_p=False)
            out["vechi_cost040_prev"] = {"expectancy_dollars": prev.get("expectancy_dollars"),
                                         "net_sum_dollars": prev.get("net_sum_dollars"),
                                         "edge_brut_dollars": prev.get("edge_brut_dollars")}
    return out


def _regime_label(seg: dict[str, Any], i: int) -> str:
    for k in ("regime", "label", "name"):
        v = seg.get(k)
        if isinstance(v, str):
            return v.lower()
    return ["bear", "bull", "correction"][i]


def main() -> int:
    df, _meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | discovery bars = {len(df)} | cost {COST_OLD}->{COST_NEW} | filtre {FILTERS}")
    if len(df) != 130_491:
        print(f"STOP: {len(df)} bare."); return 2
    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]
    t = df["time"].to_numpy()
    contexts: list[tuple[str, dict[str, Any]]] = []
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = df[(t >= s_ep) & (t < e_ep)].reset_index(drop=True)
        if EXPECTED.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        contexts.append((label, _context(sub)))

    out: dict[str, Any] = {"results": {}}
    for fam, _fn, horizon in FAMILIES:
        out["results"][fam] = {}
        print(f"\n########## {fam} (H={horizon}) — EDGE_BRUT_$ vs cost 0,20 (decizie); prev=cost0,40 ##########")
        for label, ctx in contexts:
            cell = _cell(fam, horizon, ctx)
            out["results"][fam][label] = cell
            v, nu, prev = cell["vechi"], cell["nou"], cell["vechi_cost040_prev"]
            if v.get("n_trades", 0) == 0:
                print(f"  {label:11s} (fără tranzacții)"); continue
            print(f"  {label:11s} VECHI n={v['n_trades']:5d} excl%={v['pct_excluded']:4.0f} "
                  f"EDGE_BRUT_$={v['edge_brut_dollars']:+.4f} E_$[.20]={v['expectancy_dollars']:+.4f} "
                  f"E_$[.40]={prev['expectancy_dollars']:+.4f} net$[.20]={v['net_sum_dollars']:+.0f} "
                  f"WR={v['winrate']:.3f} p={v['p_wp5']}")
            print(f"  {'':11s} NOU   n={nu['n_trades']:5d} excl%={nu['pct_excluded']:4.0f} "
                  f"EDGE_BRUT_$={nu['edge_brut_dollars']:+.4f} E_$[.20]={nu['expectancy_dollars']:+.4f} "
                  f"net$[.20]={nu['net_sum_dollars']:+.0f} WR={nu['winrate']:.3f} p={nu['p_wp5']} "
                  f"Rmed=${nu['R_mediu']:.2f} b/sR={nu['best_over_sumR']} wo1R={nu['wo1_netR']:+.0f}")

    # structură: câte celule au edge_brut_$ >= cost (0,20 nou vs 0,40 vechi), pe filtrul VECHI
    def _count(bar: float) -> int:
        return sum(1 for fam, _f, _h in FAMILIES for lb, _c in contexts
                   if out["results"][fam][lb]["vechi"].get("edge_brut_dollars", -9) >= bar)
    print(f"\n########## STRUCTURĂ (filtru vechi): celule cu edge_brut_$ ≥ 0,40 = {_count(0.40)}/24 ; "
          f"≥ 0,20 = {_count(0.20)}/24 ##########")
    fams_pos_020 = [fam for fam, _f, _h in FAMILIES
                    if any(out["results"][fam][lb]["vechi"].get("edge_brut_dollars", -9) >= 0.20 for lb, _c in contexts)]
    print(f"  familii cu ≥1 celulă edge_brut_$ ≥ 0,20 (filtru vechi): {fams_pos_020} ({len(fams_pos_020)}/8)")
    out["structure"] = {"cells_ge_040_of_24": _count(0.40), "cells_ge_020_of_24": _count(0.20),
                        "families_with_a_cell_ge_020": fams_pos_020}
    path = os.path.join(_ROOT, "reports", "task2_cost_rerun_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"\nrecord -> reports/task2_cost_rerun_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

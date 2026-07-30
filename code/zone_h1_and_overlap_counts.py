"""Trei numărători (FĂRĂ P&L, GARD 1 rămâne True, GARD 2 neatins). Statistician mandat 2026-07-30.

READ-ONLY, in-sample. Nicio metrică de tranzacție, niciun p-value — doar n-uri și suprapuneri geografice.

SARCINA 1 — zone pe H1_from_M15_v2 (context derivat, discovery-safe):
  detect_order_blocks + track_breaker pe H1. Număr de zone (OB, Breaker) per regim. Sub-stratificare:
  câte se FORMEAZĂ în sesiunea london (8 <= hh_UTC < 13). Formarea: OB la formation_idx (bara-ancoră),
  Breaker la breaker_idx (bara de flip). Doar n.

SARCINA 2 — intersecția M15 cu ancorele 1H london:
  Câte FVG și CE-50 de pe M15 intersectează GEOGRAFIC (suprapunere de preț) cu zonele 1H formate în london.
  ⚠ CONVENȚIE (disclosed): „geografic" = suprapunere de bandă de preț; scop = ACELAȘI regim ȘI forward-safe
  (zona H1 disponibilă la momentul apariției FVG-ului M15: avail_time_H1 <= time_M15[confirmed_idx]). FVG↔zonă:
  h1_lower<=fvg_upper ȘI h1_upper>=fvg_lower. CE-50↔zonă: h1_lower <= ce_50 <= h1_upper. Sub n=25 → INSUFFICIENT_N.

SARCINA 3 — suprapunerea declanșatoarelor între cele 10 tipuri M15 (restanță):
  ACEEAȘI populație braț-A ca survey-ul (import SOURCES/Ctx). Identitatea unui declanșator = (epoca barei-
  declanșator t=entry−1, direcție) — cheie GLOBALĂ, comparabilă între tipuri și regime. Matrice 10×10: câte
  declanșatoare IDENTICE per pereche, în % din populația mai mică. Plus declanșatoare UNICE per tip (absente
  din reuniunea celorlalte 9). Special: FVG vs CE-50 vs IFVG (CE-50 = punctul median al aceluiași FVG).
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
from imbalance_mechanics import detect_fvgs
from institutional_levels import derive_week_index
from market_state import session_of
from market_structure import Block
from order_block_void import OrderBlockKind
from order_flow import detect_order_blocks, track_breaker
from zone_survey_three_arm import SOURCES, Ctx, _day_index, _htf_trend, _regime_label, src_bpr

N_MIN = 25
REGIMES = ["bear", "bull", "correction"]
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}


def _load_prepared() -> tuple[Any, Any, np.ndarray, list[dict[str, Any]]]:
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh1, _ = load("H1_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh4, _ = load("H4_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    if len(dfm) != 130_491:
        raise SystemExit(f"STOP: M15 {len(dfm)}.")
    dfm = dfm.sort_values("time").reset_index(drop=True)
    for name, dfh, per in (("h1", dfh1, 3600), ("h4", dfh4, 4 * 3600)):
        htf = _htf_trend(dfh, per).sort_values("avail")
        dfm = pd.merge_asof(dfm, htf.rename(columns={"trend_up": name}), left_on="time", right_on="avail",
                            direction="backward").drop(columns="avail")
    dfm["day"] = _day_index(dfm["time"])
    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]
    dfh1 = dfh1.sort_values("time").reset_index(drop=True)
    return dfm, dfh1, dfm["time"].to_numpy(), segs


def sarcina1(dfh1: Any, segs: list[dict[str, Any]]) -> dict[str, Any]:
    print("\n########## SARCINA 1 — zone pe H1_from_M15_v2 (OB + Breaker), sub-strat london ##########")
    th = dfh1["time"].to_numpy()
    out: dict[str, Any] = {}
    for ri, seg in enumerate(segs):
        rshort = REGIMES[ri]
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfh1[(th >= s_ep) & (th < e_ep)].reset_index(drop=True)
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        tm = [int(x) for x in sub["time"].tolist()]
        obs = detect_order_blocks(o, h, l, c, n)
        n_ob = len(obs); n_ob_london = sum(1 for ob in obs if session_of(tm[ob.formation_idx]) == "london")
        n_br = 0; n_br_london = 0
        for ob in obs:
            br = track_breaker(ob, h, l, c, n)
            if br is None:
                continue
            n_br += 1
            if session_of(tm[br.breaker_idx]) == "london":
                n_br_london += 1
        out[rshort] = {"h1_bars": n, "OB": n_ob, "OB_london": n_ob_london,
                       "Breaker": n_br, "Breaker_london": n_br_london}
        print(f"  {rshort:11s} H1_bars={n:6d} | OB={n_ob:4d} (london {n_ob_london:3d}) | "
              f"Breaker={n_br:4d} (london {n_br_london:3d})")
    return out


def sarcina2(dfm: Any, dfh1: Any, t_all: np.ndarray, segs: list[dict[str, Any]]) -> dict[str, Any]:
    print("\n########## SARCINA 2 — M15 FVG/CE-50 ∩ geografic zone 1H london (forward-safe, per regim) ##########")
    th = dfh1["time"].to_numpy()
    out: dict[str, Any] = {}
    for ri, seg in enumerate(segs):
        rshort = REGIMES[ri]
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        # zonele 1H london (OB@formation, Breaker@flip) = (avail_time, lower, upper)
        subh = dfh1[(th >= s_ep) & (th < e_ep)].reset_index(drop=True)
        nh = len(subh)
        oh = subh["open"].tolist(); hh = subh["high"].tolist(); lh = subh["low"].tolist(); ch = subh["close"].tolist()
        tmh = [int(x) for x in subh["time"].tolist()]
        h1_zones: list[tuple[int, float, float]] = []
        for ob in detect_order_blocks(oh, hh, lh, ch, nh):
            if session_of(tmh[ob.formation_idx]) == "london":
                h1_zones.append((tmh[ob.formation_idx], ob.zone_lower, ob.zone_upper))
            br = track_breaker(ob, hh, lh, ch, nh)
            if br is not None and session_of(tmh[br.breaker_idx]) == "london":
                h1_zones.append((tmh[br.breaker_idx], br.zone_lower, br.zone_upper))
        zt = np.array([z[0] for z in h1_zones], dtype=np.int64)
        zlo = np.array([z[1] for z in h1_zones]); zhi = np.array([z[2] for z in h1_zones])

        subm = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        nm = len(subm)
        hm = subm["high"].tolist(); lm = subm["low"].tolist(); tmm = [int(x) for x in subm["time"].tolist()]
        fvgs = detect_fvgs(hm, lm, [Block(0, nm)])
        n_fvg = len(fvgs)
        fvg_hit = 0; ce_hit = 0
        for f in fvgs:
            tau = tmm[f.confirmed_idx]                        # forward-safe: zona H1 disponibilă la apariția FVG
            avail = zt <= tau
            if not avail.any():
                continue
            fov = avail & (zlo <= f.upper) & (zhi >= f.lower)  # suprapunere de bandă
            if fov.any():
                fvg_hit += 1
            ce = f.ce_50
            cov = avail & (zlo <= ce) & (zhi >= ce)            # ce_50 în bandă
            if cov.any():
                ce_hit += 1
        rec = {"h1_london_zones": len(h1_zones), "M15_FVG_total": n_fvg,
               "FVG_intersect": fvg_hit, "CE50_intersect": ce_hit}
        for key in ("FVG_intersect", "CE50_intersect"):
            if rec[key] < N_MIN:
                rec[key + "_INSUFFICIENT_N"] = True
        out[rshort] = rec
        fflag = " INSUFFICIENT_N" if fvg_hit < N_MIN else ""
        cflag = " INSUFFICIENT_N" if ce_hit < N_MIN else ""
        print(f"  {rshort:11s} zone1H_london={len(h1_zones):4d} | M15_FVG={n_fvg:5d} | "
              f"FVG∩={fvg_hit:4d}{fflag} | CE50∩={ce_hit:4d}{cflag}")
    return out


def sarcina3(dfm: Any, dfh1: Any, t_all: np.ndarray, segs: list[dict[str, Any]]) -> dict[str, Any]:
    print("\n########## SARCINA 3 — suprapunerea declanșatoarelor, matrice 10×10 (% din pop. mai mică) ##########")
    names = [nm for (_w, nm, _f) in SOURCES]
    trig: dict[str, set[tuple[int, int]]] = {nm: set() for nm in names}   # (epoca barei-declanșator, direcție)
    for ri, seg in enumerate(segs):
        rshort = REGIMES[ri]
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        n = len(sub)
        if EXPECTED_BARS.get(rshort) not in (None, n):
            raise SystemExit(f"STOP: {rshort} {n} bare.")
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        tm = [int(x) for x in sub["time"].tolist()]
        atr = sub["atr14"].to_numpy(); h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy(); day = sub["day"].to_numpy()
        bias_up = (h1 > 0.5) & (h4 > 0.5)
        bias_dn = (h1 <= 0.5) & (h4 <= 0.5) & np.isfinite(h1) & np.isfinite(h4)
        week = derive_week_index(day.tolist())
        ctx = Ctx(o, h, l, c, tm, atr, bias_up, bias_dn, day, week, n)
        for (_w, nm, fn) in SOURCES:
            if nm == "BPR":
                events = []
                for tol in (0.0, 0.10, 0.25):
                    events = src_bpr(ctx, tol)
                    if len(events) >= 25:
                        break
            else:
                events = fn(ctx)
            for (entry, d, _a, _ep) in events:
                trig[nm].add((tm[entry - 1], d))               # cheie globală: epoca barei t + direcție

    sizes = {nm: len(trig[nm]) for nm in names}
    inter = {a: {b: len(trig[a] & trig[b]) for b in names} for a in names}
    union_others = {nm: set().union(*[trig[o] for o in names if o != nm]) for nm in names}
    unique = {nm: len(trig[nm] - union_others[nm]) for nm in names}

    print(f"  populații (declanșatoare distincte (t,dir)): " + ", ".join(f"{nm}={sizes[nm]}" for nm in names))
    short = {nm: nm[:4] for nm in names}
    hdr = "        " + " ".join(f"{short[b]:>5s}" for b in names)
    print(hdr)
    for a in names:
        row = []
        for b in names:
            if a == b:
                row.append(f"{'—':>5s}")
            else:
                mn = min(sizes[a], sizes[b])
                pct = 100.0 * inter[a][b] / mn if mn else 0.0
                row.append(f"{pct:5.1f}")
        print(f"  {short[a]:5s} " + " ".join(row))
    print("  UNICE per tip (absent din reuniunea celorlalte 9): " + ", ".join(f"{nm}={unique[nm]}" for nm in names))
    # zoom FVG/CE-50/IFVG
    print("\n  ── FVG vs CE-50 vs IFVG (identice, % din pop. mai mică) ──")
    for a, b in (("FVG", "CE-50"), ("FVG", "IFVG"), ("CE-50", "IFVG")):
        mn = min(sizes[a], sizes[b])
        print(f"    {a} ∩ {b} = {inter[a][b]}  ({100.0*inter[a][b]/mn:.1f}% din min={mn})")
    return {"sizes": sizes, "intersections": inter, "unique": unique}


def main() -> int:
    dfm, dfh1, t_all, segs = _load_prepared()
    print(f"loader v6 | M15={len(dfm)} | H1_from_M15_v2={len(dfh1)} | GARD 1 neatins (numărători)")
    out: dict[str, Any] = {"sarcina1_h1_zones": sarcina1(dfh1, segs),
                           "sarcina2_m15_h1_london_intersect": sarcina2(dfm, dfh1, t_all, segs),
                           "sarcina3_trigger_overlap": sarcina3(dfm, dfh1, t_all, segs)}
    path = os.path.join(_ROOT, "reports", "zone_h1_and_overlap_counts_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/zone_h1_and_overlap_counts_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

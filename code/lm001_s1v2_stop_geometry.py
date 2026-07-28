"""SMC_S1_v2 — Măsurătoarea A (geometria stopului propus) + DIAGNOSTICUL de sensibilitate (Mandat 5.12).

Specificație RATIFICATĂ integral: doc `da52831` (STAT-STOP-GEOMETRY-SENSITIVITY-DESIGN-v1.0) + manifest
v2.7.7 la `b98070c`. READ-ONLY analiză pe DESCOPERIRE (in-sample). NU atinge GARD 2, NU atinge sigilatul,
NU rulează altă familie, NU optimizează (DIAGNOSTIC, nu FITTING). Pragul e citit, nu ales.

MĂSURĂTOAREA A — populația = cele 34.670 evenimente de wick-sweep BRUTE (D6/D7), NU cele 21.048 filtrate
(filtrul [10,1;65,0) e circular pentru geometria nouă). Distanța = |open[c+1] − preț_swing_major| pips,
unde swing_major = cel mai apropiat Swing CLASIFICAT de aceeași direcție, idx STRICT ANTERIOR swing-ului
bazinului, cu preț MAI EXTREM decât basin, în ACELAȘI bloc (D4). Degradare grațioasă: dacă niciun swing
mai extrem → referința = bazinul însuși (INCLUS). Excludere: dacă NICIUN swing clasificat anterior în bloc
(margine, D3_bis) → EXCLUS din distribuție, numărat separat.
⚠ INTERPRETARE semnalată de Statistician: „cel mai apropiat" = cel mai RECENT anterior (idx maxim < idx
bazin) printre cele mai extreme. Dacă CTO a intenționat pur ordinea (nu extremitatea), reconfirmare.

DIAGNOSTIC — 5 stopuri FIXE: p25/p50/p75/p90 ale distribuției AGREGATE (Măsurătoarea A) + ancora 14,7 pips.
Aceeași populație de semnale (raw sweeps, orizont complet), evaluată la fiecare. ⚠ MODEL DE IEȘIRE: spec-ul
notează explicit „winrate-ul și distribuția rezultatului se schimbă cu stopul" — ceea ce cere un STOP-LOSS
REAL (nu doar normalizarea R din Mandat 5.11). Deci: intrare open[c+1], stop structural intrabar la ±X
(long: low≤entry−X; short: high≥entry+X) verificat pe [entry, entry+20], ieșire la stop (−X) la prima
atingere ALTFEL ieșire pe timp la close[entry+20]. net_$ = gross_$ − cost(0,40); net_R = net_$/X_$.
⚠ Dacă Statisticianul a intenționat alt model de ieșire, reconfirmare — e singura alegere interpretativă.

RAPORTARE DUALĂ obligatorie (R ȘI dolari). Variabila de DECIZIE = DOLARII. Prag PRE-ÎNREGISTRAT (da52831):
  ÎNCHIS DEFINITIV      expectancy_$ ≤ 0 la TOATE cele 5 stopuri, în TOATE cele 3 regimuri.
  MERITĂ IPOTEZĂ NOUĂ   expectancy_$ > 0 la ≥2 din cele 3 stopuri mai LARGI, în ≥2 din cele 3 regimuri.
  ALTFEL                AMBIGUOUS / TESTABLE-BUT-INSUFFICIENT.
"""

from __future__ import annotations

import bisect
import json
import os
import sys
from typing import Any

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT, os.path.join(_ROOT, "edge_research")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from edge_research._common import PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC, load
import split_manifest as SM
from market_structure import Block, StructureLabel, SwingKind, detect_swings, label_structure
from liquidity_mechanics import PoolSide, PoolTier, build_pools, detect_sweeps

TICK, COST, H = 0.10, 0.40, 20
OLD_STOP_PIPS = 14.7
EXPECTED = {"bear": 52_403, "bull": 52_851, "correction": 25_237}


def _regime_label(seg: dict[str, Any], i: int) -> str:
    for k in ("regime", "label", "name"):
        v = seg.get(k)
        if isinstance(v, str):
            return v.lower()
    return ["bear", "bull", "correction"][i]


def _measure_and_collect(label: str, sub: Any) -> dict[str, Any]:
    o = sub["open"].to_numpy(); hi = sub["high"].to_numpy()
    lo = sub["low"].to_numpy(); cl = sub["close"].to_numpy()
    n = len(sub)
    blocks = [Block(0, n)]
    swings = label_structure(detect_swings(hi.tolist(), lo.tolist(), blocks, k=2))
    pools = build_pools(swings, PoolTier.EXTERNAL)
    sweeps = detect_sweeps(hi.tolist(), lo.tolist(), cl.tolist(), pools, blocks, require_close_back_inside=True)

    # swing-uri clasificate de fiecare direcție, sortate pe idx (pentru „cel mai recent anterior mai extrem")
    low_idx: list[int] = []; low_px: list[float] = []
    high_idx: list[int] = []; high_px: list[float] = []
    for s in sorted(swings, key=lambda x: x.idx):
        if s.label is StructureLabel.UNCLASSIFIED:
            continue
        if s.kind is SwingKind.LOW:
            low_idx.append(s.idx); low_px.append(s.price)
        else:
            high_idx.append(s.idx); high_px.append(s.price)

    distances: list[float] = []
    n_excluded_no_prior = 0
    n_degraded = 0
    signals: list[tuple[int, int]] = []          # (entry_idx, direction) pentru diagnostic
    raw_valid = 0
    for sw in sweeps:
        c = sw.idx
        entry = c + 1
        if entry >= n:
            continue
        raw_valid += 1
        below = sw.pool.side is PoolSide.BELOW
        direction = +1 if below else -1
        if entry + H < n:                        # populația de diagnostic = orizont complet
            signals.append((entry, direction))
        # --- Măsurătoarea A ---
        basin = sw.pool.price
        pool_idx = sw.pool.formed_idx
        idxs, pxs = (low_idx, low_px) if below else (high_idx, high_px)
        cut = bisect.bisect_left(idxs, pool_idx)   # swing-uri cu idx < pool_idx
        if cut == 0:
            n_excluded_no_prior += 1               # niciun swing clasificat anterior în bloc → EXCLUS
            continue
        major_price = None
        for j in range(cut - 1, -1, -1):           # de la cel mai recent anterior, înapoi
            more_extreme = pxs[j] < basin if below else pxs[j] > basin
            if more_extreme:
                major_price = pxs[j]; break
        if major_price is None:
            major_price = basin                    # degradare grațioasă → referința = bazinul
            n_degraded += 1
        distances.append(abs(float(o[entry]) - major_price) / TICK)

    return dict(
        label=label, n_bars=n, raw_valid=raw_valid, distances=distances,
        n_excluded_no_prior=n_excluded_no_prior, n_degraded=n_degraded,
        _arrays=(o, hi, lo, cl, n), _signals=signals)


def _dist_report(d: list[float]) -> dict[str, Any]:
    a = np.asarray(d)
    if not len(a):
        return {}
    return dict(
        n=int(len(a)), min=round(float(a.min()), 2),
        p10=round(float(np.percentile(a, 10)), 2), p25=round(float(np.percentile(a, 25)), 2),
        median=round(float(np.percentile(a, 50)), 2), p75=round(float(np.percentile(a, 75)), 2),
        p90=round(float(np.percentile(a, 90)), 2), max=round(float(a.max()), 2),
        n_over_65=int((a > 65.0).sum()), pct_over_65=round(100.0 * float((a > 65.0).mean()), 2),
        n_under_101=int((a < 10.1).sum()), pct_under_101=round(100.0 * float((a < 10.1).mean()), 2))


def _simulate(entry: int, direction: int, o: Any, hi: Any, lo: Any, cl: Any, n: int, x_d: float) -> float:
    """gross_$ al unei tranzacții cu stop-loss intrabar ±x_d + ieșire pe timp la close[entry+H]."""
    entry_px = float(o[entry])
    exit_bar = entry + H
    if direction == +1:
        stop = entry_px - x_d
        if (lo[entry:exit_bar + 1] <= stop).any():
            return -x_d
        return float(cl[exit_bar]) - entry_px
    stop = entry_px + x_d
    if (hi[entry:exit_bar + 1] >= stop).any():
        return -x_d
    return entry_px - float(cl[exit_bar])


def _cell(reg: dict[str, Any], x_pips: float) -> dict[str, Any]:
    o, hi, lo, cl, n = reg["_arrays"]
    x_d = x_pips * TICK
    net_d = np.empty(len(reg["_signals"]))
    for i, (entry, direction) in enumerate(reg["_signals"]):
        gross = _simulate(entry, direction, o, hi, lo, cl, n, x_d)
        net_d[i] = gross - COST
    net_r = net_d / x_d
    nt = len(net_d)
    sumR = float(net_r.sum())
    best_r = float(np.sort(net_r)[::-1][0]) if nt else 0.0
    return dict(
        stop_pips=round(x_pips, 2), n_trades=nt,
        winrate=round(float((net_d > 0).mean()), 4) if nt else None,
        expectancy_R=round(float(net_r.mean()), 5) if nt else None,
        expectancy_dollars=round(float(net_d.mean()), 5) if nt else None,
        net_sumR=round(sumR, 2), net_sum_dollars=round(float(net_d.sum()), 2),
        best_over_sumR=round(best_r / sumR, 4) if sumR else None,
        wo1_netR=round(sumR - best_r, 2))


def main() -> int:
    df, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | discovery bars = {len(df)}")
    if len(df) != 130_491:
        print(f"STOP: {len(df)} bare, aștept 130.491."); return 2
    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]
    t = df["time"].to_numpy()
    regimes: list[dict[str, Any]] = []
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = df[(t >= s_ep) & (t < e_ep)].reset_index(drop=True)
        if EXPECTED.get(label) not in (None, len(sub)):
            print(f"STOP: regim {label} are {len(sub)} bare, aștept {EXPECTED[label]}."); return 3
        regimes.append(_measure_and_collect(label, sub))

    # ---- MĂSURĂTOAREA A ----
    print("\n########## MĂSURĂTOAREA A — geometria noului stop (populația BRUTĂ 34.670) ##########")
    agg_dist: list[float] = []
    total_raw = 0
    measA: dict[str, Any] = {}
    for reg in regimes:
        agg_dist += reg["distances"]; total_raw += reg["raw_valid"]
        rep = _dist_report(reg["distances"])
        measA[reg["label"]] = dict(rep, raw_valid=reg["raw_valid"],
                                   excluded_no_prior_swing=reg["n_excluded_no_prior"], degraded_to_basin=reg["n_degraded"])
        print(f"\n=== {reg['label'].upper()} | raw_valid={reg['raw_valid']} | "
              f"excluse(no-prior)={reg['n_excluded_no_prior']} | degradate(basin)={reg['n_degraded']} ===")
        for k, v in rep.items():
            print(f"  {k:14s} {v}")
    agg = _dist_report(agg_dist)
    measA["AGGREGATE"] = dict(agg, total_raw=total_raw)
    print(f"\n=== AGREGAT (n={agg.get('n')}) ===")
    for k, v in agg.items():
        print(f"  {k:14s} {v}")

    # ---- 5 stopuri ----
    stops = [OLD_STOP_PIPS, agg["p25"], agg["median"], agg["p75"], agg["p90"]]
    names = ["14.7_anchor", "p25", "p50", "p75", "p90"]
    print(f"\nSTOPURI (pips): " + ", ".join(f"{nm}={sp}" for nm, sp in zip(names, stops)))
    wider3 = sorted(range(5), key=lambda k: stops[k])[-3:]     # cele 3 stopuri mai largi (după pips)
    print(f"cele 3 stopuri mai largi = {[names[k] for k in wider3]}")

    # ---- DIAGNOSTIC ----
    print("\n########## DIAGNOSTIC — 5 stopuri × 3 regimuri (raportare duală R + $) ##########")
    grid: dict[str, dict[str, Any]] = {}
    for reg in regimes:
        grid[reg["label"]] = {}
        print(f"\n=== {reg['label'].upper()} ===")
        for nm, sp in zip(names, stops):
            cell = _cell(reg, sp)
            grid[reg["label"]][nm] = cell
            print(f"  {nm:12s} stop={sp:5.1f}p n={cell['n_trades']:5d} WR={cell['winrate']} "
                  f"E_R={cell['expectancy_R']:+.4f} E_$={cell['expectancy_dollars']:+.4f} "
                  f"netR={cell['net_sumR']:+.1f} net$={cell['net_sum_dollars']:+.1f} "
                  f"best/sumR={cell['best_over_sumR']} wo1R={cell['wo1_netR']}")

    # ---- VERDICT MECANIC (pe expectancy_$) ----
    labels = [r["label"] for r in regimes]
    all_nonpos = all(grid[lb][nm]["expectancy_dollars"] <= 0 for lb in labels for nm in names)
    wider_names = [names[k] for k in wider3]
    regimes_with_2wider_pos = sum(
        1 for lb in labels if sum(1 for nm in wider_names if grid[lb][nm]["expectancy_dollars"] > 0) >= 2)
    if all_nonpos:
        verdict = "ÎNCHIS DEFINITIV (expectancy_$ ≤ 0 la toate 5 stopurile, în toate 3 regimurile)"
    elif regimes_with_2wider_pos >= 2:
        verdict = ("MERITĂ IPOTEZĂ NOUĂ (expectancy_$ > 0 la ≥2 din stopurile largi, în ≥2 regimuri) — "
                   "raportez, NU pre-înregistrez, NU rulez; Statisticianul formulează")
    else:
        verdict = "AMBIGUOUS / TESTABLE-BUT-INSUFFICIENT (tipar amestecat sau un singur regim/punct)"
    print(f"\n########## VERDICT MECANIC (citit din prag, nu ales): {verdict} ##########")

    out = dict(measurement_A=measA, stops_pips=dict(zip(names, stops)), wider3=wider_names,
               diagnostic=grid, verdict=verdict, model_notes=dict(
                   exit_model="stop-loss intrabar ±X pe [entry,entry+20] + time-exit close[entry+20]",
                   decision_variable="expectancy_dollars", cost=COST, tick=TICK, horizon=H))
    path = os.path.join(_ROOT, "reports", "lm001_s1v2_stop_geometry_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"\nrecord -> reports/lm001_s1v2_stop_geometry_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

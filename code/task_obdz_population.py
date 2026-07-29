"""OBDZ-001 — NUMĂRAREA POPULAȚIEI eligibile (pre-înregistrare Statistician, doc cfb9a5f, v2.7.10 75deeca).

READ-ONLY, in-sample, M15_v2 130.491 bare, loader v6. NU implementez mașina de stare, NU calculez P&L, NU
simulez tranzacții. Numeri geometrie + filtre. GARD 2 neatins, sigilat intact.

LANȚUL DE FILTRE (survivori la fiecare pas), per regim:
  1  bias H1/H4 aliniat   — bare unde h1_trend_up ȘI h4_trend_up sunt CONSISTENTE (ambele up / ambele down)
  2  DemandZone detectate — câte zone
  3  OB nemitigat în zonă — intersecția cross-candle (Decizia 3): OB_B (kind=bias@t) cu prima Mitigation
                            calificată la bara t (scan de la formation_idx+2), bias@t aliniat & = kind_B, ȘI
                            EXISTĂ o DemandZone_A cu: kind_A==kind_B, formation_A != formation_B, formation_A<t
                            (forward-safe), |formation_A−formation_B|<=460, ACELAȘI bloc, ȘI suprapunere de
                            interval OB_B.body × DemandZone_A.range.
  4  podeaua de ATR       — atr14[t] >= 0,857$ (= 3×0,20/0,7)

BIAS — DISCOVERY-SAFE: `ema20>ema50` (ewm span 20/50, formula mtf.py:98-102) pe timeframe-urile CONTEXT-
DERIVATE `H1_from_M15_v2`/`H4_from_M15_v2` (livrate discovery-safe de loader), merjuit forward-safe cu
`avail=time.shift(-1)` (bara HTF completă). ⚠ SEMNALARE: NU folosesc calea `mtf.py::load_mtf` (care citește
CSV-uri H1/H4 NATIVE brute, ocolind masca de holdout — H1 nativ e AWAITING_REGIME_MAP, 100% sigilat); folosesc
sursa context-derivată discovery-safe, cu ACEEAȘI formulă. Dacă Statisticianul intenționa H1 nativ, e imposibil
discovery-safe și cere reconfirmare.

PRAG pre-înregistrat: n>=25 per regim; sub → INSUFFICIENT_N pentru acel regim. Raportez și mă opresc — fără
ajustări de filtru.
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
from order_block_void import OrderBlockKind
from order_flow import detect_demand_zones, detect_order_blocks

ATR_FLOOR = 3.0 * 0.20 / 0.7          # ≈ 0,857$
HORIZON, WEEK_BARS, N_MIN = 20, 460, 25
EXPECTED = {"bear": 52_403, "bull": 52_851, "correction": 25_237}


def _htf_trend(dfh: Any, period: int) -> Any:
    ema20 = dfh["close"].ewm(span=20).mean(); ema50 = dfh["close"].ewm(span=50).mean()
    tu = (ema20 > ema50).astype(float)
    avail = dfh["time"].shift(-1)
    avail.iloc[-1] = int(dfh["time"].iloc[-1]) + period
    return pd.DataFrame({"avail": avail.astype("int64"), "trend_up": tu.to_numpy()})


def _day_index(time: Any) -> np.ndarray:
    dt = pd.to_datetime(time, unit="s", utc=True)
    ny = dt.dt.tz_convert("America/New_York").dt.tz_localize(None)
    days = (ny - pd.Timedelta(hours=17)).dt.floor("D").values.astype("datetime64[D]").astype("int64")
    return np.asarray(days, dtype=np.int64)


def _first_mitigation(ob: Any, high: Any, low: Any, close: Any, n: int) -> int | None:
    """Prima Mitigation calificată = detect_mitigations(...)[0].event_idx, dar cu ieșire timpurie (perf).
    Replică EXACT logica înghețată: scan de la formation_idx+2, oprire la breaker (close sub podea/peste plafon)."""
    zl, zh = ob.zone_lower, ob.zone_upper
    bull = ob.kind is OrderBlockKind.BULLISH
    floor, ceiling = low[ob.formation_idx], high[ob.formation_idx]
    for i in range(ob.formation_idx + 2, n):
        if bull and close[i] < floor:
            return None
        if (not bull) and close[i] > ceiling:
            return None
        if low[i] <= zh and high[i] >= zl:
            return i
    return None


def _dist(a: np.ndarray) -> dict[str, Any]:
    a = a[np.isfinite(a)]
    if not len(a):
        return {}
    return dict(n=int(len(a)), min=round(float(a.min()), 3), p25=round(float(np.percentile(a, 25)), 3),
                median=round(float(np.percentile(a, 50)), 3), p75=round(float(np.percentile(a, 75)), 3),
                max=round(float(a.max()), 3), mean=round(float(a.mean()), 3))


def _regime_label(seg: dict[str, Any], i: int) -> str:
    for k in ("regime", "label", "name"):
        v = seg.get(k)
        if isinstance(v, str):
            return v.lower()
    return ["bear", "bull", "correction"][i]


def main() -> int:
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh1, _ = load("H1_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh4, _ = load("H4_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | M15={len(dfm)} H1={len(dfh1)} H4={len(dfh4)} | ATR_FLOOR={ATR_FLOOR:.4f}$")
    if len(dfm) != 130_491:
        print(f"STOP: M15 {len(dfm)} bare."); return 2

    dfm = dfm.sort_values("time").reset_index(drop=True)
    h1 = _htf_trend(dfh1, 3600).sort_values("avail")
    h4 = _htf_trend(dfh4, 4 * 3600).sort_values("avail")
    dfm = pd.merge_asof(dfm, h1.rename(columns={"trend_up": "h1"}), left_on="time", right_on="avail",
                        direction="backward").drop(columns="avail")
    dfm = pd.merge_asof(dfm, h4.rename(columns={"trend_up": "h4"}), left_on="time", right_on="avail",
                        direction="backward").drop(columns="avail")
    dfm["day"] = _day_index(dfm["time"])
    t_all = dfm["time"].to_numpy()

    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]
    out: dict[str, Any] = {"ATR_FLOOR": round(ATR_FLOOR, 4), "N_MIN": N_MIN, "regimes": {}}
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].to_numpy(); h = sub["high"].to_numpy(); l = sub["low"].to_numpy(); c = sub["close"].to_numpy()
        atr = sub["atr14"].to_numpy(); h1v = sub["h1"].to_numpy(); h4v = sub["h4"].to_numpy(); day = sub["day"].to_numpy()
        bias_up = (h1v > 0.5) & (h4v > 0.5)
        bias_dn = (h1v <= 0.5) & (h4v <= 0.5) & np.isfinite(h1v) & np.isfinite(h4v)
        # ultima bară a fiecărei zile (pt. EOD)
        eod = np.empty(n, dtype=np.int64)
        last = n - 1
        for j in range(n - 1, -1, -1):
            if j < n - 1 and day[j] != day[j + 1]:
                last = j
            eod[j] = last

        step1 = int((bias_up | bias_dn).sum())
        obs = detect_order_blocks(o.tolist(), h.tolist(), l.tolist(), c.tolist(), n)
        dzs = detect_demand_zones(o.tolist(), h.tolist(), l.tolist(), c.tolist(), n)
        step2 = len(dzs)

        dz_by_kind: dict[Any, list[Any]] = {OrderBlockKind.BULLISH: [], OrderBlockKind.BEARISH: []}
        for dz in dzs:
            dz_by_kind[dz.kind].append(dz)

        survivors: list[tuple[int, float, int]] = []       # (t, atr_t, eff_horizon)
        step3 = 0
        for ob in obs:
            t = _first_mitigation(ob, h.tolist(), l.tolist(), c.tolist(), n)
            if t is None or t + 1 >= n:
                continue
            obdir = 1 if ob.kind is OrderBlockKind.BULLISH else -1
            biasdir = 1 if bias_up[t] else (-1 if bias_dn[t] else 0)
            if biasdir != obdir:
                continue
            ok = False
            for dz in dz_by_kind[ob.kind]:                  # (a) kind_A==kind_B
                if dz.formation_idx == ob.formation_idx:    # (b) formare diferită
                    continue
                if dz.formation_idx >= t:                   # (c) forward-safe
                    continue
                if abs(dz.formation_idx - ob.formation_idx) > WEEK_BARS:   # (d)
                    continue
                if ob.zone_lower <= dz.zone_upper and ob.zone_upper >= dz.zone_lower:   # suprapunere
                    ok = True; break
            if not ok:
                continue
            step3 += 1
            if atr[t] >= ATR_FLOOR:                          # (4) podea ATR
                entry = t + 1
                eff = min(entry + HORIZON, int(eod[entry])) - entry
                survivors.append((t, float(atr[t]), int(eff)))

        step4 = len(survivors)
        atr_surv = np.array([s[1] for s in survivors]); hor_surv = np.array([float(s[2]) for s in survivors])
        insufficient = step4 < N_MIN
        rec = dict(step1_bias_aligned_bars=step1, step2_demandzones=step2,
                   step3_composite_triggers=step3, step4_after_atr_floor=step4,
                   INSUFFICIENT_N=insufficient,
                   atr_at_survivors=_dist(atr_surv), effective_horizon_dist=_dist(hor_surv),
                   horizon_buckets={"lt10": int((hor_surv < 10).sum()) if step4 else 0,
                                    "ge10": int((hor_surv >= 10).sum()) if step4 else 0})
        out["regimes"][label] = rec
        print(f"\n=== {label.upper()} ({n} bare) ===")
        print(f"  1 bias aliniat : {step1}")
        print(f"  2 DemandZones  : {step2}")
        print(f"  3 compus (OB nemitigat×DZ, bias) : {step3}")
        print(f"  4 după podea ATR : {step4}   {'← INSUFFICIENT_N (<25)' if insufficient else ''}")
        if step4:
            print(f"  ATR@survivori : {rec['atr_at_survivors']}")
            print(f"  orizont efectiv: {rec['effective_horizon_dist']}  buckets {rec['horizon_buckets']}")

    any_insuf = [lb for lb, r in out["regimes"].items() if r["INSUFFICIENT_N"]]
    print(f"\n########## INSUFFICIENT_N: {any_insuf if any_insuf else 'niciun regim'} ##########")
    path = os.path.join(_ROOT, "reports", "obdz001_population_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("record -> reports/obdz001_population_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

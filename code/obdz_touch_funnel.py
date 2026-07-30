"""OBDZ — pâlnia în ATINGERI, la nivel de ZONĂ, unitate consistentă (Statistician v2.7.17, 89e76a2). READ-ONLY.

Pur descriptivă. NU relaxează niciun filtru, NU măsoară tipuri noi de zonă (neautorizate), NU interpretează.
GARD 2 neatins, sigilat intact. Unde e colapsul de frecvență, în UNITATE DE ZONĂ (nu bare, nu evenimente).

PÂLNIE (toate în ZONE — DemandZone din `detect_demand_zones`, [low,high] al barei-ancoră):
  DETECTED  câte DemandZone se detectează (5.560 = 2.275+2.107+1.178).
  T1 ATINSE dintre ele, câte sunt ATINSE cel puțin o dată — prima bară τ >= formation+2 (sărind impulsul,
            post-fix circularitate) unde `low[τ]<=zone_upper ȘI high[τ]>=zone_lower`, în ACELAȘI bloc. Per zonă.
  T2 OB     dintre atinse, câte au un OB nemitigat CROSS-CANDLE suprapus la momentul primei atingeri τ
            (Decizia 3: kind identic, formare diferită, |Δformation|<=460, formation_OB<τ, suprapunere de
            interval corp-OB × range-zonă, OB NEMITIGAT la τ = τ < prima mitigare/breaker a OB-ului).
  T3 BIAS   dintre acelea, câte au bias (H1+H4) aliniat & = polaritatea zonei, la bara atingerii τ. = final.

Raportat PER REGIM, AGREGAT, ȘI pe POLARITATE (demand=bullish / supply=bearish).
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
from order_block_void import OrderBlock, OrderBlockKind
from order_flow import detect_demand_zones, detect_order_blocks

WEEK_BARS = 460
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}
EXPECTED_ZONES = {"bear": 2_275, "bull": 2_107, "correction": 1_178}


def _htf_trend(dfh: Any, period: int) -> Any:
    ema20 = dfh["close"].ewm(span=20).mean(); ema50 = dfh["close"].ewm(span=50).mean()
    tu = (ema20 > ema50).astype(float)
    avail = dfh["time"].shift(-1); avail.iloc[-1] = int(dfh["time"].iloc[-1]) + period
    return pd.DataFrame({"avail": avail.astype("int64"), "trend_up": tu.to_numpy()})


def _day_index(time: Any) -> np.ndarray:
    dt = pd.to_datetime(time, unit="s", utc=True)
    ny = dt.dt.tz_convert("America/New_York").dt.tz_localize(None)
    d = (ny - pd.Timedelta(hours=17)).dt.floor("D").values.astype("datetime64[D]").astype("int64")
    return np.asarray(d, dtype=np.int64)


def _unmit_until(ob: OrderBlock, high: np.ndarray, low: np.ndarray, close: np.ndarray, n: int) -> int:
    """Prima bară >= formation+2 unde OB e mitigat (atingere de corp) SAU rupt (breaker). Altfel n (niciodată)."""
    zl, zh = ob.zone_lower, ob.zone_upper
    bull = ob.kind is OrderBlockKind.BULLISH
    f = ob.formation_idx
    floor, ceiling = low[f], high[f]
    for i in range(f + 2, n):
        if bull and close[i] < floor:
            return i
        if (not bull) and close[i] > ceiling:
            return i
        if low[i] <= zh and high[i] >= zl:
            return i
    return n


def _regime_label(seg: dict[str, Any], i: int) -> str:
    for k in ("regime", "label", "name"):
        v = seg.get(k)
        if isinstance(v, str):
            return v.lower()
    return ["bear", "bull", "correction"][i]


def _blank() -> dict[str, int]:
    return {"detected": 0, "T1_touched": 0, "T2_ob_overlap": 0, "T3_bias_final": 0}


def _pct(a: int, b: int) -> str:
    return f"{100.0 * a / b:.1f}%" if b else "-"


def _print_funnel(tag: str, d: dict[str, int]) -> None:
    print(f"  {tag:7s} detected={d['detected']:4d} → atinse={d['T1_touched']:4d} ({_pct(d['T1_touched'], d['detected'])}) "
          f"→ OB_overlap={d['T2_ob_overlap']:4d} ({_pct(d['T2_ob_overlap'], d['T1_touched'])}) "
          f"→ bias_final={d['T3_bias_final']:4d} ({_pct(d['T3_bias_final'], d['T2_ob_overlap'])})")


def main() -> int:
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh1, _ = load("H1_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh4, _ = load("H4_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | M15={len(dfm)}")
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

    out: dict[str, Any] = {"per_regime": {}}
    agg: dict[str, dict[str, int]] = {"demand": _blank(), "supply": _blank(), "TOTAL": _blank()}
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy()
        hi = np.asarray(h); lo = np.asarray(l); cl = np.asarray(c)
        bias_up = (h1 > 0.5) & (h4 > 0.5)
        bias_dn = (h1 <= 0.5) & (h4 <= 0.5) & np.isfinite(h1) & np.isfinite(h4)

        obs = detect_order_blocks(o, h, l, c, n)
        dzs = detect_demand_zones(o, h, l, c, n)
        if EXPECTED_ZONES.get(label) not in (None, len(dzs)):
            print(f"STOP: {label} zone = {len(dzs)}, aștept {EXPECTED_ZONES[label]}."); return 4
        # OB-uri per polaritate, cu unmit_until precalculat
        ob_by_kind: dict[OrderBlockKind, list[tuple[int, float, float, int]]] = {OrderBlockKind.BULLISH: [], OrderBlockKind.BEARISH: []}
        for ob in obs:
            ob_by_kind[ob.kind].append((ob.formation_idx, ob.zone_lower, ob.zone_upper, _unmit_until(ob, hi, lo, cl, n)))

        pol = {"demand": _blank(), "supply": _blank()}
        for dz in dzs:
            polarity = "demand" if dz.kind is OrderBlockKind.BULLISH else "supply"
            pol[polarity]["detected"] += 1
            # T1: prima atingere a range-ului complet, de la formation+2
            f = dz.formation_idx
            mask = (lo <= dz.zone_upper) & (hi >= dz.zone_lower)
            mask[:f + 2] = False
            if not mask.any():
                continue
            tau = int(np.argmax(mask))
            pol[polarity]["T1_touched"] += 1
            # T2: OB cross-candle nemitigat, suprapus, la τ
            found = False
            for (fo, obl, obu, unmit) in ob_by_kind[dz.kind]:
                if fo == f or fo >= tau:                            # formare diferită + forward-safe
                    continue
                if abs(fo - f) > WEEK_BARS:
                    continue
                if unmit <= tau:                                    # OB deja mitigat/rupt la τ
                    continue
                if obl <= dz.zone_upper and obu >= dz.zone_lower:   # suprapunere interval
                    found = True
                    break
            if not found:
                continue
            pol[polarity]["T2_ob_overlap"] += 1
            # T3: bias aliniat & = polaritatea zonei la τ
            aligned = bool(bias_up[tau]) if polarity == "demand" else bool(bias_dn[tau])
            if aligned:
                pol[polarity]["T3_bias_final"] += 1

        total = {k: pol["demand"][k] + pol["supply"][k] for k in _blank()}
        out["per_regime"][label] = {"demand": pol["demand"], "supply": pol["supply"], "TOTAL": total}
        for p in ("demand", "supply"):
            for k in _blank():
                agg[p][k] += pol[p][k]
                agg["TOTAL"][k] += pol[p][k]
        print(f"\n=== {label.upper()} ({n} bare) ===")
        _print_funnel("demand", pol["demand"]); _print_funnel("supply", pol["supply"]); _print_funnel("TOTAL", total)

    out["aggregate"] = agg
    print("\n=== AGREGAT ===")
    for p in ("demand", "supply", "TOTAL"):
        _print_funnel(p, agg[p])
    path = os.path.join(_ROOT, "reports", "obdz_touch_funnel_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/obdz_touch_funnel_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

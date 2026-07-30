"""SARCINA 2 — numărătoarea celor 3 VARIANTE de confirmare M15 (Statistician v2.7.26, 933f615, doc 79c1218).

READ-ONLY, in-sample, M15_v2. DOAR numărători — FĂRĂ rulări, FĂRĂ P&L, FĂRĂ test WP-5'. GARD 2 neatins,
sigilat intact. GARD 1 neatins (nu se apelează `ProductionPipeline.execute()` — numărătoare, nu rulare).

POPULAȚIA = cele 654 declanșatoare COMPUSE BRUTE (275/223/156), `detect_obdz001_signals(atr_floor=-1e18)`,
Decizia 3 neatinsă. Ancora = bara t = `trigger_idx` (prima Mitigation a OB_B). Recuperez OB_B (zona-corp)
per declanșator REPLICÂND BUCLA ÎNGHEȚATĂ din `obdz001.detect_obdz001_signals` (aceleași primitive înghețate,
aceiași predicați), și VERIFIC că mulțimea (trigger_idx, entry_idx, direction) coincide EXACT cu ieșirea
funcției oficiale — altfel STOP. OB_B e necesar DOAR pentru re-atingerea din V1 (span-overlap = testul de
mitigare deja ratificat, echivalent `price_in_zone`/interactions).

VARIANTE (spec direction_2, verbatim; anchor = t, bias = direction declanșatorului):
  V1 Dublă Respingere : bara 1 = t. Caut q ∈ {t+1, t+2}, PRIMA cu re-atingere a zonei OB_B (span overlap)
                        ȘI închidere fără a coborî sub extrema barei t (long: close[q]>=low[t]; short:
                        close[q]<=high[t]). Găsită → entry=q+1, SL long min(low[t],low[q]) / short
                        max(high[t],high[q]), sizing=q. Altfel ABANDONAT pt. acest declanșator.
  V2 Inside Bar Break : bara 1=t, bara 2=t+1 inside-bar COMPLET (high[t+1]<=high[t] ȘI low[t+1]>=low[t]),
                        bara 3=t+2 RUPE ȘI închide dincolo de extrema barei 2 în direcția bias-ului (long:
                        high[t+2]>high[t+1] ȘI close[t+2]>high[t+1]; short simetric). Ambele exact → entry=t+3
                        ('lumânarea 4'), SL long low[t+1] / short high[t+1], sizing=t+2. Secvență fixă, nu căutare.
  V3 Shift Bar        : bara 1=t cu cerință de CULOARE (long: bearish close[t]<open[t]; short: bullish). Bara
                        2=t+1 culoare opusă, corp mai mare ca al barei 1 ȘI corp>=60% din range-ul propriu.
                        Confirmat → entry=t+2, SL long min(low[t],low[t+1]) / short max(high[t],high[t+1]),
                        sizing=t+1.
INSIDE BAR = construit aici (nu exista primitivă): high[t+1]<=high[t] ȘI low[t+1]>=low[t].

PODEA GENERALIZATĂ (direction_2): R = |entry_price − sl_price| (nivel geometric, per variantă), entry_price =
open[entry_idx]; podea de eligibilitate R >= 3×cost = $0,60 aplicată direct pe R-ul realizat al fiecărei tranzacții.
SUPRAVIEȚUITOR = confirmarea ține ȘI entry valid ȘI R >= 0,60. Prag N_MIN=25/regim aplicat pe SUPRAVIEȚUITORI
(precedentul gate-ului OBDZ-002-cu-confirmare, v2.7.22-23). Dacă ORICE regim < 25 → varianta ABANDONATĂ (întreagă).
Raportat per regim, agregat, ȘI pe polaritate (demand=long / supply=short) — obligatoriu.
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
from obdz001 import WEEK_BARS, _eod_per_bar, _first_mitigation, detect_obdz001_signals

COST = 0.20
R_FLOOR = 3.0 * COST                 # = $0,60, podea generalizată pe R geometric
N_MIN = 25
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}
EXPECTED_RAW = {"bear": 275, "bull": 223, "correction": 156}


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


def _regime_label(seg: dict[str, Any], i: int) -> str:
    for k in ("regime", "label", "name"):
        v = seg.get(k)
        if isinstance(v, str):
            return v.lower()
    return ["bear", "bull", "correction"][i]


class Trigger:
    """Un declanșator compus brut: bara t + polaritatea + zona-corp OB_B (pt. re-atingerea din V1)."""
    __slots__ = ("t", "d", "entry_idx", "ob_lower", "ob_upper")

    def __init__(self, t: int, d: int, entry_idx: int, ob_lower: float, ob_upper: float) -> None:
        self.t = t; self.d = d; self.entry_idx = entry_idx; self.ob_lower = ob_lower; self.ob_upper = ob_upper


def _recover_triggers(
    o: list[float], h: list[float], l: list[float], c: list[float],
    h1: np.ndarray, h4: np.ndarray, day: np.ndarray, n: int,
) -> list[Trigger]:
    """Replică EXACT bucla înghețată din `detect_obdz001_signals` (podea -inf), capturând ȘI zona OB_B.
    Aceleași primitive/predicați înghețați; verificarea de coincidență se face în `main`."""
    obs = detect_order_blocks(o, h, l, c, n)
    dzs = detect_demand_zones(o, h, l, c, n)
    eod = _eod_per_bar(day.tolist(), n)
    dz_by_kind: dict[OrderBlockKind, list[Any]] = {OrderBlockKind.BULLISH: [], OrderBlockKind.BEARISH: []}
    for dz in dzs:
        dz_by_kind[dz.kind].append(dz)
    out: list[Trigger] = []
    for ob in obs:
        t = _first_mitigation(ob, h, l, c, n)
        if t is None or t + 1 >= n:
            continue
        obdir = 1 if ob.kind is OrderBlockKind.BULLISH else -1
        bias_up = h1[t] > 0.5 and h4[t] > 0.5
        bias_dn = h1[t] <= 0.5 and h4[t] <= 0.5
        biasdir = 1 if bias_up else (-1 if bias_dn else 0)
        if biasdir != obdir:
            continue
        ok = False
        for dz in dz_by_kind[ob.kind]:
            if dz.formation_idx == ob.formation_idx:
                continue
            if dz.formation_idx >= t:
                continue
            if abs(dz.formation_idx - ob.formation_idx) > WEEK_BARS:
                continue
            if ob.zone_lower <= dz.zone_upper and ob.zone_upper >= dz.zone_lower:
                ok = True
                break
        if not ok:
            continue
        # podea -inf → fără filtru ATR; entry = t+1 (doar pt. verificarea de coincidență cu funcția oficială)
        out.append(Trigger(t, obdir, t + 1, float(ob.zone_lower), float(ob.zone_upper)))
    return out


def _span_overlap(lo_bar: float, hi_bar: float, zl: float, zh: float) -> bool:
    """Re-atingere = suprapunere de interval bară↔zonă (principiul span-overlap de la Mitigation)."""
    return lo_bar <= zh and hi_bar >= zl


def _v1(tr: Trigger, o: list[float], h: list[float], l: list[float], c: list[float], n: int) -> float | None:
    """R geometric dacă V1 confirmă (cu entry valid), altfel None."""
    t, d = tr.t, tr.d
    for q in (t + 1, t + 2):
        if q >= n:
            break
        if not _span_overlap(l[q], h[q], tr.ob_lower, tr.ob_upper):
            continue
        if (d > 0 and c[q] >= l[t]) or (d < 0 and c[q] <= h[t]):
            entry = q + 1
            if entry >= n:
                return None
            sl = min(l[t], l[q]) if d > 0 else max(h[t], h[q])
            return abs(float(o[entry]) - sl)
    return None


def _v2(tr: Trigger, o: list[float], h: list[float], l: list[float], c: list[float], n: int) -> float | None:
    t, d = tr.t, tr.d
    if t + 3 >= n:
        return None
    if not (h[t + 1] <= h[t] and l[t + 1] >= l[t]):        # inside bar complet
        return None
    if d > 0:
        if not (h[t + 2] > h[t + 1] and c[t + 2] > h[t + 1]):
            return None
        sl = l[t + 1]
    else:
        if not (l[t + 2] < l[t + 1] and c[t + 2] < l[t + 1]):
            return None
        sl = h[t + 1]
    entry = t + 3
    return abs(float(o[entry]) - sl)


def _v3(tr: Trigger, o: list[float], h: list[float], l: list[float], c: list[float], n: int) -> float | None:
    t, d = tr.t, tr.d
    if t + 2 >= n:
        return None
    body_t = abs(c[t] - o[t]); body_1 = abs(c[t + 1] - o[t + 1]); rng_1 = h[t + 1] - l[t + 1]
    if d > 0:
        col_t = c[t] < o[t]; col_1 = c[t + 1] > o[t + 1]                 # t bearish, t+1 bullish
        sl = min(l[t], l[t + 1])
    else:
        col_t = c[t] > o[t]; col_1 = c[t + 1] < o[t + 1]                 # t bullish, t+1 bearish
        sl = max(h[t], h[t + 1])
    if not (col_t and col_1):
        return None
    if not (body_1 > body_t and body_1 >= 0.6 * rng_1):
        return None
    entry = t + 2
    return abs(float(o[entry]) - sl)


def _blank() -> dict[str, int]:
    return {"composite": 0, "confirmed": 0, "survivor": 0}


def main() -> int:
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh1, _ = load("H1_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh4, _ = load("H4_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | M15={len(dfm)} | populație = 654 compuse brute | R_floor=${R_FLOOR:.2f} | N_MIN={N_MIN}")
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

    variants = ("V1_double_rejection", "V2_inside_bar_breakout", "V3_shift_bar")
    fns = {"V1_double_rejection": _v1, "V2_inside_bar_breakout": _v2, "V3_shift_bar": _v3}
    out: dict[str, Any] = {"population": "654 raw composite", "R_floor": R_FLOOR, "N_MIN": N_MIN, "regimes": {}}
    agg: dict[str, dict[str, dict[str, int]]] = {v: {"demand": _blank(), "supply": _blank(), "TOTAL": _blank()} for v in variants}

    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        atr = sub["atr14"].to_numpy(); h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy(); day = sub["day"].to_numpy()

        # populația oficială (autoritate pe cifre) + recuperarea OB_B (autoritate pe zonă) — trebuie să coincidă
        official = detect_obdz001_signals(o, h, l, c, atr.tolist(), h1.tolist(), h4.tolist(), day.tolist(), n, atr_floor=-1e18)
        if EXPECTED_RAW.get(label) not in (None, len(official)):
            print(f"STOP: {label} compuse brute = {len(official)}, aștept {EXPECTED_RAW[label]}."); return 4
        triggers = _recover_triggers(o, h, l, c, h1, h4, day, n)
        key_off = sorted((s.trigger_idx, s.entry_idx, s.direction) for s in official)
        key_rec = sorted((tr.t, tr.entry_idx, tr.d) for tr in triggers)
        if key_off != key_rec:
            print(f"STOP: {label} recuperarea OB_B NU coincide cu funcția oficială "
                  f"({len(key_rec)} vs {len(key_off)})."); return 5

        per_v: dict[str, Any] = {}
        for v in variants:
            fn = fns[v]
            st = {"demand": _blank(), "supply": _blank(), "TOTAL": _blank()}
            for tr in triggers:
                pol = "demand" if tr.d > 0 else "supply"
                for grp in (pol, "TOTAL"):
                    st[grp]["composite"] += 1
                r = fn(tr, o, h, l, c, n)
                if r is None:
                    continue
                for grp in (pol, "TOTAL"):
                    st[grp]["confirmed"] += 1
                if np.isfinite(r) and r >= R_FLOOR:
                    for grp in (pol, "TOTAL"):
                        st[grp]["survivor"] += 1
            per_v[v] = st
            for grp in ("demand", "supply", "TOTAL"):
                for kk in ("composite", "confirmed", "survivor"):
                    agg[v][grp][kk] += st[grp][kk]
        out["regimes"][label] = per_v

        print(f"\n=== {label.upper()} ({n} bare, compuse={len(triggers)}) ===")
        for v in variants:
            tt = per_v[v]["TOTAL"]; dd = per_v[v]["demand"]; ss = per_v[v]["supply"]
            flag = " ← INSUFFICIENT_N (<25)" if tt["survivor"] < N_MIN else ""
            print(f"  {v:24s} confirmate={tt['confirmed']:3d}  supraviețuitori(R>=0,60)={tt['survivor']:3d}{flag}")
            print(f"      demand: conf={dd['confirmed']:3d} surv={dd['survivor']:3d}   "
                  f"supply: conf={ss['confirmed']:3d} surv={ss['survivor']:3d}")

    # verdict de prag: o variantă e ABANDONATĂ dacă ORICE regim are supraviețuitori < 25
    print("\n########## VERDICT DE PRAG (supraviețuitori/regim, N_MIN=25) ##########")
    verdicts: dict[str, Any] = {}
    for v in variants:
        by_reg = {lab: out["regimes"][lab][v]["TOTAL"]["survivor"] for lab in out["regimes"]}
        min_reg = min(by_reg.values()) if by_reg else 0
        abandoned = any(x < N_MIN for x in by_reg.values())
        verdicts[v] = {"survivors_by_regime": by_reg, "min_regime": min_reg, "abandoned": abandoned}
        status = "ABANDONATĂ (un regim < 25)" if abandoned else "trece pragul în toate regimurile (candidată la rulare)"
        print(f"  {v:24s} {by_reg}  → {status}")
    out["aggregate"] = agg
    out["threshold_verdict"] = verdicts

    path = os.path.join(_ROOT, "reports", "obdz_confirmation_variants_count_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/obdz_confirmation_variants_count_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

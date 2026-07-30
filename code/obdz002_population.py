"""OBDZ-002 — numărătoarea de populație (gate INSUFFICIENT_N). Sarcină unică, read-only (Statistician v2.7.21).

Refoloseste lanțul OBDZ-001 (`detect_obdz001_signals`, înghețat), SINGURA schimbare = ELIGIBILITATEA:
podeaua de ATR re-derivată la SL=1,0×ATR → `3×cost/1,0 = 3×0,20/1,0 = 0,60$` (față de 0,857 la SL=0,7×).
NU rulează OBDZ-002 (fără P&L, fără test). GARD 2 neatins, sigilat intact. Prag n>=25/regim → INSUFFICIENT_N.

⚠ SEMNALARE (conformă cu disciplina de ambiguitate): doc-ul OBDZ-002 (7ca2781) specifică intrarea ca
`declanșator compus (Decizia 3) + CONFIRMARE (Varianta 3, impuls E010 la/după bara t)`, iar ATR-ul de sizing
= ATR14 la bara de CONFIRMARE. DAR fereastra de așteptare a confirmării e explicit „de derivat, nu aleasă
acum" — deci NU pot număra confirmate fără ea, și mandatul spune „ce se schimbă: ELIGIBILITATEA" + „structura
e aceeași ca OBDZ-001". Prin urmare aici raportez lanțul OBDZ-001 cu podeaua re-derivată = **populația
PRE-CONFIRMARE (limită SUPERIOARĂ)**; populația finală OBDZ-002 (după confirmare) va fi ≤ aceasta. Podeaua se
aplică la ATR14[t] (bara declanșator), ca la OBDZ-001; doc-ul folosește ATR14 la confirmare — va diferi la
implementarea mașinii de stare. Semnalez, nu inventez fereastra de confirmare.
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
from order_flow import detect_demand_zones
from obdz001 import HORIZON, detect_obdz001_signals

ATR_FLOOR_002 = 3.0 * 0.20 / 1.0     # = 0,60$ (re-derivat la SL=1,0×ATR)
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


def _dist(a: np.ndarray) -> dict[str, Any]:
    a = a[np.isfinite(a)]
    if not len(a):
        return {}
    return dict(n=int(len(a)), min=round(float(a.min()), 2), p10=round(float(np.percentile(a, 10)), 2),
                p25=round(float(np.percentile(a, 25)), 2), median=round(float(np.percentile(a, 50)), 2),
                p75=round(float(np.percentile(a, 75)), 2), p90=round(float(np.percentile(a, 90)), 2),
                max=round(float(a.max()), 2))


def _eod(day: np.ndarray, n: int) -> np.ndarray:
    eod = np.empty(n, dtype=np.int64); last = n - 1
    for j in range(n - 1, -1, -1):
        if j < n - 1 and day[j] != day[j + 1]:
            last = j
        eod[j] = last
    return eod


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
    print(f"loader v6 | M15={len(dfm)} | podea OBDZ-002 = {ATR_FLOOR_002:.3f}$ (3×0,20/1,0) | H={HORIZON}")
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

    out: dict[str, Any] = {"ATR_FLOOR_002": round(ATR_FLOOR_002, 3), "N_MIN": N_MIN, "H": HORIZON, "regimes": {}}
    tot_n = 0; tot_days = 0.0; any_insuf: list[str] = []
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        days = (e_ep - s_ep) / 86400.0
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        atr = sub["atr14"].to_numpy(); h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy(); day = sub["day"].to_numpy()
        eod = _eod(day, n)

        bias_up = (h1 > 0.5) & (h4 > 0.5); bias_dn = (h1 <= 0.5) & (h4 <= 0.5) & np.isfinite(h1) & np.isfinite(h4)
        step1 = int((bias_up | bias_dn).sum())
        step2 = len(detect_demand_zones(o, h, l, c, n))
        raw = detect_obdz001_signals(o, h, l, c, atr.tolist(), h1.tolist(), h4.tolist(), day.tolist(), n, atr_floor=-1e18)
        if EXPECTED_RAW.get(label) not in (None, len(raw)):
            print(f"STOP: {label} declanșatoare compuse = {len(raw)}."); return 4
        step3 = len(raw)                                          # compus (fără podea) = 275/223/156
        elig = [s for s in raw if s.atr >= ATR_FLOOR_002]        # podeaua re-derivată 0,60
        step4 = len(elig)
        atr_surv = np.array([s.atr for s in elig])
        horizon_eff = np.array([float(min(s.entry_idx + HORIZON, int(eod[s.entry_idx])) - s.entry_idx) for s in elig])
        freq_wk = step4 * 7.0 / days
        insuf = step4 < N_MIN
        if insuf:
            any_insuf.append(label)
        tot_n += step4; tot_days += days
        out["regimes"][label] = dict(
            days=round(days, 1), years=round(days / 365.25, 3),
            step1_bias_bars=step1, step2_demandzones=step2, step3_composite=step3,
            step4_after_floor_0_60=step4, INSUFFICIENT_N=insuf,
            freq_per_week=round(freq_wk, 2), atr_at_survivors=_dist(atr_surv),
            effective_horizon=_dist(horizon_eff),
            horizon_buckets={"lt10": int((horizon_eff < 10).sum()), "ge10": int((horizon_eff >= 10).sum())})
        print(f"\n=== {label.upper()} ({n} bare, {days:.1f} zile / {days/365.25:.3f} ani) ===")
        print(f"  1 bias aliniat : {step1}")
        print(f"  2 DemandZones  : {step2}")
        print(f"  3 compus (fără podea) : {step3}")
        print(f"  4 după podea 0,60$ : {step4}   {'← INSUFFICIENT_N (<25)' if insuf else ''}")
        print(f"  frecvență = {freq_wk:.2f} tranzacții/săptămână")
        print(f"  ATR@survivori : {out['regimes'][label]['atr_at_survivors']}")
        print(f"  orizont efectiv: {out['regimes'][label]['effective_horizon']} buckets {out['regimes'][label]['horizon_buckets']}")

    agg_freq = tot_n * 7.0 / tot_days if tot_days else 0.0
    out["aggregate"] = dict(total_survivors=tot_n, total_days=round(tot_days, 1), freq_per_week=round(agg_freq, 2),
                            INSUFFICIENT_N_regimes=any_insuf)
    print(f"\n########## AGREGAT: {tot_n} survivori pe {tot_days:.1f} zile = {agg_freq:.2f} tranzacții/săptămână ##########")
    print(f"########## INSUFFICIENT_N: {any_insuf if any_insuf else 'niciun regim'} ##########")
    print("(NOTĂ: populație PRE-CONFIRMARE = limită SUPERIOARĂ; confirmarea Variantei 3 o va reduce — vezi docstring.)")
    path = os.path.join(_ROOT, "reports", "obdz002_population_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("record -> reports/obdz002_population_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

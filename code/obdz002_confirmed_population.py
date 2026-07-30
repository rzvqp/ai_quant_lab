"""OBDZ-002 — numărătoarea POST-CONFIRMARE (gate INSUFFICIENT_N). Read-only (Statistician v2.7.22, bcba8e8).

Procedura mecanică autorizată, EXACT ca în spec:
  PENTRU fiecare declanșator compus BRUT (654 = 275/223/156, step3, ÎNAINTE de orice podea):
    1. t = trigger_idx
    2. caută prima bară j ∈ {t+2, t+3, t+4, t+5} care satisface criteriul (a)+(b) din detect_order_blocks
       (impuls E010 + înghițire de corp) ÎN DIRECȚIA bias-ului (impuls bullish pt long / bearish pt short).
       bara 0=t (atingere), bara t+1 EXCLUSĂ (= intrarea automată OBDZ-001, nu poate fi propria confirmare).
    3. dacă nu există j → ABANDONAT (fără confirmare în fereastră).
    4. dacă există j → ATR de dimensionare = ATR14[j] (bara de CONFIRMARE, nu t); podea = 3×cost/1,0 = 0,60.
    5. dacă ATR14[j] < 0,60 → ABANDONAT (podea la j).
    6. altfel → SUPRAVIEȚUITOR OBDZ-002: entry_idx=j+1, atr=ATR14[j], entry_price=open[j+1].
Podeaua se aplică o SINGURĂ dată, la j (NU se pornește de la cei 651 filtrați la ATR[t] — corecția de procedură).
Confirmarea (a)+(b) = criteriul detect_order_blocks reutilizat verbatim: un OB cu bara de impuls (=formation_idx+1)
în fereastră și de aceeași polaritate. Prag n>=25/regim → INSUFFICIENT_N. Fără P&L, fără alte tipuri de zonă.
GARD 2 neatins, sigilat intact. Raportat per regim, agregat, ȘI pe polaritate (demand/supply).
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
from order_flow import detect_order_blocks
from obdz001 import HORIZON, detect_obdz001_signals

ATR_FLOOR_002 = 3.0 * 0.20 / 1.0     # = 0,60$ la ATR14[j]
CONF_LO, CONF_HI = 2, 5              # fereastra de confirmare [t+2, t+5]
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
    return dict(n=int(len(a)), min=round(float(a.min()), 2), median=round(float(np.percentile(a, 50)), 2),
                p25=round(float(np.percentile(a, 25)), 2), p75=round(float(np.percentile(a, 75)), 2),
                p90=round(float(np.percentile(a, 90)), 2), max=round(float(a.max()), 2))


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
    print(f"loader v6 | M15={len(dfm)} | fereastra confirmare [t+{CONF_LO},t+{CONF_HI}] | podea la ATR14[j] = {ATR_FLOOR_002:.2f}$")
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

    out: dict[str, Any] = {"floor": ATR_FLOOR_002, "N_MIN": N_MIN, "conf_window": [CONF_LO, CONF_HI], "regimes": {}}
    tot_surv = 0; tot_days = 0.0; any_insuf: list[str] = []
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        days = (e_ep - s_ep) / 86400.0
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        atr = sub["atr14"].to_numpy()
        h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy(); day = sub["day"].to_numpy()

        raw = detect_obdz001_signals(o, h, l, c, atr.tolist(), h1.tolist(), h4.tolist(), day.tolist(), n, atr_floor=-1e18)
        if EXPECTED_RAW.get(label) not in (None, len(raw)):
            print(f"STOP: {label} compuse = {len(raw)}."); return 4
        # confirmarea = OB cu bara de impuls (=formation_idx+1) în fereastră, de aceeași polaritate
        ob_impulse: dict[int, OrderBlockKind] = {ob.formation_idx + 1: ob.kind for ob in detect_order_blocks(o, h, l, c, n)}

        stats = {"demand": {"composite": 0, "confirmed": 0, "survivor": 0},
                 "supply": {"composite": 0, "confirmed": 0, "survivor": 0}}
        surv_atr: list[float] = []
        for s in raw:
            pol = "demand" if s.direction > 0 else "supply"
            want = OrderBlockKind.BULLISH if s.direction > 0 else OrderBlockKind.BEARISH
            stats[pol]["composite"] += 1
            t = s.trigger_idx
            j = -1
            for cand in range(t + CONF_LO, t + CONF_HI + 1):        # {t+2,...,t+5}
                if cand + 1 >= n:
                    break
                if ob_impulse.get(cand) is want:                    # confirmare în direcția bias-ului
                    j = cand
                    break
            if j < 0:
                continue
            stats[pol]["confirmed"] += 1
            aj = float(atr[j])
            if not np.isfinite(aj) or aj < ATR_FLOOR_002:            # podea la ATR14[j]
                continue
            stats[pol]["survivor"] += 1
            surv_atr.append(aj)

        surv = stats["demand"]["survivor"] + stats["supply"]["survivor"]
        conf = stats["demand"]["confirmed"] + stats["supply"]["confirmed"]
        comp = stats["demand"]["composite"] + stats["supply"]["composite"]
        freq = surv * 7.0 / days
        insuf = surv < N_MIN
        if insuf:
            any_insuf.append(label)
        tot_surv += surv; tot_days += days
        out["regimes"][label] = dict(days=round(days, 1), composite=comp, confirmed=conf, survivor=surv,
                                     INSUFFICIENT_N=insuf, freq_per_week=round(freq, 2),
                                     atr_at_survivors=_dist(np.asarray(surv_atr)),
                                     demand=stats["demand"], supply=stats["supply"])
        print(f"\n=== {label.upper()} ({days:.1f} zile) ===")
        print(f"  compuse(brut)={comp} → confirmate[t+2,t+5]={conf} → după podea la j={surv}   "
              f"{'← INSUFFICIENT_N (<25)' if insuf else ''}")
        print(f"    demand: {stats['demand']}   supply: {stats['supply']}")
        print(f"  frecvență = {freq:.2f} tranzacții/săptămână | ATR@survivori {out['regimes'][label]['atr_at_survivors']}")

    agg_freq = tot_surv * 7.0 / tot_days if tot_days else 0.0
    out["aggregate"] = dict(total_survivors=tot_surv, total_days=round(tot_days, 1),
                            freq_per_week=round(agg_freq, 2), INSUFFICIENT_N_regimes=any_insuf)
    print(f"\n########## AGREGAT: {tot_surv} supraviețuitori / {tot_days:.1f} zile = {agg_freq:.2f} tranzacții/săptămână ##########")
    print(f"########## INSUFFICIENT_N: {any_insuf if any_insuf else 'niciun regim'} ##########")
    path = os.path.join(_ROOT, "reports", "obdz002_confirmed_population_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("record -> reports/obdz002_confirmed_population_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

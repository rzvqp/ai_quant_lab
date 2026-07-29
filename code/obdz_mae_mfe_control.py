"""OBDZ — SARCINA 1: MAE + MFE + bara de atingere, cu CONTROL potrivit pe bias (Statistician v2.7.14, 47d742a).

READ-ONLY, in-sample. Decide dacă sarcinile 2-3 mai au rost. Livrez cifrele; Statisticianul citește grila.
NU interpretez, NU încadrez în grilă. GARD 2 neatins, sigilat intact.

POPULAȚIE ZONĂ: cele 275/223/156 declanșatoare compuse BRUTE (fără podeaua de ATR — comparație brut-la-brut).
CONTROL: 275/223/156 bare M15 alese ALEATORIU (fără înlocuire, sămânță 20260729) din populația „bias aliniat"
a fiecărui regim (pasul 1: 35.454/37.707/17.145 bare), direcția = direcția bias-ului la acea bară, fără podea
ATR — izolează contribuția SPECIFICĂ a intersecției compuse (DemandZone×OB) FAȚĂ DE simpla aliniere de bias.

MĂSURĂTOARE (identică pe ambele populații), pe fereastra `[entry, entry+92]` (entry=t+1, aceeași ca A'):
  MAE = excursie adversă maximă / ATR14[t];  MFE = excursie favorabilă maximă / ATR14[t]
  bar_MAE/bar_MFE = bara (relativ la entry) unde extremul e atins PRIMA DATĂ (argmin/argmax first-occurrence).
Raportez distribuții COMPLETE (min/p10/p25/median/p75/p90/max) pentru MAE, MFE, raport MFE/MAE, bar_MAE,
bar_MFE + fracțiile de secvențiere (bar_MAE<bar_MFE = adversul primul), separat zonă vs control, per regim+agregat.
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
from obdz001 import detect_obdz001_signals

WINDOW, SEED = 92, 20260729
EXPECTED_RAW = {"bear": 275, "bull": 223, "correction": 156}
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}


def _htf_trend(dfh: Any, period: int) -> Any:
    ema20 = dfh["close"].ewm(span=20).mean(); ema50 = dfh["close"].ewm(span=50).mean()
    tu = (ema20 > ema50).astype(float)
    avail = dfh["time"].shift(-1); avail.iloc[-1] = int(dfh["time"].iloc[-1]) + period
    return pd.DataFrame({"avail": avail.astype("int64"), "trend_up": tu.to_numpy()})


def _day_index(time: Any) -> np.ndarray:
    dt = pd.to_datetime(time, unit="s", utc=True)
    ny = dt.dt.tz_convert("America/New_York").dt.tz_localize(None)
    days = (ny - pd.Timedelta(hours=17)).dt.floor("D").values.astype("datetime64[D]").astype("int64")
    return np.asarray(days, dtype=np.int64)


def _dist(a: np.ndarray) -> dict[str, Any]:
    a = a[np.isfinite(a)]
    if not len(a):
        return {}
    return dict(n=int(len(a)), min=round(float(a.min()), 2), p10=round(float(np.percentile(a, 10)), 2),
                p25=round(float(np.percentile(a, 25)), 2), median=round(float(np.percentile(a, 50)), 2),
                p75=round(float(np.percentile(a, 75)), 2), p90=round(float(np.percentile(a, 90)), 2),
                max=round(float(a.max()), 2))


def _mae_mfe(entry: int, direction: int, atr: float, ep: float, hi: np.ndarray, lo: np.ndarray,
             n: int) -> tuple[float, float, int, int]:
    end = min(entry + WINDOW, n - 1)
    hh = hi[entry:end + 1]; ll = lo[entry:end + 1]
    if direction > 0:
        mae = ep - float(np.min(ll)); bmae = int(np.argmin(ll))
        mfe = float(np.max(hh)) - ep; bmfe = int(np.argmax(hh))
    else:
        mae = float(np.max(hh)) - ep; bmae = int(np.argmax(hh))
        mfe = ep - float(np.min(ll)); bmfe = int(np.argmin(ll))
    return max(0.0, mae) / atr, max(0.0, mfe) / atr, bmae, bmfe


def _measure(events: list[tuple[int, int, float, float]], hi: np.ndarray, lo: np.ndarray, n: int) -> dict[str, Any]:
    mae: list[float] = []; mfe: list[float] = []; bmae: list[int] = []; bmfe: list[int] = []; ratio: list[float] = []
    adv_first = fav_first = tie = 0
    for entry, d, atr, ep in events:
        ma, mf, ba, bf = _mae_mfe(entry, d, atr, ep, hi, lo, n)
        mae.append(ma); mfe.append(mf); bmae.append(ba); bmfe.append(bf)
        if ma > 0:
            ratio.append(mf / ma)
        if ba < bf:
            adv_first += 1
        elif ba > bf:
            fav_first += 1
        else:
            tie += 1
    tot = len(events)
    return dict(
        n=tot, MAE=_dist(np.asarray(mae)), MFE=_dist(np.asarray(mfe)),
        MFE_over_MAE=_dist(np.asarray(ratio)), bar_MAE=_dist(np.asarray(bmae, dtype=float)),
        bar_MFE=_dist(np.asarray(bmfe, dtype=float)),
        frac_adverse_first=round(adv_first / tot, 3) if tot else None,
        frac_favorable_first=round(fav_first / tot, 3) if tot else None,
        frac_tie=round(tie / tot, 3) if tot else None)


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
    print(f"loader v6 | M15={len(dfm)} | WINDOW={WINDOW} | seed={SEED}")
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

    out: dict[str, Any] = {"WINDOW": WINDOW, "seed": SEED, "zone": {}, "control": {}}
    # agregat = pooling de metrici per-eveniment (nu se pot re-măsura cross-segment: high/low sunt per-segment)
    zone_metrics_pool: dict[str, list[float]] = {"MAE": [], "MFE": [], "ratio": [], "bMAE": [], "bMFE": []}
    ctrl_metrics_pool: dict[str, list[float]] = {"MAE": [], "MFE": [], "ratio": [], "bMAE": [], "bMFE": []}
    zone_seq = {"adv": 0, "fav": 0, "tie": 0}; ctrl_seq = {"adv": 0, "fav": 0, "tie": 0}

    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        atr = sub["atr14"].to_numpy(); h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy(); day = sub["day"].to_numpy()
        hi = np.asarray(h); lo = np.asarray(l); op = np.asarray(o)

        sigs = detect_obdz001_signals(o, h, l, c, atr.tolist(), h1.tolist(), h4.tolist(), day.tolist(), n, atr_floor=-1e18)
        if EXPECTED_RAW.get(label) not in (None, len(sigs)):
            print(f"STOP: {label} declanșatoare brute = {len(sigs)}, aștept {EXPECTED_RAW[label]}."); return 4
        zone_events = [(s.entry_idx, s.direction, s.atr, s.entry_price) for s in sigs]

        # control: bias-aliniat, entry=i+1 valid, atr>0
        bias_up = (h1 > 0.5) & (h4 > 0.5)
        bias_dn = (h1 <= 0.5) & (h4 <= 0.5) & np.isfinite(h1) & np.isfinite(h4)
        aligned = bias_up | bias_dn
        pool = np.array([j for j in range(n - 1) if aligned[j] and np.isfinite(atr[j]) and atr[j] > 0], dtype=int)
        cnt = len(sigs)
        rng = np.random.default_rng(SEED + i)
        pick = rng.choice(pool, size=min(cnt, len(pool)), replace=False)
        ctrl_events = [(int(j) + 1, 1 if bias_up[j] else -1, float(atr[j]), float(op[j + 1])) for j in pick]

        zm = _measure(zone_events, hi, lo, n); cm = _measure(ctrl_events, hi, lo, n)
        out["zone"][label] = zm; out["control"][label] = cm
        print(f"\n=== {label.upper()} | zonă n={zm['n']} vs control n={cm['n']} ===")
        print(f"  ZONĂ    MAE={zm['MAE']}")
        print(f"          MFE={zm['MFE']}")
        print(f"          MFE/MAE={zm['MFE_over_MAE']} | bar_MAE={zm['bar_MAE']} bar_MFE={zm['bar_MFE']}")
        print(f"          adv_first={zm['frac_adverse_first']} fav_first={zm['frac_favorable_first']} tie={zm['frac_tie']}")
        print(f"  CONTROL MAE={cm['MAE']}")
        print(f"          MFE={cm['MFE']}")
        print(f"          MFE/MAE={cm['MFE_over_MAE']} | bar_MAE={cm['bar_MAE']} bar_MFE={cm['bar_MFE']}")
        print(f"          adv_first={cm['frac_adverse_first']} fav_first={cm['frac_favorable_first']} tie={cm['frac_tie']}")

        # pool pentru agregat (metrici per-eveniment, nu se pot re-măsura cross-segment)
        for ev, tgt, seq in ((zone_events, zone_metrics_pool, zone_seq), (ctrl_events, ctrl_metrics_pool, ctrl_seq)):
            for entry, d, a, ep in ev:
                ma, mf, ba, bf = _mae_mfe(entry, d, a, ep, hi, lo, n)
                tgt["MAE"].append(ma); tgt["MFE"].append(mf); tgt["bMAE"].append(float(ba)); tgt["bMFE"].append(float(bf))
                if ma > 0:
                    tgt["ratio"].append(mf / ma)
                seq["adv" if ba < bf else "fav" if ba > bf else "tie"] += 1

    for tag, pool_m, seq in (("zone", zone_metrics_pool, zone_seq), ("control", ctrl_metrics_pool, ctrl_seq)):
        tot = len(pool_m["MAE"])
        out[tag]["AGGREGATE"] = dict(
            n=tot, MAE=_dist(np.asarray(pool_m["MAE"])), MFE=_dist(np.asarray(pool_m["MFE"])),
            MFE_over_MAE=_dist(np.asarray(pool_m["ratio"])), bar_MAE=_dist(np.asarray(pool_m["bMAE"])),
            bar_MFE=_dist(np.asarray(pool_m["bMFE"])),
            frac_adverse_first=round(seq["adv"] / tot, 3), frac_favorable_first=round(seq["fav"] / tot, 3),
            frac_tie=round(seq["tie"] / tot, 3))
    print("\n=== AGREGAT ===")
    print(f"  ZONĂ    MAE={out['zone']['AGGREGATE']['MAE']} MFE={out['zone']['AGGREGATE']['MFE']} "
          f"MFE/MAE={out['zone']['AGGREGATE']['MFE_over_MAE']} adv_first={out['zone']['AGGREGATE']['frac_adverse_first']}")
    print(f"  CONTROL MAE={out['control']['AGGREGATE']['MAE']} MFE={out['control']['AGGREGATE']['MFE']} "
          f"MFE/MAE={out['control']['AGGREGATE']['MFE_over_MAE']} adv_first={out['control']['AGGREGATE']['frac_adverse_first']}")

    path = os.path.join(_ROOT, "reports", "obdz_mae_mfe_control_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/obdz_mae_mfe_control_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""OBDZ — Măsurătoarea A' + diagnosticul de raport SL/TP (Statistician v2.7.13, doc 44477f3). READ-ONLY.

DIAGNOSTIC, nu optimizare. Întrebarea: „rezultatul depinde de raport, sau e nul peste tot?" — NU „care
raport e cel mai bun". Pragul e citit mecanic din tabel, pre-înregistrat. GARD 2 neatins, sigilat intact.

POPULAȚIA: cele 275/223/156 declanșatoare compuse BRUTE (bias + cross-candle DemandZone×OB), NU cele
261/194/154 filtrate — podeaua de ATR (`3×cost/SL_MULT`) depinde ea însăși de multiplicatorul SL, deci
filtrarea cu podeaua veche (SL=0,7) înainte de a varia SL-ul ar fi CIRCULARĂ.

MĂSURĂTOAREA A': pentru fiecare declanșator (bara t, intrare t+1), MAE = excursia adversă maximă în
multipli de `ATR14[t]`, pe fereastra FIXĂ `[t+1, t+1+92]` (92 = ziua empirică, SEPARATĂ de plasa de 20 bare).
Candidați SL = {0,7 ancoră, p25, p50, p75, p90 ale MAE AGREGAT}. TP1=2×SL, TP2=3×SL (progresie 1×/2×/3×
fixată → izolează RAPORTUL). Podeaua RE-DERIVATĂ per candidat (`3×0,20/k`), exclusii raportate. Orizont FIX
20/EOD (nevariat). Fără oracol WP-5' (decizia e pe expectancy_$, nu p). Fără recalibrare de oracol.

PRAG (pre-înregistrat, dolarii = variabila de decizie):
  ÎNCHIS DEFINITIV        expectancy_$ <= 0 la TOATE cele 5 candidate, în TOATE cele 3 regimuri.
  MERITĂ IPOTEZĂ NOUĂ     expectancy_$ > 0 la >=2 din cele 3 candidate mai LATE, în >=2 regimuri (tipar).
  ALTFEL                  TESTABLE BUT INSUFFICIENT EVIDENCE.
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
from obdz001 import HORIZON, Obdz001Signal, detect_obdz001_signals
from partial_exit import simulate_partial_exit

COST, MAE_WINDOW = 0.20, 92
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
    return dict(n=int(len(a)), min=round(float(a.min()), 2), p25=round(float(np.percentile(a, 25)), 2),
                p50=round(float(np.percentile(a, 50)), 2), p75=round(float(np.percentile(a, 75)), 2),
                p90=round(float(np.percentile(a, 90)), 2), max=round(float(a.max()), 2), mean=round(float(a.mean()), 2))


def _mae(sig: Obdz001Signal, high: Any, low: Any, n: int) -> float:
    e = sig.entry_idx
    end = min(e + MAE_WINDOW, n - 1)
    if sig.direction > 0:
        adverse = sig.entry_price - float(np.min(low[e:end + 1]))
    else:
        adverse = float(np.max(high[e:end + 1])) - sig.entry_price
    return max(0.0, adverse) / sig.atr if sig.atr > 0 else 0.0


def _cell(sigs: list[Obdz001Signal], k: float, high: Any, low: Any, close: Any) -> dict[str, Any]:
    floor_k = 3.0 * COST / k
    elig = [s for s in sigs if s.atr >= floor_k]
    excluded = len(sigs) - len(elig)
    reasons: dict[str, int] = {}
    net_r: list[float] = []; net_d: list[float] = []; realized: list[int] = []
    plasa = eod = 0
    for s in elig:
        sl = s.entry_price - k * s.atr if s.direction > 0 else s.entry_price + k * s.atr
        tp1 = s.entry_price + 2 * k * s.atr if s.direction > 0 else s.entry_price - 2 * k * s.atr
        tp2 = s.entry_price + 3 * k * s.atr if s.direction > 0 else s.entry_price - 3 * k * s.atr
        res = simulate_partial_exit(s.entry_idx, s.direction, s.entry_price, sl, tp1, tp2, high, low, close,
                                    horizon=HORIZON, day_end_idx=s.eod_idx, cost=COST)
        reasons[res.exit_reason] = reasons.get(res.exit_reason, 0) + 1
        r_d = k * s.atr
        net_r.append(res.net_R); net_d.append(res.net_R * r_d)
        realized.append(res.leg2_exit_idx - s.entry_idx)
        if res.exit_reason in ("timeout_no_tp1", "tp1_then_timeout"):
            if s.entry_idx + HORIZON <= s.eod_idx:
                plasa += 1
            else:
                eod += 1
    nt = len(net_r)
    reach_tp1 = reasons.get("tp1_then_tp2", 0) + reasons.get("tp1_then_breakeven", 0) + reasons.get("tp1_then_timeout", 0)
    reach_tp2 = reasons.get("tp1_then_tp2", 0)
    if nt == 0:
        return dict(k=round(k, 3), n_trades=0, n_excluded_by_floor=excluded)
    nr = np.asarray(net_r); nd = np.asarray(net_d); srt = np.sort(nr)[::-1]
    sumR = float(nr.sum()); wins = nr[nr > 0]
    return dict(
        k=round(k, 3), floor=round(floor_k, 3), n_trades=nt, n_excluded_by_floor=excluded,
        SL=reasons.get("stopped_full", 0), TP2=reach_tp2, TP1_breakeven=reasons.get("tp1_then_breakeven", 0),
        TP1_timeout=reasons.get("tp1_then_timeout", 0), never_tp1_timeout=reasons.get("timeout_no_tp1", 0),
        reach_TP1=reach_tp1, conv_TP1_to_TP2=round(reach_tp2 / reach_tp1, 3) if reach_tp1 else None,
        timeout_frac=round((plasa + eod) / nt, 3), timeout_plasa=plasa, timeout_EOD=eod,
        winrate=round(float((nr > 0).mean()), 4), W_mean_win=round(float(wins.mean()), 4) if len(wins) else None,
        expectancy_R=round(float(nr.mean()), 5), expectancy_dollars=round(float(nd.mean()), 5),
        net_sumR=round(sumR, 3), net_sum_dollars=round(float(nd.sum()), 3),
        best_over_sumR=round(float(srt[0]) / sumR, 4) if sumR else None, wo1_netR=round(sumR - float(srt[0]), 3),
        realized_horizon=_dist(np.asarray(realized, dtype=float)))


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
    print(f"loader v6 | M15={len(dfm)} | MAE_WINDOW={MAE_WINDOW} | horizon FIX={HORIZON}")
    if len(dfm) != 130_491:
        print(f"STOP: M15 {len(dfm)} bare."); return 2
    dfm = dfm.sort_values("time").reset_index(drop=True)
    for name, dfh, per in (("h1", dfh1, 3600), ("h4", dfh4, 4 * 3600)):
        htf = _htf_trend(dfh, per).sort_values("avail")
        dfm = pd.merge_asof(dfm, htf.rename(columns={"trend_up": name}), left_on="time", right_on="avail",
                            direction="backward").drop(columns="avail")
    dfm["day"] = _day_index(dfm["time"])
    t_all = dfm["time"].to_numpy()
    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]

    # pas 1: declanșatoare BRUTE (fără podea) + MAE per declanșator
    per_regime: dict[str, dict[str, Any]] = {}
    all_mae: list[float] = []
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        atr = sub["atr14"].to_numpy(); h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy(); day = sub["day"].to_numpy()
        hi = np.asarray(h); lo = np.asarray(l)
        sigs = detect_obdz001_signals(o, h, l, c, atr.tolist(), h1.tolist(), h4.tolist(), day.tolist(), n,
                                      atr_floor=-1e18)                # BRUT: fără podea
        sigs = sorted(sigs, key=lambda s: s.entry_idx)
        if EXPECTED_RAW.get(label) not in (None, len(sigs)):
            print(f"STOP: {label} declanșatoare brute = {len(sigs)}, aștept {EXPECTED_RAW[label]} — raportez."); return 4
        mae = [_mae(s, hi, lo, n) for s in sigs]
        all_mae += mae
        per_regime[label] = {"sigs": sigs, "mae": mae, "hi": hi, "lo": lo, "close": np.asarray(c), "n": n}

    # candidați SL din MAE AGREGAT + ancora 0,7
    amae = np.asarray(all_mae)
    cand = {"0.7_anchor": 0.7, "p25": round(float(np.percentile(amae, 25)), 3),
            "p50": round(float(np.percentile(amae, 50)), 3), "p75": round(float(np.percentile(amae, 75)), 3),
            "p90": round(float(np.percentile(amae, 90)), 3)}
    wider3 = [nm for nm, _v in sorted(cand.items(), key=lambda kv: kv[1])[-3:]]
    print("\n########## MĂSURĂTOAREA A' — MAE (multipli ATR) ##########")
    print(f"AGREGAT MAE: {_dist(amae)}")
    for lb in per_regime:
        print(f"  {lb:11s} {_dist(np.asarray(per_regime[lb]['mae']))}")
    print(f"\ncandidați SL (×ATR): {cand}  | cele 3 mai late = {wider3}")

    # pas 2: diagnostic 5 candidate × 3 regimuri
    out: dict[str, Any] = {"candidates": cand, "wider3": wider3, "MAE_aggregate": _dist(amae),
                           "MAE_per_regime": {lb: _dist(np.asarray(per_regime[lb]["mae"])) for lb in per_regime},
                           "grid": {}}
    print("\n########## DIAGNOSTIC — 5 candidate × 3 regimuri (decizie = expectancy_$) ##########")
    for nm, k in cand.items():
        out["grid"][nm] = {}
        print(f"\n=== candidat {nm} (SL={k}×ATR, TP1={round(2*k,2)}×, TP2={round(3*k,2)}×, podea={round(3*COST/k,3)}$) ===")
        for lb, pr in per_regime.items():
            cell = _cell(pr["sigs"], k, pr["hi"], pr["lo"], pr["close"])
            out["grid"][nm][lb] = cell
            if cell["n_trades"] == 0:
                print(f"  {lb:11s} (fără tranzacții)"); continue
            print(f"  {lb:11s} n={cell['n_trades']:3d} excl={cell['n_excluded_by_floor']:3d} | SL={cell['SL']} "
                  f"TP2={cell['TP2']} BE={cell['TP1_breakeven']} T1to={cell['TP1_timeout']} noT1={cell['never_tp1_timeout']} "
                  f"| conv={cell['conv_TP1_to_TP2']} timeout={cell['timeout_frac']} WR={cell['winrate']} "
                  f"E_R={cell['expectancy_R']:+.4f} E_$={cell['expectancy_dollars']:+.4f} "
                  f"netR={cell['net_sumR']:+.1f} net$={cell['net_sum_dollars']:+.1f} b/sR={cell['best_over_sumR']} "
                  f"wo1R={cell['wo1_netR']:+.1f} hor={cell['realized_horizon'].get('median')}")

    labels = list(per_regime.keys())
    all_nonpos = all(out["grid"][nm][lb].get("expectancy_dollars", -9) <= 0 for nm in cand for lb in labels)
    reg_2wider_pos = sum(1 for lb in labels
                         if sum(1 for nm in wider3 if out["grid"][nm][lb].get("expectancy_dollars", -9) > 0) >= 2)
    if all_nonpos:
        verdict = "ÎNCHIS DEFINITIV (expectancy_$ <= 0 la toate 5 candidate, în toate 3 regimuri)"
    elif reg_2wider_pos >= 2:
        verdict = "MERITĂ IPOTEZĂ NOUĂ (expectancy_$ > 0 la >=2 candidate late, în >=2 regimuri) — raportez, NU pre-înregistrez"
    else:
        verdict = "TESTABLE BUT INSUFFICIENT EVIDENCE (tipar amestecat / un singur regim / punct izolat)"
    out["verdict"] = verdict
    print(f"\n########## VERDICT MECANIC: {verdict} ##########")
    path = os.path.join(_ROOT, "reports", "obdz_sltp_diagnostic_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("record -> reports/obdz_sltp_diagnostic_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

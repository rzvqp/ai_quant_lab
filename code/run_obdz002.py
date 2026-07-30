"""OBDZ-002 — RULAREA finală pe descoperire (Statistician v2.7.23, e32de2c). Read-only, in-sample, M15_v2.

Declanșator compus DIRECT (Decizia 3, NEATINS), FĂRĂ poartă de confirmare (Varianta 3 eliminată). entry=t+1.
SL 1,0× / TP1 2,0× / TP2 3,0× / podea 0,60 — TOATE la ATR14[t]. Orizont min(entry+20, EOD). Ieșire parțială
(`partial_exit`, înghețat). Populație 651 (275/220/156). Familia 2. Test WP-5' block_bootstrap L>=28,
H0: mean(net_R)<=0. Stratificare pe polaritate (demand/supply) OBLIGATORIE. GARD 2 neatins, sigilat intact.
Rezultat pozitiv pe descoperire = CANDIDAT, nu confirmare (regula SMC_S1). NU interpretez.

Reutilizez declanșatorul înghețat (`detect_obdz001_signals`, podea 0,60 la ATR[t]) și RECALCULEZ nivelurile
cu multiplii OBDZ-002 (1,0/2,0/3,0), apoi `partial_exit` direct — mecanica de măsurare neschimbată.
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
for _p in (_HERE, _ROOT, os.path.join(_ROOT, "edge_research"), os.path.join(_ROOT, "edge_research", "lm001_s8")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from edge_research._common import PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC, load
import split_manifest as SM  # type: ignore[import-not-found]
import block_bootstrap as BB  # type: ignore[import-not-found]
from obdz001 import HORIZON, detect_obdz001_signals
from partial_exit import simulate_partial_exit

FLOOR, SL_M, TP1_M, TP2_M, COST = 0.60, 1.0, 2.0, 3.0, 0.20
L, BOOT, SEED = 28, 2000, 20260729
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}


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


def _metrics(net_r: list[float], net_d: list[float], reasons: dict[str, int], want_p: bool) -> dict[str, Any]:
    nt = len(net_r)
    base: dict[str, Any] = {"n_trades": nt}
    if nt == 0:
        return base
    nr = np.asarray(net_r); nd = np.asarray(net_d); srt = np.sort(nr)[::-1]
    sumR = float(nr.sum())
    reach1 = reasons.get("tp1_then_tp2", 0) + reasons.get("tp1_then_breakeven", 0) + reasons.get("tp1_then_timeout", 0)
    reach2 = reasons.get("tp1_then_tp2", 0)
    p = ci = None
    if want_p and nt > L:
        bb = BB.run(nr, block_length=L, B=BOOT, tail="right", centering="zero", seed=SEED)
        p, ci = bb["p_hat"], bb["p_mc_ci95"]
    base.update(
        SL=reasons.get("stopped_full", 0), TP2=reach2, TP1_breakeven=reasons.get("tp1_then_breakeven", 0),
        TP1_timeout=reasons.get("tp1_then_timeout", 0), never_TP1_timeout=reasons.get("timeout_no_tp1", 0),
        reach_TP1=reach1, conv_TP1_TP2=round(reach2 / reach1, 3) if reach1 else None,
        winrate=round(float((nr > 0).mean()), 4), expectancy_R=round(float(nr.mean()), 5),
        expectancy_dollars=round(float(nd.mean()), 5),
        edge_brut_dollars=round(float(nd.mean()) + COST, 5),           # gross = net + cost
        net_sumR=round(sumR, 3), net_sum_dollars=round(float(nd.sum()), 3),
        best_over_sumR=round(float(srt[0]) / sumR, 4) if sumR else None, wo1_netR=round(sumR - float(srt[0]), 3),
        p_wp5=p, p_ci95=ci)
    return base


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
    print(f"loader v6 | M15={len(dfm)} | SL/TP/podea = {SL_M}/{TP1_M}/{TP2_M}/{FLOOR}×ATR[t] | L={L}")
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

    out: dict[str, Any] = {"floor": FLOOR, "mults": [SL_M, TP1_M, TP2_M], "L": L, "B": BOOT, "regimes": {}}
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        atr = sub["atr14"].to_numpy(); h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy(); day = sub["day"].to_numpy()

        sigs = detect_obdz001_signals(o, h, l, c, atr.tolist(), h1.tolist(), h4.tolist(), day.tolist(), n, atr_floor=FLOOR)
        sigs = sorted(sigs, key=lambda s: s.entry_idx)
        pools: dict[str, dict[str, Any]] = {
            "all": {"nr": [], "nd": [], "reasons": {}},
            "demand": {"nr": [], "nd": [], "reasons": {}},
            "supply": {"nr": [], "nd": [], "reasons": {}}}
        for s in sigs:
            r_d = SL_M * s.atr
            if s.direction > 0:
                sl, tp1, tp2 = s.entry_price - SL_M * s.atr, s.entry_price + TP1_M * s.atr, s.entry_price + TP2_M * s.atr
            else:
                sl, tp1, tp2 = s.entry_price + SL_M * s.atr, s.entry_price - TP1_M * s.atr, s.entry_price - TP2_M * s.atr
            res = simulate_partial_exit(s.entry_idx, s.direction, s.entry_price, sl, tp1, tp2, h, l, c,
                                        horizon=HORIZON, day_end_idx=s.eod_idx, cost=COST)
            pol = "demand" if s.direction > 0 else "supply"
            for key in ("all", pol):
                pools[key]["nr"].append(res.net_R); pools[key]["nd"].append(res.net_R * r_d)
                pools[key]["reasons"][res.exit_reason] = pools[key]["reasons"].get(res.exit_reason, 0) + 1

        rec = {"total": _metrics(pools["all"]["nr"], pools["all"]["nd"], pools["all"]["reasons"], True),
               "demand": _metrics(pools["demand"]["nr"], pools["demand"]["nd"], pools["demand"]["reasons"], True),
               "supply": _metrics(pools["supply"]["nr"], pools["supply"]["nd"], pools["supply"]["reasons"], True)}
        out["regimes"][label] = rec
        m = rec["total"]
        print(f"\n=== {label.upper()} ({n} bare) ===")
        print(f"  n={m['n_trades']} | SL={m['SL']} TP2={m['TP2']} BE={m['TP1_breakeven']} T1to={m['TP1_timeout']} "
              f"noT1={m['never_TP1_timeout']} | conv_TP1→TP2={m['conv_TP1_TP2']}")
        print(f"  WR={m['winrate']} E_R={m['expectancy_R']:+.4f} E_$={m['expectancy_dollars']:+.4f} "
              f"EDGE_BRUT_$={m['edge_brut_dollars']:+.4f} netR={m['net_sumR']:+.2f} net$={m['net_sum_dollars']:+.2f}")
        print(f"  best/sumR={m['best_over_sumR']} wo1R={m['wo1_netR']:+.2f} | p_WP5={m['p_wp5']} CI95={m['p_ci95']}")
        for pol in ("demand", "supply"):
            d = rec[pol]
            if d["n_trades"]:
                print(f"    [{pol}] n={d['n_trades']} WR={d['winrate']} E_$={d['expectancy_dollars']:+.4f} "
                      f"net$={d['net_sum_dollars']:+.2f} EDGE_BRUT_$={d['edge_brut_dollars']:+.4f} p={d['p_wp5']}")

    path = os.path.join(_ROOT, "reports", "obdz002_run_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/obdz002_run_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""V1 Dublă Respingere — RENUMĂRARE cu SL pe ATR, apoi RULARE (Statistician v2.7.28, 8321301, doc 6b059b6).

Read-only pe date, in-sample, M15_v2. Declanșator compus, populație 654 brute (275/223/156). Pattern-match V1
NESCHIMBAT (căut q ∈ {t+1,t+2}, prima re-atingere span-overlap a zonei OB_B ȘI închidere fără a coborî sub
extrema barei t; entry_idx=q+1). SCHIMBAREA (ordin CTO v2.7.28): dimensionarea riscului reconvertită de la
structural (sub ambele fitile) la ATR14[t] — EXACT convenția OBDZ-002:
  SL = 1,0×ATR14[t]   TP1 = 2,0×ATR14[t]   TP2 = 3,0×ATR14[t]   podea eligibilitate = ATR14[t] >= 0,60
TOATE ancorate la bara t (declanșator), NU la bara de confirmare q — entry poate cădea 1-2 bare după citirea
ATR (staleness disclosed, v2.7.28), executat EXACT ca ordonat (ATR14[t], nu ATR14[q]).

PAS 1 — RENUMĂRARE: supraviețuitor = V1 confirmă (entry valid) ȘI ATR14[t] >= 0,60. Prag N_MIN=25/regim,
verificat mecanic (estimarea CTO ~157/125/99 NU e adoptată). Per regim, agregat, pe polaritate (obligatoriu).
PAS 2 — dacă TOATE regimurile >= 25: RULEAZĂ. `partial_exit` înghețat (75/25, breakeven=entry-exact, cost 0,20),
orizont min(entry+20, EOD). Test WP-5' block_bootstrap L=28, H0: mean(net_R)<=0. Familia 3 (2 consumate + V1;
finalizare de parametrizare a aceleiași V1 deja numărate, NU un membru nou).

OB_B recuperat replicând bucla înghețată `detect_obdz001_signals` + VERIFICAT identic cu funcția oficială.
GARD 1 ridicat EXCLUSIV pentru rulare (Pas 2), coborât imediat după. GARD 2 neatins, sigilat intact. Rezultat
pozitiv pe descoperire = CANDIDAT, nu confirmare. Rezultatele JSON NU se comit. NU interpretez.
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
from order_block_void import OrderBlockKind
from order_flow import detect_demand_zones, detect_order_blocks
from obdz001 import HORIZON, WEEK_BARS, _eod_per_bar, _first_mitigation, detect_obdz001_signals
from partial_exit import simulate_partial_exit

SL_M, TP1_M, TP2_M, FLOOR, COST = 1.0, 2.0, 3.0, 0.60, 0.20
L, BOOT, SEED = 28, 2000, 20260729
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
    __slots__ = ("t", "d", "atr_t", "ob_lower", "ob_upper")

    def __init__(self, t: int, d: int, atr_t: float, ob_lower: float, ob_upper: float) -> None:
        self.t = t; self.d = d; self.atr_t = atr_t; self.ob_lower = ob_lower; self.ob_upper = ob_upper


def _recover_triggers(
    o: list[float], h: list[float], l: list[float], c: list[float], atr: np.ndarray,
    h1: np.ndarray, h4: np.ndarray, day: np.ndarray, n: int,
) -> list[Trigger]:
    """Replică EXACT bucla înghețată din `detect_obdz001_signals` (podea -inf), capturând ATR14[t] + zona OB_B."""
    obs = detect_order_blocks(o, h, l, c, n)
    dzs = detect_demand_zones(o, h, l, c, n)
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
        out.append(Trigger(t, obdir, float(atr[t]), float(ob.zone_lower), float(ob.zone_upper)))
    return out


def _v1_entry(tr: Trigger, h: list[float], l: list[float], c: list[float], n: int) -> int | None:
    """entry_idx=q+1 dacă V1 confirmă cu entry valid, altfel None. Pattern-match NESCHIMBAT."""
    t, d = tr.t, tr.d
    for q in (t + 1, t + 2):
        if q >= n:
            break
        if not (l[q] <= tr.ob_upper and h[q] >= tr.ob_lower):     # re-atingere span-overlap zona OB_B
            continue
        if (d > 0 and c[q] >= l[t]) or (d < 0 and c[q] <= h[t]):  # nu coboară sub extrema barei t
            entry = q + 1
            return entry if entry < n else None
    return None


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
        expectancy_dollars=round(float(nd.mean()), 5), edge_brut_dollars=round(float(nd.mean()) + COST, 5),
        net_sumR=round(sumR, 3), net_sum_dollars=round(float(nd.sum()), 3),
        best_over_sumR=round(float(srt[0]) / sumR, 4) if sumR else None, wo1_netR=round(sumR - float(srt[0]), 3),
        p_wp5=p, p_ci95=ci)
    return base


def main() -> int:
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh1, _ = load("H1_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh4, _ = load("H4_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | M15={len(dfm)} | V1 SL/TP/podea = {SL_M}/{TP1_M}/{TP2_M}/{FLOOR}×ATR14[t] | L={L} | N_MIN={N_MIN}")
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

    # ── PAS 1: RENUMĂRARE ──────────────────────────────────────────────────────────────────────
    print("\n########## PAS 1 — RENUMĂRARE (podea ATR14[t] >= 0,60) ##########")
    regimes: dict[str, Any] = {}
    survivors: dict[str, list[tuple[int, int, int, float]]] = {}   # label -> [(t, entry_idx, direction, atr_t)]
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        atr = sub["atr14"].to_numpy(); h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy(); day = sub["day"].to_numpy()

        official = detect_obdz001_signals(o, h, l, c, atr.tolist(), h1.tolist(), h4.tolist(), day.tolist(), n, atr_floor=-1e18)
        if EXPECTED_RAW.get(label) not in (None, len(official)):
            print(f"STOP: {label} compuse brute = {len(official)}."); return 4
        triggers = _recover_triggers(o, h, l, c, atr, h1, h4, day, n)
        if sorted((s.trigger_idx, s.entry_idx, s.direction) for s in official) != sorted((tr.t, tr.t + 1, tr.d) for tr in triggers):
            print(f"STOP: {label} recuperarea OB_B NU coincide cu funcția oficială."); return 5

        confirmed = {"demand": 0, "supply": 0}; surv = {"demand": 0, "supply": 0}
        keep: list[tuple[int, int, int, float]] = []
        for tr in triggers:
            entry = _v1_entry(tr, h, l, c, n)
            if entry is None:
                continue
            pol = "demand" if tr.d > 0 else "supply"
            confirmed[pol] += 1
            if np.isfinite(tr.atr_t) and tr.atr_t >= FLOOR:
                surv[pol] += 1
                keep.append((tr.t, entry, tr.d, tr.atr_t))
        survivors[label] = keep
        tot_conf = confirmed["demand"] + confirmed["supply"]; tot_surv = surv["demand"] + surv["supply"]
        regimes[label] = {"confirmed": {**confirmed, "TOTAL": tot_conf}, "survivors": {**surv, "TOTAL": tot_surv}}
        flag = " ← INSUFFICIENT_N (<25)" if tot_surv < N_MIN else ""
        print(f"  {label.upper():11s} confirmate={tot_conf:3d}  supraviețuitori(ATR[t]>=0,60)={tot_surv:3d}{flag}   "
              f"[demand {surv['demand']} / supply {surv['supply']}]")

    by_reg = {lab: regimes[lab]["survivors"]["TOTAL"] for lab in regimes}
    passes = all(v >= N_MIN for v in by_reg.values())
    print(f"\n  supraviețuitori/regim = {by_reg}  →  {'TRECE pragul în toate regimurile' if passes else 'NU trece — abandonat'}")
    out: dict[str, Any] = {"spec": "v2.7.28", "recount": regimes, "passes_threshold": passes,
                           "sl_tp_floor": [SL_M, TP1_M, TP2_M, FLOOR], "L": L, "family": 3}

    # ── PAS 2: RULARE (doar dacă trece) ────────────────────────────────────────────────────────
    if not passes:
        print("\nPAS 2 NU se execută (prag neîndeplinit). GARD 1 neatins.")
        _dump(out); return 0

    print("\n########## PAS 2 — RULARE (WP-5' L=28, Familia 3) ##########")
    out["run"] = {}
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        n = len(sub)
        h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist(); o = sub["open"].tolist()
        day = sub["day"].to_numpy(); eod = _eod_per_bar(day.tolist(), n)

        pools: dict[str, dict[str, Any]] = {k: {"nr": [], "nd": [], "reasons": {}} for k in ("all", "demand", "supply")}
        for (t, entry, d, atr_t) in survivors[label]:
            ep = float(o[entry])
            if d > 0:
                sl, tp1, tp2 = ep - SL_M * atr_t, ep + TP1_M * atr_t, ep + TP2_M * atr_t
            else:
                sl, tp1, tp2 = ep + SL_M * atr_t, ep - TP1_M * atr_t, ep - TP2_M * atr_t
            res = simulate_partial_exit(entry, d, ep, sl, tp1, tp2, h, l, c, horizon=HORIZON,
                                        day_end_idx=int(eod[entry]), cost=COST)
            r_d = SL_M * atr_t                                    # valoarea în $ a 1R
            pol = "demand" if d > 0 else "supply"
            for key in ("all", pol):
                pools[key]["nr"].append(res.net_R); pools[key]["nd"].append(res.net_R * r_d)
                pools[key]["reasons"][res.exit_reason] = pools[key]["reasons"].get(res.exit_reason, 0) + 1

        rec = {k: _metrics(pools[k]["nr"], pools[k]["nd"], pools[k]["reasons"], True) for k in ("all", "demand", "supply")}
        out["run"][label] = rec
        m = rec["all"]
        print(f"\n=== {label.upper()} ===")
        print(f"  n={m['n_trades']} | SL={m['SL']} TP2={m['TP2']} BE={m['TP1_breakeven']} T1to={m['TP1_timeout']} "
              f"noT1={m['never_TP1_timeout']} | conv_TP1→TP2={m['conv_TP1_TP2']}")
        print(f"  WR={m['winrate']} E_R={m['expectancy_R']:+.4f} E_$={m['expectancy_dollars']:+.4f} "
              f"EDGE_BRUT_$={m['edge_brut_dollars']:+.4f} netR={m['net_sumR']:+.2f} net$={m['net_sum_dollars']:+.2f}")
        print(f"  best/sumR={m['best_over_sumR']} wo1R={m['wo1_netR']:+.2f} | p_WP5={m['p_wp5']} CI95={m['p_ci95']}")
        for pol in ("demand", "supply"):
            d2 = rec[pol]
            if d2["n_trades"]:
                print(f"    [{pol}] n={d2['n_trades']} WR={d2['winrate']} E_$={d2['expectancy_dollars']:+.4f} "
                      f"net$={d2['net_sum_dollars']:+.2f} p={d2['p_wp5']}")
    _dump(out)
    return 0


def _dump(out: dict[str, Any]) -> None:
    path = os.path.join(_ROOT, "reports", "v1_double_rejection_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"\nrecord -> reports/v1_double_rejection_results.json")


if __name__ == "__main__":
    raise SystemExit(main())

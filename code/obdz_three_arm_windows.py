"""OBDZ — măsurătoarea CORECTATĂ: 3 brațe (A/B/C), ferestre scurte de la entry+1 (Statistician v2.7.15, f705956).

READ-ONLY, in-sample. Poarta pentru tot ce urmează. Livrez cifrele; grila e pre-înregistrată de Statistician.
NU interpretez, NU încadrez în grilă. GARD 2 neatins, sigilat intact.

BRAȚE:
  A  zona (bias+pullback+zonă) = declanșatoarele OBDZ brute 275/223/156. A_full (toate) + A_subset (cu
     pullback_depth definit, pentru comparația cu C).
  B  bias-aleatoriu = controlul anterior (275/223/156 bare bias-aliniate, sămânță 20260729+regim). Păstrat.
  C  bias+pullback FĂRĂ zonă = pt. fiecare A_subset, o bară bias-aliniată NON-zonă cu pullback_depth potrivit.

PULLBACK_DEPTH(j) (market_structure Swing/StructureLabel, aceeași primitivă ca SMC_S1_v2 A):
  bias BULLISH: (preț_swing_HIGH_clasificat_precedent − close[j]) / ATR14[j]; simetric BEARISH (swing LOW).
  swing = cel mai RECENT swing clasificat de tipul corect (orice label ≠ UNCLASSIFIED) cunoscut la j
  (confirmed_idx <= j, forward-safe), în ACELAȘI bloc. Nedefinit dacă niciun swing → bara EXCLUSĂ (numărat).
POTRIVIRE A↔C: candidați = bare bias-aliniate NON-zonă cu pullback_depth în banda `pd_A ± max(0,25×|pd_A|, 0,5)`
  (relativ 25% SAU absolut 0,5×ATR, mai LATĂ); dacă gol, se DUBLEAZĂ banda până la plafon `max(|pd_A|, 2,0)`;
  nepotrivite la plafon = raportate EXPLICIT. Selecție aleatorie fără înlocuire (sămânță 20260729+regim).

FERESTRE (doc: bara 0=entry; se scanează de la entry+1, sărind bara de intrare care reflectă atingerea):
  [entry+1, entry+2]  (=CEO [t+2,t+3])   [entry+1, entry+4]  (=[t+2,t+5], PRINCIPAL)
  [entry+1, entry+9]  (=[t+2,t+10], PRINCIPAL)   [entry+1, entry+19]  (=[t+2,t+20], orizont)
  [entry+1, entry+92]  = REFERINȚĂ de VOLATILITATE GENERALĂ (~1 zi), relabelată explicit — NU reacție la zonă.
preț ref = entry_price (open[entry]); ATR normalizator = ATR14[t]. MAE/MFE/adverse-first + distribuții complete.
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
from market_structure import Block, StructureLabel, SwingKind, detect_swings, label_structure
from obdz001 import detect_obdz001_signals

SEED = 20260729
WINDOWS = {"t2_t3": 2, "t2_t5": 4, "t2_t10": 9, "t2_t20": 19, "ref92_volatility": 92}   # (end offset de la entry)
EXPECTED_RAW = {"bear": 275, "bull": 223, "correction": 156}
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}
Event = tuple[int, int, float, float]     # (entry_idx, direction, atr, entry_price)


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


def _win(ev: Event, hi: np.ndarray, lo: np.ndarray, n: int, end_off: int) -> tuple[float, float, int] | None:
    entry, d, atr, ep = ev
    s = entry + 1
    e = min(entry + end_off, n - 1)
    if s > e or atr <= 0:
        return None
    hh = hi[s:e + 1]; ll = lo[s:e + 1]
    if d > 0:
        mae = ep - float(np.min(ll)); mfe = float(np.max(hh)) - ep
        bmae = int(np.argmin(ll)); bmfe = int(np.argmax(hh))
    else:
        mae = float(np.max(hh)) - ep; mfe = ep - float(np.min(ll))
        bmae = int(np.argmax(hh)); bmfe = int(np.argmin(ll))
    return max(0.0, mae) / atr, max(0.0, mfe) / atr, (0 if bmae < bmfe else 1 if bmae > bmfe else 2)


def _measure_pool(events: list[Event], hi: np.ndarray, lo: np.ndarray, n: int,
                  acc: dict[str, dict[str, list[float]]]) -> None:
    for wn, eo in WINDOWS.items():
        for ev in events:
            r = _win(ev, hi, lo, n, eo)
            if r is None:
                continue
            acc.setdefault(wn, {"MAE": [], "MFE": [], "ratio": [], "adv": []})
            acc[wn]["MAE"].append(r[0]); acc[wn]["MFE"].append(r[1])
            if r[0] > 0:
                acc[wn]["ratio"].append(r[1] / r[0])
            acc[wn]["adv"].append(1.0 if r[2] == 0 else 0.0)


def _summarize(acc: dict[str, dict[str, list[float]]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for wn, d in acc.items():
        out[wn] = dict(n=len(d["MAE"]), MAE=_dist(np.asarray(d["MAE"])), MFE=_dist(np.asarray(d["MFE"])),
                       MFE_over_MAE=_dist(np.asarray(d["ratio"])),
                       frac_adverse_first=round(float(np.mean(d["adv"])), 3) if d["adv"] else None)
    return out


def _pullback_depth_arrays(sub: Any, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Pentru fiecare bară j: prețul celui mai recent swing HIGH / LOW clasificat cunoscut la j (confirmed_idx<=j)."""
    h = sub["high"].tolist(); l = sub["low"].tolist()
    swings = label_structure(detect_swings(h, l, [Block(0, n)], k=2))
    evs = sorted(((s.confirmed_idx, s.kind, s.price) for s in swings if s.label is not StructureLabel.UNCLASSIFIED),
                 key=lambda x: x[0])
    last_high = np.full(n, np.nan); last_low = np.full(n, np.nan)
    ch = cl = np.nan; si = 0
    for j in range(n):
        while si < len(evs) and evs[si][0] <= j:
            if evs[si][1] is SwingKind.HIGH:
                ch = evs[si][2]
            else:
                cl = evs[si][2]
            si += 1
        last_high[j] = ch; last_low[j] = cl
    return last_high, last_low


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
    print(f"loader v6 | M15={len(dfm)} | seed={SEED}")
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

    arms = ("A_full", "A_subset", "B", "C")
    agg: dict[str, dict[str, dict[str, list[float]]]] = {a: {} for a in arms}
    out: dict[str, Any] = {"windows": WINDOWS, "seed": SEED, "per_regime": {}, "match": {}}
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        atr = sub["atr14"].to_numpy(); h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy(); day = sub["day"].to_numpy()
        hi = np.asarray(h); lo = np.asarray(l); op = np.asarray(o); cl = np.asarray(c)
        last_high, last_low = _pullback_depth_arrays(sub, n)

        sigs = detect_obdz001_signals(o, h, l, c, atr.tolist(), h1.tolist(), h4.tolist(), day.tolist(), n, atr_floor=-1e18)
        if EXPECTED_RAW.get(label) not in (None, len(sigs)):
            print(f"STOP: {label} declanșatoare brute = {len(sigs)}."); return 4
        zone_t = {s.trigger_idx for s in sigs}

        def pdepth(j: int, bull: bool) -> float:
            if atr[j] <= 0:
                return float("nan")
            return float((last_high[j] - cl[j]) / atr[j] if bull else (cl[j] - last_low[j]) / atr[j])

        A_full: list[Event] = [(s.entry_idx, s.direction, s.atr, s.entry_price) for s in sigs]
        A_subset: list[Event] = []; pd_A: list[float] = []
        undefined = 0
        for s in sigs:
            pdv = pdepth(s.trigger_idx, s.direction > 0)
            if not np.isfinite(pdv):
                undefined += 1
                continue
            A_subset.append((s.entry_idx, s.direction, s.atr, s.entry_price)); pd_A.append(pdv)

        # B: bias-aleatoriu (identic controlului anterior)
        bias_up = (h1 > 0.5) & (h4 > 0.5)
        bias_dn = (h1 <= 0.5) & (h4 <= 0.5) & np.isfinite(h1) & np.isfinite(h4)
        aligned = bias_up | bias_dn
        pool_all = np.array([j for j in range(n - 1) if aligned[j] and np.isfinite(atr[j]) and atr[j] > 0], dtype=int)
        rng = np.random.default_rng(SEED + i)
        bpick = rng.choice(pool_all, size=min(len(sigs), len(pool_all)), replace=False)
        B: list[Event] = [(int(j) + 1, 1 if bias_up[j] else -1, float(atr[j]), float(op[j + 1])) for j in bpick]

        # C: bias+pullback NON-zonă, potrivit pe pullback_depth
        cpool = np.array([j for j in pool_all if j not in zone_t and np.isfinite(pdepth(j, bool(bias_up[j])))], dtype=int)
        cpd = np.array([pdepth(int(j), bool(bias_up[j])) for j in cpool])
        order = np.argsort(cpd); spd = cpd[order]; sidx = cpool[order]
        used = np.zeros(len(cpool), dtype=bool)
        rngC = np.random.default_rng(SEED + i + 1000)
        C: list[Event] = []; matched = 0; unmatched = 0
        for (ev, pda) in zip(A_subset, pd_A):
            tol0 = max(0.25 * abs(pda), 0.5); cap = max(abs(pda), 2.0); tol = tol0; picked = -1
            while True:
                a = int(np.searchsorted(spd, pda - tol, "left")); b = int(np.searchsorted(spd, pda + tol, "right"))
                avail = [p for p in range(a, b) if not used[p]]
                if avail:
                    p = int(rngC.choice(avail)); used[p] = True; picked = int(sidx[p]); break
                if tol >= cap:
                    break
                tol = min(tol * 2, cap)
            if picked < 0:
                unmatched += 1
            else:
                matched += 1
                C.append((picked + 1, 1 if bias_up[picked] else -1, float(atr[picked]), float(op[picked + 1])))

        out["match"][label] = dict(A_full=len(A_full), A_subset=len(A_subset), pullback_undefined=undefined,
                                   C_matched=matched, C_unmatched=unmatched, B=len(B))
        reg: dict[str, Any] = {}
        for name, evlist in (("A_full", A_full), ("A_subset", A_subset), ("B", B), ("C", C)):
            acc: dict[str, dict[str, list[float]]] = {}
            _measure_pool(evlist, hi, lo, n, acc)
            reg[name] = _summarize(acc)
            _measure_pool(evlist, hi, lo, n, agg[name])       # pool pt. agregat
        out["per_regime"][label] = reg
        pw = "t2_t5"                                            # citirea principală
        print(f"\n=== {label.upper()} | A_full={len(A_full)} A_subset={len(A_subset)} (undef={undefined}) "
              f"C_matched={matched} C_unmatched={unmatched} | fereastra principală [entry+1,entry+4] ===")
        for name in arms:
            w = reg[name].get(pw, {})
            print(f"  {name:9s} n={w.get('n')} MAE_med={w.get('MAE',{}).get('median')} "
                  f"MFE_med={w.get('MFE',{}).get('median')} MFE/MAE_med={w.get('MFE_over_MAE',{}).get('median')} "
                  f"adv_first={w.get('frac_adverse_first')}")

    out["aggregate"] = {a: _summarize(agg[a]) for a in arms}
    print("\n=== AGREGAT — ferestre principale (MFE median, multipli ATR) ===")
    for pw in ("t2_t5", "t2_t10"):
        print(f"  [{pw}]  " + "  ".join(f"{a}={out['aggregate'][a].get(pw,{}).get('MFE',{}).get('median')}" for a in arms))
    print(f"  match total: " + ", ".join(f"{lb}:{out['match'][lb]['C_matched']}✓/{out['match'][lb]['C_unmatched']}✗"
                                         for lb in out["match"]))
    path = os.path.join(_ROOT, "reports", "obdz_three_arm_windows_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/obdz_three_arm_windows_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

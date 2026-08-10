"""RESTANȚELE VECHI — cele trei preconditii care BLOCHEAZĂ orice verdict formal (STAT-DOMAIN-MISMATCH-AND-
RESIDUALS-v1.0, RT-CODE-A-0006). Ordinea OBLIGATORIE din HANDOFF (spec, nu mesaj):

  (1) BLOCUL PE TIMP CALENDARISTIC — blocul = O ZI de tranzacționare; numărul de blocuri = zilele DISTINCTE cu
      tranzacții, NU n/28. `L=28` aplicat pe indexul tranzacției e un TRANSPLANT DE UNITATE (derivat în bare, H=20
      bare ≈ 5h; aplicat pe tranzacții ≈ 28 zile, ×130 mai lung) — se RETRAGE. Bloc-zi > 4×H ⇒ conține integral
      orizontul de dependență. Imun la frecvența de tranzacționare.
  (2) PRECONDIȚIA DE CALIBRARE PER CANDIDAT — matched-null/oracolul e validat DOAR pe stopuri 1,5×ATR; candidații
      folosesc stopuri STRUCTURALE (distribuții de R diferite între ei). Pentru FIECARE: distribuția lui PROPRIE de
      net_R/tranzacție (podită, cu costuri), centrată la medie zero (nul cu adevăr cunoscut, păstrează forma/
      asimetria/masa de podea), ≥1.000 replicări pe grila calendaristică, FPR@0,05 a oracolului bloc-zi, POARTĂ:
      limita superioară CI ≤ 0,07. Peste ⇒ candidatul NU primește p-value. (Caveat-ele mărginesc scopul, NU
      miscalibrarea — un p-value cu FPR necunoscut nu e un p-value.)
  (3) MATRICEA LUNARĂ DE CORELAȚII — BH presupune PRDS, neverificat între ipoteze care împart același segment.
      Corelații perechi ale seriei LUNARE net_R. Regula S-R6 pre-declarată: toate r≥0 ⇒ BH; o pereche material
      negativă ⇒ se partiționează acea pereche, restul pe BH; negativitate difuză nepartiționabilă ⇒ FAMILIA pe BY
      (BY = BH × Σ1/i, i=1..m).

DEMO NEAFECTAT (nu produce p-value). GARD 1 ridicat EXCLUSIV pentru colectarea net_R (P&L), coborât după. GARD 2
neatins. Fără verdict — VE rulează precondiția, Statisticianul decide. Prag S-R2: ≥10 zile distincte (≥20 preferat).
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
_ENGINE = os.path.join(os.path.dirname(_ROOT), "ai_quant_lab-alpha-automation", "demo_gate_engine")
for _p in (_HERE, _ROOT, os.path.join(_ROOT, "edge_research"), _ENGINE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import phase1_screening as PS
from pdh_pdl_demo_engine import ExitReason

_COUNTED = (ExitReason.STOP.value, ExitReason.TARGET.value, ExitReason.TIME_STOP.value)
DAY_MIN = 10                     # S-R2: sub 10 zile distincte ⇒ bloc-bootstrap INDISPONIBIL
DAY_PREF = 20
S_OUTER = 1000                   # replicări de calibrare (spec: ≥1.000)
B_INNER = 1000                   # B al oracolului (registru: ≥1.000)
FPR_GATE = 0.07                  # POARTĂ: limita superioară CI a FPR@0,05
L_OLD = 28                       # vechea lungime de bloc pe INDEX de tranzacție (se retrage)
NEG_MATERIAL = -0.3              # „material negativă" (ecranul anual S-R6)
N_MIN_VERDICT = 25               # familie/matrice: doar candidați verdict-eligibili (N_MIN al triajului)
RESOLVE_MONTHS = 48              # o corelație e RESOLUBILĂ doar cu ≥48 luni comune (SE(r)≈0,14); sub = zgomot


def _wilson(k: int, nn: int) -> tuple[float, float]:
    if nn == 0:
        return (0.0, 1.0)
    z, phat = 1.959963984540054, k / nn
    denom = 1.0 + z * z / nn
    center = (phat + z * z / (2 * nn)) / denom
    half = z * ((phat * (1 - phat) / nn + z * z / (4 * nn * nn)) ** 0.5) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def collect_per_trade(regimes: list[Any]) -> dict[str, dict[str, np.ndarray]]:
    """Artefact EXISTENT (nu date noi): net_R/tranzacție + ziua (17:00 NY) + luna, per candidat. P&L → GARD 1."""
    out: dict[str, dict[str, np.ndarray]] = {}
    for cid, _name, runner in PS.CANDIDATES:
        nrs: list[float] = []; days: list[int] = []; months: list[int] = []
        for rd in regimes:
            sigs, results = runner(rd)
            for s, r in zip(sigs, results):
                if r.traded and r.net_R is not None and r.exit_reason in _COUNTED:
                    ei = s.entry_idx
                    nrs.append(float(r.net_R))
                    days.append(int(rd.day[ei]))                 # ordinal absolut de zi (17:00 NY), cauzal
                    dt = pd.to_datetime(int(rd.tm[ei]), unit="s", utc=True)
                    months.append(int(dt.year) * 12 + int(dt.month))
        out[cid] = {"net_R": np.asarray(nrs, dtype=float),
                    "day": np.asarray(days, dtype=np.int64),
                    "month": np.asarray(months, dtype=np.int64)}
    return out


def _day_blocks(net_r: np.ndarray, day: np.ndarray, center: bool) -> tuple[np.ndarray, np.ndarray]:
    """Grupează pe ZI → (sum per zi, mărime per zi). `center` scoate media globală (nul cu medie 0)."""
    x = net_r - net_r.mean() if center else net_r
    uniq = np.unique(day)
    dsum = np.array([x[day == d].sum() for d in uniq], dtype=float)
    dsize = np.array([int((day == d).sum()) for d in uniq], dtype=float)
    return dsum, dsize


def calendar_block_bootstrap(net_r: np.ndarray, day: np.ndarray, b: int, seed: int) -> dict[str, Any]:
    """Bloc-bootstrap pe TIMP CALENDARISTIC: reeșantionează ZILE întregi (bloc natural de mărime variabilă).
    Media resample-ului = Σ(sum zile trase)/Σ(mărime zile trase) — ratio exact al concatenării. Coada dreaptă."""
    dsum0, dsize0 = _day_blocks(net_r, day, center=True)          # nul centrat la 0
    n_days = len(dsum0)
    observed = float(net_r.mean())
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n_days, size=(b, n_days))
    nm = dsum0[idx].sum(axis=1) / dsize0[idx].sum(axis=1)         # b medii-nul
    k = int((nm >= observed).sum())
    p_hat = (k + 1) / (b + 1)
    return {"n_trades": int(len(net_r)), "n_blocks_days": n_days, "observed": round(observed, 6),
            "p_hat": round(p_hat, 6), "n_blocks_old_L28": round(len(net_r) / L_OLD, 2)}


def calibrate_candidate(net_r: np.ndarray, day: np.ndarray, s_outer: int, b_inner: int,
                        seed: int) -> dict[str, Any]:
    """FPR@0,05 a oracolului bloc-zi pe distribuția PROPRIE centrată la 0. Outer: `s_outer` seturi sintetice nule
    (reeșantionare de zile); inner: oracolul bloc-zi (`b_inner`). Poartă: limita superioară CI ≤ 0,07."""
    dsum0, dsize0 = _day_blocks(net_r, day, center=True)
    n_days = len(dsum0)
    rng = np.random.default_rng(seed)
    rejects = 0
    for _ in range(s_outer):
        oidx = rng.integers(0, n_days, size=n_days)              # set sintetic nul = multiset de zile proprii
        ss = dsum0[oidx]; sz = dsize0[oidx]
        obs = float(ss.sum() / sz.sum())                        # media sintetică observată (~0 sub H0)
        ss_c = ss - obs * sz                                    # oracolul RE-CENTREAZĂ setul la PROPRIA medie (0)
        iidx = rng.integers(0, n_days, size=(b_inner, n_days))    # oracolul pe setul sintetic re-centrat
        nm = ss_c[iidx].sum(axis=1) / sz[iidx].sum(axis=1)       # nul ~ 0 (nu centrat pe obs — bug reparat)
        p = (int((nm >= obs).sum()) + 1) / (b_inner + 1)
        if p < 0.05:
            rejects += 1
    fpr = rejects / s_outer
    lo, hi = _wilson(rejects, s_outer)
    return {"fpr05": round(fpr, 4), "ci95": [round(lo, 4), round(hi, 4)],
            "gate_upper_le_0_07": bool(hi <= FPR_GATE), "n_days": n_days}


def monthly_matrix(per: dict[str, dict[str, np.ndarray]], cids: list[str]) -> dict[str, Any]:
    """Serii LUNARE net_R (sumă/lună) per candidat; corelații perechi pe lunile COMUNE. Regula S-R6 pre-declarată."""
    series: dict[str, dict[int, float]] = {}
    for cid in cids:
        m = per[cid]["month"]; x = per[cid]["net_R"]
        d: dict[int, float] = {}
        for mk in np.unique(m):
            d[int(mk)] = float(x[m == mk].sum())
        series[cid] = d
    pairs: list[dict[str, Any]] = []
    rs: list[float] = []
    for i in range(len(cids)):
        for j in range(i + 1, len(cids)):
            a, bser = series[cids[i]], series[cids[j]]
            common = sorted(set(a) & set(bser))
            if len(common) < 6:                                  # prea puține luni comune pt. o corelație
                continue
            va = np.array([a[mk] for mk in common]); vb = np.array([bser[mk] for mk in common])
            if va.std() == 0 or vb.std() == 0:
                continue
            r = float(np.corrcoef(va, vb)[0, 1])
            rs.append(r)
            pairs.append({"a": cids[i], "b": cids[j], "r": round(r, 3), "n_months": len(common)})
    arr = np.asarray(rs) if rs else np.asarray([0.0])
    # RESOLVABILITATE: doar perechile cu ≥RESOLVE_MONTHS luni comune pot decide regula; restul = zgomot (SE(r) mare)
    resolvable = [p for p in pairs if p["n_months"] >= RESOLVE_MONTHS]
    neg_resolv = [p for p in resolvable if p["r"] < NEG_MATERIAL]
    neg_noise = [p for p in pairs if p["r"] < NEG_MATERIAL and p["n_months"] < RESOLVE_MONTHS]
    r_res = np.asarray([p["r"] for p in resolvable]) if resolvable else np.asarray([0.0])
    # PARTIȚIONABIL = există un candidat prezent în TOATE perechile material-negative (pivot comun ⇒ se izolează).
    pair_sets = [{p["a"], p["b"]} for p in neg_resolv]
    common_pivots = set.intersection(*pair_sets) if pair_sets else set()
    pivot = sorted(common_pivots)[0] if common_pivots else None
    if len(neg_resolv) == 0:
        rule = "ALL RESOLVABLE pairs r>=-0.3 -> PRDS supported empirically, BH applies (noise-negatives excluded)"
    elif pivot is not None:
        rule = f"PARTITIONABLE: all {len(neg_resolv)} resolvable material-negative pairs share {pivot} -> partition {pivot} (CAND-0009 procedure), rest of family on BH"
    else:
        rule = f"DIFFUSE material-negative ({len(neg_resolv)} resolvable pairs, no common pivot) -> FAMILY on BY (BH x sum(1/i))"
    return {"n_pairs": len(pairs), "n_resolvable": len(resolvable), "mean_r": round(float(arr.mean()), 3),
            "median_r": round(float(np.median(arr)), 3), "min_r": round(float(arr.min()), 3),
            "max_r": round(float(arr.max()), 3), "positive": int((arr >= 0).sum()),
            "resolvable_mean_r": round(float(r_res.mean()), 3),
            "material_negative_resolvable": [{**p} for p in neg_resolv], "partition_pivot": pivot,
            "material_negative_noise_excluded": len(neg_noise), "rule_fired": rule,
            "BY_cost_factor": round(float(sum(1.0 / i for i in range(1, len(cids) + 1))), 2)}


def main() -> int:
    print("RESTANȚE — cele trei precondiții (ordine spec: bloc-zi → calibrare → matrice). GARD 1 exclusiv.")
    regimes = PS.load_regimes()
    per = collect_per_trade(regimes)
    eligible = [cid for cid in per if len(np.unique(per[cid]["day"])) >= DAY_MIN]
    out: dict[str, Any] = {"note": "descriptive precondition run; no verdict; DEMO unaffected",
                           "params": {"S_outer": S_OUTER, "B_inner": B_INNER, "FPR_gate": FPR_GATE,
                                      "day_min": DAY_MIN}, "eligible": eligible}

    # ── (1) BLOCUL PE TIMP CALENDARISTIC ──
    print("\n########## (1) BLOC PE TIMP CALENDARISTIC — zile distincte vs vechiul n/28 ##########")
    t1: dict[str, Any] = {}
    for cid in per:
        nr = per[cid]["net_R"]; day = per[cid]["day"]
        nd = int(len(np.unique(day)))
        t1[cid] = {"n_trades": int(len(nr)), "n_blocks_days": nd, "n_blocks_old_L28": round(len(nr) / L_OLD, 2),
                   "eligible_ge10_days": nd >= DAY_MIN, "preferred_ge20": nd >= DAY_PREF}
        if len(nr) >= 25:
            print(f"  {cid}: n={len(nr):5d} | ZILE distincte(=blocuri)={nd:4d} | vechi n/28={len(nr)/L_OLD:6.1f} "
                  f"| ×{nd/(len(nr)/L_OLD) if len(nr) else 0:.1f} mai multe blocuri | "
                  f"{'ELIGIBIL' if nd >= DAY_MIN else 'SUB-PRAG (no p-value path)'}")
    out["task1_calendar_blocks"] = t1

    # ── (2) PRECONDIȚIA DE CALIBRARE PER CANDIDAT ──
    print(f"\n########## (2) CALIBRARE PER CANDIDAT — FPR@0,05 oracol bloc-zi (S={S_OUTER}, B={B_INNER}), poartă CI≤{FPR_GATE} ##########")
    t2: dict[str, Any] = {}
    for ci, cid in enumerate(eligible):
        cal = calibrate_candidate(per[cid]["net_R"], per[cid]["day"], S_OUTER, B_INNER, seed=7_000_000 + ci * 1000)
        t2[cid] = cal
        print(f"  {cid}: FPR@0,05={cal['fpr05']:.4f} CI{cal['ci95']} zile={cal['n_days']:4d} "
              f"→ {'PASS (oracol valid)' if cal['gate_upper_le_0_07'] else 'FAIL → NU primește p-value'}")
    n_pass = sum(1 for c in t2.values() if c["gate_upper_le_0_07"])
    print(f"  → {n_pass}/{len(t2)} trec precondiția de calibrare")
    out["task2_calibration"] = t2

    # ── (3) MATRICEA LUNARĂ DE CORELAȚII (doar candidați verdict-eligibili n>=25) ──
    print("\n########## (3) MATRICE LUNARĂ DE CORELAȚII — regula S-R6 (PRDS pentru BH) ##########")
    mat_elig = [cid for cid in per if len(per[cid]["net_R"]) >= N_MIN_VERDICT]
    mm = monthly_matrix(per, mat_elig)
    out["task3_monthly_matrix"] = {**mm, "candidates": mat_elig}
    print(f"  candidați (n>=25): {len(mat_elig)} | perechi={mm['n_pairs']} (rezolubile ≥{RESOLVE_MONTHS} luni: {mm['n_resolvable']})")
    print(f"  media r={mm['mean_r']} mediana={mm['median_r']} min={mm['min_r']} max={mm['max_r']} | "
          f"pozitive={mm['positive']} | media r (rezolubile)={mm['resolvable_mean_r']}")
    print(f"  material-negative REZOLUBILE (≥{RESOLVE_MONTHS} luni): {len(mm['material_negative_resolvable'])}")
    for p in mm["material_negative_resolvable"]:
        print(f"    {p['a']} ~ {p['b']} r={p['r']} ({p['n_months']} luni) — REAL")
    print(f"  material-negative de ZGOMOT excluse (<{RESOLVE_MONTHS} luni, SE(r) mare): {mm['material_negative_noise_excluded']}")
    print(f"  REGULA: {mm['rule_fired']}")
    print(f"  cost fallback BY (dacă difuz) = ×{mm['BY_cost_factor']} pe m={len(mat_elig)}")

    path = os.path.join(_ROOT, "reports", "restante_validation_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/restante_validation_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

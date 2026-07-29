"""Rulare DESCRIPTIVĂ a 7 familii SMC pe descoperirea M15_v2 (Mandat 6.2). READ-ONLY, in-sample.

Familii: S2, S3, S7, S11, S13, S16, S17. NU S1 (CLOSED_DEFINITIVELY), NU S10 (verdict de rebuclă deschis).
Contract de risc NESCHIMBAT (cum compilat în trading_strategies, model 5.11): stop = spike + 2 pips fără
podea (doar normalizator R, ieșire PURĂ PE TIMP), eligibilitate [10,1;65,0). Orizonturi din manifest:
20 (S2/S3/S7/S11/S13), 92 (S16), 460 (S17).

METRICA DE DECIZIE (Corecția 1, Mandat 6.2): EDGE BRUT ÎN DOLARI = media gross_$ per tranzacție
(= expectancy_$ + cost = expectancy_R × R_mediu + 0,40). Direct comparabilă cu costul de 0,40$. Winrate și
expectancy_R NU spun dacă o familie e viabilă; edge_brut_$ da. Fără agregare de portofoliu (Corecția 3):
raportare PER FAMILIE × REGIM, fiecare stare independentă.

Fără FDR / fără corecție de testare multiplă (măsurătoare descriptivă — Statisticianul decide corecția
după ce vede structura). WP-5' rulat PER familie (nu pe array combinat), L≥28. GARD 2 neatins, sigilat
neatins, nicio autorizare scrisă. NU interpretez — raportez cifrele.

% excluse prin eligibilitate: enumerăm TOATE trigger-ele structurale lărgind temporar ELIG_LO/ELIG_HI ale
modulului (harness de măsurare — sursa înghețată NEEDITATĂ, valorile restaurate; setul eligibil rezultat e
IDENTIC cu output-ul înghețat [10,1;65,0)).

⚠ CAVEAT WP-5' (același ridicat la S1): oracolul block_bootstrap@v1 a fost calibrat pe seria de SUME-pe-
orizont, la n poolat ≈21.048, H=20, L≥H; aplicat pe net_R (R-normalizat + cost) e un transform suplimentar;
n per-familie/regim e mai mic. Pentru S16 (H=92) și S17 (H=460), L=28 < H → blocul NU conține suprapunerea
finită; oracolul e ÎN AFARA scopului validat — p raportat dar marcat NEVALIDAT.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Callable

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
import split_manifest as SM
from market_structure import Block
from institutional_levels import derive_week_index
import trading_strategies as TS
import block_bootstrap as BB

TICK, COST = 0.10, 0.40
L, BOOT, SEED = 28, 2000, 20260729
EXPECTED = {"bear": 52_403, "bull": 52_851, "correction": 25_237}

# (nume, funcție-detector pe context, orizont)
FAMILIES: list[tuple[str, Callable[[Any], list[TS.StrategySignal]], int]] = [
    ("S2", lambda a: TS.detect_s2(a["o"], a["h"], a["l"], a["c"], a["blocks"]), 20),
    ("S3", lambda a: TS.detect_s3(a["o"], a["h"], a["l"], a["c"], a["blocks"]), 20),
    ("S7", lambda a: TS.detect_s7(a["o"], a["h"], a["l"], a["c"], a["blocks"]), 20),
    ("S11", lambda a: TS.detect_s11(a["o"], a["h"], a["l"], a["c"], a["blocks"]), 20),
    ("S13", lambda a: TS.detect_s13(a["o"], a["h"], a["l"], a["c"], a["blocks"]), 20),
    ("S16", lambda a: TS.detect_s16(a["o"], a["h"], a["l"], a["c"], a["day"], a["blocks"]), 92),
    ("S17", lambda a: TS.detect_s17(a["o"], a["h"], a["l"], a["c"], a["day"], a["week"], a["blocks"]), 460),
]


def _day_index(sub: Any) -> list[int]:
    """Ordinal de zi cu ancora 17:00 NY DST-aware (resample_ny.py), aplicat caller-side (institutional_levels)."""
    dt = pd.to_datetime(sub["time"], unit="s", utc=True)
    ny = dt.dt.tz_convert("America/New_York").dt.tz_localize(None)
    shifted = ny - pd.Timedelta(hours=17)
    day_floor = shifted.dt.floor("D")
    return day_floor.values.astype("datetime64[D]").astype("int64").tolist()


def _regime_label(seg: dict[str, Any], i: int) -> str:
    for k in ("regime", "label", "name"):
        v = seg.get(k)
        if isinstance(v, str):
            return v.lower()
    return ["bear", "bull", "correction"][i]


def _context(sub: Any) -> dict[str, Any]:
    o = sub["open"].to_numpy(); h = sub["high"].to_numpy()
    lo = sub["low"].to_numpy(); c = sub["close"].to_numpy()
    n = len(sub)
    day = _day_index(sub)
    return {"o": o.tolist(), "h": h.tolist(), "l": lo.tolist(), "c": c.tolist(),
            "blocks": [Block(0, n)], "day": day, "week": derive_week_index(day),
            "O": o, "H": h, "L": lo, "C": c, "n": n}


def _all_triggers(detect: Callable[[Any], list[TS.StrategySignal]], ctx: dict[str, Any]) -> list[TS.StrategySignal]:
    """Toate trigger-ele (lărgim temporar eligibilitatea; sursa înghețată neatinsă; restaurăm)."""
    lo0, hi0 = TS.ELIG_LO, TS.ELIG_HI
    TS.ELIG_LO, TS.ELIG_HI = -1.0, 1e18
    try:
        return detect(ctx)
    finally:
        TS.ELIG_LO, TS.ELIG_HI = lo0, hi0


def _cell(fam: str, horizon: int, ctx: dict[str, Any]) -> dict[str, Any]:
    O, C, n = ctx["O"], ctx["C"], ctx["n"]
    detect = next(fn for nm, fn, _h in FAMILIES if nm == fam)
    triggers = _all_triggers(detect, ctx)
    total = len(triggers)
    eligible = [s for s in triggers if 10.1 <= s.spike_pips < 65.0]      # identic cu output-ul înghețat
    pct_excluded = 100.0 * (total - len(eligible)) / total if total else 0.0

    net_d: list[float] = []; net_r: list[float] = []; gross_d: list[float] = []; rs: list[float] = []
    edge_excluded = 0
    for s in eligible:
        exit_idx = s.entry_idx + horizon
        if exit_idx >= n:
            edge_excluded += 1
            continue
        g = s.direction * (float(C[exit_idx]) - float(O[s.entry_idx]))
        r_dollars = TS.risk_R_dollars(s.spike_pips)
        nd = g - COST
        gross_d.append(g); net_d.append(nd); net_r.append(nd / r_dollars); rs.append(r_dollars)

    nt = len(net_d)
    if nt == 0:
        return dict(family=fam, n_trades=0, pct_excluded_eligibility=round(pct_excluded, 2),
                    edge_excluded=edge_excluded, note="fără tranzacții eligibile cu orizont complet")
    net_r_a = np.asarray(net_r); net_d_a = np.asarray(net_d); gross_a = np.asarray(gross_d)
    sumR = float(net_r_a.sum()); best_r = float(np.sort(net_r_a)[::-1][0])
    p_hat = BB.run(net_r_a, block_length=L, B=BOOT, tail="right", centering="zero", seed=SEED)["p_hat"] \
        if nt > L else None                                         # block_bootstrap cere L ≤ n
    return dict(
        family=fam, n_trades=nt, pct_excluded_eligibility=round(pct_excluded, 2), edge_excluded=edge_excluded,
        winrate=round(float((net_d_a > 0).mean()), 4),
        expectancy_R=round(float(net_r_a.mean()), 5),
        expectancy_dollars=round(float(net_d_a.mean()), 5),
        edge_brut_dollars=round(float(gross_a.mean()), 5),                # METRICA DE DECIZIE (media gross_$)
        net_sumR=round(sumR, 2), net_sum_dollars=round(float(net_d_a.sum()), 2),
        R_mediu_dollars=round(float(np.mean(rs)), 4),
        best_over_sumR=round(best_r / sumR, 4) if sumR else None, wo1_netR=round(sumR - best_r, 2),
        p_wp5=p_hat, p_wp5_scope=("VALIDAT (H=20, L≥H)" if horizon == 20 else f"NEVALIDAT (H={horizon}>L={L})"))


def main() -> int:
    df, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | discovery bars = {len(df)}")
    if len(df) != 130_491:
        print(f"STOP: {len(df)} bare, aștept 130.491."); return 2
    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]
    t = df["time"].to_numpy()
    contexts: list[tuple[str, dict[str, Any]]] = []
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = df[(t >= s_ep) & (t < e_ep)].reset_index(drop=True)
        if EXPECTED.get(label) not in (None, len(sub)):
            print(f"STOP: regim {label} are {len(sub)} bare, aștept {EXPECTED[label]}."); return 3
        contexts.append((label, _context(sub)))

    out: dict[str, Any] = {"L": L, "B": BOOT, "cost": COST, "results": {}}
    for fam, _fn, horizon in FAMILIES:
        out["results"][fam] = {}
        print(f"\n########## {fam} (H={horizon}) ##########")
        for label, ctx in contexts:
            cell = _cell(fam, horizon, ctx)
            out["results"][fam][label] = cell
            if cell["n_trades"] == 0:
                print(f"  {label:11s} {cell['note']}"); continue
            print(f"  {label:11s} n={cell['n_trades']:5d} excl%={cell['pct_excluded_eligibility']:5.1f} "
                  f"WR={cell['winrate']:.3f} E_R={cell['expectancy_R']:+.4f} E_$={cell['expectancy_dollars']:+.4f} "
                  f"EDGE_BRUT_$={cell['edge_brut_dollars']:+.4f} Rmed=${cell['R_mediu_dollars']:.2f} "
                  f"netR={cell['net_sumR']:+.0f} net$={cell['net_sum_dollars']:+.0f} "
                  f"b/sR={cell['best_over_sumR']} wo1R={cell['wo1_netR']:+.0f} "
                  f"p={cell['p_wp5'] if cell['p_wp5'] is None else round(cell['p_wp5'], 3)} [{cell['p_wp5_scope']}]")

    # structura: câte familii au edge_brut_$ < 0.40 în TOATE regimurile
    fam_all_below = [fam for fam, _f, _h in FAMILIES
                     if all(out["results"][fam][lb].get("edge_brut_dollars", -9) < COST for lb, _c in contexts)]
    print(f"\n########## STRUCTURĂ: {len(fam_all_below)}/7 familii cu edge_brut_$ < 0,40 în TOATE regimurile ##########")
    print(f"  ({', '.join(fam_all_below)})" if fam_all_below else "")
    out["structure_families_all_regimes_edge_below_cost"] = fam_all_below
    path = os.path.join(_ROOT, "reports", "smc_families_descriptive_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"\nrecord -> reports/smc_families_descriptive_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

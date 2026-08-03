"""FAZA 1 — RE-SCREENING v3 (triaj descriptiv). Cei 7 candidați cu ORIZONT nou (Alpha v3.0, `21fb3f9`).

Ieșirea la „granița de bloc" nu se declanșează niciodată pe cont live (confirmat de Statistician + Red Team) →
Alpha a înlocuit-o cu un orizont FIX în bare, folosind constante deja existente în module: CAND-0002 = 460 bare
(COMPRESSION_WINDOW), CAND-0011/0013/0014/0015/0017/0018 = 20 bare (GROUP_A_HORIZON). FĂRĂ primitive noi.

Rulez ACELAȘI generator de semnal cu DOUĂ orizonturi — v2 (granița de bloc, `horizon_override=None`) și v3
(fix), ca diferența să fie EXACT orizontul. Raportez alături + fracția de ieșiri pe TIME-STOP (arată dacă noul
orizont chiar leagă). Costuri modelate identic. NU verdict, NU p-value, NU corecție de testare multiplă.
NEATINȘI (nu re-rulați): CAND-0001/0003/0007/0012/0016/0019 (ieșiri valide live), + CAND-0008/0009/0010 (fără v3).
GARD 1 ridicat exclusiv pentru rulare, coborât după. GARD 2 neatins.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Callable

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from phase1_screening import (
    TICK_SIZE, RegimeData, _metrics, load_regimes,
    gen_cand0002_compression_expansion, gen_cand0011_ob_rejection, gen_cand0013_demand_zone_reentry,
    gen_cand0014_ob_mitigation, gen_cand0015_obrej_fvg_confluence, gen_cand0017_dz_fvg_confluence,
    gen_cand0018_obrej_void_confluence,
)  # phase1_screening's import sets sys.path for the engine + market_state below
from market_state import expansion
from pdh_pdl_demo_engine import DemoSignal, DemoTradeResult, simulate_demo_trades
from dynamic_exit_engine import simulate_demo_trades_dynamic

COMPRESSION_WINDOW, GROUP_A_HORIZON = 460, 20
# (cid, name, generator, is_dynamic, horizon_v3)
CORRECTED: list[tuple[str, str, Any, bool, int]] = [
    ("CAND-0002", "COMPRESSION-EXPANSION", gen_cand0002_compression_expansion, True, COMPRESSION_WINDOW),
    ("CAND-0011", "OB-SWEEP-REJECTION", gen_cand0011_ob_rejection, False, GROUP_A_HORIZON),
    ("CAND-0013", "DEMAND-ZONE-REENTRY", gen_cand0013_demand_zone_reentry, False, GROUP_A_HORIZON),
    ("CAND-0014", "OB-MITIGATION", gen_cand0014_ob_mitigation, False, GROUP_A_HORIZON),
    ("CAND-0015", "OBREJ-FVG-CONFLUENCE", gen_cand0015_obrej_fvg_confluence, False, GROUP_A_HORIZON),
    ("CAND-0017", "DZ-FVG-CONFLUENCE", gen_cand0017_dz_fvg_confluence, False, GROUP_A_HORIZON),
    ("CAND-0018", "OBREJ-VOID-CONFLUENCE", gen_cand0018_obrej_void_confluence, False, GROUP_A_HORIZON),
]


def _run(regimes: list[RegimeData], gen: Any, dynamic: bool, horizon: int | None) -> dict[str, Any]:
    rows: list[tuple[int, str, DemoTradeResult]] = []
    for rd in regimes:
        rd.horizon_override = horizon                         # None = v2 (granița de bloc); H = v3 (fix)
        if dynamic:
            exp = expansion(rd.o, rd.h, rd.l, rd.c)
            exp_dir = [(1 if rd.c[j] > rd.o[j] else -1) if exp[j] else 0 for j in range(rd.n)]
            sigs: list[DemoSignal] = gen(rd, exp)
            results = simulate_demo_trades_dynamic(sigs, rd.o, rd.h, rd.l, rd.c, exp_dir, TICK_SIZE)
        else:
            sigs = gen(rd)
            results = simulate_demo_trades(sigs, rd.o, rd.h, rd.l, rd.c, TICK_SIZE)
        rd.horizon_override = None                            # reset (obiecte partajate)
        for s, res in zip(sigs, results):
            rows.append((int(rd.year[s.entry_idx]), rd.label, res))
    return _metrics(rows)


def _fmt(m: dict[str, Any]) -> str:
    if m["n_trades"] == 0:
        return f"n=0 (invalid={m['n_invalid']})"
    a = m["annual_stability"]; g = m["regime_stability"]
    return (f"n={m['n_trades']:5d} WR={m['winrate']:.3f} PF={m['profit_factor']} "
            f"E_R={m['expectancy_R']:+.4f} netR={m['net_R']:+.1f} net$={m['net_dollars']:+.1f} "
            f"DD_R={m['max_drawdown_R']} Sh={m['sharpe_per_trade']} "
            f"ani={a['positive_years']}/{a['eligible_years']} reg={g['positive_regimes']}/3 "
            f"| ieșiri: stop={m['exit_stop']} tinta={m['exit_target']} time={m['exit_time_stop']} "
            f"(time-stop {m['frac_time_stop']})")


def main() -> int:
    print(f"RE-SCREENING v3 | costuri modelate | orizont: 0002=460 bare, restul=20 bare | fără verdict")
    regimes = load_regimes()
    out: dict[str, Any] = {"note": "v2 vs v3 horizon comparison; descriptive triage; no verdict", "candidates": {}}
    for cid, name, gen, dynamic, hz in CORRECTED:
        m2 = _run(regimes, gen, dynamic, None)               # v2: granița de bloc
        m3 = _run(regimes, gen, dynamic, hz)                 # v3: orizont fix
        out["candidates"][cid] = {"policy": name, "horizon_v3_bars": hz, "v2": m2, "v3": m3}
        print(f"\n########## {cid} {name}  (orizont v3 = {hz} bare) ##########")
        print(f"  v2 (bloc): {_fmt(m2)}")
        print(f"  v3 (fix) : {_fmt(m3)}")
    import json
    path = os.path.join(os.path.dirname(_HERE), "reports", "phase1_rescreen_v3_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/phase1_rescreen_v3_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

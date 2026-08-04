"""SARCINA 2 — re-screening CAND-0009 (LEVEL-BREAK-DRIVE) cu orizontul CORECT v3 = 14 bare (ATR_WINDOW).

Cifrele vechi foloseau granița de BLOC (v2), care NU există pe un cont live (un bloc e construcție de discovery)
→ leg-ul nu s-ar declanșa niciodată, trade rămâne deschis la infinit. v3 îl înlocuiește cu un time-stop live-valid
de 14 bare (ATR_WINDOW — constanta din care e calculat însuși `expansion()`, trigger-ul politicii). Raportez VECHI
(bloc) vs NOU (14 bare), setări identice, DOAR orizontul diferă. Triaj DESCRIPTIV; fără p-value, fără verdict.

GARD 1 ridicat EXCLUSIV pentru rulare (din afară, flag comutat), coborât după. GARD 2 neatins. NU comit JSON.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_ENGINE = os.path.join(os.path.dirname(_ROOT), "ai_quant_lab-alpha-automation", "demo_gate_engine")
for _p in (_HERE, _ROOT, os.path.join(_ROOT, "edge_research"), _ENGINE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from market_state import ATR_WINDOW, expansion
from dynamic_exit_engine import simulate_demo_trades_dynamic
from phase1_screening import (REGIMES, TICK_SIZE, RegimeData, _metrics, gen_cand0009_level_break_drive,
                              load_regimes)


def _run(regimes: list[RegimeData], block: bool) -> dict[str, Any]:
    rows: list[tuple[int, str, Any]] = []
    for rd in regimes:
        exp = expansion(rd.o, rd.h, rd.l, rd.c)
        exp_dir = [(1 if rd.c[j] > rd.o[j] else -1) if exp[j] else 0 for j in range(rd.n)]
        sigs = gen_cand0009_level_break_drive(rd, exp, block=block)
        results = simulate_demo_trades_dynamic(sigs, rd.o, rd.h, rd.l, rd.c, exp_dir, TICK_SIZE)
        for s, res in zip(sigs, results):
            rows.append((int(rd.year[s.entry_idx]), rd.label, res))
    return _metrics(rows)


def _line(tag: str, m: dict[str, Any]) -> None:
    if m["n_trades"] == 0:
        print(f"  {tag:5s} n=0 (invalid={m['n_invalid']} no_trade={m['n_no_trade']})"); return
    a = m["annual_stability"]; g = m["regime_stability"]
    print(f"  {tag:5s} n={m['n_trades']:4d} WR={m['winrate']} PF={m['profit_factor']} "
          f"E_R={m['expectancy_R']:+.4f} netR={m['net_R']:+.2f} net$={m['net_dollars']:+.2f} "
          f"| ani+={a['positive_years']}/{a['eligible_years']} reg+={g['positive_regimes']}/3")


def main() -> int:
    print(f"loader v6 | CAND-0009 re-screening | ATR_WINDOW={ATR_WINDOW} | tick={TICK_SIZE}")
    regimes = load_regimes()
    old = _run(regimes, block=True)                            # VECHI: granița de BLOC (v2, discovery-only)
    new = _run(regimes, block=False)                           # NOU: 14 bare ATR_WINDOW (v3, live-valid)
    print("\n########## CAND-0009 LEVEL-BREAK-DRIVE — VECHI (bloc) vs NOU (14 bare) ##########")
    _line("VECHI", old)
    _line("NOU", new)
    out = {"note": "descriptive; no p-value; costs modeled; horizon old=block new=ATR_WINDOW=14",
           "CAND-0009": {"old_block_horizon": old, "new_atr_window_14": new}}
    path = os.path.join(_ROOT, "reports", "rescreen_cand0009_v3_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/rescreen_cand0009_v3_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

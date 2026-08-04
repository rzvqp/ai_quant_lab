"""CONSECINȚA D1 (RT-CODE-A-0005) — câte tranzacții de screening își schimbă rezultatul după reparație.

Toate cifrele de screening au fost produse cu defectul D1 (S1 NEimpus pe bara de intrare la tranzacțiile nepodite).
Măsor DIRECT: rulez fiecare semnal prin motorul REPARAT (nou) și printr-o REPLICĂ fidelă a motorului DEFECT (vechi
= identic, dar FĂRĂ ramura STOP pe bara de intrare la nepodite). Perechez per-tranzacție (semnale deterministe,
aceeași ordine) și număr: câte schimbă exit_reason, câte inversează semnul net_R (câștig→pierdere), netR vechi vs
nou per candidat, și dacă se schimbă CLASAMENTUL. Singura diferență între motoare e D1 (F3 mereu satisfăcut la
screening; backstop-ul clauzei-3 pre-emptat). GARD 1 ridicat exclusiv; GARD 2 neatins. Fără verdict — descriptiv.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Sequence

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_ENGINE = os.path.join(os.path.dirname(_ROOT), "ai_quant_lab-alpha-automation", "demo_gate_engine")
for _p in (_HERE, _ROOT, os.path.join(_ROOT, "edge_research"), _ENGINE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import phase1_screening as PS
from pdh_pdl_demo_engine import DemoSignal, DemoTradeResult, ExitReason, min_executable_risk

NEW_FIXED = getattr(PS, "simulate_demo_trades")
NEW_DYN = getattr(PS, "simulate_demo_trades_dynamic")


def _old_common(sig: DemoSignal, o: Sequence[float], h: Sequence[float], l: Sequence[float],
                c: Sequence[float], tick: float) -> tuple[Any, ...]:
    d = sig.direction; ei = sig.entry_idx; entry = float(o[ei])
    ssd = abs(entry - sig.strategy_stop_price)
    me = min_executable_risk(sig.effective_spread, tick, sig.atr)
    esd = max(ssd, me); floored = ssd < me
    esp = entry - d * esd
    return d, ei, entry, ssd, me, esd, floored, esp


def _mk_old(sig: DemoSignal, d: int, ei: int, entry: float, ssd: float, me: float, esd: float, floored: bool,
            esp: float, traded: bool, reason: ExitReason, xi: int | None, xp: float | None, order: str) -> DemoTradeResult:
    net_R = net_d = None
    if xp is not None and traded and esd > 0:
        net_R = (d * (xp - entry) - sig.cost) / esd; net_d = net_R * esd
    return DemoTradeResult(
        traded=traded, exit_reason=reason.value, exit_idx=xi, exit_price=xp, net_R=net_R, net_dollars=net_d,
        entry_idx=ei, entry_price=entry, direction=d, time_stop_idx=sig.time_stop_idx, intrabar_ordering=order,
        effective_spread=sig.effective_spread, strategy_stop_distance=ssd, min_executable_risk=me,
        executable_stop_distance=esd, floored=floored, executable_stop_price=esp,
        target_scan_start=ei + 1, target_scan_end=sig.time_stop_idx)


def _old_trade(sig: DemoSignal, o: Sequence[float], h: Sequence[float], l: Sequence[float],
               c: Sequence[float], tick: float) -> DemoTradeResult:
    """Motorul VECHI (pre-D1): bara de intrare verificată DOAR când e podită. Nepodit → SĂRITĂ (defectul)."""
    d, ei, entry, ssd, me, esd, floored, esp = _old_common(sig, o, h, l, c, tick)
    ss, se = ei + 1, sig.time_stop_idx
    if esd <= 0:
        return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, True, ExitReason.INVALID_EXECUTION, None, None, "zero_or_negative_risk")
    if (d > 0 and entry >= sig.target_price) or (d < 0 and entry <= sig.target_price):
        return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, False, ExitReason.NO_TRADE, None, None, "no_trade_entry_beyond_target")
    if (d > 0 and entry <= sig.strategy_stop_price) or (d < 0 and entry >= sig.strategy_stop_price):
        return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, False, ExitReason.NO_TRADE, None, None, "no_trade_entry_beyond_structural_stop")
    breach = (l[ei] <= esp) if d > 0 else (h[ei] >= esp)
    if floored and breach:                                       # DOAR podit (defectul: nepodit NEverificat)
        return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, True, ExitReason.INVALID_EXECUTION, ei, esp, "gap_through_floored_stop_at_entry")
    for j in range(ss, se + 1):
        hitS = (l[j] <= esp) if d > 0 else (h[j] >= esp)
        hitT = (h[j] >= sig.target_price) if d > 0 else (l[j] <= sig.target_price)
        boundary = (j == se)
        if hitS:
            order = ("stop_over_target_time_stop" if (hitT and boundary) else "stop_over_target" if hitT
                     else "stop_over_time_stop" if boundary else "stop")
            return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, True, ExitReason.STOP, j, esp, order)
        if boundary:
            return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, True, ExitReason.TIME_STOP, j, float(c[j]),
                           "time_stop_over_target" if hitT else "time_stop")
        if hitT:
            return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, True, ExitReason.TARGET, j, sig.target_price, "target")
    return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, True, ExitReason.TIME_STOP, se, float(c[se]), "time_stop")


def _old_trade_dyn(sig: DemoSignal, o: Sequence[float], h: Sequence[float], l: Sequence[float],
                   c: Sequence[float], ed: Sequence[int], tick: float) -> DemoTradeResult:
    d, ei, entry, ssd, me, esd, floored, esp = _old_common(sig, o, h, l, c, tick)
    ss, se = ei + 1, sig.time_stop_idx
    if esd <= 0:
        return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, True, ExitReason.INVALID_EXECUTION, None, None, "zero_or_negative_risk")
    if (d > 0 and entry <= sig.strategy_stop_price) or (d < 0 and entry >= sig.strategy_stop_price):
        return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, False, ExitReason.NO_TRADE, None, None, "no_trade_entry_beyond_structural_stop")
    breach = (l[ei] <= esp) if d > 0 else (h[ei] >= esp)
    if floored and breach:
        return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, True, ExitReason.INVALID_EXECUTION, ei, esp, "gap_through_floored_stop_at_entry")
    for j in range(ss, se + 1):
        hitS = (l[j] <= esp) if d > 0 else (h[j] >= esp)
        opposing = ed[j] == -d; boundary = (j == se)
        if hitS:
            order = ("stop_over_opposing" if opposing else "stop_over_time_stop" if boundary else "stop")
            return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, True, ExitReason.STOP, j, esp, order)
        if boundary:
            return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, True, ExitReason.TIME_STOP, j, float(c[j]),
                           "time_stop_over_opposing" if opposing else "time_stop")
        if opposing:
            return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, True, ExitReason.TARGET, j + 1, float(o[j + 1]), "opposing_expansion")
    return _mk_old(sig, d, ei, entry, ssd, me, esd, floored, esp, True, ExitReason.TIME_STOP, se, float(c[se]), "time_stop")


def _old_batch(signals: Sequence[DemoSignal], o: Any, h: Any, l: Any, c: Any, tick: float) -> list[DemoTradeResult]:
    return [_old_trade(s, o, h, l, c, tick) for s in signals]


def _old_batch_dyn(signals: Sequence[DemoSignal], o: Any, h: Any, l: Any, c: Any, ed: Any, tick: float) -> list[DemoTradeResult]:
    return [_old_trade_dyn(s, o, h, l, c, ed, tick) for s in signals]


_COUNTED = (ExitReason.STOP.value, ExitReason.TARGET.value, ExitReason.TIME_STOP.value)


def _netR(results: list[DemoTradeResult]) -> float:
    return round(sum(r.net_R for r in results if r.traded and r.net_R is not None and r.exit_reason in _COUNTED), 2)


def main() -> int:
    print("CONSECINȚA D1 — vechi (defect) vs nou (reparat), per-tranzacție")
    regimes = PS.load_regimes()
    rows: list[dict[str, Any]] = []
    tot_trades = tot_changed = tot_flip = 0
    for cid, name, runner in PS.CANDIDATES:
        old_all: list[DemoTradeResult] = []; new_all: list[DemoTradeResult] = []
        for rd in regimes:
            setattr(PS, "simulate_demo_trades", NEW_FIXED); setattr(PS, "simulate_demo_trades_dynamic", NEW_DYN)
            _s_new, res_new = runner(rd)
            setattr(PS, "simulate_demo_trades", _old_batch); setattr(PS, "simulate_demo_trades_dynamic", _old_batch_dyn)
            _s_old, res_old = runner(rd)
            new_all.extend(res_new); old_all.extend(res_old)
        setattr(PS, "simulate_demo_trades", NEW_FIXED); setattr(PS, "simulate_demo_trades_dynamic", NEW_DYN)
        changed = flip = 0
        for a, b in zip(old_all, new_all):
            if a.exit_reason != b.exit_reason:
                changed += 1
                ra = a.net_R if (a.net_R is not None and a.exit_reason in _COUNTED) else 0.0
                rb = b.net_R if (b.net_R is not None and b.exit_reason in _COUNTED) else 0.0
                if (ra > 0) != (rb > 0):
                    flip += 1
        onet = _netR(old_all); nnet = _netR(new_all)
        n = sum(1 for r in new_all if r.traded and r.exit_reason in _COUNTED)
        rows.append({"cid": cid, "name": name, "n": n, "changed": changed, "flip": flip,
                     "old_netR": onet, "new_netR": nnet, "delta_netR": round(nnet - onet, 2)})
        tot_trades += n; tot_changed += changed; tot_flip += flip

    old_rank = [r["cid"] for r in sorted(rows, key=lambda r: -r["old_netR"])]
    new_rank = [r["cid"] for r in sorted(rows, key=lambda r: -r["new_netR"])]
    rank_changed = old_rank != new_rank

    print(f"\ntotal tranzacții={tot_trades} | schimbă exit_reason={tot_changed} "
          f"({100.0*tot_changed/tot_trades if tot_trades else 0:.2f}%) | inversează semn net_R={tot_flip}")
    print(f"CLASAMENT (după netR) schimbat: {rank_changed}")
    print("\ncandidați cu schimbări (changed>0), sortați după |delta netR|:")
    for r in sorted([x for x in rows if x["changed"] > 0], key=lambda x: -abs(x["delta_netR"])):
        print(f"  {r['cid']} {r['name']:26s} n={r['n']:5d} changed={r['changed']:4d} flip={r['flip']:4d} "
              f"| netR {r['old_netR']:+.1f} → {r['new_netR']:+.1f} (Δ{r['delta_netR']:+.1f})")
    print("\nTOP 8 clasament — vechi vs nou:")
    for i in range(min(8, len(old_rank))):
        print(f"  {i+1}. vechi={old_rank[i]:10s}  nou={new_rank[i]:10s}")

    out = {"note": "D1 consequence; descriptive; no verdict", "total_trades": tot_trades,
           "changed": tot_changed, "sign_flips": tot_flip, "ranking_changed": rank_changed,
           "old_ranking": old_rank, "new_ranking": new_rank, "per_candidate": rows}
    path = os.path.join(_ROOT, "reports", "measure_d1_consequence_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/measure_d1_consequence_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

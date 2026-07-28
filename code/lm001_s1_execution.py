"""SMC_S1 / LM-001 — PRIMA EXECUȚIE PE DATE REALE, per regim (Mandat 5.11). READ-ONLY analiză.

Rulează familia ÎNGHEȚATĂ `trading_strategies.detect_s1` (sweep-reject bazin extern D6+D7) pe DESCOPERIREA
M15_v2 livrată de loader-ul oficial v6 (fail-closed, discovery-only). NU atinge GARD 2, NU emite autorizare,
NU atinge sigilatul. NU ajustează niciun parametru. NU incrementează manifestul.

De ce NU prin orchestrator.execute(): acela rulează pe un SINGUR Block(0,n) peste toată descoperirea, ceea
ce (a) traversează granițele de regim / golurile de timp (încalcă confinarea D4) și (b) nu poate produce
livrabilul PER REGIM. Aici aplic ACEEAȘI funcție înghețată `detect_s1`, dar per segment de regim (Block
propriu), exact tiparul validat în wp5_battery. GARD 1 e ridicat (GATED_BY_CTO=False); GARD 2 intact.

Contract Open-R (frozen): stop = spike + 2 pips (fără podea), eligibilitate spike ∈ [10,1;65,0) pips,
orizont 20 bare, ieșire pură pe TIMP (close[entry+20]), fără take-profit. Evenimentele cu orizont incomplet
(entry+20 ≥ n_segment) sunt EXCLUSE (populația validată Q2 cere orizont complet) — raportate separat.

Test: block_bootstrap@v1 (memorie finită, WP-5'), L=28, B=10.000, tail='right', centering='zero',
H0: mu_netR ≤ 0. ⚠ SCOP: metoda a fost calibrată pe seria de SUME-pe-orizont, la n POOLAT ≈21.048; aici o
aplic pe seria net_R (R-normalizată + cost) PER REGIM (n mai mic). Dependența de SUPRAPUNERE (ce a fost
validat) e păstrată de ambele; R-normalizarea per-eveniment e un transform suplimentar, iar n per-regim <
n validat. Raportez p-ul ca INSTRUIT și semnalez scopul — NU ajustez nimic.

REGULĂ FIXATĂ ÎNAINTE DE REZULTAT: descoperirea e in-sample. Orice rezultat, indiferent de semn, e un
CANDIDAT, nu o confirmare. Raportez și mă opresc. Verdictul e al Statisticianului.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # consola Windows cp1250 → utf-8 (cosmetic)

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT, os.path.join(_ROOT, "edge_research"), os.path.join(_ROOT, "edge_research", "lm001_s8")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from edge_research._common import PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC, load
import split_manifest as SM
from market_structure import Block, detect_swings, label_structure
from liquidity_mechanics import PoolSide, PoolTier, build_pools, detect_sweeps
import trading_strategies as TS
import block_bootstrap as BB

TICK, H, L, B, SEED = 0.10, 20, 28, 2_000, 20260729   # B=2000 = valoarea de calibrare WP-5' (Mandat 5.7)
EXPECTED = {"bear": 52_403, "bull": 52_851, "correction": 25_237}


def _regime_label(seg: dict[str, Any], order_idx: int) -> str:
    for key in ("regime", "label", "name"):
        v = seg.get(key)
        if isinstance(v, str):
            return v.lower()
    return ["bear", "bull", "correction"][order_idx]


def _analyze(label: str, sub: Any) -> dict[str, Any]:
    o = sub["open"].to_numpy(); hi = sub["high"].to_numpy()
    lo = sub["low"].to_numpy(); cl = sub["close"].to_numpy()
    sess = sub["session"].tolist() if "session" in sub.columns else [""] * len(sub)
    n = len(sub)
    blocks = [Block(0, n)]

    # populația de sweep-uri brute (pentru % excluse de eligibilitate)
    swings = label_structure(detect_swings(hi.tolist(), lo.tolist(), blocks, k=2))
    pools = build_pools(swings, PoolTier.EXTERNAL)
    sweeps = detect_sweeps(hi.tolist(), lo.tolist(), cl.tolist(), pools, blocks, require_close_back_inside=True)
    total_valid = 0
    for sw in sweeps:
        c = sw.idx
        if c + 1 >= n:
            continue
        total_valid += 1

    # semnalele ELIGIBILE = familia înghețată SMC_S1
    signals = TS.detect_s1(o.tolist(), hi.tolist(), lo.tolist(), cl.tolist(), blocks)
    n_eligible = len(signals)
    pct_excluded = 100.0 * (total_valid - n_eligible) / total_valid if total_valid else 0.0

    trades: list[dict[str, Any]] = []
    edge_excluded = 0
    for s in signals:
        exit_idx = s.entry_idx + H
        if exit_idx >= n:                                    # orizont incomplet → exclus (Q2)
            edge_excluded += 1
            continue
        entry_price = float(o[s.entry_idx]); exit_price = float(cl[exit_idx])
        r = TS.net_R(s, entry_price, exit_price)
        # metadate pentru reconstrucție
        c = s.trigger_idx
        below = s.direction == +1
        pool_price = None
        for sw in sweeps:                                    # bazinul măturat la bara c
            if sw.idx == c:
                pool_price = float(sw.pool.price); break
        trades.append(dict(
            regime=label, net_R=r, direction=s.direction, spike_pips=s.spike_pips,
            R_dollars=TS.risk_R_dollars(s.spike_pips), sweep_idx=int(c), entry_idx=int(s.entry_idx),
            exit_idx=int(exit_idx), entry_open=entry_price, exit_close=exit_price,
            sweep_low=float(lo[c]), sweep_high=float(hi[c]), sweep_close=float(cl[c]),
            pool_price=pool_price, side="below" if below else "above",
            session=str(sess[s.entry_idx]),
            path=[round(float(cl[j]), 3) for j in range(s.entry_idx, exit_idx + 1)]))

    net = np.array([t["net_R"] for t in trades], dtype=float)
    nt = len(net)
    sumR = float(net.sum())
    srt = np.sort(net)[::-1]
    best = float(srt[0]) if nt else 0.0
    top3 = float(srt[:3].sum()); top5 = float(srt[:5].sum())
    bb = BB.run(net, block_length=L, B=B, tail="right", centering="zero", seed=SEED)

    return dict(
        regime=label, n_bars=n, n_trades=nt, edge_excluded=edge_excluded,
        pct_excluded_eligibility=round(pct_excluded, 2), total_valid_sweeps=total_valid, n_eligible=n_eligible,
        winrate=round(float((net > 0).mean()), 4) if nt else None,
        expectancy_R=round(float(net.mean()), 5) if nt else None,
        net_sumR=round(sumR, 3),
        best_over_sumR=round(best / sumR, 4) if sumR else None,
        top3_over_sumR=round(top3 / sumR, 4) if sumR else None,
        top5_over_sumR=round(top5 / sumR, 4) if sumR else None,
        wo1_netR=round(sumR - best, 3),                      # net FĂRĂ cea mai mare tranzacție
        p_wp5=bb["p_hat"], observed_mean_netR=bb["observed"], p_ci95=bb["p_mc_ci95"],
        _trades=trades)


def main() -> int:
    df, meta = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | discovery bars livrate = {len(df)} | meta n_bars_delivered = {meta.get('n_bars_delivered')}")
    if len(df) != 130_491:
        print(f"STOP: descoperirea are {len(df)} bare, aștept 130.491 — raportez, nu continui.")
        return 2

    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]
    t = df["time"].to_numpy()
    results: list[dict[str, Any]] = []
    for i, seg in enumerate(segs):
        label = _regime_label(seg, i)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = df[(t >= s_ep) & (t < e_ep)].reset_index(drop=True)
        exp = EXPECTED.get(label)
        if exp is not None and len(sub) != exp:
            print(f"STOP: regim {label} are {len(sub)} bare, aștept {exp} — raportez, nu continui.")
            return 3
        res = _analyze(label, sub)
        results.append(res)
        print(f"\n=== {label.upper()} | {len(sub)} bare ===")
        for kk in ("n_trades", "edge_excluded", "pct_excluded_eligibility", "winrate", "expectancy_R",
                   "net_sumR", "best_over_sumR", "top3_over_sumR", "top5_over_sumR", "wo1_netR",
                   "observed_mean_netR", "p_wp5", "p_ci95"):
            print(f"  {kk:26s} {res[kk]}")

    # top-5 tranzacții după net_R (GLOBAL) — reconstrucție descriptivă
    all_tr = [tr for r in results for tr in r["_trades"]]
    top5 = sorted(all_tr, key=lambda x: x["net_R"], reverse=True)[:5]

    out = {"loader_version": meta.get("loader_version"), "L": L, "B": B, "H": H, "seed": SEED,
           "regimes": [{k: v for k, v in r.items() if k != "_trades"} for r in results],
           "top5_trades_reconstruction_M15": [{k: v for k, v in tr.items()} for tr in top5]}
    path = os.path.join(_ROOT, "reports", "lm001_s1_execution_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print("\n=== TOP-5 tranzacții după net_R (descriptiv, M15, nu dovadă) ===")
    for tr in top5:
        print(f"  {tr['regime']:10s} sweep@{tr['sweep_idx']} {tr['side']:5s} pool={tr['pool_price']} "
              f"sweep_lo/hi={tr['sweep_low']}/{tr['sweep_high']} close_back={tr['sweep_close']} | "
              f"entry@{tr['entry_idx']} open={tr['entry_open']} spike={tr['spike_pips']:.1f}p "
              f"R=${tr['R_dollars']:.2f} dir={tr['direction']} exit={tr['exit_close']} netR={tr['net_R']:.2f} "
              f"| {tr['session']}")
    print(f"\nrecord -> reports/lm001_s1_execution_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

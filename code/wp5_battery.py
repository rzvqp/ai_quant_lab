"""WP-5' battery — FPR@0.05 al block_bootstrap@v1 contra nulului STRUCTURAL, L∈{10,20,28,40} (Mandat 5.7 Pas 2).

Testează predicția: la L≥H (H=20 bare, orizontul real de dependență finită), blocul conține integral
dependența → FPR ar trebui să coboare stabil în banda nominală. Raportez ȘI L=10,20 (sub/la H) ca să
văd unde e tranziția reală. Dacă NU iese nominal la L≥28, raportez eșecul și mă opresc (nu ajustez).

Șocurile = randamente REALE per-bară M15 din barele de descoperire (Q5, bootstrap-resamplate) — se
CITEȘTE distribuția de randamente ca INTRARE DE CALIBRARE (nu P&L, nu backtest, nu direcție/outcome
LM-001). Restul e sintetic în memorie. Reutilizează harness-ul `block_bootstrap` existent.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_HERE, os.path.join(_ROOT, "edge_research"), os.path.join(_ROOT, "edge_research", "lm001_s8")):
    if p not in sys.path:
        sys.path.insert(0, p)

import block_bootstrap as BB  # type: ignore[import-not-found]  # noqa: E402
import split_manifest as SM  # type: ignore[import-not-found]  # noqa: E402
from market_structure import Block, detect_swings, label_structure  # noqa: E402
from liquidity_mechanics import PoolSide, PoolTier, build_pools, detect_sweeps  # noqa: E402
from wp5_null_generator import OverlapNullConfig, Wp5StructuralNullGenerator  # noqa: E402

TICK, K, H = 0.1, 2, 20
FILTER_LO, FILTER_HI = 10.1, 65.0
LS = (10, 20, 28, 40)
N_SERIES, B, ALPHA = 200, 2000, 0.05


def _session(epoch: int) -> str:
    h = pd.Timestamp(epoch, unit="s", tz="UTC").hour
    return "asia" if h < 8 else "london" if h < 13 else "ny" if h < 21 else "late"


def build_config() -> OverlapNullConfig:
    """Extrage pozițiile empirice (filtrate [10.1,65], ferestre de margine excluse), sesiunile, și
    pool-urile de randamente per-bară M15, per segment de descoperire."""
    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]
    df = pd.read_csv(os.path.join(_ROOT, "data", "market", "OANDA_XAUUSD_M15.csv")).sort_values("time").reset_index(drop=True)
    t = df["time"].to_numpy()
    positions: list[list[int]] = []
    sessions: list[list[str]] = []
    shock_pools: list[list[float]] = []
    seg_len: list[int] = []
    for seg in segs:
        s, e = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = df[(t >= s) & (t < e)].reset_index(drop=True)
        o = sub["open"].to_numpy(); hi = sub["high"].to_numpy(); lo = sub["low"].to_numpy()
        cl = sub["close"].to_numpy(); tt = sub["time"].to_numpy()
        n = len(sub)
        blocks = [Block(0, n)]
        swings = label_structure(detect_swings(hi.tolist(), lo.tolist(), blocks, k=K))
        pools = build_pools(swings, PoolTier.EXTERNAL)
        sweeps = detect_sweeps(hi.tolist(), lo.tolist(), cl.tolist(), pools, blocks, require_close_back_inside=True)
        pos: list[int] = []; sess: list[str] = []
        for sw in sweeps:
            c = sw.idx
            if c + 1 >= n:
                continue
            dist = (o[c + 1] - lo[c]) if sw.pool.side is PoolSide.BELOW else (hi[c] - o[c + 1])
            pips = float(dist) / TICK
            if not (FILTER_LO <= pips <= FILTER_HI):
                continue
            if c + H >= n:                                   # Q2: fereastra de orizont iese din segment → exclus
                continue
            pos.append(c); sess.append(_session(int(tt[c])))
        positions.append(pos); sessions.append(sess); seg_len.append(n)
        shock_pools.append(np.diff(cl).tolist())             # Q5: randamente per-bară (close-to-close)
    return OverlapNullConfig(horizon=H, event_positions=positions, event_sessions=sessions,
                             shock_pools=shock_pools, segment_lengths=seg_len)


def _fpr(ps: list[float]) -> tuple[float, int]:
    a = np.asarray(ps)
    return float((a < ALPHA).mean()), len(ps)


def main() -> int:
    cfg = build_config()
    gen = Wp5StructuralNullGenerator(cfg)
    n_events = sum(len(p) for p in cfg.event_positions)
    # verificare Q4 (post-hoc, derivat): fracția de orizont partajat pe pozițiile empirice
    all_pos = sorted(c for seg in cfg.event_positions for c in seg)
    gaps = np.diff(all_pos)
    mean_spacing = float(gaps[gaps > 0].mean()) if len(gaps) else 0.0
    shared = (H - mean_spacing) / H
    sessions_list = ["asia", "london", "ny", "late"]

    print(f"WP-5' BATTERY — n_events={n_events} | H={H} | B={B} | n_series={N_SERIES}")
    print(f"Q4 check (derived, not imposed): mean_spacing={mean_spacing:.2f} bars -> shared_horizon={shared:.3f} (~0.69)")
    print("=" * 90)
    results: dict[str, Any] = {"config": {"n_events": n_events, "H": H, "B": B, "n_series": N_SERIES,
                                          "mean_spacing": mean_spacing, "shared_horizon": shared}, "by_L": {}}
    for L in LS:
        agg: list[float] = []
        per: dict[str, list[float]] = {s: [] for s in sessions_list}
        for si in range(N_SERIES):
            out, sess = gen.generate_null_series(np.random.default_rng(1000 + si))
            agg.append(BB.run(out, block_length=L, B=B, tail="right", centering="zero", seed=7_000_000 + L * 1000 + si)["p_hat"])
            sess_arr = np.asarray(sess)
            for s in sessions_list:
                sub = out[sess_arr == s]
                if len(sub) > L:
                    per[s].append(BB.run(sub, block_length=L, B=B, tail="right", centering="zero",
                                         seed=8_000_000 + L * 10000 + si)["p_hat"])
        fpr_agg, _ = _fpr(agg)
        tag = "NOMINAL" if fpr_agg <= 0.06 else "ANTI-CONSERVATOR"
        rel = "L>=H" if L >= H else "L<H"
        print(f"L={L:2d} ({rel}): FPR@0.05 aggregate={fpr_agg:.4f} [{tag}]"
              f"  | per-session " + " ".join(f"{s}={_fpr(per[s])[0]:.3f}" for s in sessions_list), flush=True)
        results["by_L"][L] = {"fpr_aggregate": fpr_agg,
                              "fpr_by_session": {s: _fpr(per[s])[0] for s in sessions_list}}
    with open(os.path.join(_ROOT, "edge_research", "wp5_battery_results.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
    print("\nrecord -> edge_research/wp5_battery_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

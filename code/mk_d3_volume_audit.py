"""MK-01 D3 VOLUME AUDIT — Mandate 5.0 Step 2.

AUDIT DE VOLUM GEOMETRIC. Numără structuri (swing points) și măsoară fereastra
oarbă D3 per bloc de descoperire M15_v2. NU interoghează prețul pentru P&L, NU
evaluează performanță, NU rulează LM-001, NU construiește nicio tranzacție.

Sursă de mascare = config/split_manifest.json (autoritatea). Blocurile de
descoperire = `discovery_range` al fiecărui regime_segment M15_v2 (2011-2021, cu
mult înainte de granița sigilată 2025-10-23 — auditul nu poate atinge holdout-ul).
M5 EXCLUS prin D5 (maparea cross-rezoluție nu există). Segmentul 2022-2026 EXCLUS
ca SAME-WINDOW-RESAMPLED (overlap_with_M15).
"""

from __future__ import annotations

import json
import os
import sys

import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from market_structure import Block, StructureLabel, SwingKind, detect_swings, label_structure

ROOT = os.path.dirname(_HERE)
MANIFEST = os.path.join(ROOT, "config", "split_manifest.json")
K = 2


def load() -> tuple[pd.DataFrame, list[dict]]:
    m = json.load(open(MANIFEST, encoding="utf-8"))
    tf = m["timeframes"]["M15_v2"]
    assert tf["status"] == "VALIDATED", f"M15_v2 status {tf['status']}"
    csv = os.path.join(ROOT, tf["file_path"])
    df = pd.read_csv(csv)
    segs = []
    for s in tf["regime_segments"]:
        dr = s.get("discovery_range") or {}
        se, ee = dr.get("start_epoch"), dr.get("end_epoch")
        if se is None or ee is None:
            segs.append({"type": s["type"], "skipped": "no discovery_range", "n": 0})
            continue
        segs.append({"type": s["type"], "start_epoch": se, "end_epoch": ee})
    return df, segs


def audit_block(high, low) -> dict:
    n = len(high)
    blocks = [Block(0, n)]
    swings = label_structure(detect_swings(high, low, blocks, k=K))
    n_high = sum(1 for s in swings if s.kind is SwingKind.HIGH)
    n_low = sum(1 for s in swings if s.kind is SwingKind.LOW)
    unclassified = [s for s in swings if s.label is StructureLabel.UNCLASSIFIED]
    classified = [s for s in swings if s.label is not StructureLabel.UNCLASSIFIED]
    blind_bars = classified[0].idx if classified else None  # bare de la start la prima CLASIFICATĂ
    return {
        "n_bars": n, "n_swings": len(swings), "n_high": n_high, "n_low": n_low,
        "n_unclassified": len(unclassified), "n_classified": len(classified),
        "blind_bars": blind_bars,
        "blind_pct": (100.0 * blind_bars / n) if blind_bars is not None else None,
        "unclassified_pct": 100.0 * len(unclassified) / n if n else 0.0,
    }


def main() -> int:
    df, segs = load()
    t = df["time"].to_numpy()
    total_disc = 0
    rows = []
    for s in segs:
        if "skipped" in s:
            rows.append((s["type"], None, s["skipped"]))
            continue
        mask = (t >= s["start_epoch"]) & (t <= s["end_epoch"])
        sub = df[mask]
        high = sub["high"].to_numpy().tolist()
        low = sub["low"].to_numpy().tolist()
        total_disc += len(high)
        rows.append((s["type"], audit_block(high, low), None))

    print("=" * 78)
    print("MK-01 D3 VOLUME AUDIT — M15_v2 discovery blocks (geometric count only)")
    print(f"total discovery bars audited: {total_disc}  (CEO stated: 130,491)")
    print("=" * 78)
    breach = False
    for name, r, skip in rows:
        if skip:
            print(f"\n[{name}] SKIPPED — {skip}")
            continue
        print(f"\n[BLOCK: {name}]  n_bars={r['n_bars']}")
        print(f"  (a) total swings: {r['n_swings']}  (high={r['n_high']}, low={r['n_low']})")
        print(f"  (b) UNCLASSIFIED (reset at boundary): {r['n_unclassified']}"
              f"  = {r['unclassified_pct']:.4f}% of block")
        bb, bp = r["blind_bars"], r["blind_pct"]
        if bb is None:
            print("  (c) blind window: NO classified structure in block (all UNCLASSIFIED)")
        else:
            flag = ">5% BREACH" if bp > 5.0 else ("1-5% disclosure" if bp > 1.0 else "<=1% cheap")
            print(f"  (c) blind window: {bb} bars = {bp:.4f}% of block  -> {flag}")
            if bp > 5.0:
                breach = True
    print("\n" + "=" * 78)
    print("VERDICT: >5% blind window on at least one block — STOP, D3 needs redesign."
          if breach else
          "VERDICT: no block exceeds 5% blind window.")
    return 1 if breach else 0


if __name__ == "__main__":
    raise SystemExit(main())

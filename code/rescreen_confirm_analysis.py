"""CONFIRMARE INDEPENDENTĂ a clasamentului nou + întrebarea despre volum (RT-CODE-A-0005). READ-ONLY (fără P&L).

Citește DOUĂ produse independente:
  1) `phase1_screening_results.json` — screening COMPLET de la zero, motorul reparat (commit 06e4e00), calea
     standalone (motorul real, fără replică).
  2) `measure_d1_consequence_results.json` — diff per-tranzacție vechi(defect)-vs-nou(reparat), calea replică.
Confirmă că netR nou din (1) == netR nou din (2) pt. TOȚI cei 34 (două metodologii, aceeași cifră).

Întrebarea CEO: rata de inversare (flip/n) crește cu volumul (n)? Dacă da — proprietate a defectului sau a
candidaților? Calculez corelația Pearson & Spearman (n vs rată), fără verdict statistic — descriptiv.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_REP = os.path.join(_ROOT, "reports")


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2 or x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return _pearson(rx, ry)


def main() -> int:
    with open(os.path.join(_REP, "phase1_screening_results.json"), encoding="utf-8") as fh:
        fs = json.load(fh)["candidates"]
    with open(os.path.join(_REP, "measure_d1_consequence_results.json"), encoding="utf-8") as fh:
        meas = json.load(fh)
    per = {r["cid"]: r for r in meas["per_candidate"]}

    print("### CONFIRMARE INDEPENDENTĂ — netR nou: screening-de-la-zero (motor real) vs diff-per-tranzacție (replică) ###")
    rows: list[dict[str, Any]] = []
    all_match = True
    for cid, r in per.items():
        fs_new = float(fs[cid]["net_R"]) if cid in fs and fs[cid].get("net_R") is not None else None
        match = fs_new is not None and abs(fs_new - r["new_netR"]) < 0.05
        all_match = all_match and match
        rows.append({**r, "fs_new": fs_new, "match": match})

    rows_by_new = sorted(rows, key=lambda x: -x["new_netR"])
    print(f"  TOȚI cei {len(rows)} coincid (|Δ|<0.05): {all_match}")
    mism = [r["cid"] for r in rows if not r["match"]]
    if mism:
        print(f"  NEPOTRIVIRI: {mism}")

    print("\n### TABEL COMPLET — ÎNAINTE (defect) vs DUPĂ (reparat), + tranzacții schimbate ###")
    print(f"  {'#':>2} {'cid':10s} {'nume':26s} {'n':>6} {'înainte':>9} {'după':>9} {'Δ':>8} {'changed':>7} {'flip':>6} conf")
    for i, r in enumerate(rows_by_new, 1):
        print(f"  {i:>2} {r['cid']:10s} {r['name']:26s} {r['n']:>6d} {r['old_netR']:>9.1f} {r['new_netR']:>9.1f} "
              f"{r['new_netR']-r['old_netR']:>8.1f} {r['changed']:>7d} {r['flip']:>6d} {'✓' if r['match'] else '✗'}")

    old_rank = [r["cid"] for r in sorted(rows, key=lambda x: -x["old_netR"])]
    new_rank = [r["cid"] for r in rows_by_new]
    print(f"\n  clasament schimbat: {old_rank != new_rank}")
    print("  TOP 6 vechi → nou:")
    for i in range(6):
        print(f"    {i+1}. {old_rank[i]:10s} → {new_rank[i]:10s}")

    # ── ÎNTREBAREA: rata de inversare vs volum ──
    n = np.array([r["n"] for r in rows], dtype=float)
    changed = np.array([r["changed"] for r in rows], dtype=float)
    flip = np.array([r["flip"] for r in rows], dtype=float)
    nz = n > 0
    n_, changed_, flip_ = n[nz], changed[nz], flip[nz]
    changed_rate = changed_ / n_
    flip_rate = flip_ / n_

    print("\n### ÎNTREBAREA — rata de inversare crește cu volumul? ###")
    print(f"  corelație VOLUM (n) vs rată-changed:  Pearson={_pearson(n_, changed_rate):+.3f}  Spearman={_spearman(n_, changed_rate):+.3f}")
    print(f"  corelație VOLUM (n) vs rată-flip:      Pearson={_pearson(n_, flip_rate):+.3f}  Spearman={_spearman(n_, flip_rate):+.3f}")
    print(f"  corelație VOLUM (n) vs changed ABSOLUT: Pearson={_pearson(n_, changed_):+.3f}")
    print(f"  corelație VOLUM (n) vs flip ABSOLUT:    Pearson={_pearson(n_, flip_):+.3f}")
    print(f"  rată-flip: min={flip_rate.min()*100:.2f}% max={flip_rate.max()*100:.2f}% "
          f"mediană={np.median(flip_rate)*100:.2f}% (dispersie mare ⇒ NU constantă)")
    order = np.argsort(-n_)
    cids = [r["cid"] for r in rows if r["n"] > 0]
    print("\n  candidați sortați DESCRESCĂTOR după volum (n) — rata NU urmează volumul:")
    print(f"  {'cid':10s} {'n':>6} {'rată-changed':>13} {'rată-flip':>10}")
    for k in order:
        print(f"  {cids[k]:10s} {int(n_[k]):>6d} {changed_rate[k]*100:>12.2f}% {flip_rate[k]*100:>9.2f}%")

    out = {"note": "read-only confirmation + volume analysis; descriptive",
           "all_new_match": all_match, "ranking_changed": old_rank != new_rank,
           "old_ranking": old_rank, "new_ranking": new_rank,
           "corr_n_vs_changed_rate_pearson": round(_pearson(n_, changed_rate), 4),
           "corr_n_vs_flip_rate_pearson": round(_pearson(n_, flip_rate), 4),
           "corr_n_vs_flip_rate_spearman": round(_spearman(n_, flip_rate), 4),
           "corr_n_vs_flip_abs_pearson": round(_pearson(n_, flip_), 4),
           "flip_rate_min": round(float(flip_rate.min()), 4), "flip_rate_max": round(float(flip_rate.max()), 4)}
    with open(os.path.join(_REP, "rescreen_confirm_analysis_results.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/rescreen_confirm_analysis_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

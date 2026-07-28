"""Completează curba S8 la φ=0,45 și φ=0,50, n=21.048 (Mandat 5.5, Sarcina 1).

Umple golul nemăsurat dintre φ=0,4 (FPR 0,0500) și φ=0,6 (FPR 0,0767), unde cade pragul
propus de 0,45 — ca granița nominal↔anti-conservator să fie DERIVATĂ, nu aleasă. Reutilizează
aceeași baterie (`block_bootstrap.py` + `synthetic_block_bootstrap.py`), aceiași parametri:
B=10.000, L=round(n^(1/3))=28, n_series=300, α=0,05. Sintetic în memorie, zero prețuri reale.
"""

from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import block_bootstrap as BB       # noqa: E402
import synthetic_block_bootstrap as S  # noqa: E402

B = 10000
N_SERIES = 300
N = 21048
L = round(N ** (1.0 / 3.0))       # 28, aceeași regulă ca extend_n21000
ALPHA = 0.05


def fpr_ar1(phi: float, seed0: int) -> tuple[float, tuple[float, float]]:
    ps = []
    for s in range(N_SERIES):
        rng = np.random.default_rng(seed0 + s)
        r = S.generate_r_series(rng, N, edge=0.0, ar1=phi)
        ps.append(BB.run(r, block_length=L, B=B, tail="right",
                         centering="zero", seed=seed0 + s + 1_000_000)["p_hat"])
    return S.fpr(ps, ALPHA)


def main() -> int:
    t0 = time.time()
    rows = []
    for phi in (0.45, 0.50):
        seed0 = int(phi * 100) * 1000 + N       # distinct, determinist
        f, ci = fpr_ar1(phi, seed0)
        rows.append({"phi": phi, "n": N, "L": L, "fpr05": f, "ci": [round(ci[0], 4), round(ci[1], 4)]})
        print(f"phi={phi} n={N} L={L}: FPR@0.05={f:.4f} CI=[{ci[0]:.4f},{ci[1]:.4f}]  "
              f"{'NOMINAL' if f <= 0.06 else 'ANTI-CONSERVATOR'}   [{time.time()-t0:.0f}s]", flush=True)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lm001_s8_curve_completion.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"config": {"B": B, "n_series": N_SERIES, "n": N, "L": L}, "points": rows}, fh, indent=2)
    print("\nrecord ->", os.path.relpath(out))
    print("\n=== curba completă la n=21048 (φ ↑) ===")
    print("  φ=0.40: 0.0500 (măsurat anterior)")
    for r in rows:
        print(f"  φ={r['phi']:.2f}: {r['fpr05']:.4f}")
    print("  φ=0.60: 0.0767 (măsurat anterior)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
